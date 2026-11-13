"""The save answer for a ROM launched by the plugin's own RetroArch command.

On a device with no RetroDECK there is no ES-DE catalogue to ask, so asking it made
every owned launch report an unestablished save and every sync path skip with
``save_shape_unsupported`` — for a save directory the plugin had just written into the
launch's own ``--appendconfig``.
"""

from __future__ import annotations

import logging

from fakes.fake_active_core_resolver import FakeActiveCoreResolver
from fakes.fake_retrodeck_paths import FakeRetroDeckPaths
from fakes.fake_save_location_reader import FakeSaveLocationReader
from fakes.fake_unit_of_work import FakeUnitOfWork

from domain.rom import Rom
from domain.rom_install import RomInstall
from domain.shortcut_data import EmulatorInvocation
from services.saves.rom_info import RomInfoService, RomInfoServiceConfig

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
        service, catalogue = _service(
            emulator=EmulatorInvocation.libretro("mgba_libretro", "mGBA"), bank_dir=_BANK_DIR
        )

        service.save_answer(_ROM_ID)

        assert catalogue.calls == []

    def test_without_the_bank_the_catalogue_still_answers(self) -> None:
        # The bank is the switch that says the launch is redirected; with it off the
        # launch writes wherever the catalogue says, so the catalogue is asked.
        service, catalogue = _service(
            emulator=EmulatorInvocation.libretro("mgba_libretro", "mGBA"), bank_dir=None
        )

        service.save_answer(_ROM_ID)

        assert catalogue.calls != []
