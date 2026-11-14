"""Tests for Ps2MemcardAdapter.read_folder / write_folder — a card image into the bank.

These are the two halves of the import: pick the game's folder out of another client's
card, then write it where the launch reads. A card that cannot be read names no folder,
and a folder with subdirectories is refused rather than flattened.
"""

from __future__ import annotations

import logging

import pytest
from fakes.ps2_card import build_file_card

from adapters.ps2_memcard import Ps2MemcardAdapter

_LOGGER = logging.getLogger("test_ps2_card_import_folder")
_IMAGE = build_file_card(
    {
        "BASLUS-20307Burn": {"BASLUS-20307Burn": b"progress", "icon.sys": b"icon"},
        "BASCUS-97198YAOTWTD!": {"BASCUS-97198YAOTWTD!": b"other"},
    }
)


def _adapter() -> Ps2MemcardAdapter:
    return Ps2MemcardAdapter(logger=_LOGGER)


class TestReadFolder:
    def test_the_game_s_own_folder_comes_out_of_the_card(self):
        folder = _adapter().read_folder(_IMAGE, folder_name="BASLUS-20307Burn")

        assert folder is not None
        assert folder.name == "BASLUS-20307Burn"
        assert sorted(item.name for item in folder.files) == ["BASLUS-20307Burn", "icon.sys"]

    def test_an_image_that_is_not_a_card_names_no_folder(self):
        assert _adapter().read_folder(b"not a card", folder_name="BASLUS-20307Burn") is None

    def test_a_card_with_several_games_and_no_match_names_no_folder(self):
        assert _adapter().read_folder(_IMAGE, folder_name="BASLUS-99999Missing") is None


class TestWriteFolder:
    def test_the_folder_s_files_land_in_the_target(self, tmp_path):
        adapter = _adapter()
        target = tmp_path / "Mcd001.ps2" / "BASLUS-20307Burn"
        target.mkdir(parents=True)
        folder = adapter.read_folder(_IMAGE, folder_name="BASLUS-20307Burn")

        outcome = adapter.write_folder(_IMAGE, folder, str(target))

        assert outcome["status"] == "imported"
        assert outcome["folder"] == "BASLUS-20307Burn"
        assert (target / "BASLUS-20307Burn").read_bytes() == b"progress"
        assert (target / "icon.sys").read_bytes() == b"icon"
        assert not (tmp_path / "Mcd001.ps2" / "BASLUS-20307Burn.importing").exists()

    def test_a_nested_folder_is_refused(self, tmp_path):
        adapter = _adapter()
        target = tmp_path / "card" / "BASLUS-20307Burn"
        target.mkdir(parents=True)
        folder = adapter.read_folder(_IMAGE, folder_name="BASLUS-20307Burn")
        nested = type(folder)(name=folder.name, files=folder.files, folders=(folder,))

        outcome = adapter.write_folder(_IMAGE, nested, str(target))

        assert outcome == {"status": "nested", "folder": "BASLUS-20307Burn", "files": []}
        assert list(target.iterdir()) == []


@pytest.mark.parametrize("name", ["BASLUS-20307Burn"])
def test_writing_over_an_existing_file_replaces_it(tmp_path, name):
    adapter = _adapter()
    target = tmp_path / "card" / name
    target.mkdir(parents=True)
    (target / name).write_bytes(b"older-progress")
    folder = adapter.read_folder(_IMAGE, folder_name=name)

    adapter.write_folder(_IMAGE, folder, str(target))

    assert (target / name).read_bytes() == b"progress"
