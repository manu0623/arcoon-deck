"""What game a file is, when the file's own bytes say so.

Every non-libretro save shape is keyed by an identity the content path never carries: a
PS2 save folder is named after the disc's serial, a GameCube set is chosen by the disc's
game code, a 3DS title writes under its 16-hex title id, a Dreamcast VMU file is named
after the IP.BIN product number. Deriving those from bytes is what turns
``domain.save_bank`` from a layout description into something that can actually find a
save, and it is why this module exists separately from the banks and the layouts: one
place reads the identity, one place spends it.

Everything here is a pure parser over bytes the caller already read. Nothing opens a
file, nothing decodes a file system — an adapter decides what slice of which file to hand
over, and this module only says what that slice means.

**Refusing is the normal outcome.** A header that does not carry the expected magic
returns ``None`` rather than a best guess: a wrong identity is worse than no identity,
because it silently points a save at another game's folder. Where a format needs two
reads (a 3DS cart keeps its title id inside a partition, not at a fixed offset from the
front) the two steps are separate functions so the caller can read exactly what is
needed.

**Which formats are here, and why.** PS1/PS2 (serial on the boot line), Dreamcast
(IP.BIN product number), GameCube (disc game code), 3DS (NCCH program id) and PSP
(``DISC_ID`` in ``PSP_GAME/PARAM.SFO``). The PSP id has no fixed offset — it is a key in
a table that lives in a file that lives in a directory the image itself describes — so
this module also parses the two ISO 9660 structures needed to reach it (the volume
descriptor's root record and one directory record). Walking them here rather than in the
adapter keeps the format knowledge in one place; the adapter only chooses offsets to
read.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import StrEnum

# A PS1/PS2 boot line names the serial the way the filesystem does — ``SLUS_203.12``,
# ``SCES_123.45``, ``SLPS-01234``. The separator and the punctuation differ between
# publishers and between the two consoles, so the pattern accepts both and the value is
# normalised to the hyphenated form every other layer (and RomM) spells.
_BOOT_SERIAL = re.compile(r"\b([A-Z]{4})[_-](\d{3})[.]?(\d{2})\b")
# The line that carries it: PS2 uses ``BOOT2``, PS1 ``BOOT``; both point at ``cdrom0:``.
# Deliberately not anchored to a line start: the image's head arrives as one decoded
# blob, whose padding is NULs rather than newlines, so an anchored pattern would miss the
# boot line in every image that pads a sector before it.
_BOOT_LINE = re.compile(r"BOOT2?\s*=\s*cdrom0?:\\(?P<rest>[^\n\r]*)")

# Dreamcast IP.BIN: the boot sector's product number, ten ASCII bytes at 0x40, padded
# with spaces (``T-97063D  ``) and occasionally NULs. Flycast builds a VMU file name from
# exactly this token, so it is kept verbatim bar the padding.
_DREAMCAST_MAGIC = b"SEGA SEGAKATANA "
_DREAMCAST_HEADER_SIZE = 0x100
_DREAMCAST_PRODUCT_OFFSET = 0x40
_DREAMCAST_PRODUCT_LENGTH = 10

# GameCube ``boot.bin``: console ``G``, two-character game code, region, two-character
# maker code. The memory-card name uses the first four bytes (``GMSE``), not the six.
_GAMECUBE_ID_LENGTH = 4
_GAMECUBE_REGIONS = frozenset("JEPD")

# Dolphin's own region directory spelling, as its card folders are actually named.
# Measured on the reference Deck: ``GC/USA/Card A`` and ``GC/JAP`` exist. Everything
# outside Japan and the Americas is PAL to Dolphin (D/F/I/S/R/H discs included), so
# it lands under ``EUR``; that is the emulator's rule, not a guess about the disc.
_GAMECUBE_CARD_REGIONS = {"J": "JAP", "E": "USA"}
_GAMECUBE_ID_BYTES = 0x20  # covers the header excerpt a caller needs to pass

# 3DS: a cart image (``.3ds``/``.cci``) starts with an NCSD header at 0x100 and keeps the
# actual partition — an NCCH — at a media-unit offset the header states at 0x120. The
# program id sits at 0x118 of the NCCH, little-endian, and *is* the title id.
_N3DS_HEADER_OFFSET = 0x100
_N3DS_PARTITION_TABLE = 0x120
_N3DS_MEDIA_UNIT = 0x200
_N3DS_NCCH_MAGIC = b"NCCH"
_N3DS_PROGRAM_ID_OFFSET = 0x118
_N3DS_ID_LENGTH = 16


class IdentityKind(StrEnum):
    """Which of the several id vocabularies this identity belongs to.

    The kind is not decoration: a 3DS title id and a PS2 serial are both "the save id"
    to the bank, and every consumer that formats one (a folder name, a file stem, a
    split category) has to know which it holds.
    """

    DISC_SERIAL = "disc_serial"
    # A PSP ``DISC_ID`` is a serial too, but a differently shaped one (``ULUS10064``,
    # no hyphen), and the bank's folder prefixes are matched verbatim rather than
    # normalised, so the two vocabularies stay apart.
    DISC_ID = "disc_id"
    TITLE_ID = "title_id"
    # A Switch title id is the same 16 hex digits as a 3DS one and is NOT filed the same
    # way: a 3DS save lives under ``title/<high 8>/<low 8>``, while Eden keeps one folder
    # named with all 16. Measured on the reference Deck: filling a Switch answer through
    # the 3DS formatting produced ``…/01006BB0/0C6F0000``, a directory no emulator writes,
    # and the sync then found nothing to carry. Two kinds, so no caller has to sniff.
    SWITCH_TITLE_ID = "switch_title_id"
    GAME_CODE = "game_code"
    # A Wii disc's code is the same four characters a GameCube disc's is, and it is NOT
    # filed the same way: Dolphin names a Wii save folder with the code's ASCII bytes in
    # hex, so ``save_id_text`` has to spell it as ``<4 chars>.hex()`` rather than verbatim.
    WII_GAME_CODE = "wii_game_code"
    PRODUCT_NUMBER = "product_number"


@dataclass(frozen=True, slots=True)
class ContentIdentity:
    """One id read off a content file, with the rule that produced it.

    ``source`` names the rule in words ("PS2 BOOT2 line", "3DS NCCH program id") so a
    log or a UI can say *why* a save is being looked for under this name — the failure
    this avoids is an unexplained empty folder, which looks exactly like a lost save.
    """

    save_id: str
    kind: IdentityKind
    source: str
    # The region the format states, where it states one and a caller needs it as a
    # NAME rather than a code: Dolphin files a card under ``GC/<region>/Card A``.
    region: str | None = None


def disc_serial(text: str) -> ContentIdentity | None:
    """The serial from a PS1/PS2 ``SYSTEM.CNF`` boot line, or ``None``.

    *text* is the decoded head of the disc image (``SYSTEM.CNF`` is a small file near
    the start of the ISO, so the first megabyte is enough). The serial is taken from the
    ``BOOT``/``BOOT2`` line specifically rather than by scanning for any serial-shaped
    token: an image's padding and its licence text both contain serial-like strings, and
    the boot line is the one the console itself follows.
    """
    for match in _BOOT_LINE.finditer(text):
        serial = _BOOT_SERIAL.search(match.group("rest").upper())
        if serial is not None:
            code, digits, revision = serial.groups()
            return ContentIdentity(
                save_id=f"{code}-{digits}{revision}",
                kind=IdentityKind.DISC_SERIAL,
                source="PS2 BOOT2 line" if "BOOT2" in match.group(0).upper() else "PS1 BOOT line",
            )
    return None


def dreamcast_product_number(head: bytes) -> ContentIdentity | None:
    """The IP.BIN product number (``T-97063D``) from a Dreamcast boot sector, or ``None``.

    The IP.BIN magic is checked as well as the token's shape: a GDI's first bytes are the
    boot sector only for data-track-first dumps, so an image that opens with something
    else must not have ten bytes of arbitrary header read as a product number.
    """
    if len(head) < _DREAMCAST_HEADER_SIZE or not head.startswith(_DREAMCAST_MAGIC):
        return None
    raw = head[_DREAMCAST_PRODUCT_OFFSET : _DREAMCAST_PRODUCT_OFFSET + _DREAMCAST_PRODUCT_LENGTH]
    product = raw.decode("ascii", errors="replace").replace("\x00", " ").strip()
    if not product or not any(char.isalnum() for char in product):
        return None
    return ContentIdentity(save_id=product, kind=IdentityKind.PRODUCT_NUMBER, source="Dreamcast IP.BIN")


def gamecube_game_code(head: bytes) -> ContentIdentity | None:
    """The four-character GameCube game code (``GMSE``) from ``boot.bin``, or ``None``.

    Dolphin names a memory-card entry from the disc's own game code, so this is the id a
    GCI has to match. The region byte is checked because it is the only byte that tells a
    real header from four printable bytes at the front of an unrelated file.
    """
    if len(head) < _GAMECUBE_ID_BYTES or head[0:1] != b"G":
        return None
    if chr(head[3]) not in _GAMECUBE_REGIONS:
        return None
    code = head[:_GAMECUBE_ID_LENGTH].decode("ascii", errors="replace")
    if not all(char.isalnum() for char in code):
        return None
    return ContentIdentity(
        save_id=code,
        kind=IdentityKind.GAME_CODE,
        source="GameCube boot.bin",
        region=_GAMECUBE_CARD_REGIONS.get(chr(head[3]), "EUR"),
    )


# Dolphin's compressed GameCube/Wii container. Its header is not the disc: the disc's
# own 0x58-byte-offset copy of the id is what a reader can use, measured on a real
# `.rvz` of Twilight Princess (USA), whose header holds "GZ2E01" at 0x58 while the
# file itself begins `RVZ\x01`. Decompressing the first data group would work too and
# was tried first: the group is not at a fixed offset the header states unambiguously,
# so this copy is the honest route — and it is validated rather than trusted.
_RVZ_MAGIC = b"RVZ\x01"
_RVZ_DISC_ID_OFFSET = 0x58
_RVZ_DISC_ID_BYTES = 6


def rvz_gamecube_game_code(head: bytes) -> ContentIdentity | None:
    """The GameCube game code from a Dolphin ``.rvz`` container's header, or ``None``.

    A compressed container is not the disc, so :func:`gamecube_game_code` answers
    nothing for it — the first byte is ``R``, not ``G`` — and a GameCube ROM stored this
    way would keep its save refused for want of an id that is in fact sitting in the
    header. It is checked, not assumed: the six bytes at
    :data:`_RVZ_DISC_ID_OFFSET` must pass the same test a bare ``boot.bin`` passes, so a
    container whose layout differs answers nothing rather than a plausible-looking
    string out of somebody's hash table.
    """
    if not head.startswith(_RVZ_MAGIC) or len(head) < _RVZ_DISC_ID_OFFSET + _RVZ_DISC_ID_BYTES:
        return None
    identity = gamecube_game_code(head[_RVZ_DISC_ID_OFFSET : _RVZ_DISC_ID_OFFSET + 0x20].ljust(0x20, b"\x00"))
    if identity is None:
        return None
    # The reading is the disc's id, but it was not taken from a bare ``boot.bin``.
    return replace(identity, source="GameCube .rvz header")


def _wii_game_code(code: bytes, source: str) -> ContentIdentity | None:
    """The four-character Wii game code from six disc bytes, or ``None``.

    A Wii disc header opens with the same six-character code a GameCube one does
    (``SMNE01``), but the first byte is the console (``S`` for a Wii disc) rather than the
    ``G`` a GameCube boot file starts with, so neither reader can serve the other. The region
    character is the only byte that tells a real header from six printable bytes at the front
    of something else, exactly as on GameCube.
    """
    if len(code) < _RVZ_DISC_ID_BYTES:
        return None
    text = code[:6].decode("ascii", errors="replace")
    if not all(char.isalnum() for char in text):
        return None
    if text[3] not in _GAMECUBE_REGIONS:
        return None
    return ContentIdentity(
        save_id=text[:4],
        kind=IdentityKind.WII_GAME_CODE,
        source=source,
        region=_GAMECUBE_CARD_REGIONS.get(text[3], "EUR"),
    )


def wii_game_code(head: bytes) -> ContentIdentity | None:
    """The Wii game code from a bare disc image's header, or ``None``.

    Measured on the reference Deck's own ROM set: a Wii ``.rvz`` carries ``SB4E01`` at
    :data:`_RVZ_DISC_ID_OFFSET`, and Dolphin then keeps the save in
    ``Wii/title/00010000/53423445/data`` — the folder named by those four characters in hex.
    """
    return _wii_game_code(head[:6], "Wii disc header")


def rvz_wii_game_code(head: bytes) -> ContentIdentity | None:
    """The Wii game code from a Dolphin ``.rvz`` container's header, or ``None``.

    The same container offset the GameCube reader uses, checked rather than trusted: the
    magic has to be there and the six bytes have to pass the Wii test, so a container with a
    different layout answers nothing rather than a plausible string from a hash table.
    """
    if not head.startswith(_RVZ_MAGIC) or len(head) < _RVZ_DISC_ID_OFFSET + _RVZ_DISC_ID_BYTES:
        return None
    return _wii_game_code(head[_RVZ_DISC_ID_OFFSET : _RVZ_DISC_ID_OFFSET + _RVZ_DISC_ID_BYTES], "Wii .rvz header")


def wii_title_dirname(save_id: str) -> str:
    """The Dolphin title-directory name a four-character Wii game code implies.

    Measured: ``SB4E`` becomes ``53423445`` under ``Wii/title/00010000`` — the code's ASCII
    bytes in lowercase hex, which is how the emulator names a title it has a save for.
    """
    return save_id.encode("ascii").hex()


def n3ds_partition_offset(head: bytes) -> int | None:
    """Where the first NCCH partition starts in a ``.3ds``/``.cci`` image, or ``None``.

    The NCSD header states partition offsets in media units (0x200 bytes) at 0x120; the
    first entry is the game partition. A bare NCCH (``.cxi``, or a decrypted ``.app``)
    has no NCSD header at all, which is why :func:`n3ds_title_id` also accepts an image
    that begins with the NCCH magic directly.
    """
    if len(head) < _N3DS_HEADER_OFFSET + 8:
        return None
    if head[_N3DS_HEADER_OFFSET : _N3DS_HEADER_OFFSET + 4] != b"NCSD":
        return None
    entry = head[_N3DS_PARTITION_TABLE : _N3DS_PARTITION_TABLE + 4]
    if len(entry) < 4:
        return None
    # Offsets are little-endian numbers of 0x200-byte units. A zero here names no
    # partition (a demo cart with the game outside partition 0 is not something this
    # reader can follow), so it refuses rather than reading the header as content.
    units = int.from_bytes(entry, "little")
    return units * _N3DS_MEDIA_UNIT if units else None


def n3ds_title_id(ncch_head: bytes) -> ContentIdentity | None:
    """The 16-hex title id from the start of a 3DS NCCH, or ``None``.

    *ncch_head* is read from the partition's start — the same offset
    :func:`n3ds_partition_offset` returns, or 0 for a bare ``.cxi``/``.app``. That start
    is the NCCH's 0x100-byte signature block, so the ``NCCH`` magic sits at 0x100 and the
    program id just past it at 0x118, exactly as in the cart header's own copy of the
    same layout.

    The program id is little-endian and is the id the emulator keys ``title/<high>/<low>``
    on, so it is rendered as the single 16-character lowercase spelling rather than split
    here — ``domain.save_bank`` owns how an id becomes a path.
    """
    if len(ncch_head) < _N3DS_PROGRAM_ID_OFFSET + 8:
        return None
    if ncch_head[_N3DS_HEADER_OFFSET : _N3DS_HEADER_OFFSET + 4] != _N3DS_NCCH_MAGIC:
        return None
    program_id = int.from_bytes(ncch_head[_N3DS_PROGRAM_ID_OFFSET : _N3DS_PROGRAM_ID_OFFSET + 8], "little")
    text = f"{program_id:0{_N3DS_ID_LENGTH}x}"
    # A real 3DS application lives in the 00040000 category. Anything else is either a
    # system title or a mis-read header, and neither names a save this bank can place.
    if not _is_3ds_app(text):
        return None
    return ContentIdentity(save_id=text, kind=IdentityKind.TITLE_ID, source="3DS NCCH program id")


# ISO 9660, for the PSP disc id. The volume descriptor sits at sector 16 and holds the
# root directory's record at offset 156; every directory record then states its own
# extent and length, little-endian, and names itself after a 32-byte prefix. A record
# never straddles a sector: a zero length byte means "the rest of this sector is
# padding", which is why the walk jumps a sector rather than stopping.
_ISO_SECTOR = 2048
_ISO_PVD_SECTOR = 16
_ISO_DESCRIPTOR_TYPE_PRIMARY = 1
_ISO_DESCRIPTOR_MAGIC = b"CD001"
_ISO_ROOT_RECORD_OFFSET = 156
_ISO_RECORD_MIN = 34
_ISO_NAME_OFFSET = 32

# PARAM.SFO: a ``\x00PSF`` header states where the key table, the value table and the
# entries start; each entry names a key and points at its value. DISC_ID is the entry
# this reads, and the magic is checked because a plausible-looking run of bytes at a
# plausible offset is not an id.
_SFO_MAGIC = b"\x00PSF"
_SFO_HEADER_SIZE = 20
_SFO_ENTRY_SIZE = 16
_SFO_MAX_ENTRIES = 64
#: A disc id: four letters and five digits, no separator (``ULUS10064``, ``BCUS98247``).
#: PSP and PS3 both spell their id this way and the bank's prefix rule matches it
#: verbatim, so one shape covers both vocabularies.
_DISC_ID_SHAPE = re.compile(r"[A-Z]{4}[0-9]{5}")


def iso9660_root_directory(pvd: bytes) -> tuple[int, int] | None:
    """The ``(extent, size)`` of an image's root directory, from its volume descriptor.

    *pvd* is the 2048-byte primary volume descriptor (sector 16). A disc that does not
    start one there answers ``None``: a UDF-only or compressed image is not something
    this reader can walk, and reading the record from a sector that is not a descriptor
    would hand back an extent that points anywhere.
    """
    if len(pvd) < _ISO_PVD_SECTOR or pvd[0] != _ISO_DESCRIPTOR_TYPE_PRIMARY:
        return None
    if pvd[1:6] != _ISO_DESCRIPTOR_MAGIC:
        return None
    record = pvd[_ISO_ROOT_RECORD_OFFSET : _ISO_ROOT_RECORD_OFFSET + _ISO_RECORD_MIN]
    if len(record) < _ISO_RECORD_MIN or record[0] < _ISO_RECORD_MIN:
        return None
    return int.from_bytes(record[2:6], "little"), int.from_bytes(record[10:14], "little")


def iso9660_entry(directory: bytes, name: str) -> tuple[int, int] | None:
    """The ``(extent, size)`` of *name* inside one directory's bytes, or ``None``.

    The name is compared case-insensitively and without the ``;1`` version suffix an
    ISO 9660 writer appends, because both spellings name the same entry and the images
    in the wild use each.
    """
    wanted = name.strip().upper()
    offset = 0
    while offset + _ISO_RECORD_MIN <= len(directory):
        length = directory[offset]
        if length == 0:
            offset = (offset // _ISO_SECTOR + 1) * _ISO_SECTOR
            continue
        if length < _ISO_RECORD_MIN or offset + length > len(directory):
            return None
        record = directory[offset : offset + length]
        name_length = record[_ISO_NAME_OFFSET]
        raw = record[_ISO_NAME_OFFSET + 1 : _ISO_NAME_OFFSET + 1 + name_length]
        entry = raw.decode("ascii", errors="replace").split(";")[0].strip().upper()
        if entry == wanted:
            return int.from_bytes(record[2:6], "little"), int.from_bytes(record[10:14], "little")
        offset += length
    return None


def psp_disc_id(sfo: bytes) -> ContentIdentity | None:
    """The ``DISC_ID`` (``ULUS10064``, ``ULES00502``) from a PSP ``PARAM.SFO``, or ``None``.

    This is the id PPSSPP names a save folder with (``ULUS10064DATA00`` beside
    ``ULUS10064SETTINGS``), so it is the id the bank's prefix rule matches on. The shape
    is validated rather than trusted: four letters and five digits is what a disc id
    looks like, and an entry whose bytes are not that is a mis-read table, not an id.
    """
    entries = _sfo_entries(sfo)
    if entries is None:
        return None
    for key, value in entries:
        if key != "DISC_ID":
            continue
        text = value.decode("ascii", errors="replace").replace("\x00", "").strip().upper()
        if _DISC_ID_SHAPE.fullmatch(text):
            return ContentIdentity(save_id=text, kind=IdentityKind.DISC_ID, source="PSP PARAM.SFO DISC_ID")
        return None
    return None


def ps3_title_id(sfo: bytes) -> ContentIdentity | None:
    """The ``TITLE_ID`` (``BCUS98247``) from a PS3 ``PARAM.SFO``, or ``None``.

    A PS3 save folder is named after this id plus whatever the game appends
    (``BCUS98247_SAVE_SLOT_00000``), so the bank's prefix rule matches on it exactly as
    it does a PSP ``DISC_ID``, and the same :data:`IdentityKind.DISC_ID` vocabulary is
    the honest one to carry it under.

    Measured on the reference Deck: Sly Cooper: Thieves in Time wrote its save under the
    id its own ``PARAM.SFO`` states, and 3D Dot Game Heroes' disc states ``BLUS30490``.
    The format byte is not consulted: the real disc states ``TITLE_ID`` as ``0x0204``,
    while the NUL-terminated ``0x0404`` is what a hand-written file tends to use, and
    both name the same thing.
    """
    entries = _sfo_entries(sfo)
    if entries is None:
        return None
    for key, value in entries:
        if key != "TITLE_ID":
            continue
        text = value.decode("ascii", errors="replace").replace("\x00", "").strip().upper()
        if _DISC_ID_SHAPE.fullmatch(text):
            return ContentIdentity(save_id=text, kind=IdentityKind.DISC_ID, source="PS3 PARAM.SFO TITLE_ID")
        return None
    return None


def _sfo_entries(sfo: bytes) -> list[tuple[str, bytes]] | None:
    """Every ``(key, value)`` pair a PARAM.SFO states, or ``None`` when it is not one."""
    if len(sfo) < _SFO_HEADER_SIZE or sfo[:4] != _SFO_MAGIC:
        return None
    key_table = int.from_bytes(sfo[8:12], "little")
    data_table = int.from_bytes(sfo[12:16], "little")
    count = int.from_bytes(sfo[16:20], "little")
    entries: list[tuple[str, bytes]] = []
    for index in range(min(count, _SFO_MAX_ENTRIES)):
        base = _SFO_HEADER_SIZE + index * _SFO_ENTRY_SIZE
        if base + _SFO_ENTRY_SIZE > len(sfo):
            return None
        key_offset = int.from_bytes(sfo[base : base + 2], "little")
        length = int.from_bytes(sfo[base + 4 : base + 8], "little")
        data_offset = int.from_bytes(sfo[base + 12 : base + 16], "little")
        start = key_table + key_offset
        end = sfo.find(b"\x00", start)
        if start >= len(sfo) or end < 0:
            return None
        value_start = data_table + data_offset
        entries.append(
            (sfo[start:end].decode("ascii", errors="replace"), sfo[value_start : value_start + length])
        )
    return entries


def save_id_text(identity: ContentIdentity) -> str:
    """The identity as the resolver's ``<save_id>`` hole expects to be filled.

    Most shapes take the id verbatim — a PS2 folder is named ``SLUS-20312`` and a VMU
    file ``T-97063D``. The newer consoles split it: a 3DS save lives under
    ``title/<high 8>/<low 8>``, so the hole wants the two halves joined by a slash, not
    the 16-character spelling the emulator's own database uses. Formatting it here keeps
    every caller from inventing its own split.
    """
    if identity.kind is IdentityKind.TITLE_ID:
        return f"{identity.save_id[:8]}/{identity.save_id[8:]}"
    if identity.kind is IdentityKind.WII_GAME_CODE:
        return wii_title_dirname(identity.save_id)
    # A Switch id rides whole: one 16-character directory name, no split.
    return identity.save_id


def _is_3ds_app(title_id: str) -> bool:
    """Whether *title_id* is in the 3DS application category (``00040000``).

    The whole high word is compared, not its ``0004`` prefix: ``00040130`` is the system
    title category, and treating it as an application would point a save at a title that
    never writes one.
    """
    return title_id.startswith("00040000") and len(title_id) == _N3DS_ID_LENGTH
