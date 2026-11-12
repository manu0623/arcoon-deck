"""External installs joined to a platform's picker, without changing what launches.

The two properties worth pinning are that a row is *provider-qualified* (so the pick
names an install, not just an emulator) and that adding rows never moves the default:
`select_default_option` must still answer with ES-DE's first bakeable entry.
"""

from __future__ import annotations

from domain.emulator_commands import options_to_payload, select_default_option
from domain.emulator_picker import (
    EXTERNAL_LAUNCHER_REASON,
    external_option,
    external_options,
    with_external,
)
from domain.emulator_registry import InstalledEmulator, definition


def _install(emulator_id: str, provider: str, path: str) -> InstalledEmulator:
    found = definition(emulator_id)
    assert found is not None
    return InstalledEmulator(definition=found, provider=provider, path=path)


def _catalogue_row(label: str):
    """A bakeable ES-DE libretro row — the shape the catalogue supplies."""
    from domain.emulator_commands import classify_command

    return classify_command(label, "%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/snes9x_libretro.so %ROM%")


class TestExternalOption:
    def test_the_label_is_provider_qualified(self) -> None:
        row = external_option(_install("eden", "native", "/home/deck/Applications/Eden.appimage"))
        assert row.label == "Eden (AppImage)"

    def test_two_providers_are_two_rows(self) -> None:
        installs = [
            _install("pcsx2", "emudeck", "/home/deck/Emulation/tools/launchers/pcsx2-qt.sh"),
            _install("pcsx2", "native", "/home/deck/Applications/pcsx2-Qt.AppImage"),
        ]
        labels = [row.label for row in external_options(installs, "ps2")]
        assert labels == ["PCSX2 (EmuDeck)", "PCSX2 (AppImage)"]

    def test_the_row_is_listed_but_not_launchable(self) -> None:
        row = external_option(_install("eden", "native", "/home/deck/Applications/Eden.appimage"))
        assert row.status == "needs_setup"
        assert row.reason == EXTERNAL_LAUNCHER_REASON
        assert row.kind == "standalone"
        assert row.core_so is None

    def test_the_identity_is_the_definition_not_the_label(self) -> None:
        """Firmware answers are keyed on the emulator, which two providers share."""
        installs = [
            _install("pcsx2", "emudeck", "/home/deck/Emulation/tools/launchers/pcsx2-qt.sh"),
            _install("pcsx2", "native", "/home/deck/Applications/pcsx2-Qt.AppImage"),
        ]
        assert {row.emulator for row in external_options(installs, "ps2")} == {"pcsx2"}

    def test_the_command_names_the_binary_and_the_rom_placeholder(self) -> None:
        row = external_option(_install("ryujinx", "native", "/home/deck/Applications/ryujinx.AppImage"))
        assert row.command == '"/home/deck/Applications/ryujinx.AppImage" %ROM%'


class TestScope:
    def test_only_installs_that_play_the_platform(self) -> None:
        installs = [
            _install("eden", "native", "/home/deck/Applications/Eden.appimage"),
            _install("duckstation", "native", "/home/deck/Applications/DuckStation.AppImage"),
        ]
        assert [row.label for row in external_options(installs, "switch")] == ["Eden (AppImage)"]

    def test_retroarch_is_not_offered_for_a_platform_with_no_cores(self) -> None:
        installs = [_install("retroarch", "flatpak", "org.libretro.RetroArch")]
        assert external_options(installs, "switch") == []
        assert [row.label for row in external_options(installs, "gba")] == ["RetroArch (Flatpak)"]

    def test_two_builds_of_one_emulator_are_one_row(self) -> None:
        installs = [
            _install("rpcs3", "native", "/home/deck/Applications/rpcs3.AppImage"),
            _install("rpcs3", "native", "/home/deck/Applications/rpcs3.AppImage_old"),
        ]
        assert [row.label for row in external_options(installs, "ps3")] == ["RPCS3 (AppImage)"]


class TestMerge:
    def test_externals_come_after_the_catalogue(self) -> None:
        catalogue = [_catalogue_row("mGBA")]
        merged = with_external(catalogue, external_options([_install("mgba", "flatpak", "io.mgba.mGBA")], "gba"))
        assert [row.label for row in merged] == ["mGBA", "mGBA (Flatpak)"]

    def test_a_label_the_catalogue_already_offers_is_not_duplicated(self) -> None:
        catalogue = [_catalogue_row("Eden (AppImage)")]
        merged = with_external(catalogue, external_options([_install("eden", "native", "/x/Eden.appimage")], "switch"))
        assert [row.label for row in merged] == ["Eden (AppImage)"]
        assert merged[0].status == "bakeable"

    def test_an_empty_inventory_changes_nothing(self) -> None:
        catalogue = [_catalogue_row("Snes9x - Current")]
        assert with_external(catalogue, []) == catalogue


class TestTheDefaultNeverMoves:
    def test_the_catalogue_default_still_wins(self) -> None:
        catalogue = [_catalogue_row("mGBA")]
        merged = with_external(catalogue, external_options([_install("mgba", "flatpak", "io.mgba.mGBA")], "gba"))
        chosen = select_default_option(merged)
        assert chosen is not None
        assert chosen.label == "mGBA"

    def test_externals_alone_make_no_default(self) -> None:
        """With nothing bakeable from ES-DE, the platform still plain-launches."""
        merged = with_external([], external_options([_install("mgba", "flatpak", "io.mgba.mGBA")], "gba"))
        assert select_default_option(merged) is None

    def test_the_payload_says_not_bakeable_with_the_reason(self) -> None:
        merged = with_external([], external_options([_install("mgba", "flatpak", "io.mgba.mGBA")], "gba"))
        payload = options_to_payload(merged)
        assert payload[0]["bakeable"] is False
        assert payload[0]["reason"] == EXTERNAL_LAUNCHER_REASON
        assert payload[0]["label"] == "mGBA (Flatpak)"
        assert payload[0]["emulator"] == "mgba"
