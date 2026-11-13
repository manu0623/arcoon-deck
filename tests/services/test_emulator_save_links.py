"""The service: which installs get a link, and what it reports.

The emulator side is faked (the adapter's own behaviour is pinned in its tests), so
what is asserted here is the selection — the provider's config root, the platform
narrowing, and the families that take no part.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pytest

from domain.emulator_registry import DetectionHints, EmulatorDef, InstalledEmulator
from services.emulator_save_links import EmulatorSaveLinkConfig, EmulatorSaveLinkService

if TYPE_CHECKING:
    from domain.emulator_save_link import SaveLink

PPSSPP = EmulatorDef(
    id="ppsspp",
    display_name="PPSSPP",
    family="ppsspp",
    platforms=("psp",),
    hints=DetectionHints(appimage_prefixes=("ppsspp",), flatpak_ids=("org.ppsspp.PPSSPP",)),
)

DOLPHIN = EmulatorDef(
    id="dolphin",
    display_name="Dolphin",
    family="dolphin",
    platforms=("gc",),
    hints=DetectionHints(flatpak_ids=("org.DolphinEmu.dolphin-emu",)),
)

SAVES = "/home/deck/.local/share/romm-tender/saves"


class _Scanner:
    def __init__(self, installs: list[InstalledEmulator]) -> None:
        self._installs = installs

    def installs(self) -> list[InstalledEmulator]:
        return list(self._installs)


class _Roots:
    """The config reader's answer, keyed by provider, as the adapter computes it."""

    def __init__(self, roots: dict[str, str]) -> None:
        self._roots = roots
        self.asked: list[str] = []

    class _Roots:
        def __init__(self, config: str, data: str) -> None:
            self.config = config
            self.data = data

    def root_variants(self, install: InstalledEmulator, *, app_dir: str) -> tuple[Any, ...]:
        self.asked.append(f"{install.provider}:{app_dir}")
        root = self._roots.get(install.provider)
        return (self._Roots(root, root.replace("/config/", "/data/")),) if root else ()


class _Recorder:
    def __init__(self) -> None:
        self.applied: list[SaveLink] = []

    def __call__(self, link: SaveLink) -> Any:
        self.applied.append(link)
        from adapters.emulator_save_link import LinkOutcome

        return LinkOutcome(
            emulator=link.emulator,
            emulator_dir=link.emulator_dir,
            owned_dir=link.owned_dir,
            status="linked",
        )


def _service(
    installs: list[InstalledEmulator], roots: dict[str, str], apply: Any | None = None
) -> tuple[EmulatorSaveLinkService, _Recorder, _Roots]:
    recorder = apply or _Recorder()
    roots_reader = _Roots(roots)
    built = EmulatorSaveLinkService(
        config=EmulatorSaveLinkConfig(
            logger=logging.getLogger("test_emulator_save_links"),
            external_emulators=_Scanner(installs),
            config_reader=roots_reader,
            saves_path=lambda: SAVES,
            apply=recorder,
        )
    )
    return built, recorder, roots_reader


NATIVE_PPSSPP = InstalledEmulator(definition=PPSSPP, provider="native", path="/home/deck/Applications/PPSSPP.AppImage")
FLATPAK_PPSSPP = InstalledEmulator(definition=PPSSPP, provider="flatpak", path="org.ppsspp.PPSSPP")
FLATPAK_DOLPHIN = InstalledEmulator(definition=DOLPHIN, provider="flatpak", path="org.DolphinEmu.dolphin-emu")


class TestSelection:
    @pytest.mark.asyncio
    async def test_it_links_each_provider_in_its_own_config_root(self) -> None:
        built, recorder, _ = _service(
            [NATIVE_PPSSPP, FLATPAK_PPSSPP],
            {
                "native": "/home/deck/.config/ppsspp",
                "flatpak": "/home/deck/.var/app/org.ppsspp.PPSSPP/config/ppsspp",
            },
        )

        answer = await built.ensure_all()

        assert answer["saves_root"] == SAVES
        assert [entry["emulator_dir"] for entry in answer["links"]] == [
            "/home/deck/.config/ppsspp/PSP/SAVEDATA",
            "/home/deck/.var/app/org.ppsspp.PPSSPP/config/ppsspp/PSP/SAVEDATA",
        ]
        assert all(link.owned_dir == f"{SAVES}/psp/PSP/SAVEDATA" for link in recorder.applied)

    @pytest.mark.asyncio
    async def test_an_emulator_with_no_save_folder_of_ours_is_left_alone(self) -> None:
        built, recorder, _ = _service(
            [FLATPAK_DOLPHIN], {"flatpak": "/home/deck/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu"}
        )

        answer = await built.ensure_all()

        assert answer["links"] == []
        assert recorder.applied == []

    @pytest.mark.asyncio
    async def test_narrowing_to_a_platform_skips_the_others(self) -> None:
        built, recorder, _ = _service(
            [NATIVE_PPSSPP, FLATPAK_DOLPHIN],
            {
                "native": "/home/deck/.config/ppsspp",
                "flatpak": "/home/deck/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu",
            },
        )

        answer = await built.ensure_for_platform("psp")

        assert len(answer["links"]) == 1
        assert [link.emulator for link in recorder.applied] == ["ppsspp"]

    @pytest.mark.asyncio
    async def test_a_provider_with_no_config_root_is_not_guessed_at(self) -> None:
        built, recorder, roots = _service([NATIVE_PPSSPP], {})

        answer = await built.ensure_all()

        assert roots.asked == ["native:ppsspp"]
        assert answer["links"] == []
        assert recorder.applied == []

    @pytest.mark.asyncio
    async def test_the_outcome_is_reported_per_emulator(self) -> None:
        built, _, _ = _service([NATIVE_PPSSPP], {"native": "/home/deck/.config/ppsspp"})

        entry = (await built.ensure_all())["links"][0]

        assert entry["provider"] == "native"
        assert entry["status"] == "linked"
        assert entry["adopted"] == 0
        assert entry["owned_dir"] == f"{SAVES}/psp/PSP/SAVEDATA"


AZAHAR = EmulatorDef(
    id="azahar",
    display_name="Azahar",
    family="citra",
    platforms=("n3ds",),
    hints=DetectionHints(flatpak_ids=("org.azahar_emu.Azahar",)),
)

FLATPAK_AZAHAR = InstalledEmulator(definition=AZAHAR, provider="flatpak", path="org.azahar_emu.Azahar")


class TestTheDataRootedEmulator:
    @pytest.mark.asyncio
    async def test_the_sandbox_data_root_is_what_gets_pointed(self) -> None:
        """Azahar's saves sit beside its data, and the data root the reader computes is
        the sandbox's own — so the link lands inside the flatpak, not on the host."""
        built, recorder, _ = _service(
            [FLATPAK_AZAHAR],
            {"flatpak": "/home/deck/.var/app/org.azahar_emu.Azahar/config/azahar-emu"},
        )

        answer = await built.ensure_all()

        assert [entry["emulator_dir"] for entry in answer["links"]] == [
            "/home/deck/.var/app/org.azahar_emu.Azahar/data/azahar-emu/sdmc/Nintendo 3DS"
        ]
        assert recorder.applied[0].owned_dir == f"{SAVES}/3ds/sdmc/Nintendo 3DS"
