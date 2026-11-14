"""Tests for services/saves/ps2_card_import — a server card image applied before launch.

The rules under test are the ones that protect progress: only the slot's newest save is
applied (a card older than what the Deck has would roll the player back), only the
ordinary slot, the bytes are compared before writing (an applied card is a no-op), every
file is backed up through the sync layer's quarantine before it is replaced, and the
game's folder is the one the answer's own members name.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest
from fakes.ps2_card import build_file_card

from adapters.ps2_memcard import Ps2MemcardAdapter
from services.saves.ps2_card_import import Ps2CardImportService, game_folder

_LOGGER = logging.getLogger("test_ps2_card_import")
_GTA = "BASLUS-21423GTA30001"
_IMAGE = build_file_card({_GTA: {_GTA: b"gta-progress", "icon.sys": b"icon"}})
_TWO_GAMES = build_file_card({_GTA: {_GTA: b"gta"}, "BASCUS-97198YAOTWTD!": {"BASCUS-97198YAOTWTD!": b"sly"}})


class _FakeRomInfo:
    def __init__(self, *, system: str = "ps2", card_dir: str | None = None, members: tuple[str, ...] = ()) -> None:
        self._info = {
            "system": system,
            "rom_name": "Grand Theft Auto - Liberty City Stories (USA)",
            "saves_dir": "/bank",
            "file_path": "/roms/ps2/Grand Theft Auto - Liberty City Stories (USA).iso",
            "platform_slug": "ps2",
        }
        self._answer = SimpleNamespace(
            syncable=True,
            directory=card_dir,
            synced_files=tuple(SimpleNamespace(name=name) for name in members),
        )

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


def _service(tmp_path, *, saves, members=(f"{_GTA}/{_GTA}",), content: bytes = _IMAGE, system="ps2"):
    quarantined: list[tuple[str, str]] = []

    def quarantine(target: str, name: str) -> bool:
        quarantined.append((target, name))
        return True

    card_dir = tmp_path / "Mcd001.ps2"
    card_dir.mkdir(parents=True, exist_ok=True)
    service = Ps2CardImportService(
        rom_info=_FakeRomInfo(system=system, card_dir=str(card_dir), members=members),
        romm_api=_FakeApi(saves, content=content),
        memcard=Ps2MemcardAdapter(logger=_LOGGER),
        quarantine=quarantine,
        logger=_LOGGER,
    )
    return service, card_dir, quarantined


def _card(save_id: int, updated: str, *, extension: str = "ps2", slot: str = "autosave") -> dict:
    return {
        "id": save_id,
        "slot": slot,
        "file_extension": extension,
        "file_name": f"autosave [{updated}].{extension}",
        "updated_at": updated,
    }


class TestNothingToDo:
    def test_another_system_is_not_touched(self, tmp_path):
        service, _, _ = _service(tmp_path, saves=[_card(1, "2026-11-14T08:30:10+00:00")], system="psx")

        assert service.import_newest(5338) is None

    def test_the_newest_save_being_our_own_archive_downloads_nothing(self, tmp_path):
        saves = [
            _card(1, "2026-11-14T05:38:48+00:00", extension="zip"),
            _card(2, "2026-11-14T03:47:57+00:00"),
        ]
        service, card_dir, quarantined = _service(tmp_path, saves=saves)

        assert service.import_newest(5338) is None
        assert not (card_dir / _GTA).exists()
        assert quarantined == []

    def test_a_named_slot_is_never_imported(self, tmp_path):
        service, _, quarantined = _service(tmp_path, saves=[_card(1, "2026-11-14T08:30:10+00:00", slot="before-boss")])

        assert service.import_newest(5338) is None
        assert quarantined == []


class TestImport:
    def test_the_newest_card_is_written_into_the_game_folder(self, tmp_path):
        service, card_dir, quarantined = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "imported"
        assert outcome["folder"] == _GTA
        folder = card_dir / _GTA
        assert (folder / _GTA).read_bytes() == b"gta-progress"
        assert (folder / "icon.sys").read_bytes() == b"icon"
        assert quarantined == [(str(folder), _GTA), (str(folder), "icon.sys")]

    def test_an_applied_card_is_a_no_op(self, tmp_path):
        service, card_dir, quarantined = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])
        folder = card_dir / _GTA
        folder.mkdir(parents=True)
        (folder / _GTA).write_bytes(b"gta-progress")
        (folder / "icon.sys").write_bytes(b"icon")

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "unchanged"
        assert quarantined == []

    def test_a_two_game_card_is_read_by_the_name_the_answer_carries(self, tmp_path):
        service, card_dir, _ = _service(
            tmp_path,
            saves=[_card(481, "2026-11-14T08:30:10+00:00")],
            content=_TWO_GAMES,
            members=(f"{_GTA}/icon.sys",),
        )

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "imported"
        assert (card_dir / _GTA / _GTA).read_bytes() == b"gta"

    def test_an_unreadable_image_leaves_the_save_alone(self, tmp_path):
        service, card_dir, quarantined = _service(
            tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")], content=b"not a card at all"
        )

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "no_folder"
        assert list(card_dir.iterdir()) == []
        assert quarantined == []

    def test_without_a_backup_nothing_is_written(self, tmp_path):
        service, card_dir, _ = _service(tmp_path, saves=[_card(481, "2026-11-14T08:30:10+00:00")])
        service._quarantine = lambda target_dir, name: (_ for _ in ()).throw(OSError("read-only"))  # type: ignore[method-assign]

        outcome = service.import_newest(5338)

        assert outcome is not None and outcome["status"] == "backup_failed"
        assert list(card_dir.iterdir()) == []


class TestGameFolder:
    def test_the_first_member_segment_names_the_folder(self):
        answer = SimpleNamespace(synced_files=(SimpleNamespace(name=f"{_GTA}/icon.sys"),))

        assert game_folder(answer) == _GTA

    def test_an_answer_without_members_names_nothing(self):
        assert game_folder(SimpleNamespace(synced_files=())) is None


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
