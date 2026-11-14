"""Points one emulator's BIOS folder at the tree the plugin installs into.

The write is a single setting in a file the emulator owns, so everything about the file
this service is not changing has to come back exactly as it was: DuckStation's
``settings.ini`` holds its GPU backend, pad bindings, per-game overrides and everything
else, and a rewrite through a parser would reformat all of it. :func:`_rewrite` walks the
text line by line, replaces the one key inside the one section, and leaves every other
byte — order, comments, blank lines, Windows line ends already normalised by the split —
in place.

Two refusals, both about not making a working deck worse:

- **The plugin's folder is missing or empty.** A user who put their own BIOS where their
  emulator looks already has a working setup; pointing the emulator at an empty folder
  would take that away. Nothing installed means nothing to say.
- **The settings file is missing.** An emulator that has never run has written nothing to
  point; creating a file for it would be inventing a config.

A write is atomic — written beside the original and renamed over it — because a crash
between truncate and write would leave an emulator with no settings at all.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.emulator_bios_home import BiosHome

BiosHomeStatus = str
"""``pointed`` (the value changed), ``already`` (it was the plugin's folder), ``no-bios``
(the folder the plugin would name does not exist or holds nothing), ``no-config`` (no
settings file to point) or ``failed`` (the filesystem said no, with a reason)."""


@dataclass(frozen=True, slots=True)
class BiosHomeOutcome:
    """What happened to one emulator's BIOS folder setting."""

    emulator: str
    status: BiosHomeStatus
    directory: str
    config_path: str
    note: str | None = None

    @property
    def changed(self) -> bool:
        """Whether this pass wrote the file."""
        return self.status == "pointed"


def _rewrite(text: str, *, section: str, key: str, value: str) -> str:
    """*text* with ``[section] key`` set to *value*, and every other line untouched.

    An absent key is added at the end of its section and an absent section at the end of
    the file, which is where an emulator's own defaults would put them.
    """
    out: list[str] = []
    in_section = False
    seen_section = False
    written = False

    def add_key() -> None:
        """Put the key at the end of the section, above the blank lines that close it."""
        blanks: list[str] = []
        while out and not out[-1].strip():
            blanks.append(out.pop())
        out.append(f"{key} = {value}")
        out.extend(blanks)

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_section and not written:
                add_key()
                written = True
            in_section = stripped[1:-1].strip() == section
            seen_section = seen_section or in_section
            out.append(line)
            continue
        if in_section and not written and "=" in stripped and stripped.split("=", 1)[0].strip() == key:
            out.append(f"{key} = {value}")
            written = True
            continue
        out.append(line)
    if in_section and not written:
        add_key()
    if not seen_section:
        if out and out[-1].strip():
            out.append("")
        out.extend((f"[{section}]", f"{key} = {value}"))
    return "\n".join(out) + "\n"


class EmulatorBiosHomeAdapter:
    """Applies :class:`~domain.emulator_bios_home.BiosHome` plans on disk."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        isdir: Callable[[str], bool] | None = None,
        listdir: Callable[[str], list[str]] | None = None,
        exists: Callable[[str], bool] | None = None,
        read_text: Callable[[str], str] | None = None,
        write_text: Callable[[str, str], object] | None = None,
    ) -> None:
        self._logger = logger
        self._isdir = isdir or os.path.isdir
        self._listdir = listdir or os.listdir
        self._exists = exists or os.path.exists
        self._read_text = read_text or self._read
        self._write_text = write_text or self._write

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

    def point(self, plan: BiosHome) -> BiosHomeOutcome:
        """Make *plan*'s emulator search the plugin's folder for *plan*'s platform."""
        if not self._isdir(plan.directory):
            return self._outcome(plan, "no-bios", note="directory-missing")
        try:
            entries = self._listdir(plan.directory)
        except OSError as exc:
            return self._outcome(plan, "failed", note=f"unreadable directory: {exc}")
        if not entries:
            return self._outcome(plan, "no-bios", note="directory-empty")
        if not self._exists(plan.config_path):
            return self._outcome(plan, "no-config")
        try:
            text = self._read_text(plan.config_path)
        except OSError as exc:
            return self._outcome(plan, "failed", note=f"unreadable settings: {exc}")
        rewritten = _rewrite(text, section=plan.section, key=plan.key, value=plan.directory)
        if rewritten == text:
            return self._outcome(plan, "already")
        try:
            self._write_text(plan.config_path, rewritten)
        except OSError as exc:
            return self._outcome(plan, "failed", note=f"unwritable settings: {exc}")
        return self._outcome(plan, "pointed")

    def _outcome(self, plan: BiosHome, status: BiosHomeStatus, *, note: str | None = None) -> BiosHomeOutcome:
        outcome = BiosHomeOutcome(
            emulator=plan.emulator,
            status=status,
            directory=plan.directory,
            config_path=plan.config_path,
            note=note,
        )
        if outcome.status == "failed":
            self._logger.warning(f"Emulator BIOS: could not point {plan.emulator} at {plan.directory}: {note}")
        return outcome
