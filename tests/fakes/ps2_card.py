"""A synthetic PCSX2 *file* memory card, laid out the way the measured card is.

Every constant here was read off the reference Deck's own card: pages are 512 data bytes
plus a 16-byte spare area (raw stride 528), clusters are two pages, ``alloc_offset`` is
41 (so cluster 0 is page 82), the indirect FAT sits in cluster 8 and the FAT in cluster
9, and a directory entry keeps its name at ``0x40``.

The image is only as large as the card states: 16384 pages.
"""

from __future__ import annotations

import struct

PAGE_LEN = 512
SPARE = 16
STRIDE = PAGE_LEN + SPARE
PAGES_PER_CLUSTER = 2
CLUSTER = PAGE_LEN * PAGES_PER_CLUSTER
ENTRY = 512
ENTRIES_PER_CLUSTER = CLUSTER // ENTRY
ALLOC_OFFSET = 41
CLUSTERS_PER_CARD = 8192
IFT_CLUSTER = 8
FAT_CLUSTER = 9
CARD_PAGES = 16384

MODE_DIRECTORY = 0x8427
MODE_PARENT = 0xA426
MODE_FILE = 0x8497
VACANT = b"\xff" * ENTRY


def _entry(mode: int, length: int, cluster: int, name: str) -> bytes:
    raw = bytearray(ENTRY)
    struct.pack_into("<H", raw, 0, mode)
    struct.pack_into("<I", raw, 4, length)
    struct.pack_into("<I", raw, 0x10, cluster)
    encoded = name.encode("latin-1")[:32]
    raw[0x40 : 0x40 + len(encoded)] = encoded
    return bytes(raw)


def _superblock() -> bytes:
    data = bytearray(PAGE_LEN)
    data[0:28] = b"Sony PS2 Memory Card Format "
    data[28:40] = b"1.2.0.0".ljust(12, b"\x00")
    struct.pack_into("<HHHH", data, 40, PAGE_LEN, PAGES_PER_CLUSTER, 16, 0xFF00)
    struct.pack_into("<iiiii", data, 48, CLUSTERS_PER_CARD, ALLOC_OFFSET, CLUSTERS_PER_CARD - 57, 0, 1023)
    struct.pack_into("<i", data, 68, 1022)
    struct.pack_into("<I", data, 80, IFT_CLUSTER)
    return bytes(data)


def _place(image: bytearray, cluster: int, payload: bytes) -> None:
    """Write a cluster's data bytes, skipping each page's spare area."""
    start = cluster * PAGES_PER_CLUSTER * STRIDE
    for page in range(PAGES_PER_CLUSTER):
        chunk = payload[page * PAGE_LEN : (page + 1) * PAGE_LEN]
        offset = start + page * STRIDE
        image[offset : offset + len(chunk)] = chunk


def build_file_card(folders: dict[str, dict[str, bytes]]) -> bytes:
    """A file card holding *folders* (name → {file name: bytes}), nothing else."""
    image = bytearray(CARD_PAGES * STRIDE)
    image[0:PAGE_LEN] = _superblock()

    chains: dict[int, int] = {}
    next_cluster = 0

    def allocate(clusters: int) -> list[int]:
        nonlocal next_cluster
        assigned = list(range(next_cluster, next_cluster + clusters))
        next_cluster += clusters
        for index, cluster in enumerate(assigned):
            chains[cluster] = assigned[index + 1] if index + 1 < len(assigned) else chain_end()
        return assigned

    def chain_end() -> int:
        return 0xFFFFFFFF

    root_count = 2 + len(folders)
    root_clusters = allocate(-(-root_count // ENTRIES_PER_CLUSTER))
    root_entries = [
        _entry(MODE_DIRECTORY, root_count, root_clusters[0], "."),
        _entry(MODE_PARENT, 0, 0, ".."),
    ]

    folder_entries: list[tuple[list[int], list[bytes]]] = []
    for name, files in folders.items():
        count = 2 + len(files)
        clusters = allocate(-(-count // ENTRIES_PER_CLUSTER))
        entries = [
            _entry(MODE_DIRECTORY, 0, clusters[0], "."),
            _entry(MODE_PARENT, 0, 0, ".."),
        ]
        for file_name, payload in files.items():
            data_clusters = allocate(-(-len(payload) // CLUSTER))
            for index, cluster in enumerate(data_clusters):
                _place(image, ALLOC_OFFSET + cluster, payload[index * CLUSTER : (index + 1) * CLUSTER])
            entries.append(_entry(MODE_FILE, len(payload), data_clusters[0], file_name))
        root_entries.append(_entry(MODE_DIRECTORY, count, clusters[0], name))
        folder_entries.append((clusters, entries))

    _write_entries(image, root_clusters, root_entries, root_count)
    for clusters, entries in folder_entries:
        _write_entries(image, clusters, entries, len(entries))

    # Indirect FAT: one entry naming the FAT's cluster.
    ift = bytearray(CLUSTER)
    struct.pack_into("<I", ift, 0, FAT_CLUSTER)
    _place(image, IFT_CLUSTER, bytes(ift))
    # FAT: one entry per allocatable cluster, filled with the chains above.
    fat = bytearray(CLUSTER)
    for cluster, following in chains.items():
        struct.pack_into("<I", fat, cluster * 4, following)
    _place(image, FAT_CLUSTER, bytes(fat))
    return bytes(image)


def _write_entries(image: bytearray, clusters: list[int], entries: list[bytes], count: int) -> None:
    payload = entries + [VACANT] * (count - len(entries))
    payload = payload[:count]
    for index, cluster in enumerate(clusters):
        chunk = b"".join(payload[index * ENTRIES_PER_CLUSTER : (index + 1) * ENTRIES_PER_CLUSTER])
        chunk = chunk.ljust(CLUSTER, b"\xff")
        _place(image, ALLOC_OFFSET + cluster, chunk)
