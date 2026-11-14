"""Tests for services/saves/ps2_card_import — a downloaded card image written into the card.

The rules under test are the ones that protect progress: the game's folder is what gets
written (never the card image itself), the bytes are compared before writing (an applied
card is a no-op), every file is backed up through the sync layer's quarantine before it is
replaced, and a card that names no folder for this game writes nothing at all.
"""

from __future__ import annotations

import logging

import pytest
from fakes.ps2_card import build_file_card

from adapters.ps2_memcard import Ps2MemcardAdapter
from services.saves.ps2_card_import import Ps2CardImportService

_LOGGER = logging.getLogger("test_ps2_card_import")
_GTA = "BASLUS-21423GTA30001"
_IMAGE = build_file_card({_GTA: {_GTA: b"gta-progress", "icon.sys": b"icon"}})
_TWO_GAMES = build_file_card({_GTA: {_GTA: b"gta"}, "BASCUS-97198YAOTWTD!": {"BASCUS-97198YAOTWTD!": b"sly"}})


def _service(tmp_path, *, quarantine=None):
    quarantined: list[tuple[str, str]] = []

    def record(target: str, name: str) -> bool:
        quarantined.append((target, name))
        return True

    card_dir = tmp_path / "Mcd001.ps2"
    card_dir.mkdir(parents=True, exist_ok=True)
    service = Ps2CardImportService(
        memcard=Ps2MemcardAdapter(logger=_LOGGER),
        quarantine=quarantine or record,
        logger=_LOGGER,
    )
    card = tmp_path / "downloaded.ps2"
    return service, card_dir, card, quarantined


class TestImportCard:
    def test_the_game_folder_is_written_and_the_image_never_is(self, tmp_path):
        service, card_dir, card, quarantined = _service(tmp_path)
        card.write_bytes(_IMAGE)

        outcome = service.import_card(str(card), str(card_dir), _GTA)

        assert outcome is not None and outcome["status"] == "imported"
        assert outcome["folder"] == _GTA
        folder = card_dir / _GTA
        assert (folder / _GTA).read_bytes() == b"gta-progress"
        assert (folder / "icon.sys").read_bytes() == b"icon"
        assert sorted(p.name for p in card_dir.iterdir()) == [_GTA]
        assert quarantined == [(str(folder), _GTA), (str(folder), "icon.sys")]

    def test_an_applied_card_is_a_no_op(self, tmp_path):
        service, card_dir, card, quarantined = _service(tmp_path)
        card.write_bytes(_IMAGE)
        folder = card_dir / _GTA
        folder.mkdir(parents=True)
        (folder / _GTA).write_bytes(b"gta-progress")
        (folder / "icon.sys").write_bytes(b"icon")

        outcome = service.import_card(str(card), str(card_dir), _GTA)

        assert outcome is not None and outcome["status"] == "unchanged"
        assert quarantined == []

    def test_a_two_game_card_is_read_by_the_folder_name_it_is_given(self, tmp_path):
        service, card_dir, card, _ = _service(tmp_path)
        card.write_bytes(_TWO_GAMES)

        outcome = service.import_card(str(card), str(card_dir), _GTA)

        assert outcome is not None and outcome["status"] == "imported"
        assert (card_dir / _GTA / _GTA).read_bytes() == b"gta"
        assert not (card_dir / "BASCUS-97198YAOTWTD!").exists()

    def test_a_card_naming_no_folder_writes_nothing(self, tmp_path):
        service, card_dir, card, quarantined = _service(tmp_path)
        card.write_bytes(b"not a card at all")

        assert service.import_card(str(card), str(card_dir), _GTA) is None
        assert list(card_dir.iterdir()) == []
        assert quarantined == []

    def test_a_two_game_card_without_a_name_is_left_alone(self, tmp_path):
        service, card_dir, card, quarantined = _service(tmp_path)
        card.write_bytes(_TWO_GAMES)

        assert service.import_card(str(card), str(card_dir)) is None
        assert list(card_dir.iterdir()) == []
        assert quarantined == []

    def test_an_unreadable_image_is_left_alone(self, tmp_path):
        service, card_dir, card, _ = _service(tmp_path)

        assert service.import_card(str(card), str(card_dir), _GTA) is None
        assert list(card_dir.iterdir()) == []

    def test_without_a_backup_nothing_is_written(self, tmp_path):
        def refuse(target: str, name: str) -> bool:
            raise OSError("read-only")

        service, card_dir, card, _ = _service(tmp_path, quarantine=refuse)
        card.write_bytes(_IMAGE)

        outcome = service.import_card(str(card), str(card_dir), _GTA)

        assert outcome is not None and outcome["status"] == "backup_failed"
        assert list(card_dir.iterdir()) == []


@pytest.mark.parametrize("name", [None, ""])
def test_no_folder_name_falls_back_to_a_single_game_card(tmp_path, name):
    service, card_dir, card, _ = _service(tmp_path)
    card.write_bytes(_IMAGE)

    outcome = service.import_card(str(card), str(card_dir), name)

    assert outcome is not None and outcome["status"] == "imported"
