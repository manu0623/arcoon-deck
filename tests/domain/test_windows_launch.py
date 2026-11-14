"""The Windows platform's launch rules: which file is the game, and how it is named."""

from __future__ import annotations

import pytest

from domain.rom_files import detect_launch_file
from domain.windows_launch import (
    is_windows_launch_file,
    is_windows_platform,
    pick_game_exe,
    ranked_exe_paths,
    relative_to_install,
    shortcut_for_exe,
)

_ROOT = "/roms/windows/Skyrim"


def _files(*entries: tuple[str, int]) -> list[tuple[str, int]]:
    return list(entries)


class TestPlatformIdentity:
    @pytest.mark.parametrize("slug", ["windows", "Windows", " win "])
    def test_the_windows_slugs(self, slug):
        assert is_windows_platform(slug) is True

    @pytest.mark.parametrize("slug", ["psx", "dos", "pc", "", None])
    def test_everything_else(self, slug):
        assert is_windows_platform(slug) is False

    @pytest.mark.parametrize("name", ["Game.exe", "Game.EXE", "run.bat", "run.cmd"])
    def test_launchable_names(self, name):
        assert is_windows_launch_file(f"/roms/windows/{name}") is True

    @pytest.mark.parametrize("name", ["Game.zip", "Game.exe.zip", "readme.txt"])
    def test_non_launchable_names(self, name):
        assert is_windows_launch_file(f"/roms/windows/{name}") is False


class TestPickGameExe:
    def test_the_root_executable_wins_over_a_nested_one(self):
        files = _files(
            (f"{_ROOT}/Tools/diagnostic.exe", 900_000),
            (f"{_ROOT}/Skyrim.exe", 1_000),
        )
        assert pick_game_exe(files) == f"{_ROOT}/Skyrim.exe"

    def test_junk_is_never_the_game(self):
        files = _files(
            (f"{_ROOT}/setup.exe", 5_000_000),
            (f"{_ROOT}/unins000.exe", 4_000_000),
            (f"{_ROOT}/vcredist_x64.exe", 3_000_000),
            (f"{_ROOT}/Skyrim.exe", 10),
        )
        assert pick_game_exe(files) == f"{_ROOT}/Skyrim.exe"

    def test_a_folder_of_only_junk_names_nothing(self):
        files = _files(
            (f"{_ROOT}/setup.exe", 10),
            (f"{_ROOT}/UnityCrashHandler64.exe", 20),
            (f"{_ROOT}/data.bin", 1_000_000),
        )
        assert pick_game_exe(files) is None

    def test_the_name_similarity_breaks_a_depth_tie(self):
        files = _files(
            (f"{_ROOT}/BethesdaNet.exe", 10),
            (f"{_ROOT}/SkyrimLauncher.exe", 10),
        )
        assert pick_game_exe(files) == f"{_ROOT}/SkyrimLauncher.exe"

    def test_size_breaks_the_remaining_tie(self):
        files = _files(
            (f"{_ROOT}/Alpha.exe", 10),
            (f"{_ROOT}/Beta.exe", 5_000),
        )
        assert pick_game_exe(files) == f"{_ROOT}/Beta.exe"

    def test_a_bat_entry_point_is_a_launch_target(self):
        files = _files((f"{_ROOT}/start.bat", 10), (f"{_ROOT}/assets.pak", 9_000_000))
        assert pick_game_exe(files) == f"{_ROOT}/start.bat"

    def test_no_executable_at_all(self):
        files = _files((f"{_ROOT}/data.pak", 10), (f"{_ROOT}/readme.txt", 5))
        assert pick_game_exe(files) is None

    def test_ranking_keeps_junk_last_but_listed(self):
        files = _files(
            (f"{_ROOT}/unins000.exe", 90),
            (f"{_ROOT}/Skyrim.exe", 10),
        )
        assert ranked_exe_paths(files) == [f"{_ROOT}/Skyrim.exe", f"{_ROOT}/unins000.exe"]


class TestShortcutShape:
    def test_the_exe_is_the_game_and_the_folder_is_its_own(self):
        assert shortcut_for_exe("/roms/windows/Skyrim/Skyrim.exe") == (
            "/roms/windows/Skyrim/Skyrim.exe",
            "/roms/windows/Skyrim",
        )


class TestRelativeToInstall:
    def test_a_nested_file_is_relative(self):
        assert relative_to_install(_ROOT, f"{_ROOT}/bin/Game.exe") == "bin/Game.exe"

    @pytest.mark.parametrize(
        "path",
        [
            "/roms/windows/Other/Game.exe",
            f"{_ROOT}/../Other/Game.exe",
            _ROOT,
            "",
        ],
    )
    def test_anything_outside_is_refused(self, path):
        assert relative_to_install(_ROOT, path) is None


class TestDetectLaunchFile:
    def test_the_windows_branch_wins_over_a_larger_file(self):
        files = _files(
            (f"{_ROOT}/Skyrim.exe", 1_000),
            (f"{_ROOT}/Skyrim - Data.pak", 9_000_000),
        )
        assert detect_launch_file(files, m3u_supported=False, windows=True) == f"{_ROOT}/Skyrim.exe"

    def test_without_the_flag_the_largest_file_still_wins(self):
        files = _files(
            (f"{_ROOT}/Skyrim.exe", 1_000),
            (f"{_ROOT}/Skyrim - Data.pak", 9_000_000),
        )
        assert detect_launch_file(files, m3u_supported=False) == f"{_ROOT}/Skyrim - Data.pak"

    def test_a_windows_folder_with_no_executable_falls_through(self):
        # Naming no executable is not a launch target invented: selection falls to
        # the ordinary rules, and the recorder's launchable check is what refuses
        # a soundtrack cue sheet as a PC game's entry point.
        files = _files((f"{_ROOT}/soundtrack.cue", 10), (f"{_ROOT}/data.pak", 9_000_000))
        assert detect_launch_file(files, m3u_supported=True, windows=True) == f"{_ROOT}/soundtrack.cue"
