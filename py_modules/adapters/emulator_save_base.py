"""The directory a standalone emulator keeps a platform's saves under.

The catalogue cannot answer this on a device with no ES-DE, and guessing would be
worse than refusing: a synced save that lands where the emulator does not read is a
save nobody sees again. So each family is served only where its own statements can be
read, and everything else answers ``None`` — the caller then falls back to the
catalogue and says nothing it cannot support.

**The yuzu lineage is served from its own config.** Eden, Citron, Sudachi and yuzu all
write ``nand_directory`` into ``qt-config.ini``, and the device this was built on states
``nand_directory=/home/deck/Emulation/storage/yuzu/nand`` — so the saves live under
``<nand>/user/save/<profile>/<title id>``, the same shape ``domain.save_bank``'s switch
family describes. Reading the emulator's own value rather than assuming ``~/.local/share``
is what makes this work for an AppImage, a flatpak and a native install alike.

**Everything else answers ``None``.** PCSX2's memory-card directory is read by
``domain.save_locations`` but its card files are shared and card-named, not per game;
PPSSPP, Cemu and RPCS3 name saves by their own identities. Each needs its own key read
and its own naming rule before it can be stated, and none of that is guessed here.
"""

from __future__ import annotations

import os
import posixpath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

# The yuzu lineage, in probe order. Every one of them keeps ``qt-config.ini`` under its
# own app directory and states ``nand_directory`` there; the id is the definition id in
# ``domain.emulator_config``, not a family name.
_YUZU_LINEAGE: tuple[str, ...] = ("eden", "citron", "sudachi", "yuzu")

# The key each of them states its nand root under. One spelling for all four — they
# share the settings format, which is why they share this reader.
_NAND_KEY = "nand_directory"

# Each lineage member's XDG app directory and settings file. The yuzu forks share both.
_APP_DIRS: dict[str, str] = {"eden": "eden", "citron": "citron", "sudachi": "sudachi", "yuzu": "yuzu"}
_CONFIG_FILENAME = "qt-config.ini"


class EmulatorSaveBaseAdapter:
    """Resolves the platform's save base from the installed emulator's own settings."""

    def __init__(
        self,
        *,
        user_home: str,
        logger: logging.Logger,
        read_text: Callable[[str], str] | None = None,
        exists: Callable[[str], bool] | None = None,
    ) -> None:
        self._user_home = user_home
        self._logger = logger
        self._read_text = read_text or _read_text
        self._exists = exists or os.path.isfile

    def __call__(self, platform_slug: str) -> str | None:
        """The base directory for *platform_slug*'s standalone saves, or ``None``.

        ``None`` is the answer for every platform this adapter cannot state a location
        for. It is not an error: the caller has its own fallback and this seam must not
        invent a path to look more useful.
        """
        if platform_slug != "switch":
            return None
        for emulator_id in _YUZU_LINEAGE:
            nand = self._nand_directory(emulator_id)
            if nand:
                # Saves sit one level in from the nand root; ``domain.save_bank``'s switch
                # family then discovers the profile and names the title from its id.
                return posixpath.join(nand, "user")
        return None

    def _nand_directory(self, emulator_id: str) -> str | None:
        app_dir = _APP_DIRS.get(emulator_id)
        if app_dir is None:
            return None
        for path in self._candidate_paths(app_dir, _CONFIG_FILENAME):
            if not self._exists(path):
                continue
            try:
                text = self._read_text(path)
            except OSError as error:
                self._logger.debug(f"save base: {emulator_id} settings unreadable ({error})")
                continue
            # A QSettings file writes its top-level keys BEFORE its first ``[Section]``, and
            # the reference Deck's ``qt-config.ini`` has no section header at all — so the
            # key is read off the raw text rather than through an INI parser that would
            # reject the file. The read is deliberately local: importing
            # ``domain.emulator_config`` pulls in ``xml.etree``, which Decky Loader's
            # sandboxed interpreter does not ship, and a settings reader is not worth
            # failing the whole plugin to load.
            nand = (_value(text, _NAND_KEY) or "").strip()
            if nand:
                self._logger.debug(f"save base: {emulator_id} states nand={nand} ({path})")
                return nand
        return None

    def _candidate_paths(self, app_dir: str, filename: str) -> tuple[str, ...]:
        """Every place this emulator's settings can be, portable-less and sandboxed.

        Both XDG roots are named because the lineage disagrees about which one holds the
        settings — Eden keeps them in ``~/.config/eden`` while a flatpak keeps them inside
        its own ``~/.var/app/<id>/config``.
        """
        return (
            posixpath.join(self._user_home, ".config", app_dir, filename),
            posixpath.join(self._user_home, ".local", "share", app_dir, filename),
        )


def _value(text: str, key: str) -> str | None:
    """The first ``key=value`` line's value, or ``None``.

    Matched exactly, so ``nand_directory\\default=false`` next to ``nand_directory=…``
    cannot answer for it. Quotes are stripped because QSettings writes strings unquoted but
    a hand-edited file may not.
    """
    for line in text.splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == key:
            return value.strip().strip('"')
    return None


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()
