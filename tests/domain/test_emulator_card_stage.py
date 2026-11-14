"""The rule: which emulator stages a card, where its settings point, and which file a game is.

Measured on the reference Deck: DuckStation's ``settings.ini`` states ``[MemoryCards]
Directory``, and with ``Card1Type = Shared`` it opens ``<Directory>/shared_card_1.mcd`` — a
fixed name, unlike its default per-game-title card (``Disney's Tarzan (USA)_1.mcd``).
"""

from __future__ import annotations

from typing import Any

from domain.emulator_card_stage import (
    CARD_STAGES,
    card_home_for,
    stage_plan,
    stages_emulator,
)

SAVES = "/home/deck/.local/share/romm-tender/saves"
CONFIG = "/home/deck/.local/share/duckstation/settings.ini"


def _home(**overrides: Any) -> Any:
    arguments: dict[str, Any] = {
        "emulator_id": "duckstation",
        "platform": "psx",
        "config_path": CONFIG,
        "saves_root": SAVES,
    }
    arguments.update(overrides)
    return card_home_for(**arguments)


def test_duckstation_is_pointed_at_the_banks_psx_folder_with_a_fixed_card_name() -> None:
    home = _home()

    assert home is not None
    assert home.directory == f"{SAVES}/psx"
    assert home.settings == (
        ("MemoryCards", "Directory", f"{SAVES}/psx"),
        ("MemoryCards", "Card1Type", "Shared"),
    )


def test_a_game_stages_into_the_shared_card_and_is_carried_as_its_bank_file() -> None:
    home = _home()

    plan = stage_plan(home, rom_stem="Disney's Tarzan")

    assert plan is not None
    assert plan.bank_card == f"{SAVES}/psx/Disney's Tarzan.srm"
    assert plan.staged_card == f"{SAVES}/psx/shared_card_1.mcd"


def test_a_game_with_no_name_stages_nothing() -> None:
    home = _home()

    assert stage_plan(home, rom_stem=None) is None
    assert stage_plan(home, rom_stem="") is None


def test_an_emulator_nobody_read_takes_no_part() -> None:
    assert _home(emulator_id="ppsspp") is None
    assert stages_emulator("ppsspp") is False
    assert stages_emulator(None) is False


def test_an_install_with_no_settings_file_is_not_given_one() -> None:
    assert _home(config_path=None) is None


def test_another_platform_is_left_alone() -> None:
    assert _home(platform="psp") is None


def test_the_table_states_the_one_measured_emulator() -> None:
    stage = CARD_STAGES["duckstation"]

    assert (stage.section, stage.directory_key, stage.type_key) == ("MemoryCards", "Directory", "Card1Type")
    assert (stage.card_type, stage.card_file) == ("Shared", "shared_card_1.mcd")
