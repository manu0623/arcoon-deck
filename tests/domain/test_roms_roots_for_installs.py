"""Every roms root an install may sit under, today's first (ADR-0046)."""

from __future__ import annotations

from domain.runtime import RuntimeMode, roms_roots_for_installs

HOME = "/home/deck"
DATA_DIR = "/home/deck/.local/share/romm-tender"
EMUDECK_ROMS = f"{HOME}/Emulation/roms"
APP_ROMS = f"{DATA_DIR}/roms"
RETRODECK_ROMS = f"{HOME}/retrodeck/roms"


def _roots(
    settings: dict[str, object] | None = None,
    *,
    data_dir: str = DATA_DIR,
    mode: RuntimeMode = RuntimeMode.BUILTIN,
) -> tuple[str, ...]:
    return roms_roots_for_installs(
        mode=mode,
        home=HOME,
        retrodeck_roots={
            "roms": RETRODECK_ROMS,
            "saves": f"{HOME}/retrodeck/saves",
            "bios": f"{HOME}/retrodeck/bios",
            "states": f"{HOME}/retrodeck/states",
        },
        settings=settings,
        data_dir=data_dir,
    )


class TestWhatDeletionMayTouch:
    def test_the_current_root_comes_first(self) -> None:
        assert _roots({"structure": "app"})[0] == APP_ROMS
        assert _roots({"structure": "emudeck"})[0] == EMUDECK_ROMS

    def test_the_tree_a_previous_structure_wrote_is_still_offered(self) -> None:
        """A switch to the app tree leaves EmuDeck-era installs where they are."""
        roots = _roots({"structure": "app"})

        assert EMUDECK_ROMS in roots
        assert APP_ROMS in roots

    def test_switching_the_other_way_keeps_the_app_tree_reachable(self) -> None:
        roots = _roots({"structure": "emudeck"})

        assert APP_ROMS in roots

    def test_a_per_root_override_is_the_current_answer_but_not_the_only_one(self) -> None:
        roots = _roots({"structure": "app", "roms_dir": "/mnt/sd/roms"})

        assert roots[0] == "/mnt/sd/roms"
        # The trees an older choice wrote to are still accepted for deletion.
        assert EMUDECK_ROMS in roots

    def test_a_retrodeck_runtime_still_offers_the_owned_trees(self) -> None:
        roots = _roots({"structure": "app"}, mode=RuntimeMode.RETRODECK)

        assert roots[0] == RETRODECK_ROMS
        assert EMUDECK_ROMS in roots

    def test_no_data_directory_leaves_no_app_tree(self) -> None:
        roots = _roots({"structure": "app"}, data_dir="")

        assert all("romm-tender" not in root for root in roots)
        assert EMUDECK_ROMS in roots

    def test_roots_are_not_repeated(self) -> None:
        roots = _roots({"structure": "emudeck"})

        assert len(roots) == len(set(roots))
