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


def _dotted(token: str) -> str:
    """``gba`` → ``.gba``, ``.GBA`` → ``.gba``; the accept-list's one spelling."""
    lowered = token.lower()
    return lowered if lowered.startswith(".") else f".{lowered}"


class OwnedCatalogueAdapter:
    """Answer emulator questions from the plugin's own inventory."""

    def __init__(
        self,
        *,
        plugin_dir: str,
        user_home: str,
        logger: logging.Logger,
        cores_dir: Callable[[], str],
        runtime_is_builtin: Callable[[], bool],
    ) -> None:
        self._plugin_dir = plugin_dir
        self._user_home = user_home
        self._logger = logger
        self._cores_dir = cores_dir
        self._runtime_is_builtin = runtime_is_builtin
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
                platform,
                core_installed=self._core_installed,
                binary_for=self._binary_for,
                flatpak_for=self._flatpak_for,
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
        """The accept-list the document declares, empty when it knows no such system.

        Tokens are dot-prefixed here, because the document stores them bare (``gba``)
        and every reader compares them against ``os.path.splitext`` output (``.gba``)
        — ES-DE's own list is dot-prefixed, so the two sources answer in one shape.
        Normalising at this seam rather than in the document keeps the file readable
        and keeps the inventory's one reader the only place that knows the spelling
        (ADR-0041).
        """
        inventory = self._parsed()
        if inventory is None:
            return frozenset()
        platform = inventory.get(system_name.lower())
        if platform is None:
            return frozenset()
        return frozenset(_dotted(token) for token in platform.extensions)

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
        if not self._runtime_is_builtin():
            return True
        cores = self._cores_dir()
        return bool(cores) and os.path.isfile(os.path.join(cores, f"{core_so}.so"))

    def _flatpak_for(self, emulator: InventoryEmulator) -> str | None:
        """The ``flatpak`` executable when the entry's app id is installed, else ``None``.

        Read from the two install trees rather than by running ``flatpak list``: the
        picker asks on every menu open, and a subprocess per row is a price a directory
        probe does not charge. A system-wide install and a per-user one both count, and
        the executable is named absolutely when it is there because the launcher's ``PATH``
        is Steam's, not a login shell's.
        """
        app_id = emulator.flatpak
        if not app_id:
            return None
        installed = any(
            os.path.isdir(os.path.join(root, "flatpak", "app", app_id))
            for root in ("/var/lib", os.path.join(self._user_home, ".local", "share"))
        )
        if not installed:
            return None
        return "/usr/bin/flatpak" if os.path.isfile("/usr/bin/flatpak") else "flatpak"

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
    """Answer from the plugin's own inventory or ES-DE's catalogue, in the runtime's order.

    Which tier answers first is decided per call by ``owned_first``, because it follows the
    runtime rather than the device: a **built-in** runtime owns its cores and its launch, so
    the shipped inventory is asked first and ES-DE is the fallback (ADR-0045) — the app does
    not go looking for RetroDECK's catalogue to answer a question it can answer itself. A
    **RetroDECK** runtime flips both, because RetroDECK's catalogue is the only place its own
    core labels exist.

    A question the first tier refuses — it could not be read at all — passes to the second,
    and an answer that is empty but valid (a system the catalogue lists with no bakeable
    command) also passes, because a platform with nothing to launch with is exactly the case
    the other tier exists for.
    """

    def __init__(
        self,
        *,
        esde: Any,
        owned: OwnedCatalogueAdapter,
        owned_first: Callable[[], bool],
    ) -> None:
        self._esde = esde
        self._owned = owned
        self._owned_first = owned_first

    def reset_cache(self) -> None:
        self._esde.reset_cache()
        self._owned.reset_cache()

    def _tiers(self) -> tuple[Any, Any]:
        """``(first, second)`` for this call, per the runtime that is driving."""
        return (self._owned, self._esde) if self._owned_first() else (self._esde, self._owned)

    def get_emulator_options(self, system_name: str) -> dict[str, Any]:
        first, second = self._tiers()
        answer = first.get_emulator_options(system_name)
        if answer["available"] and answer["options"]:
            return answer
        other = second.get_emulator_options(system_name)
        return other if other["options"] else answer

    def get_default_emulator(self, system_name: str) -> EmulatorInvocation | None:
        first, second = self._tiers()
        return first.get_default_emulator(system_name) or second.get_default_emulator(system_name)

    def get_active_core(self, system_name: str) -> tuple[str | None, str | None]:
        first, second = self._tiers()
        core_so, label = first.get_active_core(system_name)
        if core_so is not None:
            return (core_so, label)
        return second.get_active_core(system_name)

    def get_supported_extensions(self, system_name: str) -> frozenset[str]:
        first, second = self._tiers()
        extensions = first.get_supported_extensions(system_name)
        return extensions if extensions else second.get_supported_extensions(system_name)

    def is_known_system(self, system_name: str) -> bool | None:
        first, second = self._tiers()
        known = first.is_known_system(system_name)
        return known if known is not None else second.is_known_system(system_name)

    def system_supports_m3u(self, system_name: str) -> bool:
        """True iff either source accepts ``.m3u`` for the system (see the extensions rule)."""
        return ".m3u" in self.get_supported_extensions(system_name)
