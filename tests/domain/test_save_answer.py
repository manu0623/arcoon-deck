"""Tests for the save-answer vocabulary and the rule that picks one state.

The classification is pure, so it is tested here without a machine and without
the resolver's types. What ties these plain strings to the resolver's own
constants is ``tests/adapters/test_atlas_saves.py``; what is under test here is
the RULE — which state wins where two could apply, what may be synced, and what
a download lands as.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from domain.save_answer import (
    BENIGN_SYNC_SKIP_REASONS,
    SAVE_ID_NEED,
    SAVE_SHAPE_UNSUPPORTED_REASON,
    SAVE_STATE_HOLE,
    SAVE_STATE_INSIDE_CONTENT,
    SAVE_STATE_PER_GAME_FILES,
    SAVE_STATE_SHARED,
    SAVE_STATE_UNESTABLISHED,
    UNESTABLISHED_DIRECTORY_KNOWN,
    UNESTABLISHED_NOT_ASKED,
    UNESTABLISHED_NOTHING,
    SaveAnswer,
    SaveComponent,
    SaveGroup,
    build_save_answer,
    fill_save_id,
    pick_download_name,
    save_shape_message,
    unestablished_answer,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DIR = "/saves/gba"

# The resolver's word for a file no declaration describes. Spelled here rather
# than imported because these tests hold no resolver types; it is pinned against
# the resolver's own ``ROLE_UNKNOWN`` in ``tests/adapters/test_atlas_saves.py``.
ROLE_NOBODY_NAMED = "unknown"


def _answer(**overrides):
    kwargs = {
        "emulator": "mGBA",
        "directory": _DIR,
        "backing_directory": None,
        "granularity": "per-game-file",
        "needs": (),
        "file_set_state": "declared",
        "files": ("Game.srm",),
        "groups": (),
        "caveats": (),
        "content_installed": True,
    }
    kwargs.update(overrides)
    return build_save_answer(**kwargs)


class TestExactlyOneStateHolds:
    """Where two states could apply, the precedence decides — and it is fixed."""

    def test_inside_content_outranks_everything(self):
        # A positive statement about where the save is makes the directory
        # answer meaningless, so it wins even over a hole and a shared card.
        answer = _answer(
            caveats=("save-inside-content", "file-names-unestablished"),
            needs=("save_id",),
            granularity="shared-card",
            files=(),
        )

        assert answer.state == SAVE_STATE_INSIDE_CONTENT

    def test_a_refused_file_set_outranks_a_hole(self):
        answer = _answer(file_set_state="unknown", files=(), needs=("save_id",))

        assert answer.state == SAVE_STATE_UNESTABLISHED
        assert answer.unestablished == UNESTABLISHED_NOTHING

    def test_a_hole_outranks_a_shared_card(self):
        # Neither can be completed, and naming the hole says more about why.
        answer = _answer(needs=("region",), granularity="shared-card", files=())

        assert answer.state == SAVE_STATE_HOLE

    def test_shared_outranks_unnamed_contents(self):
        answer = _answer(granularity="shared-file", caveats=("file-names-unestablished",), files=("scd_E.brm",))

        assert answer.state == SAVE_STATE_SHARED

    def test_shared_reads_the_answers_granularity_and_never_a_groups(self):
        # MAME keeps an emulator-wide ``default.cfg`` beside per-game files.
        # That group being shared does not make the GAME's save shared.
        answer = _answer(
            granularity="per-game-file",
            files=("Game.nv",),
            groups=(
                SaveGroup(directory=_DIR, files=("Game.nv",), role="battery", granularity="per-game-file"),
                SaveGroup(directory=_DIR, files=("default.cfg",), role="settings", granularity="shared-file"),
            ),
        )

        assert answer.state == SAVE_STATE_PER_GAME_FILES

    def test_named_files_with_no_hole_are_the_only_syncable_state(self):
        assert _answer().state == SAVE_STATE_PER_GAME_FILES
        assert _answer().syncable is True

    @pytest.mark.parametrize(
        ("kwargs", "state"),
        [
            ({"granularity": "shared-card", "files": ("Mcd001.ps2",)}, SAVE_STATE_SHARED),
            ({"caveats": ("save-inside-image",), "files": ()}, SAVE_STATE_INSIDE_CONTENT),
            ({"needs": ("save_id",)}, SAVE_STATE_HOLE),
            ({"file_set_state": "unknown", "files": ()}, SAVE_STATE_UNESTABLISHED),
        ],
    )
    def test_the_other_four_states_all_refuse(self, kwargs: dict[str, object], state: str):
        answer = _answer(**kwargs)

        assert answer.state == state
        assert answer.syncable is False
        assert answer.synced_names == ()
        assert answer.owned_files == ()


class TestTheShapesOfNotEstablished:
    def test_names_that_could_not_be_established_keep_the_directory(self):
        answer = _answer(caveats=("file-names-unestablished",), files=())

        assert answer.unestablished == UNESTABLISHED_DIRECTORY_KNOWN
        assert answer.directory == _DIR

    def test_a_group_with_no_names_is_not_an_empty_directory(self):
        answer = _answer(
            files=(),
            groups=(SaveGroup(directory=_DIR, files=None, role="battery", granularity="per-game-files"),),
        )

        assert answer.unestablished == UNESTABLISHED_DIRECTORY_KNOWN

    def test_naming_nothing_at_all_is_the_bare_shape(self):
        answer = _answer(files=(), granularity=None, caveats=("core-unaudited",))

        assert answer.unestablished == UNESTABLISHED_NOTHING

    def test_a_question_that_was_put_and_refused_is_the_bare_shape(self):
        answer = unestablished_answer(emulator="Ryubing (Standalone)")

        assert answer.state == SAVE_STATE_UNESTABLISHED
        assert answer.unestablished == UNESTABLISHED_NOTHING
        assert answer.emulator == "Ryubing (Standalone)"

    def test_a_question_that_was_never_put_is_its_own_shape(self):
        # RetroArch writing to the content dir, or no emulator resolving at
        # all: the emulator is not implicated, and a page must not say it is.
        answer = unestablished_answer(shape=UNESTABLISHED_NOT_ASKED)

        assert answer.unestablished == UNESTABLISHED_NOT_ASKED
        assert answer.syncable is False

    def test_the_three_shapes_are_three_values(self):
        assert len({UNESTABLISHED_NOTHING, UNESTABLISHED_DIRECTORY_KNOWN, UNESTABLISHED_NOT_ASKED}) == 3


class TestProgressAndConfiguration:
    def _saturn(self):
        return _answer(
            files=("Game.bkr", "Game.bcr", "Game.smpc"),
            groups=(
                SaveGroup(directory=_DIR, files=("Game.bkr",), role="battery", granularity="per-game-file"),
                SaveGroup(directory=_DIR, files=("Game.bcr",), role="battery", granularity="per-game-file"),
                SaveGroup(directory=_DIR, files=("Game.smpc",), role="settings", granularity="per-game-file"),
            ),
        )

    def test_a_configuration_file_is_owned_and_never_synced(self):
        answer = self._saturn()

        assert [component.name for component in answer.owned_files] == ["Game.bkr", "Game.bcr", "Game.smpc"]
        assert answer.synced_names == ("Game.bkr", "Game.bcr")

    def test_a_file_no_group_claimed_counts_as_progress(self):
        # The plain per-game case: the placement names files and decomposes
        # nothing, so there is no role to read and the file is the save.
        answer = _answer(files=("Game.srm",), groups=())

        assert answer.components[0].role is None
        assert answer.synced_names == ("Game.srm",)

    def test_a_file_whose_role_nobody_named_is_carried(self):
        # The resolver's own value for a file on the machine that no declaration
        # describes. It has to be constructed rather than waited for: nothing on
        # the reference machine answers it today, and the day something does is
        # exactly the day this rule decides whether a save survives. Carried,
        # because the failures are not symmetric — a settings file carried costs
        # a setting, a battery file dropped costs the game.
        answer = _answer(
            files=("Game.srm", "Game.dat"),
            groups=(
                SaveGroup(directory=_DIR, files=("Game.srm",), role="battery", granularity="per-game-file"),
                SaveGroup(directory=_DIR, files=("Game.dat",), role=ROLE_NOBODY_NAMED, granularity="per-game-file"),
            ),
        )

        assert [component.role for component in answer.components] == ["battery", ROLE_NOBODY_NAMED]
        assert all(component.is_progress for component in answer.components)
        assert answer.synced_names == ("Game.srm", "Game.dat")

    @pytest.mark.parametrize("role", ["settings", "notes"])
    def test_only_the_two_configuration_roles_are_held_back(self, role):
        # The other half of the rule above, and what makes it non-vacuous: turn
        # the denial into an allow-list of the roles known today and the case
        # above goes red, while this one stays green either way.
        answer = _answer(
            files=("Game.srm",),
            groups=(SaveGroup(directory=_DIR, files=("Game.srm",), role=role, granularity="per-game-file"),),
        )

        assert answer.owned_files[0].name == "Game.srm"
        assert answer.synced_names == ()


class TestPickDownloadName:
    """The server's extension is a pointer into what the emulator writes."""

    def test_an_exact_match_stands(self):
        assert pick_download_name(("Game.srm",), "Game.srm") == "Game.srm"

    def test_the_answers_longer_name_wins_over_the_path_math(self):
        # Opera writes ``<stem>.0.srm``; a server row carrying extension ``srm``
        # would otherwise download to a file the core never opens.
        assert pick_download_name(("Game.0.srm",), "Game.srm") == "Game.0.srm"

    def test_a_name_the_answer_does_not_hold_keeps_the_computed_one(self):
        assert pick_download_name(("Game.bkr",), "Game.srm") == "Game.srm"

    def test_an_ambiguous_match_is_never_guessed(self):
        assert pick_download_name(("Game.0.srm", "Game.1.srm"), "Game.srm") == "Game.srm"

    def test_a_different_stem_is_not_a_match(self):
        assert pick_download_name(("Other.0.srm",), "Game.srm") == "Game.srm"

    def test_no_answer_at_all_keeps_the_computed_name(self):
        assert pick_download_name((), "Game.srm") == "Game.srm"

    def test_a_computed_name_with_no_extension_is_left_alone(self):
        assert pick_download_name(("Game.srm",), "Game") == "Game"


class TestTheRefusalIsReportedNeutrally:
    def test_the_slug_says_nothing_about_the_server(self):
        assert SAVE_SHAPE_UNSUPPORTED_REASON == "save_shape_unsupported"

    @pytest.mark.parametrize(
        ("kwargs", "needle"),
        [
            ({"granularity": "shared-card", "files": ("Mcd001.ps2",)}, "share"),
            ({"caveats": ("save-inside-content",), "files": ()}, "inside the game file"),
            ({"needs": ("save_id",)}, "identity of the game"),
            ({"file_set_state": "unknown", "files": ()}, "could not be established"),
        ],
    )
    def test_each_refusal_says_something_different(self, kwargs: dict[str, object], needle: str):
        assert needle in save_shape_message(_answer(**kwargs))

    def test_the_message_names_the_emulator_it_is_about(self):
        # Scope is the emulator: PS2 is not unsupported, standalone PCSX2 is.
        message = save_shape_message(_answer(emulator="PCSX2 (Standalone)", granularity="shared-card"))

        assert "(PCSX2 (Standalone))" in message

    def test_an_answer_with_no_emulator_still_reads_as_a_sentence(self):
        assert save_shape_message(unestablished_answer()).endswith(".")


class TestTheBenignSkipListsAgreeAcrossTheWire:
    """The backend's benign-skip set and the frontend's are the same set.

    Two lists, one rule, and nothing joining them: the launch path treats a
    reason outside its list as a real failure and raises the fallback-launch
    confirm, so a slug added on the backend alone nags the user on every launch
    of an affected game. The frontend suite cannot see the backend's list and
    the backend suite does not read TypeScript, which is why the check lives
    here and reads the other side's source directly.
    """

    def _frontend_slugs(self) -> set[str]:
        source = (_REPO_ROOT / "src" / "types" / "saves.ts").read_text(encoding="utf-8")
        block = re.search(
            r"BENIGN_SYNC_SKIP_REASONS:\s*readonly\s+string\[\]\s*=\s*\[(.*?)\]",
            source,
            re.DOTALL,
        )
        assert block is not None, "BENIGN_SYNC_SKIP_REASONS is not declared as an array literal any more"
        names = [name.strip() for name in block.group(1).split(",") if name.strip()]
        slugs = set()
        for name in names:
            value = re.search(rf'export const {re.escape(name)} = "([^"]+)"', source)
            assert value is not None, f"{name} is listed but never assigned a literal slug"
            slugs.add(value.group(1))
        return slugs

    def test_both_sides_carry_the_same_slugs(self):
        assert self._frontend_slugs() == set(BENIGN_SYNC_SKIP_REASONS)

    def test_the_reader_finds_the_slugs_it_is_looking_for(self):
        # Non-vacuous: an empty parse would make the test above pass only when
        # the backend set were empty too, so pin that it actually read them.
        assert self._frontend_slugs() == {"savefiles_in_content_dir", "save_shape_unsupported"}


class TestFillSaveId:
    """Completing the resolver's ``<save_id>`` hole from the game's own identity."""

    _HOLE_DIR = "/sdmc/Nintendo 3DS/0/0/title/<save_id>/data"

    def _hole(self, **overrides) -> SaveAnswer:
        fields = {
            "state": SAVE_STATE_HOLE,
            "unestablished": None,
            "emulator": "Azahar",
            "directory": self._HOLE_DIR,
            "backing_directory": None,
            "granularity": "per-game",
            "needs": (SAVE_ID_NEED,),
            "components": (
                SaveComponent(name="00000001", directory=self._HOLE_DIR, role="battery", granularity="per-game"),
            ),
            "caveats": (),
            "content_installed": True,
        }
        fields.update(overrides)
        return SaveAnswer(**fields)

    def test_the_hole_becomes_a_per_game_save(self) -> None:
        filled = fill_save_id(self._hole(), "00040000/00054000")

        assert filled.state == SAVE_STATE_PER_GAME_FILES
        assert filled.directory == "/sdmc/Nintendo 3DS/0/0/title/00040000/00054000/data"
        assert filled.needs == ()
        assert filled.components[0].directory == filled.directory
        assert filled.syncable is True

    def test_no_id_leaves_the_refusal_exactly_as_it_was(self) -> None:
        hole = self._hole()

        assert fill_save_id(hole, None) is hole
        assert fill_save_id(hole, "") is hole

    def test_an_answer_without_the_need_is_untouched(self) -> None:
        # A per-game answer that happens to hold text looking like a token is not a hole.
        answer = self._hole(state=SAVE_STATE_PER_GAME_FILES, needs=())

        assert fill_save_id(answer, "00040000/00054000") is answer

    def test_another_unfilled_need_keeps_it_a_hole(self) -> None:
        # 3DS extdata is keyed by an id the title id does not fill, so filling one hole
        # must not turn a two-hole answer into a syncable one.
        filled = fill_save_id(self._hole(needs=(SAVE_ID_NEED, "extdata_id")), "00040000/00054000")

        assert filled.state == SAVE_STATE_HOLE
        assert filled.needs == ("extdata_id",)
        assert filled.syncable is False

    def test_a_shared_card_stays_shared(self) -> None:
        filled = fill_save_id(self._hole(granularity="shared-card"), "SLUS-20312")

        assert filled.state == SAVE_STATE_SHARED


class TestOwnedLibretroAnswer:
    """The answer an owned RetroArch launch states about itself.

    The appendconfig the plugin writes sets the save directory, so the plugin knows
    what the core will write and does not need to ask a catalogue — which on a device
    with no ES-DE has no entry for a core's label at all.
    """

    def _answer(self, **overrides):
        from domain.save_answer import owned_libretro_answer

        kwargs = {
            "rom_name": "Legend of Zelda, The - The Minish Cap (USA).gba",
            "emulator": "mGBA",
            "content_installed": True,
        }
        kwargs.update(overrides)
        return owned_libretro_answer(_DIR, **kwargs)

    def test_it_is_syncable_and_names_the_platform_directory(self) -> None:
        answer = self._answer()

        assert answer.state == SAVE_STATE_PER_GAME_FILES
        assert answer.syncable is True
        assert answer.directory == _DIR
        assert answer.unestablished is None
        assert answer.content_installed is True

    def test_the_save_is_named_after_the_content_stem(self) -> None:
        # RetroArch's own override log: "Redirecting save file to .../saves/gba/<stem>.srm".
        answer = self._answer()

        assert answer.synced_names == (
            "Legend of Zelda, The - The Minish Cap (USA).srm",
            "Legend of Zelda, The - The Minish Cap (USA).rtc",
        )

    def test_every_name_is_progress_so_none_is_withheld(self) -> None:
        assert all(component.is_progress for component in self._answer().synced_files)

    def test_a_dot_in_the_name_does_not_truncate_the_stem(self) -> None:
        answer = self._answer(rom_name="Sonic 3.5 (USA).md")

        assert answer.synced_names[0] == "Sonic 3.5 (USA).srm"
