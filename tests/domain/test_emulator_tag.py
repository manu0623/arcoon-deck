"""Unit tests for domain.emulator_tag — pure emulator tag construction functions."""

from __future__ import annotations

from domain.emulator_tag import (
    build_emulator_tag,
    detect_core_change,
    emulator_tag,
    normalize_emulator_identity,
)

# ---------------------------------------------------------------------------
# TestBuildEmulatorTag
# ---------------------------------------------------------------------------


class TestBuildEmulatorTag:
    def test_normal_core_strips_libretro_suffix(self):
        assert build_emulator_tag("mgba_libretro") == "retroarch-mgba"

    def test_core_with_digits_strips_libretro_suffix(self):
        assert build_emulator_tag("snes9x_libretro") == "retroarch-snes9x"

    def test_swanstation_core(self):
        assert build_emulator_tag("swanstation_libretro") == "retroarch-swanstation"

    def test_none_input_returns_fallback(self):
        assert build_emulator_tag(None) == "retroarch"

    def test_empty_string_returns_fallback(self):
        assert build_emulator_tag("") == "retroarch"

    def test_core_without_libretro_suffix_passes_through(self):
        # Shouldn't happen in practice but must not crash
        assert build_emulator_tag("mgba") == "retroarch-mgba"

    def test_uppercase_core_is_lowercased(self):
        assert build_emulator_tag("MGBA_libretro") == "retroarch-mgba"


# ---------------------------------------------------------------------------
# TestDetectCoreChange
# ---------------------------------------------------------------------------


class TestDetectCoreChange:
    def test_same_core_returns_false(self):
        assert detect_core_change("mgba_libretro", "mgba_libretro") is False

    def test_different_cores_returns_true(self):
        assert detect_core_change("mgba_libretro", "snes9x_libretro") is True

    def test_stored_none_returns_false(self):
        # First sync — no prior core recorded, can't determine change
        assert detect_core_change(None, "mgba_libretro") is False

    def test_active_none_returns_false(self):
        # Core unresolved — can't determine change
        assert detect_core_change("mgba_libretro", None) is False

    def test_both_none_returns_false(self):
        assert detect_core_change(None, None) is False


# ---------------------------------------------------------------------------
# TestEmulatorTag
# ---------------------------------------------------------------------------


class TestEmulatorTag:
    """Measured on the reference Deck's own server: a GameCube save written by Dolphin is
    filed under `dolphin`, a Switch save written by Eden under `eden` — and a Switch save
    this plugin uploaded was filed under `retroarch` on a device with no RetroArch Switch
    core at all."""

    def test_a_standalone_identity_is_the_tag(self) -> None:
        assert emulator_tag(None, identity="eden") == "eden"
        assert emulator_tag(None, identity="dolphin") == "dolphin"

    def test_a_picker_label_drops_its_provider(self) -> None:
        assert emulator_tag(None, identity="Dolphin (Standalone)") == "dolphin"
        assert emulator_tag(None, identity="Eden (Flatpak)") == "eden"

    def test_a_libretro_launch_keeps_the_core_in_the_tag(self) -> None:
        assert emulator_tag("mgba_libretro") == "retroarch-mgba"
        assert emulator_tag("mgba_libretro", identity=None) == "retroarch-mgba"

    def test_nothing_resolved_keeps_the_retroarch_fallback(self) -> None:
        assert emulator_tag(None) == "retroarch"
        assert emulator_tag(None, identity="") == "retroarch"

    def test_an_identity_that_names_nothing_is_not_a_tag(self) -> None:
        assert normalize_emulator_identity("(Standalone)") is None
        assert normalize_emulator_identity(None) is None
        assert emulator_tag(None, identity="(Standalone)") == "retroarch"

    def test_a_multi_word_identity_is_hyphenated(self) -> None:
        assert emulator_tag(None, identity="DuckStation (Standalone)") == "duckstation"
        assert emulator_tag(None, identity="melonDS (Flatpak)") == "melonds"
        assert emulator_tag(None, identity="PCSX2 v2 (Standalone)") == "pcsx2-v2"
