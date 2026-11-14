"""Tests for services/saves/ps2_card_import — a server card image applied before launch.

The rule under test is the one that protects progress: only the slot's newest save is
applied (a card older than what the Deck has would roll the player back), the bytes are
compared before writing (an applied card is a no-op), and every file is backed up through
the sync layer's quarantine before it is replaced.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest
from fakes.ps2_card import build_file_card

from adapters.ps2_memcard import Ps2MemcardAdapter
from services.saves.ps2_card_import import Ps2CardImportService

_LOGGER = logging.getLogger("test_ps2_card_import")
_IMAGE = build_file_card({"BASLUS-20307Burn": {"BASLUS-20307Burn": b"burnout-progress"}})


class _FakeRomInfo:
    def __init__(self, *, system: str = "ps2", directory: str | None = "/bank/Mcd001.ps2/BASLUS-20307Burn") -> None:
        self._info = {
            "system": system,
            "rom_name": "Burnout (USA)",
            "saves_dir": "/bank",
            "file_path": "/roms/ps2/Burnout (USA).iso",
            "platform_slug": "ps2",
        }
        self._answer = SimpleNamespace(syncable=True, directory=directory)

    def get_rom_save_info(self, rom_id: int):
        return self._info

    def save_answer(self, rom_id: int):
        return self._answer


class _FakeApi:
    def __init__(self, saves: list[dict], content: bytes = _IMAGE) -> None:
        self._saves = saves
        self._content = content
        self.downloads: list[int] = []

    def list_saves(self, rom_id: int, *, device_id: str | None = None, slot: str | None = None):
        return self._saves

    def download_save(self, save_id: int, dest_path: str) -> None:
        self.downloads.append(save_id)
        with open(dest_path, "wb") as handle:
            handle.write(self._content)


def _service(tmp_path, *, saves, rom_info=None, content: bytes = _IMAGE):
    quarantined: list[tuple[str, str]] = []

    def quarantine(target: str, name: str) -> bool:
        quarantined.append((target, name))
        return True

    target = tmp_path / "Mcd001.ps2" / "BASLUS-20307Burn"
    target.mkdir(parents=True)
    service = Ps2CardImportService(
        rom_info=rom_info or _FakeRomInfo(directory=str(target)),
        romm_api=_FakeApi(saves, content=content),
        memcard=Ps2MemcardAdapter(logger=_LOGGER),
        quarantine=quarantine,
        logger=_LOGGER,
    )
    return service, target, quarantined


def _card(save_id: int, updated: str, *, extension: str = "ps2", slot: str = "autosave") -> dict:
    return {
        "id": save_id,
        "slot": slot,
        "file_extension": extension,
        "file_name": f"Burnout (USA) [{updated}].{extension}",
        "updated_at": updated,
    }


class TestNothingToDo:
    def test_another_system_is_not_touched(self, tmp_path):
        service, _, _ = _service(
            tmp_path, saves=[_card(1, "2026-11-14T08:30:10+00:00")], rom_info=_FakeRomInfo(system="psx")
        )

        assert service.import_newest(5335) is None

    def test_the_newest_save_being_our_own_archive_downloads_nothing(self, tmp_path):
        saves = [
            _card(1, "2026-11-14T05:38:48+00:00", extension="zip"),
            _card(2, "2026-11-14T03:47:57+00:00"),
        ]
        service, target, quarantined = _service(tmp_path, saves=saves)

        assert service.import_newest(5335) is None
        assert not (target / "BASLUS-20307Burn").exists()
        assert quarantined == []

    def test_a_named_slot_is_never_imported(self, tmp_path):
        service, _, quarantined = _service(tmp_path, saves=[_card(1, "2026-11-14T08:30:10+00:00", slot="before-boss")])

        assert service.import_newest(5335) is None
        assert quarantined == []


class TestImport:
    def test_the_newest_card_is_written_into_the_game_folder(self, tmp_path):
        service, target, quarantined = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "imported"
        assert outcome["folder"] == "BASLUS-20307Burn"
        assert (target / "BASLUS-20307Burn").read_bytes() == b"burnout-progress"
        assert quarantined == [(str(target), "BASLUS-20307Burn")]

    def test_an_applied_card_is_a_no_op(self, tmp_path):
        service, target, quarantined = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])
        (target / "BASLUS-20307Burn").write_bytes(b"burnout-progress")

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "unchanged"
        assert quarantined == []

    def test_an_image_that_names_no_folder_leaves_the_save_alone(self, tmp_path):
        service, target, quarantined = _service(
            tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")], content=b"not a card at all"
        )

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "no_folder"
        assert list(target.iterdir()) == []
        assert quarantined == []

    def test_without_a_backup_nothing_is_written(self, tmp_path):
        service, target, _ = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])
        service._quarantine = lambda target_dir, name: (_ for _ in ()).throw(OSError("read-only"))  # type: ignore[method-assign]

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "backup_failed"
        assert list(target.iterdir()) == []


@pytest.mark.parametrize(
    ("saves", "expected"),
    [
        ([], None),
        ([{"id": 1, "slot": "autosave", "file_name": "no-extension", "updated_at": "2026-01-01T00:00:00+00:00"}], None),
    ],
)
def test_rows_without_a_card_extension_are_ignored(tmp_path, saves, expected):
    service, _, _ = _service(tmp_path, saves=saves)

    assert service.import_newest(5338) == expected
