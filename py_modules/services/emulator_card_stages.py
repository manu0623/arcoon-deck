"""Points a declared emulator's memory card at the bank, and stages one game into it.

The settings half runs at startup, like the BIOS folder's: the emulator's card directory has
to be the plugin's before it is first opened, and an emulator installed later has to be
caught without anyone pressing anything.

The card half runs around a launch — :meth:`stage` before the game starts and :meth:`adopt`
after it exits — because the emulator opens one fixed card file. Both take the same ROM, so
the two halves can never disagree about which game's card is in the slot.

**Which emulators take part is the domain's answer, not this service's**: only an emulator in
:data:`~domain.emulator_card_stage.CARD_STAGES` is pointed, and only when the launch this
machine would resolve for the ROM is that emulator. A ROM launched by a core, or by an
emulator whose cards the plugin has not read, is left exactly as it was.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.emulator_card_stage import card_home_for, stage_plan, stages_emulator
from domain.save_bank import canonical_platform

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.emulator_card_stage import CardHomeOutcome
    from domain.emulator_card_stage import CardHome, CardStagePlan
    from domain.emulator_registry import InstalledEmulator


class InstallsReader:
    """The scanner, as this service needs it: every install, whatever the system."""

    def installs(self) -> list[InstalledEmulator]: ...  # pragma: no cover - protocol


class ConfigCandidatesReader:
    """The config reader, narrowed to the one question asked here."""

    def candidates(self, install: InstalledEmulator) -> tuple[tuple[str, Any], ...]: ...  # pragma: no cover


@dataclass(frozen=True, slots=True)
class EmulatorCardStageConfig:
    """Everything the service is handed at construction."""

    logger: logging.Logger
    external_emulators: InstallsReader
    config_reader: ConfigCandidatesReader
    saves_path: Callable[[], str]
    rom_info: Callable[[int], dict[str, Any] | None]
    active_emulator: Callable[[int], Any | None]
    config_exists: Callable[[str], bool]
    apply_home: Callable[[CardHome], CardHomeOutcome]
    stage_card: Callable[[CardStagePlan], str]
    adopt_card: Callable[[CardStagePlan], str]


class EmulatorCardStageService:
    """Keeps the declared emulators pointed, and stages one game's card at a time."""

    def __init__(self, *, config: EmulatorCardStageConfig) -> None:
        self._logger = config.logger
        self._external_emulators = config.external_emulators
        self._config_reader = config.config_reader
        self._saves_path = config.saves_path
        self._rom_info = config.rom_info
        self._active_emulator = config.active_emulator
        self._config_exists = config.config_exists
        self._apply_home = config.apply_home
        self._stage_card = config.stage_card
        self._adopt_card = config.adopt_card

    async def ensure_homes(self) -> dict[str, Any]:
        """Point every declared emulator's card folder at this app's tree."""
        return await asyncio.get_running_loop().run_in_executor(None, self._ensure_blocking)

    def _ensure_blocking(self) -> dict[str, Any]:
        homes: list[dict[str, Any]] = []
        for install in self._external_emulators.installs():
            if not stages_emulator(install.id):
                continue
            home = self._home_for(install)
            if home is None:
                continue
            outcome = self._apply_home(home)
            homes.append(
                {
                    "emulator": outcome.emulator,
                    "provider": install.provider,
                    "status": outcome.status,
                    "directory": outcome.directory,
                    "config_path": outcome.config_path,
                }
            )
            if outcome.changed:
                self._logger.info(f"Emulator cards: {outcome.emulator} now keeps cards in {outcome.directory}")
        return {"homes": homes}

    def stage(self, rom_id: int) -> dict[str, Any]:
        """Put this game's card in the slot the emulator opens, before it starts."""
        plan = self._plan_for(int(rom_id))
        if plan is None:
            return {"status": "not-staged"}
        status = self._stage_card(plan)
        if status in {"staged", "cleared"}:
            self._logger.info(f"Emulator cards: rom {rom_id} {status} {os.path.basename(plan.bank_card)}")
        return {"status": status, "bank_card": plan.bank_card, "staged_card": plan.staged_card}

    def adopt(self, rom_id: int) -> dict[str, Any]:
        """Take the card the emulator wrote back into this game's bank file."""
        plan = self._plan_for(int(rom_id))
        if plan is None:
            return {"status": "not-adopted"}
        status = self._adopt_card(plan)
        if status == "adopted":
            self._logger.info(f"Emulator cards: rom {rom_id} adopted {os.path.basename(plan.bank_card)}")
        return {"status": status, "bank_card": plan.bank_card}

    def _plan_for(self, rom_id: int) -> CardStagePlan | None:
        """The staging plan for this ROM, or ``None`` when it is not a staged launch."""
        info = self._rom_info(rom_id)
        if not info:
            return None
        emulator = self._active_emulator(rom_id)
        emulator_id = getattr(emulator, "emulator", None)
        if not stages_emulator(emulator_id):
            return None
        platform = info.get("system") or info.get("platform_slug") or ""
        install = next(
            (candidate for candidate in self._external_emulators.installs() if candidate.id == emulator_id), None
        )
        if install is None:
            return None
        home = self._home_for(install, platform=platform)
        if home is None:
            return None
        return stage_plan(home, rom_stem=os.path.splitext(os.path.basename(info["file_path"]))[0])

    def _home_for(self, install: InstalledEmulator, *, platform: str | None = None) -> CardHome | None:
        """The settings write one install needs, with its own settings file probed."""
        platforms = install.definition.platforms
        resolved = platform or (platforms[0] if platforms else "")
        if not resolved or canonical_platform(resolved) != canonical_platform(platforms[0] if platforms else ""):
            return None
        for path, _roots in self._config_reader.candidates(install):
            if self._config_exists(path):
                return card_home_for(
                    emulator_id=install.id,
                    platform=resolved,
                    config_path=path,
                    saves_root=self._saves_path(),
                )
        return None
