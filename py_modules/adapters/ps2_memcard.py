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

**A file card already in place is left alone.** Converting it is PCSX2's own job (its
Memory Card manager does it), and overwriting it would throw away the saves it holds —
the exact loss this adapter exists to avoid. The status says which of the two it found
so a caller can report it rather than guess.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

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
        ``file_card`` — a file card occupies the name; it is not converted or replaced;
        ``failed`` — the directory could not be written (logged).
        """
        card = os.path.join(bank_dir, FOLDER_CARD_NAME)
        try:
            if os.path.isdir(card):
                self._ensure_superblock(card)
                return "present"
            if os.path.isfile(card):
                self._logger.info(
                    f"ps2 memcard: {card} is a file card; leaving it for PCSX2 to convert before syncing"
                )
                return "file_card"
            os.makedirs(card, exist_ok=True)
            self._ensure_superblock(card)
        except OSError as exc:
            self._logger.warning(f"ps2 memcard: cannot prepare {card}: {exc}")
            return "failed"
        self._logger.info(f"ps2 memcard: created the folder card {card}")
        return "created"

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
