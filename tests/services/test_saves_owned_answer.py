"""The save answer for a ROM launched by the plugin's own RetroArch command.

On a device with no RetroDECK there is no ES-DE catalogue to ask, so asking it made
every owned launch report an unestablished save and every sync path skip with
``save_shape_unsupported`` — for a save directory the plugin had just written into the
launch's own ``--appendconfig``.
"""

from __future__ import annotations

import logging
import os
from typing import ClassVar

from fakes.fake_active_core_resolver import FakeActiveCoreResolver
from fakes.fake_retrodeck_paths import FakeRetroDeckPaths
from fakes.fake_save_location_reader import FakeSaveLocationReader
from fakes.fake_unit_of_work import FakeUnitOfWork

from domain.content_identity import ContentIdentity, IdentityKind
from domain.rom import Rom
from domain.rom_install import RomInstall
from domain.shortcut_data import EmulatorInvocation
from services.saves.rom_info import PACKED_ARCHIVE_DIR_NAME, RomInfoService, RomInfoServiceConfig

_ROM_ID = 2171
_GBA_FILE = "/home/deck/Emulation/roms/gba/Legend of Zelda, The - The Minish Cap (USA).gba"
_BANK_DIR = "/home/deck/.local/share/romm-tender/saves/gba"


class _FileStore:
    """A save store that knows no files: nothing has been written yet."""

    def listdir(self, path: str) -> list[str]:
        return []

    def is_file(self, path: str) -> bool:
        return False

    def exists(self, path: str) -> bool:
        return False


def _service(
    *, emulator: EmulatorInvocation | None, bank_dir: str | None
) -> tuple[RomInfoService, FakeSaveLocationReader]:
    uow = FakeUnitOfWork()
    with uow:
        uow.roms.save(
            Rom(
                rom_id=_ROM_ID,
                platform_slug="gba",
                name="The Legend of Zelda: The Minish Cap",
                fs_name="Legend of Zelda, The - The Minish Cap (USA).gba",
                shortcut_app_id=3075086748,
                last_synced_at="2025-01-01T00:00:00",
            )
        )
        uow.rom_installs.save(
            RomInstall.mark_installed(
                rom_id=_ROM_ID,
                file_path=_GBA_FILE,
                rom_dir=None,
                platform_slug="gba",
                system="gba",
                installed_at="2025-01-01T00:00:00",
            )
        )
    catalogue = FakeSaveLocationReader()
    service = RomInfoService(
        config=RomInfoServiceConfig(
            uow_factory=lambda: uow,
            save_file_store=_FileStore(),
            retrodeck_paths=FakeRetroDeckPaths(),
            active_core=FakeActiveCoreResolver(default_emulator=emulator),
            save_locations=catalogue,
            resolve_system=lambda slug: slug,
            get_core_name=lambda core: None,
            logger=logging.getLogger("test_saves_owned_answer"),
            save_bank_dir=(lambda platform: bank_dir) if bank_dir is not None else None,
        )
    )
    return service, catalogue


class TestOwnedLibretroSaveAnswer:
    def test_the_owned_launch_states_its_own_save_set(self) -> None:
        service, _catalogue = _service(
            emulator=EmulatorInvocation.libretro("mgba_libretro", "mGBA"), bank_dir=_BANK_DIR
        )

        answer = service.save_answer(_ROM_ID)

        assert answer.syncable is True
        assert answer.directory == _BANK_DIR
        assert answer.synced_names[0] == "Legend of Zelda, The - The Minish Cap (USA).srm"

    def test_the_catalogue_is_not_asked_for_a_launch_we_wrote(self) -> None:
        service, catalogue = _service(emulator=EmulatorInvocation.libretro("mgba_libretro", "mGBA"), bank_dir=_BANK_DIR)

        service.save_answer(_ROM_ID)

        assert catalogue.calls == []

    def test_without_the_bank_the_catalogue_still_answers(self) -> None:
        # The bank is the switch that says the launch is redirected; with it off the
        # launch writes wherever the catalogue says, so the catalogue is asked.
        service, catalogue = _service(emulator=EmulatorInvocation.libretro("mgba_libretro", "mGBA"), bank_dir=None)

        service.save_answer(_ROM_ID)

        assert catalogue.calls != []


_SWITCH_NAND = "/home/deck/Emulation/storage/yuzu/nand"
_SWITCH_BASE = _SWITCH_NAND + "/user"


class _SwitchStore:
    """The switch nand as Eden lays it out, with one signed-in profile."""

    # Joined with the host's separator, because the layout rule joins the discovered
    # user onto the base the same way: the keys must be the ones it will look up.
    _TREE: ClassVar[dict[str, list[str]]] = {
        _SWITCH_BASE: ["save"],
        os.path.join(_SWITCH_BASE, "save"): ["0000000000000000"],
    }

    def listdir(self, path: str) -> list[str]:
        return self._TREE.get(path, [])

    def is_file(self, path: str) -> bool:
        return False

    def exists(self, path: str) -> bool:
        return False


def _switch_service():
    uow = FakeUnitOfWork()
    with uow:
        uow.roms.save(
            Rom(
                rom_id=4242,
                platform_slug="switch",
                name="Bayonetta Origins",
                fs_name="Bayonetta Origins.xci",
                shortcut_app_id=99,
                last_synced_at="2025-01-01T00:00:00",
            )
        )
        uow.rom_installs.save(
            RomInstall.mark_installed(
                rom_id=4242,
                file_path="/home/deck/Emulation/roms/switch/Bayonetta Origins.xci",
                rom_dir=None,
                platform_slug="switch",
                system="switch",
                installed_at="2025-01-01T00:00:00",
            )
        )
    catalogue = FakeSaveLocationReader()
    service = RomInfoService(
        config=RomInfoServiceConfig(
            uow_factory=lambda: uow,
            save_file_store=_SwitchStore(),
            retrodeck_paths=FakeRetroDeckPaths(),
            active_core=FakeActiveCoreResolver(
                default_emulator=EmulatorInvocation.standalone("/home/deck/Applications/Eden.AppImage -f -g %ROM%")
            ),
            save_locations=catalogue,
            resolve_system=lambda slug: slug,
            get_core_name=lambda core: None,
            logger=logging.getLogger("test_saves_owned_answer"),
            content_identity=lambda path, platform: ContentIdentity(
                save_id="0100000000010000", kind=IdentityKind.SWITCH_TITLE_ID, source="test"
            ),
            standalone_save_base=lambda platform: _SWITCH_BASE if platform == "switch" else None,
        )
    )
    return service, catalogue


class TestStandalonePlatformSaveAnswer:
    """A standalone emulator that states its own save tree, on a device with no ES-DE."""

    def test_the_title_folder_is_named_from_the_content_id(self) -> None:
        service, _catalogue = _switch_service()

        answer = service.save_answer(4242)

        assert answer.syncable is True
        assert answer.granularity == "title-dir"
        assert answer.directory == _SWITCH_BASE
        assert len(answer.synced_files) == 1
        assert answer.synced_files[0].name.startswith("01000000000")

    def test_the_catalogue_is_not_asked_when_the_emulator_stated_it(self) -> None:
        service, catalogue = _switch_service()

        service.save_answer(4242)

        assert catalogue.calls == []


_PSP_FILE = "/home/deck/Emulation/roms/psp/Burnout Legends.iso"
_PSP_BASE = "/home/deck/.local/share/romm-tender/saves/psp/PSP/SAVEDATA"


class _PspStore:
    """A PPSSPP memory stick holding one game's save folders.

    The tree is the one the core writes once the appendconfig names ``saves/psp``:
    it builds ``PSP/SAVEDATA`` itself, so the folders sit under the layout's base.
    """

    _TREE: ClassVar[dict[str, list[str]]] = {
        _PSP_BASE: ["ULUS10064DATA00", "ULUS10064SETTINGS", "ULUS10567SYSDATA"],
    }

    def listdir(self, path: str) -> list[str]:
        return self._TREE.get(path, [])

    def is_file(self, path: str) -> bool:
        return False

    def is_dir(self, path: str) -> bool:
        # The base itself, and any folder the base lists: that is what a member of a
        # folder-shaped save is.
        return path in self._TREE or os.path.dirname(path) == _PSP_BASE

    def exists(self, path: str) -> bool:
        return path in self._TREE or os.path.dirname(path) == _PSP_BASE


def _psp_service(
    *, with_identity: bool, emulator: EmulatorInvocation | None = None
) -> tuple[RomInfoService, FakeSaveLocationReader]:
    uow = FakeUnitOfWork()
    with uow:
        uow.roms.save(
            Rom(
                rom_id=_ROM_ID,
                platform_slug="psp",
                name="Burnout Legends",
                fs_name="Burnout Legends.iso",
                shortcut_app_id=2222,
                last_synced_at="2025-01-01T00:00:00",
            )
        )
        uow.rom_installs.save(
            RomInstall.mark_installed(
                rom_id=_ROM_ID,
                file_path=_PSP_FILE,
                rom_dir=None,
                platform_slug="psp",
                system="psp",
                installed_at="2025-01-01T00:00:00",
            )
        )
    catalogue = FakeSaveLocationReader()
    service = RomInfoService(
        config=RomInfoServiceConfig(
            uow_factory=lambda: uow,
            save_file_store=_PspStore(),
            retrodeck_paths=FakeRetroDeckPaths(),
            active_core=FakeActiveCoreResolver(
                default_emulator=(
                    emulator
                    if emulator is not None
                    else EmulatorInvocation.libretro("ppsspp_libretro", "PPSSPP (libretro)")
                )
            ),
            save_locations=catalogue,
            resolve_system=lambda slug: slug,
            get_core_name=lambda core: None,
            logger=logging.getLogger("test_saves_owned_answer"),
            save_bank_dir=lambda platform: _PSP_BASE,
            content_identity=(
                (lambda path, platform: ContentIdentity(save_id="ULUS10064", kind=IdentityKind.DISC_ID, source="test"))
                if with_identity
                else None
            ),
        )
    )
    return service, catalogue


class TestPspSaveAnswer:
    """A PSP save is the set of folders the disc id prefixes, not one file (ADR-0048)."""

    def test_the_members_are_the_folders_carrying_the_disc_id(self) -> None:
        service, _catalogue = _psp_service(with_identity=True)

        answer = service.save_answer(_ROM_ID)

        assert answer.syncable is True
        assert answer.directory == _PSP_BASE
        assert answer.granularity == "title-dir"
        assert answer.synced_names == ("ULUS10064DATA00", "ULUS10064SETTINGS")

    def test_another_games_folders_are_not_part_of_it(self) -> None:
        service, _catalogue = _psp_service(with_identity=True)

        answer = service.save_answer(_ROM_ID)

        assert "ULUS10567SYSDATA" not in answer.synced_names

    def test_without_an_identity_the_answer_is_a_hole(self) -> None:
        service, _catalogue = _psp_service(with_identity=False)

        answer = service.save_answer(_ROM_ID)

        assert answer.syncable is False
        assert "save_id" in answer.needs

    def test_the_catalogue_is_never_asked(self) -> None:
        service, catalogue = _psp_service(with_identity=True)

        service.save_answer(_ROM_ID)

        assert catalogue.calls == []

    def test_a_save_folder_counts_as_a_local_save(self) -> None:
        """The wizard has to see it, or it offers to adopt a save the machine already has."""
        service, _catalogue = _psp_service(with_identity=True)

        files = service.find_save_files(_ROM_ID)

        assert [entry["filename"] for entry in files] == ["ULUS10064DATA00", "ULUS10064SETTINGS"]


class _EmptyPspStore(_PspStore):
    """A memory stick the game has never written to."""

    _TREE: ClassVar[dict[str, list[str]]] = {_PSP_BASE: []}

    def is_dir(self, path: str) -> bool:
        return path == _PSP_BASE

    def exists(self, path: str) -> bool:
        return path == _PSP_BASE


def test_a_fresh_psp_game_still_has_a_download_target() -> None:
    """Nothing local yet, so the unit synced is the archive the server's save extracts from."""
    service, _catalogue = _psp_service(with_identity=True)
    service._save_file_store = _EmptyPspStore()
    info = service.get_rom_save_info(_ROM_ID)
    assert info is not None

    answer = service.save_answer(_ROM_ID)
    assert answer.syncable is True

    names, directory, extract_dir = service.save_unit(info, answer)

    assert names == ("Burnout Legends.zip",)
    assert directory == os.path.join(os.path.dirname(_PSP_BASE), PACKED_ARCHIVE_DIR_NAME)
    assert extract_dir == _PSP_BASE


def _standalone_ppsspp() -> EmulatorInvocation:
    """The AppImage the install action put in ~/Applications — the one the plugin links."""
    return EmulatorInvocation.standalone(
        '"/home/deck/Applications/PPSSPP.AppImage" %ROM%',
        label="PPSSPP (AppImage)",
        emulator="ppsspp",
    )


def _standalone_unlinked() -> EmulatorInvocation:
    """An emulator whose folder the plugin does not point at the bank."""
    return EmulatorInvocation.standalone(
        '"/home/deck/Applications/DuckStation.AppImage" %ROM%',
        label="DuckStation (AppImage)",
        emulator="duckstation",
    )


class TestPspStandaloneSaveAnswer:
    """The standalone PPSSPP the plugin pointed at the bank answers from the bank.

    Measured on the reference Deck (0.44.2): a PSP game launched with the standalone
    PPSSPP reported ``save_shape_unsupported``, because the save layer asked a catalogue
    that is not installed. Its save folder is a symlink into the bank (ADR-0051), so the
    bank is the truth — and the sync both downloads and uploads again.
    """

    def test_a_pointed_standalone_launch_answers_from_the_bank(self) -> None:
        service, catalogue = _psp_service(with_identity=True, emulator=_standalone_ppsspp())

        answer = service.save_answer(_ROM_ID)

        assert answer.syncable is True
        assert answer.directory == _PSP_BASE
        assert answer.synced_names == ("ULUS10064DATA00", "ULUS10064SETTINGS")
        assert catalogue.calls == []

    def test_a_standalone_emulator_the_plugin_does_not_point_keeps_the_refusal(self) -> None:
        """DuckStation's folder is nobody's redirect yet, so claiming the bank here would
        describe a program that writes somewhere else."""
        service, catalogue = _psp_service(with_identity=True, emulator=_standalone_unlinked())

        service.save_answer(_ROM_ID)

        assert catalogue.calls != []


_BANK_3DS = "/home/deck/.local/share/romm-tender/saves/3ds/sdmc/Nintendo 3DS"
_ID0 = "0" * 32
_ID1 = "0" * 32
# Joined with the host's separator, because the layout rule joins the discovered levels
# onto the base the same way: the keys must be the ones it will look up.
_TITLE_ROOT = os.path.join(_BANK_3DS, _ID0, _ID1)


class _N3dsStore:
    """Azahar's save tree as it looks after the link: two titles, one of them ours."""

    _TREE: ClassVar[dict[str, list[str]]] = {
        _BANK_3DS: [_ID0],
        os.path.join(_BANK_3DS, _ID0): [_ID1],
        _TITLE_ROOT: ["title", "extdata"],
        os.path.join(_TITLE_ROOT, "title"): ["00040000"],
        os.path.join(_TITLE_ROOT, "title", "00040000"): ["000ec300", "00054000"],
        os.path.join(_TITLE_ROOT, "title", "00040000", "000ec300"): ["data"],
        os.path.join(_TITLE_ROOT, "title", "00040000", "000ec300", "data"): ["00000001"],
        os.path.join(_TITLE_ROOT, "title", "00040000", "00054000"): ["data"],
    }

    def listdir(self, path: str) -> list[str]:
        return self._TREE.get(path, [])

    def is_file(self, path: str) -> bool:
        return False

    def exists(self, path: str) -> bool:
        return False


def _n3ds_service(*, emulator: EmulatorInvocation | None) -> tuple[RomInfoService, FakeSaveLocationReader]:
    uow = FakeUnitOfWork()
    with uow:
        uow.roms.save(
            Rom(
                rom_id=_ROM_ID,
                platform_slug="3ds",
                name="The Legend of Zelda: A Link Between Worlds",
                fs_name="Legend of Zelda A Link Between Worlds.3ds",
                shortcut_app_id=4242,
                last_synced_at="2025-01-01T00:00:00",
            )
        )
        uow.rom_installs.save(
            RomInstall.mark_installed(
                rom_id=_ROM_ID,
                file_path="/home/deck/Emulation/roms/n3ds/Legend of Zelda A Link Between Worlds.3ds",
                rom_dir=None,
                platform_slug="3ds",
                system="3ds",
                installed_at="2025-01-01T00:00:00",
            )
        )
    catalogue = FakeSaveLocationReader()
    service = RomInfoService(
        config=RomInfoServiceConfig(
            uow_factory=lambda: uow,
            save_file_store=_N3dsStore(),
            retrodeck_paths=FakeRetroDeckPaths(),
            active_core=FakeActiveCoreResolver(default_emulator=emulator),
            save_locations=catalogue,
            resolve_system=lambda slug: slug,
            get_core_name=lambda core: None,
            logger=logging.getLogger("test_saves_owned_answer"),
            save_bank_dir=lambda platform: _BANK_3DS,
            content_identity=lambda path, platform: ContentIdentity(
                save_id="00040000000ec300", kind=IdentityKind.TITLE_ID, source="test"
            ),
        )
    )
    return service, catalogue


class Test3dsSaveAnswer:
    """A 3DS save is one title's ``data`` (and ``extdata``) tree, named by the ROM's id.

    Measured on the reference Deck: the ROM's NCCH header states ``00040000000ec300`` and
    Azahar's ``sdmc/Nintendo 3DS`` holds that title under
    ``title/00040000/000ec300/data`` — which is the tree this answer has to name, or the
    sync carries the wrong game's folder.
    """

    def test_a_linked_azahar_launch_answers_from_the_bank(self) -> None:
        service, catalogue = _n3ds_service(
            emulator=EmulatorInvocation.standalone(
                '"/usr/bin/flatpak" run org.azahar_emu.Azahar %ROM%',
                label="Azahar (Flatpak)",
                emulator="azahar",
            )
        )

        answer = service.save_answer(_ROM_ID)

        assert answer.syncable is True
        assert answer.directory == _BANK_3DS
        # The member is named by its path inside the answer's directory, which is what
        # packing and restoring both walk from (see ``domain.save_bank._n3ds_title``).
        assert [component.name for component in answer.components] == [f"{_ID0}/{_ID1}/title/00040000/000ec300/data"]
        assert answer.components[0].directory == os.path.join(_TITLE_ROOT, "title", "00040000", "000ec300")
        assert catalogue.calls == []

    def test_another_titles_folder_is_not_part_of_it(self) -> None:
        service, _catalogue = _n3ds_service(emulator=EmulatorInvocation.standalone("azahar %ROM%", emulator="azahar"))

        answer = service.save_answer(_ROM_ID)

        assert all("00054000" not in component.directory for component in answer.components)

    def test_an_unlinked_3ds_emulator_keeps_the_catalogue_refusal(self) -> None:
        """Citra's tree is somewhere else, so claiming the bank would describe a program
        that writes in a directory this answer never looks at."""
        service, catalogue = _n3ds_service(emulator=EmulatorInvocation.standalone("citra-qt %ROM%", emulator="citra"))

        service.save_answer(_ROM_ID)

        assert catalogue.calls != []


def test_a_fresh_3ds_title_still_has_a_download_target() -> None:
    """Nothing local yet, so the answer is the place a server save unpacks into — the
    restore would otherwise refuse for a game the plugin can identify perfectly well."""
    service, _catalogue = _n3ds_service(emulator=EmulatorInvocation.standalone("azahar %ROM%", emulator="azahar"))
    empty = {
        key: value for key, value in _N3dsStore._TREE.items() if "000ec300" not in key or key.endswith("/00040000")
    }
    service._save_file_store = type("_EmptyStore", (_N3dsStore,), {"_TREE": empty})()

    answer = service.save_answer(_ROM_ID)

    assert answer.syncable is True
    assert answer.components == ()
    assert answer.directory == _BANK_3DS
