"""Tests for domain/emulator_switches — the switch-spelling rewrite before a bake.

The failing string is the one measured on the reference Deck: a standalone PS2
launch whose shortcut held ``--fullscreen --nogui``, which PCSX2 2.8.2 rejected with
``Unknown parameter: '--fullscreen'`` before any game was parsed.
"""

from __future__ import annotations

from domain.emulator_commands import classify_command, option_to_invocation
from domain.emulator_switches import normalise_switches
from domain.shortcut_data import EmulatorInvocation, build_launch_options

# The exact shape that failed: the flatpak form a resolved ps2 row bakes.
PCSX2_REJECTED = '/usr/bin/flatpak run net.pcsx2.PCSX2 --fullscreen --nogui -- %ROM%'


class TestNormaliseSwitches:
    def test_pcsx2_double_dash_switches_take_the_single_dash_form(self):
        # ``--nogui`` lands on ``-batch`` rather than ``-nogui``: see the abort rule below.
        assert normalise_switches(PCSX2_REJECTED) == '/usr/bin/flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- %ROM%'

    def test_nogui_becomes_batch_because_pcsx2_aborts_under_nogui(self):
        # Measured: two SIGABRT dumps whose command line carried ``-nogui``, and
        # upstream issue #7620 — the page-fault handler asserts and aborts, while
        # batch mode runs. Both mean "close when the game shuts down".
        assert normalise_switches("flatpak run net.pcsx2.PCSX2 -fullscreen -nogui -- %ROM%") == (
            "flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- %ROM%"
        )
        assert normalise_switches("%EMULATOR_PCSX2% --fullscreen --nogui -- %ROM%") == (
            "%EMULATOR_PCSX2% -fullscreen -batch -- %ROM%"
        )

    def test_the_positional_separator_survives(self):
        # PCSX2's own option list keeps ``--`` as "no more arguments"; only the
        # named switches are rewritten.
        assert normalise_switches("%EMULATOR_PCSX2% -batch -- %ROM%") == "%EMULATOR_PCSX2% -batch -- %ROM%"

    def test_already_correct_spellings_are_untouched(self):
        command = "%EMULATOR_PCSX2% -batch -fullscreen %ROM%"
        assert normalise_switches(command) == command

    def test_a_longer_token_carrying_the_letters_is_not_rewritten(self):
        command = "flatpak run net.pcsx2.PCSX2 --fullscreen-extra %ROM%"
        assert normalise_switches(command) == command

    def test_another_emulator_keeps_its_double_dash_switch(self):
        # PPSSPP takes ``--fullscreen``; only a measured refusal is listed.
        command = "%EMULATOR_PPSSPP% --fullscreen %ROM%"
        assert normalise_switches(command) == command

    def test_a_command_naming_no_listed_emulator_is_unchanged(self):
        command = "%EMULATOR_RPCS3% --no-gui %ROM%"
        assert normalise_switches(command) == command


class TestNormaliseAtTheBake:
    def test_build_launch_options_composes_the_accepted_spelling(self):
        options = build_launch_options(
            "flatpak run net.pcsx2.PCSX2 --fullscreen --nogui --",
            "/games/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso",
        )
        assert options == (
            'flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- '
            '"/games/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso"'
        )

    def test_build_launch_options_still_composes_an_empty_command_without_a_target(self):
        assert build_launch_options("flatpak run net.pcsx2.PCSX2 --fullscreen", "") == ""

    def test_option_to_invocation_normalises_the_baked_command(self):
        option = classify_command("PCSX2 (Standalone)", "%EMULATOR_PCSX2% --fullscreen %ROM%")
        assert option_to_invocation(option) == EmulatorInvocation.standalone(
            "%EMULATOR_PCSX2% -fullscreen %ROM%", "PCSX2 (Standalone)"
        )
