"""Which server slot a freshly downloaded game adopts without being asked.

The end state a download should reach is "press Play and the game is up to date". The
only thing standing between an install and that is the slot wizard, which exists for a
real reason: a machine that already holds a save and a server that holds a different one
is a decision only the user can make. A machine that holds **nothing** is not that case —
there is no local save to lose — so the newest server save is the answer, not a question.

Only named slots qualify. The legacy ``slot: null`` bucket is a migration *source* and
cannot be confirmed as a target, so adopting it would fail at the step after this one;
:func:`newest_named_server_slot` returns ``None`` there and the wizard keeps its job.

Pure compute: stdlib only, no I/O.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from domain.iso_time import parse_iso_to_epoch

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def newest_named_server_slot(server_slots: Sequence[Mapping[str, Any]]) -> str | None:
    """The named slot holding the newest save, or ``None`` when adoption would guess.

    *server_slots* is the wizard's own slot summary — ``{"slot", "latest_updated_at"}``
    per slot. A slot whose timestamp cannot be parsed loses to one that can, and a tie
    goes to the slot listed first, so the answer is stable across identical inputs.
    """
    best: tuple[float, int, str] | None = None
    for index, info in enumerate(server_slots):
        slot = info.get("slot")
        if not isinstance(slot, str) or not slot.strip():
            continue
        updated = info.get("latest_updated_at")
        epoch = parse_iso_to_epoch(updated) if isinstance(updated, str) else None
        score = (epoch or 0.0, -index, slot)
        if best is None or score > best:
            best = score
    return best[2] if best is not None else None
