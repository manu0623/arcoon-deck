"""Makes a standalone emulator's save folder be the plugin's save folder.

The one operation is *adopt then link*: whatever the emulator already saved is moved
into the plugin's tree, the emulator's now-empty folder is replaced by a symlink to
it. Adopting first is not politeness — a deck that ran the emulator before this
existed holds the user's real progress in that folder, and a link that hides it would
look exactly like lost saves.

Three refusals, each for a state a blunt ``os.symlink`` would make worse:

- **A link that points somewhere else.** Someone (the user, another tool) decided
  where this folder goes. Re-pointing it would redirect their data silently.
- **A name that exists and is not a directory** — a file where a folder belongs is a
  broken install, not something to delete.
- **A merge that would overwrite.** A file with the same name on both sides is two
  different saves; the emulator's copy stays where it is and is named in the outcome
  rather than being replaced by, or replacing, the plugin's.

Every step is injectable — ``symlink``, ``realpath``, ``listdir``, ``move`` — so the
tests describe states instead of performing them.
"""

from __future__ import annotations

import os
import posixpath
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.emulator_save_link import SaveLink

LinkStatus = str
"""``linked`` (no prior content), ``adopted`` (moved, then linked), ``already``,
``skipped`` (refused, with a reason) or ``failed`` (the filesystem said no)."""


@dataclass(frozen=True, slots=True)
class LinkOutcome:
    """What happened to one emulator's save folder.

    ``adopted`` counts the entries moved out of the emulator's folder into the plugin's
    tree; ``conflicts`` names the entries left behind because the plugin's tree already
    held that name — the only case where the emulator keeps a save the sync does not.
    """

    emulator: str
    emulator_dir: str
    owned_dir: str
    status: LinkStatus
    adopted: int = 0
    conflicts: tuple[str, ...] = field(default_factory=tuple)
    note: str | None = None


class EmulatorSaveLinkAdapter:
    """Applies :class:`~domain.emulator_save_link.SaveLink` plans on disk."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        realpath: Callable[[str], str] | None = None,
        isdir: Callable[[str], bool] | None = None,
        islink: Callable[[str], bool] | None = None,
        exists: Callable[[str], bool] | None = None,
        listdir: Callable[[str], list[str]] | None = None,
        move: Callable[[str, str], object] | None = None,
        symlink: Callable[[str, str], object] | None = None,
        make_dirs: Callable[[str], object] | None = None,
        remove_dir: Callable[[str], object] | None = None,
    ) -> None:
        self._logger = logger
        self._realpath = realpath or os.path.realpath
        self._isdir = isdir or os.path.isdir
        self._islink = islink or os.path.islink
        self._exists = exists or os.path.exists
        self._listdir = listdir or os.listdir
        self._move = move or shutil.move
        self._symlink = symlink or os.symlink
        self._make_dirs = make_dirs or (lambda path: os.makedirs(path, exist_ok=True))
        self._remove_dir = remove_dir or os.rmdir

    def apply(self, link: SaveLink) -> LinkOutcome:
        """Make ``link.emulator_dir`` a symlink to ``link.owned_dir``."""
        target = self._realpath(link.owned_dir) if self._exists(link.owned_dir) else link.owned_dir

        if self._islink(link.emulator_dir):
            if self._realpath(link.emulator_dir) == target:
                return self._outcome(link, "already")
            return self._outcome(link, "skipped", note="points-elsewhere")

        adopted: list[str] = []
        conflicts: list[str] = []
        if self._isdir(link.emulator_dir):
            try:
                self._make_dirs(link.owned_dir)
                existing = set(self._listdir(link.owned_dir))
                for entry in sorted(self._listdir(link.emulator_dir)):
                    if entry in existing:
                        conflicts.append(entry)
                        continue
                    self._move(posixpath.join(link.emulator_dir, entry), posixpath.join(link.owned_dir, entry))
                    adopted.append(entry)
            except OSError as exc:
                return self._outcome(link, "failed", note=f"adopt failed: {exc}")

            if self._listdir(link.emulator_dir):
                # Only the refused names are left; the folder has to stay, because
                # linking over it would hide them.
                return self._outcome(
                    link,
                    "skipped",
                    adopted=len(adopted),
                    conflicts=tuple(conflicts),
                    note="merge-conflict",
                )
            try:
                self._remove_dir(link.emulator_dir)
            except OSError as exc:
                return self._outcome(link, "failed", adopted=len(adopted), note=f"rmdir failed: {exc}")
        elif self._exists(link.emulator_dir):
            return self._outcome(link, "skipped", note="not-a-directory")

        try:
            self._make_dirs(link.owned_dir)
            self._make_dirs(posixpath.dirname(link.emulator_dir))
            self._symlink(link.owned_dir, link.emulator_dir)
        except OSError as exc:
            return self._outcome(link, "failed", adopted=len(adopted), note=f"symlink failed: {exc}")

        self._logger.info(
            f"Emulator saves: linked {link.emulator} ({link.provider}) "
            f"{link.emulator_dir} -> {link.owned_dir} (adopted {len(adopted)})"
        )
        return self._outcome(
            link,
            "adopted" if adopted else "linked",
            adopted=len(adopted),
            conflicts=tuple(conflicts),
            note="merge-conflict" if conflicts else None,
        )

    @staticmethod
    def _outcome(
        link: SaveLink,
        status: LinkStatus,
        *,
        adopted: int = 0,
        conflicts: tuple[str, ...] = (),
        note: str | None = None,
    ) -> LinkOutcome:
        return LinkOutcome(
            emulator=link.emulator,
            emulator_dir=link.emulator_dir,
            owned_dir=link.owned_dir,
            status=status,
            adopted=adopted,
            conflicts=conflicts,
            note=note,
        )
