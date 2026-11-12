"""Resolving a directly-startable RetroArch from the filesystem."""

from __future__ import annotations

import logging
from pathlib import Path

from adapters.retroarch_runner import FLATPAK_APP_ID, RetroArchRunnerAdapter

FLATPAK_CORES = Path(".var") / "app" / FLATPAK_APP_ID / "config" / "retroarch" / "cores"
NATIVE_CORES = Path(".config") / "retroarch" / "cores"


def _adapter(home: Path) -> RetroArchRunnerAdapter:
    return RetroArchRunnerAdapter(user_home=str(home), logger=logging.getLogger("test"))


def _install_cores(home: Path, relative: Path, core: str = "mgba_libretro") -> Path:
    cores = home / relative
    cores.mkdir(parents=True)
    (cores / f"{core}.so").touch()
    return cores


class TestNoInstall:
    def test_missing_directories_mean_no_runner(self, tmp_path: Path) -> None:
        # No RetroArch of any kind: the caller keeps the RetroDECK launch.
        assert _adapter(tmp_path)("mgba_libretro") is None

    def test_a_directory_without_the_core_is_not_a_candidate(self, tmp_path: Path) -> None:
        # The core is the test, not "is installed": starting this RetroArch would fail on
        # -L and look like a launch that does nothing.
        (tmp_path / FLATPAK_CORES).mkdir(parents=True)
        (tmp_path / FLATPAK_CORES / "snes9x_libretro.so").touch()

        assert _adapter(tmp_path)("mgba_libretro") is None


class TestCandidates:
    def test_the_flatpak_is_preferred(self, tmp_path: Path) -> None:
        flatpak_cores = _install_cores(tmp_path, FLATPAK_CORES)
        _install_cores(tmp_path, NATIVE_CORES)

        runner = _adapter(tmp_path)("mgba_libretro")

        assert runner is not None
        assert runner.prefix == f"flatpak run {FLATPAK_APP_ID}"
        assert runner.cores_dir == str(flatpak_cores)

    def test_a_flatroots_retroarch_without_the_core_falls_through_to_native(self, tmp_path: Path) -> None:
        (tmp_path / FLATPAK_CORES).mkdir(parents=True)
        (tmp_path / FLATPAK_CORES / "snes9x_libretro.so").touch()
        native_cores = _install_cores(tmp_path, NATIVE_CORES)

        runner = _adapter(tmp_path)("mgba_libretro")

        assert runner is not None
        assert runner.prefix == "/usr/bin/retroarch"
        assert runner.cores_dir == str(native_cores)

    def test_the_cores_dir_is_the_host_path_never_the_sandbox_path(self, tmp_path: Path) -> None:
        # A directly-started RetroArch cannot see RetroDECK's /var/config, so handing it
        # that path would bake a launch that cannot find its own core.
        flatpak_cores = Path(".var") / "app" / FLATPAK_APP_ID / "config" / "retroarch" / "cores"
        _install_cores(tmp_path, flatpak_cores)

        runner = _adapter(tmp_path)("mgba_libretro")

        assert runner is not None
        assert runner.cores_dir.startswith(str(tmp_path))
        assert "/var/config/retroarch" not in runner.cores_dir
