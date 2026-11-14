"""Adopting a ROM the library knows whose file is already on disk.

The failure this exists for is measured: three ``.3ds`` files in
``~/Emulation/roms/n3ds``, one of them with 128 played sessions, and no ``rom_installs`` row
for the platform — so the save layer refused every one of them with ``needs: save_id`` for a
file sitting in plain sight, and the launch bake had no path either.

The rules these tests pin are the ones that keep the claim honest: a row is adopted only
when the disk names it, a tie is not guessed between, a folder is left to the download
path's launch-file rules, and only roots this plugin owns are searched.
"""

from __future__ import annotations

import logging
import os
from typing import ClassVar

import pytest
from fakes.fake_unit_of_work import FakeUnitOfWork

from domain.rom import Rom
from domain.rom_install import RomInstall
from services.rom_install_discovery import RomInstallDiscoveryConfig, RomInstallDiscoveryService

APP_ROOT = "/home/deck/.local/share/romm-tender/roms"
EMUDECK_ROOT = "/home/deck/Emulation/roms"
ALL_EXTENSIONS = frozenset({".3ds", ".cia", ".iso", ".zip"})
NOW = "2026-11-13T14:00:00"


class _Tree:
    """A filesystem made of the entries a test states."""

    _FILES: ClassVar[dict[str, tuple[str, ...]]] = {}
    _DIRS: ClassVar[frozenset[str]] = frozenset()

    def listdir(self, path: str) -> list[str]:
        if path not in self._FILES:
            raise OSError(f"not a directory: {path}")
        return list(self._FILES[path])

    def is_file(self, path: str) -> bool:
        # Keyed by base name: the service joins a full path onto the platform directory,
        # and the fake only knows the entries a directory holds.
        name = os.path.basename(path)
        return any(name in entries for entries in self._FILES.values())

    def is_dir(self, path: str) -> bool:
        # A test states the folder-backed entries by name: the service joins them onto a
        # platform directory the fake does not model beyond its entries.
        return path in self._FILES or os.path.basename(path) in self._DIRS


class _EmptyTree(_Tree):
    _FILES: ClassVar[dict[str, tuple[str, ...]]] = {}


def _tree(files: dict[str, tuple[str, ...]]) -> type[_Tree]:
    return type("_TestTree", (_Tree,), {"_FILES": files})


def _rom(rom_id: int, *, fs_name: str, platform_slug: str = "3ds", name: str = "A Game") -> Rom:
    return Rom(
        rom_id=rom_id,
        platform_slug=platform_slug,
        name=name,
        fs_name=fs_name,
        shortcut_app_id=None,
        last_synced_at=NOW,
    )


def _service(
    *,
    roms: list[Rom],
    store: type[_Tree],
    roots: tuple[str, ...] = (APP_ROOT, EMUDECK_ROOT),
    extensions: frozenset[str] = ALL_EXTENSIONS,
) -> tuple[RomInstallDiscoveryService, FakeUnitOfWork]:
    uow = FakeUnitOfWork()
    with uow:
        for rom in roms:
            uow.roms.save(rom)
    service = RomInstallDiscoveryService(
        config=RomInstallDiscoveryConfig(
            logger=logging.getLogger("test_rom_install_discovery"),
            uow_factory=lambda: uow,
            file_store=store(),
            roms_roots=lambda: roots,
            resolve_system=lambda slug: slug,
            system_extensions=lambda system: extensions,
            now=lambda: NOW,
        ),
    )
    return service, uow


class TestTheFilesItAdopts:
    @pytest.mark.asyncio
    async def test_a_row_with_a_bare_name_matches_the_one_file_that_carries_it(self) -> None:
        """RomM often states ``Legend of Zelda A Link Between Worlds`` with no extension;
        the file on disk is ``.3ds``. The stem is the claim, and one match is enough."""
        service, uow = _service(
            roms=[_rom(11, fs_name="Legend of Zelda A Link Between Worlds")],
            store=_tree(
                {
                    os.path.join(EMUDECK_ROOT, "3ds"): (
                        "Legend of Zelda A Link Between Worlds.3ds",
                        "Super Mario 3D Land (USA).3ds",
                    )
                }
            ),
        )

        answer = await service.adopt_found_content()

        assert [entry["rom_id"] for entry in answer["adopted"]] == [11]
        install = uow.rom_installs.get(11)
        assert install is not None
        assert install.file_path == os.path.join(EMUDECK_ROOT, "3ds", "Legend of Zelda A Link Between Worlds.3ds")
        assert (install.platform_slug, install.system, install.rom_dir) == ("3ds", "3ds", None)
        assert install.installed_at == NOW

    @pytest.mark.asyncio
    async def test_an_exact_name_is_preferred_over_a_stem_match(self) -> None:
        """A row that states the extension names exactly one file, and a second file
        sharing the stem (a patched copy) must not make that a coin toss."""
        service, _uow = _service(
            roms=[_rom(1, fs_name="Kirby.3ds")],
            store=_tree({os.path.join(EMUDECK_ROOT, "3ds"): ("Kirby.3ds", "Kirby.3ds.bak.3ds")}),
            roots=(EMUDECK_ROOT,),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"][0]["file_path"] == os.path.join(EMUDECK_ROOT, "3ds", "Kirby.3ds")

    @pytest.mark.asyncio
    async def test_todays_root_is_searched_before_the_older_ones(self) -> None:
        """ADR-0046: a structure change moves nothing, so both trees can hold the file.
        Today's root is the one the install should point at."""
        service, _uow = _service(
            roms=[_rom(1, fs_name="Kirby.3ds")],
            store=_tree(
                {
                    os.path.join(APP_ROOT, "3ds"): ("Kirby.3ds",),
                    os.path.join(EMUDECK_ROOT, "3ds"): ("Kirby.3ds",),
                }
            ),
            roots=(APP_ROOT, EMUDECK_ROOT),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"][0]["file_path"] == os.path.join(APP_ROOT, "3ds", "Kirby.3ds")


class TestWhatItRefusesToAdopt:
    @pytest.mark.asyncio
    async def test_two_files_sharing_a_stem_are_not_guessed_between(self) -> None:
        """Adopting the wrong one names another game's save — worse than not adopting."""
        service, uow = _service(
            roms=[_rom(1, fs_name="Kirby")],
            store=_tree({os.path.join(EMUDECK_ROOT, "3ds"): ("Kirby.3ds", "Kirby.cia")}),
            roots=(EMUDECK_ROOT,),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert [entry["rom_id"] for entry in answer["ambiguous"]] == [1]
        assert uow.rom_installs.get(1) is None

    @pytest.mark.asyncio
    async def test_a_folder_backed_rom_is_left_to_the_download_rules(self) -> None:
        """Which file inside a folder launches is decided by the M3U and collapse rules,
        not by a scan: it is reported, not adopted."""
        service, uow = _service(
            roms=[_rom(2, fs_name="Some Disc Game", platform_slug="ps3")],
            store=type(
                "_DiscTree",
                (_Tree,),
                {
                    "_FILES": {os.path.join(EMUDECK_ROOT, "ps3"): ("Some Disc Game",)},
                    "_DIRS": frozenset({"Some Disc Game"}),
                },
            ),
            roots=(EMUDECK_ROOT,),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert [entry["rom_id"] for entry in answer["directories"]] == [2]
        assert uow.rom_installs.get(2) is None

    @pytest.mark.asyncio
    async def test_a_rom_already_installed_is_not_touched(self) -> None:
        service, uow = _service(
            roms=[_rom(3, fs_name="Kirby.3ds")],
            store=_tree({os.path.join(EMUDECK_ROOT, "3ds"): ("Kirby.3ds",)}),
            roots=(EMUDECK_ROOT,),
        )
        existing = RomInstall.mark_installed(
            rom_id=3,
            file_path="/somewhere/else/Kirby.3ds",
            rom_dir=None,
            platform_slug="3ds",
            system="3ds",
            installed_at=NOW,
        )
        with uow:
            uow.rom_installs.save(existing)

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert uow.rom_installs.get(3).file_path == "/somewhere/else/Kirby.3ds"

    @pytest.mark.asyncio
    async def test_a_row_with_no_name_or_platform_is_skipped(self) -> None:
        service, uow = _service(
            roms=[_rom(4, fs_name="", platform_slug="")],
            store=_tree({os.path.join(EMUDECK_ROOT, "3ds"): ("Kirby.3ds",)}),
            roots=(EMUDECK_ROOT,),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert uow.rom_installs.get(4) is None

    @pytest.mark.asyncio
    async def test_a_missing_platform_directory_is_not_an_error(self) -> None:
        """The ordinary case: the library is bigger than the disk."""
        service, _uow = _service(
            roms=[_rom(5, fs_name="Kirby.3ds")],
            store=_EmptyTree,
            roots=(EMUDECK_ROOT,),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert answer["roots"] == [EMUDECK_ROOT]


class TestWhatIsNotAGame:
    @pytest.mark.asyncio
    async def test_a_document_in_the_folder_is_not_adopted_as_a_game(self) -> None:
        """Measured on the reference Deck: ``rpcs3_guide.txt`` and EmuDeck's "Disc Games
        Can Be Put Here For Automatic Detection.txt" were adopted as two PS3 games,
        because their library rows carry those names and the files are right there.
        A format no emulator for the system reads is not an install."""
        service, uow = _service(
            roms=[_rom(6, fs_name="rpcs3_guide.txt", platform_slug="ps3")],
            store=_tree({os.path.join(EMUDECK_ROOT, "ps3"): ("rpcs3_guide.txt",)}),
            extensions=frozenset({".iso", ".pkg"}),
        )

        answer = await service.adopt_found_content()

        assert answer["adopted"] == []
        assert uow.rom_installs.get(6) is None
