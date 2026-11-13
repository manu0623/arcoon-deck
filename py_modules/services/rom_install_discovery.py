"""Adopt a ROM the library knows and the disk already holds.

The plugin records an install only where its own download put the file
(``services/downloads``). A library that arrived another way — an EmuDeck tree from before
this app existed, a folder copied from a desktop, a game downloaded before a structure
change — has ROM rows and no install rows. Everything downstream reads the install row: the
save layer refuses with ``needs: save_id`` because it will not read a header of a file it
cannot name (``services/saves/rom_info``), and the launch bake has no path either.

Measured on the reference Deck: three ``.3ds`` files in ``~/Emulation/roms/n3ds`` — one with
128 played sessions — while ``rom_installs`` held nothing for the platform, so the 3DS save
tree that had just been linked could not be asked about a single game.

**Adoption is a claim, so it is stated narrowly.** A file is adopted only when it is the one
the row names: the same ``fs_name`` in the platform's own directory, or — when the row
carries a bare name, as RomM often does — a unique stem match there. Two candidates are not
guessed between, a directory is not entered (which file inside it launches is a decision the
download path makes with its M3U and collapse rules), and a root is only searched if it is
one this plugin owns under a structure it can have shipped (ADR-0046): the point is the
user's own library, never "wherever a path happens to be".
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.rom_files import is_launchable_target
from domain.rom_install import RomInstall
from lib.path_safety import coerce_safe_component

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable
    from typing import Protocol

    from domain.rom import Rom

    class FileLister(Protocol):
        def listdir(self, path: str) -> list[str]: ...  # pragma: no cover - protocol

        def is_file(self, path: str) -> bool: ...  # pragma: no cover - protocol

        def is_dir(self, path: str) -> bool: ...  # pragma: no cover - protocol


FOUND = "found"
AMBIGUOUS = "ambiguous"
DIRECTORY = "directory"
#: No file for this row anywhere the plugin looks — the ordinary answer for a library
#: whose content genuinely is not on this machine.
NO_MATCH = "none"


@dataclass(frozen=True)
class ContentMatch:
    """What the disk had for one ROM: the named file, a tie, a folder, or nothing."""

    kind: str
    path: str = ""


@dataclass(frozen=True)
class RomInstallDiscoveryConfig:
    """Everything the discovery needs, injected."""

    logger: logging.Logger
    uow_factory: Callable[[], Any]
    file_store: FileLister
    roms_roots: Callable[[], tuple[str, ...]]
    resolve_system: Callable[[str], str]
    system_extensions: Callable[[str], frozenset[str]]
    now: Callable[[], str]


class RomInstallDiscoveryService:
    """Records an install for a known ROM whose content is already on disk."""

    def __init__(self, *, config: RomInstallDiscoveryConfig) -> None:
        self._logger = config.logger
        self._uow_factory = config.uow_factory
        self._file_store = config.file_store
        self._roms_roots = config.roms_roots
        self._resolve_system = config.resolve_system
        self._system_extensions = config.system_extensions
        self._now = config.now

    async def adopt_found_content(self) -> dict[str, Any]:
        """The whole pass, off the event loop. Returns what happened, per ROM."""
        return await asyncio.get_running_loop().run_in_executor(None, self._adopt_blocking)

    def _adopt_blocking(self) -> dict[str, Any]:
        roots = self._roms_roots()
        with self._uow_factory() as uow:
            installed = {install.rom_id for install in uow.rom_installs.iter_all()}
            candidates = [rom for rom in uow.roms.iter_all() if rom.rom_id not in installed]

        adopted: list[dict[str, Any]] = []
        ambiguous: list[dict[str, Any]] = []
        directories: list[dict[str, Any]] = []
        for rom in candidates:
            match = self._find(rom, roots)
            if match.kind == FOUND:
                entry = self._install(rom, match.path)
                if entry is not None:
                    adopted.append(entry)
            elif match.kind == AMBIGUOUS:
                ambiguous.append({"rom_id": rom.rom_id, "name": rom.name})
            elif match.kind == DIRECTORY:
                # Folder-backed: which file inside launches is the download path's
                # decision (M3U, collapse rename), not a guess made here.
                directories.append({"rom_id": rom.rom_id, "name": rom.name, "path": match.path})

        if adopted:
            self._logger.info(f"ROM adoption: recorded {len(adopted)} install(s) found on disk")
        return {
            "roots": list(roots),
            "adopted": adopted,
            "ambiguous": ambiguous,
            "directories": directories,
        }

    def _find(self, rom: Rom, roots: tuple[str, ...]) -> ContentMatch:
        """The file this ROM's row names, a tie, a folder, or nothing."""
        if not rom.fs_name or not rom.platform_slug:
            return ContentMatch(NO_MATCH)
        system = self._resolve_system(rom.platform_slug)
        if not system:
            return ContentMatch(NO_MATCH)
        stem = os.path.splitext(rom.fs_name)[0].lower()
        # The system comes from a resolver, but a platform slug is still coerced to one
        # component before it is joined: this walks user-chosen trees, and a name with a
        # directory in it would search somewhere the plugin does not own.
        component, _changed = coerce_safe_component(system, "")
        if not component:
            return ContentMatch(NO_MATCH)
        for root in roots:
            platform_dir = os.path.join(root, component)
            if not self._file_store.is_dir(platform_dir):
                continue
            try:
                entries = self._file_store.listdir(platform_dir)
            except OSError:
                continue
            if rom.fs_name in entries:
                path = os.path.join(platform_dir, rom.fs_name)
                if self._file_store.is_dir(path):
                    return ContentMatch(DIRECTORY, path)
                return ContentMatch(FOUND, path)
            matches = [
                entry
                for entry in entries
                if os.path.splitext(entry)[0].lower() == stem
                and self._file_store.is_file(os.path.join(platform_dir, entry))
            ]
            if len(matches) > 1:
                return ContentMatch(AMBIGUOUS, platform_dir)
            if matches:
                return ContentMatch(FOUND, os.path.join(platform_dir, matches[0]))
        return ContentMatch(NO_MATCH)

    def _install(self, rom: Rom, file_path: str) -> dict[str, Any] | None:
        """Record the row, in its own short write UoW."""
        system = self._resolve_system(rom.platform_slug)
        launchable = is_launchable_target(file_path, None, self._system_extensions(system))
        if not launchable:
            self._logger.warning(
                f"ROM adoption: no launch target for rom_id={rom.rom_id}: {system} cannot launch '{file_path}'"
            )
        try:
            install = RomInstall.mark_installed(
                rom_id=int(rom.rom_id),
                file_path=file_path,
                rom_dir=None,
                platform_slug=rom.platform_slug,
                system=system,
                installed_at=self._now(),
                launchable=launchable,
            )
        except ValueError as exc:
            self._logger.warning(f"ROM adoption: rom_id={rom.rom_id} rejected: {exc}")
            return None
        with self._uow_factory() as uow:
            uow.rom_installs.save(install)
        return {
            "rom_id": rom.rom_id,
            "name": rom.name,
            "file_path": file_path,
            "system": system,
            "launchable": launchable,
        }
