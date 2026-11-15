"""Tests for domain.pc_saves — which folder inside a Proton prefix holds saves."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "py_modules"))

from domain.pc_saves import (
    SaveCandidate,
    folder_from_note,
    is_save_candidate,
    name_score,
    pick_save_dir,
    prefix_user_dir,
    relative_to_prefix,
    resolve_relative,
)


def _candidate(name: str, *, files: int = 3, mtime: float = 1.0, path: str | None = None) -> SaveCandidate:
    return SaveCandidate(path=path or f"/prefix/Documents/{name}", name=name, file_count=files, mtime=mtime)


def test_prefix_user_dir_is_the_shortcuts_own_prefix():
    assert (
        prefix_user_dir("/steam/compatdata", 2169565722)
        .replace(os.sep, "/")
        .endswith("2169565722/pfx/drive_c/users/steamuser")
    )


def test_a_short_folder_name_shares_most_of_its_words_with_the_title():
    # "NFS Most Wanted" vs "Need for Speed: Most Wanted": two of the folder's
    # three words are in the title, which is enough to beat an unrelated folder.
    assert name_score("Need for Speed: Most Wanted", "NFS Most Wanted") == pytest.approx(2 / 3)


def test_an_unrelated_folder_scores_zero():
    assert name_score("Need for Speed: Most Wanted", "Microsoft") == 0.0


def test_stopwords_do_not_create_a_false_match():
    # "The" and "of" alone must not make a folder look like the game.
    assert name_score("The Legend of Zelda", "The") == 0.0


def test_a_name_match_beats_a_more_recent_folder():
    older_match = _candidate("NFS Most Wanted", mtime=1.0)
    newer_other = _candidate("Battlefield", mtime=99.0, path="/prefix/Documents/Battlefield")

    picked = pick_save_dir([older_match, newer_other], "Need for Speed: Most Wanted")

    assert picked is not None and picked.name == "NFS Most Wanted"


def test_with_no_name_match_the_most_recently_written_folder_wins():
    older = _candidate("Alpha", mtime=1.0, path="/prefix/Documents/Alpha")
    newer = _candidate("Beta", mtime=5.0, path="/prefix/Documents/Beta")

    picked = pick_save_dir([older, newer], "Completely Different Game")

    assert picked is not None and picked.name == "Beta"


def test_windows_housekeeping_is_never_picked():
    housekeeping = _candidate("Microsoft", mtime=99.0, path="/prefix/Documents/Microsoft")
    game = _candidate("Some Save", mtime=1.0, path="/prefix/Documents/Some Save")

    picked = pick_save_dir([housekeeping, game], "Unrelated Title")

    assert picked is not None and picked.name == "Some Save"


def test_an_empty_folder_is_not_a_candidate():
    assert is_save_candidate("NFS Most Wanted", 0) is False


def test_nothing_usable_answers_none():
    assert pick_save_dir([], "Anything") is None


def test_relative_paths_stay_inside_the_prefix():
    assert relative_to_prefix("/p/steamuser", "/p/steamuser/Documents/Game").replace(os.sep, "/") == "Documents/Game"
    assert relative_to_prefix("/p/steamuser", "/p/steamuser") is None
    assert relative_to_prefix("/p/steamuser", "/elsewhere/Game") is None


def test_exploiting_relative_paths_is_refused():
    assert resolve_relative("/p/steamuser", "Documents/Game") is not None
    assert resolve_relative("/p/steamuser", "../../etc") is None
    assert resolve_relative("/p/steamuser", "") is None


@pytest.mark.parametrize("name", ["Saved Games", "AppData", "Temp"])
def test_system_folders_are_skipped(name):
    assert is_save_candidate(name, 10) is False


class TestTheFolderAnArchiveRecords:
    """The note an archive carries about its own folder, and what we refuse to follow."""

    def test_a_plain_relative_path_is_kept(self):
        assert folder_from_note("Documents/NFS Most Wanted") == "Documents/NFS Most Wanted"

    def test_a_windows_separator_is_read_the_same(self):
        assert folder_from_note("Documents" + chr(92) + "NFS Most Wanted") == "Documents/NFS Most Wanted"

    def test_surrounding_noise_and_a_trailing_slash_are_stripped(self):
        assert folder_from_note("  Documents/Game/  ") == "Documents/Game"

    @pytest.mark.parametrize("note", [None, "", "   ", "/", "../..", "Documents/../..", "/etc"])
    def test_anything_unsafe_is_no_note_at_all(self, note):
        assert folder_from_note(note) is None
