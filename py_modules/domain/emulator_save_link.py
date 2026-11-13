"""Point a standalone emulator's save folder at the tree the plugin syncs.

The plugin redirects the runtime it owns — its RetroArch writes PSP saves into
``<saves>/psp/PSP/SAVEDATA`` because a generated appendconfig says so — but it has
never said anything to a standalone emulator. PPSSPP keeps its memory stick at
``~/.config/ppsspp/PSP``, so the AppImage the install action put in
``~/Applications`` reads an empty ``SAVEDATA`` while the game's savedata sits one
directory away in the plugin's tree. Measured on the reference Deck: the plugin's
``saves/psp/PSP/SAVEDATA/ULUS10025SAVE000`` existed, and the standalone PPSSPP
offered a first-run save.

**Pointing is a symlink, not an emulator setting.** PPSSPP's ``ppsspp.ini`` carries
no memory-stick path (checked on 1.20.4: ``MemStickInserted`` and ``MemStickSize``
are there, a directory is not), so the only lever is the filesystem. A symlink named
``SAVEDATA`` inside the emulator's own memstick resolves to the plugin's directory,
and the emulator reads and writes the same files the sync does — for a native install
and a flatpak alike, because the link is made where each provider keeps its config.

**This module only computes the two paths.** Whether the link exists, and what to do
with saves already in the emulator's folder, is the adapter's business; the decision
of *which* emulators take part is the table below, which is deliberately one entry:
a family whose save root the core launch does not already redirect has nothing to be
pointed at yet.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.save_bank import layout_for

if TYPE_CHECKING:
    from domain.emulator_registry import InstalledEmulator

# The directories a family keeps its saves under *inside its own config root*, in the
# spelling that emulator uses. PPSSPP is the family this exists for: its memstick is
# `<config>/PSP`, and the folder a game's save is named after lives in `SAVEDATA`.
_FAMILY_SAVE_SUBDIRS: dict[str, tuple[str, ...]] = {
    "ppsspp": ("PSP", "SAVEDATA"),
}

# The providers whose config root we know belongs to that install. ``emudeck`` is out
# on purpose: its record is a launcher script, and the emulator behind it may be a
# flatpak that is not installed at all — measured on the reference Deck, linking the
# launcher created ``~/.var/app/org.ppsspp.PPSSPP`` for a sandbox nothing had ever
# launched. A provider that cannot say which install it means does not get a link.
_LINKED_PROVIDERS = ("native", "flatpak")


@dataclass(frozen=True, slots=True)
class SaveLink:
    """One link to make: the emulator's folder, and the plugin's folder it should be.

    ``owned_dir`` is derived from the platform's own layout rather than spelled here,
    so a change to where the bank keeps PSP saves moves the link with it.
    """

    emulator: str
    provider: str
    family: str
    platform: str
    emulator_dir: str
    owned_dir: str


def link_for(install: InstalledEmulator, *, config_root: str, saves_root: str) -> SaveLink | None:
    """The link this install needs, or ``None`` when it takes no part.

    ``None`` covers four real answers, not one: a provider whose install is not a
    directory of its own (EmuDeck's launcher), a family with no declared subdir (the
    emulator's saves are not ours to point), an install with no config root to point at,
    and a platform with no layout in the bank.
    """
    if install.provider not in _LINKED_PROVIDERS:
        return None
    family = install.definition.family
    subdir = _FAMILY_SAVE_SUBDIRS.get(family)
    if subdir is None or not config_root or not saves_root:
        return None

    platforms = install.definition.platforms
    if not platforms:
        return None
    platform = platforms[0]
    layout = layout_for(platform)
    return SaveLink(
        emulator=install.id,
        provider=install.provider,
        family=family,
        platform=layout.platform,
        emulator_dir=posixpath.join(config_root, *subdir),
        owned_dir=posixpath.join(saves_root, *layout.subdir),
    )
