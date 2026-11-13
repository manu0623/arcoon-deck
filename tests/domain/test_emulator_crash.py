"""Tests for domain/emulator_crash — reading dumps and tying one to a ROM's launch.

The JSON sample and the launch command are both the measured ones from the reference
Deck: two SIGABRT dumps of ``/app/bin/pcsx2-qt`` after a PS2 session whose baked entry
was ``flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- "<rom>"``.
"""

from __future__ import annotations

import json

from domain.emulator_crash import (
    Coredump,
    crash_payload,
    crashed_emulator,
    emulator_name_tokens,
    parse_coredumps,
)

MEASURED_JSON = json.dumps(
    [
        {
            "time": 1794604364085378,
            "pid": 273611,
            "uid": 1000,
            "gid": 1000,
            "sig": 6,
            "corefile": "inaccessible",
            "exe": "/app/bin/pcsx2-qt",
            "size": None,
        },
        {
            "time": 1794604405447346,
            "pid": 273733,
            "uid": 1000,
            "gid": 1000,
            "sig": 6,
            "corefile": "inaccessible",
            "exe": "/app/bin/pcsx2-qt",
            "size": None,
        },
    ]
)

PCSX2_LAUNCH = (
    'flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- '
    '"/home/deck/.local/share/romm-tender/roms/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso"'
)
RETROARCH_LAUNCH = (
    'flatpak run org.libretro.RetroArch -L '
    "/home/deck/.var/app/org.libretro.RetroArch/config/retroarch/cores/pcsx2_libretro.so "
    "--appendconfig=/home/deck/.local/share/romm-tender/retroarch/retroarch-ps2.cfg "
    '"/home/deck/.local/share/romm-tender/roms/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso"'
)


class TestParseCoredumps:
    def test_reads_the_measured_listing(self):
        dumps = parse_coredumps(MEASURED_JSON)
        assert [d.pid for d in dumps] == [273611, 273733]
        assert all(d.signal == 6 for d in dumps)
        assert all(d.exe == "/app/bin/pcsx2-qt" for d in dumps)
        assert dumps[0].signal_name == "SIGABRT"

    def test_an_empty_listing_is_no_dumps(self):
        assert parse_coredumps("[]") == ()
        assert parse_coredumps("") == ()

    def test_output_that_is_not_this_json_is_no_dumps(self):
        # "could not read it" must never become "a crash happened"; the adapter above
        # this layer reports unaskable separately.
        assert parse_coredumps("TIME PID UID GID SIG COREFILE EXE\n") == ()
        assert parse_coredumps('{"not": "a list"}') == ()

    def test_rows_missing_the_fields_this_needs_are_skipped(self):
        assert parse_coredumps(json.dumps([{"pid": 1}, "nonsense"])) == ()

    def test_executable_name_drops_directories(self):
        dump = Coredump(timestamp_us=1, pid=2, signal=11, exe="/usr/bin/retroarch")
        assert dump.executable_name == "retroarch"
        assert dump.signal_name == "SIGSEGV"


class TestEmulatorNameTokens:
    def test_a_flatpak_app_id_contributes_its_last_segment(self):
        assert "pcsx2" in emulator_name_tokens(PCSX2_LAUNCH)

    def test_a_quoted_rom_path_contributes_nothing(self):
        tokens = emulator_name_tokens(PCSX2_LAUNCH)
        assert all(" " not in token for token in tokens)
        assert "sly" not in tokens

    def test_a_core_file_names_the_emulators_it_involves(self):
        tokens = emulator_name_tokens(RETROARCH_LAUNCH)
        assert "retroarch" in tokens
        assert "pcsx2" in tokens

    def test_the_launcher_is_not_a_name(self):
        assert "flatpak" not in emulator_name_tokens(PCSX2_LAUNCH)


class TestCrashedEmulator:
    def test_a_matching_dump_is_the_crash(self):
        dumps = parse_coredumps(MEASURED_JSON)
        dump = crashed_emulator(dumps, emulator_name_tokens(PCSX2_LAUNCH))
        assert dump is not None
        assert dump.pid == 273611

    def test_an_unrelated_dump_is_not_this_sessions_crash(self):
        dumps = parse_coredumps(MEASURED_JSON)
        tokens = emulator_name_tokens('%EMULATOR_PPSSPP% --fullscreen "/roms/psp/game.iso"')
        assert crashed_emulator(dumps, tokens) is None

    def test_no_dumps_is_no_crash(self):
        assert crashed_emulator((), ("pcsx2",)) is None

    def test_the_payload_names_what_died(self):
        dumps = parse_coredumps(MEASURED_JSON)
        payload = crash_payload(dumps[0])
        assert payload == {
            "exe": "/app/bin/pcsx2-qt",
            "pid": 273611,
            "signal": 6,
            "signal_name": "SIGABRT",
            "detected_at_us": 1794604364085378,
        }
