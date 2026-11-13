"""How a PSP save is described, redirected and carried (ADR-0048)."""

from __future__ import annotations

from domain.retroarch_appendconfig import appendconfig_dirs
from domain.save_answer import unit_answer
from domain.save_bank import describe_unit, layout_for, restores_by_extraction

DATA_DIR = "/home/deck/.local/share/romm-tender"
PSP_BASE = f"{DATA_DIR}/saves/psp/PSP/SAVEDATA"


class TestTheRedirect:
    def test_the_appendconfig_states_the_parent_and_the_lookup_states_the_tree(self) -> None:
        layout = layout_for("psp")

        save_dir, state_dir = appendconfig_dirs(
            data_dir=DATA_DIR, layout_subdir=layout.subdir, core_subdir=layout.core_subdir
        )

        assert save_dir == f"{DATA_DIR}/saves/psp"
        assert state_dir == f"{DATA_DIR}/states/psp"
        # The core's own tree then lands exactly where the lookup reads.
        assert f"{save_dir}/PSP/SAVEDATA" == PSP_BASE

    def test_a_subdir_without_a_core_tail_is_unchanged(self) -> None:
        save_dir, _state = appendconfig_dirs(data_dir=DATA_DIR, layout_subdir=("gba",), core_subdir=())

        assert save_dir == f"{DATA_DIR}/saves/gba"


class TestTheSaveUnit:
    def test_the_members_are_the_folders_carrying_the_disc_id(self) -> None:
        tree = {
            PSP_BASE: ["ULUS10064DATA00", "ULUS10064SETTINGS", "ULUS10567SYSDATA"],
        }

        unit = describe_unit(layout_for("psp"), bank_root="", base=PSP_BASE, save_id="ULUS10064", tree=tree)

        assert unit.members
        assert unit.archive_roots == ("ULUS10064DATA00", "ULUS10064SETTINGS")
        assert unit.place_path == PSP_BASE
        assert unit.usable

    def test_no_identity_is_a_hole_rather_than_a_guess(self) -> None:
        unit = describe_unit(layout_for("psp"), bank_root="", base=PSP_BASE, save_id=None, tree={})

        assert not unit.usable
        assert unit.needs == ("save_id",)

    def test_an_identity_with_no_folders_is_an_empty_unit(self) -> None:
        """The game has never saved: nothing to upload, and the folder it would use is named."""
        unit = describe_unit(layout_for("psp"), bank_root="", base=PSP_BASE, save_id="ULUS10064", tree={PSP_BASE: []})

        assert unit.members == ()
        assert unit.needs == ()
        assert unit.place_path == PSP_BASE


class TestTheCarry:
    def test_a_psp_save_is_restored_from_an_archive(self) -> None:
        """RomM holds the folder set as one zip, so the restore extracts rather than renames."""
        assert restores_by_extraction("psp") is True

    def test_an_ordinary_platform_is_still_a_plain_file(self) -> None:
        assert restores_by_extraction("gba") is False


class TestTheAnswer:
    def test_an_empty_memory_stick_is_still_syncable(self) -> None:
        """With nothing saved yet the download is what creates the folders."""
        unit = describe_unit(layout_for("psp"), bank_root="", base=PSP_BASE, save_id="ULUS10064", tree={PSP_BASE: []})

        answer = unit_answer(unit, emulator="PPSSPP (libretro)", content_installed=True)

        assert answer.syncable is True
        assert answer.directory == PSP_BASE
        # Carried as the one archive RomM holds, so the restore extracts into the base.
        assert answer.granularity == "title-dir"
        assert answer.synced_names == ()

    def test_a_missing_identity_is_still_a_hole(self) -> None:
        unit = describe_unit(layout_for("psp"), bank_root="", base=PSP_BASE, save_id=None, tree={})

        answer = unit_answer(unit, emulator="PPSSPP (libretro)", content_installed=True)

        assert answer.syncable is False
        assert answer.needs == ("save_id",)
