"""The bank directory the save lookup reads — and the switch that has to allow it.

This adapter is one half of a pair: the generated appendconfig redirects a launch into
these directories, and ``RomInfoService`` reads them. A test here is a test about the
pair staying in step, which is why the switched-off case is the first one.
"""

from __future__ import annotations

import logging
import os

from adapters.save_bank_dir import SaveBankDirAdapter

DATA = "/home/deck/.local/share/romm-tender"


def _adapter(enabled=None) -> SaveBankDirAdapter:
    return SaveBankDirAdapter(data_dir=DATA, logger=logging.getLogger("test"), enabled=enabled)


class TestTheSwitch:
    def test_off_answers_nothing(self) -> None:
        # The whole point: with the bank off, the lookup keeps the RetroArch path math.
        assert _adapter(lambda: False)("gba") is None

    def test_a_hand_edited_non_boolean_off_value_answers_nothing(self) -> None:
        # Settings files get edited by hand; an empty string or None is "off", not "on".
        assert _adapter(lambda: None)("gba") is None
        assert _adapter(lambda: "")("gba") is None

    def test_on_answers_the_platform_directory(self) -> None:
        assert _adapter(lambda: True)("gba") == os.path.join(DATA, "saves", "gba")

    def test_the_switch_is_read_per_call_not_captured(self) -> None:
        # Toggling the setting has to take effect on the next launch, not the next restart.
        state = {"on": False}
        adapter = _adapter(lambda: state["on"])

        assert adapter("snes") is None
        state["on"] = True
        assert adapter("snes") == os.path.join(DATA, "saves", "snes")

    def test_no_switch_at_all_means_enabled(self) -> None:
        # A caller with no settings to consult (tests, a future non-plugin host) gets the
        # bank's answer rather than a silent refusal.
        assert _adapter()("gb") == os.path.join(DATA, "saves", "gb")


class TestWhichPlatforms:
    def test_an_alias_resolves_to_the_bank_s_own_folder(self) -> None:
        # RomM says "ps1", the bank says "psx": one system, one directory.
        assert _adapter()("ps1") == os.path.join(DATA, "saves", "psx")

    def test_a_standalone_platform_is_not_answered(self) -> None:
        # 3DS saves live in Azahar's tree; the bank knows that shape but no launch has
        # been pointed at it, so naming a directory here would promise a redirect nobody
        # performs — and a sync would carry files from an empty folder.
        assert _adapter()("n3ds") is None
        assert _adapter()("gc") is None
        assert _adapter()("dreamcast") is None

    def test_an_unknown_platform_falls_back_to_the_libretro_file_shape(self) -> None:
        # The bank treats anything unlisted as <stem>.srm in saves/<slug>, which is what
        # the appendconfig already redirects; answering keeps the two in step.
        assert _adapter()("some-new-platform") == os.path.join(DATA, "saves", "some-new-platform")
