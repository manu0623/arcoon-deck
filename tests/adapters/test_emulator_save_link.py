"""Applying the link, against a real directory tree in a temp folder.

The states that matter are the ones a Deck is actually in: a folder the emulator
created and filled before this existed (adopt), one it never created (plain link), one
already linked (idempotent), and the two refusals that must not clobber anything.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pytest

from adapters.emulator_save_link import EmulatorSaveLinkAdapter
from domain.emulator_save_link import SaveLink

# A symlink on Windows needs a privilege the test user does not have, so the whole
# module is a Linux test: the Deck is the only place these states exist anyway.
pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="creating a symlink needs a privilege Windows does not grant"
)


def _link(tmp_path: Path) -> SaveLink:
    return SaveLink(
        emulator="ppsspp",
        provider="native",
        family="ppsspp",
        platform="psp",
        emulator_dir=str(tmp_path / "config" / "ppsspp" / "PSP" / "SAVEDATA"),
        owned_dir=str(tmp_path / "data" / "saves" / "psp" / "PSP" / "SAVEDATA"),
    )


def _adapter() -> EmulatorSaveLinkAdapter:
    return EmulatorSaveLinkAdapter(logger=logging.getLogger("test_emulator_save_link"))


class TestAdopting:
    def test_saves_the_emulator_already_made_move_into_the_plugin_tree(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        (tmp_path / "config" / "ppsspp" / "PSP" / "SAVEDATA" / "ULUS10025SAVE000").mkdir(parents=True)

        outcome = _adapter().apply(link)

        assert outcome.status == "adopted"
        assert outcome.adopted == 1
        assert (tmp_path / "data" / "saves" / "psp" / "PSP" / "SAVEDATA" / "ULUS10025SAVE000").is_dir()
        assert os.path.islink(link.emulator_dir)
        assert os.path.realpath(link.emulator_dir) == os.path.realpath(link.owned_dir)

    def test_a_name_on_both_sides_is_left_alone_and_named(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        emulator_save = tmp_path / "config" / "ppsspp" / "PSP" / "SAVEDATA" / "ULUS10025SAVE000"
        owned_save = tmp_path / "data" / "saves" / "psp" / "PSP" / "SAVEDATA" / "ULUS10025SAVE000"
        emulator_save.mkdir(parents=True)
        owned_save.mkdir(parents=True)
        (emulator_save / "DATA.BIN").write_text("emulator")
        (owned_save / "DATA.BIN").write_text("plugin")

        outcome = _adapter().apply(link)

        assert outcome.status == "skipped"
        assert outcome.note == "merge-conflict"
        assert outcome.conflicts == ("ULUS10025SAVE000",)
        assert (emulator_save / "DATA.BIN").read_text() == "emulator"
        assert (owned_save / "DATA.BIN").read_text() == "plugin"
        assert not os.path.islink(link.emulator_dir)


class TestLinking:
    def test_an_absent_folder_is_linked_without_touching_anything(self, tmp_path: Path) -> None:
        link = _link(tmp_path)

        outcome = _adapter().apply(link)

        assert outcome.status == "linked"
        assert outcome.adopted == 0
        assert os.path.islink(link.emulator_dir)
        assert (tmp_path / "data" / "saves" / "psp" / "PSP" / "SAVEDATA").is_dir()

    def test_an_empty_folder_is_replaced_by_the_link(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        (tmp_path / "config" / "ppsspp" / "PSP" / "SAVEDATA").mkdir(parents=True)

        outcome = _adapter().apply(link)

        assert outcome.status == "linked"
        assert os.path.islink(link.emulator_dir)

    def test_running_twice_changes_nothing(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        _adapter().apply(link)

        assert _adapter().apply(link).status == "already"


class TestRefusals:
    def test_a_link_pointing_elsewhere_is_left_where_someone_put_it(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        other = tmp_path / "somebody-elses-saves"
        other.mkdir(parents=True)
        link_dir = Path(link.emulator_dir)
        link_dir.parent.mkdir(parents=True)
        os.symlink(other, link_dir)

        outcome = _adapter().apply(link)

        assert outcome.status == "skipped"
        assert outcome.note == "points-elsewhere"
        assert os.path.realpath(link.emulator_dir) == os.path.realpath(other)

    def test_a_file_where_the_folder_belongs_is_not_deleted(self, tmp_path: Path) -> None:
        link = _link(tmp_path)
        link_dir = Path(link.emulator_dir)
        link_dir.parent.mkdir(parents=True)
        link_dir.write_text("not a folder")

        outcome = _adapter().apply(link)

        assert outcome.status == "skipped"
        assert outcome.note == "not-a-directory"
        assert link_dir.read_text() == "not a folder"
