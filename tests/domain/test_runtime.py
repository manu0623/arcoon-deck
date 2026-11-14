"""The runtime decision and the roots it owns, with RetroDECK present and absent."""

from __future__ import annotations

from domain.runtime import (
    RETROARCH_FLATPAK_CORES,
    RuntimeMode,
    resolve_launch_backend,
    resolve_mode,
    resolve_roots,
)

_RD = {
    "roms": "/home/deck/retrodeck/roms",
    "saves": "/home/deck/retrodeck/saves",
    "bios": "/home/deck/retrodeck/bios",
    "states": "/home/deck/retrodeck/states",
}


class TestWhichRuntimeIsDriven:
    def test_auto_follows_an_install(self) -> None:
        assert resolve_mode("auto", retrodeck_present=True) is RuntimeMode.RETRODECK

    def test_auto_stands_alone_without_one(self) -> None:
        assert resolve_mode("auto", retrodeck_present=False) is RuntimeMode.BUILTIN

    def test_an_unset_setting_reads_as_auto(self) -> None:
        assert resolve_mode(None, retrodeck_present=False) is RuntimeMode.BUILTIN

    def test_an_explicit_choice_outranks_detection(self) -> None:
        # A user pointing at a tree the probe does not read keeps that tree.
        assert resolve_mode("retrodeck", retrodeck_present=False) is RuntimeMode.RETRODECK
        assert resolve_mode("builtin", retrodeck_present=True) is RuntimeMode.BUILTIN

    def test_the_old_standalone_spelling_reads_as_builtin(self) -> None:
        # 0.36.0 shipped "standalone" for this decision; the file must not lose it.
        assert resolve_mode("standalone", retrodeck_present=True) is RuntimeMode.BUILTIN

    def test_a_nonsense_value_does_not_reroute_the_library(self) -> None:
        assert resolve_mode("yes", retrodeck_present=True) is RuntimeMode.RETRODECK


class TestTheRootsEachRuntimeOwns:
    def test_retrodeck_roots_pass_through_untouched(self) -> None:
        roots = resolve_roots(mode=RuntimeMode.RETRODECK, home="/home/deck", retrodeck_roots=_RD)
        assert (roots.roms, roots.saves, roots.bios, roots.states) == (
            "/home/deck/retrodeck/roms",
            "/home/deck/retrodeck/saves",
            "/home/deck/retrodeck/bios",
            "/home/deck/retrodeck/states",
        )

    def test_standalone_roots_live_in_its_own_tree(self) -> None:
        roots = resolve_roots(mode=RuntimeMode.BUILTIN, home="/home/deck", retrodeck_roots=_RD)
        assert roots.roms == "/home/deck/Emulation/roms"
        assert roots.saves == "/home/deck/Emulation/saves"
        assert roots.bios == "/home/deck/Emulation/bios"
        assert roots.states == "/home/deck/Emulation/states"

    def test_the_cores_root_is_the_owned_runtime_s(self) -> None:
        roots = resolve_roots(mode=RuntimeMode.BUILTIN, home="/home/deck", retrodeck_roots=_RD)
        assert roots.cores == "/home/deck/" + "/".join(RETROARCH_FLATPAK_CORES)

    def test_a_setting_overrides_one_root_only(self) -> None:
        roots = resolve_roots(
            mode=RuntimeMode.BUILTIN,
            home="/home/deck",
            retrodeck_roots=_RD,
            settings={"roms_dir": "/run/media/deck/roms"},
        )
        assert roots.roms == "/run/media/deck/roms"
        assert roots.saves == "/home/deck/Emulation/saves"

    def test_a_cleared_override_falls_back_instead_of_pointing_at_nothing(self) -> None:
        roots = resolve_roots(
            mode=RuntimeMode.BUILTIN,
            home="/home/deck",
            retrodeck_roots=_RD,
            settings={"saves_dir": ""},
        )
        assert roots.saves == "/home/deck/Emulation/saves"

    def test_retrodeck_mode_ignores_standalone_overrides(self) -> None:
        roots = resolve_roots(
            mode=RuntimeMode.RETRODECK,
            home="/home/deck",
            retrodeck_roots=_RD,
            settings={"roms_dir": "/run/media/deck/roms"},
        )
        assert roots.roms == "/home/deck/retrodeck/roms"


class TestWhichLauncherABakeGoesThrough:
    def test_the_shipped_default_stays_retrodeck_when_it_is_installed(self) -> None:
        assert resolve_launch_backend("retrodeck", mode=RuntimeMode.RETRODECK) == "retrodeck"

    def test_a_standalone_runtime_never_bakes_the_absent_launcher(self) -> None:
        # Measured failure this prevents: `flatpak run net.retrodeck.retrodeck` with
        # RetroDECK removed is a shortcut that exits immediately.
        assert resolve_launch_backend("retrodeck", mode=RuntimeMode.BUILTIN) == "retroarch"
        assert resolve_launch_backend(None, mode=RuntimeMode.BUILTIN) == "retroarch"

    def test_an_explicit_owned_choice_always_wins(self) -> None:
        assert resolve_launch_backend("retroarch", mode=RuntimeMode.RETRODECK) == "retroarch"
