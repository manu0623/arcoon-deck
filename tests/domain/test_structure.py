"""The structure setting: which tree the built-in runtime answers from (ADR-0046)."""

from __future__ import annotations

from domain.runtime import (
    RETROARCH_FLATPAK_ROOT,
    RuntimeMode,
    Structure,
    resolve_roots,
    resolve_structure,
)

_HOME = "/home/deck"
_DATA = "/home/deck/.local/share/romm-tender"
_RA = "/home/deck/" + "/".join(RETROARCH_FLATPAK_ROOT)


def _roots(setting: object, *, data_dir: str = _DATA):
    return resolve_roots(
        mode=RuntimeMode.BUILTIN,
        home=_HOME,
        retrodeck_roots={},
        settings={"structure": setting},
        data_dir=data_dir,
    )


class TestWhichStructureIsChosen:
    def test_the_shipped_default_is_the_app_folder(self) -> None:
        assert resolve_structure(None) is Structure.APP

    def test_every_known_shape_is_read(self) -> None:
        for structure in Structure:
            assert resolve_structure(structure.value) is structure

    def test_a_word_the_code_does_not_know_reads_as_the_app_folder(self) -> None:
        # A typo must not reroute where data lives.
        assert resolve_structure("emulationstation") is Structure.APP


class TestTheRootsEachStructureAnswers:
    def test_the_app_folder_keeps_everything_under_the_data_directory(self) -> None:
        roots = _roots("app")

        assert roots.roms == _DATA + "/roms"
        assert roots.saves == _DATA + "/saves"
        assert roots.bios == _DATA + "/bios"
        assert roots.states == _DATA + "/states"
        assert roots.cores == _DATA + "/cores"

    def test_the_emudeck_tree_is_the_deck_tree(self) -> None:
        roots = _roots("emudeck")

        assert roots.roms == _HOME + "/Emulation/roms"
        assert roots.saves == _HOME + "/Emulation/saves"
        assert roots.bios == _HOME + "/Emulation/bios"
        # Cores belong to the program that loads them.
        assert roots.cores == _RA + "/cores"

    def test_retroarch_answers_with_its_own_folders(self) -> None:
        roots = _roots("retroarch")

        assert roots.saves == _RA + "/saves"
        assert roots.states == _RA + "/states"
        assert roots.bios == _RA + "/system"
        assert roots.cores == _RA + "/cores"
        # RetroArch has no ROM root, so the app keeps the files it downloaded.
        assert roots.roms == _DATA + "/roms"

    def test_custom_falls_back_to_the_emudeck_shape_when_a_path_is_blank(self) -> None:
        roots = _roots("custom")

        assert roots.roms == _HOME + "/Emulation/roms"
        assert roots.bios == _HOME + "/Emulation/bios"

    def test_a_per_root_override_beats_the_structure(self) -> None:
        roots = resolve_roots(
            mode=RuntimeMode.BUILTIN,
            home=_HOME,
            retrodeck_roots={},
            settings={"structure": "app", "bios_dir": "/mnt/sdcard/bios"},
            data_dir=_DATA,
        )

        assert roots.bios == "/mnt/sdcard/bios"
        assert roots.roms == _DATA + "/roms"

    def test_a_caller_without_a_data_directory_falls_back_to_the_deck_tree(self) -> None:
        # Only a probe or a test omits it; answering with a plugin-relative path would be
        # a tree nobody created.
        roots = _roots("app", data_dir="")

        assert roots.roms == _HOME + "/Emulation/roms"
        assert roots.cores == _RA + "/cores"
