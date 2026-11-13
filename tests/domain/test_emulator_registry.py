"""The external-emulator registry, pinned against the filenames a real Deck holds.

Every filename in the identification cases was read off a live Steam Deck's
``~/Applications`` directory, so these tests fail if the registry stops recognising
what EmuDeck actually installs there.
"""

from __future__ import annotations

import pytest

from domain.emulator_registry import (
    ALL_PLATFORMS,
    RETROARCH_ID,
    EmulatorDef,
    InstalledEmulator,
    Provider,
    all_definitions,
    dedupe,
    definition,
    for_platform,
    identify,
    identify_flatpak,
    identify_launcher,
    labels,
    platforms_for,
)


def _install(
    emulator_id: str,
    provider: Provider = "native",
    path: str | None = None,
    *,
    size: int | None = 100,
    modified: str | None = "2026-10-21",
) -> InstalledEmulator:
    found = definition(emulator_id)
    assert found is not None, f"registry has no {emulator_id!r}"
    return InstalledEmulator(
        definition=found,
        provider=provider,
        path=path or f"/home/deck/Applications/{emulator_id}.AppImage",
        size=size,
        modified=modified,
    )


class TestIdentify:
    """Filename → definition, against the Deck's real filenames."""

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("Eden.appimage", "eden"),
            ("eden.appimage", "eden"),
            ("Eden-NX2.AppImage", "eden"),
            ("pcsx2-Qt.AppImage", "pcsx2"),
            ("DuckStation.AppImage", "duckstation"),
            ("rpcs3.AppImage", "rpcs3"),
            ("rpcs3.AppImage_old", "rpcs3"),
            ("Cemu.AppImage", "cemu"),
            ("azahar.AppImage", "azahar"),
            ("Shadps4-qt.AppImage", "shadps4"),
            ("Citron.AppImage", "citron"),
            ("yuzu.appimage", "yuzu"),
            ("ryujinx.AppImage", "ryujinx"),
            ("Vita3K", "vita3k"),
            ("publish/Ryujinx", "ryujinx"),
            ("Freegosy.appimage", None),
            ("EmuDeck.AppImage", None),
        ],
    )
    def test_identifies_by_prefix(self, filename: str, expected: str | None) -> None:
        found = identify(filename)
        assert (found.id if found is not None else None) == expected

    def test_citron_is_not_citra(self) -> None:
        """A shared prefix must not swallow a different emulator."""
        citron = identify("Citron.AppImage")
        citra = identify("citra-qt.AppImage")
        assert citron is not None and citra is not None
        assert citron.id == "citron"
        assert citra.id == "citra"

    def test_a_name_merely_containing_an_emulator_is_not_an_install(self) -> None:
        assert identify("my-eden-notes.txt") is None

    def test_empty_name_identifies_nothing(self) -> None:
        assert identify("") is None
        assert identify("/home/deck/Applications/") is None


class TestIdentifyProviderSurfaces:
    def test_launcher_names_resolve(self) -> None:
        for script, expected in (
            ("pcsx2-qt.sh", "pcsx2"),
            ("dolphin-emu.sh", "dolphin"),
            ("/home/deck/Emulation/tools/launchers/azahar.sh", "azahar"),
        ):
            found = identify_launcher(script)
            assert found is not None, script
            assert found.id == expected

    def test_emudeck_ships_no_eden_launcher(self) -> None:
        """Pinned because it is the reason Eden is detected as a binary, not a script."""
        assert identify_launcher("eden.sh") is None

    def test_flatpak_ids_resolve(self) -> None:
        for app_id, expected in (
            ("org.libretro.RetroArch", RETROARCH_ID),
            ("org.DolphinEmu.dolphin-emu", "dolphin"),
            # Measured on the reference Deck: the plugin installed this flatpak and then
            # could not see it, because the definition named no flatpak id at all.
            ("net.pcsx2.PCSX2", "pcsx2"),
        ):
            found = identify_flatpak(app_id)
            assert found is not None, app_id
            assert found.id == expected
        assert identify_flatpak("org.example.Unrelated") is None


class TestDedupe:
    def test_identical_builds_collapse_to_one_entry(self) -> None:
        """The Deck's two Edens: same bytes, different filename case."""
        installs = [
            _install("eden", path="/home/deck/Applications/Eden.appimage", size=70075388),
            _install("eden", path="/home/deck/Applications/eden.appimage", size=70075388),
        ]
        survivors = dedupe(installs)
        assert len(survivors) == 1
        assert survivors[0].path == "/home/deck/Applications/Eden.appimage"
        assert survivors[0].aliases == ("/home/deck/Applications/eden.appimage",)

    def test_different_builds_stay_separate(self) -> None:
        """rpcs3.AppImage_old beside rpcs3.AppImage is two versions, not a duplicate."""
        installs = [
            _install("rpcs3", path="/home/deck/Applications/rpcs3.AppImage", size=94685173),
            _install("rpcs3", path="/home/deck/Applications/rpcs3.AppImage_old", size=97156175),
        ]
        assert len(dedupe(installs)) == 2

    def test_the_survivor_does_not_depend_on_listing_order(self) -> None:
        first = [
            _install("dolphin", path="/home/deck/Applications/b-dolphin.AppImage"),
            _install("dolphin", path="/home/deck/Applications/a-dolphin.AppImage"),
        ]
        reversed_order = list(reversed(first))
        assert dedupe(first)[0].path == dedupe(reversed_order)[0].path

    def test_distinct_emulators_are_never_collapsed(self) -> None:
        installs = [_install("eden"), _install("citron"), _install("yuzu")]
        assert len(dedupe(installs)) == 3

    def test_the_same_build_from_two_providers_stays_two_installs(self) -> None:
        """A provider's launcher and a direct AppImage are two things to run."""
        installs = [
            _install("pcsx2", provider="emudeck", path="/launchers/pcsx2-qt.sh"),
            _install("pcsx2", provider="native", path="/Applications/pcsx2-Qt.AppImage"),
        ]
        assert len(dedupe(installs)) == 2


class TestLabels:
    def test_label_is_provider_qualified(self) -> None:
        assert _install("pcsx2", provider="emudeck").label == "PCSX2 (EmuDeck)"
        assert _install("pcsx2", provider="retrodeck").label == "PCSX2 (RetroDECK)"

    def test_two_providers_are_two_distinct_picks(self) -> None:
        """The whole point of qualification: one name per save root."""
        emudeck = _install("pcsx2", provider="emudeck")
        retrodeck = _install("pcsx2", provider="retrodeck")
        assert emudeck.label != retrodeck.label

    def test_two_builds_of_one_provider_share_a_pick(self) -> None:
        installs = [
            _install("rpcs3", provider="emudeck", path="/a/rpcs3.AppImage", size=1),
            _install("rpcs3", provider="emudeck", path="/a/rpcs3.AppImage_old", size=2),
        ]
        assert labels(installs) == ["RPCS3 (EmuDeck)"]


class TestPlatforms:
    def test_retroarch_claims_every_platform_with_a_core(self) -> None:
        retroarch = _install(RETROARCH_ID, provider="flatpak")
        assert retroarch.plays("snes")
        assert retroarch.plays("ps2")
        assert platforms_for(RETROARCH_ID) == (ALL_PLATFORMS,)

    @pytest.mark.parametrize("platform", ["switch", "wiiu", "ps3", "psvita", "xbox", "xbox360", "ps4"])
    def test_retroarch_is_not_offered_where_no_core_exists(self, platform: str) -> None:
        retroarch = _install(RETROARCH_ID, provider="flatpak")
        assert not retroarch.plays(platform)

    def test_for_platform_selects_by_declared_platforms(self) -> None:
        installs = [_install("pcsx2", provider="emudeck"), _install("dolphin", provider="flatpak")]
        ids = {install.id for install in for_platform(installs, "ps2")}
        assert ids == {"pcsx2"}

    def test_the_switch_lineage_is_all_offered(self) -> None:
        installs = [_install(name) for name in ("eden", "citron", "yuzu", "ryujinx", "sudachi")]
        families = {install.definition.family for install in for_platform(installs, "switch")}
        assert families == {"yuzu", "ryujinx"}

    def test_unknown_emulator_claims_no_platforms(self) -> None:
        assert platforms_for("nonexistent") == ()


class TestRegistryIntegrity:
    def test_ids_are_unique(self) -> None:
        ids = [item.id for item in all_definitions()]
        assert len(ids) == len(set(ids))

    def test_every_definition_declares_at_least_one_probe(self) -> None:
        for item in all_definitions():
            hints = item.hints
            probes = (
                *hints.appimage_prefixes,
                *hints.binary_prefixes,
                *hints.launcher_names,
                *hints.flatpak_ids,
            )
            assert probes, f"{item.id} declares no detection hint"

    def test_every_definition_declares_a_platform(self) -> None:
        for item in all_definitions():
            assert item.platforms, f"{item.id} declares no platform"

    def test_families_are_lowercase_slugs(self) -> None:
        for item in all_definitions():
            assert item.family == item.family.strip().lower()

    def test_switch_definitions_split_into_two_families(self) -> None:
        """The save-format boundary, stated once: yuzu-line vs Ryujinx-line."""
        switch_families = {item.family for item in all_definitions() if "switch" in item.platforms}
        assert switch_families == {"yuzu", "ryujinx"}

    def test_definition_lookup(self) -> None:
        assert isinstance(definition("eden"), EmulatorDef)
        assert definition("nope") is None
