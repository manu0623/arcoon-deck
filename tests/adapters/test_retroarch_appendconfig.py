"""Writing the appendconfig: current, idempotent, and never fatal.

The idempotence assertions read the file's mtime rather than counting writes, because
the property that matters is "a launch that changed nothing did not touch the file" —
a second ROM launching concurrently reads it.
"""

from __future__ import annotations

import logging
from pathlib import Path

from adapters.retroarch_appendconfig import APPENDCONFIG_DIR_NAME, RetroArchAppendConfigAdapter


def _adapter(tmp_path: Path) -> RetroArchAppendConfigAdapter:
    return RetroArchAppendConfigAdapter(data_dir=str(tmp_path), logger=logging.getLogger("test"))


class TestWriting:
    def test_writes_one_file_per_platform(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba")
        assert path is not None
        assert path == str(tmp_path / APPENDCONFIG_DIR_NAME / "retroarch-gba.cfg")
        assert Path(path).is_file()

    def test_the_file_states_the_bank_directory(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba")
        assert path is not None
        text = Path(path).read_text(encoding="utf-8")
        # The tail is what identifies the platform; the prefix is the temp root, whose
        # separators and escaping differ per host and are not the point here.
        assert 'savefile_directory = "' in text
        assert 'saves/gba"' in text

    def test_a_second_platform_is_a_second_file(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        gba = adapter.ensure("gba")
        snes = adapter.ensure("snes")
        assert gba != snes
        assert snes is not None
        text = Path(snes).read_text(encoding="utf-8")
        assert "saves/snes" in text
        assert "saves/gba" not in text

    def test_a_system_directory_rides_along_when_resolved(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba", system_dir="/run/media/deck/SR01T/Emulation/bios")
        assert path is not None
        assert "system_directory" in Path(path).read_text(encoding="utf-8")

    def test_the_save_and_state_directories_are_created(self, tmp_path: Path) -> None:
        """RetroArch ignores a savefile_directory that is not on disk — silently."""
        adapter = _adapter(tmp_path)
        assert adapter.ensure("gba") is not None
        assert (tmp_path / "saves" / "gba").is_dir()
        assert (tmp_path / "states" / "gba").is_dir()

    def test_directories_are_created_even_when_the_config_is_unchanged(self, tmp_path: Path) -> None:
        """A deleted bank directory must be restored on the next launch, not ignored."""
        adapter = _adapter(tmp_path)
        assert adapter.ensure("gba") is not None
        (tmp_path / "saves" / "gba").rmdir()
        adapter.ensure("gba")
        assert (tmp_path / "saves" / "gba").is_dir()

    def test_an_alias_platform_uses_the_banks_own_name(self, tmp_path: Path) -> None:
        """``psx`` and ``ps1`` must not produce two files for one system."""
        adapter = _adapter(tmp_path)
        assert adapter.ensure("psx") == adapter.ensure("ps1")


class TestIdempotence:
    def test_an_unchanged_config_is_not_rewritten(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba")
        assert path is not None
        first = Path(path).stat().st_mtime_ns
        adapter.ensure("gba")
        assert Path(path).stat().st_mtime_ns == first

    def test_a_changed_intent_rewrites(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba")
        assert path is not None
        Path(path).write_text("# stale\n", encoding="utf-8")
        adapter.ensure("gba")
        assert "savefile_directory" in Path(path).read_text(encoding="utf-8")

    def test_an_unreadable_file_is_repaired(self, tmp_path: Path) -> None:
        adapter = _adapter(tmp_path)
        path = adapter.ensure("gba")
        assert path is not None
        Path(path).write_bytes(b"\xff\xfe\x00broken")
        adapter.ensure("gba")
        assert "savefile_directory" in Path(path).read_text(encoding="utf-8")


class TestFailureIsNotFatal:
    def test_an_unwritable_data_directory_returns_none(self, tmp_path: Path, caplog) -> None:
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("", encoding="utf-8")
        adapter = RetroArchAppendConfigAdapter(data_dir=str(blocker), logger=logging.getLogger("test"))
        with caplog.at_level(logging.WARNING):
            assert adapter.ensure("gba") is None
        assert "appendconfig" in caplog.text

    def test_a_save_path_that_cannot_be_a_directory_returns_none(self, tmp_path: Path, caplog) -> None:
        """Better no redirect than one RetroArch will ignore."""
        (tmp_path / "saves").write_text("", encoding="utf-8")
        adapter = _adapter(tmp_path)
        with caplog.at_level(logging.WARNING):
            assert adapter.ensure("gba") is None
        assert "appendconfig" in caplog.text

    def test_the_path_is_still_reportable_when_generation_fails(self, tmp_path: Path) -> None:
        """A caller logs where it *would* have written; the path does not depend on success."""
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("", encoding="utf-8")
        adapter = RetroArchAppendConfigAdapter(data_dir=str(blocker), logger=logging.getLogger("test"))
        assert adapter.ensure("gba") is None
        assert adapter.path_for("gba").endswith("retroarch-gba.cfg")


class TestTheSaveBankSwitch:
    """The redirect is one half of a switch; off must mean "nothing written"."""

    def test_disabled_writes_nothing_at_all(self, tmp_path: Path) -> None:
        # With the bank off, the lookup reads the RetroArch directory. Writing a config
        # that redirects elsewhere would move saves out from under it.
        adapter = RetroArchAppendConfigAdapter(
            data_dir=str(tmp_path), logger=logging.getLogger("test"), enabled=lambda: False
        )

        assert adapter.ensure("gba") is None
        assert not (tmp_path / APPENDCONFIG_DIR_NAME).exists()
        assert not (tmp_path / "saves").exists()

    def test_enabled_writes_the_config(self, tmp_path: Path) -> None:
        adapter = RetroArchAppendConfigAdapter(
            data_dir=str(tmp_path), logger=logging.getLogger("test"), enabled=lambda: True
        )

        assert adapter.ensure("gba") is not None
        assert (tmp_path / "saves" / "gba").is_dir()

    def test_the_switch_is_read_per_bake(self, tmp_path: Path) -> None:
        state = {"on": False}
        adapter = RetroArchAppendConfigAdapter(
            data_dir=str(tmp_path), logger=logging.getLogger("test"), enabled=lambda: state["on"]
        )

        assert adapter.ensure("gba") is None
        state["on"] = True
        assert adapter.ensure("gba") is not None
