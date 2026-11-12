"""The emulator scanner, driven against a fake Deck rather than a real one.

The fake filesystem is built from paths and filenames read off a live Steam Deck —
``Eden.appimage`` beside ``eden.appimage``, ``Freegosy.appimage`` that nothing
claims, an ``Emulation/tools/launchers`` directory with no ``eden.sh`` — so these
tests describe a machine that exists rather than one invented for the occasion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from adapters.emulator_scan import EmulatorScanner, Entry, ScanResult

if TYPE_CHECKING:
    from collections.abc import Sequence

HOME = "/home/deck"


def _entry(
    name: str,
    path: str | None = None,
    *,
    is_dir: bool = False,
    size: int | None = 100,
    modified: str | None = "2026-10-21",
    executable: bool = True,
) -> Entry:
    return Entry(
        name=name,
        path=path or f"{HOME}/Applications/{name}",
        is_dir=is_dir,
        size=None if is_dir else size,
        modified=None if is_dir else modified,
        executable=executable,
    )


class FakeDirectories:
    """A filesystem that is a dict, so a scan is a pure function of its fixtures."""

    def __init__(self, listing: dict[str, list[Entry]]) -> None:
        self.listing = listing
        self.asked: list[str] = []

    def list(self, path: str) -> Sequence[Entry]:
        self.asked.append(path)
        return self.listing.get(path, ())


def _scan(
    listing: dict[str, list[Entry]],
    *,
    flatpaks: list[tuple[str, str | None]] | None = None,
) -> ScanResult:
    scanner = EmulatorScanner(
        home=HOME,
        directories=FakeDirectories(listing),
        list_flatpaks=(lambda: flatpaks) if flatpaks is not None else None,
    )
    return scanner.scan()


class TestApplicationsProbe:
    def test_finds_an_appimage_and_names_its_provider(self) -> None:
        result = _scan({f"{HOME}/Applications": [_entry("pcsx2-Qt.AppImage")]})
        assert [install.id for install in result.installs] == ["pcsx2"]
        assert result.installs[0].provider == "native"
        assert result.installs[0].label == "PCSX2 (AppImage)"

    def test_two_byte_identical_edens_become_one_install(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [
                    _entry("Eden.appimage", size=70075388, modified="2026-06-27"),
                    _entry("eden.appimage", size=70075388, modified="2026-06-27"),
                ]
            }
        )
        assert len(result.installs) == 1
        assert result.installs[0].id == "eden"
        assert result.installs[0].aliases == (f"{HOME}/Applications/eden.appimage",)

    def test_two_rpcs3_builds_stay_two_installs(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [
                    _entry("rpcs3.AppImage", size=94685173),
                    _entry("rpcs3.AppImage_old", size=97156175),
                ]
            }
        )
        assert len(result.installs) == 2
        assert {install.id for install in result.installs} == {"rpcs3"}

    def test_unclaimed_appimages_are_reported_not_dropped(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [
                    _entry("Freegosy.appimage"),
                    _entry("EmuDeck.AppImage"),
                    _entry("eden.appimage"),
                ]
            }
        )
        assert [install.id for install in result.installs] == ["eden"]
        assert result.unrecognised == (
            f"{HOME}/Applications/EmuDeck.AppImage",
            f"{HOME}/Applications/Freegosy.appimage",
        )

    def test_non_appimage_files_are_ignored_silently(self) -> None:
        result = _scan({f"{HOME}/Applications": [_entry("readme.txt"), _entry("notes.md")]})
        assert result.installs == ()
        assert result.unrecognised == ()

    def test_a_missing_applications_directory_is_a_note(self) -> None:
        result = _scan({})
        assert result.installs == ()
        assert any("Applications" in note for note in result.notes)


class TestNestedBinaries:
    def test_a_publish_directory_binary_is_found(self) -> None:
        """``~/Applications/publish/Ryujinx`` — EmuDeck's binary layout on this Deck."""
        result = _scan(
            {
                f"{HOME}/Applications": [_entry("publish", is_dir=True)],
                f"{HOME}/Applications/publish": [_entry("Ryujinx", path=f"{HOME}/Applications/publish/Ryujinx")],
            }
        )
        assert [install.id for install in result.installs] == ["ryujinx"]

    def test_a_nested_install_directory_is_found(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [_entry("Vita3K", is_dir=True)],
                f"{HOME}/Applications/Vita3K": [
                    _entry("Vita3K", path=f"{HOME}/Applications/Vita3K/Vita3K"),
                ],
            }
        )
        assert [install.id for install in result.installs] == ["vita3k"]

    def test_non_executable_namesakes_are_not_installs(self) -> None:
        """The reference Deck's ``publish/`` holds ``Ryujinx.sh`` and ``Ryujinx.xml``."""
        result = _scan(
            {
                f"{HOME}/Applications": [_entry("publish", is_dir=True)],
                f"{HOME}/Applications/publish": [
                    _entry("Ryujinx.sh", path=f"{HOME}/Applications/publish/Ryujinx.sh", executable=False),
                    _entry("Ryujinx.xml", path=f"{HOME}/Applications/publish/mime/Ryujinx.xml", executable=False),
                    _entry("Ryujinx", path=f"{HOME}/Applications/publish/Ryujinx"),
                ],
            }
        )
        assert [install.path for install in result.installs] == [f"{HOME}/Applications/publish/Ryujinx"]

    def test_unrelated_nested_binaries_are_not_installs(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [_entry("someapp", is_dir=True)],
                f"{HOME}/Applications/someapp": [_entry("helper", path=f"{HOME}/Applications/someapp/helper")],
            }
        )
        assert result.installs == ()


class TestLauncherProbe:
    def test_launcher_scripts_are_emudeck_installs(self) -> None:
        result = _scan(
            {
                f"{HOME}/Emulation/tools/launchers": [
                    _entry("pcsx2-qt.sh", path=f"{HOME}/Emulation/tools/launchers/pcsx2-qt.sh"),
                    _entry("dolphin-emu.sh", path=f"{HOME}/Emulation/tools/launchers/dolphin-emu.sh"),
                ]
            }
        )
        labels = sorted(install.label for install in result.installs)
        assert labels == ["Dolphin (EmuDeck)", "PCSX2 (EmuDeck)"]

    def test_unreadable_junk_filenames_are_skipped(self) -> None:
        """The reference Deck's launchers directory holds non-UTF-8 names."""
        result = _scan(
            {
                f"{HOME}/Emulation/tools/launchers": [
                    _entry("\x10\udc80{\udc82U", path=f"{HOME}/Emulation/tools/launchers/junk"),
                    _entry("cache", is_dir=True),
                    _entry("mgba.sh", path=f"{HOME}/Emulation/tools/launchers/mgba.sh"),
                ]
            }
        )
        assert [install.id for install in result.installs] == ["mgba"]

    def test_the_retroarch_launcher_is_not_a_second_provider(self) -> None:
        """EmuDeck's ``retroarch.sh`` wraps the flatpak the flatpak probe reports."""
        result = _scan(
            {
                f"{HOME}/Emulation/tools/launchers": [
                    _entry("retroarch.sh", path=f"{HOME}/Emulation/tools/launchers/retroarch.sh"),
                    _entry("mgba.sh", path=f"{HOME}/Emulation/tools/launchers/mgba.sh"),
                ]
            },
            flatpaks=[("org.libretro.RetroArch", "1.22.2")],
        )
        assert [install.label for install in result.installs if install.id == "retroarch"] == ["RetroArch (Flatpak)"]

    def test_emudeck_without_an_eden_launcher_yields_no_eden(self) -> None:
        """Pinned: EmuDeck ships yuzu/citron/ryujinx scripts and no eden one."""
        result = _scan(
            {
                f"{HOME}/Emulation/tools/launchers": [
                    _entry("yuzu.sh", path=f"{HOME}/Emulation/tools/launchers/yuzu.sh"),
                    _entry("citron.sh", path=f"{HOME}/Emulation/tools/launchers/citron.sh"),
                ]
            }
        )
        assert {install.id for install in result.installs} == {"yuzu", "citron"}

    def test_a_missing_launchers_directory_is_a_note(self) -> None:
        result = _scan({})
        assert any("EmuDeck" in note for note in result.notes)


class TestFlatpakProbe:
    def test_a_flatpak_install_carries_its_version(self) -> None:
        result = _scan(
            {},
            flatpaks=[
                ("org.libretro.RetroArch", "1.22.2"),
                ("org.DolphinEmu.dolphin-emu", None),
                ("org.example.Unrelated", "9"),
            ],
        )
        by_id = {install.id: install for install in result.installs}
        assert by_id["retroarch"].provider == "flatpak"
        assert by_id["retroarch"].version_hint == "1.22.2"
        assert by_id["dolphin"].version_hint is None
        assert "org.example.Unrelated" not in {install.path for install in result.installs}

    def test_retrodeck_is_presence_without_per_emulator_installs(self) -> None:
        result = _scan({}, flatpaks=[("net.retrodeck.retrodeck", "0.10.9b")])
        assert result.retrodeck_present is True
        assert result.installs == ()

    def test_a_failing_flatpak_probe_is_a_note_not_a_crash(self) -> None:
        def explode() -> list[tuple[str, str | None]]:
            raise RuntimeError("flatpak list exited 1")

        scanner = EmulatorScanner(
            home=HOME,
            directories=FakeDirectories({}),
            list_flatpaks=explode,
        )
        result = scanner.scan()
        assert result.installs == ()
        assert any("flatpak list failed" in note for note in result.notes)

    def test_no_flatpak_probe_configured_is_silent(self) -> None:
        result = _scan({}, flatpaks=None)
        assert result.installs == ()
        assert not any("flatpak" in note for note in result.notes)


class TestPlatformViews:
    def test_switch_offers_every_installed_switch_emulator(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [
                    _entry("eden.appimage"),
                    _entry("Citron.AppImage"),
                    _entry("ryujinx.AppImage", size=31885816),
                ]
            }
        )
        assert set(result.labels_for_platform("switch")) == {
            "Eden (AppImage)",
            "Citron (AppImage)",
            "Ryujinx (AppImage)",
        }

    def test_switch_never_offers_retroarch(self) -> None:
        """No libretro core exists for Switch, so the frontend is not a candidate."""
        result = _scan(
            {f"{HOME}/Applications": [_entry("eden.appimage")]},
            flatpaks=[("org.libretro.RetroArch", "1.22.2")],
        )
        assert "RetroArch (Flatpak)" not in result.labels_for_platform("switch")
        assert "RetroArch (Flatpak)" in result.labels_for_platform("snes")

    def test_a_platform_nobody_can_play_is_empty_not_an_error(self) -> None:
        result = _scan({f"{HOME}/Applications": [_entry("eden.appimage")]})
        assert result.labels_for_platform("ps3") == ()

    def test_the_same_emulator_from_two_providers_is_two_labels(self) -> None:
        result = _scan(
            {
                f"{HOME}/Applications": [_entry("pcsx2-Qt.AppImage")],
                f"{HOME}/Emulation/tools/launchers": [
                    _entry("pcsx2-qt.sh", path=f"{HOME}/Emulation/tools/launchers/pcsx2-qt.sh"),
                ],
            }
        )
        assert set(result.labels_for_platform("ps2")) == {"PCSX2 (AppImage)", "PCSX2 (EmuDeck)"}
