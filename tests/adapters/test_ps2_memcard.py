"""Tests for adapters/ps2_memcard — the bank's folder card and the core's view of it.

The rule under test is the one that protects a user's saves: a file card already in
place is never converted or overwritten, because it holds every game's saves and only
PCSX2's own Memory Card manager can turn it into a folder card without losing them.
"""

from __future__ import annotations

import logging
import os

import pytest
from fakes.ps2_card import build_file_card

from adapters.ps2_memcard import FOLDER_CARD_NAME, Ps2MemcardAdapter
from domain.save_bank import PS2_SUPERBLOCK_FILE, is_formatted_ps2_superblock

_SYMLINK_SKIP = "symlinks unavailable on this host (they need a privilege Windows lacks)"


def _symlink_or_skip(target, link) -> None:
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip(_SYMLINK_SKIP)


def _link_or_skip(adapter: Ps2MemcardAdapter, ra, bank) -> str:
    status = adapter.ensure_core_card_link(str(ra), str(bank))
    if status == "failed":
        pytest.skip(_SYMLINK_SKIP)
    return status


_LOGGER = logging.getLogger("test_ps2_memcard")


def _adapter() -> Ps2MemcardAdapter:
    return Ps2MemcardAdapter(logger=_LOGGER)


class TestEnsureFolderCard:
    def test_a_missing_card_is_created_formatted(self, tmp_path):
        status = _adapter().ensure_folder_card(str(tmp_path))

        card = tmp_path / FOLDER_CARD_NAME
        assert status == "created"
        assert card.is_dir()
        superblock = (card / PS2_SUPERBLOCK_FILE).read_bytes()
        assert is_formatted_ps2_superblock(superblock)

    def test_an_existing_folder_card_is_left_alone(self, tmp_path):
        card = tmp_path / FOLDER_CARD_NAME
        card.mkdir()
        (card / PS2_SUPERBLOCK_FILE).write_bytes(b"\xff" * 0x2000)
        (card / "SCUS-97198").mkdir()

        assert _adapter().ensure_folder_card(str(tmp_path)) == "present"
        assert (card / "SCUS-97198").is_dir()

    def test_a_file_card_is_neither_converted_nor_overwritten(self, tmp_path):
        card = tmp_path / FOLDER_CARD_NAME
        card.write_bytes(b"an 8 MB card full of somebody's saves")

        assert _adapter().ensure_folder_card(str(tmp_path)) == "file_card"
        assert card.is_file()
        assert card.read_bytes() == b"an 8 MB card full of somebody's saves"

    def test_a_folder_card_without_a_superblock_gets_one(self, tmp_path):
        card = tmp_path / FOLDER_CARD_NAME
        card.mkdir()

        assert _adapter().ensure_folder_card(str(tmp_path)) == "present"
        assert (card / PS2_SUPERBLOCK_FILE).is_file()


class TestEnsureCoreCardLink:
    def test_a_missing_folder_is_linked_at_the_bank(self, tmp_path):
        bank = tmp_path / "bank"
        bank.mkdir()
        ra = tmp_path / "retroarch"

        assert _link_or_skip(_adapter(), ra, bank) == "linked"
        link = ra / "system" / "pcsx2" / "memcards"
        assert os.path.islink(link)
        assert os.path.realpath(link) == os.path.realpath(bank)

    def test_a_link_already_naming_the_bank_is_reported(self, tmp_path):
        bank = tmp_path / "bank"
        bank.mkdir()
        ra = tmp_path / "retroarch"
        link = ra / "system" / "pcsx2" / "memcards"
        link.parent.mkdir(parents=True)
        _symlink_or_skip(bank, link)

        assert _link_or_skip(_adapter(), ra, bank) == "already_linked"

    def test_a_link_pointing_elsewhere_is_repointed(self, tmp_path):
        bank = tmp_path / "bank"
        bank.mkdir()
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        ra = tmp_path / "retroarch"
        link = ra / "system" / "pcsx2" / "memcards"
        link.parent.mkdir(parents=True)
        _symlink_or_skip(elsewhere, link)

        assert _link_or_skip(_adapter(), ra, bank) == "linked"
        assert os.path.realpath(link) == os.path.realpath(bank)

    def test_cards_a_real_folder_holds_are_adopted_into_the_bank(self, tmp_path):
        # The measured case: the core already wrote Mcd001.ps2 into its own tree.
        bank = tmp_path / "bank"
        bank.mkdir()
        ra = tmp_path / "retroarch"
        existing = ra / "system" / "pcsx2" / "memcards"
        existing.mkdir(parents=True)
        (existing / "Mcd001.ps2").write_bytes(b"the user's card")

        assert _link_or_skip(_adapter(), ra, bank) == "adopted"
        assert (bank / "Mcd001.ps2").read_bytes() == b"the user's card"
        assert os.path.islink(existing)

    def test_a_card_the_bank_already_holds_is_not_clobbered(self, tmp_path):
        bank = tmp_path / "bank"
        bank.mkdir()
        (bank / "Mcd001.ps2").write_bytes(b"bank copy")
        ra = tmp_path / "retroarch"
        existing = ra / "system" / "pcsx2" / "memcards"
        existing.mkdir(parents=True)
        (existing / "Mcd001.ps2").write_bytes(b"emulator copy")

        _link_or_skip(_adapter(), ra, bank)

        assert (bank / "Mcd001.ps2").read_bytes() == b"bank copy"


FOLDER = "BASCUS-97198YAOTWTD!"


class TestFileCardConversion:
    """A file card is converted rather than left unsyncable, and its image is kept."""

    def test_a_file_card_is_converted_and_the_image_kept(self, tmp_path):
        save = b"SLY-SAVE" * 400
        image = build_file_card({FOLDER: {"save1": save, "icon.sys": b"PS2D" + b"\x00" * 60}})
        card = tmp_path / FOLDER_CARD_NAME
        card.write_bytes(image)

        status = _adapter().ensure_folder_card(str(tmp_path))

        assert status == "converted"
        folder_card = tmp_path / FOLDER_CARD_NAME
        assert folder_card.is_dir()
        assert (folder_card / FOLDER / "save1").read_bytes() == save
        assert (folder_card / PS2_SUPERBLOCK_FILE).is_file()
        kept = tmp_path / f"{FOLDER_CARD_NAME}.file-card-image"
        assert kept.read_bytes() == image

    def test_an_image_that_does_not_parse_is_left_exactly_where_it_is(self, tmp_path):
        card = tmp_path / FOLDER_CARD_NAME
        card.write_bytes(b"not a memory card at all")

        assert _adapter().ensure_folder_card(str(tmp_path)) == "file_card"
        assert card.is_file()
        assert card.read_bytes() == b"not a memory card at all"

    def test_a_converted_card_is_present_on_the_next_run(self, tmp_path):
        card = tmp_path / FOLDER_CARD_NAME
        card.write_bytes(build_file_card({FOLDER: {"save1": b"x"}}))
        _adapter().ensure_folder_card(str(tmp_path))

        assert _adapter().ensure_folder_card(str(tmp_path)) == "present"


class TestBothSlots:
    """Slot 2 is not special: whatever card the bank holds is made syncable."""

    def test_an_empty_bank_gets_slot_one(self, tmp_path):
        assert _adapter().ensure_folder_cards(str(tmp_path)) == {FOLDER_CARD_NAME: "created"}

    def test_a_second_file_card_is_converted_beside_the_first(self, tmp_path):
        save_two = b"SECOND-CARD" * 300
        (tmp_path / FOLDER_CARD_NAME).mkdir()
        (tmp_path / FOLDER_CARD_NAME / PS2_SUPERBLOCK_FILE).write_bytes(b"\xff" * 0x2000)
        (tmp_path / "Mcd002.ps2").write_bytes(build_file_card({FOLDER: {"save1": save_two}}))

        status = _adapter().ensure_folder_cards(str(tmp_path))

        assert status == {FOLDER_CARD_NAME: "present", "Mcd002.ps2": "converted"}
        assert (tmp_path / "Mcd002.ps2" / FOLDER / "save1").read_bytes() == save_two
        assert (tmp_path / "Mcd002.ps2" / PS2_SUPERBLOCK_FILE).is_file()
        assert (tmp_path / "Mcd002.ps2.file-card-image").is_file()

    def test_the_scan_reports_each_card_by_its_own_name(self, tmp_path):
        (tmp_path / "Other.ps2").write_bytes(build_file_card({FOLDER: {"save1": b"x"}}))

        status = _adapter().ensure_folder_cards(str(tmp_path))

        assert status == {"Other.ps2": "converted"}

    def test_an_unformatted_card_becomes_an_empty_folder_card(self, tmp_path):
        # Slot 2 on the reference Deck: 8,650,752 bytes of 0xff, never used.
        (tmp_path / "Mcd002.ps2").write_bytes(b"\xff" * 0x2000)

        status = _adapter().ensure_folder_cards(str(tmp_path))

        assert status == {"Mcd002.ps2": "replaced_blank"}
        assert (tmp_path / "Mcd002.ps2").is_dir()
        assert (tmp_path / "Mcd002.ps2" / PS2_SUPERBLOCK_FILE).is_file()
