"""Which runtime the plugin drives, and the roots it owns when it drives its own.

Two words this module and the rest of the app use, and never interchangeably:

- **Built-in** — the libretro runtime and cores the plugin downloads, verifies and
  launches itself. ``BUILTIN`` below means exactly this and nothing else.
- **Standalone** — an emulator the plugin did not install and cannot configure (Eden,
  RPCS3, a flatpak, an AppImage). It is reached through the emulator registry and
  ``EmulatorInvocation.standalone``; it is never a runtime this module returns.

The plugin was written against RetroDECK: every root it read came out of
``retrodeck.json``, and with RetroDECK gone those getters return ``~/retrodeck/roms`` and
friends — paths that exist only because RetroDECK is installed. That is not a fallback, it
is a dependency with a polite error message, and it rules out the shape this app is
supposed to have: one that manages its own library, saves and emulators.

So the runtime is a value, decided once and read everywhere:

- ``BUILTIN`` — the app's own runtime, and the shipped default. Roots are its own tree
  (``<home>/Emulation`` unless a root is overridden), and a libretro launch goes through
  the RetroArch it installed with the cores it provisioned. Nothing from RetroDECK or a
  separately installed RetroArch is read, expected or required.
- ``RETRODECK`` — the classic shape, opt-in. Roots come from ``retrodeck.json`` and the
  launcher is RetroDECK's, because that is what the user asked for.
- ``AUTO`` — follow whoever is installed (RetroDECK when present). Kept for the user who
  wants the app to adapt rather than decide, never as the default.

``AUTO`` never leaves the answer empty: a Deck with nothing installed answers from the
built-in tree, so the library stays readable rather than reporting success over no roots.

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
    BUILTIN = "builtin"


#: The directory the built-in runtime keeps its library in. EmuDeck's own layout, because
#: that is the tree a Deck already has when RetroDECK is the thing being dropped; a root
#: that names another tree through settings wins over it.
BUILTIN_ROOT_DIR = "Emulation"

#: The one older spelling of :attr:`RuntimeMode.BUILTIN` a settings file may still hold.
_LEGACY_BUILTIN = "standalone"

#: Where the RetroArch Flatpak the plugin installs keeps its own folders, relative to the
#: user's home: ``saves``, ``states``, ``cores`` and ``system`` live directly beneath it.
RETROARCH_FLATPAK_ROOT = (
    ".var",
    "app",
    "org.libretro.RetroArch",
    "config",
    "retroarch",
)

#: Where that RetroArch keeps the cores it loads. The owned launch path starts it, so this
#: is the directory the provisioner writes into.
RETROARCH_FLATPAK_CORES = (*RETROARCH_FLATPAK_ROOT, "cores")


class Structure(StrEnum):
    """Where the app's built-in tree puts the data it manages (ADR-0046).

    A structure is a *shape*, not a path: the four per-root overrides still win on top of
    whichever one is chosen, so a user can keep the app's own tree and put BIOS on a card.

    - ``APP`` — the shipped default. Everything the app downloads or writes (ROMs, BIOS,
      states, cores, and the save tree the appendconfig points at) lives under its own data
      directory, the one place it is guaranteed to be able to read back.
    - ``EMUDECK`` — ``<home>/Emulation``, the tree an EmuDeck/ES-DE device already has. Cores
      stay in the installed RetroArch, since that is the program that loads them.
    - ``RETROARCH`` — the installed RetroArch's own ``saves``/``states``/``cores``/``system``
      folders, for the user who wants other RetroArch tooling to see the same saves. ROMs
      stay in the app's data directory: RetroArch has no ROM root to adopt.
    - ``CUSTOM`` — the per-root paths in settings are the answer; anything left blank falls
      back to the ``EMUDECK`` shape rather than to an empty path.
    """

    APP = "app"
    EMUDECK = "emudeck"
    RETROARCH = "retroarch"
    CUSTOM = "custom"


def resolve_structure(setting: object) -> Structure:
    """The chosen structure, with anything unrecognised reading as the shipped default.

    Same rule as the runtime: a settings file holding a word this code does not know must
    not silently reroute where a user's data lives, so it reads as ``APP`` — the one shape
    whose paths the app itself creates and can always write.
    """
    for structure in Structure:
        if setting == structure:
            return structure
    return Structure.APP

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
    if setting in (RuntimeMode.BUILTIN, _LEGACY_BUILTIN):
        # ``"standalone"`` was this decision's spelling for one build (0.36.0); reading it
        # as the current name keeps a settings file from rerouting to AUTO's answer.
        return RuntimeMode.BUILTIN
    return RuntimeMode.RETRODECK if retrodeck_present else RuntimeMode.BUILTIN


def resolve_roots(
    *,
    mode: RuntimeMode,
    home: str,
    retrodeck_roots: Mapping[str, str],
    settings: Mapping[str, object] | None = None,
    data_dir: str = "",
) -> RuntimeRoots:
    """The roots for *mode*, with per-root settings overrides on top.

    A ``RETRODECK`` runtime returns *retrodeck_roots* untouched: that adapter has already
    resolved them (symlinks included, #1838), and re-deriving them here would be a second
    spelling of one directory.

    A ``BUILTIN`` runtime answers from the structure the settings name (ADR-0046), with
    ``<root>_dir`` settings keys overriding any of them. An empty override is unset, not a
    root of ``""`` — a settings file that once held a path and had it cleared must fall
    back, not point at nothing.

    *data_dir* is what makes the ``APP`` structure possible; without it (a caller with no
    data directory, which is only true of a test or a probe) the built-in tree falls back to
    the EmuDeck shape rather than inventing a root under the plugin's install folder.
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
    retroarch_root = "/".join((home, *RETROARCH_FLATPAK_ROOT))
    emudeck_base = f"{home}/{BUILTIN_ROOT_DIR}"
    structure = resolve_structure((settings or {}).get("structure"))
    if structure is Structure.APP and not data_dir:
        # No data directory was supplied, so there is no app tree to answer from.
        structure = Structure.EMUDECK
    if structure is Structure.APP:
        base = data_dir
        defaults = {
            "roms": f"{base}/roms",
            "saves": f"{base}/saves",
            "bios": f"{base}/bios",
            "states": f"{base}/states",
            "cores": f"{base}/cores",
        }
    elif structure is Structure.RETROARCH:
        defaults = {
            # RetroArch has no ROM root to adopt, so the app keeps the files it downloaded
            # where it can always find them.
            "roms": f"{data_dir or emudeck_base}/roms",
            "saves": f"{retroarch_root}/saves",
            "states": f"{retroarch_root}/states",
            "bios": f"{retroarch_root}/system",
            "cores": f"{retroarch_root}/cores",
        }
    else:  # EMUDECK and CUSTOM share the tree; CUSTOM differs only in what overrides it
        defaults = {
            "roms": f"{emudeck_base}/roms",
            "saves": f"{emudeck_base}/saves",
            "bios": f"{emudeck_base}/bios",
            "states": f"{emudeck_base}/states",
            "cores": f"{retroarch_root}/cores",
        }
    values: dict[str, str] = {}
    for name, default in defaults.items():
        # ``states`` has no override key of its own: it follows the tree, and looking up a
        # missing name here would crash the read rather than fall back.
        key = OVERRIDE_KEYS.get(name)
        override = (settings or {}).get(key) if key is not None else None
        values[name] = override if isinstance(override, str) and override else default
    return RuntimeRoots(mode=mode, **values)


def roms_roots_for_installs(
    *,
    mode: RuntimeMode,
    home: str,
    retrodeck_roots: Mapping[str, str],
    settings: Mapping[str, object] | None = None,
    data_dir: str = "",
) -> tuple[str, ...]:
    """Every roms root an installed ROM may sit under, today's first (ADR-0046).

    A structure is a setting, and changing it moves nothing, so a device that
    downloaded games under a previous structure still holds installs outside
    today's root. Deletion has to accept those: refusing them would leave a game
    impossible to uninstall without first moving its files — the one thing the
    setting promises not to do.

    The candidates are the roots this plugin itself owns under each structure it
    can have shipped or been pointed at, not "wherever the recorded path happens
    to be": a path still has to lie inside one of our trees, so a corrupted
    install row cannot aim a deletion at the user's home. Per-root overrides are
    deliberately not applied to the historical candidates — an override is
    today's choice, and the point here is the trees an older choice wrote to. The
    current root, overrides included, is always first.
    """
    roots = [
        resolve_roots(
            mode=mode,
            home=home,
            retrodeck_roots=retrodeck_roots,
            settings=settings,
            data_dir=data_dir,
        ).roms
    ]
    roots.extend(
        resolve_roots(
            mode=RuntimeMode.BUILTIN,
            home=home,
            retrodeck_roots={},
            settings={"structure": structure.value},
            data_dir=data_dir,
        ).roms
        for structure in (Structure.APP, Structure.EMUDECK, Structure.RETROARCH)
    )
    ordered: list[str] = []
    for root in roots:
        if root and root not in ordered:
            ordered.append(root)
    return tuple(ordered)


def resolve_launch_backend(setting: object, *, mode: RuntimeMode) -> str:
    """The backend a libretro launch goes through, given the runtime.

    An explicit ``"retroarch"`` always wins, because it is the owned form and needs
    nothing from RetroDECK. The shipped default is RetroDECK's launcher, and a
    ``BUILTIN`` runtime cannot use it — there is no RetroDECK to hand the command to —
    so the default resolves to the owned one instead of baking a launch that dies at
    exec. This is the one place the setting is read through, so the read-path and the
    bake cannot disagree about which program starts.
    """
    if setting == "retroarch":
        return "retroarch"
    return "retroarch" if mode is RuntimeMode.BUILTIN else "retrodeck"
