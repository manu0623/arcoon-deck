"""The rule: which emulator gets a BIOS folder write, and which folder it is."""

from __future__ import annotations

from typing import Any

from domain.emulator_bios_home import BIOS_DIRECTORY_KEYS, bios_home_for

BIOS_ROOT = "/home/deck/.local/share/romm-tender/bios"
CONFIG = "/home/deck/.local/share/duckstation/settings.ini"


def _plan(**overrides: Any) -> Any:
    arguments: dict[str, Any] = {
        "emulator_id": "duckstation",
        "platforms": ("psx",),
        "config_path": CONFIG,
        "bios_root": BIOS_ROOT,
    }
    arguments.update(overrides)
    return bios_home_for(**arguments)


def test_duckstation_is_pointed_at_its_own_platforms_folder() -> None:
    plan = _plan()

    assert plan is not None
    assert plan.directory == f"{BIOS_ROOT}/psx"
    assert (plan.section, plan.key) == ("BIOS", "SearchDirectory")
    assert plan.config_path == CONFIG


def test_an_emulator_that_has_written_no_settings_is_left_alone() -> None:
    assert _plan(config_path=None) is None


def test_an_emulator_nobody_read_is_left_alone() -> None:
    assert _plan(emulator_id="ppsspp") is None


def test_an_emulator_with_several_platforms_names_no_folder() -> None:
    assert _plan(platforms=("psx", "ps2")) is None


def test_a_launch_pass_answers_only_for_the_platform_about_to_start() -> None:
    assert _plan(platform="psx") is not None
    assert _plan(platform="psp") is None


def test_the_table_states_the_one_measured_key() -> None:
    assert BIOS_DIRECTORY_KEYS == {"duckstation": ("BIOS", "SearchDirectory")}
