"""Where the plugin's own save bank puts one platform, when the bank is switched on.

There is one switch — ``save_bank`` in ``settings.json`` — and it has to move two things
together: the launch, which redirects RetroArch's saves into the bank through a
generated appendconfig, and the lookup, which reads the directory a sync carries files
from. Split them and every save lands in a directory nothing reads, which looks exactly
like a sync bug: the game shows no saves, or a stale one from the server.

So this adapter answers ``None`` unless the switch is on. A ``None`` makes the caller
keep the path it always used, which is the whole point: with the switch off, the plugin
is byte-for-byte what it was, and with it on, both halves address the same directory.

Only the libretro family is answered here. A standalone emulator (GameCube's GCI folder,
a PS2 card, a 3DS title tree) writes where *it* decides, and the bank's family for those
platforms describes a shape the emulator has not been pointed at yet — naming that
directory as the place to read would promise a redirect nobody performs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.save_bank import SaveFamily, layout_for, save_bank_base, save_bank_root

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable


#: The families a libretro launch can redirect into the bank. A plain per-ROM file and
#: PSP's folder set are both written where the appendconfig says, so both have a bank
#: directory to read. A standalone emulator's families (a PS2 card, a Dolphin card
#: folder, a 3DS title tree) stay out: the bank describes a shape nothing has pointed
#: that emulator at yet, and naming the directory would promise a redirect nobody makes.
_REDIRECTED_FAMILIES = frozenset({SaveFamily.LIBRETRO_FILE, SaveFamily.PREFIX_BUNDLE})


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
        if layout.family not in _REDIRECTED_FAMILIES:
            return None
        return save_bank_base(save_bank_root(self._data_dir), platform)
