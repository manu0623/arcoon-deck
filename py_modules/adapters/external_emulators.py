"""Cached, platform-scoped view of the emulators this machine actually has installed.

:mod:`adapters.emulator_scan` is the probe: it walks ``~/Applications``, EmuDeck's
launchers and the flatpak list, and it is deliberately uncached and thorough, because
a one-off inventory is allowed to cost a subprocess. The picker is the opposite
consumer — it is asked every time a menu opens, once per ROM — so it is handed this
adapter instead, which scans once per TTL and answers ``for_platform`` from the
result.

**The cache is time-based, not event-based, and short.** Installing an emulator on a
Deck means leaving the plugin, and the plugin process is torn down for the game to
launch, so a stale answer lives minutes at most; a TTL keeps a menu that is reopened
three times in a row from spawning three ``flatpak list`` calls. ``reset_cache``
exists for the caller that knows something changed.

**A scan can never fail the picker.** The probe already returns an empty result with
notes when a directory is unreadable, so a machine with no ``~/Applications``
produces no rows rather than an exception; the notes are logged once per scan so a
missing list is explainable.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from adapters.emulator_scan import ScanResult, scan_home
from domain.emulator_picker import external_options

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.emulator_commands import EmulatorOption
    from domain.emulator_registry import InstalledEmulator

DEFAULT_TTL_SECONDS = 60.0


class ExternalEmulatorsAdapter:
    """The installed-emulator inventory behind the picker, cached for ``ttl`` seconds."""

    def __init__(
        self,
        *,
        user_home: str,
        logger: logging.Logger,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        scan: Callable[[str], ScanResult] | None = None,
    ) -> None:
        self._user_home = user_home
        self._logger = logger
        self._ttl = ttl_seconds
        self._clock = clock
        self._scan = scan if scan is not None else scan_home
        self._installs: list[InstalledEmulator] | None = None
        self._expires_at = 0.0

    def reset_cache(self) -> None:
        """Discard the cached inventory so the next call rescans."""
        self._installs = None

    def installs(self) -> list[InstalledEmulator]:
        """Every emulator found on this machine, rescanning when the TTL has passed."""
        now = self._clock()
        if self._installs is not None and now < self._expires_at:
            return self._installs
        result = self._scan(self._user_home)
        installs = list(result.installs)
        for note in result.notes:
            self._logger.info(f"Emulator scan: {note}")
        self._installs = installs
        self._expires_at = now + self._ttl
        return installs

    def for_platform(self, platform: str) -> list[InstalledEmulator]:
        """The installs that can play *platform*, in the scanner's stable order."""
        return [install for install in self.installs() if install.plays(platform)]

    def options_for_platform(self, platform: str) -> list[EmulatorOption]:
        """Picker rows for *platform*, ready to append to a catalogue's list."""
        return external_options(self.for_platform(platform), platform)
