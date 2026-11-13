"""RetroDECK paths adapter — reads retrodeck.json for path resolution.

Provides path resolution for saves, ROMs, BIOS, and the RetroDECK home
directory. The adapter reads ``retrodeck.json`` (RetroDECK's user-facing
configurator output) once and caches the result for 30 seconds — long
enough to amortize repeated reads during a sync run, short enough to
pick up edits made via the RetroDECK configurator within a single
plugin session.

Path getters are best-effort and never raise: a missing, unreadable, or
malformed ``retrodeck.json`` falls back to ``<user_home>/retrodeck/*``.
On an SD-card install that fallback root is wrong, so the silent
fallback is paired with :meth:`RetroDeckPathsAdapter.config_health`,
the loud signal ``main.py`` surfaces to the frontend banner.

Every root is symlink-resolved, whichever of the two sources answered.
The content roots are handed to the path guards as safe roots, and the
ROM paths those guards are asked about are recorded resolved wherever
``lib.path_safety.safe_join`` built them — so a root left as
``retrodeck.json`` spells it makes one directory look like two on any
system where ``/home`` is a link to ``/var/home``, and a ROM recorded
inside the root is refused as outside it (#1838).

The home is not a safe root, and is resolved for its own reason:
``MigrationService`` diffs it against the home it stored to decide
whether RetroDECK moved, and two spellings of one directory are not a
move.

``realpath`` on a path that is not on disk resolves as far as it can and
normalizes the rest rather than raising, so the getters keep their
best-effort, never-raises contract. Normalizing is not nothing: the
home's ``<user_home>/retrodeck/`` fallback loses its trailing separator,
which is what a prefix match wanted anyway.
"""

from __future__ import annotations

import json
import os
import time
from typing import TYPE_CHECKING, Any

from adapters.flatpak_install import flatpak_app_files_dirs
from domain.runtime import _LEGACY_BUILTIN, RuntimeMode, resolve_mode, resolve_roots
from lib.retrodeck_health import RetroDeckConfigHealth

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Mapping


class RetroDeckPathsAdapter:
    """Adapter for reading RetroDECK path configuration from retrodeck.json."""

    _CACHE_TTL = 30  # seconds

    def __init__(
        self,
        *,
        user_home: str,
        logger: logging.Logger,
        settings: Callable[[], Mapping[str, object]] | None = None,
        data_dir: str = "",
    ) -> None:
        self._user_home = user_home
        self._logger = logger
        # Where the app keeps its own data. The ``APP`` structure answers from it, so a
        # caller that omits it gets the EmuDeck shape rather than a root under the plugin.
        self._data_dir = data_dir
        # The live settings dict, when the caller has one. It carries the runtime choice
        # and any per-root override, so this adapter can answer for a Deck that has no
        # RetroDECK at all — see ``domain.runtime``.
        self._settings = settings
        self._cached_config: dict[str, Any] | None = None
        self._cache_time = 0.0
        # Load outcome that distinguishes "no file" (ABSENT, quiet) from
        # "file present but unreadable" (UNREADABLE, loud). The getters
        # only need the dict-or-None; ``config_health`` needs the reason.
        self._last_load_health: RetroDeckConfigHealth = RetroDeckConfigHealth.ABSENT

    def config_path(self) -> str:
        """Absolute path to ``retrodeck.json`` that this adapter probes."""
        return os.path.join(
            self._user_home,
            ".var",
            "app",
            "net.retrodeck.retrodeck",
            "config",
            "retrodeck",
            "retrodeck.json",
        )

    def _load_config(self) -> dict[str, Any] | None:
        now = time.monotonic()
        if self._cached_config is not None and (now - self._cache_time) < self._CACHE_TTL:
            return self._cached_config
        config_path = self.config_path()
        try:
            with open(config_path) as f:
                config = json.load(f)
            self._cached_config = config
            self._cache_time = now
            self._last_load_health = RetroDeckConfigHealth.OK
            return config
        except FileNotFoundError:
            # Missing file is the expected fallback path (fresh install, no
            # RetroDECK yet) — don't spam the log on every read. A created file
            # is picked up on the next read because the TTL guard tests the
            # cached value before the age, and both failure paths null it; the
            # unset time here is not what buys that.
            self._cached_config = None
            self._last_load_health = RetroDeckConfigHealth.ABSENT
            return None
        except (OSError, json.JSONDecodeError) as exc:
            self._logger.warning(f"Failed to load RetroDECK config at {config_path}: {exc}")
            self._cached_config = None
            self._cache_time = now
            self._last_load_health = RetroDeckConfigHealth.UNREADABLE
            return None

    def _get_path(self, key: str, fallback_subdir: str) -> str:
        """Return the symlink-resolved root for *key*, or its ``~/retrodeck`` fallback."""
        config = self._load_config()
        if config:
            path = config.get("paths", {}).get(key, "")
            if path:
                return os.path.realpath(path)
        return os.path.realpath(os.path.join(self._user_home, "retrodeck", fallback_subdir))

    def runtime_mode(self) -> RuntimeMode:
        """Which runtime this device is driving, from the setting and what is installed.

        ``ROOT_MISSING`` counts as present: the config exists and names a home that is not
        on disk (an ejected card), which is a broken install of something installed — not
        the absent case that hands the roots to the standalone tree.

        **The config alone is not presence.** Uninstalling the RetroDECK flatpak leaves
        ``retrodeck.json`` and ``~/retrodeck`` behind; measured on the reference Deck, that
        made every query answer "RetroDECK is here" and kept the plugin pointed at a
        launcher that no longer existed. So presence is the *app* being installed in either
        flatpak tree, with the config as the second half of the answer.
        """
        setting = None if self._settings is None else self._settings().get("runtime_mode")
        # An explicit choice is the answer, and it is answered without probing: a built-in
        # runtime must not go looking for a RetroDECK it was not asked to use, and a retrodeck
        # one was chosen on purpose. Only ``auto`` (or nothing) needs the machine inspected.
        if setting in (RuntimeMode.BUILTIN, RuntimeMode.RETRODECK, _LEGACY_BUILTIN):
            return resolve_mode(setting, retrodeck_present=False)
        present = self.config_health() in (
            RetroDeckConfigHealth.OK,
            RetroDeckConfigHealth.ROOT_MISSING,
        ) and bool(flatpak_app_files_dirs(self._user_home))
        return resolve_mode(setting, retrodeck_present=present)

    def _owned_root(self, name: str) -> str | None:
        """The standalone tree's root *name*, or ``None`` while RetroDECK drives.

        Resolved the same way the RetroDECK getters are (:func:`os.path.realpath`), so a
        root spelled through ``/home`` does not become a second directory beside the same
        one reached through ``/var/home`` (#1838).
        """
        if self.runtime_mode() is not RuntimeMode.BUILTIN:
            return None
        roots = resolve_roots(
            mode=RuntimeMode.BUILTIN,
            home=self._user_home,
            retrodeck_roots={},
            settings=None if self._settings is None else self._settings(),
            data_dir=self._data_dir,
        )
        return os.path.realpath(getattr(roots, name))

    def bios_path(self) -> str:
        return self._owned_root("bios") or self._get_path("bios_path", "bios")

    def roms_path(self) -> str:
        return self._owned_root("roms") or self._get_path("roms_path", "roms")

    def saves_path(self) -> str:
        return self._owned_root("saves") or self._get_path("saves_path", "saves")

    def states_path(self) -> str:
        return self._owned_root("states") or self._get_path("states_path", "states")

    def cores_path(self) -> str:
        """Where the owned runtime loads cores from, when it is the one driving.

        Empty while RetroDECK drives: its cores live inside its own flatpak and are none
        of this plugin's business.
        """
        return self._owned_root("cores") or ""

    def retrodeck_home(self) -> str:
        return self._get_path("rd_home_path", "")

    def config_health(self) -> RetroDeckConfigHealth:
        """Classify how trustworthy the resolved RetroDECK roots are.

        Reuses the 30-second TTL cache via :meth:`_load_config` — no
        second independent file read within the TTL. Four outcomes:

        - ``ABSENT``: ``retrodeck.json`` not found — the legitimate
          fresh-install case. Wins over ``ROOT_MISSING`` even when the
          ``~/retrodeck`` fallback does not exist on disk, so it stays
          quiet.
        - ``UNREADABLE``: the file exists but could not be read/parsed.
        - ``ROOT_MISSING``: the file read OK but the resolved RetroDECK
          home directory does not exist on disk (e.g. SD card ejected).
        - ``OK``: read OK and the resolved home exists.
        """
        self._load_config()
        # ABSENT wins over the disk probe: ``~/retrodeck`` not existing on
        # a fresh install is expected, not a failure.
        if self._last_load_health in (
            RetroDeckConfigHealth.ABSENT,
            RetroDeckConfigHealth.UNREADABLE,
        ):
            return self._last_load_health
        # Config read OK — probe the resolved home directory on disk.
        if not os.path.isdir(self.retrodeck_home()):
            return RetroDeckConfigHealth.ROOT_MISSING
        return RetroDeckConfigHealth.OK
