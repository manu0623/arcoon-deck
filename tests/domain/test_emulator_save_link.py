"""The plan for pointing a standalone emulator at the plugin's save tree.

Both sides of the link are computed rather than spelled out: the emulator's folder from
its provider's config root, the plugin's from the platform's own layout. That is what
these tests pin, along with the three ways a plan can be ``None``.
"""

from __future__ import annotations

from domain.emulator_registry import ALL_PLATFORMS, DetectionHints, EmulatorDef, InstalledEmulator
from domain.emulator_save_link import link_for, linked_save_families, links_emulator
from domain.save_bank import SaveFamily

PPSSPP = EmulatorDef(
    id="ppsspp",
    display_name="PPSSPP",
    family="ppsspp",
    platforms=("psp",),
    hints=DetectionHints(appimage_prefixes=("ppsspp",), flatpak_ids=("org.ppsspp.PPSSPP",)),
)

DOLPHIN = EmulatorDef(
    id="dolphin",
    display_name="Dolphin",
    family="dolphin",
    platforms=("gc",),
    hints=DetectionHints(flatpak_ids=("org.DolphinEmu.dolphin-emu",)),
)

RETROARCH = EmulatorDef(
    id="retroarch",
    display_name="RetroArch",
    family="retroarch",
    platforms=(ALL_PLATFORMS,),
    hints=DetectionHints(flatpak_ids=("org.libretro.RetroArch",)),
)

AZAHAR = EmulatorDef(
    id="azahar",
    display_name="Azahar",
    family="citra",
    platforms=("n3ds",),
    hints=DetectionHints(flatpak_ids=("org.azahar_emu.Azahar",)),
)

CITRA = EmulatorDef(
    id="citra",
    display_name="Citra",
    family="citra",
    platforms=("n3ds",),
    hints=DetectionHints(flatpak_ids=("org.citra_emu.citra",)),
)

SAVES = "/home/deck/.local/share/romm-tender/saves"


def _install(definition: EmulatorDef, provider: str, path: str) -> InstalledEmulator:
    return InstalledEmulator(definition=definition, provider=provider, path=path)  # type: ignore[arg-type]


class TestTheTwoSides:
    def test_a_native_install_is_pointed_from_its_xdg_config_root(self) -> None:
        link = link_for(
            _install(PPSSPP, "native", "/home/deck/Applications/PPSSPP.AppImage"),
            config_root="/home/deck/.config/ppsspp",
            saves_root=SAVES,
        )

        assert link is not None
        assert link.emulator_dir == "/home/deck/.config/ppsspp/PSP/SAVEDATA"
        assert link.owned_dir == f"{SAVES}/psp/PSP/SAVEDATA"
        assert (link.emulator, link.provider, link.platform) == ("ppsspp", "native", "psp")

    def test_a_flatpak_install_is_pointed_inside_its_own_sandbox(self) -> None:
        link = link_for(
            _install(PPSSPP, "flatpak", "org.ppsspp.PPSSPP"),
            config_root="/home/deck/.var/app/org.ppsspp.PPSSPP/config/ppsspp",
            saves_root=SAVES,
        )

        assert link is not None
        assert link.emulator_dir == "/home/deck/.var/app/org.ppsspp.PPSSPP/config/ppsspp/PSP/SAVEDATA"


class TestTheRefusals:
    def test_a_family_with_no_declared_save_folder_is_not_linked(self) -> None:
        """Dolphin's cards are not this change's business, and naming a folder for it
        would be a link nothing asked for."""
        assert (
            link_for(
                _install(DOLPHIN, "flatpak", "org.DolphinEmu.dolphin-emu"),
                config_root="/home/deck/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu",
                saves_root=SAVES,
            )
            is None
        )

    def test_a_retroarch_install_is_not_linked(self) -> None:
        """Its own appendconfig already redirects it; a second redirect would fight it."""
        assert (
            link_for(
                _install(RETROARCH, "flatpak", "org.libretro.RetroArch"),
                config_root="/home/deck/.var/app/org.libretro.RetroArch/config/retroarch",
                saves_root=SAVES,
            )
            is None
        )

    def test_an_emudeck_launcher_does_not_get_a_link(self) -> None:
        """Its record is a script, not an install: linking a flatpak sandbox for it
        created one for an emulator that had never been launched."""
        assert (
            link_for(
                _install(PPSSPP, "emudeck", "/home/deck/Emulation/tools/launchers/ppsspp.sh"),
                config_root="/home/deck/.var/app/org.ppsspp.PPSSPP/config/ppsspp",
                saves_root=SAVES,
            )
            is None
        )

    def test_no_config_root_means_no_plan(self) -> None:
        assert (
            link_for(
                _install(PPSSPP, "native", "/home/deck/Applications/PPSSPP.AppImage"),
                config_root="",
                saves_root=SAVES,
            )
            is None
        )

    def test_no_saves_root_means_no_plan(self) -> None:
        assert (
            link_for(
                _install(PPSSPP, "native", "/home/deck/Applications/PPSSPP.AppImage"),
                config_root="/home/deck/.config/ppsspp",
                saves_root="",
            )
            is None
        )


class TestTheDataRoot:
    """Azahar keeps its NAND beside its data, so the link hangs off the data root.

    Measured on the reference Deck: ``config/azahar-emu/qt-config.ini`` holds the
    settings while ``data/azahar-emu/{nand,sdmc}`` holds everything the console writes,
    and the save tree is ``sdmc/Nintendo 3DS`` — the same shape the bank's n3ds layout
    reads, level for level.
    """

    def test_a_flatpak_install_is_pointed_from_its_data_root(self) -> None:
        link = link_for(
            _install(AZAHAR, "flatpak", "org.azahar_emu.Azahar"),
            config_root="/home/deck/.var/app/org.azahar_emu.Azahar/config/azahar-emu",
            data_root="/home/deck/.var/app/org.azahar_emu.Azahar/data/azahar-emu",
            saves_root=SAVES,
        )

        assert link is not None
        assert link.emulator_dir == ("/home/deck/.var/app/org.azahar_emu.Azahar/data/azahar-emu/sdmc/Nintendo 3DS")
        assert link.owned_dir == f"{SAVES}/3ds/sdmc/Nintendo 3DS"
        assert (link.emulator, link.family, link.platform) == ("azahar", "citra", "n3ds")

    def test_a_data_root_emulator_handed_no_data_root_is_not_guessed_at(self) -> None:
        """Falling back to the config root would point at ``config/azahar-emu/sdmc``,
        a directory the emulator never reads."""
        assert (
            link_for(
                _install(AZAHAR, "flatpak", "org.azahar_emu.Azahar"),
                config_root="/home/deck/.var/app/org.azahar_emu.Azahar/config/azahar-emu",
                saves_root=SAVES,
            )
            is None
        )

    def test_a_config_root_emulator_ignores_the_data_root(self) -> None:
        link = link_for(
            _install(PPSSPP, "native", "/home/deck/Applications/PPSSPP.AppImage"),
            config_root="/home/deck/.config/ppsspp",
            data_root="/home/deck/.local/share/ppsspp",
            saves_root=SAVES,
        )

        assert link is not None
        assert link.emulator_dir == "/home/deck/.config/ppsspp/PSP/SAVEDATA"

    def test_an_unmeasured_sibling_of_the_same_family_is_not_linked(self) -> None:
        """Citra shares Azahar's save format and not its directory, and only Azahar's
        was verified — a row for Citra would be a claim about a path nobody read."""
        assert (
            link_for(
                _install(CITRA, "flatpak", "org.citra_emu.citra"),
                config_root="/home/deck/.var/app/org.citra_emu.citra/config/citra-emu",
                data_root="/home/deck/.var/app/org.citra_emu.citra/data/citra-emu",
                saves_root=SAVES,
            )
            is None
        )


class TestWhoIsPointed:
    def test_the_save_layer_knows_the_linked_emulators(self) -> None:
        # ``EmulatorInvocation.emulator`` is a definition id, which is what the table is
        # keyed by — so a launch answers without going through the registry.
        assert links_emulator("ppsspp") is True
        assert links_emulator("azahar") is True
        assert links_emulator("citra") is False
        assert links_emulator(None) is False

    def test_the_covered_bank_families_come_from_the_table(self) -> None:
        """The bank's own vocabulary: the shape a platform's save has, which is what a
        caller holding only a platform slug can ask about."""
        assert linked_save_families() == frozenset({SaveFamily.PREFIX_BUNDLE, SaveFamily.N3DS_TITLE})
