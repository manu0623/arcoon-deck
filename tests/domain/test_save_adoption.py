"""Which slot a fresh install adopts without asking (ADR-0047)."""

from __future__ import annotations

from domain.save_adoption import newest_named_server_slot


def _slot(name: object, updated: object) -> dict[str, object]:
    return {"slot": name, "latest_updated_at": updated}


class TestWhichSlotIsAdopted:
    def test_the_newest_slot_wins(self) -> None:
        slots = [
            _slot("desktop", "2024-01-01T10:00:00Z"),
            _slot("autosave", "2024-06-01T10:00:00Z"),
            _slot("old", "2023-01-01T10:00:00Z"),
        ]

        assert newest_named_server_slot(slots) == "autosave"

    def test_the_instant_decides_not_the_string(self) -> None:
        # 13:00+02:00 is a LATER string but an EARLIER instant than 12:00Z.
        slots = [_slot("a", "2024-01-01T13:00:00+02:00"), _slot("b", "2024-01-01T12:00:00Z")]

        assert newest_named_server_slot(slots) == "b"

    def test_a_legacy_slot_is_never_adopted(self) -> None:
        # slot:null is a migration source and cannot be confirmed as a target.
        assert newest_named_server_slot([_slot(None, "2024-06-01T10:00:00Z")]) is None

    def test_a_named_slot_beats_an_unnameable_one(self) -> None:
        slots = [_slot(None, "2024-06-01T10:00:00Z"), _slot("named", "2024-01-01T10:00:00Z")]

        assert newest_named_server_slot(slots) == "named"

    def test_no_slots_means_nothing_to_adopt(self) -> None:
        assert newest_named_server_slot([]) is None

    def test_an_unparseable_timestamp_loses_to_a_parseable_one(self) -> None:
        slots = [_slot("bad", "not a date"), _slot("good", "2024-01-01T10:00:00Z")]

        assert newest_named_server_slot(slots) == "good"

    def test_a_tie_goes_to_the_first_listed_slot(self) -> None:
        slots = [_slot("first", "2024-01-01T10:00:00Z"), _slot("second", "2024-01-01T10:00:00Z")]

        assert newest_named_server_slot(slots) == "first"
