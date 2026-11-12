"""The `layout.json` contract, as a reader: what is managed, and what degrading looks like.

The property under test throughout is the one ADR-0034 rests on: **a file that cannot be
trusted must leave the plugin exactly where it is today.** Every malformed document below
answers `None`, and every malformed entry answers "this platform is not managed" — never a
half-applied launch, and never an error a caller has to catch.
"""

from __future__ import annotations

import json

import pytest

from domain.layout_manifest import (
    KNOWN_SAVE_UNITS,
    MANIFEST_FILENAME,
    SUPPORTED_VERSION,
    parse_layout_manifest,
)
from domain.save_answer import (
    SAVE_STATE_HOLE,
    SAVE_STATE_PER_GAME_FILES,
    fill_gci_set,
    fill_region,
    manifest_answer,
)

_ROOT = "/home/deck/homebrew/data/romm-tender"

_GC = {
    "emulator": "Dolphin (Standalone)",
    "launch": ["%EMULATOR_DOLPHIN%", "-C", "Core/GCIFolderAPath={root}/saves/gc/GC/%g", "-b", "-e", "%ROM%"],
    "save_dir": "{root}/saves/gc/GC/<region>/Card A",
    "save_unit": "gci-set",
    "needs": ["region"],
}


_DEFAULT_PLATFORMS = {"gc": _GC}


def _document(platforms: object = _DEFAULT_PLATFORMS, **overrides) -> str:
    body = {"version": SUPPORTED_VERSION, "root": _ROOT, "platforms": platforms}
    body.update(overrides)
    return json.dumps(body)


class TestAUsableManifest:
    def test_the_gamecube_entry_keeps_its_placeholders(self) -> None:
        manifest = parse_layout_manifest(_document())
        assert manifest is not None
        entry = manifest.entry_for("ngc")
        assert entry is not None
        assert entry.emulator == "Dolphin (Standalone)"
        assert entry.save_unit == "gci-set"
        assert entry.needs == ("region",)
        assert "%ROM%" in entry.launch_command
        assert "%EMULATOR_DOLPHIN%" in entry.launch_command

    def test_the_root_is_substituted_once_and_only_once(self) -> None:
        manifest = parse_layout_manifest(_document())
        assert manifest is not None
        entry = manifest.entry_for("gc")
        assert entry is not None
        assert "{root}" not in entry.save_dir
        assert entry.save_dir == f"{_ROOT}/saves/gc/GC/<region>/Card A"
        assert f"{_ROOT}/saves/gc/GC/%g" in entry.launch_command

    def test_a_platform_spelled_differently_is_still_the_same_platform(self) -> None:
        """``ngc`` in RomM, ``gc`` in RetroDECK — one platform, either key accepted."""
        manifest = parse_layout_manifest(_document({"ngc": _GC}))
        assert manifest is not None
        assert manifest.entry_for("gc") is not None
        assert manifest.entry_for("ngc") is not None

    def test_an_unmanaged_platform_answers_nothing(self) -> None:
        manifest = parse_layout_manifest(_document())
        assert manifest is not None
        assert manifest.entry_for("ps2") is None
        assert manifest.entry_for("") is None
        assert manifest.entry_for(None) is None

    def test_the_save_unit_defaults_to_one_file(self) -> None:
        entry_body = {"launch": ["%EMULATOR_X%", "%ROM%"], "save_dir": "{root}/saves/x"}
        manifest = parse_layout_manifest(_document({"x": entry_body}))
        assert manifest is not None
        entry = manifest.entry_for("x")
        assert entry is not None
        assert entry.save_unit in KNOWN_SAVE_UNITS
        assert entry.save_unit == "single-file"
        assert entry.needs == ()
        assert entry.emulator is None

    def test_unknown_keys_are_ignored(self) -> None:
        """A newer provisioner may write keys this reader does not read; it still works."""
        entry_body = dict(_GC, future_key={"anything": [1, 2, 3]})
        manifest = parse_layout_manifest(_document({"gc": entry_body}, future_top_level=True))
        assert manifest is not None
        assert manifest.entry_for("gc") is not None


class TestDocumentsThatCannotBeTrusted:
    @pytest.mark.parametrize("text", ["", "not json", "[]", "null", "42"])
    def test_a_document_that_is_not_a_manifest_answers_nothing(self, text: str) -> None:
        assert parse_layout_manifest(text) is None

    def test_a_version_this_reader_does_not_know_answers_nothing(self) -> None:
        """A newer file is not guessed at; the plugin stays on today's behaviour."""
        assert parse_layout_manifest(_document(version=2)) is None
        assert parse_layout_manifest(_document(version="1")) is None
        assert parse_layout_manifest(_document(version=True)) is None
        assert parse_layout_manifest(_document(version=SUPPORTED_VERSION)) is not None

    @pytest.mark.parametrize("root", ["", "   ", None, 7])
    def test_a_manifest_without_a_root_answers_nothing(self, root: object) -> None:
        assert parse_layout_manifest(_document(root=root)) is None

    @pytest.mark.parametrize("platforms", [{}, None, "gc", []])
    def test_a_manifest_without_platforms_answers_nothing(self, platforms: object) -> None:
        assert parse_layout_manifest(_document(platforms=platforms)) is None


class TestEntriesThatCannotBeTrusted:
    @pytest.mark.parametrize(
        "entry",
        [
            {"save_dir": "{root}/saves/x"},  # no launch: nothing to run
            {"launch": [], "save_dir": "{root}/saves/x"},  # empty launch
            {"launch": ["%EMULATOR_X%"], "save_dir": ""},  # no directory
            {"launch": ["%EMULATOR_X%"], "save_dir": "   "},
            {"launch": ["%EMULATOR_X%", 7], "save_dir": "{root}/x"},  # non-string argv
            {"launch": "%EMULATOR_X% %ROM%", "save_dir": "{root}/x"},  # a string, not argv
            {"launch": ["%EMULATOR_X%"], "save_dir": "{root}/x", "save_unit": "cards"},  # unknown unit
            {"launch": ["%EMULATOR_X%"], "save_dir": "{root}/x", "needs": 7},
            {"launch": ["%EMULATOR_X%"], "save_dir": "{root}/x", "emulator": 7},
        ],
    )
    def test_one_bad_entry_does_not_sink_the_others(self, entry: dict) -> None:
        """A typo must switch ONE platform back to inference, not the whole file."""
        document = _document({"gc": _GC, "x": entry})
        manifest = parse_layout_manifest(document)
        assert manifest is not None
        assert manifest.entry_for("gc") is not None
        assert manifest.entry_for("x") is None

    def test_a_file_whose_only_entries_are_bad_is_no_manifest(self) -> None:
        manifest = parse_layout_manifest(_document({"x": {"save_dir": "{root}/x"}}))
        assert manifest is None

    def test_a_platform_key_that_is_not_a_name_is_dropped(self) -> None:
        manifest = parse_layout_manifest(_document({"gc": _GC, "  ": _GC}))
        assert manifest is not None
        assert [entry.platform for entry in manifest.platforms] == ["gc"]


def test_the_contract_names_its_own_file() -> None:
    assert MANIFEST_FILENAME == "layout.json"


class TestTheAnswerAManagedEntryStates:
    """A managed entry names the folder; the same fills settle the region and the entries."""

    def _entry(self, **overrides):
        manifest = parse_layout_manifest(_document({"gc": dict(_GC, **overrides)}))
        assert manifest is not None
        entry = manifest.entry_for("gc")
        assert entry is not None
        return entry

    def test_a_gci_set_states_a_region_hole_and_unnamed_entries(self) -> None:
        answer = manifest_answer(self._entry(), content_installed=True)
        assert answer is not None
        assert answer.state == SAVE_STATE_HOLE
        assert answer.needs == ("region",)
        assert answer.directory == f"{_ROOT}/saves/gc/GC/<region>/Card A"
        assert "file-names-unestablished" in answer.caveats
        assert answer.content_installed is True

    def test_the_fills_settle_it_into_an_upload_unit(self) -> None:
        answer = manifest_answer(self._entry(), content_installed=True)
        assert answer is not None
        settled = fill_gci_set(fill_region(answer, "USA"), game_code="GZ2E", names=("01-GZ2E-gczelda2.gci",))
        assert settled.state == SAVE_STATE_PER_GAME_FILES
        assert settled.synced_names == ("01-GZ2E-gczelda2.gci",)

    def test_an_unmodelled_unit_answers_nothing_rather_than_a_half_answer(self) -> None:
        """Falling back is safer than managing a shape this plugin cannot name files in."""
        assert manifest_answer(self._entry(save_unit="single-file"), content_installed=True) is None
        assert manifest_answer(self._entry(save_unit="directory"), content_installed=True) is None

    def test_no_entry_answers_nothing(self) -> None:
        assert manifest_answer(None, content_installed=True) is None
