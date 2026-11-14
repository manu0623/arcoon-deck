"""The save bank: Arcoon Deck's own save tree, laid out in Argosy's shapes.

This is the second layer of the launcher — the one that owns where saves live —
and it exists because the first layer no longer asks RetroDECK. Arcoon Deck's older
save math (``domain.save_path.resolve_save_dir`` plus a ``<rom_name>.<ext>``
probe) is RetroArch's naming rule and nothing else: it can only ever address one
single-token file per ROM, so every memory-card platform is refused upstream as
an unsupported shape.

Argosy solves the same problem per platform, by turning the game's own identity
(``save_id``) into a directory or file path. The shapes below are ports of its
handlers — ``FolderSaveHandler``, ``PrefixBundleFolderHandler``,
``CategorySplitFolderHandler``, ``N3dsFolderHandler``, ``Ps2FolderHandler``,
``SwitchSaveHandler``, ``GciSaveHandler``, ``DreamcastSaveHandler`` — and the
point of the port is convergence: a save written here must be the unit an
Argosy device would have written, or the two clients disagree about what a save
*is* and the server accumulates two incompatible archives of the same game.

Three things are load-bearing and none of them is obvious from a path alone:

* **The save unit is a member set, not a path.** PS2 and PSP bundle several
  sibling directories; GameCube bundles every ``.gci`` whose header carries the
  disc's game code. An upload of "the folder the answer named" ships a fraction
  of the save.
* **Archive root names are part of the wire format.** A 3DS archive is rooted at
  ``data``/``extdata`` and never names its title; a PS2 archive is rooted at the
  card. Root names decide whether a restore can identify an archive at all.
* **Some identities cannot be invented.** A Switch save needs a profile
  directory that already exists, and a PS2 save needs a card, because a guessed
  one writes to a place the emulator never reads. Those answer ``needs`` instead.

Everything here is pure: no I/O, no service/adapter imports, stdlib only. The
caller supplies a directory listing (``tree``) when it has scanned the bank, and
this module decides what that listing means. A directory that exists appears as
a key in ``tree`` even when it holds nothing, which is how "present but empty"
stays distinguishable from "absent".
"""

from __future__ import annotations

import os
import re
import struct
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# The bank's root directory below the plugin's data directory. One name, owned
# here, because every path this module builds hangs off it.
SAVE_BANK_DIR_NAME = "saves"

# PCSX2 writes a folder memory card as a directory ending ``.ps2`` (or holding
# this file), and reads the card only when the superblock's byte 0x16 is 0x6F.
PS2_SUPERBLOCK_FILE = "_pcsx2_superblock"
PS2_SUPERBLOCK_SIZE = 0x2000
_PS2_FORMATTED_MARKER_OFFSET = 0x16
_PS2_FORMATTED_MARKER = 0x6F

_3DS_BASE_CATEGORY = "00040000"
_3DS_EXTDATA_HIGH = "00000000"
_3DS_EXTDATA_SHIFT = 8

_HEX8 = re.compile(r"[0-9a-f]{8}")

# Argosy's PS2 rules, ported verbatim: a region-prefixed stem is taken as given,
# a bare serial gets its prefix derived from the third character of the serial
# code, and the prefix is dropped entirely only as a last resort.
_PS2_REGION_PREFIXED = re.compile(r"^B[AEI][A-Z]{4}")
_PS2_BARE_SERIAL = re.compile(r"^([A-Z]{4})(\d+.*)$")

# Flycast's own sanitisation of a disc's product number before it builds a VMU
# file name; the standalone build additionally replaces a double quote.
_DREAMCAST_RESERVED = frozenset({" ", "/", "\\", ":", "*", "?", "|", "<", ">"})


class SaveUsage(StrEnum):
    """How a platform spends a save id on disk — the contract between id and path.

    Getting this wrong mismatches saves silently rather than failing, which is
    why it is a field of the layout rather than a fact buried in each branch.
    """

    FOLDER_EXACT = "folder_exact"
    FOLDER_PREFIX = "folder_prefix"
    FILE_EXACT = "file_exact"
    FILE_PREFIX = "file_prefix"
    FOLDER_SPLIT = "folder_split"


class SaveFamily(StrEnum):
    """Which resolution rule a platform follows.

    Named after the shape rather than the platform, because two platforms share
    a rule far more often than they share a folder name (PSP and PS3 are one
    family; Wii and Wii U are one family).
    """

    LIBRETRO_FILE = "libretro_file"
    EXACT_FOLDER = "exact_folder"
    PREFIX_BUNDLE = "prefix_bundle"
    N3DS_TITLE = "n3ds_title"
    CATEGORY_SPLIT = "category_split"
    PS2_CARD = "ps2_card"
    SWITCH_TITLE = "switch_title"
    DREAMCAST_VMU = "dreamcast_vmu"
    GCI_SET = "gci_set"


class ArchiveRootMatch(StrEnum):
    """How strongly an archive's top-level entry corresponds to the save it claims.

    The order is the strength order: ``EXACT`` then ``PREFIX`` then
    ``CONTAINS``, and ``UNIDENTIFIED`` last because such a root names no title
    at all and the resolved destination is the only thing identifying it.
    """

    EXACT = "exact"
    PREFIX = "prefix"
    CONTAINS = "contains"
    UNIDENTIFIED = "unidentified"


@dataclass(frozen=True, slots=True)
class SaveMember:
    """One part of a save unit, and the name it takes at the top of its archive.

    ``archive_root`` is deliberately not the member's own basename for every
    platform: a 3DS title directory lands under ``data``, and a PS2 game folder
    lands under its own name inside a card-rooted archive.
    """

    path: str
    archive_root: str
    is_directory: bool


@dataclass(frozen=True, slots=True)
class SaveUnit:
    """Everything a save of one game consists of, in the bank's own terms.

    ``place_path`` is where a restore unpacks: the member itself for a
    single-directory save, the card for PS2, and the container directory for a
    prefix bundle. ``conflicts`` is non-empty only where the layout refuses to
    choose (two PS2 cards holding the same game); a caller must then stop, not
    pick, because picking overwrites another card's save.
    """

    platform: str
    family: SaveFamily
    usage: SaveUsage
    base: str
    place_path: str | None
    members: tuple[SaveMember, ...]
    identified: bool
    container: str | None = None
    conflicts: tuple[str, ...] = ()
    needs: tuple[str, ...] = ()

    @property
    def archive_roots(self) -> tuple[str, ...]:
        """The top-level archive entry names this unit is written under."""
        return tuple(member.archive_root for member in self.members)

    @property
    def paths(self) -> tuple[str, ...]:
        """The on-disk paths this unit consists of."""
        return tuple(member.path for member in self.members)

    @property
    def usable(self) -> bool:
        """Whether the unit can be read or written at all.

        An ambiguous unit and one whose identity could not be derived are both
        unusable, and both say why in ``conflicts``/``needs`` so a caller can
        report the reason instead of a bare "no save".
        """
        return not self.conflicts and bool(self.members)


@dataclass(frozen=True, slots=True)
class SaveLayout:
    """One platform's save rule: where it lives and how its id becomes a path."""

    platform: str
    family: SaveFamily
    usage: SaveUsage
    subdir: tuple[str, ...]
    extensions: tuple[str, ...] = ("srm",)
    identified: bool = True
    container: str | None = None
    unidentified_roots: frozenset[str] = frozenset()
    category_pattern: str | None = None
    # The tail of ``subdir`` that the *emulator* builds beneath whatever folder it is
    # handed, for platforms whose own tree already ends in the layout's last components.
    # PPSSPP is the case this exists for: handed a folder, it creates ``PSP/SAVEDATA``
    # inside it, so handing it ``saves/psp/PSP/SAVEDATA`` produced a doubled
    # ``SAVEDATA/PSP/SAVEDATA`` that no lookup reads.
    core_subdir: tuple[str, ...] = ()

    @property
    def tree_depth(self) -> int:
        """How many directory levels below the base a discovery rule has to see.

        A prefix rule reads the base's children and a per-ROM file reads the base itself,
        so two levels cover both. A 3DS title is reached through
        ``id0/id1/title/<category>/<low id>/data``: the rule enumerates each of those
        levels rather than inventing one, which is why it has to be handed all seven.
        """
        return 7 if self.family is SaveFamily.N3DS_TITLE else 2


# The platforms whose saves are not a plain per-ROM file. Everything absent from
# this table is the libretro default — ``<rom_stem>.srm`` in ``saves/<slug>`` —
# which is what the bank needs for the ~150 core/platform pairs that really do
# write one file per game.
_PLATFORM_LAYOUTS: dict[str, SaveLayout] = {
    "vita": SaveLayout("vita", SaveFamily.EXACT_FOLDER, SaveUsage.FOLDER_EXACT, ("vita",)),
    "psp": SaveLayout(
        "psp",
        SaveFamily.PREFIX_BUNDLE,
        SaveUsage.FOLDER_PREFIX,
        ("psp", "PSP", "SAVEDATA"),
        core_subdir=("PSP", "SAVEDATA"),
    ),
    "ps3": SaveLayout("ps3", SaveFamily.PREFIX_BUNDLE, SaveUsage.FOLDER_PREFIX, ("ps3", "savedata")),
    "ps2": SaveLayout("ps2", SaveFamily.PS2_CARD, SaveUsage.FOLDER_PREFIX, ("ps2",), container="ps2_folder_card"),
    "n3ds": SaveLayout(
        "n3ds",
        SaveFamily.N3DS_TITLE,
        SaveUsage.FOLDER_SPLIT,
        ("3ds", "sdmc", "Nintendo 3DS"),
        identified=False,
        unidentified_roots=frozenset({"data", "extdata"}),
    ),
    "wii": SaveLayout(
        "wii",
        SaveFamily.CATEGORY_SPLIT,
        SaveUsage.FOLDER_SPLIT,
        ("wii", "title", "00010000"),
        category_pattern=r"0001[0-9a-f]{4}",
    ),
    "wiiu": SaveLayout(
        "wiiu",
        SaveFamily.CATEGORY_SPLIT,
        SaveUsage.FOLDER_SPLIT,
        ("wiiu", "mlc01", "usr", "save", "00050000"),
        category_pattern=r"0005[0-9a-f]{4}",
    ),
    "switch": SaveLayout("switch", SaveFamily.SWITCH_TITLE, SaveUsage.FOLDER_EXACT, ("switch", "nand", "user", "save")),
    "gc": SaveLayout("gc", SaveFamily.GCI_SET, SaveUsage.FILE_PREFIX, ("gc", "Card A")),
    "dreamcast": SaveLayout("dreamcast", SaveFamily.DREAMCAST_VMU, SaveUsage.FILE_EXACT, ("dreamcast",)),
}

#: The families a launch the plugin itself writes (a RetroArch appendconfig) redirects
#: into the bank. A standalone emulator reaches the bank through a save link instead, so
#: its families are the ones ``domain.emulator_save_link`` declares — and the two sets
#: are kept apart because a redirect the plugin did not make must not be claimed here.
#: Families whose launch the plugin redirects into the bank itself — so the bank is
#: genuinely where that launch writes, and a lookup may answer from it.
#:
#: ``PS2_CARD`` is here because both shapes of ps2 launch are redirected: a standalone
#: PCSX2 has its ``config/PCSX2/memcards`` folder linked at the bank (a ``SavePoint``),
#: and the libretro core's own card folder, ``system/pcsx2/memcards``, is linked at the
#: same directory because the core ignores ``savefile_directory`` for memory cards —
#: measured on the reference Deck, where a redirected launch still wrote its card into
#: the emulator's system tree.
LAUNCH_REDIRECTED_FAMILIES = frozenset({SaveFamily.LIBRETRO_FILE, SaveFamily.PREFIX_BUNDLE, SaveFamily.PS2_CARD})

# RomM, Argosy and RomM's own client pick different spellings for four systems.
# Normalising here means a caller never has to know which vocabulary it holds.
_PLATFORM_ALIASES: dict[str, str] = {
    "3ds": "n3ds",
    "n3ds": "n3ds",
    "ngc": "gc",
    "gamecube": "gc",
    "gcn": "gc",
    "psvita": "vita",
    "vita": "vita",
    "dc": "dreamcast",
    "dreamcast": "dreamcast",
    "psx": "psx",
    "ps1": "psx",
}


def canonical_platform(platform: str) -> str:
    """The bank's own name for *platform*, so one system has one folder."""
    key = platform.strip().lower()
    return _PLATFORM_ALIASES.get(key, key)


def layout_for(platform: str) -> SaveLayout:
    """The save rule for *platform*, falling back to the libretro per-ROM file."""
    key = canonical_platform(platform)
    known = _PLATFORM_LAYOUTS.get(key)
    if known is not None:
        return known
    return SaveLayout(
        platform=key,
        family=SaveFamily.LIBRETRO_FILE,
        usage=SaveUsage.FILE_EXACT,
        subdir=(key,),
    )


def restores_by_extraction(platform: str) -> bool:
    """Whether this platform's save is a member set that RomM ships as one archive.

    GameCube is the family this holds for, and the failure it prevents is
    measured: the unit is every ``.gci`` whose header carries the disc's code,
    RomM stores that set as a single zip, and writing the zip into the card
    folder leaves Dolphin reading an empty card — the game offers to make a new
    one while the save sits beside it unread. Restoring therefore means
    extracting the archive's members into the directory the answer names.

    Only a family RomM carries as ONE archive answers True: the restore unpacks that
    archive into the directory the answer names. GameCube's set and a Switch title
    folder are flat member sets; a PSP save is the set of ``<DISC_ID>*`` folders, which
    extracts back into the ``SAVEDATA`` tree exactly as it was packed.

    A 3DS title answers True for the same reason as PSP, one level deeper: the unit is
    ``data`` (and often ``extdata``) — directories of files the emulator names — so a
    restore that renamed the zip beside the title tree would leave Azahar reading nothing,
    the failure this rule was written for. The upload half already packed it (a
    ``title-dir`` answer is what decides that), so leaving this False made the pair
    asymmetric: it would have uploaded a save it could not put back.
    """
    return layout_for(platform).family in {
        SaveFamily.GCI_SET,
        SaveFamily.SWITCH_TITLE,
        SaveFamily.PREFIX_BUNDLE,
        SaveFamily.N3DS_TITLE,
        # A PS2 folder card's unit is the game's own folder INSIDE the card, and RomM
        # carries it as one archive; writing that zip into the card directory leaves
        # PCSX2 reading a card with no such save (measured: the upload packed
        # ``<rom>.zip``, and a restore that dropped the zip beside ``Mcd001.ps2`` left
        # the game offering to create a memory card). Extracting puts the folder back
        # where PCSX2 reads it.
        SaveFamily.PS2_CARD,
        # A Wii title's save is the files inside its ``data/`` folder, and RomM carries them
        # as one ``<rom>.zip`` packed from that folder. Measured on the reference Deck: the
        # download landed the zip in the staging directory beside the title and nothing was
        # extracted, so the save that had just been uploaded never came back.
        SaveFamily.CATEGORY_SPLIT,
    }


def save_bank_root(data_dir: str) -> str:
    """The bank's root inside the plugin's data directory."""
    return os.path.join(data_dir, SAVE_BANK_DIR_NAME)


def save_bank_base(bank_root: str, platform: str) -> str:
    """The directory *platform*'s saves live in, or are constructed in."""
    return os.path.join(bank_root, *layout_for(platform).subdir)


def describe_unit(
    layout: SaveLayout,
    *,
    bank_root: str,
    save_id: str | None = None,
    rom_stem: str | None = None,
    tree: Mapping[str, Sequence[str]] | None = None,
    header_matched: Sequence[str] = (),
    base: str | None = None,
) -> SaveUnit:
    """Resolve one game's save unit from what the bank already holds.

    *tree* maps a directory path to the names it contains, as one scan of the
    bank reports them; a directory that exists is a key even when it holds
    nothing. It is only consulted by the layouts that must discover an
    intermediate level (3DS ``id0``/``id1``, a Switch profile, a PS2 card) —
    those levels are enumerated and never invented, because a fabricated one
    points at a directory the emulator does not read.

    *header_matched* carries the GameCube members a caller identified by reading
    each ``.gci`` header, which is the only reliable membership test there: a
    hack and its base disc share a filename but not necessarily a game code, and
    a bundle is every ``.gci`` whose header carries the disc's code.

    *base* names the directory the emulator itself keeps this platform's saves under,
    for a caller answering for an emulator that does not write into the bank at all.
    It is the same level of the tree the bank's own ``<root>/<platform subdir>`` names,
    so every family rule below applies unchanged — the platform prefix in
    ``layout.subdir`` is a property of the bank's tree, not of a save layout.
    """
    base = base if base is not None else save_bank_base(bank_root, layout.platform)
    listing: Mapping[str, Sequence[str]] = tree or {}

    match layout.family:
        case SaveFamily.LIBRETRO_FILE:
            return _libretro_file(layout, base, rom_stem)
        case SaveFamily.EXACT_FOLDER:
            return _exact_folder(layout, base, save_id)
        case SaveFamily.PREFIX_BUNDLE:
            return _prefix_bundle(layout, base, save_id, listing)
        case SaveFamily.N3DS_TITLE:
            return _n3ds_title(layout, base, save_id, listing)
        case SaveFamily.CATEGORY_SPLIT:
            return _category_split(layout, base, save_id)
        case SaveFamily.PS2_CARD:
            return _ps2_card(layout, base, save_id, listing)
        case SaveFamily.SWITCH_TITLE:
            return _switch_title(layout, base, save_id, listing)
        case SaveFamily.DREAMCAST_VMU:
            return _dreamcast_vmu(layout, base, save_id)
        case _:
            return _gci_set(layout, base, save_id, listing, header_matched)


def matches_name(
    layout: SaveLayout,
    name: str,
    save_id: str | None = None,
    rom_stem: str | None = None,
) -> bool:
    """Whether *name* (one direct child of the base) belongs to this save.

    The single membership predicate a scanning caller needs, so no adapter grows
    its own copy of a platform's match rule. False whenever the identity the
    rule needs is missing — a caller with no id has no answer, not a permissive
    one.
    """
    match layout.family:
        case SaveFamily.LIBRETRO_FILE:
            return bool(rom_stem) and name.lower().startswith(f"{rom_stem.lower()}.")
        case SaveFamily.EXACT_FOLDER:
            return bool(save_id) and name.lower() == save_id.strip().lower()
        case SaveFamily.PREFIX_BUNDLE:
            return bool(save_id) and name.lower().startswith(save_id.strip().lower())
        case SaveFamily.PS2_CARD:
            return bool(save_id) and ps2_name_matches(name, save_id)
        case SaveFamily.N3DS_TITLE | SaveFamily.CATEGORY_SPLIT:
            low = _low_id(save_id)
            return low is not None and name.lower() == low
        case SaveFamily.DREAMCAST_VMU:
            return bool(save_id) and name.lower() == f"{dreamcast_vmu_stem(save_id).lower()}.a1.bin"
        case SaveFamily.SWITCH_TITLE:
            title = base_application_id(save_id) if save_id else None
            return title is not None and name.lower() == title
        case _:
            return bool(save_id) and name.lower().endswith(".gci") and save_id.strip().upper() in name.upper()


def match_archive_root(layout: SaveLayout, root_name: str, save_id: str | None = None) -> ArchiveRootMatch | None:
    """How strongly an archive's top entry corresponds to the save it claims.

    Mirrors Argosy's four tiers in its own order, weakest last. An archive that
    matches on none of them is not this save and must never be unpacked over it,
    which is why this answers ``None`` rather than a permissive default.
    """
    root = root_name.strip().rstrip("/")
    if not root:
        return None
    if root in layout.unidentified_roots:
        return ArchiveRootMatch.UNIDENTIFIED
    if save_id is None:
        return None

    candidate = save_id.strip()
    # Every tier reads the WHOLE entry name, never its last segment: "other/<id>"
    # is not the save's own root, and it must fall through to CONTAINS rather
    # than matching as a prefix because of how the path happens to end.
    if _normalized(root) == _normalized(candidate):
        return ArchiveRootMatch.EXACT
    if matches_name(layout, root, save_id) or _normalized(root).startswith(_normalized(candidate)):
        return ArchiveRootMatch.PREFIX
    if _normalized(candidate) and _normalized(candidate) in _normalized(root):
        return ArchiveRootMatch.CONTAINS
    return None


@dataclass(frozen=True, slots=True)
class ArchivePlacement:
    """Where each member of an over-packed archive lands, and what is not this save.

    ``placements`` pairs the archive's own member names with the names they take under the
    destination; ``refused`` names the members the archive carries but the save does not own,
    which are never written.
    """

    placements: tuple[tuple[str, str], ...]
    refused: tuple[str, ...]


def place_archive_members(members: Sequence[str], destination: str) -> ArchivePlacement | None:
    """Where the members of an archive belong under *destination*, or ``None`` for a flat one.

    RomM holds whatever bytes a client gave it, and clients pack at different depths. A client
    that packs the unit folder itself names every member ``<folder>/<file>``; one that packs the
    folder's parent — Wii's title folder, which holds both ``data/`` (the save) and ``content/``
    (the emulator's installed title metadata) — names them ``<title>/data/<file>``. Both are
    relative to a directory ABOVE the destination, so writing them as they are nests the save,
    and the emulator reads an empty folder while the bytes sit one level down. Measured on the
    reference Deck: a Switch save restored to ``<title>/<title>/savedata1.bin`` and Eden offered
    a new game (ADR-0066), and Wii rom 6938's newest server save is packed from its title folder.

    So the heading is aligned with the destination's own path: when every member sits under one
    heading that names a component of *destination*, the members are read from that heading's
    directory down, and each one is placed relative to *destination*. A member that then falls
    outside *destination* is not part of this save — Wii's ``content/title.tmd`` is the
    emulator's, not the game's — and is refused rather than written.

    ``None`` when the archive is flat (the shape this plugin packs), mixed, headed by a name that
    is not on the destination's path (PSP's ``<DISC_ID>DATA00`` beside it), or when nothing would
    be placed at all: a caller only changes an archive it can align, never on a guess.
    """
    parts = [part for part in destination.replace("\\", "/").split("/") if part not in ("", ".")]
    if not parts or not members:
        return None
    normalized = tuple(_zip_member_name(member) for member in members)
    headings = {name.partition("/")[0] for name in normalized}
    if len(headings) != 1:
        return None
    # The deepest place the heading holds on the destination's own path: aligning with the
    # shallowest would read the archive from further up than it was packed.
    heading = next(iter(headings))
    positions = [index for index, part in enumerate(parts) if part == heading]
    if not positions:
        return None
    below = parts[positions[-1] + 1 :]
    placements: list[tuple[str, str]] = []
    refused: list[str] = []
    for member, name in zip(members, normalized, strict=True):
        tail = name.partition("/")[2]
        if not tail:
            # A member that IS the heading names a directory, not a file this rule can place.
            return None
        tail_parts = tail.split("/")
        if below:
            if tail_parts[: len(below)] != below:
                refused.append(member)
                continue
            tail_parts = tail_parts[len(below) :]
            if not tail_parts:
                return None
        placements.append((member, "/".join(tail_parts)))
    if not placements:
        return None
    return ArchivePlacement(placements=tuple(placements), refused=tuple(refused))


def _zip_member_name(member: str) -> str:
    """A member name as ``/``-separated parts without a leading ``./``, as a zip spells it."""
    name = member.replace("\\", "/")
    while name.startswith("./"):
        name = name[2:]
    return name


def ps2_name_matches(folder_name: str, save_id: str) -> bool:
    """Whether a card entry belongs to the game *save_id* names.

    Comparison is on a normalised form — ``-`` and ``_`` stripped, uppercased —
    because the region-prefixed stem and the folder the emulator writes differ
    only in punctuation. A wrong region prefix still leaves the disc
    identifiable, so the prefix-less form is the last resort rather than a
    failure.
    """
    folder = _normalized(folder_name)
    stem = ps2_stem(save_id)
    if folder.startswith(stem):
        return True
    return _without_region_prefix(folder).startswith(_without_region_prefix(stem))


def ps2_stem(save_id: str) -> str:
    """Sigil's PS2 stem for *save_id*, deriving the region prefix when it is bare."""
    cleaned = _normalized(save_id)
    if _PS2_REGION_PREFIXED.match(cleaned):
        return cleaned
    bare = _PS2_BARE_SERIAL.match(cleaned)
    if bare is None:
        return cleaned
    code, rest = bare.groups()
    return f"{_ps2_territory_prefix(code)}{code}{rest}"


def dreamcast_vmu_stem(save_id: str) -> str:
    """The disc's product number sanitised the way Flycast sanitises it.

    Flycast names port A1's card after the disc's IP.BIN id, replacing each
    reserved character with an underscore; the file name is that stem plus
    ``.A1.bin``.
    """
    return "".join("_" if char in _DREAMCAST_RESERVED else char for char in save_id.strip())


def base_application_id(title_id: str, *, known_applications: Sequence[str] = ()) -> str | None:
    """A Switch title id as the *application* id, or ``None`` when it is not one.

    The emulator keeps a save only under the application id. A merged NSP or XCI
    can report its patch (``application + 0x800``) or add-on content
    (``(application & ~0xFFF) + 0x1000 + index``) instead, and a save built from
    either lands where nothing reads it.

    A patch maps back on its own. Add-on content does not: its form collides
    with ordinary application ids, so it is only recognised against a known
    application the caller supplies. Without one the id stands as given, because
    rewriting it by a guess would move the save somewhere the emulator never
    looks.
    """
    text = title_id.strip().lower()
    if len(text) != 16 or any(char not in "0123456789abcdef" for char in text):
        return None
    if not text.startswith("01"):
        return None
    value = int(text, 16)
    if value & 0xFFF == 0x800:
        return f"{value - 0x800:016x}"
    for known in known_applications:
        candidate = known.strip().lower()
        if len(candidate) != 16 or any(char not in "0123456789abcdef" for char in candidate):
            continue
        span = int(candidate, 16) & ~0xFFF
        if span + 0x1000 <= value < span + 0x2000:
            return candidate
    return text


def gci_filename(maker_code: str, game_id: str, internal_filename: str) -> str:
    """The name a GameCube save takes on disk: ``<maker>-<id>-<internal>.gci``.

    The internal name is 32 raw bytes off the GCI header, so it is whatever the
    file carries rather than a name a volume accepts; separators in it are
    folded so they cannot steer the built path out of the card directory.
    """
    safe = internal_filename.replace("/", "_").replace("\\", "_").replace("\x00", "").strip()
    return f"{maker_code.strip()}-{game_id.strip()}-{safe}.gci"


def is_formatted_ps2_superblock(payload: bytes | None) -> bool:
    """Whether a folder memory card's superblock is one PCSX2 will index.

    PCSX2 loads the full 0x2000-byte superblock and indexes the card only when
    byte 0x16 is 0x6F; anything shorter, including an empty file, is treated as
    an unformatted card whose folders the game never sees.
    """
    return (
        payload is not None
        and len(payload) >= PS2_SUPERBLOCK_SIZE
        and payload[_PS2_FORMATTED_MARKER_OFFSET] == _PS2_FORMATTED_MARKER
    )


def ps2_card_superblock() -> bytes:
    """The standard 8 MB folder-card superblock, as PCSX2 writes it.

    A restore must leave the card holding a formatted superblock or the game
    reads an empty card. A formatted card is left byte-for-byte alone; this is
    only for one that is missing, short, or unformatted. The superblock itself
    never travels in an archive.
    """
    data = bytearray(b"\xff" * PS2_SUPERBLOCK_SIZE)
    data[0:28] = b"Sony PS2 Memory Card Format "[:28].ljust(28, b"\x00")
    data[28:40] = b"1.2.0.0".ljust(12, b"\x00")
    # page length, pages per cluster, pages per block, unused half-word
    struct.pack_into("<HHHH", data, 40, 512, 2, 16, 0xFF00)
    # clusters per card, alloc offset, alloc end, rootdir cluster, backup blocks
    struct.pack_into("<iiiii", data, 48, 8192, 8192 // 0x100 + 9, 8192 - 0x10 - (8192 // 0x100 + 9), 0, 1023)
    struct.pack_into("<i", data, 68, 1022)
    struct.pack_into("<q", data, 72, 0)
    struct.pack_into("<i", data, 80, 8)
    data[84 : 84 + 31 * 4] = b"\x00" * (31 * 4)
    data[84 + 31 * 4 : 84 + 63 * 4] = b"\xff" * (32 * 4)
    data[336] = 2  # card type: PS2
    data[337] = 0x52  # card flags
    return bytes(data)


# -- resolution rules --------------------------------------------------------


def _libretro_file(layout: SaveLayout, base: str, rom_stem: str | None) -> SaveUnit:
    """The libretro default: one file per ROM, named after the ROM."""
    if not rom_stem:
        return _unit(layout, base, None, (), needs=("rom_stem",))
    members = tuple(
        SaveMember(
            path=os.path.join(base, f"{rom_stem}.{extension}"),
            archive_root=f"{rom_stem}.{extension}",
            is_directory=False,
        )
        for extension in layout.extensions
    )
    return _unit(layout, base, members[0].path, members)


def _exact_folder(layout: SaveLayout, base: str, save_id: str | None) -> SaveUnit:
    """One directory named exactly for the id (Vita)."""
    if not save_id:
        return _unit(layout, base, None, (), needs=("save_id",))
    member = SaveMember(path=os.path.join(base, save_id), archive_root=save_id, is_directory=True)
    return _unit(layout, base, member.path, (member,))


def _prefix_bundle(
    layout: SaveLayout, base: str, save_id: str | None, listing: Mapping[str, Sequence[str]]
) -> SaveUnit:
    """Several sibling directories sharing the id as a prefix (PSP, PS3).

    The unit is the parent plus a prefix predicate, never one folder: a game
    commonly writes ``ULUS10064DATA00`` beside ``ULUS10064SETTINGS``, and
    uploading one of them leaves the rest of the save behind.
    """
    if not save_id:
        return _unit(layout, base, base, (), needs=("save_id",))
    matched = tuple(name for name in _children(listing, base) if _prefix_match(name, save_id))
    members = tuple(SaveMember(path=os.path.join(base, name), archive_root=name, is_directory=True) for name in matched)
    return _unit(layout, base, base, members)


def _archive_root(base: str, member_path: str) -> str:
    """A member's name inside its answer's directory, in the archive's own spelling."""
    return os.path.relpath(member_path, base).replace(os.sep, "/")


def _n3ds_title(layout: SaveLayout, base: str, save_id: str | None, listing: Mapping[str, Sequence[str]]) -> SaveUnit:
    """One 3DS title's ``data`` tree and its derived ``extdata`` tree.

    ``save_id`` arrives already split (``00040000/00033500``) and the directory
    tree below it is the id used as-is. Some titles keep every byte of progress
    in extdata and never create ``data``, which is why either directory alone
    counts as the save and a title with neither has none.
    """
    key = _n3ds_key(save_id)
    if key is None:
        return _unit(layout, base, None, (), needs=("save_id",))
    category, low_id, extdata_id = key

    id0 = _first_child(listing, base)
    if id0 is None:
        return _unit(layout, base, None, (), needs=("id0",))
    id1 = _first_child(listing, os.path.join(base, id0))
    if id1 is None:
        return _unit(layout, base, None, (), needs=("id1",))

    title_root = os.path.join(base, id0, id1)
    title_data = os.path.join(title_root, "title", category, low_id, "data")
    extdata = os.path.join(title_root, "extdata", _3DS_EXTDATA_HIGH, extdata_id) if extdata_id else None

    # The archive roots are each member's path INSIDE the answer's directory — the one
    # invariant every packed unit shares with a prefix bundle, where the member is the
    # folder's own name. A 3DS title sits several levels below that directory, so its root
    # spells those levels out (`id0/id1/title/<category>/<low id>/data`). Naming it "data"
    # instead made the packed unit look for `<base>/data` — measured on the reference Deck
    # as a FileNotFoundError while packing a game whose save was right there — and would
    # have restored a download into a folder Azahar does not read.
    members = []
    if title_data in listing:
        members.append(SaveMember(path=title_data, archive_root=_archive_root(base, title_data), is_directory=True))
    if extdata is not None and extdata in listing:
        members.append(SaveMember(path=extdata, archive_root=_archive_root(base, extdata), is_directory=True))

    # The resolved path stays the title ``data`` directory whenever it exists, so
    # rows written before extdata joined the unit keep their paths; a title with
    # extdata only resolves to the extdata directory.
    place_path = title_data if title_data in listing or extdata is None or not members else extdata
    # The title IS named at this point: the save id split into a category and a low id,
    # and the console's id0/id1 were discovered rather than invented. So an empty title
    # folder is a game that has not saved yet — the place a server save lands in — not an
    # unidentified one. Measured on the reference Deck: with the local folder removed, a
    # download refused with ``save_shape_unsupported`` and the save could never come back.
    return _unit(layout, base, place_path, tuple(members), identified=True)


def _category_split(layout: SaveLayout, base: str, save_id: str | None) -> SaveUnit:
    """A title id split into a category directory and a low-id folder (Wii, Wii U).

    The base is already the category directory, so only the low half names the
    folder. Joining the split id whole points at ``00050000/00050000/<low>``,
    which is the bug this rule exists to prevent.
    """
    low_id = _low_id(save_id)
    if low_id is None:
        return _unit(layout, base, None, (), needs=("save_id",))
    category = _category_of(save_id)
    container = _category_base(base, category, layout.category_pattern)
    member = SaveMember(path=os.path.join(container, low_id), archive_root=low_id, is_directory=True)
    return _unit(layout, container, member.path, (member,))


def _ps2_card(layout: SaveLayout, base: str, save_id: str | None, listing: Mapping[str, Sequence[str]]) -> SaveUnit:
    """A game's own folders on a folder memory card.

    The save unit is the card, but an upload must bundle only the folders this
    game owns: the card holds every game's saves, and an upload rooted there
    ships all of them under one game's save. Two cards holding the same game is
    a refusal, not a choice — either answer overwrites the other card's save.
    """
    if not save_id:
        return _unit(layout, base, os.path.join(base, "Shared.ps2"), (), needs=("save_id",))

    cards = _ps2_cards(base, listing)
    if not cards:
        return _unit(layout, base, os.path.join(base, "Shared.ps2"), ())

    owners: list[tuple[str, tuple[str, ...]]] = []
    for card in cards:
        matched = tuple(name for name in _children(listing, card) if ps2_name_matches(name, save_id))
        if matched:
            owners.append((card, matched))
    if len(owners) > 1:
        return _unit(
            layout,
            base,
            None,
            (),
            conflicts=tuple(card for card, _ in owners),
            needs=("preferred_card",),
        )
    if owners:
        card, matched = owners[0]
        members = tuple(
            SaveMember(path=os.path.join(card, name), archive_root=name, is_directory=True) for name in matched
        )
        return _unit(layout, card, card, members)
    return _unit(layout, cards[0], cards[0], ())


def _switch_title(layout: SaveLayout, base: str, save_id: str | None, listing: Mapping[str, Sequence[str]]) -> SaveUnit:
    """One Switch title under the emulator's own user and profile directories.

    Both intermediate levels are discovered and never constructed: they name the
    signed-in profile, so a guessed one points at a directory the emulator does
    not read. With no profile on disk there is no path to answer with.
    """
    title = base_application_id(save_id) if save_id else None
    if title is None:
        return _unit(layout, base, None, (), needs=("save_id",))
    user = _first_child(listing, base)
    if user is None:
        return _unit(layout, base, None, (), needs=("profile",))
    profile = _first_child(listing, os.path.join(base, user))
    if profile is None:
        return _unit(layout, base, None, (), needs=("profile",))
    path = os.path.join(base, user, profile, title)
    member = SaveMember(path=path, archive_root=title, is_directory=True)
    return _unit(layout, base, path, (member,))


def _dreamcast_vmu(layout: SaveLayout, base: str, save_id: str | None) -> SaveUnit:
    """Port A1's VMU card, named after the disc's product number.

    Flycast never implements ``RETRO_MEMORY_SAVE_RAM``, so there is no ``.srm``
    for the platform at all; the bytes are one file, and only the name is
    platform-specific.
    """
    if not save_id or not save_id.strip():
        return _unit(layout, base, None, (), needs=("save_id",))
    name = f"{dreamcast_vmu_stem(save_id)}.A1.bin"
    member = SaveMember(path=os.path.join(base, name), archive_root=name, is_directory=False)
    return _unit(layout, base, member.path, (member,))


def _gci_set(
    layout: SaveLayout,
    base: str,
    save_id: str | None,
    listing: Mapping[str, Sequence[str]],
    header_matched: Sequence[str],
) -> SaveUnit:
    """Every ``.gci`` in the card whose header carries the disc's game code.

    One file uploads raw and two or more upload as a zip under their own names,
    so the unit is the matched set and never the first hit. Membership by header
    is the reliable test; a name-only fallback is what a caller without the
    bytes can do.
    """
    if header_matched:
        names = tuple(header_matched)
    elif save_id:
        needle = save_id.strip().upper()
        names = tuple(
            name for name in _children(listing, base) if name.lower().endswith(".gci") and needle in name.upper()
        )
    else:
        names = ()
    members = tuple(SaveMember(path=os.path.join(base, name), archive_root=name, is_directory=False) for name in names)
    return _unit(layout, base, base, members)


# -- helpers -----------------------------------------------------------------


def _unit(
    layout: SaveLayout,
    base: str,
    place_path: str | None,
    members: tuple[SaveMember, ...],
    *,
    identified: bool | None = None,
    conflicts: tuple[str, ...] = (),
    needs: tuple[str, ...] = (),
) -> SaveUnit:
    """Assemble an answer without repeating the layout's own identity fields."""
    return SaveUnit(
        platform=layout.platform,
        family=layout.family,
        usage=layout.usage,
        base=base,
        place_path=place_path,
        members=members,
        identified=layout.identified if identified is None else identified,
        container=layout.container,
        conflicts=conflicts,
        needs=needs,
    )


def _children(listing: Mapping[str, Sequence[str]], path: str) -> tuple[str, ...]:
    """The names directly inside *path*, or nothing when the scan did not reach it."""
    return tuple(listing.get(path, ()))


def _first_child(listing: Mapping[str, Sequence[str]], path: str) -> str | None:
    """The first name inside *path*, in the order the scan reported it."""
    children = _children(listing, path)
    return children[0] if children else None


def _prefix_match(name: str, save_id: str) -> bool:
    return name.strip().lower().startswith(save_id.strip().lower())


def _normalized(value: str) -> str:
    return value.replace("-", "").replace("_", "").strip().upper()


def _without_region_prefix(stem: str) -> str:
    return stem[2:] if _PS2_REGION_PREFIXED.match(stem) else stem


def _ps2_territory_prefix(code: str) -> str:
    third = code[2]
    if third == "E":
        return "BE"
    if third in {"P", "J", "K"}:
        return "BI"
    return "BA"


def _ps2_cards(base: str, listing: Mapping[str, Sequence[str]]) -> tuple[str, ...]:
    """The folder memory cards a scan found, or the base itself when it is one.

    The cards directly under the base win; only when it holds none is one level
    below searched, because a base pointed at the parent of a ``memcards``
    directory must still resolve to the cards every other lookup uses. The
    descent stops at one level, so no deeper tree is ever searched.
    """
    if _is_ps2_card(base, listing):
        return (base,)
    children = tuple(os.path.join(base, name) for name in _children(listing, base))
    direct = tuple(path for path in children if _is_ps2_card(path, listing))
    if direct:
        return direct
    return tuple(
        nested
        for child in children
        for nested in (os.path.join(child, name) for name in _children(listing, child))
        if _is_ps2_card(nested, listing)
    )


def _is_ps2_card(path: str, listing: Mapping[str, Sequence[str]]) -> bool:
    if path.rstrip(os.sep).lower().endswith(".ps2"):
        return True
    return PS2_SUPERBLOCK_FILE in _children(listing, path)


def _n3ds_key(save_id: str | None) -> tuple[str, str, str | None] | None:
    """Category, low id and the extdata id the low id derives, all lowercase.

    The extdata rule for a retail title: take the low 8 hex of the title id,
    shift it right by 8 bits, render 8 lowercase hex digits, so ``00113200``
    becomes ``00001132``. A ``save_id`` shorter than 16 characters has no
    category in it and falls back to the retail one.
    """
    low_id = _low_id(save_id)
    if low_id is None:
        return None
    category = _category_of(save_id) or _3DS_BASE_CATEGORY
    extdata_id = f"{int(low_id, 16) >> _3DS_EXTDATA_SHIFT:08x}"
    return category, low_id, extdata_id


def _low_id(save_id: str | None) -> str | None:
    """The last 8 hex of an id, which is the folder name on the newer consoles."""
    if not save_id:
        return None
    text = save_id.replace("/", "").strip().lower()
    candidate = text[-8:]
    return candidate if _HEX8.fullmatch(candidate) else None


def _category_of(save_id: str | None) -> str | None:
    """The high 8 hex of a full 16-hex id, or ``None`` for a bare low id."""
    if not save_id:
        return None
    text = save_id.replace("/", "").strip().lower()
    if len(text) < 16:
        return None
    candidate = text[:8]
    return candidate if _HEX8.fullmatch(candidate) else None


def _category_base(base: str, category: str | None, pattern: str | None) -> str:
    """The category directory *base* names, or its sibling for another category.

    A demo id under ``00050002`` resolves beside a base ending ``00050000``, and
    a low id alone carries no category and stays where the base points.
    """
    if category is None or pattern is None:
        return base
    trimmed = base.rstrip(os.sep)
    last = os.path.basename(trimmed)
    if not re.fullmatch(pattern, last, re.IGNORECASE) or last.lower() == category:
        return base
    return os.path.join(os.path.dirname(trimmed), category)
