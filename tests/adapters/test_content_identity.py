"""The identity adapter: which bytes a platform's reader gets."""

from __future__ import annotations

import logging
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
