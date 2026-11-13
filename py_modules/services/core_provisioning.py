"""CoreProvisioningService — filling a platform's missing libretro cores.

The owned runtime starts a RetroArch the plugin drives, and that RetroArch can only load
cores that exist in its cores directory. This service answers "does this platform have
what it needs, and if not, get it": it asks the inventory which libretro cores back a
system's rows, asks the filesystem which are already there, and installs the rest through
one injected callable.

Which cores a platform needs is a property of the inventory, not of this service: adding
an emulator to the document adds its core to this work with no code change. Nothing here
decides a source or trusts a download — the installer verifies before it writes — and a
failure is reported per core rather than aborting the batch, because one unavailable core
must not stop the others from being installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.core_provision import missing_cores

if TYPE_CHECKING:
    import asyncio
    import logging
    from collections.abc import Callable

    from domain.owned_inventory import InventoryPlatform


@dataclass(frozen=True)
class CoreProvisioningConfig:
    """What the service needs: the inventory, the disk, the installer, and a loop."""

    loop: asyncio.AbstractEventLoop
    logger: logging.Logger
    inventory: Callable[[str], InventoryPlatform | None]
    installed: Callable[[str], bool]
    installer: Callable[[str], dict[str, Any]]


class CoreProvisioningService:
    """Install the libretro cores a platform's inventory rows need."""

    def __init__(self, *, config: CoreProvisioningConfig) -> None:
        self._loop = config.loop
        self._logger = config.logger
        self._inventory = config.inventory
        self._installed = config.installed
        self._installer = config.installer

    async def ensure_for_system(self, system_name: str) -> dict[str, Any]:
        """Install what *system_name* is missing and report every core's outcome.

        ``reason`` is set only for the answers a caller can act on: ``unknown_system``
        (the inventory does not describe this system) and ``no_libretro`` (it describes
        only standalone emulators, so there is nothing to download). A system that is
        already complete answers ``success: True`` with empty lists rather than taking a
        trip through the installer.

        The installs run one at a time in the executor: cores are a handful of megabytes
        each and a batch is rarely more than one or two, so serialising them keeps the
        progress story simple and never blocks the event loop.
        """
        platform = self._inventory(system_name)
        if platform is None:
            return {"success": False, "reason": "unknown_system", "system": system_name, "cores": []}
        wanted = [
            emulator.core_so
            for emulator in platform.emulators
            if emulator.kind == "libretro" and emulator.core_so
        ]
        if not wanted:
            return {"success": False, "reason": "no_libretro", "system": system_name, "cores": []}
        missing = missing_cores(wanted, installed=self._installed)
        results: list[dict[str, Any]] = [
            await self._loop.run_in_executor(None, self._installer, core) for core in missing
        ]
        installed = [result["core"] for result in results if result.get("ok")]
        failed = [result for result in results if not result.get("ok")]
        if installed:
            self._logger.info(f"core_provisioning: installed {len(installed)} core(s) for {system_name}: {installed}")
        if failed:
            self._logger.warning(f"core_provisioning: {len(failed)} core(s) failed for {system_name}: {failed}")
        return {
            "success": not failed,
            "system": system_name,
            "installed": installed,
            "failed": failed,
            "already_present": [core for core in wanted if core not in missing],
            "cores": results,
        }
