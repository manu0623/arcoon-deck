"""PC save sync — a Proton game's own save folder, carried to RomM as one set.

A Windows game writes inside its Wine prefix, so the libretro battery-file
pipeline never sees it: measured on the reference Deck, `do_sync_rom_saves` for
a `win` ROM looked in `<data>/saves/win` and found nothing while the game's
profile sat in `compatdata/<appId>/pfx/drive_c/users/steamuser/Documents/…`.

This is the prototype that closes that gap for one game at a time:

* **capture** (after a session) zips the game's save folder and uploads it to
  RomM against the ROM, labelled ``proton``.
* **restore** (before a launch) downloads the newest such save and unzips it
  back over the same folder.

The folder is chosen once per ROM — by name against the game's title, else the
most recently written candidate — and remembered in ``kv_config`` as a path
relative to the prefix, so a rebuilt prefix under the same appId still finds it
and a hand-edited value can never point outside the game's own prefix.

Deliberately not handled here: saves a game keeps in the registry (no file to
carry), and games that scatter progress across two folders. Both are visible as
"the folder I picked does not contain my progress", which is why the pick is
logged with the folder it chose.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.iso_time import parse_iso_to_epoch
from domain.pc_saves import (
    SAVE_ROOTS,
    SaveCandidate,
    pick_save_dir,
    prefix_user_dir,
    relative_to_prefix,
    resolve_relative,
)
from domain.windows_launch import is_windows_platform

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.romm.romm_api import RommApiAdapter
    from adapters.steam_config import SteamConfigAdapter
    from domain.rom import Rom
    from services.protocols import DownloadFileStore, UnitOfWorkFactory

#: The emulator label a PC save is stored under on the server. RomM keys saves by
#: (rom, emulator, slot); ``proton`` says what wrote it without pretending to be
#: a libretro core.
PC_SAVE_EMULATOR = "proton"

#: One slot for the prototype: a PC game's profile is a single set, not a
#: battery file with autosave/manual variants.
PC_SAVE_SLOT = "default"

#: ``kv_config`` key prefix for the remembered folder, per ROM.
_KV_PREFIX = "pc_save_dir:"

#: How deep under a save root a candidate may sit (``AppData/Roaming/<game>``).
_MAX_DEPTH = 2


@dataclass(frozen=True)
class PcSaveSyncConfig:
    """Everything the service needs, handed in by the composition root."""

    romm_api: RommApiAdapter
    uow_factory: UnitOfWorkFactory
    file_store: DownloadFileStore
    steam_config: SteamConfigAdapter
    logger: logging.Logger
    data_dir: str
    #: Called with the ROM's name and the folder it picked, for the log line that
    #: makes a wrong pick diagnosable without a debugger.
    log_pick: Callable[[str, str], None] | None = None


class PcSaveSync:
    """Zip-and-upload / download-and-unzip for one PC game's save folder."""

    def __init__(self, *, config: PcSaveSyncConfig) -> None:
        self._romm_api = config.romm_api
        self._uow_factory = config.uow_factory
        self._file_store = config.file_store
        self._steam_config = config.steam_config
        self._logger = config.logger
        self._data_dir = config.data_dir
        self._log_pick = config.log_pick

    # -- what this service owns ------------------------------------------------

    def handles(self, rom_id: int) -> bool:
        """Whether *rom_id* is a Windows game — the only platform this serves."""
        rom = self._rom(rom_id)
        return rom is not None and is_windows_platform(rom.platform_slug)

    # -- the two hooks ---------------------------------------------------------

    def restore(self, rom_id: int) -> dict[str, Any]:
        """Put the newest server save back into the game's folder, before launch."""
        rom = self._rom(rom_id)
        if rom is None or not is_windows_platform(rom.platform_slug):
            return {"success": True, "synced": 0, "message": "Not a Windows game"}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {"success": True, "synced": 0, "message": "No Proton prefix for this game yet"}
        target = self._target_dir(rom, prefix_user)
        if target is None:
            return {"success": True, "synced": 0, "message": "No save folder found in the game's prefix yet"}
        try:
            saves = self._romm_api.list_saves(int(rom_id))
        except Exception as exc:
            self._logger.warning(f"PC save restore for rom {rom_id}: listing saves failed: {exc}")
            return {"success": False, "synced": 0, "message": f"Could not list saves: {exc}"}
        if not saves:
            return {"success": True, "synced": 0, "message": "No save on the server yet"}
        newest = max(saves, key=lambda save: parse_iso_to_epoch(save.get("updated_at")) or 0.0)
        tmp_zip = os.path.join(self._data_dir, "pc-saves", f"{int(rom_id)}.download.zip")
        try:
            self._file_store.make_dirs(os.path.dirname(tmp_zip))
            self._romm_api.download_save(int(newest["id"]), tmp_zip)
            self._file_store.make_dirs(target)
            self._file_store.extract_zip(tmp_zip, target, prefix_user)
        except Exception as exc:
            self._logger.warning(f"PC save restore for rom {rom_id} failed: {exc}")
            return {"success": False, "synced": 0, "message": f"Could not restore the save: {exc}"}
        finally:
            self._remove_quietly(tmp_zip)
        name = newest.get("file_name") or newest.get("id")
        self._logger.info(f"PC save restored for rom {rom_id}: {name} -> {target}")
        return {"success": True, "synced": 1, "message": f"Restored {name}"}

    def capture(self, rom_id: int) -> dict[str, Any]:
        """Zip the game's save folder and upload it, after a session."""
        rom = self._rom(rom_id)
        if rom is None or not is_windows_platform(rom.platform_slug):
            return {"success": True, "uploaded": 0, "message": "Not a Windows game"}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {"success": True, "uploaded": 0, "message": "No Proton prefix for this game yet"}
        target = self._target_dir(rom, prefix_user)
        if target is None or not os.path.isdir(target):
            return {"success": True, "uploaded": 0, "message": "No save folder found in the game's prefix yet"}
        zip_path = os.path.join(self._data_dir, "pc-saves", f"{int(rom_id)}.zip")
        try:
            size = self._file_store.zip_dir(target, zip_path)
            if size <= 0:
                return {"success": True, "uploaded": 0, "message": "The save folder is empty"}
            self._romm_api.upload_save(int(rom_id), zip_path, PC_SAVE_EMULATOR, slot=PC_SAVE_SLOT)
        except Exception as exc:
            self._logger.warning(f"PC save capture for rom {rom_id} failed: {exc}")
            return {"success": False, "uploaded": 0, "message": f"Could not upload the save: {exc}"}
        finally:
            self._remove_quietly(zip_path)
        self._logger.info(f"PC save uploaded for rom {rom_id}: {target} ({size} bytes)")
        return {"success": True, "uploaded": 1, "message": f"Uploaded {size} bytes"}

    # -- rows and paths --------------------------------------------------------

    def _rom(self, rom_id: int) -> Rom | None:
        with self._uow_factory() as uow:
            return uow.roms.get(int(rom_id))

    def _prefix_user(self, rom: Rom) -> str | None:
        """The Windows user folder of *rom*'s prefix, or ``None`` when it has none."""
        app_id = rom.shortcut_app_id
        if app_id is None:
            return None
        root = self._steam_config.compatdata_root()
        if root is None:
            return None
        prefix_user = prefix_user_dir(root, int(app_id))
        return prefix_user if os.path.isdir(prefix_user) else None

    def _target_dir(self, rom: Rom, prefix_user: str) -> str | None:
        """The folder this ROM's saves live in, remembered once it is chosen."""
        stored = self._stored_relative(rom.rom_id)
        if stored:
            resolved = resolve_relative(prefix_user, stored)
            if resolved is not None and os.path.isdir(resolved):
                return resolved
        picked = pick_save_dir(self._candidates(prefix_user), rom.name)
        if picked is None:
            return None
        relative = relative_to_prefix(prefix_user, picked.path)
        if relative is None:
            return None
        self._store_relative(rom.rom_id, relative)
        if self._log_pick is not None:
            self._log_pick(rom.name, relative)
        self._logger.info(f"PC save folder for rom {rom.rom_id} ({rom.name}): {relative}")
        return picked.path

    def _candidates(self, prefix_user: str) -> list[SaveCandidate]:
        """Every folder under the save roots that could hold a game's saves."""
        found: list[SaveCandidate] = []
        for root_name in SAVE_ROOTS:
            root = os.path.join(prefix_user, *root_name.split("/"))
            if not os.path.isdir(root):
                continue
            for path, name, depth in self._walk_dirs(root, 1):
                if depth > _MAX_DEPTH:
                    continue
                found.append(
                    SaveCandidate(
                        path=path,
                        name=name,
                        file_count=self._count_files(path),
                        mtime=self._mtime(path),
                    )
                )
        return found

    def _walk_dirs(self, root: str, depth: int) -> list[tuple[str, str, int]]:
        """``(path, name, depth)`` for the directories under *root*, breadth first."""
        out: list[tuple[str, str, int]] = []
        try:
            entries = sorted(os.listdir(root))
        except OSError:
            return out
        for name in entries:
            path = os.path.join(root, name)
            if not os.path.isdir(path):
                continue
            out.append((path, name, depth))
            if depth < _MAX_DEPTH:
                out.extend(self._walk_dirs(path, depth + 1))
        return out

    def _count_files(self, directory: str) -> int:
        total = 0
        for _root, _dirs, files in os.walk(directory):
            total += len(files)
            if total > 5000:  # a save folder is small; stop counting a library
                break
        return total

    @staticmethod
    def _mtime(path: str) -> float:
        try:
            return os.path.getmtime(path)
        except OSError:
            return 0.0

    def _stored_relative(self, rom_id: int) -> str | None:
        with self._uow_factory() as uow:
            return uow.kv_config.get(f"{_KV_PREFIX}{int(rom_id)}")

    def _store_relative(self, rom_id: int, relative: str) -> None:
        with self._uow_factory() as uow:
            uow.kv_config.set(f"{_KV_PREFIX}{int(rom_id)}", relative)

    def _remove_quietly(self, path: str) -> None:
        try:
            if self._file_store.exists(path):
                self._file_store.remove_file(path)
        except Exception as exc:
            self._logger.warning(f"PC save: could not remove {path}: {exc}")
