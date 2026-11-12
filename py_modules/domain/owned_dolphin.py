"""An owned standalone launch: the user directory we pin, and the save it implies.

Measured on the reference Deck, and the reason this module exists: the plugin baked
RetroDECK's placeholder command (``%EMULATOR_DOLPHIN% -b -e %ROM%``) and handed it over,
so the emulator's user directory was chosen after the plugin stopped looking. The session
then wrote ``~/retrodeck/saves/gc/User/GC/USA/Card A/01-GZ2E-gczelda2.gci`` while the save
layer resolved ``~/retrodeck/saves/gc`` — where the old misplaced ``…(USA).zip`` sat — and
skipped that zip as already synced. A save that plainly existed was never carried.

Pinning the user directory with ``-u`` turns it into a fact of OUR command, and the save
directory follows from it by the emulator's own compiled-in default (``<user>/GC/<region>/
Card A`` in GCI-folder mode, whose slot device this machine's ``Dolphin.ini`` leaves at that
default). Nothing here guesses where an emulator MIGHT write: the plugin states where it
told the emulator to write.

Everything in this module is pure text — no filesystem, no settings, no I/O.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.shortcut_data import EmulatorInvocation

# The one flag that moves a Dolphin-family emulator's user directory.
_USER_DIR_FLAG = "-u"

# ES-DE's emulator placeholder, e.g. ``%EMULATOR_DOLPHIN%``.
_EMULATOR_TOKEN = re.compile(r"%EMULATOR_[A-Z0-9_]+%")

# Labels/identities that name the emulator this pin is about. PrimeHack is Dolphin's
# Metroid fork and has its OWN user tree, so it is deliberately not in this set: pinning
# Dolphin's directory onto it would point a launch at another emulator's saves.
_DOLPHIN_NAMES = ("dolphin",)

# Where RetroDECK keeps this emulator's user tree, relative to the saves root.
_GC_USER_DIR = "gc/User"


def is_owned_dolphin(label: str | None, emulator: str | None) -> bool:
    """Whether this invocation is a Dolphin launch whose user directory we may pin.

    Answered from what the catalogue itself states — the ES-DE label and the resolver's
    emulator identity — and never from a command string, so a rebranded command cannot
    silently gain the flag.
    """
    names = [name.strip().lower() for name in (label, emulator) if name is not None]
    # PrimeHack is checked across BOTH names first: an ES-DE label may say "Dolphin"
    # while the resolved identity is the fork, and pinning then crosses save trees.
    if any("primehack" in name for name in names):
        return False
    return any(name.startswith(dolphin) for name in names for dolphin in _DOLPHIN_NAMES)


def command_with_user_dir(command: str, user_dir: str) -> str | None:
    """*command* with ``-u <user_dir>`` after its emulator token, or ``None`` when it cannot carry it.

    The flag has to sit after the binary token and before ``%ROM%``: ES-DE's launcher
    substitutes ``%EMULATOR_DOLPHIN%`` for the binary path, so inserting anywhere else
    would put the flag where the emulator reads it as a ROM name or nowhere at all.

    ``None`` is a refusal, not a silent no-op — a command that already states its own
    ``-u`` is somebody else's decision about the user directory, and this plugin does not
    overwrite one it did not make. A command with no emulator token is not an ES-DE
    invocation at all.
    """
    token = _EMULATOR_TOKEN.search(command)
    if token is None or _has_user_dir_flag(command):
        return None
    head = command[: token.end()]
    tail = command[token.end() :]
    return f"{head} {_USER_DIR_FLAG} {user_dir}{tail}"


def _has_user_dir_flag(command: str) -> bool:
    """Whether the command already carries ``-u`` as a flag of its own."""
    return re.search(r"(^|\s)-u(\s|$)", command) is not None


def with_user_dir(invocation: EmulatorInvocation, user_dir: str) -> EmulatorInvocation | None:
    """*invocation* pinned to *user_dir*, or ``None`` when it cannot be pinned.

    Only a standalone invocation is pinnable: a libretro core is pointed at a directory by
    its ``--appendconfig``, and claiming a ``-u`` there would be a statement about a
    program that never receives it.
    """
    if invocation.kind not in {"standalone", "direct"} or not invocation.command:
        return None
    # The command is checked, not rewritten: the flag is added once, at render time, so
    # there is exactly one place that composes it and no chance of stacking two.
    if command_with_user_dir(invocation.command, user_dir) is None:
        return None
    return replace(invocation, user_dir=user_dir)


def user_dir_for(platform_slug: str, saves_base: str) -> str | None:
    """The Dolphin user directory for *platform_slug*, or ``None`` for platforms it does not cover.

    Today only GameCube: the measured Deck keeps this emulator's user tree under
    ``<saves>/gc/User``, which is where the last session actually wrote. Adopting it is why
    nothing has to move — the existing save is picked up on the first owned launch.
    """
    if platform_slug not in {"gc", "ngc", "gamecube", "gcn"}:
        return None
    return f"{saves_base.rstrip('/')}/{_GC_USER_DIR}"


def gc_card_dir(user_dir: str) -> str:
    """The GCI folder this user directory implies, with its region still a hole.

    ``<user>/GC/<region>/Card A`` is Dolphin's compiled-in default for a GCI folder in
    slot A; the plugin fills ``<region>`` from the disc, never from a guess.
    """
    return f"{user_dir.rstrip('/')}/GC/<region>/Card A"
