"""Emulator tag construction for RomM save uploads.

The emulator tag determines the server-side folder path for saves:
saves/{system}/{rom_id}/{emulator}/

Format: retroarch-{core} where core is the libretro core name
without the _libretro suffix, lowercased.

No I/O, no service/adapter/lib imports. Pure functions only.
"""

from __future__ import annotations

import re

_LIBRETRO_SUFFIX = "_libretro"
_FALLBACK = "retroarch"

# A picker label carries the provider in parentheses (``Dolphin (Standalone)``,
# ``Eden (Flatpak)``); the tag is the emulator's own name, not its provider's.
_PROVIDER_SUFFIX = re.compile(r"\([^)]*\)")
_ANY_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def build_emulator_tag(core_so: str | None) -> str:
    """Build a RomM emulator tag from a RetroArch core .so name.

    Parameters
    ----------
    core_so:
        The libretro core name as found in ES-DE config, e.g. "mgba_libretro",
        "snes9x_libretro", "swanstation_libretro".
        May be None if core resolution failed.

    Returns
    -------
    str
        Emulator tag string, e.g. "retroarch-mgba", "retroarch-snes9x".
        Returns "retroarch" as fallback when core_so is None or empty.

    Rules:
    - Strip "_libretro" suffix
    - Lowercase
    - Prepend "retroarch-"
    - Fallback to "retroarch" if core_so is None/empty
    """
    if not core_so:
        return _FALLBACK
    core = core_so.lower()
    if core.endswith(_LIBRETRO_SUFFIX):
        core = core[: -len(_LIBRETRO_SUFFIX)]
    return f"retroarch-{core}"


def normalize_emulator_identity(identity: str | None) -> str | None:
    """The tag spelling of an emulator's own name, or ``None`` when it names nothing.

    Measured on the reference Deck's own server: a GameCube save written by Dolphin is
    filed under ``dolphin`` and a Switch save written by Eden under ``eden`` — so the tag
    is the emulator, spelled its own way, and a provider suffix in a picker label is not
    part of it.
    """
    if not identity:
        return None
    words = _ANY_NON_ALNUM.sub(" ", _PROVIDER_SUFFIX.sub(" ", identity.strip().lower())).split()
    tag = "-".join(words)
    return tag or None


def emulator_tag(core_so: str | None, *, identity: str | None = None) -> str:
    """The tag an upload is stamped with: the emulator that actually ran.

    A standalone launch answers its own identity (``dolphin``, ``eden``) because there is
    no RetroArch core involved at all — measured on the reference Deck, a Switch save
    uploaded this way was labelled ``retroarch`` on a device with no RetroArch Switch core,
    which files the save in a folder no Eden install reads. A libretro launch keeps
    ``retroarch-<core>``, and ``retroarch`` remains only for a ROM whose launch could not be
    resolved at all.

    *identity* is whatever the resolving layer calls the emulator — a definition id from
    the registry (``eden``) or a picker label (``Dolphin (Standalone)``); both normalise to
    the same tag.
    """
    own = normalize_emulator_identity(identity)
    return own or build_emulator_tag(core_so)


def detect_core_change(stored_core: str | None, active_core: str | None) -> bool:
    """Detect if the active RetroArch core has changed since last sync.

    Parameters
    ----------
    stored_core:
        The core_so name recorded at last sync, or None if never synced.
    active_core:
        The currently active core_so name, or None if unresolved.

    Returns
    -------
    bool
        True if the cores differ and both are non-None (actual change).
        False if either is None (can't determine) or they match.
    """
    if stored_core is None or active_core is None:
        return False
    return stored_core != active_core
