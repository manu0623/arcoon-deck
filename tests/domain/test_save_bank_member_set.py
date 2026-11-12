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

    @pytest.mark.parametrize(
        "platform",
        ["gba", "snes", "genesis", "n64", "psx", "ps2", "psp", "ps3", "n3ds", "switch", "wii", "wiiu", "dreamcast"],
    )
    def test_every_other_family_is_written_as_a_file(self, platform: str) -> None:
        """Only a flat member set restores by extraction; the rest keep their own rule."""
        assert restores_by_extraction(platform) is False

    def test_an_unknown_platform_is_not_a_member_set(self) -> None:
        """An unaudited system falls back to the libretro per-ROM file, as everywhere else."""
        assert restores_by_extraction("some-new-core") is False
