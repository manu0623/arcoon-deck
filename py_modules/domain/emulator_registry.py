"""The external emulators a Deck install can offer, and which install each save belongs to.

A provider-neutral registry of emulator *definitions*, plus the value an on-disk
probe produces from one: :class:`InstalledEmulator`. It answers the questions the
picker and the save layer both need and neither can invent:

* **Which emulator is this file?** :func:`identify` maps an AppImage or binary
  filename to a definition by prefix, case-insensitively and longest-prefix-first
  — so ``eden.appimage``, ``Eden.appimage`` and ``Eden-Canary.AppImage`` are one
  emulator, and ``Citron`` is never read as ``Citra``.
* **Which install is it?** A provider is part of the identity: EmuDeck's PCSX2 and
  RetroDECK's PCSX2 are the same program with different binaries *and different
  save roots*, so a pick that names only "PCSX2" cannot say where the save goes.
  :func:`qualified_label` is the provider-qualified pick key, and it is what gets
  stored in a per-game or per-platform pick.
* **Are two of these the same build?** :func:`dedupe` collapses byte-identical
  installs — a Deck can hold ``Eden.appimage`` and ``eden.appimage`` with the same
  size and mtime — while keeping genuinely different builds (an ``_old``
  AppImage) as separate entries, because the version is the reason a user wants
  that emulator at all.

The registry is data, not detection: it says where a definition *may* be found
(AppImage prefix, launcher script, flatpak id, binary prefix) and the adapter that
owns the filesystem performs the probes. Nothing here reads a file, stats a path
or executes anything, so every rule below is testable without a Deck.

Platforms are spelled in RomM's own vocabulary (``psx``, ``n3ds``, ``gc``, …),
which is also what :mod:`domain.save_bank`'s ``canonical_platform`` normalises to.

Pure compute: stdlib only, and ``posixpath`` rather than ``os.path`` because every
path this module reasons about is a SteamOS path — a Windows test host must not
decide a different answer from the Deck.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from typing import Literal

# Where an install came from. The provider is not decoration: it decides the
# launch argv, the save root, and how freshness can honestly be reported.
Provider = Literal["retrodeck", "emudeck", "flatpak", "native"]

_PROVIDER_LABELS: dict[Provider, str] = {
    "retrodeck": "RetroDECK",
    "emudeck": "EmuDeck",
    "flatpak": "Flatpak",
    "native": "AppImage",
}

# The libretro frontend's own definition id. It is not a platform-bound emulator:
# a single RetroArch serves every platform a core exists for, so its platform
# tuple is the wildcard rather than an enumeration.
RETROARCH_ID = "retroarch"
ALL_PLATFORMS = "*"

# Platforms with **no libretro core at all**, taken from this repository's own core
# audit: Switch, Wii U, PS3, Vita, Xbox, Xbox 360 and PS4 have none. A definition
# that claims :data:`ALL_PLATFORMS` is a frontend serving whatever cores exist, so
# on these systems it must not be offered — a picker row that launches into "no
# core available" is a promise the machine cannot keep.
PLATFORMS_WITHOUT_LIBRETRO_CORES: frozenset[str] = frozenset(
    {"switch", "wiiu", "ps3", "psvita", "xbox", "xbox360", "ps4"}
)


@dataclass(frozen=True, slots=True)
class DetectionHints:
    """The names an install of one definition goes by, per probe kind.

    All four are matched case-insensitively. ``appimage_prefixes`` and
    ``binary_prefixes`` are filename prefixes (``"eden"`` matches
    ``eden.appimage``); ``launcher_names`` are EmuDeck launcher script basenames
    without ``.sh``; ``flatpak_ids`` are exact application ids.
    """

    appimage_prefixes: tuple[str, ...] = ()
    binary_prefixes: tuple[str, ...] = ()
    launcher_names: tuple[str, ...] = ()
    flatpak_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EmulatorDef:
    """One emulator the picker can offer, independent of where it came from.

    ``platforms`` names the systems this emulator can play in RomM's vocabulary,
    or :data:`ALL_PLATFORMS` for a frontend that covers the catalogue rather than
    one system. ``family`` groups the code lineages that share a save format —
    ``yuzu`` (yuzu, Citron, Eden, Sudachi) and ``ryujinx`` (Ryujinx, kenjinx) are
    two families because their save layouts are incompatible, not variants of one.
    """

    id: str
    display_name: str
    family: str
    platforms: tuple[str, ...]
    hints: DetectionHints
    #: A SteamGridDB game id, for an emulator whose own name ranks below a game of the same
    #: word in SGDB's autocomplete. ``Citron`` is the measured case: the first row for
    #: "Citron" is ``CITRON WORLD FORWARD:ZERO``, which holds no art of any kind, while
    #: ``Citron (Emulator)`` is the second row and holds all five (2026-11-13).
    sgdb_id: int | None = None


@dataclass(frozen=True, slots=True)
class InstalledEmulator:
    """One emulator found on this machine, by one provider, at one path.

    ``version_hint`` is whatever the probe could establish without trusting
    itself: an AppImage's build date from its filename, a flatpak's version, or
    ``None``. It is never a guess — a provider whose version cannot be read says
    so, which is why RetroDECK reports its bundled app version and not a
    per-emulator date it does not have.

    ``aliases`` are other paths holding the *same build* (identical size and
    mtime). They are kept rather than dropped so a log can say why one entry
    stands for two files, and so deleting the chosen copy can offer the other.
    """

    definition: EmulatorDef
    provider: Provider
    path: str
    version_hint: str | None = None
    size: int | None = None
    modified: str | None = None
    aliases: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        """The definition id — the emulator, ignoring which provider it came from."""
        return self.definition.id

    @property
    def label(self) -> str:
        """The provider-qualified pick label, e.g. ``PCSX2 (EmuDeck)``.

        This is the string a per-game or per-platform pick stores. Qualification
        is not cosmetic: the same emulator under two providers writes saves to two
        different places, so an unqualified ``PCSX2`` could not answer where the
        save belongs.
        """
        return qualified_label(self.definition, self.provider)

    def plays(self, platform: str) -> bool:
        """Whether this emulator can play *platform* (RomM's spelling).

        A wildcard definition (RetroArch) serves every platform a *core* exists
        for, so it is denied the ones no core covers — see
        :data:`PLATFORMS_WITHOUT_LIBRETRO_CORES`.
        """
        if ALL_PLATFORMS in self.definition.platforms:
            return platform not in PLATFORMS_WITHOUT_LIBRETRO_CORES
        return platform in self.definition.platforms


# ── The registry ────────────────────────────────────────────────────────────
#
# Ordered roughly by how likely a Deck user meets them. Only definitions whose
# install location we have actually seen on a Deck or read from the emulator's own
# documented layout are listed: an entry here is the promise that its saves can be
# located, and a definition with no save layout must not be offered.

_DEFINITIONS: tuple[EmulatorDef, ...] = (
    EmulatorDef(
        id=RETROARCH_ID,
        display_name="RetroArch",
        family="retroarch",
        platforms=(ALL_PLATFORMS,),
        hints=DetectionHints(
            appimage_prefixes=("retroarch",),
            binary_prefixes=("retroarch",),
            launcher_names=("retroarch",),
            flatpak_ids=("org.libretro.RetroArch",),
        ),
    ),
    EmulatorDef(
        id="dolphin",
        display_name="Dolphin",
        family="dolphin",
        platforms=("gc", "wii"),
        hints=DetectionHints(
            appimage_prefixes=("dolphin",),
            binary_prefixes=("dolphin-emu", "dolphin"),
            launcher_names=("dolphin-emu",),
            flatpak_ids=("org.DolphinEmu.dolphin-emu",),
        ),
    ),
    EmulatorDef(
        id="primehack",
        display_name="PrimeHack",
        family="dolphin",
        platforms=("gc", "wii"),
        hints=DetectionHints(
            appimage_prefixes=("primehack",),
            launcher_names=("primehack",),
            flatpak_ids=("io.github.shiiion.primehack",),
        ),
    ),
    EmulatorDef(
        id="pcsx2",
        display_name="PCSX2",
        family="pcsx2",
        platforms=("ps2",),
        hints=DetectionHints(
            appimage_prefixes=("pcsx2",),
            binary_prefixes=("pcsx2",),
            launcher_names=("pcsx2-qt", "pcsx2"),
            # Measured on the reference Deck: the plugin's own emulator install put
            # ``net.pcsx2.PCSX2`` on this machine, and without this id the scan did not
            # see it — ``flatpak list`` answered the app, ``identify_flatpak`` said no,
            # so PCSX2 never appeared among the standalone emulators it had just
            # installed. The flatpak's own tree (``config/PCSX2/inis/PCSX2.ini``) is the
            # root ``domain.emulator_config`` already names for it.
            flatpak_ids=("net.pcsx2.PCSX2",),
        ),
    ),
    EmulatorDef(
        id="duckstation",
        display_name="DuckStation",
        family="duckstation",
        platforms=("psx",),
        hints=DetectionHints(
            appimage_prefixes=("duckstation",),
            binary_prefixes=("duckstation",),
            launcher_names=("duckstation",),
        ),
    ),
    EmulatorDef(
        id="ppsspp",
        display_name="PPSSPP",
        family="ppsspp",
        platforms=("psp",),
        hints=DetectionHints(
            appimage_prefixes=("ppsspp",),
            binary_prefixes=("ppsspp",),
            launcher_names=("ppsspp",),
            flatpak_ids=("org.ppsspp.PPSSPP",),
        ),
    ),
    EmulatorDef(
        id="melonds",
        display_name="melonDS",
        family="melonds",
        platforms=("nds",),
        hints=DetectionHints(
            appimage_prefixes=("melonds",),
            binary_prefixes=("melonds",),
            launcher_names=("melonds",),
            flatpak_ids=("net.kuribo64.melonDS",),
        ),
    ),
    EmulatorDef(
        id="azahar",
        display_name="Azahar",
        family="citra",
        platforms=("n3ds",),
        hints=DetectionHints(
            appimage_prefixes=("azahar",),
            binary_prefixes=("azahar",),
            launcher_names=("azahar",),
            flatpak_ids=("org.azahar_emu.Azahar",),
        ),
    ),
    EmulatorDef(
        id="lime3ds",
        display_name="Lime3DS",
        family="citra",
        platforms=("n3ds",),
        hints=DetectionHints(
            appimage_prefixes=("lime3ds",),
            launcher_names=("lime3ds",),
        ),
    ),
    EmulatorDef(
        id="citra",
        display_name="Citra",
        family="citra",
        platforms=("n3ds",),
        hints=DetectionHints(
            appimage_prefixes=("citra", "citra-qt"),
            binary_prefixes=("citra",),
            launcher_names=("citra",),
        ),
    ),
    EmulatorDef(
        id="cemu",
        display_name="Cemu",
        family="cemu",
        platforms=("wiiu",),
        hints=DetectionHints(
            appimage_prefixes=("cemu",),
            binary_prefixes=("cemu",),
            launcher_names=("cemu",),
        ),
    ),
    EmulatorDef(
        id="rpcs3",
        display_name="RPCS3",
        family="rpcs3",
        platforms=("ps3",),
        hints=DetectionHints(
            appimage_prefixes=("rpcs3",),
            binary_prefixes=("rpcs3",),
            launcher_names=("rpcs3",),
            flatpak_ids=("net.rpcs3.RPCS3",),
        ),
    ),
    EmulatorDef(
        id="vita3k",
        display_name="Vita3K",
        family="vita3k",
        platforms=("psvita",),
        hints=DetectionHints(
            appimage_prefixes=("vita3k",),
            binary_prefixes=("vita3k",),
            launcher_names=("vita3k",),
        ),
    ),
    # The yuzu lineage. One family because they share ``nand/user/save/<user>/
    # <profile>/<title id>``; four definitions because they are four binaries a
    # user may have installed, and the pick must name the one that runs.
    EmulatorDef(
        id="eden",
        display_name="Eden",
        family="yuzu",
        platforms=("switch",),
        hints=DetectionHints(
            appimage_prefixes=("eden",),
            binary_prefixes=("eden",),
        ),
    ),
    EmulatorDef(
        id="citron",
        display_name="Citron",
        family="yuzu",
        platforms=("switch",),
        hints=DetectionHints(
            appimage_prefixes=("citron",),
            binary_prefixes=("citron",),
            launcher_names=("citron",),
        ),
        # Measured: "Citron" autocompletes to a game first (`CITRON WORLD FORWARD:ZERO`,
        # no assets at all); the emulator's own SGDB entry is the next row.
        sgdb_id=5471414,
    ),
    EmulatorDef(
        id="yuzu",
        display_name="yuzu",
        family="yuzu",
        platforms=("switch",),
        hints=DetectionHints(
            appimage_prefixes=("yuzu",),
            binary_prefixes=("yuzu",),
            launcher_names=("yuzu",),
        ),
    ),
    EmulatorDef(
        id="sudachi",
        display_name="Sudachi",
        family="yuzu",
        platforms=("switch",),
        hints=DetectionHints(
            appimage_prefixes=("sudachi",),
            binary_prefixes=("sudachi",),
        ),
    ),
    # The Ryujinx lineage: ``bis/user/save/<folder id>``, where a title's folder
    # id is allocated by the emulator and resolved only through ``imkvdb.arc``.
    # Same platform, incompatible unit — which is why the family is the key.
    EmulatorDef(
        id="ryujinx",
        display_name="Ryujinx",
        family="ryujinx",
        platforms=("switch",),
        hints=DetectionHints(
            appimage_prefixes=("ryujinx",),
            binary_prefixes=("ryujinx", "publish/Ryujinx"),
            launcher_names=("ryujinx",),
        ),
    ),
    EmulatorDef(
        id="flycast",
        display_name="Flycast",
        family="flycast",
        platforms=("dreamcast",),
        hints=DetectionHints(
            appimage_prefixes=("flycast",),
            binary_prefixes=("flycast",),
            launcher_names=("flycast",),
            flatpak_ids=("org.flycast.Flycast",),
        ),
    ),
    EmulatorDef(
        id="mgba",
        display_name="mGBA",
        family="mgba",
        platforms=("gb", "gbc", "gba"),
        hints=DetectionHints(
            appimage_prefixes=("mgba",),
            binary_prefixes=("mgba",),
            launcher_names=("mgba",),
            flatpak_ids=("io.mgba.mGBA",),
        ),
    ),
    EmulatorDef(
        id="rmg",
        display_name="Rosalie's Mupen GUI",
        family="mupen64plus",
        platforms=("n64",),
        hints=DetectionHints(
            appimage_prefixes=("rmg", "rosalies-mupen"),
            launcher_names=("rmg",),
        ),
    ),
    EmulatorDef(
        id="xemu",
        display_name="xemu",
        family="xemu",
        platforms=("xbox",),
        hints=DetectionHints(
            appimage_prefixes=("xemu",),
            binary_prefixes=("xemu",),
            launcher_names=("xemu-emu", "xemu"),
            flatpak_ids=("app.xemu.xemu",),
        ),
    ),
    EmulatorDef(
        id="xenia",
        display_name="Xenia",
        family="xenia",
        platforms=("xbox360",),
        hints=DetectionHints(
            appimage_prefixes=("xenia",),
            binary_prefixes=("xenia",),
            launcher_names=("xenia",),
        ),
    ),
    EmulatorDef(
        id="shadps4",
        display_name="shadPS4",
        family="shadps4",
        platforms=("ps4",),
        hints=DetectionHints(
            appimage_prefixes=("shadps4",),
            binary_prefixes=("shadps4",),
            launcher_names=("shadps4",),
        ),
    ),
)

_BY_ID: dict[str, EmulatorDef] = {definition.id: definition for definition in _DEFINITIONS}


def all_definitions() -> tuple[EmulatorDef, ...]:
    """Every emulator definition, in registry order."""
    return _DEFINITIONS


def definition(emulator_id: str) -> EmulatorDef | None:
    """The definition for *emulator_id*, or ``None`` when the registry has no such emulator."""
    return _BY_ID.get(emulator_id)


def platforms_for(emulator_id: str) -> tuple[str, ...]:
    """The platforms *emulator_id* can play, or empty for an unknown emulator."""
    known = _BY_ID.get(emulator_id)
    return known.platforms if known is not None else ()


# ── Filename identification ─────────────────────────────────────────────────

# An AppImage is a file whose *name* carries the emulator; the compression suffix
# is not part of the identity, so it is stripped before matching. ``.AppImage_old``
# is EmuDeck's own convention for a previous build, left in place by its updater.
_STRIPPED_SUFFIXES = (".appimage_old", ".appimage", ".AppImage", ".AppImage_old", ".old")


def _matchable(name: str) -> str:
    """A filename reduced to what identification matches on.

    Lowercased, path-stripped, with the AppImage/``_old`` decoration removed. Only
    the decoration goes: ``rpcs3.AppImage_old`` stays ``rpcs3`` (the same emulator,
    a different build) rather than becoming a different emulator.
    """
    base = posixpath.basename(name).strip()
    lowered = base.lower()
    for suffix in _STRIPPED_SUFFIXES:
        if lowered.endswith(suffix.lower()):
            return lowered[: -len(suffix)]
    return lowered


def identify(filename: str) -> EmulatorDef | None:
    """The definition *filename* names, or ``None`` for a file no definition claims.

    Longest prefix wins, so ``citron`` beats a hypothetical ``cit`` and ``eden-nx2``
    resolves to ``eden`` rather than to nothing. A name only *prefix*-matches: an
    unrelated file that merely contains an emulator's name (``my-eden-notes.txt``)
    is not an install.
    """
    candidate = _matchable(filename)
    if not candidate:
        return None
    best: tuple[int, EmulatorDef] | None = None
    for definition in _DEFINITIONS:
        prefixes = (
            definition.hints.appimage_prefixes + definition.hints.binary_prefixes + definition.hints.launcher_names
        )
        for prefix in prefixes:
            lowered = prefix.lower()
            if candidate.startswith(lowered) and (best is None or len(lowered) > best[0]):
                best = (len(lowered), definition)
    return best[1] if best is not None else None


def identify_launcher(script_name: str) -> EmulatorDef | None:
    """The definition an EmuDeck launcher script basename names (``pcsx2-qt.sh``).

    A launcher is a *provider's* command surface, so it matches on the launcher
    names the provider ships rather than on AppImage prefixes — ``dolphin-emu.sh``
    launches Dolphin, and the script is not the binary.
    """
    base = posixpath.basename(script_name).strip().lower()
    if base.endswith(".sh"):
        base = base[: -len(".sh")]
    for definition in _DEFINITIONS:
        if base in (name.lower() for name in definition.hints.launcher_names):
            return definition
    return None


def identify_flatpak(app_id: str) -> EmulatorDef | None:
    """The definition a flatpak application id names, or ``None``."""
    lowered = app_id.strip().lower()
    for definition in _DEFINITIONS:
        if lowered in (candidate.lower() for candidate in definition.hints.flatpak_ids):
            return definition
    return None


# ── Provider and label ──────────────────────────────────────────────────────


def qualified_label(definition_value: EmulatorDef, provider: Provider) -> str:
    """The provider-qualified pick label for one definition: ``PCSX2 (EmuDeck)``.

    This string is the pick key. It is built here, in one place, because a label
    written anywhere else drifts from the one the resolver looks up — and a pick
    that does not resolve degrades to a default silently, which is the failure
    mode this qualification exists to prevent.
    """
    return f"{definition_value.display_name} ({_PROVIDER_LABELS[provider]})"


def dedupe(installs: list[InstalledEmulator]) -> list[InstalledEmulator]:
    """Collapse installs of the *same build* into one entry, keeping the rest as aliases.

    Two paths are the same build when they name the same definition, came from the
    same provider, and agree on both size and mtime — the case a Deck produces with
    ``Eden.appimage`` beside ``eden.appimage``. The provider is part of the key: an
    EmuDeck launcher and the AppImage it launches are two different things to run
    even when they would write the same bytes, and collapsing them would drop an
    install the user can see on disk. The survivor is chosen by path order so the
    answer never depends on directory-listing order, and the others ride along in
    ``aliases``.

    A build that differs in size or mtime is *not* collapsed: ``rpcs3.AppImage_old``
    beside a newer ``rpcs3.AppImage`` is two versions, and which one runs is a
    decision only the user can make.
    """
    survivors: list[InstalledEmulator] = []
    buckets: dict[tuple[str, Provider, int | None, str | None], list[InstalledEmulator]] = {}
    for install in installs:
        key = (install.id, install.provider, install.size, install.modified)
        buckets.setdefault(key, []).append(install)
    for group in buckets.values():
        ordered = sorted(group, key=lambda install: install.path)
        first, rest = ordered[0], ordered[1:]
        if rest:
            first = InstalledEmulator(
                definition=first.definition,
                provider=first.provider,
                path=first.path,
                version_hint=first.version_hint,
                size=first.size,
                modified=first.modified,
                aliases=tuple(install.path for install in rest),
            )
        survivors.append(first)
    return sorted(survivors, key=lambda install: (install.id, install.path))


def for_platform(installs: list[InstalledEmulator], platform: str) -> list[InstalledEmulator]:
    """Every install that can play *platform*, in stable provider/path order."""
    return sorted(
        (install for install in installs if install.plays(platform)),
        key=lambda install: (install.id, install.provider, install.path),
    )


def labels(installs: list[InstalledEmulator]) -> list[str]:
    """The distinct pick labels these installs offer, in order.

    Distinct because two installs of one provider (two RPCS3 builds) share a label:
    the pick names *which emulator under which provider*, and choosing between two
    builds of it is a separate question.
    """
    seen: list[str] = []
    for install in installs:
        if install.label not in seen:
            seen.append(install.label)
    return seen
