"""One installed emulator as a Steam tile: what it execs, and where it starts.

The two providers that qualify are the two whose install IS a command; everything
else is declined rather than guessed at, because a tile that opens a file picker or
a script that demands a ROM is not the tile a reader asked for.
"""

from __future__ import annotations

from domain.emulator_registry import DetectionHints, EmulatorDef, InstalledEmulator
from domain.emulator_shortcut import FLATPAK_EXE, shortcut_for, shortcuts

PPSSPP = EmulatorDef(
    id="ppsspp",
    display_name="PPSSPP",
    family="ppsspp",
    platforms=("psp",),
    hints=DetectionHints(appimage_prefixes=("ppsspp",), flatpak_ids=("org.ppsspp.PPSSPP",)),
)


def _install(provider: str, path: str, version: str | None = None) -> InstalledEmulator:
    return InstalledEmulator(definition=PPSSPP, provider=provider, path=path, version_hint=version)  # type: ignore[arg-type]


class TestTheTwoLaunchableProviders:
    def test_a_native_build_is_the_file_itself(self) -> None:
        row = shortcut_for(_install("native", "/home/deck/Applications/PPSSPP.AppImage", "1.20.4"))

        assert row is not None
        assert (row.exe, row.start_dir, row.launch_options) == (
            "/home/deck/Applications/PPSSPP.AppImage",
            "/home/deck/Applications",
            "",
        )
        assert row.version == "1.20.4"
        assert row.key == "ppsspp@native"

    def test_a_flatpak_is_its_application_id_through_flatpak_run(self) -> None:
        row = shortcut_for(_install("flatpak", "org.ppsspp.PPSSPP", "1.20.4"))

        assert row is not None
        assert (row.exe, row.start_dir, row.launch_options) == (FLATPAK_EXE, "", "run org.ppsspp.PPSSPP")
        assert row.key == "ppsspp@flatpak"

    def test_the_art_search_is_the_emulators_own_name(self) -> None:
        row = shortcut_for(_install("flatpak", "org.ppsspp.PPSSPP"))

        assert row is not None
        assert row.name == "PPSSPP (Flatpak)"
        assert row.search_term == "PPSSPP"

    def test_a_launcher_script_is_not_a_tile(self) -> None:
        """EmuDeck's launchers take a ROM; run bare they are not a window."""
        assert shortcut_for(_install("emudeck", "/home/deck/Emulation/tools/launchers/ppsspp.sh")) is None


class TestTheCatalogue:
    def test_one_row_per_emulator_and_provider(self) -> None:
        rows = shortcuts(
            [
                _install("native", "/home/deck/Applications/PPSSPP.AppImage"),
                _install("flatpak", "org.ppsspp.PPSSPP"),
            ]
        )

        # "AppImage" sorts before "Flatpak", which is the order the labels read in.
        assert [row.key for row in rows] == ["ppsspp@native", "ppsspp@flatpak"]

    def test_two_builds_under_one_provider_are_one_row(self) -> None:
        rows = shortcuts(
            [
                _install("native", "/home/deck/Applications/PPSSPP.AppImage"),
                _install("native", "/home/deck/Applications/PPSSPP.AppImage_old"),
            ]
        )

        assert [row.exe for row in rows] == ["/home/deck/Applications/PPSSPP.AppImage"]

    def test_the_rows_are_alphabetical(self) -> None:
        davinci = EmulatorDef(
            id="dolphin",
            display_name="Dolphin",
            family="dolphin",
            platforms=("gc",),
            hints=DetectionHints(flatpak_ids=("org.DolphinEmu.dolphin-emu",)),
        )
        rows = shortcuts(
            [
                _install("flatpak", "org.ppsspp.PPSSPP"),
                InstalledEmulator(definition=davinci, provider="flatpak", path="org.DolphinEmu.dolphin-emu"),
            ]
        )

        assert [row.name for row in rows] == ["Dolphin (Flatpak)", "PPSSPP (Flatpak)"]
