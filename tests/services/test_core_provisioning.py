"""The whole-device core sweep behind the Settings button.

The one-off system path is exercised on a device; what is pinned here is the sweep's
own arithmetic — which systems it visits, that two platforms naming one system download
once, and that a platform the inventory cannot describe is *reported* instead of being
silently counted as done.
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
        emulators=tuple(
            InventoryEmulator(label=core, emulator=core, kind="libretro", core_so=core) for core in cores
        ),
    )


class _Harness:
    """An inventory with no cores on disk and an installer that records what it gets."""

    def __init__(self, platforms: dict[str, InventoryPlatform], aliases: dict[str, str] | None = None) -> None:
        self._platforms = platforms
        self._aliases = aliases or {}
        self.installed_calls: list[str] = []

    def platform_for(self, system: str) -> InventoryPlatform | None:
        return self._platforms.get(system)

    def resolve(self, slug: str) -> str:
        return self._aliases.get(slug, slug)

    def install(self, core: str) -> dict:
        self.installed_calls.append(core)
        return {"core": core, "ok": True}

    async def sweep(self, slugs: list[str]) -> dict:
        service = CoreProvisioningService(
            config=CoreProvisioningConfig(
                loop=asyncio.get_running_loop(),
                logger=logging.getLogger("test_core_provisioning"),
                inventory=self.platform_for,
                installed=lambda core: False,
                installer=self.install,
                runtime_installed=lambda: True,
                runtime_installer=lambda: _RUNTIME_OK,
                runtime_is_builtin=lambda: True,
                resolve_system=self.resolve,
            )
        )
        return await service.ensure_for_platforms(slugs)


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
