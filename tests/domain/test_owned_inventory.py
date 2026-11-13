"""The plugin's own inventory: parsing, option building, and what a missing piece does."""

from __future__ import annotations

from domain.emulator_commands import select_default_option
from domain.owned_inventory import (
    host_command,
    libretro_command,
    options_for,
    parse_inventory,
    platform_names,
)

_DOC = {
    "platforms": {
        "switch": {
            "aliases": ["nx"],
            "extensions": ["NSP", "xci"],
            "emulators": [
                {
                    "label": "Eden (Standalone)",
                    "id": "eden",
                    "kind": "standalone",
                    "host": {
                        "binaries": ["~/Applications/Eden.AppImage"],
                        "args": ["-f", "-g"],
                        "flatpak": "io.github.eden_emulator.Eden",
                    },
                },
                {"label": "Ryujinx", "id": "ryujinx", "kind": "libretro", "core": "ryujinx_libretro"},
            ],
        },
        "psx": {
            "aliases": ["ps1"],
            "extensions": ["cue", "chd"],
            "emulators": [
                {"label": "Beetle PSX HW", "id": "beetle", "kind": "libretro", "core": "mednafen_psx_hw_libretro"}
            ],
        },
    }
}


_FLATPAK_DOC = {
    "platforms": {
        "gc": {
            "extensions": ["iso"],
            "emulators": [
                {
                    "label": "Dolphin (Standalone)",
                    "id": "dolphin",
                    "kind": "standalone",
                    "host": {
                        "binaries": ["~/Applications/Dolphin.AppImage"],
                        "args": ["-b", "-e"],
                        "flatpak": "org.DolphinEmu.dolphin-emu",
                    },
                }
            ],
        }
    }
}


class TestReadingTheDocument:
    def test_a_platform_answers_to_its_own_name_and_every_alias(self) -> None:
        inventory = parse_inventory(_DOC)
        assert inventory["switch"] is inventory["nx"]
        assert inventory["ps1"] is inventory["psx"]

    def test_extensions_are_lowercased_for_membership_checks(self) -> None:
        assert parse_inventory(_DOC)["switch"].extensions == ("nsp", "xci")

    def test_the_names_are_what_the_inventory_describes(self) -> None:
        assert platform_names(parse_inventory(_DOC)) == {"switch", "nx", "psx", "ps1"}

    def test_a_malformed_emulator_is_skipped_not_fatal(self) -> None:
        document = {
            "platforms": {
                "gc": {
                    "emulators": [
                        {"label": "", "kind": "libretro", "core": "x_libretro"},
                        {"label": "No core", "kind": "libretro"},
                        {"label": "Unknown kind", "kind": "cloud"},
                        {"label": "Dolphin", "kind": "libretro", "core": "dolphin_libretro"},
                    ]
                }
            }
        }
        emulators = parse_inventory(document)["gc"].emulators
        assert [e.label for e in emulators] == ["Dolphin"]

    def test_a_platform_with_no_usable_emulator_is_not_registered(self) -> None:
        assert parse_inventory({"platforms": {"gc": {"emulators": [{"label": "x", "kind": "cloud"}]}}}) == {}

    def test_a_nonsense_document_reads_as_empty_rather_than_raising(self) -> None:
        assert parse_inventory("not a document") == {}
        assert parse_inventory({"platforms": []}) == {}


class TestTheCommandsAnEntryBecomes:
    def test_a_libretro_entry_takes_the_es_de_shape(self) -> None:
        assert libretro_command("mgba_libretro") == (
            "%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/mgba_libretro.so %ROM%"
        )

    def test_a_standalone_entry_runs_the_binary_on_the_host(self) -> None:
        assert host_command("/apps/Eden.AppImage", ["-f", "-g"]) == (
            "%EMULATOR_FLATPAK-SPAWN% --host /apps/Eden.AppImage -f -g %ROM%"
        )

    def test_an_argument_carrying_a_placeholder_is_dropped(self) -> None:
        # It would be read as an unresolvable placeholder by the bake rules.
        assert host_command("/apps/X", ["--mode=%CONFIG%"]) == "%EMULATOR_FLATPAK-SPAWN% --host /apps/X %ROM%"


class TestWhatThePickerOffers:
    def _options(self, *, core_ok: bool = True, binary: str | None = "/apps/Eden.AppImage"):
        inventory = parse_inventory(_DOC)
        return options_for(
            inventory["switch"],
            core_installed=lambda core: core_ok,
            binary_for=lambda emulator: binary,
        )

    def test_the_inventory_order_decides_the_default(self) -> None:
        assert select_default_option(self._options()).label == "Eden (Standalone)"

    def test_a_found_binary_is_bakeable(self) -> None:
        assert [o.status for o in self._options()] == ["bakeable", "bakeable"]

    def test_a_missing_binary_keeps_the_row_and_says_why(self) -> None:
        eden = self._options(binary=None)[0]
        assert (eden.status, eden.reason) == ("needs_setup", "not_installed")

    def test_a_missing_binary_hands_the_default_to_the_next_entry(self) -> None:
        assert select_default_option(self._options(binary=None)).label == "Ryujinx"

    def test_a_missing_core_downgrades_the_libretro_row(self) -> None:
        row = self._options(core_ok=False)[1]
        assert (row.status, row.reason) == ("needs_setup", "not_installed")

    def test_nothing_installed_selects_no_default(self) -> None:
        assert select_default_option(self._options(core_ok=False, binary=None)) is None


class TestFlatpakInstalledEmulators:
    """An emulator installed as a Flatpak is launchable, not missing."""

    def _options(self, *, binary: str | None = None, flatpak: str | None = None):
        inventory = parse_inventory(_FLATPAK_DOC)
        return options_for(
            inventory["gc"],
            core_installed=lambda _core: True,
            binary_for=lambda _emulator: binary,
            flatpak_for=lambda _emulator: flatpak,
        )

    def test_the_document_carries_the_app_id(self) -> None:
        assert parse_inventory(_FLATPAK_DOC)["gc"].emulators[0].flatpak == "org.DolphinEmu.dolphin-emu"

    def test_a_flatpak_install_is_launchable_without_a_binary(self) -> None:
        row = self._options(flatpak="/usr/bin/flatpak")[0]
        assert (row.status, row.reason) == ("bakeable", None)
        assert row.command == (
            "%EMULATOR_FLATPAK-SPAWN% --host /usr/bin/flatpak run org.DolphinEmu.dolphin-emu -b -e %ROM%"
        )

    def test_a_binary_outranks_the_flatpak(self) -> None:
        row = self._options(binary="/apps/Dolphin.AppImage", flatpak="/usr/bin/flatpak")[0]
        assert row.command.startswith("%EMULATOR_FLATPAK-SPAWN% --host /apps/Dolphin.AppImage")

    def test_installed_nowhere_still_says_why(self) -> None:
        row = self._options()[0]
        assert (row.status, row.reason) == ("needs_setup", "not_installed")
