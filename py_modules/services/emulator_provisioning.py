"""EmulatorProvisioningService — obtaining the standalone emulators a system offers.

Core provisioning answers the libretro half of "can this platform launch?"; this is the
other half. A system the inventory describes only with standalone emulators (Switch, PS3,
3DS, Wii U) has no core to install, and until now the answer was "install it yourself",
which in Game Mode means not at all.

Which emulators and where they come from is the inventory's statement, not this service's:
each row that names a source becomes one install, and a row that names none is reported as
the emulator the user still has to fetch by hand. Nothing here verifies a download — the
adapter refuses anything it cannot hash — and a failure is reported per emulator rather
than aborting the batch, exactly as a missing core is.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.emulator_install import FlatpakInstall, ReleaseInstall, install_plan

if TYPE_CHECKING:
    import asyncio
    import logging
    from collections.abc import Callable

    from domain.owned_inventory import InventoryEmulator, InventoryPlatform


@dataclass(frozen=True)
class EmulatorProvisioningConfig:
    """What the service needs: the inventory, the installer, and a loop."""

    loop: asyncio.AbstractEventLoop
    logger: logging.Logger
    inventory: Callable[[str], InventoryPlatform | None]
    installer: Callable[[InventoryEmulator], dict[str, Any]]


class EmulatorProvisioningService:
    """Install the standalone emulators one system's inventory names a source for."""

    def __init__(self, *, config: EmulatorProvisioningConfig) -> None:
        self._loop = config.loop
        self._logger = config.logger
        self._inventory = config.inventory
        self._installer = config.installer

    def describe_for_system(self, system_name: str) -> dict[str, Any]:
        """What *system_name* offers and where each row comes from, without installing.

        A surface needs this before it can show a button: which rows have a source, which
        source each one is (a store id or a release repository), and which rows are the
        emulator the user installs by hand. It reads the inventory and nothing else, so it
        is cheap enough to ask on every platform selection.
        """
        platform = self._inventory(system_name)
        if platform is None:
            return {"system": system_name, "known": False, "emulators": [], "manual": []}
        return {
            "system": system_name,
            "known": True,
            "emulators": [_describe(emulator) for emulator in platform.emulators if install_plan(emulator) is not None],
            "manual": [emulator.label for emulator in platform.emulators if install_plan(emulator) is None],
        }

    async def ensure_for_system(self, system_name: str, *, label: str | None = None) -> dict[str, Any]:
        """Install what *system_name* names a source for, and report every outcome.

        ``reason`` is set only for the answers a caller can act on: ``unknown_system``
        (the inventory does not describe this system), ``unknown_emulator`` (a label this
        system does not offer) and ``no_source`` (it describes the system, but every row
        is an emulator the user installs themselves).

        *label* narrows the work to one row, which is what a surface showing per-emulator
        progress calls once per row: one install at a time, each reporting as it lands.
        Installs run one at a time in the executor either way — they are hundreds of
        megabytes each, and serialising them keeps the progress story simple without
        blocking the event loop.
        """
        platform = self._inventory(system_name)
        if platform is None:
            return {"success": False, "reason": "unknown_system", "system": system_name, "emulators": []}
        installable = [emulator for emulator in platform.emulators if install_plan(emulator) is not None]
        manual = [emulator.label for emulator in platform.emulators if install_plan(emulator) is None]
        if label is not None:
            matched = [emulator for emulator in installable if emulator.label == label]
            if not matched:
                return {
                    "success": False,
                    "reason": "unknown_emulator",
                    "system": system_name,
                    "emulators": [],
                    "manual": manual,
                }
            installable = matched
        if not installable:
            return {
                "success": False,
                "reason": "no_source",
                "system": system_name,
                "emulators": [],
                "manual": manual,
            }
        results: list[dict[str, Any]] = [
            await self._loop.run_in_executor(None, self._installer, emulator) for emulator in installable
        ]
        installed = [str(result.get("label")) for result in results if result.get("ok")]
        failed = [result for result in results if not result.get("ok")]
        if installed:
            self._logger.info(f"emulator_provisioning: {system_name}: installed {installed}")
        if failed:
            self._logger.warning(f"emulator_provisioning: {system_name}: failed {failed}")
        return {
            "success": not failed,
            "system": system_name,
            "emulators": results,
            "installed": installed,
            "failed": failed,
            "manual": manual,
        }


def _describe(emulator: InventoryEmulator) -> dict[str, Any]:
    """One row as a surface reads it: the label, and the source it would use.

    ``prefer_newest`` is the same call the installer makes, so a row that says "release"
    is the row that downloads a release — the two cannot disagree about which channel is
    in play.
    """
    plan = install_plan(emulator)
    if isinstance(plan, FlatpakInstall):
        return {"label": emulator.label, "source": "store", "app_id": plan.app_id, "repo": None}
    if isinstance(plan, ReleaseInstall):
        return {"label": emulator.label, "source": "release", "app_id": None, "repo": plan.repo}
    return {"label": emulator.label, "source": None, "app_id": None, "repo": None}
