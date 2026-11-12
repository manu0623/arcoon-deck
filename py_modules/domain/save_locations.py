"""Where an emulator keeps its saves, established from its own configuration.

One rule per emulator *family* and platform: the config keys to read first, then
the directories to fall back to. Resolution is a pure function of values the
adapter already parsed, so the answer is testable without an emulator installed and
identical on every machine that holds the same config.

Three properties decide the shape.

**Configured beats defaulted, always.** The emulator acts on its config, so a path
named there is the truth even when the directory does not exist yet — it is where
the emulator will write. ``exists`` is reported beside it rather than folded into
the choice, because a configured-but-absent root is a *fact* the session layer needs:
it is either a first launch (create it) or a moved library (say so).

**A rule that cannot answer says so.** :func:`resolve` returns
:class:`UnresolvedSaveRoot` for a family with no rule, or a platform the family does
not serve — never a plausible-looking path. The picker refuses such a pick instead
of syncing a directory nobody chose.

**Only verified keys are encoded.** PCSX2's ``Folders/MemoryCards`` and DuckStation's
``MemoryCards/Directory`` were read off a live Deck's own config files; RetroArch's
``savefile_directory`` likewise. Families whose key could not be confirmed carry
defaults only, and their docstrings say so rather than inventing a key that would
read as absent and silently fall through.

Pure compute: stdlib only, ``posixpath`` for the same reason the registry uses it.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable

RootSource = Literal["config", "default"]
UnresolvedReason = Literal["unknown-family", "platform-not-served", "no-candidates"]

# `{home}`, `{config}` and `{data}` are the only placeholders. `home` is the user's
# home directory; `config` and `data` are the emulator's XDG roots as the *provider*
# keeps them — a flatpak's `~/.var/app/<id>/config/<app>` and a native install's
# `~/.config/<app>` are different values for the same rule, which is why the caller
# supplies them rather than the rule assuming one.
#
# Two roots, not one, because emulators disagree about which they write into: PCSX2
# keeps memory cards beside its settings (`{config}/memcards`) while Dolphin keeps
# them in its data tree (`{data}/GC`). Both were read off the same Deck.
HOME_TOKEN = "{home}"
CONFIG_TOKEN = "{config}"
DATA_TOKEN = "{data}"


@dataclass(frozen=True, slots=True)
class SaveRootRule:
    """The config keys and fallback directories for one emulator family.

    ``keys`` are flattened ``Section/Key`` (or bare ``Key`` for a flat file),
    tried in order; the first with a non-empty value wins. ``defaults`` are
    templates, tried in order, first **existing** one wins. Both may be empty —
    but not both, which :func:`rule_for` guarantees by construction.
    """

    family: str
    platforms: tuple[str, ...]
    keys: tuple[str, ...] = ()
    defaults: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ResolvedSaveRoot:
    """An answered save root.

    ``source`` says which half answered, so a UI can distinguish "your emulator's
    config says here" from "the emulator's default location". ``exists`` is
    reported, never used to override the answer.
    """

    path: str
    source: RootSource
    exists: bool


@dataclass(frozen=True, slots=True)
class UnresolvedSaveRoot:
    """A refusal, carrying the reason a pick can show."""

    family: str
    platform: str
    reason: UnresolvedReason


SaveRootAnswer = ResolvedSaveRoot | UnresolvedSaveRoot


# ── The rules ───────────────────────────────────────────────────────────────
#
# Verified against a live Deck unless marked otherwise:
#   retroarch.savefile_directory        — read from the flatpak's retroarch.cfg
#   pcsx2.Folders/MemoryCards           — read from ~/.config/PCSX2/inis/PCSX2.ini
#   duckstation.MemoryCards/Directory   — read from duckstation's settings.ini
#   dolphin                             — its Dolphin.ini carries no save path, so
#                                         the rule is defaults-only by observation
#   yuzu family / ryujinx               — data roots confirmed; layout inside them
#                                         belongs to save_bank's families

_RULES: tuple[SaveRootRule, ...] = (
    SaveRootRule(
        family="retroarch",
        platforms=("*",),
        keys=("savefile_directory",),
        defaults=("{config}/saves",),
    ),
    SaveRootRule(
        family="pcsx2",
        platforms=("ps2",),
        keys=("Folders/MemoryCards",),
        defaults=("{config}/memcards", "{data}/saves"),
    ),
    SaveRootRule(
        family="duckstation",
        platforms=("psx",),
        keys=("MemoryCards/Directory",),
        defaults=("{data}/memcards", "{data}/saves"),
    ),
    SaveRootRule(
        family="dolphin",
        platforms=("gc", "wii"),
        # No key verified: this Deck's Dolphin.ini states no card path, and
        # naming a key that reads as absent would fall through silently.
        defaults=(
            "{data}/GC/USA/Card A",
            "{data}/GC/Europe/Card A",
            "{data}/GC/Japan/Card A",
            "{data}/GC",
        ),
    ),
    SaveRootRule(
        family="ppsspp",
        platforms=("psp",),
        defaults=("{data}/PSP/SAVEDATA", "{data}/saves"),
    ),
    SaveRootRule(
        family="melonds",
        platforms=("nds",),
        defaults=("{data}/saves", "{data}/savestates"),
    ),
    SaveRootRule(
        family="citra",
        platforms=("n3ds",),
        defaults=("{data}/sdmc",),
    ),
    SaveRootRule(
        family="yuzu",
        platforms=("switch",),
        defaults=("{data}",),
    ),
    SaveRootRule(
        family="ryujinx",
        platforms=("switch",),
        # Ryujinx is the one emulator here that puts its whole tree under the
        # *config* root: this Deck holds bis/, games/ and system/ in
        # `~/.config/Ryujinx` and has no `~/.local/share/Ryujinx` at all. The yuzu
        # lineage is the opposite (`~/.local/share/eden` holds nand/).
        defaults=("{config}",),
    ),
    SaveRootRule(
        family="cemu",
        platforms=("wiiu",),
        defaults=("{data}/mlc01",),
    ),
    SaveRootRule(
        family="rpcs3",
        platforms=("ps3",),
        defaults=("{data}/dev_hdd0/home/00000001/savedata",),
    ),
    SaveRootRule(
        family="vita3k",
        platforms=("psvita",),
        defaults=("{data}/ux0/user/00/savedata",),
    ),
    SaveRootRule(
        family="flycast",
        platforms=("dreamcast",),
        defaults=("{data}",),
    ),
    SaveRootRule(
        family="mgba",
        platforms=("gb", "gbc", "gba"),
        defaults=("{data}/saves",),
    ),
    # The four below are declared from each emulator's documented tree, not from a
    # config read here — the Deck holds the binaries but no saved game yet for any
    # of them. They are defaults-only on purpose, so a wrong default surfaces as an
    # empty harvest the first time a game is played rather than as a wrong write.
    SaveRootRule(
        family="mupen64plus",
        platforms=("n64",),
        defaults=("{data}/save",),
    ),
    SaveRootRule(
        family="xemu",
        platforms=("xbox",),
        # Xbox saves live inside the HDD image, not as loose files; a per-game unit
        # is not addressable here at all.
        defaults=("{data}/saves",),
    ),
    SaveRootRule(
        family="xenia",
        platforms=("xbox360",),
        defaults=("{data}/content",),
    ),
    SaveRootRule(
        family="shadps4",
        platforms=("ps4",),
        defaults=("{data}/savedata",),
    ),
)

_BY_FAMILY: dict[str, SaveRootRule] = {rule.family: rule for rule in _RULES}


def all_rules() -> tuple[SaveRootRule, ...]:
    """Every rule, in registry order."""
    return _RULES


def rule_for(family: str) -> SaveRootRule | None:
    """The rule for *family*, or ``None`` when no rule exists for it."""
    return _BY_FAMILY.get(family)


def _expand(template: str, *, home: str, data: str, config: str) -> str:
    """Fill the three tokens and normalise a Deck-style path.

    ``~`` is expanded because emulators write it in their own configs
    (``~/saves``), and ``posixpath.normpath`` collapses the ``..`` a config may
    carry without resolving symlinks — an emulator's symlinked save directory must
    stay the path the emulator itself would open.
    """
    expanded = template.replace(HOME_TOKEN, home).replace(CONFIG_TOKEN, config).replace(DATA_TOKEN, data)
    if expanded.startswith("~/"):
        expanded = posixpath.join(home, expanded[2:])
    return posixpath.normpath(expanded)


def _configured(rule: SaveRootRule, values: dict[str, str]) -> str | None:
    """The first non-empty configured value among the rule's keys.

    Keys are matched as given; a bare key is also tried without its section, so a
    reader that flattens ``[Folders] MemoryCards`` as either ``Folders/MemoryCards``
    or ``MemoryCards`` answers the same rule. Values are stripped: several of these
    files write trailing spaces (PCSX2's ``BlockDumpSaveDirectory = `` is empty, not
    a path).
    """
    for key in rule.keys:
        for candidate in (key, key.rsplit("/", 1)[-1]):
            raw = values.get(candidate)
            if raw is None:
                continue
            cleaned = raw.strip().strip('"').strip()
            if cleaned:
                return cleaned
    return None


def resolve(
    *,
    family: str,
    platform: str,
    values: dict[str, str],
    home: str,
    data: str,
    config: str | None = None,
    exists: Callable[[str], bool],
) -> SaveRootAnswer:
    """Resolve the save root for one emulator family and platform.

    Order, and why:

    1. **The configured path**, expanded. Returned even when absent — the emulator
       will create it, and a first launch is not an error.
    2. **The first default that exists**, in rule order. Existence is what makes a
       default an answer rather than a choice: with none present we still return
       the first as ``source="default", exists=False``, because the session layer
       must create it before launching, and refusing here would make a fresh
       install unplayable.
    3. **A refusal** only when the family has no rule, the platform is not one the
       family serves, or the rule declares no candidates at all.

    ``config`` defaults to ``data``: a caller that knows only one root (an emulator
    whose settings and data share a directory) then states one fact, and a rule using
    the other token still expands to something sane instead of a literal template.
    """
    config_root = data if config is None else config
    rule = _BY_FAMILY.get(family)
    if rule is None:
        return UnresolvedSaveRoot(family=family, platform=platform, reason="unknown-family")
    if "*" not in rule.platforms and platform not in rule.platforms:
        return UnresolvedSaveRoot(family=family, platform=platform, reason="platform-not-served")
    if not rule.keys and not rule.defaults:
        return UnresolvedSaveRoot(family=family, platform=platform, reason="no-candidates")

    configured = _configured(rule, values)
    if configured is not None:
        path = _expand(configured, home=home, data=data, config=config_root)
        return ResolvedSaveRoot(path=path, source="config", exists=exists(path))

    for template in rule.defaults:
        path = _expand(template, home=home, data=data, config=config_root)
        if exists(path):
            return ResolvedSaveRoot(path=path, source="default", exists=True)

    first = _expand(rule.defaults[0], home=home, data=data, config=config_root) if rule.defaults else None
    if first is None:
        return UnresolvedSaveRoot(family=family, platform=platform, reason="no-candidates")
    return ResolvedSaveRoot(path=first, source="default", exists=False)
