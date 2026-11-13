"""Reading the saves out of a PCSX2 *file* memory card (an 8 MB ``.ps2`` image).

A file card is a PS2 memory card image: 16384 pages of 512 data bytes plus a 16-byte
spare area each, grouped into clusters of two pages, with a superblock in page 0, an
indirect FAT table, a FAT, and an allocatable area holding directory entries and file
data. Measured on the reference Deck's own card (8,650,752 bytes):

- page raw stride is ``page_len + (page_len // 128) * 4`` = 528;
- ``alloc_offset`` 41 means cluster 0 is page 82, so the root directory of that card
  sits at raw offset ``82 * 528``;
- the root directory's first entries are ``.``, ``..`` and ``BASCUS-97198YAOTWTD!``
  (mode ``0x8427``, length 8 entries, cluster 2 — a directory), and inside it the save
  files: a same-named file (mode ``0x8497``), ``icon.sys`` and ``.ico`` files.

This module is the *read* half only, and it is pure: it takes the image's bytes and
answers the save folders with the byte spans that hold each file, so an adapter can copy
them without this layer touching a filesystem. The reason it exists is that a file card
holds every game's saves in one image, so syncing "this game's save" is impossible while
the card stays a file; PCSX2 can convert a card, but only from its own UI, so the plugin
does the same job itself and keeps the image untouched as a backup.

Only two things are trusted from the image: the superblock's geometry and the
directory/FAT structures the PS2 format defines. Nothing is guessed — a card whose
geometry does not parse is refused rather than partially extracted.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

#: Directory entries are one card page each: the last measured card's root entry for
#: ``BASCUS-97198YAOTWTD!`` began at a page boundary and held its name at ``0x40``.
ENTRY_SIZE = 512
NAME_OFFSET = 0x40
NAME_LENGTH = 32
#: ``mode`` bit set on every directory entry the measured card holds (``.``, ``..`` and
#: the save folder are ``0x8427``/``0xa426``; files are ``0x8497`` and do not set it).
MODE_DIRECTORY = 0x0020
#: ``mode`` bit that says the entry is in use; an unused entry is ``0xffff``.
MODE_EXISTS = 0x8000
#: The FAT's end-of-chain marker; the chain's next-cluster field is the low 31 bits.
FAT_END = 0x7FFFFFFF


class Ps2CardError(ValueError):
    """The image is not a file memory card this module can read."""


@dataclass(frozen=True)
class Ps2CardFile:
    """One file inside a save folder, as the raw spans that hold its bytes."""

    name: str
    size: int
    spans: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class Ps2CardFolder:
    """One save folder on the card: its name as the card spells it, and its files."""

    name: str
    files: tuple[Ps2CardFile, ...]
    folders: tuple[Ps2CardFolder, ...] = ()


@dataclass(frozen=True)
class _Geometry:
    page_len: int
    pages_per_cluster: int
    clusters_per_card: int
    alloc_offset: int
    rootdir_cluster: int
    ifc_clusters: tuple[int, ...]

    @property
    def spare(self) -> int:
        """The bytes every page spends on ECC, skipped when reading data."""
        return (self.page_len // 128) * 4

    @property
    def page_stride(self) -> int:
        return self.page_len + self.spare

    @property
    def cluster_size(self) -> int:
        return self.page_len * self.pages_per_cluster

    def page_offset(self, page: int) -> int:
        return page * self.page_stride

    def entries_per_cluster(self) -> int:
        return self.cluster_size // ENTRY_SIZE


def read_file_card(data: bytes) -> tuple[Ps2CardFolder, ...]:
    """Every save folder on the card, in the order the root directory lists them.

    Raises :class:`Ps2CardError` when the image does not parse — a refused card is a
    save that stays where it is, which is the only honest answer for an unknown format.
    """
    geometry = _geometry(data)
    reader = _Reader(data, geometry)
    folders: list[Ps2CardFolder] = []
    for entry in reader.root_entries():
        if not entry.is_directory or entry.name in (".", ".."):
            continue
        folders.append(reader.folder(entry))
    return tuple(folders)


def _geometry(data: bytes) -> _Geometry:
    if len(data) < 0x200:
        raise Ps2CardError("the image is shorter than one card page")
    if not data[:28].startswith(b"Sony PS2 Memory Card Format"):
        raise Ps2CardError("the image has no PS2 memory card superblock")
    page_len, pages_per_cluster = struct.unpack_from("<HH", data, 0x28)
    clusters_per_card = struct.unpack_from("<I", data, 0x30)[0]
    alloc_offset, _alloc_end, rootdir = struct.unpack_from("<III", data, 0x34)
    ifc = struct.unpack_from("<32I", data, 0x50)
    if not page_len or not pages_per_cluster or not clusters_per_card:
        raise Ps2CardError("the superblock states a card of zero size")
    if not any(value not in (0, 0xFFFFFFFF) for value in ifc):
        raise Ps2CardError("the superblock names no indirect FAT table")
    return _Geometry(
        page_len=page_len,
        pages_per_cluster=pages_per_cluster,
        clusters_per_card=clusters_per_card,
        alloc_offset=alloc_offset,
        rootdir_cluster=rootdir,
        ifc_clusters=tuple(value for value in ifc if value not in (0, 0xFFFFFFFF)),
    )


@dataclass(frozen=True)
class _Entry:
    name: str
    mode: int
    length: int
    cluster: int

    @property
    def is_directory(self) -> bool:
        return bool(self.mode & MODE_DIRECTORY)

    @property
    def exists(self) -> bool:
        return bool(self.mode & MODE_EXISTS)


class _Reader:
    """Follows the card's FAT chains on top of the image bytes."""

    def __init__(self, data: bytes, geometry: _Geometry) -> None:
        self._data = data
        self._geometry = geometry
        self._fat: dict[int, int] = {}

    # -- clusters ---------------------------------------------------------
    def cluster_bytes(self, relative: int) -> bytes:
        """One allocatable cluster's data bytes, addressed as the card addresses them.

        Directory entries and FAT chains number clusters *relative to ``alloc_offset``*
        (measured: the save folder states cluster 2 and sits at page 86, which is
        ``(41 + 2) * 2``), so every entry cluster goes through this offset. The IFT and
        FAT clusters live before that area and are addressed absolutely.
        """
        return self._absolute_bytes(self._geometry.alloc_offset + relative)

    def _absolute_bytes(self, cluster: int) -> bytes:
        """One cluster's data bytes, with each page's spare area dropped."""
        start = self._geometry.page_offset(cluster * self._geometry.pages_per_cluster)
        page_len = self._geometry.page_len
        stride = self._geometry.page_stride
        chunks = [
            self._data[start + page * stride:start + page * stride + page_len]
            for page in range(self._geometry.pages_per_cluster)
        ]
        return b"".join(chunks)

    def chain(self, first: int, *, count: int | None = None) -> tuple[int, ...]:
        """The clusters in one FAT chain, following next-cluster values to the end."""
        clusters: list[int] = []
        cluster = first
        seen: set[int] = set()
        while cluster != FAT_END and cluster not in seen:
            seen.add(cluster)
            clusters.append(cluster)
            if count is not None and len(clusters) >= count:
                break
            cluster = self.fat(cluster)
        return tuple(clusters)

    def fat(self, cluster: int) -> int:
        if not self._fat:
            self._fat = self._read_fat()
        return self._fat.get(cluster, FAT_END)

    def _read_fat(self) -> dict[int, int]:
        geometry = self._geometry
        table: list[int] = []
        for ifc_cluster in geometry.ifc_clusters:
            raw = self._absolute_bytes(ifc_cluster)
            for index in range(0, len(raw), 4):
                (fat_cluster,) = struct.unpack_from("<I", raw, index)
                if fat_cluster in (0, 0xFFFFFFFF):
                    continue
                entries = self._cluster_bytes_absolute_or_relative(fat_cluster)
                table.extend(
                    struct.unpack_from("<I", entries, offset)[0] for offset in range(0, len(entries), 4)
                )
        return {
            index: value & FAT_END
            for index, value in enumerate(table)
            if value not in (0, 0xFFFFFFFF)
        }

    # -- directories ------------------------------------------------------
    def root_entries(self) -> tuple[_Entry, ...]:
        """The root directory's entries, whose count its own ``.`` entry states.

        The measured card's root ``.`` states 3 (``.``, ``..`` and the save folder), so
        the count is read from the card rather than assumed.
        """
        cluster = self._geometry.rootdir_cluster
        first = self._parse_entry(self.cluster_bytes(cluster)[:ENTRY_SIZE])
        return self.directory(cluster, first.length if first is not None else 0)

    def _cluster_bytes_absolute_or_relative(self, cluster: int) -> bytes:
        """A FAT cluster's bytes, whichever of the two numberings the card used.

        The format says an indirect-FAT entry names a *cluster*; a card that numbered it
        absolutely would put it before the allocatable area, so a value below
        ``alloc_offset`` is read as-is and anything else as an allocatable cluster.
        """
        if cluster < self._geometry.alloc_offset:
            return self._absolute_bytes(cluster)
        return self.cluster_bytes(cluster - self._geometry.alloc_offset)

    def directory(self, cluster: int, count: int) -> tuple[_Entry, ...]:
        """Every used entry of a directory of *count* entries starting at *cluster*.

        ``count`` comes from the entry that names this directory (the measured card's
        save folder states 8), not from the directory's own ``.`` entry, which states 0
        on that same card — the reason this is a parameter instead of a reading.
        """
        if count <= 0:
            return ()
        needed = -(-count // self._geometry.entries_per_cluster())
        raw = b"".join(self.cluster_bytes(c) for c in self.chain(cluster, count=needed))
        entries: list[_Entry] = []
        for offset in range(0, min(len(raw), count * ENTRY_SIZE), ENTRY_SIZE):
            entry = self._parse_entry(raw[offset:offset + ENTRY_SIZE])
            if entry is not None:
                entries.append(entry)
        return tuple(entries)

    @staticmethod
    def _parse_entry(raw: bytes) -> _Entry | None:
        if len(raw) < NAME_OFFSET + NAME_LENGTH:
            return None
        (mode,) = struct.unpack_from("<H", raw, 0)
        (length,) = struct.unpack_from("<I", raw, 4)
        (cluster,) = struct.unpack_from("<I", raw, 0x10)
        name = raw[NAME_OFFSET:NAME_OFFSET + NAME_LENGTH].split(b"\x00")[0].decode("latin-1").strip()
        # An unused slot is 0xff-filled, which decodes to a name nobody could write and
        # sets the same bits a real entry does — so it is refused by name, not by mode.
        if not name or name == "\ufffd" or any(not ch.isprintable() for ch in name):
            return None
        return _Entry(name=name, mode=mode, length=length, cluster=cluster)

    # -- saves ------------------------------------------------------------
    def folder(self, entry: _Entry) -> Ps2CardFolder:
        children = self.directory(entry.cluster, entry.length)
        return Ps2CardFolder(
            name=entry.name,
            files=tuple(
                self._file(child)
                for child in children
                if not child.is_directory and child.name not in (".", "..") and child.exists
            ),
            folders=tuple(
                self.folder(child)
                for child in children
                if child.is_directory and child.name not in (".", "..") and child.exists
            ),
        )

    def _file(self, entry: _Entry) -> Ps2CardFile:
        geometry = self._geometry
        spans: list[tuple[int, int]] = []
        remaining = entry.length
        for cluster in self.chain(entry.cluster):
            if remaining <= 0:
                break
            # The chain numbers clusters relative to ``alloc_offset``, exactly as the
            # directory entries do; the measured card's first save file sits at cluster
            # 3 = page 88, and reading it as page 6 lands in the FAT instead.
            start = geometry.page_offset((geometry.alloc_offset + cluster) * geometry.pages_per_cluster)
            for page in range(geometry.pages_per_cluster):
                if remaining <= 0:
                    break
                take = min(geometry.page_len, remaining)
                spans.append((start + page * geometry.page_stride, take))
                remaining -= take
        return Ps2CardFile(name=entry.name, size=entry.length, spans=tuple(spans))
