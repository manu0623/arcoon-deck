"""Locating an install's settings file, by provider, with the filesystem faked.

The provider roots asserted here are the ones measured on the reference Deck: EmuDeck's
PCSX2 settings in ``~/.config/PCSX2``, RetroDECK's in its own flatpak sandbox, the
flatpak RetroArch in ``~/.var/app/org.libretro.RetroArch/config/retroarch``.
"""

from __future__ import annotations

import pytest

from adapters.emulator_config import EmulatorConfigReader
from domain.emulator_registry import InstalledEmulator, definition

HOME = "/home/deck"
RA_FLATPAK = f"{HOME}/.var/app/org.libretro.RetroArch/config/retroarch/retroarch.cfg"
PCSX2_XDG = f"{HOME}/.config/PCSX2/inis/PCSX2.ini"
PCSX2_RETRODECK = f"{HOME}/.var/app/net.retrodeck.retrodeck/config/PCSX2/inis/PCSX2.ini"
PCSX2_PORTABLE = f"{HOME}/Applications/inis/PCSX2.ini"
DOLPHIN_FLATPAK = f"{HOME}/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Dolphin.ini"
DOLPHIN_XDG = f"{HOME}/.config/dolphin-emu/Dolphin.ini"


def _install(emulator_id: str, provider: str, path: str) -> InstalledEmulator:
    found = definition(emulator_id)
    assert found is not None
    return InstalledEmulator(definition=found, provider=provider, path=path)  # type: ignore[arg-type]


def _reader(files: dict[str, str], *, errors: dict[str, str] | None = None) -> EmulatorConfigReader:
    def read_text(path: str) -> str:
        if errors and path in errors:
            raise OSError(errors[path])
        return files[path]

    return EmulatorConfigReader(user_home=HOME, read_text=read_text, exists=lambda path: path in files)


class TestProviderRoots:
    def test_flatpak_reads_inside_its_sandbox(self) -> None:
        install = _install("retroarch", "flatpak", "org.libretro.RetroArch")
        read = _reader({RA_FLATPAK: 'savefile_directory = "/run/media/deck/SR01T/saves"\n'}).read(install)
        assert read.path == RA_FLATPAK
        assert read.values["savefile_directory"] == "/run/media/deck/SR01T/saves"
        assert read.roots is not None
        assert read.roots.config == f"{HOME}/.var/app/org.libretro.RetroArch/config/retroarch"
        assert read.note is None

    def test_native_reads_xdg_config(self) -> None:
        install = _install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage")
        read = _reader({PCSX2_XDG: "[Folders]\nMemoryCards = /saves\n"}).read(install)
        assert read.path == PCSX2_XDG
        assert read.roots is not None
        assert read.roots.config == f"{HOME}/.config/PCSX2"
        assert read.roots.data == f"{HOME}/.local/share/PCSX2"

    def test_retrodeck_reads_inside_the_shared_sandbox(self) -> None:
        install = _install("pcsx2", "retrodeck", "retroarch")
        read = _reader(
            {PCSX2_RETRODECK: "[Folders]\nMemoryCards = /home/deck/retrodeck/saves/ps2/pcsx2/memcards\n"}
        ).read(install)
        assert read.path == PCSX2_RETRODECK
        assert read.values["Folders/MemoryCards"] == "/home/deck/retrodeck/saves/ps2/pcsx2/memcards"

    def test_emudeck_appimage_reads_xdg(self) -> None:
        install = _install("pcsx2", "emudeck", f"{HOME}/Emulation/tools/launchers/pcsx2-qt.sh")
        read = _reader({PCSX2_XDG: "[Folders]\nMemoryCards = /saves\n"}).read(install)
        assert read.path == PCSX2_XDG

    def test_emudeck_flatpak_install_reads_the_sandbox(self) -> None:
        """EmuDeck's Dolphin is the flatpak, not an AppImage."""
        install = _install("dolphin", "emudeck", f"{HOME}/Emulation/tools/launchers/dolphin-emu.sh")
        read = _reader({DOLPHIN_FLATPAK: "[Core]\nSlotA = 8\n"}).read(install)
        assert read.path == DOLPHIN_FLATPAK

    def test_emudeck_falls_back_to_xdg_when_the_sandbox_has_no_file(self) -> None:
        install = _install("dolphin", "emudeck", f"{HOME}/Emulation/tools/launchers/dolphin-emu.sh")
        read = _reader({DOLPHIN_XDG: "[Core]\nSlotA = 8\n"}).read(install)
        assert read.path == DOLPHIN_XDG

    def test_a_flatpak_definition_without_an_app_id_uses_xdg(self) -> None:
        """Only definitions that declare a flatpak id may probe a sandbox."""
        install = _install("eden", "emudeck", f"{HOME}/Emulation/tools/launchers/eden.sh")
        paths = [path for path, _roots in _reader({}).candidates(install)]
        assert all(".var/app" not in path for path in paths)


class TestPortableMode:
    def test_settings_beside_the_appimage_win(self) -> None:
        install = _install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage")
        read = _reader(
            {PCSX2_PORTABLE: "[Folders]\nMemoryCards = /portable\n", PCSX2_XDG: "[Folders]\nMemoryCards = /xdg\n"}
        ).read(install)
        assert read.path == PCSX2_PORTABLE
        assert read.values["Folders/MemoryCards"] == "/portable"

    def test_a_portable_file_carries_xdg_roots(self) -> None:
        install = _install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage")
        read = _reader({PCSX2_PORTABLE: "[Folders]\nMemoryCards = /portable\n"}).read(install)
        assert read.roots is not None
        assert read.roots.data == f"{HOME}/.local/share/PCSX2"

    def test_a_launcher_script_is_not_a_portable_directory(self) -> None:
        """EmuDeck's launcher path names a script, so nothing sits beside it."""
        install = _install("pcsx2", "emudeck", f"{HOME}/Emulation/tools/launchers/pcsx2-qt.sh")
        paths = [path for path, _roots in _reader({}).candidates(install)]
        assert f"{HOME}/Emulation/tools/launchers/inis/PCSX2.ini" not in paths


class TestFormats:
    def test_melonds_toml(self) -> None:
        path = f"{HOME}/.config/melonDS/melonDS.toml"
        install = _install("melonds", "native", f"{HOME}/Applications/melonDS.AppImage")
        read = _reader({path: '[Save]\nSavePath = "/saves"\n'}).read(install)
        assert read.values["Save/SavePath"] == "/saves"

    def test_ryujinx_json(self) -> None:
        path = f"{HOME}/.config/Ryujinx/Config.json"
        install = _install("ryujinx", "native", f"{HOME}/Applications/ryujinx.AppImage")
        read = _reader({path: '{"Saves": {"SaveRoot": "/saves"}}'}).read(install)
        assert read.values["Saves/SaveRoot"] == "/saves"

    def test_cemu_xml(self) -> None:
        path = f"{HOME}/.config/Cemu/settings.xml"
        install = _install("cemu", "native", f"{HOME}/Applications/Cemu.AppImage")
        read = _reader({path: "<settings><Save><Dir>/saves</Dir></Save></settings>"}).read(install)
        assert read.values["settings/Save/Dir"] == "/saves"


class TestFailures:
    def test_no_settings_file_reports_the_reason(self) -> None:
        install = _install("duckstation", "native", f"{HOME}/Applications/DuckStation.AppImage")
        read = _reader({}).read(install)
        assert read.path is None
        assert read.values == {}
        assert read.note == "no-settings-file"
        assert read.found is False

    def test_yaml_is_refused_before_any_file_is_opened(self) -> None:
        """RPCS3's config.yml is not parsed; an empty dict must not look like success."""
        install = _install("rpcs3", "native", f"{HOME}/Applications/rpcs3.AppImage")
        read = _reader({f"{HOME}/.config/rpcs3/config.yml": "Miscellaneous:\n  Foo: 1\n"}).read(install)
        assert read.note == "format-unreadable"
        assert read.values == {}
        assert read.found is False

    def test_an_unreadable_file_says_so(self) -> None:
        install = _install("duckstation", "native", f"{HOME}/Applications/DuckStation.AppImage")
        path = f"{HOME}/.local/share/duckstation/settings.ini"
        read = _reader({path: ""}, errors={path: "Permission denied"}).read(install)
        assert read.note is not None
        assert read.note.startswith("unreadable:")
        assert read.path == path

    def test_values_for_returns_no_roots_when_nothing_was_read(self) -> None:
        reader = _reader({})
        values, roots, note = reader.values_for(
            _install("duckstation", "native", f"{HOME}/Applications/DuckStation.AppImage")
        )
        assert values == {}
        assert roots is None
        assert note == "no-settings-file"

    def test_values_for_returns_roots_on_success(self) -> None:
        reader = _reader({PCSX2_XDG: "[Folders]\nMemoryCards = /saves\n"})
        values, roots, note = reader.values_for(_install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage"))
        assert values["Folders/MemoryCards"] == "/saves"
        assert roots is not None
        assert note is None


class TestAgainstTheSaveResolver:
    def test_a_read_config_answers_the_save_root(self) -> None:
        """The seam end to end: adapter values in, resolved save root out."""
        from domain.save_locations import ResolvedSaveRoot, resolve

        reader = _reader({PCSX2_XDG: f"[Folders]\nMemoryCards = {HOME}/SD/saves\n"})
        install = _install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage")
        values, roots, _note = reader.values_for(install)
        assert roots is not None
        answer = resolve(
            family="pcsx2",
            platform="ps2",
            values=values,
            home=HOME,
            data=roots.data,
            config=roots.config,
            exists=lambda _path: False,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{HOME}/SD/saves"
        assert answer.source == "config"

    def test_no_config_falls_back_to_the_declared_default(self) -> None:
        from domain.save_locations import ResolvedSaveRoot, resolve

        reader = _reader({})
        install = _install("pcsx2", "native", f"{HOME}/Applications/pcsx2-Qt.AppImage")
        values, _roots, _note = reader.values_for(install)
        answer = resolve(
            family="pcsx2",
            platform="ps2",
            values=values,
            home=HOME,
            data=f"{HOME}/.config/PCSX2",
            exists=lambda _path: False,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{HOME}/.config/PCSX2/memcards"
        assert answer.source == "default"

    @pytest.mark.parametrize(
        ("emulator_id", "provider", "path"),
        [
            ("eden", "native", f"{HOME}/Applications/Eden.appimage"),
            ("yuzu", "emudeck", f"{HOME}/Emulation/tools/launchers/yuzu.sh"),
            ("ryujinx", "native", f"{HOME}/Applications/ryujinx.AppImage"),
        ],
    )
    def test_every_switch_emulator_can_be_asked(self, emulator_id: str, provider: str, path: str) -> None:
        """Each Switch family resolves to *some* answer, configured or defaulted."""
        from domain.save_locations import resolve

        reader = _reader({})
        install = _install(emulator_id, provider, path)
        values, _roots, _note = reader.values_for(install)
        answer = resolve(
            family=install.definition.family,
            platform="switch",
            values=values,
            home=HOME,
            data=f"{HOME}/.local/share/{install.definition.id}",
            exists=lambda _path: False,
        )
        assert not hasattr(answer, "reason"), answer
