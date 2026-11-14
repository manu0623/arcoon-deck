"""The write: one setting replaced in an emulator's own file, nothing else moved.

The settings file is DuckStation's real shape — sections, keys in a meaningful order,
values whose spelling matters — because the whole point of the rewrite is that the rest
of it survives unchanged.
"""

from __future__ import annotations

import logging

from adapters.emulator_bios_home import EmulatorBiosHomeAdapter, _rewrite
from domain.emulator_bios_home import BiosHome

MEASURED = """[BIOS]
PatchFastBoot = false
PatchTTYEnable = false
SearchDirectory = /run/media/deck/SR01T/Emulation/bios

[Console]
Enable8MBRAM = false
"""


def test_the_value_is_replaced_and_every_other_line_survives() -> None:
    rewritten = _rewrite(MEASURED, section="BIOS", key="SearchDirectory", value="/home/deck/bios/psx")

    assert "SearchDirectory = /home/deck/bios/psx" in rewritten
    assert "/run/media" not in rewritten
    assert "PatchFastBoot = false" in rewritten
    assert "[Console]\nEnable8MBRAM = false" in rewritten


def test_an_absent_key_is_added_to_its_section() -> None:
    text = "[BIOS]\nPatchFastBoot = false\n\n[Console]\nEnable8MBRAM = false\n"

    rewritten = _rewrite(text, section="BIOS", key="SearchDirectory", value="/home/deck/bios/psx")

    assert rewritten == (
        "[BIOS]\nPatchFastBoot = false\nSearchDirectory = /home/deck/bios/psx\n\n[Console]\nEnable8MBRAM = false\n"
    )


def test_an_absent_section_is_added_at_the_end() -> None:
    text = "[Console]\nEnable8MBRAM = false\n"

    rewritten = _rewrite(text, section="BIOS", key="SearchDirectory", value="/home/deck/bios/psx")

    assert rewritten == "[Console]\nEnable8MBRAM = false\n\n[BIOS]\nSearchDirectory = /home/deck/bios/psx\n"


def test_a_same_named_key_in_another_section_is_not_touched() -> None:
    text = "[Other]\nSearchDirectory = /somewhere\n\n[BIOS]\nSearchDirectory = /run/media/deck/Emulation/bios\n"

    rewritten = _rewrite(text, section="BIOS", key="SearchDirectory", value="/home/deck/bios/psx")

    assert "[Other]\nSearchDirectory = /somewhere" in rewritten
    assert "[BIOS]\nSearchDirectory = /home/deck/bios/psx" in rewritten


def _adapter(**overrides: object) -> EmulatorBiosHomeAdapter:
    arguments: dict[str, object] = {"logger": logging.getLogger("test")}
    arguments.update(overrides)
    return EmulatorBiosHomeAdapter(**arguments)  # type: ignore[arg-type]


def _plan(config_path: str = "/home/deck/.local/share/duckstation/settings.ini") -> BiosHome:
    return BiosHome(
        emulator="duckstation",
        config_path=config_path,
        section="BIOS",
        key="SearchDirectory",
        directory="/home/deck/.local/share/romm-tender/bios/psx",
    )


class _Files:
    """A settings file and a BIOS folder, as the adapter asks about them."""

    def __init__(self, *, text: str | None = MEASURED, bios_entries: list[str] | None = None) -> None:
        self.text = text
        self.written: list[str] = []
        self.bios_entries = ["scph5501.bin"] if bios_entries is None else bios_entries

    def isdir(self, path: str) -> bool:
        return not path.endswith("missing")

    def listdir(self, path: str) -> list[str]:
        return list(self.bios_entries)

    def exists(self, path: str) -> bool:
        return self.text is not None

    def read_text(self, path: str) -> str:
        assert self.text is not None
        return self.text

    def write_text(self, path: str, text: str) -> None:
        self.written.append(text)
        self.text = text


def test_a_pointed_emulator_has_the_folder_written_and_reports_it() -> None:
    files = _Files()

    outcome = _adapter(
        isdir=files.isdir,
        listdir=files.listdir,
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
    ).point(_plan())

    assert outcome.status == "pointed"
    assert outcome.changed is True
    assert files.written and "SearchDirectory = /home/deck/.local/share/romm-tender/bios/psx" in files.written[0]


def test_an_emulator_already_pointing_at_the_folder_is_not_rewritten() -> None:
    files = _Files(text="[BIOS]\nSearchDirectory = /home/deck/.local/share/romm-tender/bios/psx\n")

    outcome = _adapter(
        isdir=files.isdir,
        listdir=files.listdir,
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
    ).point(_plan())

    assert outcome.status == "already"
    assert files.written == []


def test_a_plugin_folder_holding_nothing_leaves_the_emulator_alone() -> None:
    files = _Files(bios_entries=[])

    outcome = _adapter(
        isdir=files.isdir,
        listdir=files.listdir,
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
    ).point(_plan())

    assert outcome.status == "no-bios"
    assert outcome.note == "directory-empty"
    assert files.written == []


def test_a_missing_plugin_folder_leaves_the_emulator_alone() -> None:
    plan = _plan()
    missing = BiosHome(
        emulator=plan.emulator,
        config_path=plan.config_path,
        section=plan.section,
        key=plan.key,
        directory="/home/deck/.local/share/romm-tender/bios/missing",
    )
    files = _Files()

    outcome = _adapter(
        isdir=files.isdir,
        listdir=files.listdir,
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
    ).point(missing)

    assert outcome.status == "no-bios"
    assert outcome.note == "directory-missing"


def test_an_emulator_with_no_settings_file_is_not_given_one() -> None:
    files = _Files(text=None)

    outcome = _adapter(
        isdir=files.isdir,
        listdir=files.listdir,
        exists=files.exists,
        read_text=files.read_text,
        write_text=files.write_text,
    ).point(_plan())

    assert outcome.status == "no-config"
    assert files.written == []


def test_an_unwritable_settings_file_fails_with_its_reason() -> None:
    files = _Files()

    def refuse(path: str, text: str) -> None:
        raise OSError("read-only file system")

    outcome = _adapter(
        isdir=files.isdir, listdir=files.listdir, exists=files.exists, read_text=files.read_text, write_text=refuse
    ).point(_plan())

    assert outcome.status == "failed"
    assert outcome.note is not None and "read-only file system" in outcome.note
