"""Write a PS2 save that RomM holds as a card image into the card the launch reads.

A PS2 emulator keeps every game's saves in one memory card, and the card has two on-disk
shapes: a *file* card (one 8,650,752-byte image) and a *folder* card (a directory with
``_pcsx2_superblock`` and one folder per game). This plugin's launch reads a folder card —
the bank's ``Mcd001.ps2/`` holds each game's own folder, ``BASLUS-20307Burn`` for instance.

Another client uploads the other shape. Measured on the reference server: the Android
device sent ``Burnout (USA) [..].ps2`` and ``autosave [..].ps2`` — whole card images —
and the sync skipped them as "not a file this emulator's answer carries", so a save made
on the handheld at 03:30 never reached a Deck that had last saved at 00:38.

Nothing about that image is a foreign format. The game's folder is inside it, and
:func:`domain.ps2_file_card.read_file_card` reads it — the same reader the bank's own
file-card conversion uses, measured on the handheld's file for rom 5338, which parsed to
``BASLUS-21423GTA30001``, the folder the bank's card holds for that game.

So the matrix admits that row as a target like any other, downloads it, and hands the image
here instead of renaming it into the card folder (8 MB of card where a save folder belongs
reads as nothing at all). This module only writes; *which* save to apply is the sync's
decision, so the import cannot disagree with the bookkeeping that follows it.

Every file is backed up through the sync layer's quarantine before it is replaced, so the
save being overwritten is recoverable as any other download's is.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from domain.ps2_file_card import host_file_name

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.ps2_memcard import Ps2MemcardAdapter
    from domain.ps2_file_card import Ps2CardFolder

#: The extension every PS2 card keeps, whatever emulator wrote it.
CARD_EXTENSION = "ps2"


class Ps2CardImportService:
    """Write the game's folder out of a PS2 card image into the bank's folder card."""

    def __init__(
        self,
        *,
        memcard: Ps2MemcardAdapter,
        quarantine: Callable[[str, str], bool],
        logger: logging.Logger,
    ) -> None:
        self._memcard = memcard
        self._quarantine = quarantine
        self._logger = logger

    def import_card(self, image_path: str, card_dir: str, folder_name: str | None = None) -> dict[str, Any] | None:
        """Write the game's folder out of the card at *image_path* into *card_dir*.

        *card_dir* is the folder card (``…/saves/ps2/Mcd001.ps2``); the game's folder is
        written inside it, selected by *folder_name* — the name the answer's own members
        carry — or, when that is unknown, only when the card holds exactly one game.

        ``None`` when the file names no folder — an unreadable image, or a card holding
        several games and none of them this one. The folder's files are backed up through
        quarantine before any of them is replaced, and a card whose bytes already match is
        reported ``unchanged`` rather than written again.
        """
        try:
            with open(image_path, "rb") as handle:
                image = handle.read()
        except OSError as exc:
            self._logger.warning(f"PS2 card import: cannot read {image_path}: {exc}")
            return None
        folder = self._memcard.read_folder(image, folder_name=folder_name)
        if folder is None:
            self._logger.info(
                f"PS2 card import: the card names no folder for this game "
                f"({folder_name or 'no name known'}); nothing was written"
            )
            return None
        target = os.path.join(card_dir, folder.name)
        names = [host_file_name(item.name) for item in folder.files]
        if self._already_there(image, folder, target):
            return {"status": "unchanged", "folder": folder.name, "files": names}
        for item in folder.files:
            try:
                self._quarantine(target, host_file_name(item.name))
            except Exception as exc:  # no backup, no write
                self._logger.warning(
                    f"PS2 card import: cannot back up {host_file_name(item.name)} in {target}, writing nothing: {exc}"
                )
                return {"status": "backup_failed", "folder": folder.name, "files": []}
        return self._memcard.write_folder(image, folder, target)

    @staticmethod
    def _already_there(image: bytes, folder: Ps2CardFolder, target: str) -> bool:
        """Whether every file the card holds for this game is already what is on disk."""
        for item in folder.files:
            try:
                with open(os.path.join(target, host_file_name(item.name)), "rb") as handle:
                    current = handle.read()
            except OSError:
                return False
            if current != b"".join(image[start : start + length] for start, length in item.spans):
                return False
        return True
