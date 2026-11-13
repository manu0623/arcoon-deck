"""Which saves are restored by extraction rather than written as a file.

Measured failure this rule exists for: RomM held a GameCube save as one zip whose
member was ``01-GZ2E-gczelda2.gci``; the plugin renamed that zip into
``~/retrodeck/saves/gc/`` and Dolphin, in GCI-Folder mode, read
``User/GC/USA/Card A/`` — found it empty and offered a new card. The save was on
disk the whole time, in a form nothing opens.
"""

from __future__ import annotations

import pytest

from domain.save_bank import restores_by_extraction


class TestWhichPlatformsRestoreByExtraction:
    def test_gamecube_is_a_member_set(self) -> None:
        """Every ``.gci`` carrying the disc's code, which RomM ships as one zip."""
        assert restores_by_extraction("gc") is True

    def test_the_alias_answers_the_same_way(self) -> None:
        """RomM spells it ``ngc``; the bank must not care which name it is handed."""
        assert restores_by_extraction("ngc") is True

    def test_a_switch_title_folder_is_a_member_set_too(self) -> None:
        """Eden's per-title directory, which RomM also ships as one zip.

        Measured on the reference Deck (2026-11-12): the folder is
        ``<nand>/user/save/<user>/<slot>/<title id>/`` of files Eden names itself, and the
        server's save for the same ROM is a zip. Restoring the zip into that folder — the
        old behaviour for a non-GameCube system — would leave Eden reading none of it, the
        same failure this rule was written for. It is flat, which is the condition.
        """
        assert restores_by_extraction("switch") is True

    @pytest.mark.parametrize("platform", ["psp", "ps3"])
    def test_a_prefix_bundle_is_a_member_set(self, platform: str) -> None:
        """PSP and PS3 saves are sibling folders sharing the game's id prefix.

        RomM stores one as `<title> [timestamp].zip`, and a restore that renamed that zip
        into the folder instead of extracting it would leave PPSSPP reading an empty
        memory stick — the same failure GameCube's card had (ADR-0048).
        """
        assert restores_by_extraction(platform) is True

    def test_a_3ds_title_tree_is_a_member_set(self) -> None:
        """``data`` and ``extdata`` are directories of files Azahar names itself.

        The upload half already packed them (a ``title-dir`` answer is what decides that),
        so a restore that renamed the zip beside the tree would have been the asymmetry
        this rule exists to prevent: a save the plugin can send and cannot put back.
        Measured shape on the reference Deck:
        ``<id0>/<id1>/title/00040000/000ec300/data``.
        """
        assert restores_by_extraction("3ds") is True
        assert restores_by_extraction("n3ds") is True

    @pytest.mark.parametrize(
        "platform",
        ["gba", "snes", "genesis", "n64", "psx", "ps2", "wii", "wiiu", "dreamcast"],
    )
    def test_every_other_family_is_written_as_a_file(self, platform: str) -> None:
        """Only a flat member set restores by extraction; the rest keep their own rule."""
        assert restores_by_extraction(platform) is False

    def test_an_unknown_platform_is_not_a_member_set(self) -> None:
        """An unaudited system falls back to the libretro per-ROM file, as everywhere else."""
        assert restores_by_extraction("some-new-core") is False
