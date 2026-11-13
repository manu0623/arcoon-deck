"""The emulator collection's backend half, against a fake Deck and a fake SGDB.

What is pinned here is the part Steam cannot answer: which rows exist, which app id
each already has, and what happens when SteamGridDB has nothing to give. The art
tests deliberately cover the misses, because a miss must never cost a shortcut.
"""

from __future__ import annotations

import logging
from typing import Any

import pytest

from domain.emulator_registry import DetectionHints, EmulatorDef, InstalledEmulator
from services.emulator_shortcuts import BINDINGS_KEY, EmulatorShortcutConfig, EmulatorShortcutService

DOLPHIN = EmulatorDef(
    id="dolphin",
    display_name="Dolphin",
    family="dolphin",
    platforms=("gc",),
    hints=DetectionHints(flatpak_ids=("org.DolphinEmu.dolphin-emu",)),
)

PPSSPP = EmulatorDef(
    id="ppsspp",
    display_name="PPSSPP",
    family="ppsspp",
    platforms=("psp",),
    hints=DetectionHints(appimage_prefixes=("ppsspp",), flatpak_ids=("org.ppsspp.PPSSPP",)),
)


class _Scanner:
    def __init__(self) -> None:
        self.rows = [
            InstalledEmulator(
                definition=PPSSPP, provider="native", path="/home/deck/Applications/PPSSPP.AppImage"
            ),
            InstalledEmulator(definition=PPSSPP, provider="flatpak", path="org.ppsspp.PPSSPP"),
            # An emulator SteamGridDB's fake below has never heard of, for the
            # no-match branch: the art search is by name, so it can come back empty.
            InstalledEmulator(definition=DOLPHIN, provider="flatpak", path="org.DolphinEmu.dolphin-emu"),
        ]

    def installs(self) -> list[InstalledEmulator]:
        return list(self.rows)


class _Persister:
    def __init__(self) -> None:
        self.saves = 0

    def save_settings(self) -> None:
        self.saves += 1


class _Sgdb:
    """SGDB with one game, one grid image, and a switch to refuse everything."""

    def __init__(self) -> None:
        self.paths: list[str] = []
        self.downloads: list[str] = []

    def request(self, path: str) -> dict[str, Any] | None:
        self.paths.append(path)
        if path.startswith("/search/autocomplete/"):
            return {"success": True, "data": [{"id": 9001}] if "PPSSPP" in path else []}
        return {"success": True, "data": [{"url": "https://cdn.example/art.png"}]}

    def download_image(self, url: str, dest_path: str) -> bool:
        self.downloads.append(url)
        with open(dest_path, "wb") as handle:
            handle.write(b"\x89PNG fake")
        return True


@pytest.fixture()
def service() -> tuple[EmulatorShortcutService, dict[str, Any], _Persister, _Sgdb]:
    settings: dict[str, Any] = {"steamgriddb_api_key": "key"}
    persister = _Persister()
    sgdb = _Sgdb()
    built = EmulatorShortcutService(
        config=EmulatorShortcutConfig(
            logger=logging.getLogger("test_emulator_shortcuts"),
            external_emulators=_Scanner(),
            sgdb_api=sgdb,
            settings=settings,
            settings_persister=persister,
        )
    )
    return built, settings, persister, sgdb


class TestTheCatalogue:
    def test_it_offers_both_installs_of_one_emulator(self, service) -> None:
        built, _, _, _ = service

        answer = built.catalogue()

        assert answer["collection"] == "Emulators"
        assert [row["key"] for row in answer["emulators"]] == [
            "dolphin@flatpak",
            "ppsspp@native",
            "ppsspp@flatpak",
        ]
        assert [row["app_id"] for row in answer["emulators"]] == [None, None, None]

    def test_it_states_the_app_id_a_row_already_became(self, service) -> None:
        built, settings, _, _ = service
        settings[BINDINGS_KEY] = {"ppsspp@native": 4242}

        answer = built.catalogue()

        assert {row["key"]: row["app_id"] for row in answer["emulators"]} == {
            "dolphin@flatpak": None,
            "ppsspp@native": 4242,
            "ppsspp@flatpak": None,
        }

    def test_a_binding_of_the_wrong_shape_is_ignored(self, service) -> None:
        """The settings file is user-editable; a string id is not one of ours."""
        built, settings, _, _ = service
        settings[BINDINGS_KEY] = {"ppsspp@native": "4242"}

        answer = built.catalogue()

        assert [row["app_id"] for row in answer["emulators"]] == [None, None, None]


class TestTheBindings:
    def test_binding_persists_the_map(self, service) -> None:
        built, settings, persister, _ = service

        result = built.bind("ppsspp@native", 4242)

        assert result == {"success": True, "key": "ppsspp@native", "app_id": 4242}
        assert settings[BINDINGS_KEY] == {"ppsspp@native": 4242}
        assert persister.saves == 1

    def test_a_key_this_machine_does_not_offer_is_refused(self, service) -> None:
        built, settings, persister, _ = service

        result = built.bind("ps4@native", 1)

        assert result == {"success": False, "reason": "unknown_emulator"}
        assert BINDINGS_KEY not in settings
        assert persister.saves == 0

    def test_forgetting_a_stale_binding_removes_only_it(self, service) -> None:
        built, settings, _, _ = service
        settings[BINDINGS_KEY] = {"ppsspp@native": 4242, "ppsspp@flatpak": 4243}

        built.forget("ppsspp@native")

        assert settings[BINDINGS_KEY] == {"ppsspp@flatpak": 4243}

    def test_forgetting_a_key_that_was_never_bound_says_so(self, service) -> None:
        built, _, persister, _ = service

        assert built.forget("ppsspp@native") == {"success": True, "forgotten": False}
        assert persister.saves == 0


class TestTheArtwork:
    @pytest.mark.asyncio
    async def test_it_searches_by_name_then_fetches_the_asset(self, service) -> None:
        built, _, _, sgdb = service

        answer = await built.artwork("ppsspp@native", 3)

        assert answer["base64"] is not None
        assert sgdb.paths == ["/search/autocomplete/PPSSPP", "/grids/game/9001?dimensions=460x215,920x430"]
        assert sgdb.downloads == ["https://cdn.example/art.png"]

    @pytest.mark.asyncio
    async def test_no_api_key_is_reported_rather_than_searched(self, service) -> None:
        built, settings, _, sgdb = service
        settings["steamgriddb_api_key"] = ""

        answer = await built.artwork("ppsspp@native", 1)

        assert answer == {"base64": None, "no_api_key": True}
        assert sgdb.paths == []

    @pytest.mark.asyncio
    async def test_a_name_with_no_match_is_no_art(self, service) -> None:
        built, _, _, _ = service

        answer = await built.artwork("dolphin@flatpak", 1)

        assert answer["base64"] is None

    @pytest.mark.asyncio
    async def test_an_unknown_emulator_is_refused(self, service) -> None:
        built, _, _, sgdb = service

        answer = await built.artwork("ps4@native", 1)

        assert answer == {"base64": None, "no_api_key": False, "reason": "unknown_emulator"}
        assert sgdb.paths == []

    @pytest.mark.asyncio
    async def test_an_unknown_asset_type_is_refused(self, service) -> None:
        built, _, _, sgdb = service

        answer = await built.artwork("ppsspp@native", 9)

        assert answer == {"base64": None, "no_api_key": False, "reason": "unknown_asset_type"}
        assert sgdb.paths == []
