"""Installing a system's standalone emulators: which rows are fetched, and what is reported.

The network is never touched here — the adapter owns that, and it refuses anything it
cannot hash. What is pinned is the service's own arithmetic: a row with a source becomes
one install, a row without one is reported as manual, and one failure does not hide the
others.
"""

from __future__ import annotations

import asyncio
import logging

import pytest

from domain.owned_inventory import InventoryEmulator, InventoryInstall, InventoryPlatform
from services.emulator_provisioning import EmulatorProvisioningConfig, EmulatorProvisioningService

_GC = InventoryPlatform(
    platform="gc",
    names=("gc",),
    extensions=("iso",),
    emulators=(
        InventoryEmulator(
            label="Dolphin (Standalone)",
            emulator="dolphin",
            kind="standalone",
            install=InventoryInstall(flatpak="org.DolphinEmu.dolphin-emu"),
        ),
    ),
)

_SWITCH = InventoryPlatform(
    platform="switch",
    names=("switch", "nx"),
    extensions=("nsp",),
    emulators=(
        InventoryEmulator(label="Eden (Standalone)", emulator="eden", kind="standalone"),
        InventoryEmulator(
            label="Citron (Standalone)",
            emulator="citron",
            kind="standalone",
            install=InventoryInstall(),
        ),
        InventoryEmulator(
            label="Eden (Flatpak)",
            emulator="eden",
            kind="standalone",
            install=InventoryInstall(flatpak="io.github.eden_emulator.Eden"),
        ),
    ),
)


class _Harness:
    def __init__(self, *, failing: set[str] | None = None) -> None:
        self.asked: list[str] = []
        self._failing = failing or set()

    def platform_for(self, system: str) -> InventoryPlatform | None:
        return {"gc": _GC, "switch": _SWITCH}.get(system)

    def install(self, emulator: InventoryEmulator) -> dict:
        self.asked.append(emulator.label)
        if emulator.label in self._failing:
            return {"label": emulator.label, "ok": False, "reason": "hash_mismatch"}
        return {"label": emulator.label, "ok": True, "already_present": False}

    async def ensure(self, system: str) -> dict:
        service = EmulatorProvisioningService(
            config=EmulatorProvisioningConfig(
                loop=asyncio.get_running_loop(),
                logger=logging.getLogger("test_emulator_provisioning"),
                inventory=self.platform_for,
                installer=self.install,
            )
        )
        return await service.ensure_for_system(system)


@pytest.fixture
def harness() -> _Harness:
    return _Harness()


class TestTheInstall:
    @pytest.mark.asyncio
    async def test_a_store_row_is_installed(self, harness: _Harness) -> None:
        result = await harness.ensure("gc")

        assert result["success"] is True
        assert result["installed"] == ["Dolphin (Standalone)"]
        assert harness.asked == ["Dolphin (Standalone)"]

    @pytest.mark.asyncio
    async def test_a_row_without_a_source_is_not_fetched(self, harness: _Harness) -> None:
        """An install block that names nothing is "install it yourself", and it is said."""
        result = await harness.ensure("switch")

        assert harness.asked == ["Eden (Flatpak)"]
        assert result["installed"] == ["Eden (Flatpak)"]
        assert result["manual"] == ["Eden (Standalone)", "Citron (Standalone)"]

    @pytest.mark.asyncio
    async def test_one_failure_does_not_hide_the_others(self) -> None:
        failing = _Harness(failing={"Dolphin (Standalone)"})

        result = await failing.ensure("gc")

        assert result["success"] is False
        assert result["failed"] == [{"label": "Dolphin (Standalone)", "ok": False, "reason": "hash_mismatch"}]

    @pytest.mark.asyncio
    async def test_a_system_the_inventory_cannot_describe_is_reported(self, harness: _Harness) -> None:
        result = await harness.ensure("ps4")

        assert result["success"] is False
        assert result["reason"] == "unknown_system"
        assert harness.asked == []

    @pytest.mark.asyncio
    async def test_a_system_with_no_fetchable_emulator_says_so(self, harness: _Harness) -> None:
        empty = InventoryPlatform(platform="x", names=("x",), extensions=(), emulators=(_SWITCH.emulators[0],))
        service = EmulatorProvisioningService(
            config=EmulatorProvisioningConfig(
                loop=asyncio.get_running_loop(),
                logger=logging.getLogger("test_emulator_provisioning"),
                inventory=lambda system: empty,
                installer=harness.install,
            )
        )

        result = await service.ensure_for_system("x")

        assert result["success"] is False
        assert result["reason"] == "no_source"
        assert result["manual"] == ["Eden (Standalone)"]
