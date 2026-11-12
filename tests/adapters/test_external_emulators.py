"""The cached external inventory: one scan per TTL, platform-scoped answers.

The cache exists because the picker is asked on every menu open while the probe
behind it spawns ``flatpak list``; the tests pin the TTL boundary, the explicit
reset, and that a scan's notes reach the log rather than disappearing.
"""

from __future__ import annotations

import logging

from adapters.emulator_scan import ScanResult
from adapters.external_emulators import ExternalEmulatorsAdapter
from domain.emulator_registry import InstalledEmulator, definition

HOME = "/home/deck"


def _install(emulator_id: str, provider: str, path: str) -> InstalledEmulator:
    found = definition(emulator_id)
    assert found is not None
    return InstalledEmulator(definition=found, provider=provider, path=path)


EDEN = _install("eden", "native", f"{HOME}/Applications/Eden.appimage")
DUCKSTATION = _install("duckstation", "native", f"{HOME}/Applications/DuckStation.AppImage")


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class FakeScan:
    def __init__(self, result: ScanResult) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, user_home: str) -> ScanResult:
        self.calls += 1
        return self.result


def _scanner(installs: list[InstalledEmulator], notes: tuple[str, ...] = ()) -> FakeScan:
    return FakeScan(ScanResult(installs=installs, unrecognised=[], retrodeck_present=True, notes=list(notes)))


def _adapter(scan: FakeScan, clock: FakeClock | None = None, ttl: float = 60.0) -> ExternalEmulatorsAdapter:
    return ExternalEmulatorsAdapter(
        user_home=HOME,
        logger=logging.getLogger("test"),
        ttl_seconds=ttl,
        clock=clock or FakeClock(),
        scan=scan,
    )


class TestCaching:
    def test_one_scan_serves_repeated_questions(self) -> None:
        scan = _scanner([EDEN])
        adapter = _adapter(scan)
        adapter.for_platform("switch")
        adapter.for_platform("switch")
        adapter.installs()
        assert scan.calls == 1

    def test_the_ttl_boundary_rescans(self) -> None:
        clock = FakeClock()
        scan = _scanner([EDEN])
        adapter = _adapter(scan, clock=clock, ttl=60.0)
        adapter.installs()
        clock.now += 59.0
        adapter.installs()
        assert scan.calls == 1
        clock.now += 2.0
        adapter.installs()
        assert scan.calls == 2

    def test_reset_forces_the_next_call_to_rescan(self) -> None:
        scan = _scanner([EDEN])
        adapter = _adapter(scan)
        adapter.installs()
        adapter.reset_cache()
        adapter.installs()
        assert scan.calls == 2


class TestPlatformScope:
    def test_only_installs_that_play_the_platform(self) -> None:
        adapter = _adapter(_scanner([EDEN, DUCKSTATION]))
        assert [install.id for install in adapter.for_platform("switch")] == ["eden"]
        assert [install.id for install in adapter.for_platform("psx")] == ["duckstation"]

    def test_options_are_provider_qualified_and_not_bakeable(self) -> None:
        adapter = _adapter(_scanner([EDEN]))
        rows = adapter.options_for_platform("switch")
        assert [row.label for row in rows] == ["Eden (AppImage)"]
        assert rows[0].status == "needs_setup"

    def test_a_machine_with_nothing_installed_answers_empty(self) -> None:
        adapter = _adapter(_scanner([]))
        assert adapter.for_platform("switch") == []
        assert adapter.options_for_platform("switch") == []


class TestDiagnostics:
    def test_scan_notes_are_logged(self, caplog) -> None:
        adapter = _adapter(_scanner([], notes=("flatpak list failed: PermissionError",)))
        with caplog.at_level(logging.INFO):
            adapter.installs()
        assert "flatpak list failed" in caplog.text
