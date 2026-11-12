"""Tests for ActiveCoreResolver — the single per-ROM active-core read seam.

Covers the three-layer precedence: a resolvable per-game override wins; a
per-platform ``settings.json`` core beats the live es_systems default; the
per-game override beats the per-platform core; a NULL override with no
per-platform core delegates to the es_systems default; a stale per-game or
per-platform label degrades to the next layer without raising or emitting a
bogus ``-e`` override; a per-game/per-platform label may name a **standalone**
emulator; and the retired ES-DE gamelist is never consulted.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fakes.fake_core_info_provider import (
    FakeCoreInfoProvider,
    FakeSandboxLauncher,
    libretro_option,
    standalone_option,
)
from fakes.fake_unit_of_work import FakeUnitOfWork, FakeUnitOfWorkFactory

from domain.layout_manifest import ManagedPlatform
from domain.retroarch_runner import RetroArchRunner
from domain.rom import Rom
from domain.rom_install import RomInstall
from domain.shortcut_data import EmulatorInvocation, resolve_emulator_invocation
from services.active_core_resolver import ActiveCoreResolver, ActiveCoreResolverConfig

if TYPE_CHECKING:
    import pytest


class FakeSystemResolver:
    """In-memory ``SystemResolver`` mapping platform slugs to RetroDECK systems.

    Records each call so a test can assert the resolver normalized the ROM's
    platform slug before reaching the core read seams. Unknown slugs pass
    through unchanged, mirroring the real resolver.
    """

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping if mapping is not None else {}
        self.calls: list[tuple[str, str | None]] = []

    def __call__(self, platform_slug: str, platform_fs_slug: str | None = None) -> str:
        self.calls.append((platform_slug, platform_fs_slug))
        return self.mapping.get(platform_slug, platform_slug)


class FakePlatformCoreReader:
    """In-memory ``PlatformCoreReader`` mapping platform slugs to core labels.

    Returns the configured label for a slug, or ``None`` when absent. Records
    each queried slug so a test can assert the per-platform layer was consulted
    (or skipped when a per-game override already resolved).
    """

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping if mapping is not None else {}
        self.calls: list[str] = []

    def get_platform_core(self, platform_slug: str) -> str | None:
        self.calls.append(platform_slug)
        return self.mapping.get(platform_slug)


def _seed_rom(
    uow: FakeUnitOfWork,
    *,
    rom_id: int,
    platform_slug: str,
    emulator_override: str | None = None,
) -> None:
    """Seed one ``Rom`` (optionally pinned to ``emulator_override``) into the UoW."""
    uow.roms.save(
        Rom(
            rom_id=rom_id,
            platform_slug=platform_slug,
            name=f"rom-{rom_id}",
            fs_name=f"rom-{rom_id}.gba",
            shortcut_app_id=rom_id,
            last_synced_at="2026-01-01T00:00:00+00:00",
            emulator_override=emulator_override,
        )
    )


def _seed_install(
    uow: FakeUnitOfWork,
    *,
    rom_id: int,
    file_path: str,
    rom_dir: str | None,
    platform_slug: str = "ps3",
    system: str = "ps3",
) -> None:
    """Seed one ``RomInstall`` into the UoW (folder-backed unless *rom_dir* is None)."""
    uow.rom_installs.save(
        RomInstall.mark_installed(
            rom_id=rom_id,
            file_path=file_path,
            rom_dir=rom_dir,
            platform_slug=platform_slug,
            system=system,
            installed_at="2026-01-01T00:00:00",
        )
    )


def _make_resolver(
    *,
    uow: FakeUnitOfWork,
    core_info: FakeCoreInfoProvider,
    resolve_system: FakeSystemResolver | None = None,
    platform_core_reader: FakePlatformCoreReader | None = None,
    sandbox_launchers: dict[str, str] | None = None,
    appendconfig=None,
    launch_backend=None,
    runner=None,
    managed_layout=None,
) -> tuple[ActiveCoreResolver, FakeSystemResolver]:
    resolver_fn = resolve_system if resolve_system is not None else FakeSystemResolver()
    platform_reader = platform_core_reader if platform_core_reader is not None else FakePlatformCoreReader()
    resolver = ActiveCoreResolver(
        config=ActiveCoreResolverConfig(
            uow_factory=FakeUnitOfWorkFactory(uow=uow),
            core_info=core_info,
            sandbox_launcher=FakeSandboxLauncher(sandbox_launchers),
            platform_core_reader=platform_reader,
            resolve_system=resolver_fn,
            logger=logging.getLogger("test"),
            retroarch_appendconfig=appendconfig,
            launch_backend=launch_backend,
            retroarch_runner=runner,
            managed_layout=managed_layout,
        ),
    )
    return resolver, resolver_fn


# --- override set + resolvable → returns the override's (core_so, label) -------


def test_resolvable_override_returns_pinned_core() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=42, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(
        available_cores=[
            {"core_so": "vba_next_libretro", "label": "VBA Next", "is_default": True},
            {"core_so": "mgba_libretro", "label": "mGBA", "is_default": False},
        ],
        # System default differs from the pin so the test proves the override won.
        active_core=("vba_next_libretro", "VBA Next"),
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_core_for_rom(42) == ("mgba_libretro", "mGBA")
    # System-layer get_active_core must NOT be consulted when the override resolves.
    assert core_info.active_core_calls == []


def test_resolvable_override_normalizes_platform_slug_to_system() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=7, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
    )
    resolver, resolve_system = _make_resolver(
        uow=uow,
        core_info=core_info,
        resolve_system=FakeSystemResolver(mapping={"gba": "gba"}),
    )

    resolver.active_core_for_rom(7)
    # The available-cores read seam must receive the resolved system, not the raw slug.
    assert resolve_system.calls == [("gba", None)]
    assert core_info.emulator_options_calls == ["gba"]


# --- override NULL → returns the system-default (delegation works) -------------


def test_null_override_delegates_to_system_default() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=1, platform_slug="snes", emulator_override=None)
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "snes9x_libretro", "label": "Snes9x", "is_default": True}],
        active_core=("snes9x_libretro", "Snes9x"),
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_core_for_rom(1) == ("snes9x_libretro", "Snes9x")
    # Delegation path: the system-layer get_active_core was consulted with the system only.
    assert core_info.active_core_calls == ["snes"]


def test_null_override_passes_through_system_none() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5, platform_slug="unknown", emulator_override=None)
    core_info = FakeCoreInfoProvider(active_core=(None, None))
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    # An unconfigured system yields (None, None); that passes through unchanged.
    assert resolver.active_core_for_rom(5) == (None, None)


# --- per-platform layer beats es_systems default; per-game beats per-platform ---


def test_per_platform_core_beats_es_systems_default() -> None:
    """An un-pinned ROM whose platform carries a per-platform core gets that core,
    not the es_systems default — the layer-2 selection wins over the system layer."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=20, platform_slug="snes", emulator_override=None)
    core_info = FakeCoreInfoProvider(
        available_cores=[
            {"core_so": "snes9x_libretro", "label": "Snes9x", "is_default": True},
            {"core_so": "bsnes_libretro", "label": "bsnes", "is_default": False},
        ],
        # es_systems default is Snes9x — the per-platform core must override it.
        active_core=("snes9x_libretro", "Snes9x"),
    )
    platform_reader = FakePlatformCoreReader(mapping={"snes": "bsnes"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    assert resolver.active_core_for_rom(20) == ("bsnes_libretro", "bsnes")
    # The es_systems default layer was never consulted — the per-platform core resolved.
    assert core_info.active_core_calls == []
    assert platform_reader.calls == ["snes"]


def test_per_game_override_beats_per_platform_core() -> None:
    """A pinned ROM keeps its per-game core even when its platform has a per-platform
    selection — layer-1 (per-game) wins over layer-2 (per-platform)."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=21, platform_slug="snes", emulator_override="Snes9x")
    core_info = FakeCoreInfoProvider(
        available_cores=[
            {"core_so": "snes9x_libretro", "label": "Snes9x", "is_default": True},
            {"core_so": "bsnes_libretro", "label": "bsnes", "is_default": False},
        ],
        active_core=("bsnes_libretro", "bsnes"),
    )
    platform_reader = FakePlatformCoreReader(mapping={"snes": "bsnes"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    assert resolver.active_core_for_rom(21) == ("snes9x_libretro", "Snes9x")
    # Per-game override resolved first — the per-platform layer is never consulted.
    assert platform_reader.calls == []
    assert core_info.active_core_calls == []


# --- override set but STALE → degrades to system default (no raise, no bogus so) ---


def test_stale_override_degrades_to_system_default() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=99, platform_slug="gba", emulator_override="Removed Core")
    # The options no longer carry "Removed Core" → label_to_invocation → None.
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
        active_core=("mgba_libretro", "mGBA"),
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    result = resolver.active_core_for_rom(99)

    # Degrades to the system default — never a bogus "None.so", never raises.
    assert result == ("mgba_libretro", "mGBA")
    # The system layer was consulted (the degrade delegated past the unresolvable pin).
    assert core_info.active_core_calls == ["gba"]


def test_stale_override_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=99, platform_slug="gba", emulator_override="Removed Core")
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
        active_core=("mgba_libretro", "mGBA"),
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    with caplog.at_level(logging.WARNING, logger="test"):
        resolver.active_core_for_rom(99)

    assert any("Removed Core" in r.message and "degrading" in r.message for r in caplog.records)


# --- stale per-platform core → degrades to es_systems default (no raise) -------


def test_stale_per_platform_core_degrades_to_system_default() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=30, platform_slug="gba", emulator_override=None)
    # available_cores no longer carries the per-platform label → degrades.
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
        active_core=("mgba_libretro", "mGBA"),
    )
    platform_reader = FakePlatformCoreReader(mapping={"gba": "Removed Core"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    result = resolver.active_core_for_rom(30)

    # Degrades to the es_systems default — never a bogus "None.so", never raises.
    assert result == ("mgba_libretro", "mGBA")
    assert platform_reader.calls == ["gba"]
    assert core_info.active_core_calls == ["gba"]


def test_stale_per_platform_core_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=30, platform_slug="gba", emulator_override=None)
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
        active_core=("mgba_libretro", "mGBA"),
    )
    platform_reader = FakePlatformCoreReader(mapping={"gba": "Removed Core"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    with caplog.at_level(logging.WARNING, logger="test"):
        resolver.active_core_for_rom(30)

    assert any("Removed Core" in r.message and "per-platform" in r.message for r in caplog.records)


# --- no per-platform core → falls through to es_systems default ----------------


def test_no_per_platform_core_falls_through_to_system_default() -> None:
    """A NULL override + an empty per-platform map delegates straight to the
    es_systems default — the per-platform layer was consulted and found nothing."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=40, platform_slug="snes", emulator_override=None)
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "snes9x_libretro", "label": "Snes9x", "is_default": True}],
        active_core=("snes9x_libretro", "Snes9x"),
    )
    platform_reader = FakePlatformCoreReader()  # empty map → None for every slug
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    assert resolver.active_core_for_rom(40) == ("snes9x_libretro", "Snes9x")
    assert platform_reader.calls == ["snes"]
    assert core_info.active_core_calls == ["snes"]


# --- bad path: unknown rom_id → (None, None), no raise -------------------------


def test_missing_rom_resolves_to_none_with_warning(caplog: pytest.LogCaptureFixture) -> None:
    uow = FakeUnitOfWork()
    core_info = FakeCoreInfoProvider(active_core=("mgba_libretro", "mGBA"))
    platform_reader = FakePlatformCoreReader(mapping={"gba": "mGBA"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    with caplog.at_level(logging.WARNING, logger="test"):
        result = resolver.active_core_for_rom(404)

    assert result == (None, None)
    # No system read happens for a ROM that does not exist — and the per-platform
    # layer (the retired-gamelist replacement) is never consulted for a missing ROM.
    assert core_info.active_core_calls == []
    assert platform_reader.calls == []
    assert any("404" in r.message for r in caplog.records)


# --- active_emulator_for_rom: the standalone-aware launch-bake seam (#129) ------


def test_standalone_system_default_resolves_to_standalone_emulator() -> None:
    """An un-pinned ROM on a standalone-emulator platform (PS3) resolves to the
    standalone :class:`EmulatorInvocation`, not a libretro core."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=50, platform_slug="ps3", emulator_override=None)
    rpcs3 = EmulatorInvocation.standalone("%EMULATOR_RPCS3% --no-gui %ROM%", "RPCS3 Directory (Standalone)")
    core_info = FakeCoreInfoProvider(standalone={"ps3": rpcs3})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_emulator_for_rom(50) == rpcs3
    # A standalone emulator has no libretro core — the .so-space projection is
    # (None, label) so read-path consumers degrade exactly as for (None, None).
    assert resolver.active_core_for_rom(50) == (None, "RPCS3 Directory (Standalone)")


def test_per_game_pin_beats_standalone_system_default() -> None:
    """A per-game libretro pin wins over a platform's standalone default — the
    launch-bake seam returns the libretro invocation."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=51, platform_slug="ps2", emulator_override="LRPS2")
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "pcsx2_libretro", "label": "LRPS2", "is_default": False}],
        standalone={"ps2": EmulatorInvocation.standalone("%EMULATOR_PCSX2% -batch %ROM%", "PCSX2 (Standalone)")},
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_emulator_for_rom(51) == EmulatorInvocation.libretro(
        "pcsx2_libretro", "LRPS2", "pcsx2_libretro.so"
    )


def test_per_platform_core_beats_standalone_system_default() -> None:
    """A per-platform libretro core wins over the standalone system default."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=52, platform_slug="ps2", emulator_override=None)
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "pcsx2_libretro", "label": "LRPS2", "is_default": False}],
        standalone={"ps2": EmulatorInvocation.standalone("%EMULATOR_PCSX2% -batch %ROM%", "PCSX2 (Standalone)")},
    )
    platform_reader = FakePlatformCoreReader(mapping={"ps2": "LRPS2"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    assert resolver.active_emulator_for_rom(52) == EmulatorInvocation.libretro(
        "pcsx2_libretro", "LRPS2", "pcsx2_libretro.so"
    )


def test_resolvable_pin_returns_libretro_invocation() -> None:
    """The launch-bake seam returns a libretro invocation for a resolvable pin."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=53, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(
        available_cores=[{"core_so": "mgba_libretro", "label": "mGBA", "is_default": True}],
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_emulator_for_rom(53) == EmulatorInvocation.libretro(
        "mgba_libretro", "mGBA", "mgba_libretro.so"
    )


def test_unresolvable_platform_returns_none() -> None:
    """A platform with no libretro default and no standalone pref resolves to None
    — the bake site falls back to the plain launch."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=54, platform_slug="unknown", emulator_override=None)
    core_info = FakeCoreInfoProvider(active_core=(None, None))
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_emulator_for_rom(54) is None


# --- per-game / per-platform pin to a STANDALONE emulator label (#1210) --------

_RPCS3_COMMAND = "%EMULATOR_RPCS3% --no-gui %ROM%"
_RPCS3_LABEL = "RPCS3 Directory (Standalone)"
_RPCS3 = EmulatorInvocation.standalone(_RPCS3_COMMAND, _RPCS3_LABEL)


def test_per_game_pin_to_standalone_label_resolves_standalone() -> None:
    """A per-game pin naming a bakeable STANDALONE emulator resolves to it."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=60, platform_slug="ps3", emulator_override=_RPCS3_LABEL)
    core_info = FakeCoreInfoProvider(options=[standalone_option(_RPCS3_COMMAND, _RPCS3_LABEL)])
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    assert resolver.active_emulator_for_rom(60) == _RPCS3
    # The .so-space projection is (None, label) — read-path consumers degrade.
    assert resolver.active_core_for_rom(60) == (None, _RPCS3_LABEL)


def test_per_platform_standalone_label_resolves_standalone() -> None:
    """A per-platform pin naming a bakeable STANDALONE emulator resolves to it."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=61, platform_slug="ps3", emulator_override=None)
    core_info = FakeCoreInfoProvider(options=[standalone_option(_RPCS3_COMMAND, _RPCS3_LABEL)])
    platform_reader = FakePlatformCoreReader(mapping={"ps3": "RPCS3 Directory (Standalone)"})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, platform_core_reader=platform_reader)

    assert resolver.active_emulator_for_rom(61) == _RPCS3


def test_stale_standalone_pin_degrades_to_default(caplog: pytest.LogCaptureFixture) -> None:
    """A per-game pin to a standalone label that is now un-bakeable degrades + warns.

    ``label_to_invocation`` returns ``None`` for a matched-but-un-bakeable option
    exactly as for an unknown label, so the degrade path is uniform across
    libretro and standalone kinds.
    """
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=62, platform_slug="ps3", emulator_override="RPCS3 Shortcut (Standalone)")
    core_info = FakeCoreInfoProvider(
        # The pinned label exists but is now un-bakeable (a shortcut form).
        options=[
            standalone_option(
                "%ENABLESHORTCUTS% %ROM%", "RPCS3 Shortcut (Standalone)", status="unbakeable", reason="shortcut_script"
            )
        ],
        standalone={"ps3": _RPCS3},
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)

    with caplog.at_level(logging.WARNING, logger="test"):
        result = resolver.active_emulator_for_rom(62)

    # Degrades to the system default (the bakeable RPCS3 Directory), never raises.
    assert result == _RPCS3
    assert any("RPCS3 Shortcut (Standalone)" in r.message and "degrading" in r.message for r in caplog.records)


# --- folder-boot direct rewrite: standalone → sandbox launch (ADR-0019 / #1212) -

_PS3_EBOOT = "/roms/ps3/MyGame/PS3_GAME/USRDIR/EBOOT.BIN"
_PS3_ROM_DIR = "/roms/ps3/MyGame"
_RPCS3_LAUNCHER = "/app/retrodeck/components/rpcs3/component_launcher.sh"


def test_folder_boot_standalone_rewrites_to_direct() -> None:
    """A standalone PS3 default over a folder-boot install becomes the ``direct``
    sandbox invocation (its launcher resolved via the es_find_rules probe)."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=70, platform_slug="ps3", emulator_override=None)
    _seed_install(uow, rom_id=70, file_path=_PS3_EBOOT, rom_dir=_PS3_ROM_DIR)
    core_info = FakeCoreInfoProvider(standalone={"ps3": _RPCS3})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, sandbox_launchers={_RPCS3_COMMAND: _RPCS3_LAUNCHER})

    assert resolver.active_emulator_for_rom(70) == EmulatorInvocation.direct(
        _RPCS3_COMMAND, _RPCS3_LAUNCHER, _RPCS3_LABEL
    )
    # The .so-space projection stays (None, label) — unchanged from the standalone.
    assert resolver.active_core_for_rom(70) == (None, _RPCS3_LABEL)


def test_folder_boot_standalone_pin_also_rewrites_to_direct() -> None:
    """A per-game standalone PIN over a folder-boot install rewrites to direct too —
    the rewrite is on the resolved emulator, whichever layer produced it."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=71, platform_slug="ps3", emulator_override=_RPCS3_LABEL)
    _seed_install(uow, rom_id=71, file_path=_PS3_EBOOT, rom_dir=_PS3_ROM_DIR)
    core_info = FakeCoreInfoProvider(options=[standalone_option(_RPCS3_COMMAND, _RPCS3_LABEL)])
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, sandbox_launchers={_RPCS3_COMMAND: _RPCS3_LAUNCHER})

    assert resolver.active_emulator_for_rom(71) == EmulatorInvocation.direct(
        _RPCS3_COMMAND, _RPCS3_LAUNCHER, _RPCS3_LABEL
    )


def test_non_folder_install_keeps_standalone_run_game_form() -> None:
    """A standalone over a NON-folder install (e.g. a .iso, no folder-boot marker)
    is left as the run_game ``-e`` standalone form — byte-identical to before."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=72, platform_slug="ps3", emulator_override=None)
    _seed_install(uow, rom_id=72, file_path="/roms/ps3/Game.iso", rom_dir="/roms/ps3/Game")
    core_info = FakeCoreInfoProvider(standalone={"ps3": _RPCS3})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, sandbox_launchers={_RPCS3_COMMAND: _RPCS3_LAUNCHER})

    assert resolver.active_emulator_for_rom(72) == _RPCS3


def test_uninstalled_rom_keeps_standalone() -> None:
    """No install row (uninstalled ROM) → no folder-boot rewrite; the standalone
    invocation passes through unchanged for the read-path projection."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=73, platform_slug="ps3", emulator_override=None)
    core_info = FakeCoreInfoProvider(standalone={"ps3": _RPCS3})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, sandbox_launchers={_RPCS3_COMMAND: _RPCS3_LAUNCHER})

    assert resolver.active_emulator_for_rom(73) == _RPCS3


def test_libretro_over_folder_boot_install_is_never_rewritten() -> None:
    """A libretro pin is never rewritten to direct, even over a folder-boot layout —
    the rewrite fires only for standalone emulators."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=74, platform_slug="ps3", emulator_override="LRPS3")
    _seed_install(uow, rom_id=74, file_path=_PS3_EBOOT, rom_dir=_PS3_ROM_DIR)
    core_info = FakeCoreInfoProvider(
        options=[
            standalone_option(_RPCS3_COMMAND, _RPCS3_LABEL),
            libretro_option("lrps3_libretro", "LRPS3"),
        ],
    )
    resolver, _ = _make_resolver(uow=uow, core_info=core_info, sandbox_launchers={_RPCS3_COMMAND: _RPCS3_LAUNCHER})

    assert resolver.active_emulator_for_rom(74) == EmulatorInvocation.libretro(
        "lrps3_libretro", "LRPS3", "lrps3_libretro.so"
    )


def test_folder_boot_standalone_unresolvable_launcher_keeps_run_game_and_warns(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """When the sandbox launcher cannot be resolved, the standalone run_game form is
    kept (no direct) and a WARNING is logged — the launch fails until a re-bake heals."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=75, platform_slug="ps3", emulator_override=None)
    _seed_install(uow, rom_id=75, file_path=_PS3_EBOOT, rom_dir=_PS3_ROM_DIR)
    core_info = FakeCoreInfoProvider(standalone={"ps3": _RPCS3})
    resolver, _ = _make_resolver(uow=uow, core_info=core_info)  # no launcher seeded → unresolvable

    with caplog.at_level(logging.WARNING, logger="test"):
        result = resolver.active_emulator_for_rom(75)

    assert result == _RPCS3
    assert any("sandbox" in r.message and "launcher" in r.message for r in caplog.records)


# --- the generated RetroArch appendconfig rides a libretro launch ------------


def test_a_libretro_launch_carries_the_generated_appendconfig() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=1, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")])
    asked: list[str] = []

    def ensure(platform: str) -> str | None:
        asked.append(platform)
        return "/data/retroarch/retroarch-gba.cfg"

    resolver, _ = _make_resolver(uow=uow, core_info=core_info, appendconfig=ensure)
    emulator = resolver.active_emulator_for_rom(1)

    assert emulator is not None
    assert emulator.appendconfig == "/data/retroarch/retroarch-gba.cfg"
    assert asked == ["gba"]


def test_without_a_generator_the_launch_is_unchanged() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=2, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")])

    resolver, _ = _make_resolver(uow=uow, core_info=core_info)
    emulator = resolver.active_emulator_for_rom(2)

    assert emulator is not None
    assert emulator.appendconfig is None


def test_a_generator_with_nothing_to_offer_degrades_to_no_redirect() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=3, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")])

    resolver, _ = _make_resolver(uow=uow, core_info=core_info, appendconfig=lambda _platform: None)
    emulator = resolver.active_emulator_for_rom(3)

    assert emulator is not None
    assert emulator.appendconfig is None


def test_a_raising_generator_never_fails_a_launch(caplog) -> None:
    """A save nicety must not be able to stop a game starting."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=4, platform_slug="gba", emulator_override="mGBA")
    core_info = FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")])

    def boom(_platform: str) -> str | None:
        raise OSError("data directory is read-only")

    resolver, _ = _make_resolver(uow=uow, core_info=core_info, appendconfig=boom)
    with caplog.at_level(logging.WARNING):
        emulator = resolver.active_emulator_for_rom(4)

    assert emulator is not None
    assert emulator.core_so == "mgba_libretro"
    assert emulator.appendconfig is None
    assert "appendconfig" in caplog.text


def test_a_standalone_launch_never_carries_one() -> None:
    """Standalone emulators are placed-and-harvested, never pointed at a config."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5, platform_slug="ps2", emulator_override="PCSX2")
    core_info = FakeCoreInfoProvider(options=[standalone_option("%EMULATOR_PCSX2% %ROM%", "PCSX2")])

    resolver, _ = _make_resolver(
        uow=uow,
        core_info=core_info,
        appendconfig=lambda _platform: "/data/retroarch/retroarch-ps2.cfg",
    )
    emulator = resolver.active_emulator_for_rom(5)

    assert emulator is not None
    assert emulator.kind == "standalone"
    assert emulator.appendconfig is None


# --- the owned launch, when the settings opt into it --------------------------

_OWNED_RUNNER = RetroArchRunner(
    prefix="flatpak run org.libretro.RetroArch",
    cores_dir="/home/deck/.var/app/org.libretro.RetroArch/config/retroarch/cores",
    label="RetroArch (Flatpak)",
)


def _owned_uow(rom_id: int) -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=rom_id, platform_slug="gba", emulator_override="mGBA")
    return uow


def test_the_owned_backend_swaps_in_a_direct_retroarch_launch() -> None:
    resolver, _ = _make_resolver(
        uow=_owned_uow(11),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        appendconfig=lambda platform: f"/data/retroarch/retroarch-{platform}.cfg",
        launch_backend=lambda: "retroarch",
        runner=lambda core_so: _OWNED_RUNNER,
    )

    emulator = resolver.active_emulator_for_rom(11)

    assert emulator is not None
    assert emulator.runner == _OWNED_RUNNER
    assert "retrodeck" not in resolve_emulator_invocation({}, emulator).lower()


def test_the_default_backend_keeps_the_retrodeck_launch() -> None:
    resolver, _ = _make_resolver(
        uow=_owned_uow(12),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        launch_backend=lambda: "retrodeck",
        runner=lambda core_so: _OWNED_RUNNER,
    )

    emulator = resolver.active_emulator_for_rom(12)

    assert emulator is not None
    assert emulator.runner is None
    assert resolve_emulator_invocation({}, emulator).startswith("flatpak run net.retrodeck.retrodeck")


def test_no_runner_holding_the_core_keeps_the_retrodeck_launch() -> None:
    # The opt-in is a preference, not a promise: an install that cannot start the core
    # must still launch the game, through the path it used before.
    resolver, _ = _make_resolver(
        uow=_owned_uow(13),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        launch_backend=lambda: "retroarch",
        runner=lambda core_so: None,
    )

    emulator = resolver.active_emulator_for_rom(13)

    assert emulator is not None
    assert emulator.runner is None


def test_a_raising_runner_keeps_the_retrodeck_launch(caplog) -> None:
    def boom(_core_so: str):
        raise OSError("cannot stat the cores directory")

    resolver, _ = _make_resolver(
        uow=_owned_uow(14),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        appendconfig=lambda platform: f"/data/retroarch/retroarch-{platform}.cfg",
        launch_backend=lambda: "retroarch",
        runner=boom,
    )
    with caplog.at_level(logging.WARNING):
        emulator = resolver.active_emulator_for_rom(14)

    assert emulator is not None
    assert emulator.runner is None
    # The redirect survives the fallback: it is what the lookup reads either way.
    assert emulator.appendconfig == "/data/retroarch/retroarch-gba.cfg"
    assert "no owned runner" in caplog.text


def test_a_standalone_launch_is_never_owned() -> None:
    # Standalone emulators already run their own command; there is nothing RetroDECK
    # adds to them that this path removes.
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=15, platform_slug="ps2", emulator_override="PCSX2")
    resolver, _ = _make_resolver(
        uow=uow,
        core_info=FakeCoreInfoProvider(options=[standalone_option("%EMULATOR_PCSX2% %ROM%", "PCSX2")]),
        launch_backend=lambda: "retroarch",
        runner=lambda core_so: _OWNED_RUNNER,
    )

    emulator = resolver.active_emulator_for_rom(15)

    assert emulator is not None
    assert emulator.kind == "standalone"
    assert emulator.runner is None


def test_an_owned_launch_needs_the_redirect_too() -> None:
    """Owned-but-unredirected writes to RetroArch's own directory — sync looks elsewhere."""
    resolver, _ = _make_resolver(
        uow=_owned_uow(16),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        launch_backend=lambda: "retroarch",
        runner=lambda core_so: _OWNED_RUNNER,
    )

    emulator = resolver.active_emulator_for_rom(16)

    assert emulator is not None
    assert emulator.appendconfig is None
    assert emulator.runner is None
    assert resolve_emulator_invocation({}, emulator).startswith("flatpak run net.retrodeck.retrodeck")


def test_the_owned_launch_arrives_once_both_opt_ins_are_on() -> None:
    resolver, _ = _make_resolver(
        uow=_owned_uow(17),
        core_info=FakeCoreInfoProvider(options=[libretro_option("mgba_libretro", "mGBA")]),
        appendconfig=lambda platform: f"/data/retroarch/retroarch-{platform}.cfg",
        launch_backend=lambda: "retroarch",
        runner=lambda core_so: _OWNED_RUNNER,
    )

    emulator = resolver.active_emulator_for_rom(17)

    assert emulator is not None
    assert emulator.appendconfig == "/data/retroarch/retroarch-gba.cfg"
    assert emulator.runner == _OWNED_RUNNER
    rendered = resolve_emulator_invocation({}, emulator)
    assert "retrodeck" not in rendered.lower()
    assert "--appendconfig=/data/retroarch/retroarch-gba.cfg" in rendered


# --- the manifest and the picker: who outranks whom ---------------------------


def _gc_entry() -> ManagedPlatform:
    """The GameCube entry the provisioner writes, as the resolver would read it."""
    return ManagedPlatform(
        platform="gc",
        emulator="Dolphin (Standalone)",
        launch=("%EMULATOR_DOLPHIN%", "-b", "-e", "%ROM%"),
        save_dir="/tmp/arcoon/saves/gc/GC/<region>/Card A",
        save_unit="gci-set",
        needs=("region",),
    )


def _gc_resolver(*, uow: FakeUnitOfWork, platform_cores: dict[str, str] | None = None):
    core_info = FakeCoreInfoProvider(
        options=[
            libretro_option("/cores/dolphin_libretro.so", "Dolphin"),
            standalone_option("%EMULATOR_DOLPHIN% -b -e %ROM%", "Dolphin (Standalone)"),
        ],
        active_core=("dolphin_libretro", "Dolphin"),
    )
    return _make_resolver(
        uow=uow,
        core_info=core_info,
        platform_core_reader=FakePlatformCoreReader(platform_cores),
        managed_layout=lambda slug: _gc_entry() if slug == "gc" else None,
    )[0]


def test_the_manifest_states_the_launch_when_nothing_has_been_chosen() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5319, platform_slug="gc")
    _seed_install(uow, rom_id=5319, file_path="/roms/gc/zelda.rvz", rom_dir="/roms/gc")

    resolver = _gc_resolver(uow=uow)

    emulator = resolver.active_emulator_for_rom(5319)
    assert emulator is not None
    assert emulator.label == "Dolphin (Standalone)"
    command = resolve_emulator_invocation({}, emulator)
    assert "%EMULATOR_DOLPHIN%" in command and "-b" in command


def test_the_per_game_pick_outranks_the_manifest() -> None:
    """The picker is the user saying which emulator runs; the manifest is the default."""
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5319, platform_slug="gc", emulator_override="Dolphin")
    _seed_install(uow, rom_id=5319, file_path="/roms/gc/zelda.rvz", rom_dir="/roms/gc")

    resolver = _gc_resolver(uow=uow)

    emulator = resolver.active_emulator_for_rom(5319)
    assert emulator is not None
    assert emulator.label == "Dolphin"
    assert resolver.managed_entry(5319) is None


def test_the_per_platform_core_outranks_the_manifest() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5319, platform_slug="gc")
    _seed_install(uow, rom_id=5319, file_path="/roms/gc/zelda.rvz", rom_dir="/roms/gc")

    resolver = _gc_resolver(uow=uow, platform_cores={"gc": "Dolphin"})

    emulator = resolver.active_emulator_for_rom(5319)
    assert emulator is not None
    assert emulator.label == "Dolphin"
    assert resolver.managed_entry(5319) is None


def test_the_save_layer_is_told_the_same_entry_the_launch_used() -> None:
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5319, platform_slug="gc")
    _seed_install(uow, rom_id=5319, file_path="/roms/gc/zelda.rvz", rom_dir="/roms/gc")

    resolver = _gc_resolver(uow=uow)

    entry = resolver.managed_entry(5319)
    assert entry is not None
    assert entry.save_dir.endswith("GC/<region>/Card A")


def test_the_save_path_does_not_step_aside_for_the_pick() -> None:
    """The picker chooses the program; the platform owns where its cards live.

    Measured on the reference Deck: RetroDECK runs the libretro Dolphin core inside
    Dolphin's user tree, so both emulators write the same card folder. Letting the
    pick move the save path is what pointed the sync at a folder the launch never
    wrote — rom 5319 reported ``uploaded=0`` with the card one directory away.
    """
    uow = FakeUnitOfWork()
    _seed_rom(uow, rom_id=5319, platform_slug="gc", emulator_override="Dolphin")
    _seed_install(uow, rom_id=5319, file_path="/roms/gc/zelda.rvz", rom_dir="/roms/gc")

    resolver = _gc_resolver(uow=uow)

    assert resolver.managed_entry(5319) is None
    entry = resolver.managed_save_entry(5319)
    assert entry is not None
    assert entry.save_unit == "gci-set"
    assert entry.save_dir.endswith("GC/<region>/Card A")
