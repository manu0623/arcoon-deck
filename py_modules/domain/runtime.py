"""Which runtime the plugin drives, and the roots it owns when it drives its own.

The plugin was written against RetroDECK: every root it read came out of
``retrodeck.json``, and with RetroDECK gone those getters return
``~/retrodeck/roms`` and friends — paths that exist only because RetroDECK is installed.
That is not a fallback, it is a dependency with a polite error message, and it rules out
the shape this plugin is supposed to have: an app that manages its own library, saves and
emulators.

So the runtime is a value, decided once and read everywhere:

- ``RETRODECK`` — the classic shape. Roots come from ``retrodeck.json`` exactly as before.
- ``STANDALONE`` — the plugin owns its roots. They default to an EmuDeck-style
  ``<home>/Emulation`` tree, which is where a Deck's standalone emulators (Eden, Dolphin,
  Cemu) already keep their saves, and any of them can be overridden in settings.
- ``AUTO`` — the user's setting: follow whoever is installed.

The measured state of a Deck with RetroDECK removed is why this exists rather than a
guess: ``~/retrodeck/{roms,saves,bios}`` exist only on a RetroDECK install, and the
RetroArch Flatpak that the owned launch path starts holds none of RetroDECK's cores. A
runtime that answers "no roots" would leave the library unreadable while everything above
it kept reporting success, so ``AUTO`` never leaves the answer empty — it picks the tree
that a standalone Deck actually has.

This module is pure: it takes what was detected and what was configured, and returns
values. Nothing here touches the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class RuntimeMode(StrEnum):
    """Which runtime the plugin is driving."""

    AUTO = "auto"
    RETRODECK = "retrodeck"
    STANDALONE = "standalone"


#: The directory a standalone runtime keeps its library in. EmuDeck's own layout, because
#: that is the tree a Deck already has when RetroDECK is the thing being dropped.
STANDALONE_ROOT_DIR = "Emulation"

#: Where RetroArch's Flatpak keeps the cores it loads, relative to the user's home. The
#: owned launch path starts that RetroArch, so its cores directory is the one to provision.
RETROARCH_FLATPAK_CORES = (
    ".var",
    "app",
    "org.libretro.RetroArch",
    "config",
    "retroarch",
    "cores",
)

#: Settings keys that override a standalone root, per root name.
OVERRIDE_KEYS = {
    "roms": "roms_dir",
    "saves": "saves_dir",
    "bios": "bios_dir",
    "cores": "cores_dir",
}


@dataclass(frozen=True)
class RuntimeRoots:
    """The four roots every layer above this reads, whichever runtime answered."""

    mode: RuntimeMode
    roms: str
    saves: str
    bios: str
    states: str
    cores: str


def resolve_mode(setting: object, *, retrodeck_present: bool) -> RuntimeMode:
    """The runtime to drive, given the user's setting and what is installed.

    ``AUTO`` follows the installation. An explicit ``"retrodeck"`` is honoured even when
    nothing was detected — a user who says RetroDECK may be pointing at a tree the
    detection does not read, and overriding that would be the same silent substitution
    this module exists to remove. Any unrecognized value reads as ``AUTO`` rather than as
    a third meaning: a settings file with ``"runtime_mode": "yes"`` must not reroute the
    whole library.
    """
    if setting == RuntimeMode.RETRODECK:
        return RuntimeMode.RETRODECK
    if setting == RuntimeMode.STANDALONE:
        return RuntimeMode.STANDALONE
    return RuntimeMode.RETRODECK if retrodeck_present else RuntimeMode.STANDALONE


def resolve_roots(
    *,
    mode: RuntimeMode,
    home: str,
    retrodeck_roots: Mapping[str, str],
    settings: Mapping[str, object] | None = None,
) -> RuntimeRoots:
    """The roots for *mode*, with per-root settings overrides on top.

    A ``RETRODECK`` runtime returns *retrodeck_roots* untouched: that adapter has already
    resolved them (symlinks included, #1838), and re-deriving them here would be a second
    spelling of one directory.

    A ``STANDALONE`` runtime answers from its own tree, with ``<root>_dir`` settings keys
    overriding any of them. An empty override is unset, not a root of ``""`` — a settings
    file that once held a path and had it cleared must fall back, not point at nothing.
    """
    if mode is RuntimeMode.RETRODECK:
        return RuntimeRoots(
            mode=mode,
            roms=retrodeck_roots["roms"],
            saves=retrodeck_roots["saves"],
            bios=retrodeck_roots["bios"],
            states=retrodeck_roots["states"],
            cores=retrodeck_roots.get("cores", ""),
        )
    base = f"{home}/{STANDALONE_ROOT_DIR}"
    defaults = {
        "roms": f"{base}/roms",
        "saves": f"{base}/saves",
        "bios": f"{base}/bios",
        "states": f"{base}/states",
        "cores": "/".join((home, *RETROARCH_FLATPAK_CORES)),
    }
    values: dict[str, str] = {}
    for name, default in defaults.items():
        # ``states`` has no override key of its own: it follows the tree, and looking up a
        # missing name here would crash the read rather than fall back.
        key = OVERRIDE_KEYS.get(name)
        override = (settings or {}).get(key) if key is not None else None
        values[name] = override if isinstance(override, str) and override else default
    return RuntimeRoots(mode=mode, **values)


def resolve_launch_backend(setting: object, *, mode: RuntimeMode) -> str:
    """The backend a libretro launch goes through, given the runtime.

    An explicit ``"retroarch"`` always wins, because it is the owned form and needs
    nothing from RetroDECK. The shipped default is RetroDECK's launcher, and a
    ``STANDALONE`` runtime cannot use it — there is no RetroDECK to hand the command to —
    so the default resolves to the owned one instead of baking a launch that dies at
    exec. This is the one place the setting is read through, so the read-path and the
    bake cannot disagree about which program starts.
    """
    if setting == "retroarch":
        return "retroarch"
    return "retroarch" if mode is RuntimeMode.STANDALONE else "retrodeck"
