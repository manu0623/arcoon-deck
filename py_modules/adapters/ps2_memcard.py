"""A PS2 folder memory card the bank owns, and the core's view of the same card.

PCSX2 has two card shapes, and only one of them can be synced per game. A *file* card
is a single 8 MB image holding every game's saves; a *folder* card is a directory
ending ``.ps2`` that holds ``_pcsx2_superblock`` and one subfolder per game, named
after the disc's serial (``SCUS-97198``). Measured on the reference Deck: a libretro
PS2 launch wrote ``Mcd001.ps2`` — 8,650,752 bytes, one shared card — so uploading it as
"Sly Cooper's save" would have shipped whatever else the card held.

So the bank's ps2 directory holds a folder card, and both launch shapes read it:

- a standalone PCSX2 reads ``config/PCSX2/memcards`` (its ``SavePoint``), which the
  save link points at the bank;
- the libretro core reads ``<retroarch>/system/pcsx2/memcards`` and **ignores**
  ``savefile_directory`` for memory cards — measured, the redirected launch still wrote
  into the emulator's system tree — so that folder is replaced with a symlink to the
  bank.

**A file card is converted, and the image is kept.** PCSX2 can convert a file card to a
folder card, but only from its own Memory Card window; there is no command-line form
(the Qt binary only starts when asked, measured on the reference Deck). A card that is
never converted is a card whose saves can never sync, so the plugin does the same job
itself: it reads every save folder out of the image with
:func:`domain.ps2_file_card.read_file_card` and writes those files under
``Mcd001.ps2/``. The image itself is moved aside, never overwritten — if the extraction
is refused (an image that does not parse) the card stays exactly where it was and the
status says why.
"""

from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

from domain.ps2_file_card import Ps2CardError, Ps2CardFile, Ps2CardFolder, read_file_card
from domain.save_bank import PS2_SUPERBLOCK_FILE, ps2_card_superblock

if TYPE_CHECKING:
    import logging

#: Slot 1's card file name, and the name a folder card keeps: PCSX2's
#: ``[MemoryCards] Slot1_Filename`` on the reference Deck.
FOLDER_CARD_NAME = "Mcd001.ps2"


class Ps2MemcardAdapter:
    """Keeps a folder card in the bank and the core's card folder pointed at it."""

    def __init__(self, *, logger: logging.Logger) -> None:
        self._logger = logger

    def ensure(self, bank_dir: str, retroarch_config_dir: str | None) -> dict[str, str]:
        """Make the bank's ps2 directory hold a usable card, and point the core at it."""
        status: dict[str, str] = {}
        status["card"] = self.ensure_folder_card(bank_dir)
        if retroarch_config_dir is None:
            status["core_link"] = "no_retroarch"
        else:
            status["core_link"] = self.ensure_core_card_link(retroarch_config_dir, bank_dir)
        return status

    def ensure_folder_card(self, bank_dir: str) -> str:
        """A folder card at ``<bank>/Mcd001.ps2``, or a stated reason there is not one.

        ``created`` — the card directory and its superblock were written;
        ``present`` — a folder card is already there and left untouched;
        ``converted`` — a file card's saves were extracted into a folder card and the
        image was kept beside it;
        ``file_card`` — a file card is there and could not be read, so it was left alone;
        ``failed`` — the directory could not be written (logged).
        """
        card = os.path.join(bank_dir, FOLDER_CARD_NAME)
        try:
            if os.path.isdir(card):
                self._ensure_superblock(card)
                return "present"
            if os.path.isfile(card):
                return self._convert(card, bank_dir)
            os.makedirs(card, exist_ok=True)
            self._ensure_superblock(card)
        except OSError as exc:
            self._logger.warning(f"ps2 memcard: cannot prepare {card}: {exc}")
            return "failed"
        self._logger.info(f"ps2 memcard: created the folder card {card}")
        return "created"

    def _convert(self, card: str, bank_dir: str) -> str:
        """Extract a file card's saves into a folder card, keeping the image.

        The image is moved aside only after every file of every folder has been written,
        so a conversion that fails halfway leaves the card that PCSX2 reads untouched.
        """
        staged = f"{card}.converting"
        try:
            with open(card, "rb") as handle:
                image = handle.read()
            folders = read_file_card(image)
        except (OSError, Ps2CardError) as exc:
            self._logger.warning(
                f"ps2 memcard: {card} is a file card that could not be read ({exc}); leaving it as it is"
            )
            return "file_card"
        try:
            os.makedirs(staged, exist_ok=True)
            written = 0
            for folder in folders:
                written += self._write_folder(image, os.path.join(staged, folder.name), folder)
            self._ensure_superblock(staged)
            if written == 0:
                raise OSError("the card holds no save folder")
            kept = self._keep_image(card, bank_dir)
            os.replace(staged, card)
        except OSError as exc:
            self._logger.warning(f"ps2 memcard: cannot convert {card}: {exc}")
            self._discard(staged)
            return "file_card"
        self._logger.info(
            f"ps2 memcard: converted the file card {card} into a folder card "
            f"({len(folders)} save folder(s), {written} file(s)); the image is kept at {kept}"
        )
        return "converted"

    def _write_folder(self, image: bytes, target: str, folder: Ps2CardFolder) -> int:
        """Write one save folder's files; answer how many were written."""
        os.makedirs(target, exist_ok=True)
        written = 0
        for item in folder.files:
            self._write_file(image, os.path.join(target, item.name), item)
            written += 1
        for child in folder.folders:
            written += self._write_folder(image, os.path.join(target, child.name), child)
        return written

    @staticmethod
    def _write_file(image: bytes, path: str, item: Ps2CardFile) -> None:
        with open(path, "wb") as handle:
            for offset, length in item.spans:
                handle.write(image[offset:offset + length])

    @staticmethod
    def _keep_image(card: str, bank_dir: str) -> str:
        """Move the file card beside the folder card, never deleting it."""
        kept = os.path.join(bank_dir, f"{FOLDER_CARD_NAME}.file-card-image")
        suffix = 1
        while os.path.exists(kept):
            suffix += 1
            kept = os.path.join(bank_dir, f"{FOLDER_CARD_NAME}.file-card-image.{suffix}")
        os.replace(card, kept)
        return kept

    @staticmethod
    def _discard(path: str) -> None:
        shutil.rmtree(path, ignore_errors=True)

    def ensure_core_card_link(self, retroarch_config_dir: str, bank_dir: str) -> str:
        """Point ``<retroarch>/system/pcsx2/memcards`` at *bank_dir*.

        ``already_linked`` — it already names the bank; ``linked`` — it was made to;
        ``adopted`` — a real folder's cards were moved into the bank first;
        ``failed`` — the filesystem refused (logged).
        """
        link = os.path.join(retroarch_config_dir, "system", "pcsx2", "memcards")
        try:
            if os.path.islink(link):
                if os.path.realpath(link) == os.path.realpath(bank_dir):
                    return "already_linked"
                os.unlink(link)
            outcome = "linked"
            if os.path.isdir(link):
                outcome = "adopted" if self._adopt_cards(link, bank_dir) else "linked"
                # A card the bank already held is deliberately left in both places; the
                # emulator's copy stays beside the link rather than being thrown away.
                leftovers = os.listdir(link)
                if leftovers:
                    kept = f"{link}.old"
                    os.replace(link, kept)
                    self._logger.warning(f"ps2 memcard: {len(leftovers)} card(s) also in the bank kept at {kept}")
                else:
                    os.rmdir(link)
            os.makedirs(os.path.dirname(link), exist_ok=True)
            os.symlink(bank_dir, link, target_is_directory=True)
        except OSError as exc:
            self._logger.warning(f"ps2 memcard: cannot link {link} at the bank: {exc}")
            return "failed"
        self._logger.info(f"ps2 memcard: core card folder {link} -> {bank_dir}")
        return outcome

    def _adopt_cards(self, emulator_dir: str, bank_dir: str) -> bool:
        """Move cards the emulator already wrote into the bank; say whether any moved."""
        moved = False
        for name in sorted(os.listdir(emulator_dir)):
            if not name.endswith(".ps2"):
                continue
            target = os.path.join(bank_dir, name)
            if os.path.exists(target):
                self._logger.warning(f"ps2 memcard: {name} exists in both the emulator and the bank; keeping both")
                continue
            os.replace(os.path.join(emulator_dir, name), target)
            moved = True
        return moved

    @staticmethod
    def _ensure_superblock(card_dir: str) -> None:
        """Write the formatted superblock a folder card needs to be read as one."""
        superblock = os.path.join(card_dir, PS2_SUPERBLOCK_FILE)
        if os.path.exists(superblock):
            return
        with open(superblock, "wb") as handle:
            handle.write(ps2_card_superblock())
