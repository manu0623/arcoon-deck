"""The plan for pointing a standalone emulator at the plugin's save tree.

Both sides of the link are computed rather than spelled out: the emulator's folder from
its provider's config root, the plugin's from the platform's own layout. That is what
these tests pin, along with the three ways a plan can be ``None``.
"""

from __future__ import annotations

from domain.emulator_registry import ALL_PLATFORMS, DetectionHints, EmulatorDef, InstalledEmulator
from domain.emulator_save_link import link_for

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
