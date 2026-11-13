"""The owned Dolphin launch: one command, and the save directory that follows from it.

Measured failure on the reference Deck: the plugin baked RetroDECK's placeholder command,
so the emulator's user directory was chosen after the plugin stopped looking. The session
wrote `~/retrodeck/saves/gc/User/GC/USA/Card A/01-GZ2E-gczelda2.gci` while the save layer
resolved `~/retrodeck/saves/gc` — where an old misplaced zip sat — skipped that zip as
already synced and carried nothing. Pinning `-u` makes the directory a fact of the command
we bake, and the answer below is derived from that pin instead of from a catalogue's model
of where the emulator might write.
"""

from __future__ import annotations

import pytest

from domain.owned_dolphin import (
    command_with_user_dir,
    gc_card_dir,
    is_owned_dolphin,
    user_dir_for,
    wii_title_dir,
    with_user_dir,
)
from domain.save_answer import (
    SAVE_STATE_HOLE,
    SAVE_STATE_PER_GAME_FILES,
    fill_gci_set,
    fill_region,
    owned_dolphin_answer,
)
from domain.shortcut_data import EmulatorInvocation, resolve_emulator_invocation

_USER_DIR = "/home/deck/retrodeck/saves/gc/User"
_COMMAND = "%EMULATOR_DOLPHIN% -b -e %ROM%"


class TestTheFlagGoesWhereTheEmulatorReadsIt:
    def test_it_sits_after_the_binary_and_before_the_rom(self) -> None:
        assert command_with_user_dir(_COMMAND, _USER_DIR) == f"%EMULATOR_DOLPHIN% -u {_USER_DIR} -b -e %ROM%"

    def test_a_command_without_a_binary_token_is_refused(self) -> None:
        """Not an ES-DE invocation — there is nowhere to put a flag."""
        assert command_with_user_dir("dolphin-emu -b -e game.rvz", _USER_DIR) is None

    def test_a_command_that_states_its_own_user_dir_is_left_alone(self) -> None:
        """Somebody else's decision about the user directory is not ours to overwrite."""
        assert command_with_user_dir("%EMULATOR_DOLPHIN% -u /elsewhere -b -e %ROM%", _USER_DIR) is None

    def test_only_a_standalone_launch_can_be_pinned(self) -> None:
        libretro = EmulatorInvocation.libretro(core_so="dolphin_libretro", label="Dolphin")
        assert with_user_dir(libretro, _USER_DIR) is None

    def test_a_standalone_launch_carries_the_fact_the_bake_reads(self) -> None:
        """The invocation records the pin; the command is composed once, at render time."""
        invocation = EmulatorInvocation.standalone(_COMMAND, label="Dolphin (Standalone)", emulator="DOLPHIN")
        pinned = with_user_dir(invocation, _USER_DIR)
        assert pinned is not None
        assert pinned.user_dir == _USER_DIR
        assert f"-u {_USER_DIR}" not in pinned.command

    def test_the_baked_override_carries_the_pin(self) -> None:
        invocation = EmulatorInvocation.standalone(_COMMAND, label="Dolphin (Standalone)", emulator="DOLPHIN")
        pinned = with_user_dir(invocation, _USER_DIR)
        assert pinned is not None
        rendered = resolve_emulator_invocation({}, pinned)
        assert f"-u {_USER_DIR}" in rendered
        assert "%ROM%" in rendered


class TestWhichEmulatorThisPinIsAbout:
    @pytest.mark.parametrize(
        ("label", "emulator"),
        [("Dolphin (Standalone)", "DOLPHIN"), ("Dolphin", None), (None, "DOLPHIN")],
    )
    def test_dolphin_is_the_emulator(self, label: str | None, emulator: str | None) -> None:
        assert is_owned_dolphin(label, emulator)

    @pytest.mark.parametrize(
        ("label", "emulator"),
        [("PrimeHack (Standalone)", "PRIMEHACK"), (None, None), ("Dolphin", "PRIMEHACK")],
    )
    def test_nothing_else_is(self, label: str | None, emulator: str | None) -> None:
        """PrimeHack is Dolphin's fork with its OWN user tree — pinning would cross saves."""
        assert not is_owned_dolphin(label, emulator)


class TestTheDirectoryThePinImplies:
    def test_gamecube_keeps_its_user_tree_under_the_saves_root(self) -> None:
        assert user_dir_for("ngc", "/home/deck/retrodeck/saves") == "/home/deck/retrodeck/saves/gc/User"

    def test_a_trailing_slash_does_not_double_up(self) -> None:
        assert user_dir_for("gc", "/home/deck/retrodeck/saves/") == "/home/deck/retrodeck/saves/gc/User"

    def test_wii_is_pinned_in_its_own_tree(self) -> None:
        """The same program writes both systems' saves, so the same pin serves both."""
        assert user_dir_for("wii", "/home/deck/retrodeck/saves") == "/home/deck/retrodeck/saves/wii/User"

    def test_a_platform_this_emulator_does_not_write_is_not_pinned(self) -> None:
        """Wii U is Cemu's; pinning Dolphin's tree onto it would cross saves."""
        assert user_dir_for("wiiu", "/home/deck/retrodeck/saves") is None
        assert user_dir_for("ps2", "/home/deck/retrodeck/saves") is None

    def test_the_wii_title_tree_is_under_the_same_user_directory(self) -> None:
        assert wii_title_dir(_USER_DIR) == f"{_USER_DIR}/Wii/title"

    def test_the_card_folder_is_the_emulators_own_default(self) -> None:
        assert gc_card_dir(_USER_DIR) == f"{_USER_DIR}/GC/<region>/Card A"


class TestTheAnswerTheLaunchImplies:
    def test_it_states_a_region_hole_and_unnamed_entries(self) -> None:
        answer = owned_dolphin_answer(_USER_DIR, content_installed=True)
        assert answer.state == SAVE_STATE_HOLE
        assert answer.needs == ("region",)
        assert "file-names-unestablished" in answer.caveats
        assert answer.directory == f"{_USER_DIR}/GC/<region>/Card A"

    def test_the_same_fills_settle_it(self) -> None:
        answer = fill_region(owned_dolphin_answer(_USER_DIR, content_installed=True), "USA")
        filled = fill_gci_set(answer, game_code="GZ2E", names=("01-GZ2E-gczelda2.gci",))
        assert filled.state == SAVE_STATE_PER_GAME_FILES
        assert filled.syncable
        assert filled.synced_names == ("01-GZ2E-gczelda2.gci",)
        assert filled.synced_files[0].directory == f"{_USER_DIR}/GC/USA/Card A"
