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
of *which* emulators take part is the table below — one entry per emulator whose save
folder was verified on a device, because a row is a claim about where that program
really writes.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.emulator_registry import all_definitions
from domain.save_bank import SaveFamily, layout_for

if TYPE_CHECKING:
    from domain.emulator_registry import InstalledEmulator


@dataclass(frozen=True, slots=True)
class SavePoint:
    """Where one emulator keeps its saves, stated against the root its provider computes.

    ``in_data_dir`` chooses which of the two XDG roots the subdir hangs off, because the
    two emulators this covers disagree: PPSSPP keeps its whole memstick in the config
    root (``config/ppsspp/PSP``), while Azahar keeps its settings in ``config/azahar-emu``
    and its NAND beside its data (``data/azahar-emu/{nand,sdmc}``).
    """

    in_data_dir: bool
    subdir: tuple[str, ...]


# Keyed by definition id, not family: the folder is spelled by the emulator, and that
# spelling is not the family's. Azahar and Citra share a save format but not a directory
# (``azahar-emu`` vs ``citra-emu``), so only the install actually measured gets a row.
_SAVE_POINTS: dict[str, SavePoint] = {
    # The memstick PPSSPP builds under its config root; the folder a game's save is named
    # after lives in ``SAVEDATA``.
    "ppsspp": SavePoint(in_data_dir=False, subdir=("PSP", "SAVEDATA")),
    # Measured on the reference Deck: "Nintendo 3DS" holds the console's id0/id1 tree, the
    # same shape the bank's n3ds layout reads, so the two sides line up level for level.
    "azahar": SavePoint(in_data_dir=True, subdir=("sdmc", "Nintendo 3DS")),
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


def linked_save_families() -> frozenset[SaveFamily]:
    """The bank families this table covers, for callers that only hold a platform.

    A caller with a platform slug (the bank-directory lookup) cannot name an install, so
    it asks which of the BANK's families are covered instead — the platform's save shape,
    not the emulator's family name, because that is the vocabulary those callers hold.
    Derived from the registry and the layout table rather than spelled twice, since a
    platform written down here and one written in the table are exactly the pair that
    drifts apart.
    """
    return frozenset(
        layout_for(definition.platforms[0]).family
        for definition in all_definitions()
        if definition.id in _SAVE_POINTS and definition.platforms
    )


def links_emulator(emulator_id: str | None) -> bool:
    """Whether a standalone launch by *emulator_id* writes into the plugin's tree.

    The save layer asks this about a resolved ``EmulatorInvocation`` (whose
    ``emulator`` field is a definition id), and the answer decides whether the emulator's
    own directory or the bank is the truth about where this launch writes. An id in the
    table is an id whose install the startup pass points, so the two can never disagree.
    """
    return bool(emulator_id) and emulator_id in _SAVE_POINTS


def link_for(
    install: InstalledEmulator, *, config_root: str, saves_root: str, data_root: str | None = None
) -> SaveLink | None:
    """The link this install needs, or ``None`` when it takes no part.

    ``None`` covers five real answers, not one: a provider whose install is not a
    directory of its own (EmuDeck's launcher), an emulator with no declared save point
    (its saves are not ours to point), an install with no root to point at — including a
    data-root emulator handed no data root — an install with no platform, and a platform
    with no layout in the bank.
    """
    if install.provider not in _LINKED_PROVIDERS:
        return None
    point = _SAVE_POINTS.get(install.id)
    if point is None or not saves_root:
        return None
    root = data_root if point.in_data_dir else config_root
    if not root:
        return None

    platforms = install.definition.platforms
    if not platforms:
        return None
    platform = platforms[0]
    layout = layout_for(platform)
    return SaveLink(
        emulator=install.id,
        provider=install.provider,
        family=install.definition.family,
        platform=layout.platform,
        emulator_dir=posixpath.join(root, *point.subdir),
        owned_dir=posixpath.join(saves_root, *layout.subdir),
    )
