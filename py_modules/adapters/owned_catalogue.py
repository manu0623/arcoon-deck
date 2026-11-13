"""The plugin's own emulator inventory adapter, and the fallback that reads it last.

The inventory document ships with the plugin (``emulator_inventory.json``, flattened to
the plugin root by the Decky CLI and read from ``defaults/`` on a dev deploy — the same
two-location rule ``config.json`` follows). This adapter turns it into the answers the
picker and the resolver already ask for, and it is only ever consulted when ES-DE's
catalogue cannot answer: RetroDECK absent, ``es_systems.xml`` unreadable, or a system the
catalogue does not list.

Two device facts are probed, never assumed: whether an owned core is on disk (in the
runtime's own cores directory) and whether a standalone emulator's binary was found under
one of the paths the inventory lists. A ``RETRODECK`` runtime answers "installed" for every
core, because its RetroArch ships with its own cores.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from domain.emulator_commands import EmulatorOption, option_to_invocation, select_default_option
from domain.owned_inventory import (
    InventoryEmulator,
    InventoryPlatform,
    options_for,
    parse_inventory,
    platform_names,
)

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.shortcut_data import EmulatorInvocation

DOCUMENT_NAME = "emulator_inventory.json"

#: The picker's "emulator list unavailable" answer, built fresh so no caller can mutate
#: another's list.
def _unavailable() -> dict[str, Any]:
    return {"available": False, "options": []}


class OwnedCatalogueAdapter:
    """Answer emulator questions from the plugin's own inventory."""

    def __init__(
        self,
        *,
        plugin_dir: str,
        user_home: str,
        logger: logging.Logger,
        cores_dir: Callable[[], str],
        runtime_is_standalone: Callable[[], bool],
    ) -> None:
        self._plugin_dir = plugin_dir
        self._user_home = user_home
        self._logger = logger
        self._cores_dir = cores_dir
        self._runtime_is_standalone = runtime_is_standalone
        self._inventory: dict[str, InventoryPlatform] | None = None

    def reset_cache(self) -> None:
        """Drop the parsed inventory so the next answer re-reads the document."""
        self._inventory = None

    # -- public API (mirrors AtlasCatalogueAdapter) --------------------------

    def get_emulator_options(self, system_name: str) -> dict[str, Any]:
        """Classified options for *system_name*, or ``available: False`` with no document.

        An unknown system is ``available: True`` with an empty list — the document was
        read, and it really does not name this system, which is a different statement
        from "nothing could be read".
        """
        inventory = self._parsed()
        if inventory is None:
            return _unavailable()
        platform = inventory.get(system_name.lower())
        if platform is None:
            return {"available": True, "options": []}
        return {
            "available": True,
            "options": options_for(
                platform, core_installed=self._core_installed, binary_for=self._binary_for
            ),
        }

    def get_default_emulator(self, system_name: str) -> EmulatorInvocation | None:
        """The first bakeable inventory entry rendered into an invocation, else ``None``."""
        result = self.get_emulator_options(system_name)
        if not result["available"]:
            return None
        options: list[EmulatorOption] = result["options"]
        return option_to_invocation(select_default_option(options))

    def get_active_core(self, system_name: str) -> tuple[str | None, str | None]:
        """The first libretro entry's ``(core_so, label)``, bakeable or not."""
        result = self.get_emulator_options(system_name)
        if not result["available"]:
            return (None, None)
        for option in result["options"]:
            if option.kind == "libretro" and option.core_so:
                return (option.core_so, option.label)
        return (None, None)

    def platform_for(self, system_name: str) -> InventoryPlatform | None:
        """The inventory entry for *system_name*, or ``None`` when no document names it.

        Exposed because core provisioning needs the platform's own statements (which cores
        back its rows) rather than a projection of them into picker options.
        """
        inventory = self._parsed()
        return None if inventory is None else inventory.get(system_name.lower())

    def core_installed(self, core_so: str) -> bool:
        """Whether the owned runtime can load *core_so* right now."""
        return self._core_installed(core_so)

    def get_supported_extensions(self, system_name: str) -> frozenset[str]:
        """The accept-list the document declares, empty when it knows no such system."""
        inventory = self._parsed()
        if inventory is None:
            return frozenset()
        platform = inventory.get(system_name.lower())
        return frozenset(platform.extensions) if platform is not None else frozenset()

    def is_known_system(self, system_name: str) -> bool | None:
        """``None`` when no document could be read; else whether it names the system."""
        inventory = self._parsed()
        if inventory is None:
            return None
        return system_name.lower() in platform_names(inventory)

    def system_supports_m3u(self, system_name: str) -> bool:
        """True iff the document lists ``.m3u`` for the system."""
        return ".m3u" in self.get_supported_extensions(system_name)

    # -- helpers -------------------------------------------------------------

    def _document_path(self) -> str:
        root = os.path.join(self._plugin_dir, DOCUMENT_NAME)
        dev = os.path.join(self._plugin_dir, "defaults", DOCUMENT_NAME)
        return root if os.path.exists(root) else dev

    def _parsed(self) -> dict[str, InventoryPlatform] | None:
        """The parsed inventory, or ``None`` when the document is missing or malformed."""
        if self._inventory is not None:
            return self._inventory
        path = self._document_path()
        try:
            with open(path, encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            self._logger.warning(f"owned_inventory: no usable inventory at {path}: {exc}")
            return None
        inventory = parse_inventory(document)
        if not inventory:
            self._logger.warning(f"owned_inventory: {path} declares no usable platform")
            return None
        self._inventory = inventory
        return inventory

    def _core_installed(self, core_so: str) -> bool:
        """Whether a libretro core can be loaded, which depends on which runtime drives.

        A RetroDECK runtime is never asked: its RetroArch and its cores live inside its
        own flatpak, where this probe cannot see them, and answering "missing" there
        would disable every libretro row on a working device.
        """
        if not core_so:
            return False
        if not self._runtime_is_standalone():
            return True
        cores = self._cores_dir()
        return bool(cores) and os.path.isfile(os.path.join(cores, f"{core_so}.so"))

    def _binary_for(self, emulator: InventoryEmulator) -> str | None:
        """The first existing binary among the entry's candidates, else ``None``.

        ``~`` is expanded per candidate rather than trusted from the document, so an
        inventory written for one user still resolves on another.
        """
        for candidate in emulator.host_binaries:
            path = os.path.expanduser(candidate)
            if os.path.isfile(path):
                return path
        return None


class FallbackCatalogueAdapter:
    """Answer from ES-DE's catalogue, and from the owned inventory where it cannot.

    The primary is asked first and always wins any question it can answer. A question it
    refuses — the catalogue could not be read at all — passes to the fallback, and an
    answer that is empty but valid (a system the catalogue lists with no bakeable
    command) also passes, because a platform with nothing to launch with is exactly the
    case the inventory exists for.

    Nothing here decides which source is "better": a device with RetroDECK keeps
    answering from ES-DE, and a device without one gets the shipped inventory.
    """

    def __init__(self, *, primary: Any, fallback: OwnedCatalogueAdapter) -> None:
        self._primary = primary
        self._fallback = fallback

    def reset_cache(self) -> None:
        self._primary.reset_cache()
        self._fallback.reset_cache()

    def get_emulator_options(self, system_name: str) -> dict[str, Any]:
        answer = self._primary.get_emulator_options(system_name)
        if answer["available"] and answer["options"]:
            return answer
        owned = self._fallback.get_emulator_options(system_name)
        return owned if owned["options"] else answer

    def get_default_emulator(self, system_name: str) -> EmulatorInvocation | None:
        return self._primary.get_default_emulator(system_name) or self._fallback.get_default_emulator(system_name)

    def get_active_core(self, system_name: str) -> tuple[str | None, str | None]:
        core_so, label = self._primary.get_active_core(system_name)
        if core_so is not None:
            return (core_so, label)
        return self._fallback.get_active_core(system_name)

    def get_supported_extensions(self, system_name: str) -> frozenset[str]:
        extensions = self._primary.get_supported_extensions(system_name)
        return extensions if extensions else self._fallback.get_supported_extensions(system_name)

    def is_known_system(self, system_name: str) -> bool | None:
        known = self._primary.is_known_system(system_name)
        return known if known is not None else self._fallback.is_known_system(system_name)

    def system_supports_m3u(self, system_name: str) -> bool:
        """True iff either source accepts ``.m3u`` for the system (see the extensions rule)."""
        return ".m3u" in self.get_supported_extensions(system_name)
