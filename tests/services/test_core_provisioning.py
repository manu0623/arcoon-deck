"""The whole-device core sweep behind the Settings button.

What is pinned here is the sweep's own arithmetic — which systems it visits, that two
platforms naming one system download once, and that a platform the inventory cannot
describe is *reported* instead of being silently counted as done — plus the one-platform
path, including the forced re-fetch the platform pane's reinstall button asks for.
"""

from __future__ import annotations

import asyncio
import logging

import pytest

from domain.owned_inventory import InventoryEmulator, InventoryPlatform
from services.core_provisioning import CoreProvisioningConfig, CoreProvisioningService

_RUNTIME_OK = {"success": True, "already_present": True}


def _platform(system: str, *cores: str) -> InventoryPlatform:
    return InventoryPlatform(
        platform=system,
        names=(system,),
        extensions=(f".{system}",),
        emulators=tuple(InventoryEmulator(label=core, emulator=core, kind="libretro", core_so=core) for core in cores),
    )


class _Harness:
    """An inventory with no cores on disk and an installer that records what it gets."""

    def __init__(
        self,
        platforms: dict[str, InventoryPlatform],
        aliases: dict[str, str] | None = None,
        on_disk: set[str] | None = None,
        failing: set[str] | None = None,
    ) -> None:
        self._platforms = platforms
        self._aliases = aliases or {}
        self.on_disk = on_disk or set()
        self.failing = failing or set()
        self.installed_calls: list[str] = []

    def platform_for(self, system: str) -> InventoryPlatform | None:
        return self._platforms.get(system)

    def resolve(self, slug: str) -> str:
        return self._aliases.get(slug, slug)

    def install(self, core: str) -> dict:
        self.installed_calls.append(core)
        if core in self.failing:
            return {"core": core, "ok": False, "reason": "not_elf"}
        return {"core": core, "ok": True}

    def service(self) -> CoreProvisioningService:
        return CoreProvisioningService(
            config=CoreProvisioningConfig(
                loop=asyncio.get_running_loop(),
                logger=logging.getLogger("test_core_provisioning"),
                inventory=self.platform_for,
                installed=self.on_disk.__contains__,
                installer=self.install,
                runtime_installed=lambda: True,
                runtime_installer=lambda: _RUNTIME_OK,
                runtime_is_builtin=lambda: True,
                resolve_system=self.resolve,
            )
        )

    async def sweep(self, slugs: list[str]) -> dict:
        return await self.service().ensure_for_platforms(slugs)

    async def ensure(self, system: str, *, force: bool = False) -> dict:
        return await self.service().ensure_for_system(system, force=force)


@pytest.fixture
def harness() -> _Harness:
    return _Harness(
        {
            "gba": _platform("gba", "mgba_libretro", "vbam_libretro"),
            "gbc": _platform("gbc", "gambatte_libretro"),
            "snes": _platform("snes", "snes9x_libretro"),
        },
        # Two RomM slugs, one inventory system: gb and gbc are the same emulator.
        aliases={"gameboy": "gbc"},
    )


class TestEnsureForPlatforms:
    def test_installs_a_missing_core_for_every_platform(self, harness: _Harness) -> None:
        result = asyncio.run(harness.sweep(["gba", "gbc", "snes"]))

        assert result["success"] is True
        assert sorted(result["installed"]) == ["gambatte_libretro", "mgba_libretro", "snes9x_libretro", "vbam_libretro"]

    def test_two_platforms_naming_one_system_download_once(self, harness: _Harness) -> None:
        result = asyncio.run(harness.sweep(["gbc", "gameboy"]))

        assert result["installed"] == ["gambatte_libretro"]
        assert harness.installed_calls == ["gambatte_libretro"]

    def test_a_platform_the_inventory_cannot_describe_is_reported(self, harness: _Harness) -> None:
        # Not a failure — this build simply has no emulator data for it — but it must
        # reach the reader, or "everything installed" is a claim about platforms it
        # never looked at.
        result = asyncio.run(harness.sweep(["gba", "ps3"]))

        assert result["skipped"] == ["ps3"]
        assert result["failed"] == []
        assert result["success"] is True

    def test_no_platforms_installs_nothing_and_claims_nothing(self, harness: _Harness) -> None:
        result = asyncio.run(harness.sweep([]))

        assert result["installed"] == []
        assert result["skipped"] == []
        assert harness.installed_calls == []


class TestEnsureForSystem:
    """One platform's cores, and the reinstall that only `force` can express."""

    def test_installs_only_what_is_missing(self) -> None:
        harness = _Harness({"gba": _platform("gba", "mgba_libretro", "vbam_libretro")}, on_disk={"mgba_libretro"})

        result = asyncio.run(harness.ensure("gba"))

        assert result["installed"] == ["vbam_libretro"]
        assert result["already_present"] == ["mgba_libretro"]
        assert harness.installed_calls == ["vbam_libretro"]

    def test_force_refetches_a_core_that_is_already_on_disk(self) -> None:
        # The whole point of the button: a file the filesystem reports is not
        # necessarily a core RetroArch can load, and missing-only never looks twice.
        harness = _Harness({"gba": _platform("gba", "mgba_libretro")}, on_disk={"mgba_libretro"})

        result = asyncio.run(harness.ensure("gba", force=True))

        assert result["success"] is True
        assert result["installed"] == ["mgba_libretro"]
        # Nothing was skipped, so nothing may be reported as already present.
        assert result["already_present"] == []
        assert harness.installed_calls == ["mgba_libretro"]

    def test_a_forced_core_that_fails_is_reported_not_counted(self) -> None:
        # A reinstall that half-lands must say so: the old file is still there, and
        # "reinstalled" over a refused download would be the claim that hides it.
        harness = _Harness(
            {"gba": _platform("gba", "mgba_libretro", "vbam_libretro")},
            on_disk={"mgba_libretro", "vbam_libretro"},
            failing={"vbam_libretro"},
        )

        result = asyncio.run(harness.ensure("gba", force=True))

        assert result["success"] is False
        assert result["installed"] == ["mgba_libretro"]
        assert result["failed"] == [{"core": "vbam_libretro", "ok": False, "reason": "not_elf"}]
