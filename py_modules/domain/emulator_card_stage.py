"""A standalone emulator whose memory card the plugin stages from the bank, one game at a time.

Measured on the reference Deck (2026-11-13). A PS1 game played through DuckStation never
reached the server: every session ended ``post_exit_sync skipped: save_shape_unsupported``,
because DuckStation keeps its own memory cards and the plugin knew neither where they were
nor what they were called. DuckStation's own console named both:

    [MemoryCards] Card1Type = PerGameTitle
    Directory = /run/media/deck/SR01T/Emulation/saves/duckstation/saves
    I/System: Memory Card 1: .../saves/duckstation/saves/Disney's Tarzan (USA)_1.mcd

A per-game card named after the game's own title is a name the plugin cannot derive — the
title comes from DuckStation's database, not from the ROM's path — so nothing could be
answered for it. Measured with ``Card1Type = Shared``, the same launch opened
``<Directory>/shared_card_1.mcd``: one fixed name, whatever the game.

So the card moves into the plugin's tree and one game is staged into it at a time:

- ``[MemoryCards] Directory`` is pointed at the bank's ``saves/<platform>``;
- ``[MemoryCards] Card1Type`` is set to ``Shared``, whose file name is fixed;
- before a launch the game's own bank card (``<stem>.srm``, the file the plugin's RetroArch
  launches write and the sync already carries) is copied over the shared card;
- after the session the shared card is copied back and removed, so the next game starts
  from its own card rather than inheriting the last one's saves.

**Why the bank card keeps the ``.srm`` name.** Both formats are one 128 KiB memory-card
image — RetroArch's ``.srm`` and DuckStation's ``.mcd`` are the same bytes — and the existing
PS1 answer, the save bank layout and every synced file already use ``<stem>.srm``. Staging
translates the name, not the shape, so nothing else about PS1 changes.

**Only a declared emulator takes part.** :data:`CARD_STAGES` is the measured fact that
DuckStation states these two keys and opens this file. An emulator nobody has read is absent
from it, and its cards are left where its own settings put them.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass

from domain.save_bank import canonical_platform


@dataclass(frozen=True, slots=True)
class CardStage:
    """How one emulator names the memory card it opens, and where it keeps it."""

    section: str
    directory_key: str
    type_key: str
    card_type: str
    card_file: str
    platform: str


CARD_STAGES: dict[str, CardStage] = {
    # DuckStation's ``settings.ini``: the folder its cards live in, and the card type whose
    # name is fixed (``shared_card_1.mcd``, measured) rather than the game's own title.
    "duckstation": CardStage(
        section="MemoryCards",
        directory_key="Directory",
        type_key="Card1Type",
        card_type="Shared",
        card_file="shared_card_1.mcd",
        platform="psx",
    ),
}

#: The bank file a staged emulator's card is carried as: one 128 KiB card image per game,
#: under the name the plugin's own launches and the sync already use.
STAGED_CARD_SUFFIX = ".srm"


def stages_emulator(emulator_id: str | None) -> bool:
    """Whether a standalone launch by *emulator_id* reads a card this plugin stages."""
    return bool(emulator_id) and emulator_id in CARD_STAGES


@dataclass(frozen=True, slots=True)
class CardHome:
    """The settings write that makes one emulator's card folder the plugin's own."""

    emulator: str
    platform: str
    config_path: str
    directory: str
    settings: tuple[tuple[str, str, str], ...]


@dataclass(frozen=True, slots=True)
class CardStagePlan:
    """One game's card: where the bank keeps it, and the file the emulator opens."""

    emulator: str
    platform: str
    config_path: str
    bank_card: str
    staged_card: str


def card_home_for(
    *,
    emulator_id: str,
    platform: str,
    config_path: str | None,
    saves_root: str,
) -> CardHome | None:
    """The settings this emulator's card folder needs, or ``None`` when it takes no part.

    A settings file is required for the same reason as the BIOS folder: an emulator that has
    never run has nothing to point, and creating its settings would be inventing a config.
    """
    stage = CARD_STAGES.get(emulator_id)
    if stage is None or not config_path:
        return None
    if canonical_platform(platform) != stage.platform:
        return None
    directory = posixpath.join(saves_root, stage.platform)
    return CardHome(
        emulator=emulator_id,
        platform=stage.platform,
        config_path=config_path,
        directory=directory,
        settings=(
            (stage.section, stage.directory_key, directory),
            (stage.section, stage.type_key, stage.card_type),
        ),
    )


def stage_plan(home: CardHome, *, rom_stem: str | None) -> CardStagePlan | None:
    """The card this game stages into *home*'s emulator, or ``None`` without a name."""
    stage = CARD_STAGES.get(home.emulator)
    if stage is None or not rom_stem:
        return None
    return CardStagePlan(
        emulator=home.emulator,
        platform=home.platform,
        config_path=home.config_path,
        bank_card=posixpath.join(home.directory, f"{rom_stem}{STAGED_CARD_SUFFIX}"),
        staged_card=posixpath.join(home.directory, stage.card_file),
    )
