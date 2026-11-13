"""Where a standalone emulator comes from: the plan, its preference, and its ambiguity rule."""

from __future__ import annotations

import json
import os

from domain.emulator_install import (
    FlatpakInstall,
    ReleaseInstall,
    download_url,
    install_plan,
    matching_asset,
)
from domain.owned_inventory import parse_inventory

_DOC = {
    "platforms": {
        "gc": {
            "extensions": ["iso"],
            "emulators": [
                {
                    "label": "Dolphin (Standalone)",
                    "id": "dolphin",
                    "kind": "standalone",
                    "host": {"binaries": ["~/Applications/Dolphin.AppImage"], "flatpak": "org.DolphinEmu.dolphin-emu"},
                    "install": {"flatpak": "org.DolphinEmu.dolphin-emu"},
                }
            ],
        },
        "psp": {
            "extensions": ["iso"],
            "emulators": [
                {
                    "label": "PPSSPP (Standalone)",
                    "id": "ppsspp",
                    "kind": "standalone",
                    "host": {"binaries": ["~/Applications/PPSSPP.AppImage"]},
                    "install": {
                        "flatpak": "org.ppsspp.PPSSPP",
                        "github": {"repo": "hrydgard/ppsspp", "asset": "PPSSPP-*-anylinux-x86_64.AppImage"},
                    },
                },
                {"label": "PPSSPP (libretro)", "id": "ppsspp", "kind": "libretro", "core": "ppsspp_libretro"},
            ],
        },
        "switch": {
            "extensions": ["nsp"],
            "emulators": [
                {
                    "label": "Eden (Standalone)",
                    "id": "eden",
                    "kind": "standalone",
                    "host": {"binaries": ["~/Applications/Eden.AppImage"], "flatpak": "io.github.eden_emulator.Eden"},
                    "install": {"github": {"repo": "eden-emulator/Releases", "asset": "Eden-Linux-*-amd64-*.AppImage"}},
                }
            ],
        },
    }
}


def _emulator(platform: str, label_prefix: str):
    platform_doc = parse_inventory(_DOC)[platform]
    return next(entry for entry in platform_doc.emulators if entry.label.startswith(label_prefix))


class TestThePlan:
    def test_a_store_build_is_one_unattended_command(self) -> None:
        plan = install_plan(_emulator("gc", "Dolphin"))

        assert isinstance(plan, FlatpakInstall)
        assert plan.argv == ("flatpak", "install", "--user", "-y", "flathub", "org.DolphinEmu.dolphin-emu")

    def test_a_release_states_the_endpoint_not_a_tag(self) -> None:
        plan = install_plan(_emulator("switch", "Eden"))

        assert isinstance(plan, ReleaseInstall)
        assert plan.release_api == "https://api.github.com/repos/eden-emulator/Releases/releases/latest"
        assert plan.asset_pattern == "Eden-Linux-*-amd64-*.AppImage"

    def test_a_row_with_both_prefers_the_release(self) -> None:
        """The store copy is only as current as its last manifest bump (ADR-0049)."""
        plan = install_plan(_emulator("psp", "PPSSPP (Standalone)"))

        assert isinstance(plan, ReleaseInstall)

    def test_the_store_build_can_be_asked_for(self) -> None:
        plan = install_plan(_emulator("psp", "PPSSPP (Standalone)"), prefer_newest=False)

        assert isinstance(plan, FlatpakInstall)
        assert plan.app_id == "org.ppsspp.PPSSPP"

    def test_the_store_build_answers_when_it_is_the_only_source(self) -> None:
        plan = install_plan(_emulator("psp", "PPSSPP (Standalone)"), prefer_newest=False)

        assert isinstance(plan, FlatpakInstall)

    def test_a_libretro_core_is_not_installed_here(self) -> None:
        """Cores are the core provisioner's work; this module only fetches programs."""
        assert install_plan(_emulator("psp", "PPSSPP (libretro)")) is None


class TestARowWithoutASource:
    def test_no_install_block_is_not_a_plan(self) -> None:
        document = {"platforms": {"gc": _DOC["platforms"]["gc"]}}
        document["platforms"]["gc"] = json.loads(json.dumps(document["platforms"]["gc"]))
        del document["platforms"]["gc"]["emulators"][0]["install"]

        emulator = parse_inventory(document)["gc"].emulators[0]

        assert install_plan(emulator) is None

    def test_a_block_that_names_nothing_is_dropped_at_parse(self) -> None:
        document = json.loads(json.dumps(_DOC))
        document["platforms"]["gc"]["emulators"][0]["install"] = {"flatpak": "", "github": {}}

        emulator = parse_inventory(document)["gc"].emulators[0]

        assert emulator.install is None
        assert install_plan(emulator) is None


class TestTheAmbiguityRule:
    def test_one_match_is_the_asset(self) -> None:
        names = ["PPSSPP-v1.20.4-anylinux-x86_64.AppImage", "PPSSPP-v1.20.4-anylinux-aarch64.AppImage"]

        found = matching_asset(names, "PPSSPP-*-anylinux-x86_64.AppImage")

        assert found == "PPSSPP-v1.20.4-anylinux-x86_64.AppImage"

    def test_two_matches_are_refused(self) -> None:
        """An x86_64 build beside a v3 one is a CPU decision this module may not make."""
        names = ["eden-amd64.AppImage", "eden-amd64-v3.AppImage"]

        assert matching_asset(names, "eden-amd64*.AppImage") is None

    def test_no_match_is_none(self) -> None:
        assert matching_asset(["eden-arm64.AppImage"], "eden-amd64*.AppImage") is None

    def test_the_tag_is_carried_into_the_url(self) -> None:
        url = download_url("hrydgard/ppsspp", "v1.20.4", "PPSSPP-v1.20.4-anylinux-x86_64.AppImage")

        assert url == (
            "https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/"
            "PPSSPP-v1.20.4-anylinux-x86_64.AppImage"
        )


class TestTheShippedDocument:
    """The real inventory, because a JSON typo would only surface at install time."""

    def _document(self) -> dict:
        path = os.path.join(os.path.dirname(__file__), "..", "..", "defaults", "emulator_inventory.json")
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def _standalone(self, inventory: dict) -> list:
        platforms = {id(entry): entry for entry in inventory.values()}.values()
        return [row for platform in platforms for row in platform.emulators if row.kind == "standalone"]

    def test_every_named_source_resolves_to_a_plan(self) -> None:
        rows = self._standalone(parse_inventory(self._document()))
        named = [row for row in rows if row.install is not None]

        assert named, "the shipped inventory states no source at all"
        unresolved = [row.label for row in named if install_plan(row) is None]
        assert not unresolved, unresolved

    def test_a_row_without_a_source_stays_honest(self) -> None:
        """Eden is the measured case: its GitHub mirror answers 451, so it is manual."""
        rows = self._standalone(parse_inventory(self._document()))

        manual = [row.label for row in rows if row.install is None]

        assert manual == ["Eden (Standalone)"], manual

    def test_the_platforms_that_must_be_installable_carry_a_source(self) -> None:
        inventory = parse_inventory(self._document())

        for system in ("gc", "wii", "ps2", "psp", "psx", "switch", "ps3", "n3ds", "wiiu"):
            platform = inventory[system]
            sources = [emulator for emulator in platform.emulators if install_plan(emulator) is not None]

            assert sources, f"{system} has no emulator the plugin can install"
