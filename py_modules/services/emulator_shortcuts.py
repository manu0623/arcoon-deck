"""The emulator collection's backend half: what to add, and the art to dress it in.

Steam is the only thing that can create a shortcut or a collection, so the
frontend does both (``src/utils/emulatorShortcuts.ts``). What it cannot do is know
which emulators exist on this machine, or fetch SteamGridDB art for them — those
are here.

**Bindings live in settings, keyed by the shortcut's key**, so a second run finds
the shortcut it made last time instead of creating a second tile for the same
emulator. A binding whose app id Steam no longer has is stale (the shortcut was
deleted, or Steam's store was rebuilt) and the frontend clears it by creating the
row again — which is why the map is a hint, not the truth.

**The art is best-effort by design.** SteamGridDB is searched by the emulator's
name, so "PPSSPP" gives a real tile and something obscure gives nothing; a missing
key, a no-match, or a failed download all mean "no art", never "no shortcut". The
shortcut is the feature; the picture is what makes it fit beside the games.

**An asset already on disk is answered, not fetched.** Steam's grid directory is the
truth for "does this tile carry art": a file there costs one presence check, where
re-fetching would spend a SteamGridDB request and a download on every plugin mount.
That is what lets the frontend ask for art on a tile it did not create this run — 13
tiles bound before the art existed would otherwise keep the default tile forever.
"""

from __future__ import annotations

import asyncio
import base64
import os
import tempfile
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Protocol
from urllib.parse import quote

from domain.artwork_paths import asset_grid_filenames
from domain.emulator_shortcut import EmulatorShortcut, shortcuts
from domain.sgdb_artwork import asset_type_name, sgdb_endpoint_path

if TYPE_CHECKING:
    import logging

    from domain.emulator_registry import InstalledEmulator

COLLECTION_NAME = "Emulators"
"""The collection's own name. The frontend machine-scopes it, like every other."""

BINDINGS_KEY = "emulator_shortcuts"
"""The settings key holding ``{shortcut key: steam app id}``."""

API_KEY_SETTING = "steamgriddb_api_key"


class InstallsReader(Protocol):
    """The scanner, as this service needs it: every install, whatever the system."""

    def installs(self) -> list[InstalledEmulator]: ...


class SgdbReader(Protocol):
    """The two SteamGridDB calls the art search makes."""

    def request(self, path: str) -> dict[str, Any] | None: ...

    def download_image(self, url: str, dest_path: str) -> bool: ...


class SettingsPersister(Protocol):
    """What a written binding needs to survive a restart."""

    def save_settings(self) -> None: ...


class GridDirReader(Protocol):
    """Steam's grid directory, as the presence check needs it."""

    def grid_dir(self) -> str | None: ...


@dataclass(frozen=True)
class EmulatorShortcutConfig:
    """Everything this service is handed at construction.

    No loop: the art fetch asks for the running one when it needs it, so a caller
    cannot hand this service a loop that is not the one its coroutine runs on.
    """

    logger: logging.Logger
    external_emulators: InstallsReader
    sgdb_api: SgdbReader
    settings: dict[str, Any]
    settings_persister: SettingsPersister
    #: Steam's grid directory. ``None`` means "cannot tell", and every asset is then
    #: fetched as before — a missing answer must never look like "already applied".
    grid_dir: GridDirReader | None = None


class EmulatorShortcutService:
    """Which emulators deserve a tile, which app ids they already have, and their art."""

    def __init__(self, *, config: EmulatorShortcutConfig) -> None:
        self._logger = config.logger
        self._external_emulators = config.external_emulators
        self._sgdb_api = config.sgdb_api
        self._settings = config.settings
        self._settings_persister = config.settings_persister
        self._grid_dir = config.grid_dir

    # ── reading ──────────────────────────────────────────────────────────────

    def catalogue(self) -> dict[str, Any]:
        """The emulators to offer, each with the app id it already has (or ``None``).

        Synchronous on purpose: it reads the scanner's cache and the settings dict,
        so a surface can draw a list without waiting on the network.
        """
        bindings = self._bindings()
        return {
            "collection": COLLECTION_NAME,
            "emulators": [{**asdict(row), "app_id": bindings.get(row.key)} for row in self._rows()],
        }

    def _rows(self) -> list[EmulatorShortcut]:
        return shortcuts(self._external_emulators.installs())

    def _bindings(self) -> dict[str, int]:
        raw = self._settings.get(BINDINGS_KEY)
        if not isinstance(raw, dict):
            return {}
        # Anything that is not an int did not come from this service; ignoring it
        # is cheaper than trusting it enough to type-check every caller.
        return {key: value for key, value in raw.items() if isinstance(key, str) and isinstance(value, int)}

    # ── writing ──────────────────────────────────────────────────────────────

    def bind(self, key: str, app_id: int) -> dict[str, Any]:
        """Remember which shortcut this key's tile became.

        A key this machine does not offer is refused rather than stored: a binding
        no catalogue row can claim is one nobody can ever use or clear.
        """
        if not any(row.key == key for row in self._rows()):
            return {"success": False, "reason": "unknown_emulator"}

        bindings = self._bindings()
        bindings[key] = int(app_id)
        self._settings[BINDINGS_KEY] = bindings
        self._settings_persister.save_settings()
        return {"success": True, "key": key, "app_id": int(app_id)}

    def forget(self, key: str) -> dict[str, Any]:
        """Drop a binding whose shortcut Steam no longer has."""
        bindings = self._bindings()
        if key not in bindings:
            return {"success": True, "forgotten": False}
        del bindings[key]
        self._settings[BINDINGS_KEY] = bindings
        self._settings_persister.save_settings()
        return {"success": True, "forgotten": True}

    # ── artwork ──────────────────────────────────────────────────────────────

    async def artwork(self, key: str, asset_type_num: int) -> dict[str, Any]:
        """SteamGridDB art for one emulator, as base64 PNG, or why there is none.

        Runs the network on the executor like every other adapter call here: the
        SGDB client is synchronous, and a 30-second image fetch is not something
        the plugin's event loop can afford to sit through.
        """
        return await asyncio.get_running_loop().run_in_executor(None, self._artwork_blocking, key, asset_type_num)

    def _artwork_blocking(self, key: str, asset_type_num: int) -> dict[str, Any]:
        no_key = not self._settings.get(API_KEY_SETTING, "")
        if no_key:
            return {"base64": None, "no_api_key": True}

        name = asset_type_name(asset_type_num)
        if name is None:
            return {"base64": None, "no_api_key": False, "reason": "unknown_asset_type"}

        row = next((candidate for candidate in self._rows() if candidate.key == key), None)
        if row is None:
            return {"base64": None, "no_api_key": False, "reason": "unknown_emulator"}

        if self._already_applied(key, name):
            return {"base64": None, "no_api_key": False, "present": True}

        sgdb_id = row.sgdb_id if row.sgdb_id is not None else self._search_game_id(row.search_term)
        if sgdb_id is None:
            return {"base64": None, "no_api_key": False, "reason": "no_match"}

        path = sgdb_endpoint_path(name, sgdb_id)
        if path is None:
            return {"base64": None, "no_api_key": False, "reason": "unknown_asset_type"}

        url = self._first_asset_url(path)
        if url is None:
            return {"base64": None, "no_api_key": False, "reason": "no_asset"}

        return {"base64": self._download_base64(url), "no_api_key": False}

    def _already_applied(self, key: str, asset_type: str) -> bool:
        """Whether the bound tile already carries this asset, read off Steam's grid dir.

        Three answers mean "cannot tell, so fetch": no ``grid_dir`` handed in, no
        binding for this key (no tile to dress yet), and an asset type in no grid form.
        """
        if self._grid_dir is None:
            return False
        app_id = self._bindings().get(key)
        if app_id is None:
            return False
        directory = self._grid_dir.grid_dir()
        if not directory:
            return False
        names = asset_grid_filenames(asset_type, app_id)
        return any(os.path.exists(os.path.join(directory, name)) for name in names)

    def _search_game_id(self, term: str) -> int | None:
        """SteamGridDB's best guess at the emulator, by name.

        Autocomplete rather than an exact match: SGDB's entries are games and its
        hit for "PPSSPP" is called "PPSSPP" sometimes and "PPSSPP Gold" others, and
        the first row is the most popular name match either way.

        The guess is wrong where a game shares the emulator's name and outranks it, which
        is why an emulator may state its SGDB id instead — the caller prefers that one.
        """
        try:
            found = self._sgdb_api.request(f"/search/autocomplete/{quote(term)}")
        except Exception as exc:  # a failed search is no art, not a failed sync
            self._logger.warning(f"Emulator artwork: SGDB search for {term!r} failed: {exc}")
            return None
        rows = (found or {}).get("data") or []
        if not rows:
            return None
        game_id = rows[0].get("id")
        return int(game_id) if isinstance(game_id, int) else None

    def _first_asset_url(self, path: str) -> str | None:
        try:
            result = self._sgdb_api.request(path)
        except Exception as exc:
            self._logger.warning(f"Emulator artwork: SGDB asset request {path} failed: {exc}")
            return None
        assets = (result or {}).get("data") or []
        if not assets:
            return None
        url = assets[0].get("url")
        return url if isinstance(url, str) else None

    def _download_base64(self, url: str) -> str | None:
        """The image as base64, through a temp file the adapter can write to.

        The adapter downloads to a path, and Steam takes art as base64 — a temp
        file is the seam between them, and it is removed before returning even when
        the read fails.
        """
        with tempfile.TemporaryDirectory(prefix="emulator-art-") as directory:
            path = f"{directory}/art.png"
            if not self._sgdb_api.download_image(url, path):
                return None
            try:
                with open(path, "rb") as handle:
                    return base64.b64encode(handle.read()).decode("ascii")
            except OSError as exc:
                self._logger.warning(f"Emulator artwork: could not read {path}: {exc}")
                return None
