"""The two catalogue tiers, and which one answers first under each runtime (ADR-0045)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from adapters.owned_catalogue import FallbackCatalogueAdapter, OwnedCatalogueAdapter

if TYPE_CHECKING:
    from domain.emulator_commands import EmulatorInvocation


class FakeSource:
    """One catalogue tier that remembers what it was asked."""

    def __init__(self, *, options: dict | None = None, core: tuple[str | None, str | None] = (None, None)) -> None:
        self.calls: list[str] = []
        self._options = options or {"available": True, "options": []}
        self._core = core

    def reset_cache(self) -> None:  # pragma: no cover - the composite forwards this
        pass

    def get_emulator_options(self, system_name: str) -> dict:
        self.calls.append(f"options:{system_name}")
        return self._options

    def get_default_emulator(self, system_name: str) -> EmulatorInvocation | None:
        self.calls.append(f"default:{system_name}")
        return None

    def get_active_core(self, system_name: str) -> tuple[str | None, str | None]:
        self.calls.append(f"core:{system_name}")
        return self._core

    def get_supported_extensions(self, system_name: str) -> frozenset[str]:
        self.calls.append(f"ext:{system_name}")
        return frozenset()

    def is_known_system(self, system_name: str) -> bool | None:
        self.calls.append(f"known:{system_name}")
        return None


def _composite(*, owned_first: bool, owned: FakeSource, esde: FakeSource) -> FallbackCatalogueAdapter:
    return FallbackCatalogueAdapter(
        esde=esde,
        owned=owned,  # type: ignore[arg-type]  # the composite only calls the protocol methods
        owned_first=lambda: owned_first,
    )


class TestWhichTierAnswersFirst:
    def test_a_builtin_runtime_asks_its_own_inventory_first(self) -> None:
        owned = FakeSource(options={"available": True, "options": [{"label": "mgba"}]})
        esde = FakeSource()

        answer = _composite(owned_first=True, owned=owned, esde=esde).get_emulator_options("gba")

        assert answer["options"] == [{"label": "mgba"}]
        assert owned.calls == ["options:gba"]
        assert esde.calls == []

    def test_a_retrodeck_runtime_asks_es_de_first(self) -> None:
        owned = FakeSource(options={"available": True, "options": [{"label": "mgba"}]})
        esde = FakeSource(options={"available": True, "options": [{"label": "RetroDECK mgba"}]})

        answer = _composite(owned_first=False, owned=owned, esde=esde).get_emulator_options("gba")

        assert answer["options"] == [{"label": "RetroDECK mgba"}]
        assert owned.calls == []

    def test_the_order_is_read_per_call_not_frozen_at_construction(self) -> None:
        # Switching the runtime in Settings must change the answer without a restart.
        owned = FakeSource(options={"available": True, "options": [{"label": "mgba"}]})
        esde = FakeSource(options={"available": True, "options": [{"label": "RetroDECK mgba"}]})
        state = {"owned_first": True}
        composite = FallbackCatalogueAdapter(
            esde=esde,
            owned=owned,  # type: ignore[arg-type]
            owned_first=lambda: state["owned_first"],
        )

        assert composite.get_emulator_options("gba")["options"] == [{"label": "mgba"}]
        state["owned_first"] = False
        assert composite.get_emulator_options("gba")["options"] == [{"label": "RetroDECK mgba"}]

    def test_an_empty_first_answer_falls_through_to_the_second_tier(self) -> None:
        owned = FakeSource(options={"available": True, "options": []})
        esde = FakeSource(options={"available": True, "options": [{"label": "RetroDECK mgba"}]})

        answer = _composite(owned_first=True, owned=owned, esde=esde).get_emulator_options("gba")

        assert answer["options"] == [{"label": "RetroDECK mgba"}]

    def test_a_core_only_one_tier_knows_is_still_found(self) -> None:
        owned = FakeSource(core=(None, None))
        esde = FakeSource(core=("/cores/bsnes.so", "bsnes"))

        found = _composite(owned_first=True, owned=owned, esde=esde).get_active_core("snes")

        assert found == ("/cores/bsnes.so", "bsnes")


def test_the_adapter_is_constructible_with_real_owned_inventory(tmp_path) -> None:
    """The composite never needs the real tier to answer a question it was not asked."""
    owned = OwnedCatalogueAdapter(
        plugin_dir=str(tmp_path),
        user_home="/home/deck",
        logger=logging.getLogger("test"),
        cores_dir=lambda: "/cores",
        runtime_is_builtin=lambda: True,
    )
    composite = FallbackCatalogueAdapter(esde=FakeSource(), owned=owned, owned_first=lambda: True)

    composite.reset_cache()
