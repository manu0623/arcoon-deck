"""Self-update from a URL, driven from the plugin's own settings page.

The panel already runs with the loader's privileges and already knows where it is
installed, so the only missing piece between "a new build exists" and "it is running"
is: download it somewhere private, hand it to the installer, and let Decky restart.
Doing it here rather than asking the user for a terminal is the point — on a Deck in
Game Mode there is no terminal to ask them for.

The URL is user-supplied, so it is only ever fetched with ``urllib`` (never a shell)
and the download is capped: an endpoint that streams forever must not fill the Deck.
"""

from __future__ import annotations

import io
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import TYPE_CHECKING, Any

from domain.plugin_archive import UpdateRefused

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.plugin_installer import PluginInstaller

# A plugin zip is ~6 MB. This ceiling is far above that and still bounds the damage a
# wrong URL can do, which is the only thing it needs to do.
_MAX_BYTES = 64 * 1024 * 1024
_TIMEOUT_SECONDS = 60

#: Where the Update button installs from when no URL is pasted: this fork's own main
#: branch, as a source archive. Main is the newest pushed build — ``dist/`` is
#: committed, so the archive is installable as-is — which makes an update the same act
#: as a push, with no release step or asset naming to keep in step.
DEFAULT_UPDATE_URL = "https://github.com/manu0623/arcoon-deck/archive/refs/heads/main.zip"

#: The subset a Decky plugin needs at runtime — the same list ``scripts/deck-update.sh``
#: installs. A source archive holds the whole repository, and an update must not carry
#: tests, docs or CI onto the Deck.
SHIPPED_ENTRIES: tuple[str, ...] = (
    "plugin.json",
    "main.py",
    "package.json",
    "LICENSE",
    "README.md",
    "dist",
    "defaults",
    "bin",
    "assets",
    "py_modules",
    "scripts",
)


class PluginUpdateService:
    """Download a build, install it over this plugin, and restart the loader."""

    def __init__(
        self,
        *,
        installer: PluginInstaller,
        folder: str,
        plugin_name: str,
        current_version: str,
        logger: logging.Logger,
        fetcher: Callable[[str], bytes] | None = None,
    ) -> None:
        self._installer = installer
        self._folder = folder
        self._plugin_name = plugin_name
        self._current_version = current_version
        self._logger = logger
        self._fetcher = fetcher or _download

    def update_from_url(self, url: str | None) -> dict[str, Any]:
        """Install the build at *url*, or this fork's newest build when it is blank.

        A blank URL is the ordinary case: the panel's Update button installs from
        :data:`DEFAULT_UPDATE_URL`, so keeping the plugin current needs no link. A URL
        still wins when one is given, which is how a build from anywhere else is
        installed.
        """
        target = (url or "").strip() or DEFAULT_UPDATE_URL
        try:
            _check_url(target)
            payload = _reparent(self._fetcher(target), folder=self._folder)
        except (UpdateRefused, ValueError) as exc:
            self._logger.warning(f"Plugin update refused before download: {exc}")
            return {"success": False, "message": str(exc)}
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            self._logger.warning(f"Plugin update download failed from {target}: {exc}")
            return {"success": False, "message": f"Could not download the update: {exc}"}

        archive_path = ""
        try:
            with tempfile.NamedTemporaryFile(prefix="arcoon-update-", suffix=".zip", delete=False) as handle:
                archive_path = handle.name
                handle.write(payload)
            installed = self._installer.install(
                archive_path,
                self._folder,
                expected_name=self._plugin_name,
                current_version=self._current_version,
            )
        except (UpdateRefused, OSError, zipfile.BadZipFile) as exc:
            self._logger.warning(f"Plugin update refused: {exc}")
            return {"success": False, "message": str(exc)}
        finally:
            if archive_path:
                with _suppress_oserror():
                    os.unlink(archive_path)

        self._logger.info(f"Plugin updated {self._current_version} -> {installed.version}; restarting Decky")
        self._installer.schedule_loader_restart()
        return {
            "success": True,
            "version": installed.version,
            "message": f"Updated to {installed.version}. Decky restarts in a few seconds.",
        }


def _reparent(payload: bytes, *, folder: str) -> bytes:
    """Re-root a source archive so the installer sees a folder named *folder*.

    A zip built for a release already holds that folder and is returned untouched. A
    GitHub source archive unpacks into ``<repo>-main/`` instead, so its shipped subset
    is moved under the plugin's own folder name and everything else in the repository
    — tests, docs, CI, the frontend sources — is dropped rather than installed onto
    the Deck. Anything that is not an archive, or that has no single top folder, is
    returned unchanged for the installer to refuse with its own message.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as source:
            names = [info.filename for info in source.infolist() if not info.is_dir()]
            tops = {name.split("/", 1)[0] for name in names}
            if len(tops) != 1:
                return payload
            top = tops.pop()
            if top == folder:
                return payload
            wanted = [
                name
                for name in names
                if name.startswith(f"{top}/") and name.split("/", 2)[1] in SHIPPED_ENTRIES
            ]
            if not wanted:
                return payload
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as out:
                for name in wanted:
                    out.writestr(f"{folder}/{name[len(top) + 1 :]}", source.read(name))
            return buffer.getvalue()
    except zipfile.BadZipFile:
        return payload


def _check_url(url: str) -> None:
    """Refuse anything that is not a plain http(s) download."""
    parsed = urllib.parse.urlparse(url or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise UpdateRefused("Enter a full http:// or https:// URL to a plugin zip.")


def _download(url: str) -> bytes:
    """Fetch *url*, refusing more than :data:`_MAX_BYTES`."""
    with urllib.request.urlopen(url, timeout=_TIMEOUT_SECONDS) as response:
        data = response.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise UpdateRefused("That file is far larger than a plugin build.")
    return data


class _suppress_oserror:
    """Tiny context manager: a temp file that is already gone is not an error."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        return isinstance(exc, OSError)
