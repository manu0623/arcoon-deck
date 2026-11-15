"""Where a PC game keeps its saves inside its Proton prefix — pure decisions.

A Proton game runs inside a Wine prefix that belongs to its Steam shortcut, so
its saves live under ``<Steam>/steamapps/compatdata/<appId>/pfx/drive_c/users/
steamuser`` — not in the plugin's per-system save directory, and not next to the
game's files. This module answers only two questions: which folders under that
prefix *could* be saves, and which one most plausibly belongs to this ROM. It
does no I/O.

The candidates are the places Windows games actually write: ``Documents``,
``Saved Games``, ``AppData/Roaming`` and ``AppData/Local``. The pick is a name
match first (``Documents/NFS Most Wanted`` for *Need for Speed: Most Wanted*),
then the most recently written folder, because a game's own save folder is
written by playing while the surrounding Windows folders are touched once when
the prefix is created.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

#: Where the Windows user's document/app-data folders sit inside the prefix.
PREFIX_USER_SUFFIX: tuple[str, ...] = ("pfx", "drive_c", "users", "steamuser")

#: The entry a save archive carries at its root, recording the folder the files
#: came from relative to the Wine user directory. Without it a second machine has
#: to guess where another machine's save belongs, which is how a save arrives and
#: lands in the wrong place (or nowhere) on a fresh setup.
ARCHIVE_FOLDER_NOTE = ".arcoon-folder"


def folder_from_note(note: str | None) -> str | None:
    """The folder an archive records for itself, or ``None`` when it records none.

    Accepts either separator so an archive written on one platform is readable on
    the other, and rejects anything that is not a plain relative path — an absolute
    path, a drive letter, or a ``..`` component is a note we will not follow. The
    caller still resolves the result against its own prefix.
    """
    if not note:
        return None
    text = note.strip().replace("\\", "/")
    if not text or text.startswith("/") or ":" in text:
        return None
    parts = text.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        return None
    return "/".join(parts)


#: The folders Windows games put saves in. Relative to the prefix's user folder.
SAVE_ROOTS: tuple[str, ...] = ("Documents", "Saved Games", "AppData/Roaming", "AppData/Local")

#: Windows housekeeping that lives beside the saves but is never a game's own.
#: A candidate whose name is one of these is skipped before scoring.
SKIP_NAMES: frozenset[str] = frozenset(
    {
        "microsoft",
        "microsoft corporation",
        "packages",
        "programs",
        "temp",
        "dxvk",
        "nvidia",
        "d3dscache",
        "intel",
        "amd",
        "wine",
        "windows",
        "desktop",
        "downloads",
        "music",
        "pictures",
        "videos",
        "links",
        "favorites",
        "saved games",
        "my games",
        "appdata",
    }
)

#: Words that carry no identity in a game title, so they may not make a folder
#: look like a match ("The", "of", "2005" in `Need for Speed: Most Wanted 2005`).
_STOPWORDS: frozenset[str] = frozenset(
    {"the", "a", "an", "of", "and", "for", "to", "in", "on", "edition", "remastered", "hd"}
)


@dataclass(frozen=True)
class SaveCandidate:
    """One folder that could be a PC game's saves."""

    path: str
    name: str
    file_count: int
    mtime: float


def prefix_user_dir(compatdata_root: str, app_id: int) -> str:
    """The Windows user folder of the prefix belonging to shortcut *app_id*."""
    return os.path.join(compatdata_root, str(int(app_id)), *PREFIX_USER_SUFFIX)


def _tokens(text: str) -> frozenset[str]:
    """Lowercase alphanumeric words of *text*, minus the ones that mean nothing."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return frozenset(word for word in words if word not in _STOPWORDS and len(word) > 1)


def name_score(rom_name: str, candidate_name: str) -> float:
    """How much *candidate_name* looks like *rom_name*, from 0 to 1.

    The share of the candidate's own words that appear in the game's title, so a
    folder called ``NFS Most Wanted`` scores 1.0 against *Need for Speed: Most
    Wanted* (both of its words are in the title) while ``Microsoft`` scores 0.

    A year in the title is dropped from the game's words: keys are matched
    against the folder, not the other way round, because the folder is usually
    shorter than the store title.
    """
    game = _tokens(rom_name)
    folder = _tokens(candidate_name)
    if not folder:
        return 0.0
    return len(folder & game) / len(folder)


def is_save_candidate(name: str, file_count: int) -> bool:
    """Whether a folder named *name* with *file_count* files could be a save folder."""
    if file_count <= 0:
        return False
    return name.strip().lower() not in SKIP_NAMES


def pick_save_dir(candidates: list[SaveCandidate], rom_name: str) -> SaveCandidate | None:
    """The candidate that most plausibly holds *rom_name*'s saves, or ``None``.

    A name match beats recency: two games can share one prefix only by accident,
    but a game's folder is named after it while ``AppData/Roaming`` is written
    by installers and runtimes. When nothing matches by name, the most recently
    written candidate wins — that is the folder the game just played from.
    """
    usable = [c for c in candidates if is_save_candidate(c.name, c.file_count)]
    if not usable:
        return None
    scored = [(name_score(rom_name, c.name), c) for c in usable]
    best_score = max(score for score, _ in scored)
    if best_score > 0:
        tied = [c for score, c in scored if score == best_score]
        return max(tied, key=lambda c: (c.mtime, c.path))
    return max(usable, key=lambda c: (c.mtime, c.path))


def relative_to_prefix(prefix_user: str, path: str) -> str | None:
    """*path* relative to *prefix_user*, or ``None`` when it is not inside it.

    The stored answer is relative so a prefix rebuilt under the same appId keeps
    finding the folder, and so a path from a hand-edited row can never point the
    sync outside the game's own prefix.
    """
    root = os.path.normpath(prefix_user)
    target = os.path.normpath(path)
    if target == root or not target.startswith(root + os.sep):
        return None
    # Stored with forward slashes so the value means the same on both platforms.
    return os.path.relpath(target, root).replace(os.sep, "/")


def resolve_relative(prefix_user: str, relative: str) -> str | None:
    """*relative* inside *prefix_user*, or ``None`` when it would escape it."""
    if not relative:
        return None
    root = os.path.normpath(prefix_user)
    target = os.path.normpath(os.path.join(root, relative))
    if target == root or not target.startswith(root + os.sep):
        return None
    return target
