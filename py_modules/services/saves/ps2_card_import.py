"""Apply a PS2 save that RomM holds as a card image to the card the launch reads.

A PS2 emulator keeps every game's saves in one memory card, and the card has two on-disk
shapes: a *file* card (one 8,650,752-byte image) and a *folder* card (a directory with
``_pcsx2_superblock`` and one folder per game). This plugin's launch reads a folder card —
the bank's ``Mcd001.ps2/`` holds each game's own folder, ``BASLUS-20307Burn`` for instance —
and uploads that folder as one archive.

Another client uploads the other shape. Measured on the reference server: the Android
device sent ``Burnout (USA) [..].ps2`` and ``autosave [..].ps2`` — whole card images — and
the sync skipped them as "not a file this emulator's answer carries", so a save made on
the handheld at 03:30 never reached a Deck that had last saved at 00:38.

Nothing about that image is a foreign format. The game's folder is inside it, and
:func:`domain.ps2_file_card.read_file_card` reads it — the same reader the bank's own
file-card conversion uses, measured on the handheld's file for rom 5338, which parsed to
``BASLUS-21423GTA30001``, the folder the bank's card holds for that game.

So a card that is the NEWEST save in the slot is opened and its game's folder written into
the folder the launch reads. Two guards keep that from doing harm:

- **Only the newest save in the slot.** A card older than what this device already has is
  history; writing it would roll the player back, so it is left where it is. Checked
  across every emulator's rows, because the handheld uploads under its own key.
- **Bytes compared before anything is written.** A card already applied is a no-op rather
  than a copy of the same 8 MB on every launch.

Every file is backed up through the sync layer's quarantine before it is replaced, so the
save being overwritten is recoverable as any other download's is.
"""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from adapters.ps2_memcard import Ps2MemcardAdapter
    from domain.ps2_file_card import Ps2CardFolder
    from services.protocols import RommSyncApi
    from services.saves.rom_info import RomInfoService

#: The extension every PS2 card keeps, whatever emulator wrote it.
CARD_EXTENSION = "ps2"
#: The slot ordinary play goes to; a named slot is a deliberate checkpoint this never touches.
DEFAULT_SLOT = "autosave"
#: The system whose saves travel as a memory card.
PS2_SYSTEM = "ps2"


class Ps2CardImportService:
    """Bring a card-shaped PS2 save from the server into the bank's folder card."""

    def __init__(
        self,
        *,
        rom_info: RomInfoService,
        romm_api: RommSyncApi,
        memcard: Ps2MemcardAdapter,
        quarantine: Callable[[str, str], bool],
        logger: logging.Logger,
    ) -> None:
        self._rom_info = rom_info
        self._romm_api = romm_api
        self._memcard = memcard
        self._quarantine = quarantine
        self._logger = logger

    def import_newest(self, rom_id: int) -> dict[str, Any] | None:
        """Apply the slot's newest PS2 card to this ROM's folder, or answer ``None``.

        ``None`` is every case where there is nothing to do: another system, a refusing
        answer, no server saves, or a newest save that is not a card (this plugin's own
        archive, or another client's flat file). The caller treats all of them the same —
        the ordinary sync decides, exactly as it did before.
        """
        info = self._rom_info.get_rom_save_info(rom_id)
        if not info or (info.get("system") or "") != PS2_SYSTEM:
            return None
        answer = self._rom_info.save_answer(rom_id)
        card_dir = getattr(answer, "directory", None)
        if answer is None or not answer.syncable or not card_dir:
            return None
        newest = self._newest_in_slot(rom_id)
        if newest is None:
            return None
        if _extension(newest) != CARD_EXTENSION:
            return None
        return self._apply(rom_id, int(newest["id"]), card_dir, game_folder(answer), newest)

    # ------------------------------------------------------------------
    # Reading the slot
    # ------------------------------------------------------------------

    def _newest_in_slot(self, rom_id: int) -> dict[str, Any] | None:
        """The newest save the slot holds, whichever emulator wrote it."""
        try:
            saves = self._romm_api.list_saves(rom_id)
        except Exception as exc:  # a server that cannot answer is not a broken launch
            self._logger.warning(f"PS2 card import: cannot list saves for rom {rom_id}: {exc}")
            return None
        candidates = [
            save for save in saves if (save.get("slot") or DEFAULT_SLOT) == DEFAULT_SLOT and save.get("id") is not None
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda save: save.get("updated_at") or "")

    # ------------------------------------------------------------------
    # Applying the card
    # ------------------------------------------------------------------

    def import_card(self, image_path: str, card_dir: str, folder_name: str | None = None) -> dict[str, Any] | None:
        """Write the game's folder out of the card at *image_path* into *card_dir*.

        *card_dir* is the folder card (``…/saves/ps2/Mcd001.ps2``); the game's folder is
        written inside it, selected by *folder_name* — the name the answer's own members
        carry — or, when that is unknown, only when the card holds exactly one game.

        ``None`` when the file names no folder — an unreadable image, or a card holding
        several games and none of them this one. The folder's files are backed up through
        quarantine before any of them is replaced, and a card whose bytes already match is
        reported ``unchanged`` rather than written again.

        Public because a version switch downloads the same card (``VersionsService``), so
        both the launch and the restore take the identical path into the bank.
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
        names = [item.name for item in folder.files]
        if self._already_there(image, folder, target):
            return {"status": "unchanged", "folder": folder.name, "files": names}
        for item in folder.files:
            try:
                self._quarantine(target, item.name)
            except Exception as exc:  # no backup, no write
                self._logger.warning(f"PS2 card import: cannot back up {item.name} in {target}, writing nothing: {exc}")
                return {"status": "backup_failed", "folder": folder.name, "files": []}
        return self._memcard.write_folder(image, folder, target)

    def _apply(
        self,
        rom_id: int,
        save_id: int,
        card_dir: str,
        folder_name: str | None,
        server_save: dict[str, Any],
    ) -> dict[str, Any] | None:
        staged = f"{card_dir}.card"
        try:
            self._romm_api.download_save(save_id, staged)
        except Exception as exc:
            self._logger.warning(f"PS2 card import: cannot download save {save_id}: {exc}")
            return None
        try:
            outcome = self.import_card(staged, card_dir, folder_name)
        finally:
            with contextlib.suppress(OSError):
                os.remove(staged)
        if outcome is None:
            self._logger.info(
                f"PS2 card import: rom {rom_id}'s newest save is a card that names no folder "
                f"for this game ({folder_name or 'no name known'}); leaving it on the server"
            )
            return {"status": "no_folder"}
        if outcome.get("status") == "imported":
            self._logger.info(
                f"PS2 card import: rom {rom_id} took {outcome.get('folder')} "
                f"({len(outcome.get('files') or ())} file(s)) from save {server_save.get('id')} "
                f"made {server_save.get('updated_at')} into {card_dir}"
            )
        return outcome

    @staticmethod
    def _already_there(image: bytes, folder: Ps2CardFolder, target: str) -> bool:
        """Whether every file the card holds for this game is already what is on disk."""
        for item in folder.files:
            try:
                with open(os.path.join(target, item.name), "rb") as handle:
                    current = handle.read()
            except OSError:
                return False
            if current != b"".join(image[start : start + length] for start, length in item.spans):
                return False
        return True


def game_folder(answer: Any) -> str | None:
    """The game's own folder on the card, from the answer's members (``BASLUS-…/icon.sys``).

    A PS2 answer names the card folder as its directory and every member below it, so the
    first path segment is the folder this game's saves live in. ``None`` when the game has
    never saved here — the download then has to name its own folder, which only a one-game
    card can do.
    """
    for component in getattr(answer, "synced_files", ()) or ():
        name = str(getattr(component, "name", component))
        if "/" in name:
            return name.split("/", 1)[0]
    return None


def _extension(server_save: dict[str, Any]) -> str:
    """A server save's extension, from the row's own field before its name."""
    declared = server_save.get("file_extension")
    if isinstance(declared, str) and declared:
        return declared.lstrip(".").lower()
    name = str(server_save.get("file_name") or "")
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""
