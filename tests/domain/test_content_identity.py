"""Parsing a game's own identity out of its bytes.

Every case here builds the bytes by hand rather than shipping a ROM: the point is the
format's layout, and a fixture states exactly which offsets a reader depends on.
"""

from __future__ import annotations

import struct

import pytest

from domain.content_identity import (
    ContentIdentity,
    IdentityKind,
    disc_serial,
    dreamcast_product_number,
    gamecube_game_code,
    n3ds_partition_offset,
    n3ds_title_id,
    ps3_title_id,
    rvz_wii_game_code,
    save_id_text,
    wii_game_code,
    wii_title_dirname,
)


def _ncsd_head(*, units: int = 0x20) -> bytes:
    """A 3DS cart header: NCSD magic at 0x100, first partition offset at 0x120."""
    head = bytearray(0x200)
    head[0x100:0x104] = b"NCSD"
    head[0x120:0x124] = units.to_bytes(4, "little")
    return bytes(head)


def _ncch_head(program_id: int, *, magic: bytes = b"NCCH") -> bytes:
    head = bytearray(0x400)
    head[0x100:0x104] = magic
    head[0x118:0x120] = program_id.to_bytes(8, "little")
    return bytes(head)


class TestDiscSerial:
    def test_a_ps2_boot_line_yields_the_hyphenated_serial(self) -> None:
        text = "BOOT2 = cdrom0:\\SLUS_203.12;1\nVER = 1.00\nVMODE = NTSC\n"

        assert disc_serial(text) == ContentIdentity("SLUS-20312", IdentityKind.DISC_SERIAL, "PS2 BOOT2 line")

    def test_a_ps1_boot_line_is_read_too(self) -> None:
        text = "BOOT = cdrom:\\SCES_123.45;1\nTCB = 4\nEVENT = 10\n"

        assert disc_serial(text) == ContentIdentity("SCES-12345", IdentityKind.DISC_SERIAL, "PS1 BOOT line")

    def test_a_hyphenated_boot_serial_is_normalised_the_same_way(self) -> None:
        # Publishers and regions spell the separator both ways; one id comes out.
        assert disc_serial("BOOT2 = cdrom0:\\SLPS-01234;1\n").save_id == "SLPS-01234"

    def test_a_serial_shaped_token_off_the_boot_line_is_ignored(self) -> None:
        # Licence text and padding are full of serial-like strings; the boot line is the
        # one the console itself follows, so only it may answer.
        text = "Copyright SCUS_944.26 and SLUS_999.99\nVER = 1.00\n"

        assert disc_serial(text) is None

    def test_no_boot_line_at_all_refuses(self) -> None:
        assert disc_serial("") is None
        assert disc_serial("BOOT2 = cdrom0:\\NOTASERIAL;1\n") is None


class TestDreamcastProductNumber:
    def _ip_bin(self, product: bytes) -> bytes:
        head = bytearray(0x100)
        head[0:16] = b"SEGA SEGAKATANA "
        head[0x40 : 0x40 + len(product)] = product
        return bytes(head)

    def test_the_product_number_is_the_id(self) -> None:
        identity = dreamcast_product_number(self._ip_bin(b"T-97063D  "))

        assert identity is not None
        assert identity.save_id == "T-97063D"
        assert identity.kind == IdentityKind.PRODUCT_NUMBER

    def test_an_image_without_the_ip_bin_magic_refuses(self) -> None:
        # Otherwise ten bytes of any header would be read as a product number.
        assert dreamcast_product_number(b"\x00" * 0x100) is None

    def test_a_header_too_short_to_hold_the_field_refuses(self) -> None:
        assert dreamcast_product_number(b"SEGA SEGAKATANA " + b"\x00" * 0x20) is None


class TestGamecubeGameCode:
    def test_the_four_character_code_is_the_id(self) -> None:
        identity = gamecube_game_code(b"GMSE01" + b"\x00" * 0x1A)

        assert identity is not None
        assert identity.save_id == "GMSE"
        assert identity.kind == IdentityKind.GAME_CODE

    def test_a_non_gamecube_console_byte_refuses(self) -> None:
        assert gamecube_game_code(b"XXXX01" + b"\x00" * 0x1A) is None

    def test_an_unknown_region_refuses(self) -> None:
        # The region byte is the only thing separating a real header from four printable
        # bytes at the front of an unrelated file.
        assert gamecube_game_code(b"GMZZ01" + b"\x00" * 0x1A) is None


class TestN3ds:
    def test_the_partition_offset_is_stated_in_media_units(self) -> None:
        assert n3ds_partition_offset(_ncsd_head(units=0x20)) == 0x4000

    def test_a_bare_ncch_has_no_partition_offset(self) -> None:
        assert n3ds_partition_offset(_ncch_head(0x0004000000054000)) is None

    def test_a_zero_partition_offset_refuses(self) -> None:
        assert n3ds_partition_offset(_ncsd_head(units=0)) is None

    def test_the_program_id_is_the_title_id(self) -> None:
        identity = n3ds_title_id(_ncch_head(0x0004000000054000))

        assert identity is not None
        assert identity.save_id == "0004000000054000"
        assert identity.kind == IdentityKind.TITLE_ID

    def test_a_title_outside_the_application_category_refuses(self) -> None:
        # A system title has no save this bank could place, and reporting its id would
        # point the caller at a folder the emulator never writes.
        assert n3ds_title_id(_ncch_head(0x0004013000001A02)) is None

    def test_a_non_ncch_blob_refuses(self) -> None:
        assert n3ds_title_id(b"\x00" * 0x200) is None

    @pytest.mark.parametrize("size", [0, 4, 0x118, 0x11F])
    def test_a_header_too_short_for_the_field_refuses(self, size: int) -> None:
        assert n3ds_title_id(b"NCCH" + b"\x00" * max(size - 4, 0)) is None

def _param_sfo(**entries: str) -> bytes:
    """A PARAM.SFO holding *entries*, laid out the way the format states."""
    keys = b''
    offsets: list[int] = []
    for key in entries:
        offsets.append(len(keys))
        keys += key.encode() + bytes(1)
    data = b''
    values: list[tuple[int, int]] = []
    for value in entries.values():
        values.append((len(data), len(value) + 1))
        data += value.encode() + bytes(1)
    key_table = 20 + 16 * len(entries)
    data_table = key_table + len(keys)
    out = struct.pack('<4sIIII', bytes(1) + b'PSF', 0x00000101, key_table, data_table, len(entries))
    for offset, (value_offset, length) in zip(offsets, values, strict=True):
        out += struct.pack('<HHIII', offset, 0x0204, length, length, value_offset)
    return out + keys + data


class TestPs3TitleId:
    def test_the_title_id_is_the_save_id(self) -> None:
        """Measured on the reference Deck: Sly Cooper: Thieves in Time wrote its save under
        BCUS98247_SAVE_SLOT_00000, the id its own PARAM.SFO states."""
        identity = ps3_title_id(_param_sfo(TITLE_ID='BCUS98247', TITLE='Sly Cooper: Thieves in Time'))

        assert identity is not None
        assert identity.save_id == 'BCUS98247'
        assert identity.kind == IdentityKind.DISC_ID

    def test_a_file_without_a_title_id_is_not_given_one(self) -> None:
        assert ps3_title_id(_param_sfo(TITLE='Some Game')) is None

    def test_a_value_that_is_not_a_disc_id_refuses(self) -> None:
        assert ps3_title_id(_param_sfo(TITLE_ID='DEMO')) is None

    def test_something_that_is_not_an_sfo_refuses(self) -> None:
        assert ps3_title_id(b'not an sfo, just bytes') is None
        assert ps3_title_id(b'') is None


class TestTheWiiGameCode:
    """Measured on the reference Deck: a Wii `.rvz` carries `SB4E01` at 0x58, and Dolphin
    then keeps that save in `Wii/title/00010000/53423445/data`."""

    def test_a_bare_wii_disc_header_names_the_code(self) -> None:
        identity = wii_game_code(b"SB4E01" + bytes(0x20))
        assert identity is not None
        assert identity.save_id == "SB4E"
        assert identity.kind is IdentityKind.WII_GAME_CODE
        assert identity.region == "USA"

    def test_the_rvz_container_is_read_at_the_measured_offset(self) -> None:
        head = bytearray(0x120)
        head[0:4] = b"RVZ" + bytes([1])
        head[0x58:0x5E] = b"SB4E01"
        identity = rvz_wii_game_code(bytes(head))
        assert identity is not None
        assert identity.save_id == "SB4E"
        assert identity.source == "Wii .rvz header"

    def test_a_gamecube_code_reads_as_its_own_four_characters(self) -> None:
        """The six bytes are shaped the same; only the console byte and the filing differ."""
        identity = wii_game_code(b"GZ2E01" + bytes(0x20))
        assert identity is not None
        assert identity.save_id == "GZ2E"

    @pytest.mark.parametrize("code", [b"SB4X01", bytes(6), b"SB4E"])
    def test_anything_that_is_not_a_code_refuses(self, code: bytes) -> None:
        assert wii_game_code(code + bytes(0x20)) is None

    def test_the_title_directory_is_the_codes_ascii_bytes_in_hex(self) -> None:
        assert wii_title_dirname("SB4E") == "53423445"

    def test_the_save_id_spelling_is_that_directory_name(self) -> None:
        identity = wii_game_code(b"SMNE01" + bytes(0x20))
        assert identity is not None
        assert save_id_text(identity) == "534d4e45"
