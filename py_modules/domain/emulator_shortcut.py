"""One installed emulator, described as the Steam shortcut that opens it.

The library's shortcuts all point at a ROM. Nothing points at an emulator, so a
reader asking "does 3DS actually work on this thing?" has no tile to press — the
emulator only exists as an argument inside a launch option nobody typed. The
collection this module feeds is the answer: one shortcut per installed emulator,
opening the emulator itself, which is where its settings, its controller bindings
and its BIOS paths can be looked at.

**Only the providers whose install is a command line are here.** ``native`` is a
path on disk (an AppImage or a binary), which Steam can exec directly. ``flatpak``
is an application id, which launches through ``flatpak run``. Both are a
self-contained way to start the emulator with no ROM and no arguments, which is
the entire requirement.

What is deliberately left out, and why:

- **EmuDeck launchers.** A launcher script takes a ROM path; run with none it is
  not a window a reader wanted. The emulator it wraps is usually installed
  separately anyway, often by EmuDeck's own flatpaks, and that install is offered.
- **RetroDECK's bundled emulators.** They live inside the sandbox and are reached
  through the frontend, not by path — the scanner already declines to report them.
- **Anything the scanner did not identify.** An unknown binary is not offered a
  title, because a shortcut named after a guess is worse than no tile.

The key is ``<definition id>@<provider>`` rather than the label: two installs of
one emulator under one provider (``rpcs3.AppImage`` beside ``rpcs3.AppImage_old``)
are one pick, and the label carries spaces and brackets that a persisted map is
better off without.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from domain.emulator_registry import InstalledEmulator

FLATPAK_EXE = "/usr/bin/flatpak"
"""Where a Deck's flatpak lives. `flatpak` on PATH is a symlink to it."""

LAUNCHING_PROVIDERS = ("native", "flatpak")
"""The providers whose install can be started as a bare command."""


@dataclass(frozen=True, slots=True)
class EmulatorShortcut:
    """One emulator shortcut: what Steam needs, plus what the art search needs.

    ``launch_options`` is empty for a native build and ``run <app_id>`` for a
    flatpak, because Steam appends launch options to the exe it execs.
    ``search_term`` is the emulator's own name — the string handed to SteamGridDB,
    which knows "PPSSPP" but not "PPSSPP (Flatpak)".
    """

    key: str
    name: str
    exe: str
    start_dir: str
    launch_options: str
    search_term: str
    version: str | None = None
    #: The SteamGridDB id this emulator's own entry has, when its name alone ranks a game
    #: first. ``None`` means "search for it", which is what every other emulator wants.
    sgdb_id: int | None = None


def shortcut_for(install: InstalledEmulator) -> EmulatorShortcut | None:
    """The shortcut for one install, or ``None`` when it cannot be started alone."""
    if install.provider not in LAUNCHING_PROVIDERS:
        return None

    if install.provider == "flatpak":
        return EmulatorShortcut(
            key=f"{install.id}@flatpak",
            name=install.label,
            exe=FLATPAK_EXE,
            # An empty start dir rather than the home folder: flatpak does its own
            # sandbox setup, and a start dir of `~` would put Steam's working
            # directory somewhere nothing needs it.
            start_dir="",
            launch_options=f"run {install.path}",
            search_term=install.definition.display_name,
            version=install.version_hint,
            sgdb_id=install.definition.sgdb_id,
        )

    return EmulatorShortcut(
        key=f"{install.id}@native",
        name=install.label,
        exe=install.path,
        start_dir=posixpath.dirname(install.path),
        launch_options="",
        search_term=install.definition.display_name,
        version=install.version_hint,
        sgdb_id=install.definition.sgdb_id,
    )


def shortcuts(installs: Iterable[InstalledEmulator]) -> list[EmulatorShortcut]:
    """One row per emulator, alphabetical, first install of a key winning.

    First wins because the scanner's order is its own (AppImages, then launchers,
    then flatpaks) and stable; taking a later one to be "newer" would be reading a
    meaning into that order it does not have.
    """
    rows: dict[str, EmulatorShortcut] = {}
    for install in installs:
        row = shortcut_for(install)
        if row is not None and row.key not in rows:
            rows[row.key] = row
    return sorted(rows.values(), key=lambda row: row.name.lower())
