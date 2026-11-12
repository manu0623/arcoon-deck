"""Replace this plugin's own folder with an unpacked update, and restart the loader.

Runs inside Decky's loader process, which is already root: no password, no terminal,
which is the whole reason the panel can update itself in Game Mode.

Two rules keep that safe. Nothing is written until the archive validates
(:func:`domain.plugin_archive.inspect_archive`). And the old folder is never deleted
until the new one is in place and holds its ``plugin.json`` — if the swap fails
half-way the old folder goes back, because the alternative is a panel entry that
opens to an import error.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from typing import TYPE_CHECKING

from domain.plugin_archive import PluginArchive, inspect_archive

if TYPE_CHECKING:
    import logging

_MANIFEST = "plugin.json"


class PluginInstaller:
    """Filesystem half of a self-update: validate, stage, swap, restart."""

    def __init__(self, *, plugins_dir: str, logger: logging.Logger) -> None:
        self._plugins_dir = plugins_dir
        self._logger = logger

    def install(
        self,
        archive_path: str,
        folder: str,
        *,
        expected_name: str,
        current_version: str,
    ) -> PluginArchive:
        """Install *archive_path* over *folder* and return what was installed."""
        with zipfile.ZipFile(archive_path, "r") as archive:
            names = [info.filename for info in archive.infolist() if not info.is_dir()]
            # Read the manifest by its own position (top-dir/plugin.json) rather than
            # assuming the first member is it: a zip's order is whatever the packer chose.
            manifest_name = next(
                (name for name in names if name.count("/") == 1 and name.endswith(f"/{_MANIFEST}")),
                "",
            )
            manifest = archive.read(manifest_name) if manifest_name else b""
            validated = inspect_archive(
                names,
                manifest,
                expected_folder=folder,
                expected_name=expected_name,
                current_version=current_version,
            )

            staging = self._fresh_dir(f".{folder}.staging")
            self._extract(archive, staging, validated.folder)

        staged = os.path.join(staging, folder)
        target = os.path.join(self._plugins_dir, folder)
        retired = os.path.join(self._plugins_dir, f".{folder}.old")
        if os.path.exists(retired):
            shutil.rmtree(retired, ignore_errors=True)

        moved_out = False
        try:
            if os.path.isdir(target):
                os.replace(target, retired)
                moved_out = True
            os.replace(staged, target)
        except OSError:
            if moved_out and not os.path.exists(target):
                # The swap failed after the old folder moved: put it back rather than
                # leave Decky pointing at nothing.
                os.replace(retired, target)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)

        if not os.path.isfile(os.path.join(target, _MANIFEST)):
            raise OSError("the installed folder has no plugin.json")
        return validated

    def schedule_loader_restart(self, *, delay_seconds: int = 3) -> None:
        """Restart Decky's loader shortly after answering, so the panel shows the result.

        Detached on purpose: this process is a child of the loader being restarted, so
        waiting for it would kill the caller before it could reply to the UI.
        """
        subprocess.Popen(
            ["sh", "-c", f"sleep {int(delay_seconds)}; systemctl restart plugin_loader"],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _fresh_dir(self, name: str) -> str:
        path = os.path.join(self._plugins_dir, name)
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)
        return path

    def _extract(self, archive: zipfile.ZipFile, dest: str, folder: str) -> None:
        """Unpack the archive's files under *dest*, refusing any path outside it."""
        real_dest = os.path.realpath(dest)
        for info in archive.infolist():
            if info.is_dir():
                continue
            target = os.path.realpath(os.path.join(real_dest, info.filename))
            if target != real_dest and not target.startswith(real_dest + os.sep):
                raise OSError(f"archive member {info.filename!r} would extract outside {dest!r}")
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with archive.open(info) as source, open(target, "wb") as destination:
                shutil.copyfileobj(source, destination)
        if not os.path.isdir(os.path.join(real_dest, folder)):
            raise OSError(f"archive did not unpack {folder!r}")
