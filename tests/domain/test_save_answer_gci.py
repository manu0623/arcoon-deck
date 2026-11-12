"""Filling the holes a GameCube save has: its region, and the names inside its card.

Measured failure, on the reference Deck: Dolphin in GCI-Folder mode reads
``GC/USA/Card A/*.gci``; the answer carried ``GC/<region>/Card A`` plus "file names
unestablished", so the ROM refused to sync in either direction and the card looked
empty. Both holes are fillable from things a caller already has — the disc's region
byte, and the card folder's own listing.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from domain.content_identity import gamecube_game_code, rvz_gamecube_game_code
from domain.save_answer import (
    SAVE_REGION_NEED,
    SAVE_STATE_HOLE,
    SAVE_STATE_PER_GAME_FILES,
    SAVE_STATE_UNESTABLISHED,
    UNESTABLISHED_DIRECTORY_KNOWN,
    SaveAnswer,
    fill_gci_set,
    fill_region,
    gci_names_for,
)

_FOLDER = "/home/deck/retrodeck/saves/gc/User/GC/<region>/Card A"


def _hole(**overrides) -> SaveAnswer:
    fields = {
        "state": SAVE_STATE_HOLE,
        "unestablished": None,
        "emulator": "Dolphin",
        "directory": _FOLDER,
        "backing_directory": None,
        "granularity": "gci-folder",
        "needs": (SAVE_REGION_NEED,),
        "components": (),
        "caveats": ("file-names-unestablished",),
        "content_installed": True,
    }
    fields.update(overrides)
    return SaveAnswer(**fields)


class TestTheRegionHole:
    def test_it_completes_the_card_folder(self) -> None:
        filled = fill_region(_hole(), "USA")
        assert filled.directory == "/home/deck/retrodeck/saves/gc/User/GC/USA/Card A"
        assert filled.needs == ()

    def test_the_names_still_refuse_on_their_own(self) -> None:
        """Naming the folder is not naming the files: the answer says so, honestly."""
        filled = fill_region(_hole(), "USA")
        assert filled.state == SAVE_STATE_UNESTABLISHED
        assert filled.unestablished == UNESTABLISHED_DIRECTORY_KNOWN

    def test_no_region_leaves_the_hole(self) -> None:
        assert fill_region(_hole(), None) == _hole()

    def test_an_answer_without_the_need_is_untouched(self) -> None:
        answer = _hole(needs=())
        assert fill_region(answer, "USA") == answer

    def test_the_region_is_the_emulators_spelling(self) -> None:
        """``Europe`` is a library word; Dolphin only ever creates ``EUR``."""
        assert "Europe" not in fill_region(_hole(), "EUR").directory


class TestTheCardEntries:
    _CARD = ("01-GZ2E-gczelda2.gci", "02-GMSE-other.gci", "readme.txt")

    def test_the_entries_carrying_this_discs_code_are_the_save(self) -> None:
        assert gci_names_for(self._CARD, "GZ2E") == ("01-GZ2E-gczelda2.gci",)

    def test_the_code_matches_case_insensitively(self) -> None:
        assert gci_names_for(("01-gz2e-lower.gci",), "GZ2E") == ("01-gz2e-lower.gci",)

    @pytest.mark.parametrize("name", ["readme.txt", "GZ2E.gci", "01-GZ2E.gci", "01GZ2E-x.gci"])
    def test_anything_else_is_not_claimed(self, name: str) -> None:
        """A name that is not ``<maker>-<code>-<internal>.gci`` is not this game's."""
        assert gci_names_for((name,), "GZ2E") == ()

    def test_the_set_becomes_syncable(self) -> None:
        filled = fill_gci_set(fill_region(_hole(), "USA"), game_code="GZ2E", names=self._CARD)
        assert filled.state == SAVE_STATE_PER_GAME_FILES
        assert filled.unestablished is None
        assert filled.synced_names == ("01-GZ2E-gczelda2.gci",)
        assert filled.synced_files[0].directory == "/home/deck/retrodeck/saves/gc/User/GC/USA/Card A"

    def test_the_unestablished_caveat_stops_being_true(self) -> None:
        filled = fill_gci_set(fill_region(_hole(), "USA"), game_code="GZ2E", names=self._CARD)
        assert "file-names-unestablished" not in filled.caveats

    def test_an_empty_card_stays_refused(self) -> None:
        """Nothing to carry yet — and the download path places members by their names."""
        answer = fill_region(_hole(), "USA")
        assert fill_gci_set(answer, game_code="GZ2E", names=()) == answer

    def test_another_games_card_is_not_this_ones(self) -> None:
        answer = fill_region(_hole(), "USA")
        assert fill_gci_set(answer, game_code="GALE", names=self._CARD) == answer

    def test_an_answer_that_already_names_its_files_is_untouched(self) -> None:
        answer = replace(_hole(), caveats=())
        assert fill_gci_set(answer, game_code="GZ2E", names=self._CARD) == answer


class TestTheRegionComesFromTheDisc:
    @pytest.mark.parametrize(
        ("code", "region"),
        [(b"GZ2E01", "USA"), (b"GZ2J01", "JAP"), (b"GZ2P01", "EUR")],
    )
    def test_the_region_byte_names_the_card_folder(self, code: bytes, region: str) -> None:
        identity = gamecube_game_code(code + b"\x00" * 32)
        assert identity is not None
        assert identity.save_id == code[:4].decode()
        assert identity.region == region


class TestTheCompressedContainer:
    """A ``.rvz`` is not the disc — its own header carries the disc id at 0x58."""

    @staticmethod
    def _container(ident: bytes = b"GZ2E01") -> bytes:
        return b"RVZ\x01" + b"\x00" * 0x54 + ident + b"\x00" * 0x20

    def test_the_header_copy_is_the_discs_id(self) -> None:
        identity = rvz_gamecube_game_code(self._container())
        assert identity is not None
        assert identity.save_id == "GZ2E"
        assert identity.region == "USA"
        assert ".rvz" in identity.source

    def test_a_bare_disc_is_not_a_container(self) -> None:
        assert rvz_gamecube_game_code(b"GZ2E01" + b"\x00" * 0x40) is None

    def test_a_container_without_a_usable_id_is_refused(self) -> None:
        """The offset is measured, not trusted: a wrong layout answers nothing."""
        assert rvz_gamecube_game_code(self._container(b"NOPE00")) is None

    def test_a_short_head_is_refused(self) -> None:
        assert rvz_gamecube_game_code(b"RVZ\x01") is None
