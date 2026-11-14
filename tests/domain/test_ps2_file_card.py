"""Reading a PCSX2 file memory card: the save folders and the bytes of each file.

The layout under test is the measured one (see ``tests/fakes/ps2_card``): 512-byte
pages with a 16-byte spare area, clusters of two pages, an indirect FAT plus FAT, and
directory entries that keep their name at ``0x40``. What matters for sync is that a
file's spans reassemble exactly the bytes the card holds — an extractor that is off by
one page produces a save that loads as garbage.
"""

from __future__ import annotations

import pytest
from fakes.ps2_card import build_file_card

from domain.ps2_file_card import Ps2CardError, host_file_name, read_file_card

FOLDER = "BASCUS-97198YAOTWTD!"


def _payload(size: int, seed: int) -> bytes:
    return bytes((index * 31 + seed) % 251 for index in range(size))


def _contents(image: bytes, spans: tuple[tuple[int, int], ...]) -> bytes:
    return b"".join(image[start : start + length] for start, length in spans)


class TestReadFileCard:
    def test_a_save_folder_and_its_files_are_read_back(self) -> None:
        save = _payload(1500, 7)
        image = build_file_card({FOLDER: {"icon.sys": b"PS2D" + b"\x00" * 60, "save1": save}})

        folders = read_file_card(image)

        assert [folder.name for folder in folders] == [FOLDER]
        by_name = {item.name: item for item in folders[0].files}
        assert by_name["icon.sys"].size == 64
        assert by_name["save1"].size == len(save)
        assert _contents(image, by_name["save1"].spans) == save

    def test_a_file_spanning_several_clusters_keeps_its_bytes_in_order(self) -> None:
        save = _payload(5000, 3)
        image = build_file_card({FOLDER: {"save1": save}})

        item = read_file_card(image)[0].files[0]

        assert len(item.spans) > 1
        assert _contents(image, item.spans) == save

    def test_several_folders_are_all_read(self) -> None:
        image = build_file_card(
            {
                FOLDER: {"save1": b"a" * 10},
                "BASLUS-20000OTHER": {"save1": b"b" * 20},
            }
        )

        folders = read_file_card(image)

        assert [folder.name for folder in folders] == [FOLDER, "BASLUS-20000OTHER"]
        assert [folder.files[0].size for folder in folders] == [10, 20]

    def test_vacant_slots_are_not_folders(self) -> None:
        # A directory with more slots than entries: the rest are 0xff-filled.
        image = build_file_card({FOLDER: {"save1": b"x"}})

        folders = read_file_card(image)

        assert all(folder.name.strip("\xff") for folder in folders)

    def test_an_empty_card_holds_no_save(self) -> None:
        assert read_file_card(build_file_card({})) == ()

    def test_something_that_is_not_a_card_is_refused(self) -> None:
        with pytest.raises(Ps2CardError):
            read_file_card(b"\x00" * 4096)

    def test_a_card_with_no_superblock_magic_is_refused(self) -> None:
        image = bytearray(build_file_card({FOLDER: {"save1": b"x"}}))
        image[0:28] = b"not a memory card format  "

        with pytest.raises(Ps2CardError):
            read_file_card(bytes(image))

    def test_a_short_image_is_refused(self) -> None:
        with pytest.raises(Ps2CardError):
            read_file_card(b"Sony PS2 Memory Card Format " + b"\x00" * 10)


class TestHostFileName:
    """PCSX2's own host names, from ``FileAccessHelper::CleanMemcardFilename``."""

    def test_the_characters_a_host_refuses_become_underscores(self):
        assert host_file_name("1: Home Sweet Home") == "1_ Home Sweet Home"
        assert host_file_name("a" + chr(92) + 'b%c:d|e"f<g>h') == "a_b_c_d_e_f_g_h"

    def test_trailing_dots_and_spaces_are_replaced(self):
        assert host_file_name("save. ") == "save__"
        assert host_file_name("save...") == "save___"

    def test_a_name_a_host_accepts_is_unchanged(self):
        assert host_file_name("BASLUS-21423GTA30001") == "BASLUS-21423GTA30001"
        assert host_file_name("icon.sys") == "icon.sys"
