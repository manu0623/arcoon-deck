"""Saying how a session's emulator exited, when it did not exit cleanly.

A session ends when Steam stops reporting the game as running — which is the same
event whether the player quit or the emulator died mid-frame. Nothing in that signal
carries an exit status, so this service asks the one source that does: the core dumps
the kernel recorded since the session began.

The answer is deliberately three-valued:

- a dump matching this ROM's baked launch command → the emulator crashed, and the
  payload names the executable, the signal and the pid;
- no dump at all → the session ended without a signal death (or cores are off, which
  this cannot distinguish and does not claim to);
- **``None``** → the question could not be put: no session marker to date the window
  from, no baked command to name the emulator, or ``coredumpctl`` unavailable. "Could
  not ask" is reported as nothing rather than as a clean exit.

It runs at the *start* of the end-of-session round-trip, before the playtime recorder
clears the session marker the window is dated from.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from domain.emulator_crash import crash_payload, crashed_emulator, emulator_name_tokens

if TYPE_CHECKING:
    import asyncio
    import logging
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from services.protocols.infra import CoredumpReader


@dataclass(frozen=True)
class CrashDetectionServiceConfig:
    """The three things this needs: the ROM's own rows, the dumps, and the loop."""

    uow_factory: Callable[[], AbstractContextManager[Any]]
    coredumps: CoredumpReader
    loop: asyncio.AbstractEventLoop
    logger: logging.Logger


class CrashDetectionService:
    """Detects whether a session's emulator left a core dump behind."""

    def __init__(self, *, config: CrashDetectionServiceConfig) -> None:
        self._uow_factory = config.uow_factory
        self._coredumps = config.coredumps
        self._loop = config.loop
        self._logger = config.logger

    async def detect_session_crash(self, rom_id: int) -> dict[str, Any] | None:
        """The crash this session's emulator left, or ``None``.

        The work is one short read Unit of Work plus a bounded local command, so it
        runs in the executor: the SQLite connection has thread affinity and
        ``coredumpctl`` blocks while it reads the journal.
        """
        return await self._loop.run_in_executor(None, self._detect_io, int(rom_id))

    def _detect_io(self, rom_id: int) -> dict[str, Any] | None:
        """Synchronous twin of :meth:`detect_session_crash`."""
        rid = int(rom_id)
        try:
            with self._uow_factory() as uow:
                session = uow.playtime.get(rid)
                rom = uow.roms.get(rid)
                started_at = session.last_session_start if session is not None else None
                launch_options = rom.applied_launch_options if rom is not None else None
        except Exception as exc:  # a read failure is "could not ask", not a clean exit
            self._logger.warning(f"crash_detection: rom {rid} session rows unreadable: {exc!r}")
            return None

        if not started_at or not launch_options:
            return None
        try:
            started_epoch = datetime.fromisoformat(started_at).timestamp()
        except ValueError:
            self._logger.debug(f"crash_detection: rom {rid} session start {started_at!r} is not a timestamp")
            return None

        dumps = self._coredumps.read_since(int(started_epoch * 1_000_000))
        if dumps is None:
            return None
        tokens = emulator_name_tokens(launch_options)
        if not tokens:
            return None
        dump = crashed_emulator(dumps, tokens)
        if dump is None:
            self._logger.debug(
                f"crash_detection: rom {rid} ended with no dump for {', '.join(tokens)} ({len(dumps)} dumps seen)"
            )
            return None

        self._logger.warning(
            f"[session] rom {rid}: the emulator crashed ({dump.signal_name}, exe={dump.exe}, pid={dump.pid}) "
            f"— the session did not end cleanly"
        )
        return crash_payload(dump)
