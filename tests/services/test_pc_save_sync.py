"""Tests for services.pc_save_sync — one PC game's save folder, zipped and carried."""

from __future__ import annotations

import io
import logging
import os
import zipfile

import pytest
from fakes.fake_unit_of_work import FakeUnitOfWork, FakeUnitOfWorkFactory

from adapters.download_file import DownloadFileAdapter
from domain.rom import Rom
from domain.save_answer import BENIGN_SYNC_SKIP_REASONS
from services.pc_save_sync import PcSaveSync, PcSaveSyncConfig, PcSaveSyncExitHook

APP_ID = 2169565722
ROM_ID = 7159


class FakeRommApi:
    """Stands in for the save endpoints; keeps what was uploaded and served."""

    def __init__(self) -> None:
        self.saves: list[dict] = []
        self.uploads: list[dict] = []
        self.downloaded: list[int] = []
        self.served: bytes | None = None

    def list_saves(self, rom_id: int) -> list[dict]:
        return [save for save in self.saves if save["rom_id"] == rom_id]

    def upload_save(self, rom_id: int, file_path: str, emulator: str, *, slot: str | None = None) -> dict:
        with open(file_path, "rb") as handle:
            body = handle.read()
        self.uploads.append({"rom_id": rom_id, "emulator": emulator, "slot": slot, "body": body})
        return {"id": 1}

    def download_save(self, save_id: int, dest_path: str) -> None:
        self.downloaded.append(save_id)
        assert self.served is not None
        with open(dest_path, "wb") as handle:
            handle.write(self.served)


class FakeSteamConfig:
    def __init__(self, root: str | None) -> None:
        self._root = root

    def compatdata_root(self) -> str | None:
        return self._root


@pytest.fixture
def compatdata(tmp_path) -> str:
    root = tmp_path / "steamapps" / "compatdata"
    root.mkdir(parents=True)
    return str(root)


def _rom(*, platform: str = "win", name: str = "Need for Speed: Most Wanted") -> Rom:
    return Rom(
        rom_id=ROM_ID,
        platform_slug=platform,
        name=name,
        fs_name="Need For Speed Most Wanted 2005",
        shortcut_app_id=APP_ID,
        last_synced_at="2025-01-01T00:00:00",
    )


def _build(data_dir, compatdata: str | None, *, rom: Rom | None = None):
    """A service over a fake unit of work, an in-memory server, and real file I/O."""
    uow = FakeUnitOfWork()
    uow.roms.save(rom if rom is not None else _rom())
    api = FakeRommApi()
    service = PcSaveSync(
        config=PcSaveSyncConfig(
            romm_api=api,
            uow_factory=FakeUnitOfWorkFactory(uow=uow),
            file_store=DownloadFileAdapter(),
            steam_config=FakeSteamConfig(compatdata),
            logger=logging.getLogger("test"),
            data_dir=str(data_dir),
        ),
    )
    return service, api, uow


def _save_folder(compatdata: str, name: str = "NFS Most Wanted") -> str:
    folder = os.path.join(
        compatdata, str(APP_ID), "pfx", "drive_c", "users", "steamuser", "Documents", name
    )
    os.makedirs(folder, exist_ok=True)
    return folder


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, body in files.items():
            archive.writestr(name, body)
    return buffer.getvalue()


def test_windows_games_are_handled_and_others_are_not(tmp_path):
    service, _api, _uow = _build(tmp_path, str(tmp_path / "compatdata"))
    assert service.handles(ROM_ID) is True

    other, _api2, _uow2 = _build(tmp_path, str(tmp_path / "compatdata"), rom=_rom(platform="snes"))
    assert other.handles(ROM_ID) is False


def test_capture_uploads_the_game_folder_and_remembers_it(compatdata, tmp_path):
    folder = _save_folder(compatdata)
    with open(os.path.join(folder, "profile"), "wb") as handle:
        handle.write(b"progress")

    service, api, uow = _build(tmp_path, compatdata)
    result = service.capture(ROM_ID)

    assert result["uploaded"] == 1
    assert api.uploads[0]["emulator"] == "proton"
    uploaded = tmp_path / "uploaded.zip"
    uploaded.write_bytes(api.uploads[0]["body"])
    with zipfile.ZipFile(uploaded) as archive:
        assert archive.namelist() == ["profile"]
    assert uow.kv_config.get(f"pc_save_dir:{ROM_ID}") == "Documents/NFS Most Wanted"


def test_restore_unzips_the_newest_server_save_over_the_same_folder(compatdata, tmp_path):
    folder = _save_folder(compatdata)
    with open(os.path.join(folder, "profile"), "wb") as handle:
        handle.write(b"old")

    service, api, uow = _build(tmp_path, compatdata)
    uow.kv_config.set(f"pc_save_dir:{ROM_ID}", "Documents/NFS Most Wanted")
    api.saves = [
        {"id": 4, "rom_id": ROM_ID, "file_name": "old.zip", "updated_at": "2026-01-01T10:00:00"},
        {"id": 9, "rom_id": ROM_ID, "file_name": "new.zip", "updated_at": "2026-02-01T10:00:00"},
    ]
    api.served = _zip_bytes({"profile": b"new"})

    result = service.restore(ROM_ID)

    assert result["synced"] == 1
    assert api.downloaded == [9]
    with open(os.path.join(folder, "profile"), "rb") as handle:
        assert handle.read() == b"new"


def test_restore_with_no_server_save_leaves_the_folder_alone(compatdata, tmp_path):
    _save_folder(compatdata)
    service, api, _uow = _build(tmp_path, compatdata)

    result = service.restore(ROM_ID)

    assert result["synced"] == 0
    assert api.downloaded == []


def test_a_game_that_never_ran_has_no_prefix_and_nothing_happens(tmp_path):
    service, api, _uow = _build(tmp_path, str(tmp_path / "missing"))

    assert service.restore(ROM_ID)["synced"] == 0
    assert service.capture(ROM_ID)["uploaded"] == 0
    assert api.uploads == []


def test_the_remembered_folder_is_used_even_when_another_looks_newer(compatdata, tmp_path):
    remembered = _save_folder(compatdata, "NFS Most Wanted")
    newer = _save_folder(compatdata, "Something Else")
    with open(os.path.join(remembered, "profile"), "wb") as handle:
        handle.write(b"kept")
    with open(os.path.join(newer, "other"), "wb") as handle:
        handle.write(b"x")
    os.utime(os.path.join(newer, "other"), (9_999_999_999, 9_999_999_999))

    service, api, uow = _build(tmp_path, compatdata)
    uow.kv_config.set(f"pc_save_dir:{ROM_ID}", "Documents/NFS Most Wanted")

    service.capture(ROM_ID)

    uploaded = tmp_path / "uploaded.zip"
    uploaded.write_bytes(api.uploads[0]["body"])
    with zipfile.ZipFile(uploaded) as archive:
        assert archive.namelist() == ["profile"]


class TestTheExitHookTheLifecycleCalls:
    """The session's exit goes through the lifecycle's own collaborator, not the handler."""

    @pytest.mark.asyncio
    async def test_a_windows_game_is_captured_through_the_pc_path(self, compatdata, tmp_path):
        import asyncio

        folder = _save_folder(compatdata)
        with open(os.path.join(folder, "Manu"), "wb") as handle:
            handle.write(b"profile" * 10)

        service, api, _uow = _build(tmp_path, compatdata)
        hook = PcSaveSyncExitHook(pc=service, emulator=_NeverCalled(), loop=asyncio.get_running_loop())

        result = await hook.post_exit_sync(ROM_ID)

        assert result["uploaded"] == 1
        assert result["success"] is True
        assert api.uploads[0]["emulator"] == "proton"

    @pytest.mark.asyncio
    async def test_an_emulator_game_is_left_to_the_emulator_service(self, tmp_path):
        import asyncio

        emulator = _NeverCalled()
        service, _api, _uow = _build(tmp_path, str(tmp_path / "compatdata"), rom=_rom(platform="snes"))
        hook = PcSaveSyncExitHook(pc=service, emulator=emulator, loop=asyncio.get_running_loop())

        result = await hook.post_exit_sync(ROM_ID)

        assert result == {"delegated": True}
        assert emulator.calls == [ROM_ID]

    @pytest.mark.asyncio
    async def test_nothing_to_carry_is_a_benign_skip_not_a_failure(self, compatdata, tmp_path):
        import asyncio

        service, _api, _uow = _build(tmp_path, compatdata)
        hook = PcSaveSyncExitHook(pc=service, emulator=_NeverCalled(), loop=asyncio.get_running_loop())

        result = await hook.post_exit_sync(ROM_ID)

        assert result["reason"] in BENIGN_SYNC_SKIP_REASONS
        assert result["uploaded"] == 0


class _NeverCalled:
    """A stand-in for SaveService that records whether it was asked to sync."""

    def __init__(self) -> None:
        self.calls: list[int] = []

    async def post_exit_sync(self, rom_id: int) -> dict:
        self.calls.append(rom_id)
        return {"delegated": True}
