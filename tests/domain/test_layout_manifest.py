"""The `layout.json` contract, as a reader: what is managed, and what degrading looks like.

The property under test throughout is the one ADR-0034 rests on: **a file that cannot be
trusted must leave the plugin exactly where it is today.** Every malformed document below
answers `None`, and every malformed entry answers "this platform is not managed" — never a
half-applied launch, and never an error a caller has to catch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
from domain.shortcut_data import EmulatorInvocation, resolve_emulator_invocation

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


def _provision_layout():
    """The provisioner as a module, so the test asserts the argv it WRITES, not a copy."""
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "scripts" / "provision_layout.py"
    spec = importlib.util.spec_from_file_location("provision_layout", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Registered before exec: a module loaded from a path is absent from `sys.modules`, and
    # `@dataclass(slots=True)` needs its own module entry to resolve the fields' annotations.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestTheProvisionedDolphinLaunch:
    """Measured on the reference Deck: a managed argv is baked as a standalone invocation, and
    the shortcut layer wraps that in ``flatpak run net.retrodeck.retrodeck -e "<command>"``.
    RetroDECK's launcher resolves ``%EMULATOR_DOLPHIN%`` to ITS Dolphin, which this device does
    not have, so the wrapper execs nothing and the game exits instantly — the failure that made
    a Wii title refuse to start. The host-spawn form bakes bare argv instead.
    """

    def _manifest(self, platform: str, directory: str, hosts=None) -> dict:
        module = _provision_layout()
        return module.build_manifest(Path("/tmp/layout"), {platform: directory}, hosts=hosts or _hosts())

    @pytest.mark.parametrize("platform", ["gc", "wii"])
    def test_the_stated_argv_bakes_to_the_flatpak_the_device_has(self, platform: str) -> None:
        entry = self._manifest(platform, "/saves/root")["platforms"][platform]
        invocation = EmulatorInvocation.standalone(" ".join(entry["launch"]))
        assert resolve_emulator_invocation({}, invocation) == "/usr/bin/flatpak run org.DolphinEmu.dolphin-emu -b -e"

    @pytest.mark.parametrize("flatpak", ["/usr/local/bin/flatpak", "/home/someone/.local/bin/flatpak"])
    def test_the_argv_names_wherever_flatpak_was_found(self, flatpak: str) -> None:
        entry = self._manifest("wii", "/saves/root", hosts=_hosts(flatpak=flatpak))["platforms"]["wii"]
        invocation = EmulatorInvocation.standalone(" ".join(entry["launch"]))
        assert resolve_emulator_invocation({}, invocation) == f"{flatpak} run org.DolphinEmu.dolphin-emu -b -e"

    def test_no_argv_carries_a_placeholder_nothing_resolves(self) -> None:
        for platform in ("gc", "wii"):
            entry = self._manifest(platform, "/saves/root")["platforms"][platform]
            assert "%EMULATOR_DOLPHIN%" not in entry["launch"]


def _hosts(*, flatpak: str | None = "/usr/bin/flatpak", eden: str | None = None, searched: tuple[str, ...] = ()):
    """What a device states it has, spelled here so no test depends on the host running it."""
    module = _provision_layout()
    return module.HostBinaries(flatpak=flatpak, eden=eden, searched=searched)


class TestTheProvisionerFindsThisDevicesPrograms:
    """Measured in the audit that preceded this: a managed entry named
    `~/Applications/Eden.AppImage` and `/usr/bin/flatpak` outright, so a device whose home or
    Eden install is anywhere else got a launch line that cannot exec."""

    def test_flatpak_is_named_absolutely_when_it_is_there(self) -> None:
        module = _provision_layout()
        found = module.discover_flatpak(isfile=lambda path: path == "/usr/bin/flatpak", which=lambda name: "/x")
        assert found == "/usr/bin/flatpak"

    def test_flatpak_falls_back_to_whatever_path_answers(self) -> None:
        module = _provision_layout()
        found = module.discover_flatpak(isfile=lambda path: False, which=lambda name: "/usr/local/bin/flatpak")
        assert found == "/usr/local/bin/flatpak"

    def test_a_device_with_no_flatpak_states_none(self) -> None:
        module = _provision_layout()
        assert module.discover_flatpak(isfile=lambda path: False, which=lambda name: None) is None

    def test_edens_candidates_are_the_inventorys_own(self) -> None:
        module = _provision_layout()
        home = Path("/home/someone")
        assert module.eden_candidates(home=home)[0] == str(home / "Applications" / "Eden.AppImage")

    def test_eden_resolves_under_the_home_it_was_pointed_at(self, tmp_path) -> None:
        module = _provision_layout()
        (tmp_path / "Applications").mkdir()
        binary = tmp_path / "Applications" / "Eden.AppImage"
        binary.write_text("", encoding="utf-8")
        assert module.discover_eden(home=tmp_path) == str(binary)

    def test_edens_second_candidate_resolves_too(self, tmp_path) -> None:
        module = _provision_layout()
        # Injected rather than written to disk: a case-insensitive filesystem would make the
        # first candidate match the second one's file and hide which candidate answered.
        found = module.discover_eden(home=tmp_path, isfile=lambda path: path.endswith("eden.AppImage"))
        assert found == str(tmp_path / "Applications" / "eden.AppImage")

    def test_a_device_with_no_eden_states_none(self, tmp_path) -> None:
        module = _provision_layout()
        assert module.discover_eden(home=tmp_path) is None

    def test_a_platform_whose_program_is_missing_is_refused(self, tmp_path) -> None:
        module = _provision_layout()
        with pytest.raises(module.ProvisionError):
            module.build_manifest(tmp_path, {"wii": "/dolphin"}, hosts=_hosts(flatpak=None))

    def test_the_refusal_names_what_was_searched(self, tmp_path) -> None:
        module = _provision_layout()
        hosts = _hosts(eden=None, searched=("/home/someone/Applications/Eden.AppImage",))
        with pytest.raises(module.ProvisionError, match=r"Eden\.AppImage"):
            module.build_manifest(tmp_path, {"switch": "/nand/slot"}, hosts=hosts)

    def test_the_switch_argv_names_the_eden_that_was_found(self) -> None:
        module = _provision_layout()
        entry = module.build_manifest(
            Path("/tmp/layout"), {"switch": "/nand/slot"}, hosts=_hosts(eden="/opt/Eden.AppImage")
        )["platforms"]["switch"]
        invocation = EmulatorInvocation.standalone(" ".join(entry["launch"]))
        assert resolve_emulator_invocation({}, invocation) == "/opt/Eden.AppImage -f -g"


class TestProvisioningKeepsWhatItDidNotName:
    """Measured: re-running the provisioner to adopt Wii dropped the Switch entry that was
    already in `layout.json`, and the plugin then answered Switch from the catalogue."""

    def test_a_platform_this_run_does_not_name_keeps_its_entry(self, tmp_path) -> None:
        module = _provision_layout()
        switch_entry = {
            "emulator": "Eden (Standalone)",
            "launch": ["%EMULATOR_FLATPAK-SPAWN%", "--host", "/x", "-f", "-g", "%ROM%"],
            "save_dir": "/nand/user/save/0000000000000000/93543B1D30E2AEB87D0F28AE30D83730/<save_id>",
            "save_unit": "title-dir",
            "needs": ["save_id"],
        }
        (tmp_path / "layout.json").write_text(
            json.dumps({"version": 1, "root": str(tmp_path), "platforms": {"switch": switch_entry}}),
            encoding="utf-8",
        )

        document = module.build_manifest(
            tmp_path, {"wii": "/dolphin/Wii/title/00010000"}, kept=module.existing_entries(tmp_path), hosts=_hosts()
        )

        assert document["platforms"]["switch"] == switch_entry
        assert document["platforms"]["wii"]["save_unit"] == "title-dir"
