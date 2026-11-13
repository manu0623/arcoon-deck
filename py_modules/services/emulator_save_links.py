"""Keep every standalone emulator pointed at the save tree the plugin syncs.

The platforms this covers are the ones the plugin already redirects its own runtime
into — today PSP, whose savedata is a folder set under ``<saves>/psp/PSP/SAVEDATA``,
and 3DS, whose title tree lives under ``<saves>/3ds/sdmc/Nintendo 3DS``. A standalone
PPSSPP is the case the first measurement caught: installed by this plugin's own install
action, it read an empty memory stick while the game's save sat in the plugin's
directory.

**Which providers take part is the domain's answer, not this service's.** An install
whose emulator has a declared save subdir is linked at the folder *its* provider keeps
config in: ``~/.config/ppsspp`` for the AppImage, ``~/.var/app/org.ppsspp.PPSSPP/
config/ppsspp`` for the flatpak. Both are read through the same roots the config
reader already computes, so a provider this code has not met is simply not linked
rather than linked in a place that does not exist.

**It runs at startup and after an install**, for the same reason the emulator tiles
do: the folder has to be pointed before the emulator is first opened, and an emulator
installed later (by the install button, or by the user) has to be caught without the
reader doing anything about it.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.emulator_config import layout_for as config_layout_for
from domain.emulator_save_link import SaveLink, link_for

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.emulator_save_link import LinkOutcome
    from domain.emulator_registry import InstalledEmulator


class InstallsReader:
    """The scanner, as this service needs it: every install, whatever the system."""

    def installs(self) -> list[InstalledEmulator]: ...  # pragma: no cover - protocol


class ConfigRootsReader:
    """The config reader, narrowed to the one question asked here."""

    def root_variants(self, install: InstalledEmulator, *, app_dir: str) -> tuple[Any, ...]: ...  # pragma: no cover


@dataclass(frozen=True)
class EmulatorSaveLinkConfig:
    """Everything the service is handed at construction."""

    logger: logging.Logger
    external_emulators: InstallsReader
    config_reader: ConfigRootsReader
    saves_path: Callable[[], str]
    apply: Callable[[SaveLink], LinkOutcome]
    #: PS2's extra step, taken once PCSX2 is linked: the bank needs a folder memory
    #: card, and the libretro core's own card folder is pointed at it (it ignores
    #: ``savefile_directory`` for cards). ``None`` for a caller with no card source.
    ps2_cards: Callable[[str], dict[str, str]] | None = None


class EmulatorSaveLinkService:
    """Makes the links, one emulator at a time, and reports each outcome."""

    def __init__(self, *, config: EmulatorSaveLinkConfig) -> None:
        self._logger = config.logger
        self._external_emulators = config.external_emulators
        self._config_reader = config.config_reader
        self._saves_path = config.saves_path
        self._apply = config.apply
        self._ps2_cards = config.ps2_cards

    async def ensure_all(self) -> dict[str, Any]:
        """Every install that needs a link, linked. Runs the filesystem work off-thread."""
        return await asyncio.get_running_loop().run_in_executor(None, self._ensure_blocking, None)

    async def ensure_for_platform(self, platform: str) -> dict[str, Any]:
        """The same, narrowed to the installs that can play *platform*."""
        return await asyncio.get_running_loop().run_in_executor(None, self._ensure_blocking, platform)

    def _ensure_blocking(self, platform: str | None) -> dict[str, Any]:
        saves_root = self._saves_path()
        outcomes: list[dict[str, Any]] = []
        for install in self._external_emulators.installs():
            if platform is not None and not install.plays(platform):
                continue
            link = self._link_for(install, saves_root)
            if link is None:
                continue
            outcome = self._apply(link)
            outcomes.append(
                {
                    "emulator": outcome.emulator,
                    "provider": install.provider,
                    "status": outcome.status,
                    "emulator_dir": outcome.emulator_dir,
                    "owned_dir": outcome.owned_dir,
                    "adopted": outcome.adopted,
                    "conflicts": list(outcome.conflicts),
                    "note": outcome.note,
                }
            )
            if outcome.status == "failed":
                self._logger.warning(
                    f"Emulator saves: could not link {outcome.emulator} at {outcome.emulator_dir}: {outcome.note}"
                )
        cards = self._ensure_ps2_cards(outcomes, saves_root)
        return {"saves_root": saves_root, "links": outcomes, "ps2_cards": cards}

    def _ensure_ps2_cards(self, outcomes: list[dict[str, Any]], saves_root: str) -> dict[str, str] | None:
        """The ps2 card step, run only when this pass linked PCSX2.

        Keyed off the link rather than the platform: a Deck with no PCSX2 installed has
        nothing to point at a card, and creating one in the bank for an emulator nobody
        runs would be an invented save root.
        """
        if self._ps2_cards is None or not any(outcome["emulator"] == "pcsx2" for outcome in outcomes):
            return None
        cards = self._ps2_cards(os.path.join(saves_root, "ps2"))
        self._logger.info(f"Emulator saves: ps2 card {cards}")
        return cards

    def _link_for(self, install: InstalledEmulator, saves_root: str) -> SaveLink | None:
        """The plan for one install, with its own provider's config root expanded."""
        layout = config_layout_for(install.id)
        if layout is None:
            return None
        roots = self._config_reader.root_variants(install, app_dir=layout.app_dir)
        if not roots:
            return None
        # Both roots are handed over: which one the saves hang off is the emulator's own
        # fact (``domain.emulator_save_link``), and the reader computed both together so a
        # flatpak's ``data/`` is the sandbox's, never the host's.
        return link_for(install, config_root=roots[0].config, data_root=roots[0].data, saves_root=saves_root)
