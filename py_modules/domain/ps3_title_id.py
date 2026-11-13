"""Read a PlayStation 3 game's title id out of the game itself.

A PS3 save folder is named after the game's title id and nothing else — measured on
the reference Deck, ``dev_hdd0/home/00000001/savedata`` holds ``BCES00301_SAVE_1``,
``BCUS98111-AUTOSAVE`` and ``BLUS30443DEMONSS005``. The library row names the game
(``3D Dot Game Heroes (USA).iso``) and never the id, so a save layer that reads rows
alone can point at a directory full of other games' saves and not one save of its own.
The id lives in ``PS3_GAME/PARAM.SFO`` inside the image, which is why this module asks
the game rather than the row.

**Only the two shapes a PS3 install takes are read**: a folder whose ``PS3_GAME``
sits beside the boot file, and an ISO9660 image whose root directory lists it. The
reference image answered ``PS3_DISC.SFB``, ``PS3_GAME`` and ``PS3_UPDATE`` at the
root, so the walk is the plain ISO9660 one — no Joliet, no Rock Ridge, no UDF. An
image that carries only UDF answers ``None`` rather than a guess.

**Reading is the caller's business.** Both entry points take a ``read_at`` callable
so the parsing stays here, where it can be tested against bytes, and the file handle
stays in the adapter.
"""

from __future__ import annotations

import struct
from collections.abc import Callable, Iterator

SECTOR = 2048

#: ``read_at(offset, length) -> bytes`` — every read this module needs of an image.
ReadAt = Callable[[int, int], bytes]

_SFO_MAGIC = b"\x00PSF"
_SFO_HEADER = 20
_SFO_ENTRY = 16
_UTF8 = 0x0404
_PS3_GAME = "PS3_GAME"
_PARAM_SFO = "PARAM.SFO"
_ROOT_RECORD = 156


def title_id_from_sfo(blob: bytes) -> str | None:
    """Return the ``TITLE_ID`` a ``PARAM.SFO`` states, or ``None``.

    The format is a header of four 32-bit fields, then ``count`` entries of five, and
    two string tables whose offsets are absolute. Keys are compared, never scanned for,
    because a title id appearing inside some other field would be a coincidence.
    """
    if len(blob) < _SFO_HEADER or not blob.startswith(_SFO_MAGIC):
        return None
    key_table, data_table, count = struct.unpack_from("<III", blob, 8)
    for index in range(count):
        entry = _SFO_HEADER + index * _SFO_ENTRY
        if entry + _SFO_ENTRY > len(blob):
            return None
        key_offset, data_format, data_len, _max_len, data_offset = struct.unpack_from("<HHIII", blob, entry)
        key = _text(blob, key_table + key_offset)
        if key != "TITLE_ID":
            continue
        if data_format != _UTF8:
            return None
        value = _text(blob, data_table + data_offset, data_len)
        return _normalise(value)
    return None


def find_param_sfo(read_at: ReadAt) -> bytes | None:
    """Return the ``PARAM.SFO`` bytes an ISO9660 image holds, or ``None``.

    One level down from the root is all a PS3 disc needs: the root lists ``PS3_GAME``
    and that directory holds the file, so a recursive walk would be work nobody asked
    of this.
    """
    pvd = read_at(16 * SECTOR, SECTOR)
    if pvd[1:6] != b"CD001":
        return None
    root = pvd[_ROOT_RECORD : _ROOT_RECORD + 34]
    if len(root) < 34:
        return None
    game = _child(read_at, root, _PS3_GAME)
    if game is None or not game.is_directory:
        return None
    sfo = _child(read_at, game.record, _PARAM_SFO)
    if sfo is None or sfo.is_directory or not sfo.size:
        return None
    return read_at(sfo.extent * SECTOR, sfo.size)


def title_id_from_image(read_at: ReadAt) -> str | None:
    """The title id an ISO9660 image states, if it states one."""
    blob = find_param_sfo(read_at)
    return title_id_from_sfo(blob) if blob else None


def _child(read_at: ReadAt, record: bytes, wanted: str) -> _Entry | None:
    """Find one named entry inside the directory ``record`` describes."""
    extent, size = struct.unpack_from("<I", record, 2)[0], struct.unpack_from("<I", record, 10)[0]
    if not size:
        return None
    for entry in _records(read_at(extent * SECTOR, size)):
        if entry.name.upper() == wanted:
            return entry
    return None


class _Entry:
    __slots__ = ("extent", "is_directory", "name", "record", "size")

    def __init__(self, name: str, extent: int, size: int, is_directory: bool, record: bytes) -> None:
        self.name = name
        self.extent = extent
        self.size = size
        self.is_directory = is_directory
        self.record = record


def _records(directory: bytes) -> Iterator[_Entry]:
    """Walk ISO9660 directory records, honouring the zero-length sector padding.

    A record shorter than 34 bytes, or one that runs past the block it starts in, ends
    the walk: an image that says so is malformed and a guess from it would be worse
    than nothing.
    """
    offset = 0
    while offset < len(directory):
        length = directory[offset]
        if length == 0:
            offset = (offset // SECTOR + 1) * SECTOR
            continue
        end = offset + length
        if length < 34 or end > len(directory):
            return
        record = directory[offset:end]
        name_len = record[32]
        raw = record[33 : 33 + name_len]
        offset = end
        if name_len == 1 and raw in (b"\x00", b"\x01"):
            continue
        name = raw.split(b";")[0].rstrip(b"\x00").decode("latin-1")
        extent = struct.unpack_from("<I", record, 2)[0]
        size = struct.unpack_from("<I", record, 10)[0]
        yield _Entry(name, extent, size, bool(record[25] & 0x02), record)


def _text(blob: bytes, offset: int, length: int | None = None) -> str:
    if offset < 0 or offset >= len(blob):
        return ""
    chunk = blob[offset:] if length is None else blob[offset : offset + length]
    return chunk.split(b"\x00", 1)[0].decode("utf-8", "replace")


def _normalise(value: str) -> str | None:
    """A title id is four letters and five digits; anything else is not one."""
    candidate = value.strip().upper()
    if len(candidate) != 9 or not candidate[:4].isalpha() or not candidate[4:].isdigit():
        return None
    return candidate
