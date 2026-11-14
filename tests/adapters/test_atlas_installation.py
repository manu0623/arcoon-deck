"""Which emulator arrangement answers a question — the chooser every atlas seam shares.

What is under test is the choice, not the reading: detection labels the
arrangements it found, the runtime in force decides which of them is asked, and a
marker a removed flatpak left behind is not one of the candidates. The resolver's
own answers are upstream's and are tested there.

The fake handle carries nothing but ``kind`` — the one field the chooser reads —
because a chooser that reached further would be choosing on a reading rather than
on an arrangement's identity.
"""

from __future__ import annotations

from adapters.atlas_installation import first_detected_installation, installation_for_runtime


class _Handle:
    """A detected arrangement, by kind only."""

    def __init__(self, kind: str) -> None:
        self.kind = kind


def _found(*handles: _Handle):
    def find(home: str) -> list[_Handle]:
        assert home == "/home/deck"
        return list(handles)

    return find


class TestTheAppOwnRuntime:
    """Under the app's own runtime a RetroDECK handle outlives the flatpak that wrote it."""

    def test_a_retrodeck_handle_is_passed_over(self):
        """Measured on the reference Deck: the marker present, no RetroDECK installed.

        The handle that marker yields answered zero cores, zero requirements and zero
        systems for every question, while naming ``~/retrodeck`` directories nothing
        reads — and the RetroArch flatpak beside it answered 19 cores.
        """
        dead = _Handle("retrodeck")
        live = _Handle("bare_retroarch_flatpak")

        chosen = installation_for_runtime("/home/deck", builtin=True, find=_found(dead, live))

        assert chosen is live

    def test_no_arrangement_left_answers_none(self):
        """Nothing to ask is unresolved, never "nothing is wanted"."""
        assert installation_for_runtime("/home/deck", builtin=True, find=_found(_Handle("retrodeck"))) is None

    def test_an_empty_detection_answers_none(self):
        """A machine with no arrangement at all is the same answer, not an error."""
        assert installation_for_runtime("/home/deck", builtin=True, find=_found()) is None

    def test_detections_own_order_still_decides_among_the_survivors(self):
        """Offering several arrangements is #918; this does not reorder them."""
        first = _Handle("bare_retroarch_flatpak")
        second = _Handle("bare_retroarch_native")

        assert installation_for_runtime("/home/deck", builtin=True, find=_found(first, second)) is first


class TestRetroDeckDrives:
    """Under RetroDECK its catalogue is the only place its own core labels exist."""

    def test_retrodeck_answers_first(self):
        deck = _Handle("retrodeck")
        other = _Handle("bare_retroarch_flatpak")

        assert installation_for_runtime("/home/deck", builtin=False, find=_found(deck, other)) is deck

    def test_a_missing_retrodeck_handle_still_answers_the_next_one(self):
        """A chosen runtime is honoured even where detection would not have offered it."""
        other = _Handle("bare_retroarch_flatpak")

        assert installation_for_runtime("/home/deck", builtin=False, find=_found(other)) is other


class TestThePlainChoice:
    """``first_detected_installation`` is the unqualified order, and stays that."""

    def test_the_first_detected_arrangement_answers(self):
        deck = _Handle("retrodeck")

        assert first_detected_installation("/home/deck", find=_found(deck, _Handle("bare_retroarch_flatpak"))) is deck

    def test_nothing_detected_answers_none(self):
        assert first_detected_installation("/home/deck", find=_found()) is None
