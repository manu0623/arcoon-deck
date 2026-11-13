"""The plugin's own emulator inventory, for a device with no ES-DE catalogue.

Every emulator the picker offers and every per-platform default comes out of the live
``es_systems.xml`` today. That file is ES-DE's, and it ships with RetroDECK — so on a Deck
where RetroDECK is gone the picker is empty, every platform resolves to no emulator, and
every launch falls back to a launcher that is not there either. The catalogue needs a
second source, one the plugin owns.

This module is that source's pure half: it turns a shipped document into the same
:class:`~domain.emulator_commands.EmulatorOption` values the ES-DE path produces, so
nothing above (picker, per-platform precedence, launch bake) can tell which source
answered. Two rules make that work:

- **A libretro entry is synthesised into the exact ES-DE command shape**
  (``%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/<core>.so %ROM%``) rather than being built
  as an option directly, so the classifier keeps one definition of "libretro".
- **A standalone entry becomes an owned host launch**
  (``%EMULATOR_FLATPAK-SPAWN% --host <binary> -f -g %ROM%``), which is the form the bake
  already renders as bare argv. A standalone emulator is therefore a binary path plus its
  arguments, not a command string that only a sandbox can resolve.

The inventory states nothing it cannot know. Whether a binary exists and whether a core is
installed are facts of the device, not of the document, so they arrive as two injected
predicates and a missing one downgrades the row to ``needs_setup`` instead of offering a
pick that would launch nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from domain.emulator_commands import EmulatorOption, classify_command

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

#: The token ES-DE uses for its spawn helper. A ``--host`` form is the one the bake can
#: render as bare argv, so an owned standalone is written in it and no sandbox is needed.
SPAWN_TOKEN = "%EMULATOR_FLATPAK-SPAWN%"

_LIBRETRO_COMMAND = "%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/{core}.so %ROM%"

#: The only kinds an inventory entry may declare.
KINDS = ("libretro", "standalone")


@dataclass(frozen=True)
class InventoryEmulator:
    """One emulator an inventory platform offers, as the document states it."""

    label: str
    emulator: str
    kind: str
    core_so: str | None = None
    host_binaries: tuple[str, ...] = ()
    host_args: tuple[str, ...] = ()


@dataclass(frozen=True)
class InventoryPlatform:
    """One platform's inventory: its accept-list and the emulators it can launch with."""

    platform: str
    names: tuple[str, ...]
    extensions: tuple[str, ...]
    emulators: tuple[InventoryEmulator, ...]


def _strings(value: Any) -> tuple[str, ...]:
    """Every non-empty string in *value*, ignoring anything else.

    A document is data, so a wrong type is a malformed line rather than a crash: a
    ``binaries`` that arrived as a string instead of a list yields that one path, and a
    number yields nothing.
    """
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, (list, tuple)):
        return tuple(item for item in value if isinstance(item, str) and item)
    return ()


def _emulator(raw: Any) -> InventoryEmulator | None:
    """Parse one emulator entry, or ``None`` when it is not one this module can use."""
    if not isinstance(raw, dict):
        return None
    label = raw.get("label")
    kind = raw.get("kind")
    if not isinstance(label, str) or not label or kind not in KINDS:
        return None
    identity = raw.get("id") if isinstance(raw.get("id"), str) else label
    if kind == "libretro":
        core = raw.get("core")
        # A libretro row without a core is not a row: there is nothing to load.
        if not isinstance(core, str) or not core:
            return None
        return InventoryEmulator(label=label, emulator=identity, kind=kind, core_so=core)
    host = raw.get("host") if isinstance(raw.get("host"), dict) else {}
    return InventoryEmulator(
        label=label,
        emulator=identity,
        kind=kind,
        host_binaries=_strings(host.get("binaries")),
        host_args=_strings(host.get("args")),
    )


def parse_inventory(document: Any) -> dict[str, InventoryPlatform]:
    """Read an inventory document into platforms keyed by every name it answers to.

    A platform is registered under its own key and each of its ``aliases``, because the
    name that reaches this module is whatever the platform map resolved, and ``ps1``,
    ``psx`` and ``playstation`` are one platform to the user. A malformed platform or
    emulator is skipped rather than failing the read: a partial inventory still picks a
    default for everything it does describe.
    """
    if not isinstance(document, dict):
        return {}
    platforms = document.get("platforms")
    if not isinstance(platforms, dict):
        return {}
    parsed: dict[str, InventoryPlatform] = {}
    for key, raw in platforms.items():
        if not isinstance(key, str) or not isinstance(raw, dict):
            continue
        emulators = tuple(
            emulator for emulator in (_emulator(item) for item in raw.get("emulators") or []) if emulator is not None
        )
        if not emulators:
            continue
        names = (key, *_strings(raw.get("aliases")))
        entry = InventoryPlatform(
            platform=key,
            names=tuple(dict.fromkeys(names)),
            extensions=tuple(token.lower() for token in _strings(raw.get("extensions"))),
            emulators=emulators,
        )
        for name in entry.names:
            parsed.setdefault(name.lower(), entry)
    return parsed


def libretro_command(core_so: str) -> str:
    """The ES-DE libretro command shape for an owned core name."""
    return _LIBRETRO_COMMAND.format(core=core_so)


def host_command(binary: str, args: Iterable[str] = ()) -> str:
    """The owned host launch for a standalone binary: ``--host <bin> <args> %ROM%``.

    Written in the ``%EMULATOR_FLATPAK-SPAWN%`` form so the existing bake rule renders it
    as bare argv (:func:`domain.shortcut_data._host_argv`). An arg that itself carries a
    ``%`` would be read as a placeholder by the classifier, so such args are dropped here
    rather than baked into a launch that then cannot resolve.
    """
    safe = [arg for arg in args if arg and "%" not in arg]
    tail = " ".join(safe)
    return f"{SPAWN_TOKEN} --host {binary} {tail} %ROM%" if tail else f"{SPAWN_TOKEN} --host {binary} %ROM%"


def options_for(
    platform: InventoryPlatform,
    *,
    core_installed: Callable[[str], bool],
    binary_for: Callable[[InventoryEmulator], str | None],
) -> list[EmulatorOption]:
    """Classify one platform's entries into picker options, in document order.

    Order is the inventory's own preference order, so the first bakeable entry is the
    platform default — the same rule the ES-DE path follows, which is what keeps a
    default stable across a device gaining or losing its catalogue.

    A libretro entry whose core is not installed, and a standalone entry whose binary was
    not found, are downgraded to ``needs_setup`` with reason ``not_installed``: they stay
    visible (so the reason can be shown) but neither becomes the default nor bakes a
    launch that would fail.
    """
    options: list[EmulatorOption] = []
    for emulator in platform.emulators:
        if emulator.kind == "libretro":
            option = classify_command(
                emulator.label, libretro_command(emulator.core_so or ""), emulator=emulator.emulator
            )
            if not core_installed(emulator.core_so or ""):
                option = replace(option, status="needs_setup", reason="not_installed")
            options.append(option)
            continue
        binary = binary_for(emulator)
        command = host_command(binary, emulator.host_args) if binary else host_command(emulator.label)
        option = classify_command(emulator.label, command, emulator=emulator.emulator)
        if binary is None:
            option = replace(option, status="needs_setup", reason="not_installed")
        options.append(option)
    return options


def platform_names(inventory: Mapping[str, InventoryPlatform]) -> frozenset[str]:
    """Every name the inventory answers to — the systems it can describe."""
    return frozenset(inventory)
