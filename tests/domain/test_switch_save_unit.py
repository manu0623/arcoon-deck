"""Switch's save unit: the title id read from the ROM, and the folder the manifest states.

Measured on the reference Deck (2026-11-12): Eden keeps a title's save at
``<nand>/user/save/<user>/<slot>/<title id>/``, RomM holds it as a zip of that folder, and
the id is named by the ``.tik`` entry inside the ``.nsp``. These tests pin the three steps
that turn those facts into a syncable answer: the id read, the manifest entry that states
the unit, and the members named from the directory the entry points at.
"""

from __future__ import annotations

import struct

from domain.content_identity import ContentIdentity, IdentityKind, save_id_text
from domain.layout_manifest import ManagedPlatform, parse_layout_manifest
from domain.save_answer import (
    SAVE_STATE_HOLE,
    SAVE_STATE_PER_GAME_FILES,
    SAVE_STATE_UNESTABLISHED,
    UNESTABLISHED_DIRECTORY_KNOWN,
    fill_directory_members,
    fill_save_id,
    manifest_answer,
)
from domain.save_bank import restores_by_extraction
from domain.switch_title_id import title_id_from_nsp

_TITLE_ID = "01006BB00C6F0000"


def _pfs0(names: tuple[str, ...]) -> bytes:
    """A PFS0 header naming *names*, in the layout the real archives use."""
    strings = b""
    name_offsets = []
    for name in names:
        name_offsets.append(len(strings))
        strings += name.encode() + b"\0"
    entries = b"".join(struct.pack("<QQII", 0, 0, offset, 0) for offset in name_offsets)
    header = b"PFS0" + struct.pack("<II", len(names), len(strings)) + b"\0\0\0\0"
    return header + entries + strings


def _entry(**overrides: object) -> ManagedPlatform:
    body = {
        "emulator": "Eden (Standalone)",
        "launch": ["%EMULATOR_FLATPAK-SPAWN%", "--host", "/home/deck/Applications/Eden.AppImage", "-f", "-g", "%ROM%"],
        "save_dir": "/nand/user/save/0000000000000000/93543B1D30E2AEB87D0F28AE30D83730/<save_id>",
        "save_unit": "title-dir",
        "needs": ["save_id"],
    }
    body.update(overrides)
    manifest = parse_layout_manifest('{"version": 1, "root": "/data", "platforms": {"switch": ' + _json(body) + "}}")
    assert manifest is not None
    entry = manifest.entry_for("switch")
    assert entry is not None
    return entry


def _json(value: object) -> str:
    import json

    return json.dumps(value)


class TestTheIdIsNotSplitLikeA3dsOne:
    """Measured failure: the 3DS split produced a directory no emulator writes.

    The live log showed ``…/93543B1D30E2AEB87D0F28AE30D83730/01006BB0/0C6F0000`` while Eden's
    folder is ``…/01006BB00C6F0000`` — the sync then found nothing, and the tab said the
    shape was unavailable.
    """

    def test_a_switch_id_rides_whole(self) -> None:
        identity = ContentIdentity(_TITLE_ID, IdentityKind.SWITCH_TITLE_ID, "Switch NSP ticket")
        assert save_id_text(identity) == _TITLE_ID

    def test_a_3ds_id_still_splits(self) -> None:
        identity = ContentIdentity("0004000000123400", IdentityKind.TITLE_ID, "3DS NCCH program id")
        assert save_id_text(identity) == "00040000/00123400"


class TestTheTitleIdComesFromTheArchive:
    def test_the_ticket_name_carries_the_title_id(self) -> None:
        head = _pfs0((_TITLE_ID.lower() + "0000000000000008.tik", "abc123.nca"))
        assert title_id_from_nsp(head) == _TITLE_ID

    def test_an_xci_shaped_file_states_nothing(self) -> None:
        # A gamecard image starts with its own header, not PFS0: refusing is the whole
        # point, because an id read from the wrong offset would file a save under a folder
        # the emulator never writes.
        assert title_id_from_nsp(b"HEAD" + b"\0" * 0x400) is None

    def test_an_archive_with_no_ticket_states_nothing(self) -> None:
        assert title_id_from_nsp(_pfs0(("abc123.nca",))) is None

    def test_a_truncated_head_states_nothing(self) -> None:
        full = _pfs0((_TITLE_ID.lower() + "0000000000000008.tik",))
        assert title_id_from_nsp(full[:20]) is None


class TestTheManifestStatesTheUnit:
    def test_a_title_dir_entry_answers_a_hole_naming_the_id(self) -> None:
        answer = manifest_answer(_entry(), content_installed=True)

        assert answer is not None
        assert answer.state == SAVE_STATE_HOLE
        assert answer.needs == ("save_id",)
        assert answer.granularity == "title-dir"
        assert answer.emulator == "Eden (Standalone)"
        assert answer.syncable is False

    def test_switch_restores_by_extraction_like_a_card_set(self) -> None:
        assert restores_by_extraction("switch") is True
        assert restores_by_extraction("gc") is True

    def test_filling_the_id_then_the_members_makes_it_syncable(self) -> None:
        stated = manifest_answer(_entry(), content_installed=True)
        assert stated is not None

        with_id = fill_save_id(stated, _TITLE_ID)
        assert with_id.directory is not None
        assert with_id.directory.endswith(_TITLE_ID)
        # The directory is now sayable and its members are not, which is the
        # "directory known" shape rather than a hole.
        assert with_id.state == SAVE_STATE_UNESTABLISHED
        assert with_id.unestablished == UNESTABLISHED_DIRECTORY_KNOWN

        named = fill_directory_members(with_id, ["0", "1", ".hidden"])
        assert named.state == SAVE_STATE_PER_GAME_FILES
        assert named.syncable is True
        assert named.synced_names == ("0", "1")

    def test_an_empty_folder_is_a_restore_target(self) -> None:
        """Measured on the reference Deck's Wii title: the managed folder was moved aside, the
        sync refused, and the save just uploaded was never fetched back."""
        stated = manifest_answer(_entry(), content_installed=True)
        assert stated is not None
        with_id = fill_save_id(stated, _TITLE_ID)

        empty = fill_directory_members(with_id, [])
        assert empty.syncable is True
        assert empty.components == ()
        assert empty.directory == with_id.directory

    def test_the_entry_is_managed_only_while_the_id_survives(self) -> None:
        # No id means no folder to read, so the answer stays a hole rather than pointing at
        # a directory with a literal ``<save_id>`` in its path.
        entry = _entry()
        assert "<save_id>" in entry.save_dir
