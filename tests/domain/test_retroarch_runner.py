"""The owned RetroArch argv and the backend choice that selects it."""

from __future__ import annotations

import pytest

from domain.retroarch_runner import (
    DEFAULT_LAUNCH_BACKEND,
    ROM_PLACEHOLDER,
    RetroArchRunner,
    resolve_backend,
    retroarch_command,
)

RUNNER = RetroArchRunner(
    prefix="flatpak run org.libretro.RetroArch",
    cores_dir="/home/deck/.var/app/org.libretro.RetroArch/config/retroarch/cores",
    label="RetroArch (Flatpak)",
)


class TestResolveBackend:
    @pytest.mark.parametrize("value", ["retroarch"])
    def test_the_literal_selects_the_owned_path(self, value: str) -> None:
        assert resolve_backend(value) == "retroarch"

    @pytest.mark.parametrize("value", [None, "", "retrodeck", "RetroArch", "yes", 1, True, {"a": 1}])
    def test_everything_else_stays_on_retrodeck(self, value: object) -> None:
        # A hand-edited settings file must not be able to reroute the whole library on a
        # truthy-but-wrong value; only the documented literal opts in.
        assert resolve_backend(value) == DEFAULT_LAUNCH_BACKEND == "retrodeck"


class TestRetroarchCommand:
    def test_owned_argv_has_no_retrodeck_in_it(self) -> None:
        command = retroarch_command(RUNNER, core_so="mgba_libretro", appendconfig=None)

        assert command == f"flatpak run org.libretro.RetroArch -L {RUNNER.cores_dir}/mgba_libretro.so"
        assert "retrodeck" not in command.lower()
        assert "%EMULATOR_RETROARCH%" not in command
        assert " -e " not in command

    def test_the_command_carries_no_content_placeholder(self) -> None:
        # Nothing substitutes %ROM% on this path, and build_launch_options appends the
        # real path: a leftover placeholder becomes an argument RetroArch tries to load.
        command = retroarch_command(RUNNER, core_so="mgba_libretro", appendconfig=None)

        assert ROM_PLACEHOLDER not in command
        assert "%ROM%" not in command

    def test_the_appendconfig_rides_after_the_core(self) -> None:
        # RetroArch takes global flags before the content path, so the appendconfig sits
        # after -L and before the path build_launch_options appends.
        command = retroarch_command(
            RUNNER, core_so="mgba_libretro", appendconfig="/home/deck/.local/share/romm-tender/retroarch/gba.cfg"
        )

        assert command.endswith("--appendconfig=/home/deck/.local/share/romm-tender/retroarch/gba.cfg")
        assert command.index("-L ") < command.index("--appendconfig=")
        assert " -e " not in command

    def test_a_path_that_cannot_ride_unquoted_is_dropped_not_escaped(self) -> None:
        command = retroarch_command(RUNNER, core_so="mgba_libretro", appendconfig="/home/deck/My Saves/gba.cfg")

        assert "--appendconfig" not in command
        assert command.endswith("mgba_libretro.so")

    def test_a_native_runner_uses_its_own_cores_dir_and_binary(self) -> None:
        native = RetroArchRunner(
            prefix="/usr/bin/retroarch", cores_dir="/home/deck/.config/retroarch/cores", label="RetroArch (system)"
        )

        command = retroarch_command(native, core_so="snes9x_libretro", appendconfig=None)

        assert command == "/usr/bin/retroarch -L /home/deck/.config/retroarch/cores/snes9x_libretro.so"
