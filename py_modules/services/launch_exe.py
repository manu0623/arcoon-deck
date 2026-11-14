"""LaunchExeService — a Windows game's executable: what it is, and how it changes.

A RomM ``windows`` entry is played by no emulator: Steam starts the game's own
executable, under Proton, and that is the whole launch chain
(:mod:`domain.windows_launch`). So the only launch fact this platform has is
*which file that is*, and it is decided twice:

- **Automatically**, on download, by :func:`domain.windows_launch.pick_game_exe`.
  A ranking over names and shapes, which is right most of the time and is allowed
  to be wrong.
- **By hand**, here. A folder can hold a launcher, an uninstaller and the real
  game, and nothing in a filename proves which one a person wants to press. This
  service is the list they pick from, and the write that makes the pick real.

The write lands on the ``RomInstall`` aggregate (``retarget_launch_file``), not in
``settings``: the launch file is the install's own identity, and the sync, the
uninstall, the adoption and the download all read it there. The frontend is handed
the shortcut's new ``exe``/``start_dir`` back because it is the only side that can
write them onto the live Steam shortcut — the backend never owns that store.

**A single-file Windows install has nothing to pick.** A lone ``.exe`` in the
shared platform directory owns no folder of its own, so scanning "its" directory
would offer every other game in the platform. That install answers with no
candidates and refuses every write, which is the honest answer: there is exactly
one file it could run.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.windows_launch import (
    is_windows_launch_file,
    is_windows_platform,
    ranked_exe_paths,
    relative_to_install,
    shortcut_for_exe,
)
from lib.list_result import ErrorCode

if TYPE_CHECKING:
    import asyncio
    import logging

    from services.protocols import DownloadFileStore, UnitOfWorkFactory

#: How many executables the picker is offered. A game folder with more than this
#: many is either a suite (an engine SDK, a pack of tools) or not a game, and a
#: menu that long is not a menu — the list states it was cut rather than implying
#: it holds everything.
_MAX_CANDIDATES = 60


@dataclass(frozen=True)
class LaunchExeServiceConfig:
    """Frozen wiring bundle handed to ``LaunchExeService.__init__``.

    Carries the runtime infrastructure (event loop, logger), the SQLite
    Unit-of-Work factory (to read the install and write the new launch file), and
    the file store the install directory is listed through — the same seam the
    download path detects its launch file with, so the list the picker shows and
    the file a download picked come from one scan of one directory.
    """

    loop: asyncio.AbstractEventLoop
    logger: logging.Logger
    uow_factory: UnitOfWorkFactory
    file_store: DownloadFileStore


class LaunchExeService:
    """The Windows exe picker's read (``get_launch_exe``) and write (``set_launch_exe``)."""

    def __init__(self, *, config: LaunchExeServiceConfig) -> None:
        self._loop = config.loop
        self._logger = config.logger
        self._uow_factory = config.uow_factory
        self._file_store = config.file_store

    async def get_launch_exe(self, rom_id: int) -> dict[str, Any]:
        """Report the executable picker's state for ``rom_id``.

        Returns ``{"windows": False}`` for an unknown ROM, an uninstalled one, or
        one on any other platform — the frontend renders no picker in those cases.
        For a Windows install it returns ``windows: True`` with ``current`` (the
        recorded launch file, relative to the install), ``candidates`` in the
        ranking order the automatic pick uses (``path`` relative, ``size_bytes``)
        and ``truncated`` when the list was cut at :data:`_MAX_CANDIDATES`.

        Read-only, and the not-Windows answer is the normal one rather than a
        failure: every game page asks, and almost every answer is "no picker".
        """
        return await self._loop.run_in_executor(None, self._get_launch_exe_io, rom_id)

    def _get_launch_exe_io(self, rom_id: int) -> dict[str, Any]:
        with self._uow_factory() as uow:
            install = uow.rom_installs.get(int(rom_id))
        if install is None or not is_windows_platform(install.platform_slug):
            return {"windows": False}
        if install.rom_dir is None:
            # A single-file install owns no folder — see the module docstring.
            return {
                "windows": True,
                "current": posixpath.basename(install.file_path),
                "candidates": [],
                "truncated": False,
            }
        # The listing runs after the read UoW has closed: a UoW holds SQLite's
        # BEGIN IMMEDIATE write lock, and a directory walk inside one stalls every
        # other writer for as long as the walk takes (ADR-0006).
        files = self._file_store.scan_files_with_sizes(install.rom_dir)
        ranked = ranked_exe_paths(files)
        sizes = dict(files)
        candidates = [
            {"path": posixpath.relpath(path, install.rom_dir), "size_bytes": sizes.get(path, 0)}
            for path in ranked[:_MAX_CANDIDATES]
        ]
        return {
            "windows": True,
            "current": relative_to_install(install.rom_dir, install.file_path) or posixpath.basename(install.file_path),
            "candidates": candidates,
            "truncated": len(ranked) > _MAX_CANDIDATES,
        }

    async def set_launch_exe(self, rom_id: int, relative_path: str) -> dict[str, Any]:
        """Record *relative_path* as the executable ``rom_id`` launches.

        *relative_path* is relative to the install's own directory and must name
        a file that directory actually holds, with a launchable extension. Anything
        outside it is refused rather than clamped — the same rule the download
        path applies to every server-supplied name, for the same reason.

        On success the install's launch file is rewritten, the install is marked
        launchable, and the response carries the shortcut's new ``exe`` and
        ``start_dir`` plus the bound ``app_id`` — the frontend writes those onto
        the live Steam shortcut, and no-op when the ROM has none yet (the next
        sync creates the shortcut with the same shape).
        """
        return await self._loop.run_in_executor(None, self._set_launch_exe_io, rom_id, relative_path)

    def _set_launch_exe_io(self, rom_id: int, relative_path: str) -> dict[str, Any]:
        with self._uow_factory() as uow:
            rom = uow.roms.get(int(rom_id))
            install = uow.rom_installs.get(int(rom_id))
        if rom is None or install is None or not is_windows_platform(install.platform_slug):
            return {
                "success": False,
                "reason": "not_installed",
                "message": f"ROM {rom_id} is not an installed Windows game",
            }
        if install.rom_dir is None:
            return {
                "success": False,
                "reason": ErrorCode.UNSUPPORTED.value,
                "message": f"ROM {rom_id} is a single executable; there is nothing to choose",
            }
        relative = relative_to_install(install.rom_dir, relative_path)
        if relative is None:
            return {
                "success": False,
                "reason": ErrorCode.NOT_FOUND.value,
                "message": f"'{relative_path}' is not inside ROM {rom_id}'s install directory",
            }
        if not is_windows_launch_file(relative):
            return {
                "success": False,
                "reason": ErrorCode.UNSUPPORTED.value,
                "message": f"'{relative_path}' is not an executable",
            }
        absolute = posixpath.join(install.rom_dir, relative)
        # Listed, not merely joined: a path the file store cannot see is a typo or
        # a file that moved between the two transactions, and writing it would aim
        # the shortcut at nothing.
        if absolute not in {path for path, _size in self._file_store.scan_files_with_sizes(install.rom_dir)}:
            return {
                "success": False,
                "reason": ErrorCode.NOT_FOUND.value,
                "message": f"'{relative_path}' is not in ROM {rom_id}'s install directory",
            }
        with self._uow_factory() as uow:
            # Re-read: the row is decided against a snapshot, and an uninstall can
            # retire it between the two transactions on its own connection.
            current = uow.rom_installs.get(int(rom_id))
            rom_row = uow.roms.get(int(rom_id))
            if current is None or current.rom_dir is None:
                return {
                    "success": False,
                    "reason": "not_installed",
                    "message": f"ROM {rom_id} is not installed any more",
                }
            current.retarget_launch_file(absolute, launchable=True)
            uow.rom_installs.save(current)
            app_id = rom_row.shortcut_app_id if rom_row is not None else None
        exe, start_dir = shortcut_for_exe(absolute)
        self._logger.info(f"Windows launch target for rom {rom_id} set to '{relative}'")
        return {
            "success": True,
            "message": f"Launching {relative}",
            "app_id": app_id,
            "exe": exe,
            "start_dir": start_dir,
            "launch_options": "",
        }
