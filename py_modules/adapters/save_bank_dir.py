"""Where the plugin's own save bank puts one platform, when the bank is switched on.

There is one switch — ``save_bank`` in ``settings.json`` — and it has to move two things
together: the launch, which redirects RetroArch's saves into the bank through a
generated appendconfig, and the lookup, which reads the directory a sync carries files
from. Split them and every save lands in a directory nothing reads, which looks exactly
like a sync bug: the game shows no saves, or a stale one from the server.

So this adapter answers ``None`` unless the switch is on. A ``None`` makes the caller
keep the path it always used, which is the whole point: with the switch off, the plugin
is byte-for-byte what it was, and with it on, both halves address the same directory.

Two families of redirect are answered. The launch the plugin writes itself (a RetroArch
appendconfig) covers the libretro family, and a save link covers the emulators
``domain.emulator_save_link`` points at the bank — Azahar's 3DS title tree is the second
one. Everything else is ``None``: a standalone emulator nobody has pointed writes where
*it* decides, and naming the bank for it would promise a redirect nobody performs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.emulator_save_link import linked_save_families
from domain.save_bank import LAUNCH_REDIRECTED_FAMILIES, layout_for, save_bank_base, save_bank_root

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable


class SaveBankDirAdapter:
    """The bank directory for one platform, or ``None`` when the bank is not in use."""

    def __init__(
        self,
        *,
        data_dir: str,
        logger: logging.Logger,
        enabled: Callable[[], object] | None = None,
    ) -> None:
        self._data_dir = data_dir
        self._logger = logger
        self._enabled = enabled

    def __call__(self, platform: str) -> str | None:
        """``<data>/saves/<platform>`` for a libretro platform with the bank on, else ``None``.

        The switch is read per call rather than captured at construction: it is a user
        setting, and toggling it has to take effect on the next launch rather than at
        the next plugin restart.
        """
        if self._enabled is not None and not self._enabled():
            return None
        layout = layout_for(platform)
        # A libretro family the plugin's own appendconfig redirects, or a family a save
        # link points at the bank. The caller still decides which of the two applies to
        # the launch it is answering for (``services/saves/rom_info``); this only says
        # the directory is somebody's real save root.
        if layout.family not in LAUNCH_REDIRECTED_FAMILIES and layout.family not in linked_save_families():
            return None
        return save_bank_base(save_bank_root(self._data_dir), platform)
