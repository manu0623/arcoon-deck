"""Tests for domain.artwork_paths — pure cover-art filename builders."""

from __future__ import annotations

import pytest

from domain.artwork_paths import (
    SHORTCUT_APP_ID_MAX,
    SHORTCUT_APP_ID_MIN,
    asset_grid_filenames,
    final_filename,
    grid_image_filenames,
    is_shortcut_app_id,
    parse_grid_image_app_id,
    staging_filename,
)


class TestStagingFilename:
    def test_int_rom_id(self):
        assert staging_filename(42) == "romm_42_cover.png"

    def test_str_rom_id(self):
        assert staging_filename("42") == "romm_42_cover.png"

    def test_zero(self):
        assert staging_filename(0) == "romm_0_cover.png"

    def test_large_id(self):
        assert staging_filename(999_999_999) == "romm_999999999_cover.png"


class TestFinalFilename:
    def test_app_id(self):
        assert final_filename(100001) == "100001p.png"

    def test_str_id(self):
        assert final_filename("12345") == "12345p.png"

    def test_zero(self):
        assert final_filename(0) == "0p.png"


class TestIsShortcutAppId:
    """The high-bit-set uint32 range check — the cleanup's first safety gate."""

    def test_store_app_id_rejected(self):
        # A regular Steam game's appId (user custom art) is never a candidate.
        assert is_shortcut_app_id(570) is False

    def test_zero_rejected(self):
        assert is_shortcut_app_id(0) is False

    def test_negative_rejected(self):
        # The signed-int32 form shortcuts.vdf records is out of range here —
        # candidates are parsed from unsigned filename digits only.
        assert is_shortcut_app_id(-1294967296) is False

    def test_below_lower_boundary_rejected(self):
        assert is_shortcut_app_id(SHORTCUT_APP_ID_MIN - 1) is False

    def test_lower_boundary_accepted(self):
        assert is_shortcut_app_id(SHORTCUT_APP_ID_MIN) is True
        assert SHORTCUT_APP_ID_MIN == 0x8000_0000

    def test_mid_range_accepted(self):
        # A realistic Steam-assigned shortcut appId (uniform in the range).
        assert is_shortcut_app_id(3000000000) is True

    def test_upper_boundary_accepted(self):
        assert is_shortcut_app_id(SHORTCUT_APP_ID_MAX) is True
        assert SHORTCUT_APP_ID_MAX == 0xFFFF_FFFF

    def test_above_upper_boundary_rejected(self):
        # Beyond uint32 — cannot be a Steam appId.
        assert is_shortcut_app_id(SHORTCUT_APP_ID_MAX + 1) is False


class TestParseGridImageAppId:
    """Strict grid-image filename parse — non-matches must return None."""

    @pytest.mark.parametrize("suffix", ["p", "_hero", "_logo", "_icon", ""])
    @pytest.mark.parametrize("ext", ["png", "jpg", "jpeg"])
    def test_all_suffix_extension_forms_match(self, suffix, ext):
        assert parse_grid_image_app_id(f"2200000001{suffix}.{ext}") == 2200000001

    def test_store_app_id_still_parses(self):
        # The parse is range-agnostic — the range check is a separate gate.
        assert parse_grid_image_app_id("570p.png") == 570

    @pytest.mark.parametrize(
        "filename",
        [
            "123abc.png",  # trailing junk after the digits
            "abc123.png",  # leading junk before the digits
            "123p.gif",  # non-raster-set extension
            "123p.PNG",  # uppercase extension (Steam writes lowercase)
            "123_grid.png",  # not one of the five grid forms
            "123p.png.tmp",  # atomic-write sidecar
            "romm_42_cover.png",  # plugin staging file
            "123",  # no extension
            ".png",  # no digits
            "",  # empty
            "123 p.png",  # embedded space
        ],
    )
    def test_non_grid_image_names_rejected(self, filename):
        assert parse_grid_image_app_id(filename) is None


class TestGridImageFilenames:
    def test_full_suffix_extension_product(self):
        names = grid_image_filenames(2200000001)
        assert len(names) == 15
        assert set(names) == {
            f"2200000001{suffix}.{ext}"
            for suffix in ("p", "_hero", "_logo", "_icon", "")
            for ext in ("png", "jpg", "jpeg")
        }

    def test_every_generated_name_parses_back(self):
        for name in grid_image_filenames(3123456789):
            assert parse_grid_image_app_id(name) == 3123456789

    def test_str_app_id(self):
        assert "12345p.png" in grid_image_filenames("12345")


class TestAssetGridFilenames:
    """Which grid file means an SGDB asset type is already applied.

    The suffix set is measured: a live grid directory on a Deck holds ``_logo`` (2178 files),
    ``_hero`` (1927), portrait ``p`` (1098), bare wide ``.png`` (131) and ``_icon`` (104 png,
    26 ico) and nothing else of that shape.
    """

    def test_hero_is_its_own_suffix(self):
        assert asset_grid_filenames("hero", 7) == ("7_hero.png", "7_hero.jpg", "7_hero.jpeg")

    def test_logo_and_icon_are_their_own_suffixes(self):
        assert asset_grid_filenames("logo", 7)[0] == "7_logo.png"
        assert asset_grid_filenames("icon", 7)[0] == "7_icon.png"

    def test_grid_is_the_wide_form_only(self):
        assert asset_grid_filenames("grid", 7) == ("7.png", "7.jpg", "7.jpeg")

    def test_cover_is_the_portrait_form_only(self):
        assert asset_grid_filenames("cover", 7) == ("7p.png", "7p.jpg", "7p.jpeg")

    def test_an_unknown_asset_type_has_nothing_to_check(self):
        assert asset_grid_filenames("banner", 7) == ()
