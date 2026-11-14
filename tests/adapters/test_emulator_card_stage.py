"""The writes: two settings keys, and one card file moved in and out of the emulator's slot.

The settings file is DuckStation's real shape, because the point of the write is that
everything else in it survives.
"""

from __future__ import annotations

import logging

from adapters.emulator_card_stage import EmulatorCardStageAdapter
from domain.emulator_card_stage import card_home_for, stage_plan

MEASURED = """[BIOS]
SearchDirectory = /home/deck/.local/share/romm-tender/bios/psx

[MemoryCards]
Card1Type = PerGameTitle
Card2Type = None
Directory = /run/media/deck/SR01T/Emulation/saves/duckstation/saves
UsePlaylistTitle = true

[Folders]
SaveStates = /run/media/deck/SR01T/Emulation/saves/duckstation/states
"""

SAVES = "/home/deck/.local/share/romm-tender/saves"
CONFIG = "/home/deck/.local/share/duckstation/settings.ini"


class _Files:
    """One settings file and the two card paths, as the adapter asks about them."""

    def __init__(self, *, text: str | None = MEASURED, present: set[str] | None = None) -> None:
        self.text = text
        self.written: list[str] = []
        self.copied: list[tuple[str, str]] = []
        self.removed: list[str] = []
        self.present = set(present or ())

    def exists(self, path: str) -> bool:
        if path == CONFIG:
            return self.text is not None
        return path in self.present

    def read_text(self, path: str) -> str:
        assert self.text is not None
        return self.text

    def write_text(self, path: str, text: str) -> None:
        self.written.append(text)
        self.text = text

    def copy(self, src: str, dst: str) -> None:
        self.copied.append((src, dst))
        self.present.add(dst)

    def remove(self, path: str) -> None:
        self.removed.append(path)
        self.present.discard(path)


def _adapter(files: _Files) -> EmulatorCardStageAdapter:
    return EmulatorCardStageAdapter(
        logger=logging.getLogger("test"),
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
        copy=files.copy,
        remove=files.remove,
    )


def _home() -> object:
    home = card_home_for(emulator_id="duckstation", platform="psx", config_path=CONFIG, saves_root=SAVES)
    assert home is not None
    return home


def _plan() -> object:
    plan = stage_plan(_home(), rom_stem="Disney's Tarzan")
    assert plan is not None
    return plan


class TestSettingsHome:
    def test_both_keys_are_written_and_every_other_line_survives(self) -> None:
        files = _Files()

        outcome = _adapter(files).write_home(_home())

        assert outcome.status == "written"
        assert outcome.changed is True
        written = files.written[0]
        assert f"Directory = {SAVES}/psx" in written
        assert "Card1Type = Shared" in written
        assert "Card2Type = None" in written
        assert "UsePlaylistTitle = true" in written
        assert "SearchDirectory = /home/deck/.local/share/romm-tender/bios/psx" in written
        assert "/run/media/deck/SR01T/Emulation/saves/duckstation/saves" not in written

    def test_an_emulator_already_pointed_is_not_rewritten(self) -> None:
        text = MEASURED.replace("/run/media/deck/SR01T/Emulation/saves/duckstation/saves", f"{SAVES}/psx").replace(
            "Card1Type = PerGameTitle", "Card1Type = Shared"
        )
        files = _Files(text=text)

        outcome = _adapter(files).write_home(_home())

        assert outcome.status == "already"
        assert files.written == []

    def test_no_settings_file_is_not_given_one(self) -> None:
        files = _Files(text=None)

        outcome = _adapter(files).write_home(_home())

        assert outcome.status == "no-config"
        assert files.written == []


class TestStaging:
    def test_the_games_card_is_copied_into_the_slot(self) -> None:
        plan = _plan()
        files = _Files(present={plan.bank_card})

        assert _adapter(files).stage(plan) == "staged"
        assert files.copied == [(plan.bank_card, plan.staged_card)]

    def test_a_game_with_no_card_clears_a_stale_slot(self) -> None:
        plan = _plan()
        files = _Files(present={plan.staged_card})

        assert _adapter(files).stage(plan) == "cleared"
        assert files.removed == [plan.staged_card]
        assert files.copied == []

    def test_an_empty_slot_and_no_card_stage_nothing(self) -> None:
        assert _adapter(_Files()).stage(_plan()) == "no-card"

    def test_the_slot_is_adopted_back_into_the_bank_and_emptied(self) -> None:
        plan = _plan()
        files = _Files(present={plan.staged_card})

        assert _adapter(files).adopt(plan) == "adopted"
        assert files.copied == [(plan.staged_card, plan.bank_card)]
        assert files.removed == [plan.staged_card]

    def test_an_empty_slot_adopts_nothing(self) -> None:
        files = _Files()

        assert _adapter(files).adopt(_plan()) == "nothing"
        assert files.copied == []
