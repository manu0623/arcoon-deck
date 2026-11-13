"""The standalone save base, read from the emulator's own settings file.

The catalogue cannot answer this on a device with no ES-DE, so the emulator's own
``nand_directory`` is the truth — measured on the reference Deck, where Eden states
``/home/deck/Emulation/storage/yuzu/nand``.
"""

from __future__ import annotations

import logging

import pytest

from adapters.emulator_save_base import EmulatorSaveBaseAdapter

_EDEN_CONFIG = "/home/deck/.config/eden/qt-config.ini"
_NAND = "/home/deck/Emulation/storage/yuzu/nand"


def _adapter(files: dict[str, str]) -> EmulatorSaveBaseAdapter:
    return EmulatorSaveBaseAdapter(
        user_home="/home/deck",
        logger=logging.getLogger("test_emulator_save_base"),
        read_text=lambda path: files[path],
        exists=lambda path: path in files,
    )


@pytest.fixture
def eden_config() -> str:
    return (
        "nand_directory=" + _NAND + "\n"
        "nand_directory\\default=false\n"
        "sdmc_directory=/home/deck/Emulation/storage/yuzu/sdmc\n"
    )


class TestSwitchBase:
    def test_reads_the_nand_directory_the_emulator_states(self, eden_config: str) -> None:
        base = _adapter({_EDEN_CONFIG: eden_config})("switch")

        # Saves sit one level in from the nand root: nand/user/save/<profile>/<title>.
        assert base == f"{_NAND}/user"

    def test_no_settings_file_answers_nothing(self) -> None:
        assert _adapter({})("switch") is None

    def test_a_config_without_the_key_answers_nothing(self) -> None:
        # An older or edited file must not turn into a guessed ~/.local/share path: the
        # caller's catalogue fallback is honest, a wrong directory is not.
        assert _adapter({_EDEN_CONFIG: "sdmc_directory=/x\n"})("switch") is None


class TestEverythingElse:
    @pytest.mark.parametrize("platform", ["gba", "ps2", "ps3", "gc", "wiiu", "nds"])
    def test_a_family_without_a_verified_rule_answers_nothing(self, platform: str, eden_config: str) -> None:
        # Only the family whose key has been read off a live config is served; every other
        # platform keeps the catalogue's answer rather than a path this plugin invented.
        assert _adapter({_EDEN_CONFIG: eden_config})(platform) is None
