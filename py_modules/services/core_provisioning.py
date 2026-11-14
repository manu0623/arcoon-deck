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
    from collections.abc import Callable, Iterable

    from domain.owned_inventory import InventoryPlatform


@dataclass(frozen=True)
class CoreProvisioningConfig:
    """What the service needs: the inventory, the disk, both installers, and a loop."""

    loop: asyncio.AbstractEventLoop
    logger: logging.Logger
    inventory: Callable[[str], InventoryPlatform | None]
    installed: Callable[[str], bool]
    installer: Callable[[str], dict[str, Any]]
    # The runtime itself: a core needs a program to load it, and on a Deck with neither
    # RetroDECK nor RetroArch there is nothing to install cores *for*.
    runtime_installed: Callable[[], bool]
    runtime_installer: Callable[[], dict[str, Any]]
    # Installing a flatpak on a device RetroDECK already drives would be a second runtime
    # nobody launches; while it drives, this service has nothing to do.
    runtime_is_builtin: Callable[[], bool]
    # A RomM platform slug is not an inventory system name; the platform map
    # answers the difference for the whole-device sweep.
    resolve_system: Callable[[str], str]


class CoreProvisioningService:
    """Install the libretro cores a platform's inventory rows need."""

    def __init__(self, *, config: CoreProvisioningConfig) -> None:
        self._loop = config.loop
        self._logger = config.logger
        self._inventory = config.inventory
        self._installed = config.installed
        self._installer = config.installer
        self._runtime_installed = config.runtime_installed
        self._runtime_installer = config.runtime_installer
        self._runtime_is_builtin = config.runtime_is_builtin
        self._resolve_system = config.resolve_system

    async def ensure_runtime(self) -> dict[str, Any]:
        """Make sure the plugin has a runtime it can start, installing it when it does not.

        A ``RetroDECK`` runtime is ``skipped``: its RetroArch is inside its own flatpak and
        installing a second one would be a program nothing launches. Otherwise the owned
        runtime is the RetroArch Flatpak, installed per user so the install needs no
        password — the one thing Game Mode cannot provide.
        """
        if not self._runtime_is_builtin():
            return {"success": True, "skipped": "retrodeck"}
        if self._runtime_installed():
            return {"success": True, "already_present": True}
        result = await self._loop.run_in_executor(None, self._runtime_installer)
        return {"success": bool(result.get("ok")), **result}

    async def ensure_for_platforms(self, platform_slugs: Iterable[str]) -> dict[str, Any]:
        """Provision every enabled platform: one call for the whole device.

        Slugs are resolved to inventory systems first and deduplicated, so two platforms
        that name one system (``gb``/``gbc`` both landing on ``gbc``) do not download the
        same core twice. A platform the inventory does not describe is reported but not
        counted as a failure — it is a system this build has no emulator data for, not a
        download that broke.
        """
        runtime = await self.ensure_runtime()
        # ``dict.fromkeys`` dedupes while keeping the order, so two platforms naming
        # one system download its cores once and the report reads in list order.
        resolved = (self._resolve_system(slug) for slug in platform_slugs)
        systems = list(dict.fromkeys(system for system in resolved if system))
        results: list[dict[str, Any]] = [await self.ensure_for_system(system) for system in systems]
        installed = [core for result in results for core in result.get("installed", [])]
        failed = [core for result in results for core in result.get("failed", [])]
        # Platforms the button cannot install for: no inventory entry at all, or an entry
        # that knows only standalone emulators (an AppImage the plugin does not fetch).
        # Reported rather than dropped — "everything is installed" over a device whose
        # platforms were never looked at is the answer that made the button untrustworthy.
        uncovered_reasons = {"unknown_system", "no_libretro"}
        unknown = {result.get("system") for result in results if result.get("reason") in uncovered_reasons}
        skipped = sorted({slug for slug in platform_slugs if self._resolve_system(slug) in unknown})
        broken = [
            result for result in results if not result.get("success") and result.get("reason") != "unknown_system"
        ]
        return {
            "success": not failed and not broken and bool(runtime.get("success")),
            "runtime": runtime,
            "systems": results,
            "installed": installed,
            "failed": failed,
            "skipped": skipped,
        }

    async def ensure_for_system(self, system_name: str, *, force: bool = False) -> dict[str, Any]:
        """Install what *system_name* needs and report every core's outcome.

        ``reason`` is set only for the answers a caller can act on: ``unknown_system``
        (the inventory does not describe this system) and ``no_libretro`` (it describes
        only standalone emulators, so there is nothing to download). A system that is
        already complete answers ``success: True`` with empty lists rather than taking a
        trip through the installer.

        *force* re-fetches the cores that are already on disk, which is the one thing a
        missing-only sweep cannot do. Two states need it: a core RetroArch refuses to load
        (a truncated or mismatched build written before the archive checks landed) and a
        core that is simply out of date, because the build bot publishes nightlies and
        nothing in this app tracks a version to compare against. ``already_present`` is
        therefore empty on a forced run — nothing was skipped — and every core comes back
        in ``installed`` or ``failed``. Overwriting is what the installer's atomic replace
        is for: the old file keeps working until the verified one lands.

        The installs run one at a time in the executor: cores are a handful of megabytes
        each and a batch is rarely more than one or two, so serialising them keeps the
        progress story simple and never blocks the event loop.
        """
        # The runtime first: a core downloaded with no program to load it is a file, not a
        # working platform. A failed runtime install does not stop the cores — they are still
        # the right files for whenever a runtime appears — but it does make the answer fail.
        runtime = await self.ensure_runtime()
        platform = self._inventory(system_name)
        if platform is None:
            return {
                "success": False,
                "reason": "unknown_system",
                "system": system_name,
                "runtime": runtime,
                "cores": [],
            }
        wanted = [
            emulator.core_so for emulator in platform.emulators if emulator.kind == "libretro" and emulator.core_so
        ]
        if not wanted:
            return {
                "success": False,
                "reason": "no_libretro",
                "system": system_name,
                "runtime": runtime,
                "cores": [],
            }
        targets = wanted if force else missing_cores(wanted, installed=self._installed)
        results: list[dict[str, Any]] = [
            await self._loop.run_in_executor(None, self._installer, core) for core in targets
        ]
        installed = [result["core"] for result in results if result.get("ok")]
        failed = [result for result in results if not result.get("ok")]
        if installed:
            verb = "reinstalled" if force else "installed"
            self._logger.info(f"core_provisioning: {verb} {len(installed)} core(s) for {system_name}: {installed}")
        if failed:
            self._logger.warning(f"core_provisioning: {len(failed)} core(s) failed for {system_name}: {failed}")
        return {
            "success": not failed and bool(runtime.get("success")),
            "system": system_name,
            "runtime": runtime,
            "installed": installed,
            "failed": failed,
            "already_present": [] if force else [core for core in wanted if core not in targets],
            "cores": results,
        }
