"""Points every standalone emulator that states a BIOS folder at the plugin's tree.

The platforms this covers are the ones the plugin installs firmware for and a standalone
emulator boots with — today PlayStation, whose images the plugin downloads into
``<bios>/psx``. A standalone DuckStation is the case the first measurement caught: it
searched an SD card's per-system folder holding no ``scph`` image, so the game it was
handed closed a second after it opened while the images it needed sat in this app's tree.

**Which emulators take part is the domain's answer, not this service's.** Only an
emulator whose settings file has been read is in
:data:`~domain.emulator_bios_home.BIOS_DIRECTORY_KEYS`, and its own config layout
(:mod:`domain.emulator_config`) decides which of the candidate files to write. An
emulator nobody has read is simply not pointed rather than pointed blindly.

**It runs at startup, after an install, and before a platform is launched**, for the
same reason the save link does: the folder has to be stated before the emulator is
first opened, and an emulator installed later has to be caught without the reader
doing anything about it. The write persists, so the launch pass is a safety net rather
than the mechanism.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.emulator_bios_home import bios_home_for

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.emulator_bios_home import BiosHomeOutcome
    from domain.emulator_bios_home import BiosHome
    from domain.emulator_registry import InstalledEmulator


class InstallsReader:
    """The scanner, as this service needs it: every install, whatever the system."""

    def installs(self) -> list[InstalledEmulator]: ...  # pragma: no cover - protocol


class ConfigCandidatesReader:
    """The config reader, narrowed to the one question asked here."""

    def candidates(self, install: InstalledEmulator) -> tuple[tuple[str, Any], ...]: ...  # pragma: no cover


@dataclass(frozen=True, slots=True)
class EmulatorBiosHomeConfig:
    """Everything the service is handed at construction."""

    logger: logging.Logger
    external_emulators: InstallsReader
    config_reader: ConfigCandidatesReader
    #: The app's own BIOS root, or none while another runtime drives this machine — the
    #: plugin installs no firmware there, so it has no folder to name.
    bios_path: Callable[[], str | None]
    config_exists: Callable[[str], bool]
    apply: Callable[[BiosHome], BiosHomeOutcome]


class EmulatorBiosHomeService:
    """Points the emulators one at a time, and reports each outcome."""

    def __init__(self, *, config: EmulatorBiosHomeConfig) -> None:
        self._logger = config.logger
        self._external_emulators = config.external_emulators
        self._config_reader = config.config_reader
        self._bios_path = config.bios_path
        self._config_exists = config.config_exists
        self._apply = config.apply

    async def ensure_all(self) -> dict[str, Any]:
        """Every declared emulator pointed at this app's BIOS tree."""
        return await asyncio.get_running_loop().run_in_executor(None, self._ensure_blocking, None)

    async def ensure_for_platform(self, platform: str) -> dict[str, Any]:
        """The same, narrowed to the installs that can play *platform*."""
        return await asyncio.get_running_loop().run_in_executor(None, self._ensure_blocking, platform)

    def _ensure_blocking(self, platform: str | None) -> dict[str, Any]:
        bios_root = self._bios_path()
        if not bios_root:
            return {"bios_root": None, "homes": []}
        homes: list[dict[str, Any]] = []
        for install in self._external_emulators.installs():
            if platform is not None and not install.plays(platform):
                continue
            plan = bios_home_for(
                emulator_id=install.id,
                platforms=install.definition.platforms,
                config_path=self._config_path(install),
                bios_root=bios_root,
                platform=platform,
            )
            if plan is None:
                continue
            outcome = self._apply(plan)
            homes.append(
                {
                    "emulator": outcome.emulator,
                    "provider": install.provider,
                    "status": outcome.status,
                    "directory": outcome.directory,
                    "config_path": outcome.config_path,
                    "note": outcome.note,
                }
            )
            if outcome.changed:
                self._logger.info(f"Emulator BIOS: {outcome.emulator} now searches {outcome.directory}")
            elif outcome.status == "no-bios":
                self._logger.info(
                    f"Emulator BIOS: {outcome.emulator} left alone — {outcome.directory} ({outcome.note})"
                )
        return {"bios_root": bios_root, "homes": homes}

    def _config_path(self, install: InstalledEmulator) -> str | None:
        """The settings file this install already has, in the reader's own probe order."""
        for path, _roots in self._config_reader.candidates(install):
            if self._config_exists(path):
                return path
        return None
