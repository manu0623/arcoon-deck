"""Writes the card settings, and moves one game's card in and out of the emulator's card.

Three small filesystem operations, each with its own refusal:

- **The settings write** replaces two keys in a file the emulator owns and leaves every other
  line alone (``lib.ini_lines``). A missing settings file is refused rather than created.
- **Staging** copies the game's bank card over the emulator's shared card, and removes a
  stale shared card when the bank has none — so a game with no save yet opens an empty card
  instead of the previous game's.
- **Adopting** copies the shared card back into the game's bank card and then removes it, so
  the next game cannot inherit it. A session that saved nothing copies back the same bytes.

A copy is written beside its target and renamed over it, because a crash midway through a
card copy would otherwise leave a half-written memory card where a save used to be.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from lib.ini_lines import rewrite_value

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.emulator_card_stage import CardHome, CardStagePlan

CardHomeStatus = str
"""``written`` (the settings changed), ``already`` (they were the plugin's), ``no-config`` (no
settings file to point) or ``failed`` (the filesystem said no, with a reason)."""

CardMoveStatus = str
"""``staged`` / ``adopted`` (a card moved), ``cleared`` (a stale card removed), ``no-card`` /
``nothing`` (there was nothing to move) or ``failed`` (the filesystem said no)."""


@dataclass(frozen=True, slots=True)
class CardHomeOutcome:
    """What happened to one emulator's card settings."""

    emulator: str
    status: CardHomeStatus
    directory: str
    config_path: str
    note: str | None = None

    @property
    def changed(self) -> bool:
        """Whether this pass wrote the file."""
        return self.status == "written"


class EmulatorCardStageAdapter:
    """Applies :mod:`domain.emulator_card_stage` plans on disk."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        exists: Callable[[str], bool] | None = None,
        read_text: Callable[[str], str] | None = None,
        write_text: Callable[[str, str], object] | None = None,
        copy: Callable[[str, str], object] | None = None,
        remove: Callable[[str], object] | None = None,
    ) -> None:
        self._logger = logger
        self._exists = exists or os.path.exists
        self._read_text = read_text or self._read
        self._write_text = write_text or self._write
        self._copy = copy or self._copy_file
        self._remove = remove or os.remove

    @staticmethod
    def _read(path: str) -> str:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()

    @staticmethod
    def _write(path: str, text: str) -> None:
        temporary = f"{path}.romm-tender.tmp"
        with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)

    @staticmethod
    def _copy_file(src: str, dst: str) -> None:
        temporary = f"{dst}.romm-tender.tmp"
        shutil.copyfile(src, temporary)
        os.replace(temporary, dst)

    def write_home(self, home: CardHome) -> CardHomeOutcome:
        """Point *home*'s emulator at the plugin's card folder, and at a fixed card name."""
        if not self._exists(home.config_path):
            return self._outcome(home, "no-config")
        try:
            text = self._read_text(home.config_path)
        except OSError as exc:
            return self._outcome(home, "failed", note=f"unreadable settings: {exc}")
        rewritten = text
        for section, key, value in home.settings:
            rewritten = rewrite_value(rewritten, section=section, key=key, value=value)
        if rewritten == text:
            return self._outcome(home, "already")
        try:
            self._write_text(home.config_path, rewritten)
        except OSError as exc:
            return self._outcome(home, "failed", note=f"unwritable settings: {exc}")
        return self._outcome(home, "written")

    def stage(self, plan: CardStagePlan) -> CardMoveStatus:
        """Put this game's card where the emulator will open it."""
        if self._exists(plan.bank_card):
            try:
                self._copy(plan.bank_card, plan.staged_card)
            except OSError as exc:
                self._logger.warning(f"Emulator cards: could not stage {plan.bank_card}: {exc}")
                return "failed"
            return "staged"
        # No card for this game: the emulator must not open the last game's.
        if self._exists(plan.staged_card):
            try:
                self._remove(plan.staged_card)
            except OSError as exc:
                self._logger.warning(f"Emulator cards: could not clear {plan.staged_card}: {exc}")
                return "failed"
            return "cleared"
        return "no-card"

    def adopt(self, plan: CardStagePlan) -> CardMoveStatus:
        """Take the card the emulator just wrote back into this game's bank file."""
        if not self._exists(plan.staged_card):
            return "nothing"
        try:
            self._copy(plan.staged_card, plan.bank_card)
            self._remove(plan.staged_card)
        except OSError as exc:
            self._logger.warning(f"Emulator cards: could not adopt {plan.staged_card}: {exc}")
            return "failed"
        return "adopted"

    def _outcome(self, home: CardHome, status: CardHomeStatus, *, note: str | None = None) -> CardHomeOutcome:
        outcome = CardHomeOutcome(
            emulator=home.emulator,
            status=status,
            directory=home.directory,
            config_path=home.config_path,
            note=note,
        )
        if outcome.status == "failed":
            self._logger.warning(f"Emulator cards: could not point {home.emulator} at {home.directory}: {note}")
        return outcome
