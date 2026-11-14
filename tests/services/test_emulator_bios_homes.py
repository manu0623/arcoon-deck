"""The service: which installs get a BIOS folder write, and what it reports.

The adapter's own behaviour is pinned in its tests, so what is asserted here is the
selection — the settings file probed, the platform narrowing, the families that take no
part, and the runtime with no BIOS root to name.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pytest

from adapters.emulator_bios_home import BiosHomeOutcome
from domain.emulator_registry import DetectionHints, EmulatorDef, InstalledEmulator
from services.emulator_bios_homes import EmulatorBiosHomeConfig, EmulatorBiosHomeService

if TYPE_CHECKING:
    from domain.emulator_bios_home import BiosHome

DUCKSTATION = EmulatorDef(
    id="duckstation",
    display_name="DuckStation",
    family="duckstation",
    platforms=("psx",),
    hints=DetectionHints(appimage_prefixes=("duckstation",)),
)

PPSSPP = EmulatorDef(
    id="ppsspp",
    display_name="PPSSPP",
    family="ppsspp",
    platforms=("psp",),
    hints=DetectionHints(appimage_prefixes=("ppsspp",)),
)

BIOS_ROOT = "/home/deck/.local/share/romm-tender/bios"
CONFIG = "/home/deck/.local/share/duckstation/settings.ini"


class _Scanner:
    def __init__(self, installs: list[InstalledEmulator]) -> None:
        self._installs = installs

    def installs(self) -> list[InstalledEmulator]:
        return list(self._installs)


class _Candidates:
    """The config reader's probe order, with the first candidate missing on purpose."""

    def __init__(self, paths: dict[str, tuple[str, ...]]) -> None:
        self._paths = paths
        self.asked: list[str] = []

    def candidates(self, install: InstalledEmulator) -> tuple[tuple[str, Any], ...]:
        self.asked.append(install.id)
        return tuple((path, object()) for path in self._paths.get(install.id, ()))


class _Recorder:
    def __init__(self) -> None:
        self.applied: list[BiosHome] = []

    def __call__(self, plan: BiosHome) -> BiosHomeOutcome:
        self.applied.append(plan)
        return BiosHomeOutcome(
            emulator=plan.emulator,
            status="pointed",
            directory=plan.directory,
            config_path=plan.config_path,
        )


def _service(
    *,
    installs: list[InstalledEmulator],
    candidates: _Candidates,
    bios_root: str | None = BIOS_ROOT,
    existing: set[str] | None = None,
    recorder: _Recorder | None = None,
) -> tuple[EmulatorBiosHomeService, _Recorder]:
    apply = recorder or _Recorder()
    files = existing if existing is not None else {CONFIG}
    return (
        EmulatorBiosHomeService(
            config=EmulatorBiosHomeConfig(
                logger=logging.getLogger("test"),
                external_emulators=_Scanner(installs),
                config_reader=candidates,
                bios_path=lambda: bios_root,
                config_exists=lambda path: path in files,
                apply=apply,
            )
        ),
        apply,
    )


@pytest.mark.asyncio
async def test_a_declared_emulator_is_pointed_at_its_platforms_folder() -> None:
    candidates = _Candidates(
        {"duckstation": ("/home/deck/Applications/settings.ini", CONFIG), "ppsspp": ("/x/ppsspp.ini",)}
    )
    service, apply = _service(
        installs=[
            InstalledEmulator(
                definition=DUCKSTATION, provider="native", path="/home/deck/Applications/DuckStation.AppImage"
            ),
            InstalledEmulator(definition=PPSSPP, provider="native", path="/home/deck/Applications/PPSSPP.AppImage"),
        ],
        candidates=candidates,
    )

    result = await service.ensure_all()

    assert result["bios_root"] == BIOS_ROOT
    assert [(home["emulator"], home["directory"]) for home in result["homes"]] == [("duckstation", f"{BIOS_ROOT}/psx")]
    # The first candidate does not exist, so the reader's next one is the file to write.
    assert [plan.config_path for plan in apply.applied] == [CONFIG]


@pytest.mark.asyncio
async def test_the_launch_pass_narrows_to_the_platform_about_to_start() -> None:
    service, apply = _service(
        installs=[
            InstalledEmulator(
                definition=DUCKSTATION, provider="native", path="/home/deck/Applications/DuckStation.AppImage"
            )
        ],
        candidates=_Candidates({"duckstation": (CONFIG,)}),
    )

    result = await service.ensure_for_platform("psp")

    assert result["homes"] == []
    assert apply.applied == []


@pytest.mark.asyncio
async def test_no_bios_root_means_no_write() -> None:
    service, apply = _service(
        installs=[
            InstalledEmulator(
                definition=DUCKSTATION, provider="native", path="/home/deck/Applications/DuckStation.AppImage"
            )
        ],
        candidates=_Candidates({"duckstation": (CONFIG,)}),
        bios_root=None,
    )

    result = await service.ensure_all()

    assert result == {"bios_root": None, "homes": []}
    assert apply.applied == []


@pytest.mark.asyncio
async def test_an_install_with_no_settings_file_is_not_written_to() -> None:
    service, apply = _service(
        installs=[
            InstalledEmulator(
                definition=DUCKSTATION, provider="native", path="/home/deck/Applications/DuckStation.AppImage"
            )
        ],
        candidates=_Candidates({"duckstation": (CONFIG,)}),
        existing=set(),
    )

    result = await service.ensure_all()

    assert result["homes"] == []
    assert apply.applied == []
