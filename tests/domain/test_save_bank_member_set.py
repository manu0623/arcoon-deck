"""Which saves are restored by extraction rather than written as a file.

Measured failure this rule exists for: RomM held a GameCube save as one zip whose
member was ``01-GZ2E-gczelda2.gci``; the plugin renamed that zip into
``~/retrodeck/saves/gc/`` and Dolphin, in GCI-Folder mode, read
``User/GC/USA/Card A/`` — found it empty and offered a new card. The save was on
disk the whole time, in a form nothing opens.
"""

from __future__ import annotations

import pytest

from domain.save_bank import place_archive_members, restores_by_extraction


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
        ["gba", "snes", "genesis", "n64", "psx", "dreamcast"],
    )
    def test_every_other_family_is_written_as_a_file(self, platform: str) -> None:
        """Only a flat member set restores by extraction; the rest keep their own rule."""
        assert restores_by_extraction(platform) is False

    @pytest.mark.parametrize("platform", ["ps2", "wii", "wiiu"])
    def test_a_category_split_title_restores_by_extraction(self, platform: str) -> None:
        """The unit is the files inside a title folder, and RomM carries them as one zip.

        Measured for Wii on the reference Deck: the download landed the archive in the
        staging folder beside the title and nothing was extracted, so a save that had just
        been uploaded never came back. Wii U shares the family rule and therefore the
        restore, but its own tree has not been measured — which is why its save answer still
        refuses without a provisioned entry.
        """
        assert restores_by_extraction(platform) is True

    def test_an_unknown_platform_is_not_a_member_set(self) -> None:
        """An unaudited system falls back to the libretro per-ROM file, as everywhere else."""
        assert restores_by_extraction("some-new-core") is False


class TestPlaceArchiveMembers:
    """An archive can arrive packed above the folder the save belongs in (ADR-0066).

    Measured on the reference Deck: a Switch save uploaded elsewhere carried members named
    ``01006BB00C6F0000/savedata1.bin``, the restore extracted them into the title folder as
    they were, and Eden read ``<title>/`` — empty — while the save sat at
    ``<title>/01006BB00C6F0000/savedata1.bin``. The game started a new one. Wii has the same
    shape one level higher: RomM holds rom 6938's save with members ``534d4e45/data/wiimj2d.sav``
    and ``534d4e45/content/title.tmd``, and the folder Dolphin reads is ``<title>/data``.
    """

    _SWITCH_TITLE = "/nand/user/save/0000000000000000/93543B1D30E2AEB87D0F28AE30D83730/01006BB00C6F0000"
    _WII_SAVE = "/Wii/title/00010000/534d4e45/data"

    def test_members_named_after_the_folder_are_read_relative_to_it(self) -> None:
        plan = place_archive_members(
            ("01006BB00C6F0000/savedata1.bin", "01006BB00C6F0000/screenshot0.bin"),
            self._SWITCH_TITLE,
        )
        assert plan is not None
        assert plan.placements == (
            ("01006BB00C6F0000/savedata1.bin", "savedata1.bin"),
            ("01006BB00C6F0000/screenshot0.bin", "screenshot0.bin"),
        )
        assert plan.refused == ()

    def test_a_title_folder_archive_places_only_the_saves_own_subtree(self) -> None:
        """The heading names the destination's parent, and ``content/`` is not the save."""
        plan = place_archive_members(
            ("534d4e45/data/wiimj2d.sav", "534d4e45/content/title.tmd"),
            self._WII_SAVE,
        )
        assert plan is not None
        assert plan.placements == (("534d4e45/data/wiimj2d.sav", "wiimj2d.sav"),)
        assert plan.refused == ("534d4e45/content/title.tmd",)

    def test_a_flat_archive_is_left_alone(self) -> None:
        """The shape this plugin packs: the members ARE the folder's own, so nothing moves."""
        assert place_archive_members(("wiimj2d.sav", "banner.bin"), self._WII_SAVE) is None

    def test_a_heading_that_is_not_on_the_path_is_left_alone(self) -> None:
        """A PSP save folder sits INSIDE the destination, so nothing is aligned away."""
        assert place_archive_members(("ULUS10064DATA00/data.bin",), "/PSP/SAVEDATA") is None

    def test_mixed_headings_are_left_alone(self) -> None:
        """Two headings are not one archive packed above the destination — no alignment."""
        assert place_archive_members(("534d4e45/data/a.sav", "other/data/b.sav"), self._WII_SAVE) is None

    def test_a_sibling_whose_name_only_starts_the_same_is_not_the_heading(self) -> None:
        assert place_archive_members(("534d4e451/data/a.sav",), self._WII_SAVE) is None

    def test_a_lower_level_below_the_heading_is_kept(self) -> None:
        """A 3DS archive names the ids above the title, and the tree under it survives."""
        plan = place_archive_members(
            ("id0/id1/title/00040000/00033500/data/save.bin",),
            "/3ds/id0/id1",
        )
        assert plan is not None
        assert plan.placements == (
            ("id0/id1/title/00040000/00033500/data/save.bin", "title/00040000/00033500/data/save.bin"),
        )

    def test_nothing_placed_means_no_alignment(self) -> None:
        """An archive holding only files outside the save is read flat, never emptied."""
        assert place_archive_members(("534d4e45/content/title.tmd",), self._WII_SAVE) is None

    def test_no_members_is_not_an_alignment(self) -> None:
        assert place_archive_members((), self._WII_SAVE) is None
