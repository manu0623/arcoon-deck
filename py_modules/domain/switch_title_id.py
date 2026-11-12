"""Reading a Switch ROM's title id out of the file itself.

Eden files a save under the title id, so carrying one at all starts here: without the id
there is no way to know which ``nand/user/save/<user>/<slot>/<id>`` directory belongs to a
ROM, and asking the emulator would mean reading its log after the fact.

The id is not a guess. A ``.nsp`` is a PFS0 archive, and its string table names the
tickets inside it after the id they are for — ``01006bb00c6f00000000000000000008``, which
is the 16-hex-digit title id followed by the key generation. Measured on the reference
Deck: the ``.nsp`` for *Link's Awakening* names
``01006bb00c6f00000000000000000008.tik``, and Eden printed ``01006BB00C6F0000`` when it
booted the same file — so the read is checkable against the emulator's own statement.

Pure compute over bytes: the caller reads the archive header, this module parses it. A
``.xci`` is a different container (its root is an HFS0 of partitions, with no ticket list),
so it answers ``None`` rather than a wrong id — a refusal the caller can name.

See [save-structure.md](../../docs/architecture/save-structure.md) for the measured tree
this feeds.
"""

from __future__ import annotations

import struct

PFS0_MAGIC = b"PFS0"

# An entry table entry is ``<u64 offset><u64 size><u32 name offset><u32 reserved>``.
_ENTRY = struct.Struct("<QQII")

# The shortest header that can hold a magic, a count and a string-table size.
_MIN_HEADER = 0x10

# A ticket name is the 16-hex-digit title id followed by the 16-hex-digit key generation.
_TICKET_TITLE_DIGITS = 16


def title_id_from_nsp(head: bytes) -> str | None:
    """The title id a ``.nsp`` header names, or ``None`` when it names none.

    *head* is the beginning of the archive — the PFS0 header, its entry table and its
    string table. The caller reads a bounded prefix (64 KiB is ample: the tables sit at
    the front), so nothing here seeks and nothing here opens a file.

    Only the ticket entry is read. The alternative — parsing an NCA header for the id —
    needs the NCA's own offset and a plaintext header that a dumped archive need not
    carry; the ticket filename states the same id in the table this function already has.
    """
    if len(head) < _MIN_HEADER or head[:4] != PFS0_MAGIC:
        return None
    count, string_table_size = struct.unpack_from("<II", head, 4)
    if count <= 0:
        return None
    # The string table starts where the entry table ends.
    strings_start = _MIN_HEADER + count * _ENTRY.size
    if strings_start + string_table_size > len(head):
        return None
    strings = head[strings_start : strings_start + string_table_size]
    for index in range(count):
        _offset, _size, name_offset, _reserved = _ENTRY.unpack_from(head, _MIN_HEADER + index * _ENTRY.size)
        name = _entry_name(strings, name_offset)
        if name is None or not name.lower().endswith(".tik"):
            continue
        stem = name.rsplit(".", 1)[0]
        title = stem[:_TICKET_TITLE_DIGITS]
        if len(title) == _TICKET_TITLE_DIGITS and all(char in "0123456789abcdefABCDEF" for char in title):
            return title.upper()
    return None


def _entry_name(strings: bytes, name_offset: int) -> str | None:
    """The NUL-terminated name at *name_offset* in the string table, or ``None``."""
    if name_offset >= len(strings):
        return None
    end = strings.find(b"\0", name_offset)
    if end < 0:
        return None
    return strings[name_offset:end].decode("utf-8", "replace")
