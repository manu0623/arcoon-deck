"""The PSP disc id: an ISO 9660 walk and a PARAM.SFO table (ADR-0048)."""

from __future__ import annotations

from domain.content_identity import (
    IdentityKind,
    iso9660_entry,
    iso9660_root_directory,
    psp_disc_id,
    save_id_text,
)

NUL = bytes([0])
SECTOR = 2048


def _sfo(entries: list[tuple[str, bytes]]) -> bytes:
    """A PARAM.SFO with *entries*, built the way the format lays them out."""
    keys = b""
    key_offsets: list[int] = []
    for key, _value in entries:
        key_offsets.append(len(keys))
        keys += key.encode() + NUL
    values = b""
    data_offsets: list[int] = []
    for _key, value in entries:
        data_offsets.append(len(values))
        values += value + NUL
    header = 20
    key_table = header + 16 * len(entries)
    data_table = key_table + len(keys)
    out = b"\x00PSF" + (0x101).to_bytes(4, "little") + key_table.to_bytes(4, "little")
    out += data_table.to_bytes(4, "little") + len(entries).to_bytes(4, "little")
    for offset, value_offset, (_key, value) in zip(key_offsets, data_offsets, entries, strict=True):
        out += offset.to_bytes(2, "little") + (0x0004).to_bytes(2, "little")
        out += (len(value) + 1).to_bytes(4, "little") * 2 + value_offset.to_bytes(4, "little")
    return out + keys + values


def _record(name: str, extent: int, size: int) -> bytes:
    """One ISO 9660 directory record naming *name*.

    The name area is padded to an even length, and byte 32 of the record is the name's
    own length — the two are separate fields, which is why the name does not carry its
    length byte with it.
    """
    raw = name.encode()
    area = raw if len(raw) % 2 == 0 else raw + NUL
    record = bytearray(33 + len(area))
    record[0] = 33 + len(area)
    record[2:6] = extent.to_bytes(4, "little")
    record[10:14] = size.to_bytes(4, "little")
    record[32] = len(raw)
    record[33:] = area
    return bytes(record)


def _volume_descriptor(root_extent: int, root_size: int) -> bytes:
    pvd = bytearray(SECTOR)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    pvd[156 : 156 + 34] = _record("\x00", root_extent, root_size)
    return bytes(pvd)


class TestTheDiscId:
    def test_it_is_read_from_param_sfo(self) -> None:
        sfo = _sfo([("TITLE", b"Burnout Legends"), ("DISC_ID", b"ULUS10064"), ("VERSION", b"1.00")])

        identity = psp_disc_id(sfo)

        assert identity is not None
        assert identity.save_id == "ULUS10064"
        assert identity.kind is IdentityKind.DISC_ID
        assert "PARAM.SFO" in identity.source

    def test_a_disc_id_is_spent_verbatim(self) -> None:
        """The bank matches a save folder on the id as written, so no reshaping happens."""
        identity = psp_disc_id(_sfo([("DISC_ID", b"ULES00502")]))

        assert identity is not None
        assert save_id_text(identity) == "ULES00502"

    def test_a_file_without_the_magic_names_nothing(self) -> None:
        assert psp_disc_id(b"\x00PSX" + bytes(60)) is None

    def test_an_sfo_without_a_disc_id_names_nothing(self) -> None:
        assert psp_disc_id(_sfo([("TITLE", b"Something")])) is None

    def test_a_disc_id_of_the_wrong_shape_names_nothing(self) -> None:
        """Four letters and five digits is the shape; anything else is a mis-read table."""
        assert psp_disc_id(_sfo([("DISC_ID", b"ULUS100640")])) is None
        assert psp_disc_id(_sfo([("DISC_ID", b"")])) is None


class TestTheIsoWalk:
    def test_the_root_directory_comes_from_the_volume_descriptor(self) -> None:
        assert iso9660_root_directory(_volume_descriptor(20, SECTOR)) == (20, SECTOR)

    def test_a_sector_that_is_not_a_volume_descriptor_names_nothing(self) -> None:
        assert iso9660_root_directory(bytes(SECTOR)) is None
        assert iso9660_root_directory(b"\x00CD001" + bytes(SECTOR)) is None

    def test_an_entry_is_found_by_name(self) -> None:
        directory = _record("\x00", 20, SECTOR) + _record("PSP_GAME", 21, SECTOR)

        assert iso9660_entry(directory, "PSP_GAME") == (21, SECTOR)
        assert iso9660_entry(directory, "psp_game") == (21, SECTOR)

    def test_the_version_suffix_is_ignored(self) -> None:
        directory = _record("\x00", 20, SECTOR) + _record("PARAM.SFO;1", 22, 512)

        assert iso9660_entry(directory, "PARAM.SFO") == (22, 512)

    def test_a_zero_length_record_is_padding_not_the_end(self) -> None:
        """Records never straddle a sector, so a listing continues after the padding."""
        first = _record("\x00", 20, SECTOR)
        padded = first + bytes(-len(first) % SECTOR) + _record("PSP_GAME", 21, SECTOR)

        assert iso9660_entry(padded, "PSP_GAME") == (21, SECTOR)

    def test_an_absent_entry_names_nothing(self) -> None:
        assert iso9660_entry(_record("\x00", 20, SECTOR), "PSP_GAME") is None
