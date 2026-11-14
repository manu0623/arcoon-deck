"""Tests for domain.ps2_file_card.select_folder — which folder on a card is this game's."""

from __future__ import annotations

from domain.ps2_file_card import Ps2CardFolder, select_folder

_BURNOUT = Ps2CardFolder(name="BASLUS-20307Burn", files=())
_SLY = Ps2CardFolder(name="BASCUS-97198YAOTWTD!", files=())


def test_the_named_folder_is_taken_even_beside_another_game():
    assert select_folder((_BURNOUT, _SLY), "BASLUS-20307Burn") is _BURNOUT


def test_a_card_holding_one_folder_is_that_game_whoever_named_it():
    assert select_folder((_SLY,), "BASLUS-20307Burn") is _SLY


def test_a_card_holding_several_folders_and_none_named_is_ambiguous():
    assert select_folder((_BURNOUT, _SLY), "BASLUS-99999Other") is None


def test_an_empty_card_names_nothing():
    assert select_folder((), "BASLUS-20307Burn") is None
