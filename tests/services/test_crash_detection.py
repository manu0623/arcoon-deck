"""Tests for services/crash_detection — how a session's emulator exited.

The three-valued answer is the point: a matching dump is a crash, no dump is no crash,
and an unaskable question (no session marker, no baked command, no journal) is reported
as nothing at all rather than as a clean exit.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from domain.emulator_crash import Coredump
from services.crash_detection import CrashDetectionService, CrashDetectionServiceConfig

_LOGGER = logging.getLogger("test_crash_detection")

PCSX2_LAUNCH = 'flatpak run net.pcsx2.PCSX2 -fullscreen -batch -- "/roms/ps2/Sly Cooper (USA).iso"'
_SESSION_START = "2026-11-13T16:03:45"


class _Session:
    def __init__(self, started_at: str | None) -> None:
        self.last_session_start = started_at


class _Rom:
    def __init__(self, launch_options: str | None) -> None:
        self.applied_launch_options = launch_options


class _Table:
    def __init__(self, row: Any) -> None:
        self._row = row

    def get(self, rom_id: int) -> Any:
        return self._row


class _Uow:
    def __init__(self, *, session: _Session | None, rom: _Rom | None) -> None:
        self.playtime = _Table(session)
        self.roms = _Table(rom)


def _service(
    *,
    session: _Session | None,
    rom: _Rom | None,
    dumps: tuple[Coredump, ...] | None,
    uow_error: Exception | None = None,
) -> tuple[Any, list[int]]:
    """A builder for the service (the loop only exists inside the test's coroutine)."""
    calls: list[int] = []

    class _Reader:
        def read_since(self, since_us: int) -> tuple[Coredump, ...] | None:
            calls.append(since_us)
            return dumps

    @contextmanager
    def _uow_factory():
        if uow_error is not None:
            raise uow_error
        yield _Uow(session=session, rom=rom)

    def build(loop: asyncio.AbstractEventLoop) -> CrashDetectionService:
        return CrashDetectionService(
            config=CrashDetectionServiceConfig(
                uow_factory=_uow_factory,
                coredumps=_Reader(),
                loop=loop,
                logger=_LOGGER,
            ),
        )

    return build, calls


def _run(build: Any, rom_id: int = 7) -> dict[str, Any] | None:
    async def main() -> dict[str, Any] | None:
        return await build(asyncio.get_running_loop()).detect_session_crash(rom_id)

    return asyncio.run(main())


class TestDetectSessionCrash:
    def test_a_matching_dump_is_reported_with_what_died(self):
        build, calls = _service(
            session=_Session(_SESSION_START),
            rom=_Rom(PCSX2_LAUNCH),
            dumps=(Coredump(timestamp_us=1794604364085378, pid=273611, signal=6, exe="/app/bin/pcsx2-qt"),),
        )

        payload = _run(build)

        assert payload is not None
        assert payload["signal_name"] == "SIGABRT"
        assert payload["exe"] == "/app/bin/pcsx2-qt"
        # The window starts at the session marker, in microseconds.
        assert calls == [int(datetime.fromisoformat(_SESSION_START).timestamp() * 1_000_000)]

    def test_an_unreadable_journal_reports_nothing(self):
        build, _ = _service(session=_Session(_SESSION_START), rom=_Rom(PCSX2_LAUNCH), dumps=None)
        assert _run(build) is None

    def test_no_dumps_is_no_crash(self):
        build, calls = _service(session=_Session(_SESSION_START), rom=_Rom(PCSX2_LAUNCH), dumps=())
        assert _run(build) is None
        assert len(calls) == 1

    def test_no_session_marker_never_asks_the_journal(self):
        build, calls = _service(
            session=_Session(None),
            rom=_Rom(PCSX2_LAUNCH),
            dumps=(Coredump(timestamp_us=1, pid=2, signal=6, exe="/app/bin/pcsx2-qt"),),
        )
        assert _run(build) is None
        assert calls == []

    def test_a_rom_with_no_baked_command_never_asks_the_journal(self):
        build, calls = _service(session=_Session(_SESSION_START), rom=_Rom(None), dumps=())
        assert _run(build) is None
        assert calls == []

    def test_another_emulators_dump_is_not_this_roms_crash(self):
        build, _ = _service(
            session=_Session(_SESSION_START),
            rom=_Rom('%EMULATOR_PPSSPP% --fullscreen "/roms/psp/game.iso"'),
            dumps=(Coredump(timestamp_us=1, pid=2, signal=6, exe="/app/bin/pcsx2-qt"),),
        )
        assert _run(build) is None

    def test_a_row_read_failure_is_not_a_crash(self):
        build, calls = _service(
            session=_Session(_SESSION_START),
            rom=_Rom(PCSX2_LAUNCH),
            dumps=(Coredump(timestamp_us=1, pid=2, signal=6, exe="/app/bin/pcsx2-qt"),),
            uow_error=RuntimeError("db locked"),
        )
        assert _run(build) is None
        assert calls == []


class _Playtime:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[int] = []

    async def record_session_end(self, rom_id: int) -> dict[str, Any]:
        self.calls.append(rom_id)
        return self.payload


class _PostExitSync:
    async def post_exit_sync(self, rom_id: int) -> dict[str, Any]:
        return {"offline": False, "success": True, "synced": 0, "uploaded": 0, "downloaded": 0, "conflicts": []}


class _AchievementSync:
    async def sync_achievements_after_session(self, rom_id: int) -> None:
        return None


class _MigrationReader:
    def is_retrodeck_migration_pending(self) -> bool:
        return False

    async def refresh_state(self) -> dict[str, Any]:
        return {}


class TestLifecycleIntegration:
    def test_finalize_carries_the_crash_and_still_runs_the_other_steps(self):
        from services.session_lifecycle import SessionLifecycleService, SessionLifecycleServiceConfig

        probe_calls: list[int] = []

        class _Probe:
            async def detect_session_crash(self, rom_id: int) -> dict[str, Any] | None:
                probe_calls.append(rom_id)
                return {"exe": "/app/bin/pcsx2-qt", "pid": 1, "signal": 6, "signal_name": "SIGABRT"}

        playtime = _Playtime(payload={"success": True, "total_seconds": 60})
        service = SessionLifecycleService(
            config=SessionLifecycleServiceConfig(
                playtime_recorder=playtime,
                post_exit_sync=_PostExitSync(),
                achievement_sync=_AchievementSync(),
                migration_reader=_MigrationReader(),
                logger=_LOGGER,
                crash_probe=_Probe(),
            ),
        )

        async def main() -> Any:
            result = await service.finalize(99)
            tasks = list(service._background_tasks)
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            return result

        result = asyncio.run(main())

        assert probe_calls == [99]
        assert result.crash is not None
        assert result.crash["signal_name"] == "SIGABRT"
        assert result.total_seconds == 60
        assert playtime.calls == [99]

    def test_a_failing_probe_does_not_stop_the_finalize(self):
        from services.session_lifecycle import SessionLifecycleService, SessionLifecycleServiceConfig

        class _Probe:
            async def detect_session_crash(self, rom_id: int) -> dict[str, Any] | None:
                raise RuntimeError("coredumpctl missing")

        playtime = _Playtime(payload={"success": True, "total_seconds": 60})
        service = SessionLifecycleService(
            config=SessionLifecycleServiceConfig(
                playtime_recorder=playtime,
                post_exit_sync=_PostExitSync(),
                achievement_sync=_AchievementSync(),
                migration_reader=_MigrationReader(),
                logger=_LOGGER,
                crash_probe=_Probe(),
            ),
        )

        result = asyncio.run(service.finalize(99))

        assert result.crash is None
        assert result.total_seconds == 60
        assert playtime.calls == [99]
