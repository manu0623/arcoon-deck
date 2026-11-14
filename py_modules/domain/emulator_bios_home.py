"""Which standalone emulator states a BIOS folder, and what folder to state.

Measured on the reference Deck while fixing a crash. Disney's Tarzan (PSX) was started
from its library tile with DuckStation chosen and the game window closed inside two
seconds — three times, each session under 2.5 s in the plugin's own log. Running the
shortcut's exact command from a shell named the cause in DuckStation's own output::

    I/BIOS: Searching for a NTSC-U BIOS in '/run/media/deck/SR01T/Emulation/bios'...
    W(FindBIOSImageInDirectory): Skipping 'readme.txt': incorrect size

and then no ``I/System: Using BIOS`` line at all. The emulator refuses to boot a disc
without one, and ``-batch`` — the flag the baked shortcut carries — exits instead of
opening its BIOS-missing dialog. The plugin had downloaded SCPH-5500/5501/5502 into
``<app>/bios/psx`` hours earlier; DuckStation was searching the SD card's per-system
folder, which holds no PlayStation image. Pointing that setting at the plugin's folder
booted the same game in 1.0 s.

The lesson is the save link's, one asset over: a standalone emulator reads its own
folders, and the plugin's tree is read only when the emulator is told to look there.
RetroArch is told at launch (the owned launch states ``system_directory``); a standalone
emulator is told nothing, because its BIOS folder is its own setting rather than a launch
argument.

**Only a declared emulator takes part.** :data:`BIOS_DIRECTORY_KEYS` is a measured fact
about one settings file — DuckStation keeps ``[BIOS] SearchDirectory`` in
``settings.ini`` — not a convention guessed from family names. An emulator nobody has
read is absent from the table and is never written to: a wrong section would make the
plugin edit a file for a reason it cannot state.

**One platform per emulator.** The folder named is ``<bios root>/<platform>``, which is
where the plugin's firmware install puts a platform's images. An emulator that plays
several systems cannot be pointed at one of them without aiming the other system's BIOS
search at the wrong tree, so it is left alone rather than half-right.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass

BIOS_DIRECTORY_KEYS: dict[str, tuple[str, str]] = {
    # DuckStation's ``settings.ini``, under its own data directory on Linux
    # (``~/.local/share/duckstation``): the section and key its BIOS search reads.
    "duckstation": ("BIOS", "SearchDirectory"),
}
"""Emulator id -> ``(section, key)`` holding the folder it searches for BIOS images."""


@dataclass(frozen=True, slots=True)
class BiosHome:
    """One settings write: the folder one emulator should search, and where to say so."""

    emulator: str
    config_path: str
    section: str
    key: str
    directory: str


def bios_home_for(
    *,
    emulator_id: str,
    platforms: tuple[str, ...],
    config_path: str | None,
    bios_root: str,
    platform: str | None = None,
) -> BiosHome | None:
    """The one write this install needs, or ``None`` when it needs no write.

    *config_path* is the settings file the config reader found, and a missing one means
    no write: an emulator that has never run has no settings to point, and creating a
    file for it would be inventing a config the emulator did not write.

    *platform* narrows both the question and the answer: a start-up pass asks about every
    install (``None``), while a pre-launch pass asks only about the installs that can play
    the system about to start — and then the answer's folder is that system's.
    """
    key = BIOS_DIRECTORY_KEYS.get(emulator_id)
    if key is None or not config_path:
        return None
    targets = tuple(slug for slug in platforms if platform is None or slug == platform)
    if len(targets) != 1:
        return None
    return BiosHome(
        emulator=emulator_id,
        config_path=config_path,
        section=key[0],
        key=key[1],
        directory=posixpath.join(bios_root, targets[0]),
    )
