"""The identity adapter: which bytes a platform's reader gets."""

from __future__ import annotations

import logging
import struct
from typing import TYPE_CHECKING

from adapters.content_identity import ContentIdentityAdapter

if TYPE_CHECKING:
    from pathlib import Path


def _adapter() -> ContentIdentityAdapter:
    return ContentIdentityAdapter(logger=logging.getLogger("test"))


def _ncsd_image(program_id: int = 0x0004000000054000) -> bytes:
    """A cart image whose first partition (at 0x4000) is an NCCH with *program_id*."""
    image = bytearray(0x4000 + 0x200)
    image[0x100:0x104] = b"NCSD"
    image[0x120:0x124] = (0x20).to_bytes(4, "little")  # 0x20 media units = 0x4000
    image[0x4000 + 0x100 : 0x4000 + 0x104] = b"NCCH"
    image[0x4000 + 0x118 : 0x4000 + 0x120] = program_id.to_bytes(8, "little")
    return bytes(image)


class TestN3ds:
    def test_a_cart_image_is_read_through_its_first_partition(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.3ds"
        rom.write_bytes(_ncsd_image())

        identity = _adapter()(str(rom), "n3ds")

        assert identity is not None
        assert identity.save_id == "0004000000054000"

    def test_a_bare_ncch_is_read_directly(self, tmp_path: Path) -> None:
        rom = tmp_path / "title.cxi"
        image = bytearray(0x400)
        image[0x100:0x104] = b"NCCH"
        image[0x118:0x120] = (0x0004000000030600).to_bytes(8, "little")
        rom.write_bytes(bytes(image))

        identity = _adapter()(str(rom), "3ds")

        assert identity is not None
        assert identity.save_id == "0004000000030600"


class TestDiscSerials:
    def test_a_ps2_image_reads_its_system_cnf(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.iso"
        rom.write_bytes(b"\x00" * 0x8000 + b"BOOT2 = cdrom0:\\SLUS_203.12;1\nVER = 1.00\n")

        identity = _adapter()(str(rom), "ps2")

        assert identity is not None
        assert identity.save_id == "SLUS-20312"

    def test_the_same_file_answers_differently_by_platform(self, tmp_path: Path) -> None:
        # An .iso is a PS1, PS2 or GameCube image depending on what it was installed
        # for; the platform picks the reader, and the wrong reader refuses on its magic.
        rom = tmp_path / "game.iso"
        rom.write_bytes(b"\x00" * 0x8000 + b"BOOT = cdrom:\\SCES_123.45;1\n")

        assert _adapter()(str(rom), "psx").save_id == "SCES-12345"
        assert _adapter()(str(rom), "gamecube") is None


class TestOtherPlatforms:
    def test_a_dreamcast_boot_sector(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.gdi"
        head = bytearray(0x100)
        head[0:16] = b"SEGA SEGAKATANA "
        head[0x40:0x48] = b"T-97063D"
        rom.write_bytes(bytes(head))

        identity = _adapter()(str(rom), "dreamcast")

        assert identity is not None
        assert identity.save_id == "T-97063D"

    def test_a_gamecube_disc(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.iso"
        rom.write_bytes(b"GMSE01" + b"\x00" * 0x1A)

        identity = _adapter()(str(rom), "gc")

        assert identity is not None
        assert identity.save_id == "GMSE"


class TestDegradation:
    def test_an_unreadable_file_is_logged_and_answers_nothing(self, tmp_path: Path, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            identity = _adapter()(str(tmp_path / "missing.iso"), "ps2")

        assert identity is None
        assert "cannot read" in caplog.text

    def test_a_platform_with_no_reader_answers_nothing(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.gba"
        rom.write_bytes(b"BOOT2 = cdrom0:\\SLUS_203.12;1\n")

        assert _adapter()(str(rom), "gba") is None



_SECTOR = 2048
_NUL = chr(0)


def _iso_record(name: str, extent: int, size: int, *, directory: bool = False) -> bytes:
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


def _param_sfo(**entries: str) -> bytes:
    keys = b""
    offsets: list[int] = []
    for key in entries:
        offsets.append(len(keys))
        keys += key.encode() + bytes(1)
    data = b""
    values: list[tuple[int, int]] = []
    for value in entries.values():
        values.append((len(data), len(value) + 1))
        data += value.encode() + bytes(1)
    key_table = 20 + 16 * len(entries)
    data_table = key_table + len(keys)
    out = struct.pack("<4sIIII", bytes(1) + b"PSF", 0x00000101, key_table, data_table, len(entries))
    for offset, (value_offset, length) in zip(offsets, values, strict=True):
        out += struct.pack("<HHIII", offset, 0x0204, length, length, value_offset)
    return out + keys + data


def _ps3_iso(sfo: bytes, *, game_dir: str = "PS3_GAME") -> bytes:
    """An image whose root lists *game_dir*, holding ``PARAM.SFO``."""
    pvd = bytearray(_SECTOR)
    pvd[0] = 1  # primary volume descriptor
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    root = _iso_record(_NUL, 17, _SECTOR, directory=True)
    pvd[156 : 156 + len(root)] = root
    listing = _iso_record(game_dir, 18, _SECTOR, directory=True)
    sfo_entry = _iso_record("PARAM.SFO;1", 19, len(sfo))
    sectors = {
        16: bytes(pvd),
        17: listing.ljust(_SECTOR, bytes(1)),
        18: sfo_entry.ljust(_SECTOR, bytes(1)),
        19: sfo.ljust(_SECTOR, bytes(1)),
    }
    return b"".join(sectors.get(index, bytes(_SECTOR)) for index in range(20))


class TestPs3:
    """Measured on the reference Deck: ``3D Dot Game Heroes (USA).iso`` is a plain ISO 9660
    image whose root lists ``PS3_GAME``, and the id it states is ``BLUS30490``."""

    def test_a_disc_image_reads_its_param_sfo(self, tmp_path: Path) -> None:
        rom = tmp_path / "3D Dot Game Heroes (USA).iso"
        rom.write_bytes(_ps3_iso(_param_sfo(TITLE="3D DOT GAME HEROES", TITLE_ID="BLUS30490")))

        identity = _adapter()(str(rom), "ps3")

        assert identity is not None
        assert identity.save_id == "BLUS30490"

    def test_a_disc_without_a_ps3_game_directory_answers_nothing(self, tmp_path: Path) -> None:
        rom = tmp_path / "game.iso"
        rom.write_bytes(_ps3_iso(_param_sfo(TITLE_ID="BLUS30490"), game_dir="PSP_GAME"))

        assert _adapter()(str(rom), "ps3") is None

    def test_a_folder_boot_install_states_its_id(self, tmp_path: Path) -> None:
        game = tmp_path / "Game.ps3"
        (game / "PS3_GAME" / "USRDIR").mkdir(parents=True)
        (game / "PS3_GAME" / "PARAM.SFO").write_bytes(_param_sfo(TITLE_ID="BCUS98247"))

        identity = _adapter()(str(game), "ps3")

        assert identity is not None
        assert identity.save_id == "BCUS98247"

    def test_a_folder_without_a_param_sfo_answers_nothing(self, tmp_path: Path) -> None:
        game = tmp_path / "Game.ps3"
        (game / "USRDIR").mkdir(parents=True)

        assert _adapter()(str(game), "ps3") is None
