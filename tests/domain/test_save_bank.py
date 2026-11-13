"""Tests for py_modules/domain/save_bank.py — the Argosy-compatible save bank."""

from __future__ import annotations

import os

import pytest

from domain.save_bank import (
    SAVE_BANK_DIR_NAME,
    ArchiveRootMatch,
    SaveFamily,
    SaveUnit,
    SaveUsage,
    base_application_id,
    canonical_platform,
    describe_unit,
    dreamcast_vmu_stem,
    gci_filename,
    is_formatted_ps2_superblock,
    layout_for,
    match_archive_root,
    matches_name,
    ps2_card_superblock,
    ps2_name_matches,
    ps2_stem,
    restores_by_extraction,
    save_bank_base,
    save_bank_root,
)

BANK = os.path.join(os.sep, "data", "romm-tender", SAVE_BANK_DIR_NAME)


def unit(platform: str, **kwargs: object) -> SaveUnit:
    """Describe a platform's save unit against this bank."""
    return describe_unit(layout_for(platform), bank_root=BANK, **kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Bank root and layout table
# ---------------------------------------------------------------------------


class TestBankLayout:
    def test_bank_root_is_a_plain_subdirectory_of_the_data_dir(self) -> None:
        assert save_bank_root(os.path.join(os.sep, "data", "romm-tender")) == BANK

    def test_unknown_platform_falls_back_to_the_libretro_per_rom_file(self) -> None:
        layout = layout_for("gba")
        assert layout.family == SaveFamily.LIBRETRO_FILE
        assert layout.usage == SaveUsage.FILE_EXACT
        assert save_bank_base(BANK, "gba") == os.path.join(BANK, "gba")

    def test_platform_aliases_share_one_folder(self) -> None:
        assert canonical_platform("3ds") == canonical_platform("n3ds") == "n3ds"
        assert canonical_platform("GameCube") == "gc"
        assert canonical_platform("ngc") == "gc"
        assert canonical_platform("psvita") == "vita"
        assert save_bank_base(BANK, "3ds") == save_bank_base(BANK, "n3ds")

    @pytest.mark.parametrize(
        ("platform", "usage"),
        [
            ("vita", SaveUsage.FOLDER_EXACT),
            ("psp", SaveUsage.FOLDER_PREFIX),
            ("ps3", SaveUsage.FOLDER_PREFIX),
            ("ps2", SaveUsage.FOLDER_PREFIX),
            ("n3ds", SaveUsage.FOLDER_SPLIT),
            ("wii", SaveUsage.FOLDER_SPLIT),
            ("wiiu", SaveUsage.FOLDER_SPLIT),
            ("switch", SaveUsage.FOLDER_EXACT),
            ("gc", SaveUsage.FILE_PREFIX),
            ("dreamcast", SaveUsage.FILE_EXACT),
            ("gba", SaveUsage.FILE_EXACT),
        ],
    )
    def test_usages_match_argosy(self, platform: str, usage: SaveUsage) -> None:
        """The five usages are the contract between sigil's id and a path."""
        assert layout_for(platform).usage == usage


# ---------------------------------------------------------------------------
# Libretro per-ROM file
# ---------------------------------------------------------------------------


class TestLibretroFile:
    def test_member_is_the_rom_stem_with_the_core_extension(self) -> None:
        result = unit("gba", rom_stem="Pokemon - Emerald Version (USA, Europe)")
        assert result.paths == (os.path.join(BANK, "gba", "Pokemon - Emerald Version (USA, Europe).srm"),)
        assert result.archive_roots == ("Pokemon - Emerald Version (USA, Europe).srm",)
        assert result.place_path == result.paths[0]
        assert result.identified is True
        assert result.usable is True

    def test_no_rom_stem_is_a_refusal_not_a_guess(self) -> None:
        result = unit("gba", rom_stem=None)
        assert result.members == ()
        assert result.needs == ("rom_stem",)
        assert result.usable is False

    def test_membership_predicate_accepts_sidecars_for_the_same_stem(self) -> None:
        layout = layout_for("gb")
        assert matches_name(layout, "Tetris.srm", rom_stem="Tetris") is True
        assert matches_name(layout, "Tetris.rtc", rom_stem="Tetris") is True
        assert matches_name(layout, "Tetris DX.srm", rom_stem="Tetris") is False
        assert matches_name(layout, "Tetris.srm", rom_stem=None) is False


# ---------------------------------------------------------------------------
# Vita: one folder named for the id
# ---------------------------------------------------------------------------


class TestExactFolder:
    def test_folder_is_named_exactly_for_the_save_id(self) -> None:
        result = unit("vita", save_id="PCSE00023")
        assert result.paths == (os.path.join(BANK, "vita", "PCSE00023"),)
        assert result.place_path == result.paths[0]

    def test_membership_is_case_insensitive_equality(self) -> None:
        layout = layout_for("vita")
        assert matches_name(layout, "pcse00023", "PCSE00023") is True
        assert matches_name(layout, "PCSE00023AUTOSAVE", "PCSE00023") is False

    def test_no_save_id_refuses(self) -> None:
        assert unit("vita", save_id=None).needs == ("save_id",)


# ---------------------------------------------------------------------------
# PSP / PS3: several siblings sharing a prefix
# ---------------------------------------------------------------------------


class TestPrefixBundle:
    def test_unit_spans_every_sibling_sharing_the_prefix(self) -> None:
        """A PSP game writes DATA00 beside SETTINGS; one folder is not the save."""
        base = save_bank_base(BANK, "psp")
        tree = {base: ("ULUS10064DATA00", "ULUS10064SETTINGS", "ULJS00001DATA00")}
        result = unit("psp", save_id="ULUS10064", tree=tree)
        assert result.paths == (
            os.path.join(base, "ULUS10064DATA00"),
            os.path.join(base, "ULUS10064SETTINGS"),
        )
        assert result.archive_roots == ("ULUS10064DATA00", "ULUS10064SETTINGS")
        assert result.place_path == base, "a restore clears the siblings and unpacks back into the parent"

    def test_prefix_matching_is_case_insensitive(self) -> None:
        layout = layout_for("psp")
        assert matches_name(layout, "ulus10064data00", "ULUS10064") is True
        assert matches_name(layout, "ULUS10065DATA00", "ULUS10064") is False

    def test_ps3_uses_the_same_shape(self) -> None:
        base = save_bank_base(BANK, "ps3")
        tree = {base: ("BCUS99086GAMEDATA", "BCUS99086-AUTOSAVE")}
        result = unit("ps3", save_id="BCUS99086", tree=tree)
        assert len(result.members) == 2
        assert result.place_path == base

    def test_no_matches_is_an_empty_unit_with_a_usable_place(self) -> None:
        result = unit("psp", save_id="ULUS10064", tree={save_bank_base(BANK, "psp"): ()})
        assert result.members == ()
        assert result.place_path == save_bank_base(BANK, "psp")
        assert result.usable is False


# ---------------------------------------------------------------------------
# 3DS: data + extdata under a discovered id0/id1
# ---------------------------------------------------------------------------


def n3ds_tree(id0: str = "00000000000000000000000000000001", id1: str = "00000000000000000000000000000002"):
    """A 3DS SD tree with both save components present for title 00113200."""
    base = save_bank_base(BANK, "n3ds")
    title_root = os.path.join(base, id0, id1)
    data = os.path.join(title_root, "title", "00040000", "00113200", "data")
    extdata = os.path.join(title_root, "extdata", "00000000", "00001132")
    tree = {
        base: (id0,),
        os.path.join(base, id0): (id1,),
        data: ("00000001.sav",),
        extdata: ("user",),
    }
    return base, id0, id1, data, extdata, tree


class TestN3dsTitle:
    def test_both_components_are_the_save_unit(self) -> None:
        """The archive root is each member's path INSIDE the answer's directory.

        For a prefix bundle that is the folder's own name (``ULUS10064DATA00``); a 3DS
        title sits several levels lower, so its root spells those levels out. Naming it
        "data" alone made the packed unit look for ``<base>/data`` — measured on the
        reference Deck as a ``FileNotFoundError`` while packing a save that was right
        there — and would have restored a download outside the tree Azahar reads.
        """
        _, id0, id1, data, extdata, tree = n3ds_tree()
        result = unit("n3ds", save_id="00040000/00113200", tree=tree)
        assert result.paths == (data, extdata)
        assert result.archive_roots == (
            f"{id0}/{id1}/title/00040000/00113200/data",
            f"{id0}/{id1}/extdata/00000000/00001132",
        )
        assert result.identified is True, "the save id and the console's ids name the title"
        assert result.place_path == data

    def test_an_empty_title_folder_is_where_a_server_save_lands(self) -> None:
        """A 3DS game that has not saved yet is not unidentified: the id was read and the
        console's id0/id1 were discovered, so the download has a directory to unpack into.

        Measured on the reference Deck: with the local folder removed, the sync refused
        with ``save_shape_unsupported`` and the uploaded save could never come back.
        """
        base, id0, id1, data, _extdata, _tree = n3ds_tree()
        empty = {
            base: (id0,),
            os.path.join(base, id0): (id1,),
            os.path.join(base, id0, id1, "title"): ("00040000",),
            os.path.join(base, id0, id1, "title", "00040000"): ("00113200",),
            os.path.dirname(data): (),
        }

        result = unit("n3ds", save_id="00040000/00113200", tree=empty)

        assert result.members == ()
        assert result.identified is True
        assert result.place_path == data

    def test_extdata_id_is_the_low_half_shifted_right_eight_bits(self) -> None:
        """``00113200`` becomes ``00001132`` — the low half shifted right 8 bits."""
        _, _, _, _, extdata, tree = n3ds_tree()
        result = unit("n3ds", save_id="00040000/00113200", tree=tree)
        assert extdata in result.paths
        assert os.path.basename(extdata) == "00001132"

    def test_flat_id_still_resolves_to_the_retail_category(self) -> None:
        _, _, _, data, _, tree = n3ds_tree()
        assert unit("n3ds", save_id="0004000000113200", tree=tree).paths[0] == data
        assert unit("n3ds", save_id="00113200", tree=tree).paths[0] == data

    def test_extdata_only_title_is_still_a_save(self) -> None:
        """Fantasy Life keeps every byte of progress in extdata and never writes data."""
        _, _, _, data, extdata, tree = n3ds_tree()
        without_data = {path: names for path, names in tree.items() if path != data}
        result = unit("n3ds", save_id="00040000/00113200", tree=without_data)
        assert result.paths == (extdata,)
        assert result.place_path == extdata

    def test_no_title_tree_is_absent_not_an_estimate(self) -> None:
        result = unit("n3ds", save_id="00040000/00113200", tree={})
        assert result.needs == ("id0",)
        assert result.place_path is None

    def test_no_id0_yet_means_no_path_is_invented(self) -> None:
        base = save_bank_base(BANK, "n3ds")
        result = unit("n3ds", save_id="00040000/00113200", tree={base: ()})
        assert result.members == ()
        assert result.place_path is None

    def test_archive_roots_are_the_platforms_unidentified_roots(self) -> None:
        layout = layout_for("n3ds")
        assert match_archive_root(layout, "data", "00040000/00113200") is ArchiveRootMatch.UNIDENTIFIED
        assert match_archive_root(layout, "extdata", "00040000/00113200") is ArchiveRootMatch.UNIDENTIFIED


# ---------------------------------------------------------------------------
# Wii / Wii U: category split
# ---------------------------------------------------------------------------


class TestCategorySplit:
    def test_wii_uses_the_low_id_under_the_category_directory(self) -> None:
        result = unit("wii", save_id="00010000/524d4745")
        assert result.paths == (os.path.join(BANK, "wii", "title", "00010000", "524d4745"),)
        assert result.place_path == result.paths[0]

    def test_flat_and_bare_low_ids_resolve_to_the_same_folder(self) -> None:
        split = unit("wii", save_id="00010000/524d4745").paths
        flat = unit("wii", save_id="00010000524d4745").paths
        bare = unit("wii", save_id="524d4745").paths
        assert split == flat == bare

    def test_low_id_is_written_lowercase(self) -> None:
        result = unit("wiiu", save_id="00050000/1012BD00")
        assert os.path.basename(result.paths[0]) == "1012bd00"

    def test_another_category_resolves_beside_the_base(self) -> None:
        """A demo id under 00050002 is a sibling of the 00050000 base, never nested in it."""
        result = unit("wiiu", save_id="00050002/1012bd00")
        assert result.paths == (os.path.join(BANK, "wiiu", "mlc01", "usr", "save", "00050002", "1012bd00"),)
        assert "00050000" not in result.paths[0]

    def test_wii_never_joins_the_category_twice(self) -> None:
        joined = os.path.join(BANK, "wii", "title", "00010000", "00010000", "524d4745")
        assert unit("wii", save_id="00010000/524d4745").paths[0] != joined


# ---------------------------------------------------------------------------
# PS2: folder memory cards
# ---------------------------------------------------------------------------


def ps2_tree(cards: tuple[str, ...] = ("Card A.ps2",), entries: tuple[str, ...] = ()):
    """A PS2 base holding the named cards, each with the same entries."""
    base = save_bank_base(BANK, "ps2")
    tree: dict[str, tuple[str, ...]] = {base: cards}
    for card in cards:
        tree[os.path.join(base, card)] = (*entries, "_pcsx2_superblock")
    return base, tree


class TestPs2Card:
    def test_region_prefix_is_derived_from_the_serial(self) -> None:
        assert ps2_stem("SLUS20565") == "BASLUS20565"
        assert ps2_stem("SLES55555") == "BESLES55555"
        assert ps2_stem("SLPS25000") == "BISLPS25000"
        assert ps2_stem("SLKA00123") == "BISLKA00123"
        assert ps2_stem("BASLUS20565") == "BASLUS20565"

    def test_matching_ignores_punctuation_and_case(self) -> None:
        assert ps2_name_matches("BASLUS-20565AC04", "BASLUS-20565") is True
        assert ps2_name_matches("baslus20565sys", "BASLUS-20565") is True
        assert ps2_name_matches("BASLUS-20152AC04", "BASLUS-20565") is False

    def test_a_wrong_region_prefix_still_identifies_the_disc(self) -> None:
        assert ps2_name_matches("BASLUS-20565AC04", "BESLUS20565") is True

    def test_unit_bundles_only_this_games_folders(self) -> None:
        base, tree = ps2_tree(entries=("BASLUS-20565AC04", "BASLUS-20565SYS", "BASLUS-99999AC04"))
        result = unit("ps2", save_id="SLUS-20565", tree=tree)
        card = os.path.join(base, "Card A.ps2")
        assert result.paths == (
            os.path.join(card, "BASLUS-20565AC04"),
            os.path.join(card, "BASLUS-20565SYS"),
        )
        assert result.place_path == card, "a restore lands in the card, never in one game folder"
        assert result.container == "ps2_folder_card"

    def test_two_cards_holding_the_game_is_a_refusal(self) -> None:
        """Picking one would overwrite the other card's save."""
        base, tree = ps2_tree(cards=("Card A.ps2", "Card B.ps2"), entries=("BASLUS-20565AC04",))
        result = unit("ps2", save_id="SLUS-20565", tree=tree)
        assert result.members == ()
        assert result.conflicts == (os.path.join(base, "Card A.ps2"), os.path.join(base, "Card B.ps2"))
        assert result.needs == ("preferred_card",)
        assert result.usable is False

    def test_a_missing_card_is_constructed_as_the_shared_card(self) -> None:
        base, tree = ps2_tree(cards=())
        result = unit("ps2", save_id="SLUS-20565", tree=tree)
        assert result.place_path == os.path.join(base, "Shared.ps2")
        assert result.members == ()

    def test_cards_one_level_below_are_found_as_armsx2_writes_them(self) -> None:
        base = save_bank_base(BANK, "ps2")
        card = os.path.join(base, "memcards", "MemCard1")
        tree = {
            base: ("memcards",),
            os.path.join(base, "memcards"): ("MemCard1",),
            card: ("BASLUS-20565AC04", "_pcsx2_superblock"),
        }
        result = unit("ps2", save_id="SLUS-20565", tree=tree)
        assert result.paths == (os.path.join(card, "BASLUS-20565AC04"),)
        assert result.conflicts == ()

    def test_card_rooted_archive_matches_by_a_folder_inside_it(self) -> None:
        layout = layout_for("ps2")
        assert match_archive_root(layout, "Card A", "SLUS-20565") is None
        assert match_archive_root(layout, "BASLUS-20565AC04", "SLUS-20565") is ArchiveRootMatch.PREFIX


class TestPs2Superblock:
    def test_a_formatted_superblock_is_recognised(self) -> None:
        payload = ps2_card_superblock()
        assert len(payload) == 0x2000
        assert payload[0x16] == 0x6F
        assert is_formatted_ps2_superblock(payload) is True

    def test_empty_short_and_blank_cards_are_not_formatted(self) -> None:
        assert is_formatted_ps2_superblock(None) is False
        assert is_formatted_ps2_superblock(b"") is False
        assert is_formatted_ps2_superblock(b"\x00" * 0x2000) is False
        assert is_formatted_ps2_superblock(b"\xff" * 0x100) is False

    def test_layout_constants_match_pcsx2(self) -> None:
        payload = ps2_card_superblock()
        assert payload.startswith(b"Sony PS2 Memory Card Format ")
        assert b"1.2.0.0" in payload[28:40]
        assert payload[336] == 2  # PS2 card type


# ---------------------------------------------------------------------------
# Switch: discovered user and profile
# ---------------------------------------------------------------------------


class TestSwitchTitle:
    USER = "0100000000000001"
    PROFILE = "0100000000000002"

    def switch_tree(self):
        base = save_bank_base(BANK, "switch")
        return base, {base: (self.USER,), os.path.join(base, self.USER): (self.PROFILE,)}

    def test_title_id_is_nested_under_the_discovered_profile(self) -> None:
        base, tree = self.switch_tree()
        result = unit("switch", save_id="0100152000022000", tree=tree)
        assert result.paths == (os.path.join(base, self.USER, self.PROFILE, "0100152000022000"),)

    def test_patch_id_maps_back_to_the_application_id(self) -> None:
        assert base_application_id("0100152000022800") == "0100152000022000"

    def test_add_on_content_id_maps_back_when_the_application_is_known(self) -> None:
        assert base_application_id("0100152000023000", known_applications=("0100152000022000",)) == "0100152000022000"

    def test_unknown_add_on_id_is_left_alone(self) -> None:
        """Its form collides with ordinary ids, so a guess would move the save."""
        assert base_application_id("0100152000023000") == "0100152000023000"

    def test_application_id_is_unchanged(self) -> None:
        assert base_application_id("0100152000022000") == "0100152000022000"

    def test_non_title_id_is_refused(self) -> None:
        assert base_application_id("not-a-title") is None
        assert base_application_id("0200152000022000") is None

    def test_no_profile_means_no_path_rather_than_a_guess(self) -> None:
        base, _ = self.switch_tree()
        result = unit("switch", save_id="0100152000022000", tree={base: ()})
        assert result.place_path is None
        assert result.needs == ("profile",)


# ---------------------------------------------------------------------------
# Dreamcast: VMU card named after the disc
# ---------------------------------------------------------------------------


class TestDreamcastVmu:
    def test_port_a1_card_is_named_after_the_product_number(self) -> None:
        result = unit("dreamcast", save_id="T13301N")
        assert result.paths == (os.path.join(BANK, "dreamcast", "T13301N.A1.bin"),)

    def test_reserved_characters_are_underscored_as_flycast_does(self) -> None:
        assert dreamcast_vmu_stem(" T1/33:01|N ") == "T1_33_01_N"
        assert dreamcast_vmu_stem("T13301N") == "T13301N"

    def test_membership_matches_the_built_name(self) -> None:
        layout = layout_for("dreamcast")
        assert matches_name(layout, "t13301n.a1.bin", "T13301N") is True
        assert matches_name(layout, "vmu_save_A1.bin", "T13301N") is False


# ---------------------------------------------------------------------------
# GameCube: the whole .gci set
# ---------------------------------------------------------------------------


class TestGciSet:
    def test_header_matched_members_are_the_unit(self) -> None:
        names = ("GZLE01-GZLE01-FZero.gci", "GZLE01-GZLE01-FZero2.gci")
        result = unit("gc", save_id="GZLE01", header_matched=names)
        assert [os.path.basename(path) for path in result.paths] == list(names)
        assert result.place_path == save_bank_base(BANK, "gc")

    def test_name_fallback_without_headers(self) -> None:
        base = save_bank_base(BANK, "gc")
        tree = {base: ("GZLE-FZero.gci", "GALE-Other.gci")}
        result = unit("gc", save_id="GZLE", tree=tree)
        assert [os.path.basename(path) for path in result.paths] == ["GZLE-FZero.gci"]

    def test_gci_name_is_built_from_the_header_fields(self) -> None:
        assert gci_filename("GZLE", "GZLE01", "F-Zero GX") == "GZLE-GZLE01-F-Zero GX.gci"
        assert gci_filename("GZLE", "GZLE01", "../escape") == "GZLE-GZLE01-.._escape.gci"


# ---------------------------------------------------------------------------
# Archive root matching
# ---------------------------------------------------------------------------


class TestArchiveRootMatching:
    def test_exact_prefix_contains_and_none_tiers(self) -> None:
        layout = layout_for("psp")
        assert match_archive_root(layout, "ULUS10064DATA00", "ULUS10064") is ArchiveRootMatch.PREFIX
        assert match_archive_root(layout, "ULUS10064", "ULUS10064") is ArchiveRootMatch.EXACT
        assert match_archive_root(layout, "other/ULUS10064", "ULUS10064") is ArchiveRootMatch.CONTAINS

    def test_an_unrelated_root_matches_nothing(self) -> None:
        assert match_archive_root(layout_for("psp"), "ULJS00001DATA00", "ULUS10064") is None
        assert match_archive_root(layout_for("psp"), "", "ULUS10064") is None
        assert match_archive_root(layout_for("psp"), "ULUS10064", None) is None


class TestRestoresByExtraction:
    """Which families put a downloaded archive back by unpacking it."""

    def test_a_wii_title_restores_by_extraction(self) -> None:
        """Measured: the zip landed in the staging folder beside the title, unextracted."""
        assert restores_by_extraction("wii") is True

    def test_a_ps2_card_restores_by_extraction(self) -> None:
        # The unit is the game's folder inside the card; dropping the zip beside the
        # card leaves PCSX2 reading a card without that save.
        assert restores_by_extraction("ps2") is True

    def test_a_plain_rom_file_platform_does_not(self) -> None:
        assert restores_by_extraction("snes") is False
