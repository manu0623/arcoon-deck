"""LaunchExeService — the Windows exe picker's read and write."""

from __future__ import annotations

import asyncio
import logging

import pytest
from fakes.fake_download_file_store import FakeDownloadFileStore
from fakes.fake_unit_of_work import FakeUnitOfWork, FakeUnitOfWorkFactory

from domain.rom import Rom
from domain.rom_install import RomInstall
from services.launch_exe import LaunchExeService, LaunchExeServiceConfig

_ROM_DIR = "/roms/windows/Skyrim"
_GAME = f"{_ROM_DIR}/Skyrim.exe"
_NESTED = f"{_ROM_DIR}/bin/Win64/SkyrimSE.exe"
_JUNK = f"{_ROM_DIR}/unins000.exe"


def _seed_rom(uow: FakeUnitOfWork, *, rom_id: int = 1, app_id: int | None = 42) -> None:
    uow.roms.save(
        Rom(
            rom_id=rom_id,
            platform_slug="windows",
            name="Skyrim",
            fs_name="Skyrim.exe",
            shortcut_app_id=app_id,
            last_synced_at="2026-01-01T00:00:00+00:00",
        )
    )


def _seed_install(
    uow: FakeUnitOfWork,
    *,
    rom_id: int = 1,
    file_path: str = _GAME,
    rom_dir: str | None = _ROM_DIR,
    platform_slug: str = "windows",
    launchable: bool = False,
) -> None:
    uow.rom_installs.save(
        RomInstall(
            rom_id=rom_id,
            file_path=file_path,
            rom_dir=rom_dir,
            platform_slug=platform_slug,
            system=platform_slug,
            installed_at="2026-01-01T00:00:00+00:00",
            launchable=launchable,
        )
    )


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def file_store() -> FakeDownloadFileStore:
    return FakeDownloadFileStore(
        files={
            _GAME: b"x" * 10,
            _NESTED: b"x" * 5_000,
            _JUNK: b"x" * 900,
            f"{_ROM_DIR}/Data/Skyrim.esm": b"x" * 9_000_000,
        }
    )


@pytest.fixture
def service(event_loop, uow, file_store) -> LaunchExeService:
    return LaunchExeService(
        config=LaunchExeServiceConfig(
            loop=event_loop,
            logger=logging.getLogger("test_launch_exe"),
            uow_factory=FakeUnitOfWorkFactory(uow=uow),
            file_store=file_store,
        ),
    )


class TestGetLaunchExe:
    def test_a_non_windows_install_has_no_picker(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow, platform_slug="psx", file_path="/roms/psx/game.cue", rom_dir="/roms/psx/game")
        assert event_loop.run_until_complete(service.get_launch_exe(1)) == {"windows": False}

    def test_an_uninstalled_rom_has_no_picker(self, event_loop, service):
        assert event_loop.run_until_complete(service.get_launch_exe(1)) == {"windows": False}

    def test_a_windows_install_lists_its_executables_best_first(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.get_launch_exe(1))
        assert result["windows"] is True
        assert result["current"] == "Skyrim.exe"
        paths = [row["path"] for row in result["candidates"]]
        # The root game exe first, the uninstaller last — the same order the
        # automatic pick reads, so the first row is the guess.
        assert paths[0] == "Skyrim.exe"
        assert paths[-1] == "unins000.exe"
        assert "Data/Skyrim.esm" not in paths

    def test_a_single_file_install_offers_nothing(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow, file_path="/roms/windows/Skyrim.exe", rom_dir=None)
        result = event_loop.run_until_complete(service.get_launch_exe(1))
        assert result == {"windows": True, "current": "Skyrim.exe", "candidates": [], "truncated": False}

    def test_candidate_sizes_come_from_the_listing(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.get_launch_exe(1))
        sizes = {row["path"]: row["size_bytes"] for row in result["candidates"]}
        assert sizes["Skyrim.exe"] == 10
        assert sizes["bin/Win64/SkyrimSE.exe"] == 5_000


class TestSetLaunchExe:
    def test_a_pick_retargets_the_install_and_hands_back_the_shortcut_shape(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "bin/Win64/SkyrimSE.exe"))

        assert result["success"] is True
        assert result["app_id"] == 42
        assert result["exe"] == _NESTED
        assert result["start_dir"] == f"{_ROM_DIR}/bin/Win64"
        assert result["launch_options"] == ""

        with uow as current:
            install = current.rom_installs.get(1)
        assert install is not None
        assert install.file_path == _NESTED
        # A hand-picked executable is a launch target however the download's
        # guess went — that is the whole point of the picker.
        assert install.launchable is True

    def test_the_relative_path_is_what_is_returned_as_current_afterwards(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        event_loop.run_until_complete(service.set_launch_exe(1, "bin/Win64/SkyrimSE.exe"))
        assert event_loop.run_until_complete(service.get_launch_exe(1))["current"] == "bin/Win64/SkyrimSE.exe"

    def test_a_path_outside_the_install_is_refused(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "../Other/Game.exe"))
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_a_file_the_install_does_not_hold_is_refused(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "Missing.exe"))
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_a_non_executable_is_refused(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "Data/Skyrim.esm"))
        assert result["success"] is False
        assert result["reason"] == "unsupported"

    def test_a_single_file_install_has_nothing_to_choose(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow, file_path="/roms/windows/Skyrim.exe", rom_dir=None)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "Skyrim.exe"))
        assert result["success"] is False
        assert result["reason"] == "unsupported"

    def test_a_non_windows_install_is_refused(self, event_loop, service, uow):
        _seed_rom(uow)
        _seed_install(uow, platform_slug="psx", file_path="/roms/psx/game.cue", rom_dir="/roms/psx/game")
        result = event_loop.run_until_complete(service.set_launch_exe(1, "game.exe"))
        assert result["success"] is False
        assert result["reason"] == "not_installed"

    def test_an_unbound_rom_answers_no_app_id(self, event_loop, service, uow):
        _seed_rom(uow, app_id=None)
        _seed_install(uow)
        result = event_loop.run_until_complete(service.set_launch_exe(1, "Skyrim.exe"))
        assert result["success"] is True
        assert result["app_id"] is None
