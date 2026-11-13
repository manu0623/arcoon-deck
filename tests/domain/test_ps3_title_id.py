"""Reading a PS3 game's title id out of its own ``PARAM.SFO``.

The id is the only thing a PS3 save folder is named after, so the save layer needs it
before it can point at anything. These tests pin the two shapes an install takes and the
refusals: a key that is not ``TITLE_ID``, a value that is not a title id, an image with
no ISO9660 tree.
"""

from __future__ import annotations

import struct

from domain.ps3_title_id import SECTOR, find_param_sfo, title_id_from_image, title_id_from_sfo

#: Measured on the reference Deck: ``3D Dot Game Heroes (USA).iso`` states this, as
#: ``0x0204``, inside ``PS3_GAME/PARAM.SFO``.
TITLE_ID = "BLUS30490"


def sfo(*entries: tuple[str, str]) -> bytes:
    """A ``PARAM.SFO`` holding the given key/value pairs, laid out the way the format says."""
    keys = b""
    key_offsets: list[int] = []
    for key, _value in entries:
        key_offsets.append(len(keys))
        keys += key.encode() + bytes(1)
    data = b""
    data_offsets: list[int] = []
    lengths: list[int] = []
    for _key, value in entries:
        data_offsets.append(len(data))
        encoded = value.encode() + bytes(1)
        lengths.append(len(encoded))
        data += encoded
    key_table = 20 + 16 * len(entries)
    data_table = key_table + len(keys)
    out = struct.pack("<4sIIII", b"" + bytes(1) + b"PSF", 0x00000101, key_table, data_table, len(entries))
    for key_offset, length, offset in zip(key_offsets, lengths, data_offsets, strict=True):
        out += struct.pack("<HHIII", key_offset, 0x0204, length, length, offset)
    return out + keys + data


def record(name: str, extent: int, size: int, *, directory: bool = False) -> bytes:
    """One ISO9660 directory record, padded to the even length the format requires."""
    raw = name.encode()
    length = 33 + len(raw)
    if length % 2:
        length += 1
    out = bytearray(length)
    out[0] = length
    struct.pack_into("<I", out, 2, extent)
    struct.pack_into(">I", out, 6, extent)
    struct.pack_into("<I", out, 10, size)
    struct.pack_into(">I", out, 14, size)
    if directory:
        out[25] = 0x02
    out[28] = out[31] = 1
    out[32] = len(raw)
    out[33 : 33 + len(raw)] = raw
    return bytes(out)


def image(sfo_bytes: bytes) -> dict[int, bytes]:
    """A sector-addressed image: volume descriptor, root directory, ``PS3_GAME``, the SFO."""
    pvd = bytearray(SECTOR)
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    root = record(chr(0), 17, SECTOR, directory=True)
    pvd[156 : 156 + len(root)] = root
    listing = record("PS3_GAME", 18, SECTOR, directory=True)
    sfo_entry = record("PARAM.SFO;1", 19, len(sfo_bytes))
    return {
        16: bytes(pvd),
        17: listing.ljust(SECTOR, bytes(1)),
        18: sfo_entry.ljust(SECTOR, bytes(1)),
        19: sfo_bytes.ljust(SECTOR, bytes(1)),
    }


def reader(sectors: dict[int, bytes]):
    """The one read the parser is handed: an offset and a length into the image."""

    def read_at(offset: int, length: int) -> bytes:
        first = offset // SECTOR
        start = offset % SECTOR
        count = (start + length) // SECTOR + 1
        blob = b"".join(sectors.get(number, bytes(SECTOR)) for number in range(first, first + count))
        return blob[start : start + length]

    return read_at


class TestTheTitleId:
    def test_the_id_is_found_beside_the_other_keys(self) -> None:
        blob = sfo(("APP_VER", "01.00"), ("TITLE_ID", TITLE_ID), ("TITLE", "3D Dot Game Heroes"))

        assert title_id_from_sfo(blob) == TITLE_ID

    def test_a_title_without_an_id_is_not_given_one(self) -> None:
        assert title_id_from_sfo(sfo(("APP_VER", "01.00"), ("TITLE", "Some Game"))) is None

    def test_a_value_that_is_not_a_title_id_is_refused(self) -> None:
        """``TITLE_ID`` is four letters and five digits; a demo's ``NPUA80001`` is not one,
        and a save folder is never named after it."""
        assert title_id_from_sfo(sfo(("TITLE_ID", "DEMO"))) is None

    def test_the_terminated_utf8_format_is_read_too(self) -> None:
        blob = bytearray(sfo(("TITLE_ID", TITLE_ID)))
        struct.pack_into("<H", blob, 20 + 2, 0x0404)

        assert title_id_from_sfo(bytes(blob)) == TITLE_ID

    def test_a_value_in_another_format_is_refused(self) -> None:
        blob = bytearray(sfo(("TITLE_ID", TITLE_ID)))
        struct.pack_into("<H", blob, 20 + 2, 0x0404 + 0x0100)

        assert title_id_from_sfo(bytes(blob)) is None

    def test_something_that_is_not_an_sfo_is_refused(self) -> None:
        assert title_id_from_sfo(b"not an sfo at all, just bytes") is None
        assert title_id_from_sfo(b"") is None


class TestTheImage:
    def test_the_sfo_is_read_out_of_the_iso9660_tree(self) -> None:
        assert title_id_from_image(reader(image(sfo(("TITLE_ID", TITLE_ID))))) == TITLE_ID

    def test_an_image_with_no_iso9660_tree_is_refused(self) -> None:
        """A UDF-only image answers nothing rather than a guess."""
        sectors = image(sfo(("TITLE_ID", TITLE_ID)))
        sectors[16] = bytes(SECTOR)

        assert find_param_sfo(reader(sectors)) is None
        assert title_id_from_image(reader(sectors)) is None


class TestTheInstalledGame:
    def test_a_folder_boot_install_states_its_id(self, tmp_path) -> None:
        from services.rom_title_id import ps3_title_id

        game = tmp_path / "3D Dot Game Heroes (USA).ps3"
        (game / "PS3_GAME" / "USRDIR").mkdir(parents=True)
        (game / "PS3_GAME" / "PARAM.SFO").write_bytes(sfo(("TITLE_ID", TITLE_ID)))

        assert ps3_title_id(str(game)) == TITLE_ID
        assert ps3_title_id(str(tmp_path / "missing")) is None

    def test_an_image_on_disk_is_read_through_its_handle(self, tmp_path) -> None:
        from services.rom_title_id import ps3_title_id

        sectors = image(sfo(("TITLE_ID", TITLE_ID)))
        iso = tmp_path / "game.iso"
        iso.write_bytes(b"".join(sectors.get(number, bytes(SECTOR)) for number in range(max(sectors) + 1)))

        assert ps3_title_id(str(iso)) == TITLE_ID


def test_the_self_and_parent_records_are_not_mistaken_for_an_entry() -> None:
    """A directory always opens with the chr(0) and 0x01 records; the walk skips them."""
    sectors = image(sfo(("TITLE_ID", TITLE_ID)))
    sectors[17] = (record(chr(0), 17, SECTOR, directory=True) + record(chr(1), 17, SECTOR, directory=True)).ljust(
        SECTOR, bytes(1)
    )

    assert title_id_from_image(reader(sectors)) is None
