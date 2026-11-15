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
    ARCHIVE_FOLDER_NOTE,
    SAVE_ROOTS,
    SaveCandidate,
    folder_from_note,
    is_save_candidate,
    name_score,
    pick_save_dir,
    prefix_user_dir,
    relative_to_prefix,
    resolve_relative,
)
from domain.save_answer import SAVE_SHAPE_UNSUPPORTED_REASON
from domain.windows_launch import is_windows_platform
from services.saves._settings import save_sync_enabled, sync_after_exit, sync_before_launch

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.romm.romm_api import RommApiAdapter
    from adapters.steam_config import SteamConfigAdapter
    from domain.rom import Rom
    from services.protocols import DownloadFileStore, UnitOfWorkFactory
    from services.protocols.cross_service import SessionPostExitSync

#: The emulator label a PC save is stored under on the server. RomM keys saves by
#: (rom, emulator, slot); ``proton`` says what wrote it without pretending to be
#: a libretro core.
PC_SAVE_EMULATOR = "proton"

#: One slot for the prototype: a PC game's profile is a single set, not a
#: battery file with autosave/manual variants.
PC_SAVE_SLOT = "default"

#: ``kv_config`` key prefix for the remembered folder, per ROM.
_KV_PREFIX = "pc_save_dir:"

#: Set to ``"1"`` when the remembered folder was chosen by hand, so a recomputed
#: guess never overwrites a person's decision.
_MANUAL_PREFIX = "pc_save_dir_manual:"

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
    #: The live ``settings.json`` dict. The PC path honours the same three toggles
    #: as the emulator path — without this it would sync while the user has save
    #: sync, pre-launch sync, or post-exit sync switched off.
    settings: dict[str, Any]
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
        self._settings = config.settings
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
        if not save_sync_enabled(self._settings):
            return {"success": True, "synced": 0, "message": "Save sync is off"}
        if not sync_before_launch(self._settings):
            return {"success": True, "synced": 0, "message": "Pre-launch sync disabled"}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {"success": True, "synced": 0, "message": "No Proton prefix for this game yet"}
        try:
            saves = self._romm_api.list_saves(int(rom_id))
        except Exception as exc:
            self._logger.warning(f"PC save restore for rom {rom_id}: listing saves failed: {exc}")
            return {"success": False, "synced": 0, "message": f"Could not list saves: {exc}"}
        if not saves:
            return {"success": True, "synced": 0, "message": "No save on the server yet"}
        newest = max(saves, key=lambda save: parse_iso_to_epoch(save.get("updated_at")) or 0.0)
        tmp_zip = os.path.join(self._data_dir, "pc-saves", f"{int(rom_id)}.download.zip")
        # The archive states the folder it came from, relative to the Wine user
        # directory. That is what lets a second machine put the save back without
        # guessing: the folder is created if this device has never seen it, and the
        # game finds its own progress on the first launch there. Archives written
        # before the note existed fall back to guessing locally, which is all that
        # was possible then.
        recorded: str | None = None
        try:
            self._file_store.make_dirs(os.path.dirname(tmp_zip))
            self._romm_api.download_save(int(newest["id"]), tmp_zip)
            raw_note = self._file_store.read_zip_entry(tmp_zip, ARCHIVE_FOLDER_NOTE)
            recorded = folder_from_note(raw_note)
            if raw_note is not None and recorded is None:
                # The save states where it goes and we will not follow it. Guessing a
                # folder instead would drop another device's progress where the game
                # never reads it — a silent loss dressed up as a restore.
                self._logger.warning(
                    f"PC save restore for rom {rom_id}: the save records the folder {raw_note!r}, "
                    "which is not a path this plugin will write to"
                )
                return {
                    "success": False,
                    "synced": 0,
                    "message": "The save records a folder we cannot follow",
                }
            if recorded is not None:
                target = resolve_relative(prefix_user, recorded)
                if target is None:
                    self._logger.warning(
                        f"PC save restore for rom {rom_id}: the save records {recorded!r}, "
                        "which is outside this game's Wine prefix"
                    )
                    return {
                        "success": False,
                        "synced": 0,
                        "message": "The save records a folder outside this game's Wine prefix",
                    }
                base = prefix_user
            else:
                guessed = self._target_dir(rom, prefix_user)
                if guessed is None:
                    return {
                        "success": True,
                        "synced": 0,
                        "message": "No save folder found in the game's prefix yet",
                    }
                target = base = guessed
            self._file_store.make_dirs(target)
            self._file_store.extract_zip(tmp_zip, base, prefix_user, skip_members=(ARCHIVE_FOLDER_NOTE,))
        except Exception as exc:
            self._logger.warning(f"PC save restore for rom {rom_id} failed: {exc}")
            return {"success": False, "synced": 0, "message": f"Could not restore the save: {exc}"}
        finally:
            self._remove_quietly(tmp_zip)
        # This device now knows where the game saves, from the save itself — so the
        # capture after this session reads the same folder the restore wrote to. A
        # hand-picked folder is a person's decision and is left alone.
        if recorded is not None and not self._is_manual(rom.rom_id):
            self._store_relative(rom.rom_id, recorded)
        name = newest.get("file_name") or newest.get("id")
        origin = "recorded in the save" if recorded is not None else "guessed on this device"
        self._logger.info(f"PC save restored for rom {rom_id}: {name} -> {target} ({origin})")
        return {"success": True, "synced": 1, "message": f"Restored {name}"}

    def capture(self, rom_id: int) -> dict[str, Any]:
        """Zip the game's save folder and upload it, after a session."""
        rom = self._rom(rom_id)
        if rom is None or not is_windows_platform(rom.platform_slug):
            return {"success": True, "uploaded": 0, "message": "Not a Windows game"}
        if not save_sync_enabled(self._settings):
            return {"success": True, "uploaded": 0, "message": "Save sync is off"}
        if not sync_after_exit(self._settings):
            return {"success": True, "uploaded": 0, "message": "Post-exit sync disabled"}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {"success": True, "uploaded": 0, "message": "No Proton prefix for this game yet"}
        target = self._target_dir(rom, prefix_user)
        if target is None or not os.path.isdir(target):
            return {"success": True, "uploaded": 0, "message": "No save folder found in the game's prefix yet"}
        zip_path = os.path.join(self._data_dir, "pc-saves", f"{int(rom_id)}.zip")
        # The archive carries its own folder, not just its files: another device
        # reads the note before unpacking and needs no local knowledge at all.
        relative = relative_to_prefix(prefix_user, target)
        try:
            size = self._file_store.zip_dir(
                target,
                zip_path,
                arc_prefix=relative or "",
                marker=(ARCHIVE_FOLDER_NOTE, relative) if relative else None,
            )
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

    # -- what the game panel shows ---------------------------------------------

    def get_save_folder(self, rom_id: int) -> dict[str, Any]:
        """The folder this game's saves live in, and the ones it could be instead.

        ``{"windows": False}`` for anything that is not a Windows game — the
        answer for most pages, and not a failure. A read never guesses and
        stores: the folder is chosen on the first capture or restore, so opening
        a game page cannot quietly decide where a game saves.
        """
        rom = self._rom(rom_id)
        if rom is None or not is_windows_platform(rom.platform_slug):
            return {"windows": False}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {
                "windows": True,
                "prefix": False,
                "folder": None,
                "manual": False,
                "candidates": [],
                "message": "This game's Wine prefix does not exist yet — launch it once, then reopen this page.",
            }
        candidates = self._ranked_candidates(rom, prefix_user)
        stored = self._stored_relative(rom_id)
        manual = self._is_manual(rom_id)
        resolved = resolve_relative(prefix_user, stored) if stored else None
        chosen = stored if resolved is not None and os.path.isdir(resolved) else None
        if chosen is None and candidates:
            chosen = candidates[0]["path"]
            manual = False
        return {
            "windows": True,
            "prefix": True,
            "folder": chosen,
            "manual": manual and chosen is not None,
            "candidates": candidates,
            "message": None if candidates else "No folder in this game's prefix looks like a save yet.",
        }

    def set_save_folder(self, rom_id: int, relative_path: str | None) -> dict[str, Any]:
        """Choose this game's save folder by hand, or hand the choice back.

        *relative_path* must be inside the game's own prefix; an empty value
        forgets the choice so the next capture picks again. The folder is stored
        relative to the prefix, the same shape the automatic pick uses, so a
        manually chosen folder and a guessed one behave identically afterwards.
        """
        rom = self._rom(rom_id)
        if rom is None or not is_windows_platform(rom.platform_slug):
            return {"success": False, "message": "Not a Windows game"}
        prefix_user = self._prefix_user(rom)
        if prefix_user is None:
            return {"success": False, "message": "This game's Wine prefix does not exist yet"}
        if not relative_path:
            self._forget_folder(rom_id)
            picked = pick_save_dir(self._candidates(prefix_user), rom.name)
            chosen = relative_to_prefix(prefix_user, picked.path) if picked is not None else None
            if chosen is not None:
                self._store_relative(rom_id, chosen)
            return {"success": True, "folder": chosen, "manual": False}
        target = resolve_relative(prefix_user, relative_path)
        if target is None or not os.path.isdir(target):
            return {"success": False, "message": "That folder is not inside this game's Wine prefix"}
        relative = relative_to_prefix(prefix_user, target)
        if relative is None:
            return {"success": False, "message": "That folder is not inside this game's Wine prefix"}
        self._store_relative(rom_id, relative)
        self._mark_manual(rom_id)
        self._logger.info(f"PC save folder for rom {rom_id} set by hand: {relative}")
        return {"success": True, "folder": relative, "manual": True}

    def _ranked_candidates(self, rom: Rom, prefix_user: str) -> list[dict[str, Any]]:
        """The folders a save could be in, likeliest first — the automatic pick's own rule.

        The same predicate decides membership here as decides the guess: a folder
        with no files, or one that is Windows housekeeping (``Temp``, ``dxvk``,
        the shell's own Documents subfolders), is not offered. Measured on the
        reference Deck, listing every scanned directory made a 13-row menu in which
        the game's own folder was one line among a dozen empty ones.
        """
        candidates = [c for c in self._candidates(prefix_user) if is_save_candidate(c.name, c.file_count)]
        ranked = sorted(
            candidates,
            key=lambda c: (-name_score(rom.name, c.name), -c.mtime, c.name),
        )
        return [
            {
                "path": relative_to_prefix(prefix_user, c.path),
                "files": c.file_count,
                "modified_at": c.mtime,
            }
            for c in ranked
            if relative_to_prefix(prefix_user, c.path) is not None
        ]

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

    def _is_manual(self, rom_id: int) -> bool:
        with self._uow_factory() as uow:
            return uow.kv_config.get(f"{_MANUAL_PREFIX}{int(rom_id)}") == "1"

    def _mark_manual(self, rom_id: int) -> None:
        with self._uow_factory() as uow:
            uow.kv_config.set(f"{_MANUAL_PREFIX}{int(rom_id)}", "1")

    def _forget_folder(self, rom_id: int) -> None:
        with self._uow_factory() as uow:
            for key in (f"{_KV_PREFIX}{int(rom_id)}", f"{_MANUAL_PREFIX}{int(rom_id)}"):
                uow.kv_config.delete(key)

    def _store_relative(self, rom_id: int, relative: str) -> None:
        with self._uow_factory() as uow:
            uow.kv_config.set(f"{_KV_PREFIX}{int(rom_id)}", relative)

    def _remove_quietly(self, path: str) -> None:
        try:
            if self._file_store.exists(path):
                self._file_store.remove_file(path)
        except Exception as exc:
            self._logger.warning(f"PC save: could not remove {path}: {exc}")


class PcSaveSyncExitHook:
    """The session lifecycle's post-exit sync, routed by platform.

    A session ends through ``SessionLifecycleService``, which holds its own
    ``post_exit_sync`` collaborator — measured on the reference Deck, the exit of
    rom 7159 reached the emulator pipeline even though the handler was branched,
    and logged ``do_sync_rom_saves(7159): system=win … server_saves=0`` while the
    game's folder sat unread in the prefix. This is the collaborator the
    lifecycle gets instead: a Windows game goes to the PC folder, everything else
    to the emulator service, so the two entry points cannot disagree.
    """

    def __init__(self, *, pc: PcSaveSync, emulator: SessionPostExitSync, loop: Any) -> None:
        self._pc = pc
        self._emulator = emulator
        self._loop = loop

    async def post_exit_sync(self, rom_id: int) -> dict[str, Any]:
        if not self._pc.handles(rom_id):
            return await self._emulator.post_exit_sync(rom_id)
        result = await self._loop.run_in_executor(None, self._pc.capture, int(rom_id))
        uploaded = int(result.get("uploaded") or 0)
        # The lifecycle renders a toast from this shape. A PC game with nothing to
        # carry yet (never saved, or its folder is not one we can name) is a benign
        # skip, not a failure: the same reason the emulator side uses so no toast
        # fires and the frontend's benign list stays in agreement.
        if uploaded == 0 and result.get("success", True):
            return {
                "offline": False,
                "success": False,
                "reason": SAVE_SHAPE_UNSUPPORTED_REASON,
                "synced": 0,
                "uploaded": 0,
                "downloaded": 0,
                "conflicts": [],
            }
        return {
            "offline": False,
            "success": bool(result.get("success", True)),
            "synced": uploaded,
            "uploaded": uploaded,
            "downloaded": 0,
            "conflicts": [],
        }
