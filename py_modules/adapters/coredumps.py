"""Reading ``coredumpctl`` for dumps since an instant.

The only trace a signal death leaves that a non-root reader can see: systemd's own
scope log records a flatpak's ``Started`` and ``Consumed`` lines and no exit status at
all. ``coredumpctl --json=short list --since @<epoch>`` answers one JSON row per dump
(``time`` in microseconds, ``pid``, ``sig``, ``exe``, ``corefile``), and the listing is
readable without elevation — the *contents* are not, which is why nothing here tries to
open a core file.

Every way this question can go unanswered — no ``coredumpctl`` on the machine, a
timeout, a non-zero exit, output that is not the JSON this reads — returns ``None``,
never ``()``. An empty tuple means "asked, and there were no dumps"; ``None`` means
"could not ask", and the caller must not read that as a clean exit.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from domain.emulator_crash import Coredump, parse_coredumps

if TYPE_CHECKING:
    import logging

#: A listing is a local journal query. Seconds, not minutes: this runs at session end,
#: while the frontend waits for the finalize round-trip.
_LIST_TIMEOUT_SECONDS = 5


class CoredumpAdapter:
    """Lists core dumps recorded since an instant, synchronously."""

    def __init__(self, *, logger: logging.Logger) -> None:
        self._logger = logger

    def read_since(self, since_us: int) -> tuple[Coredump, ...] | None:
        """Dumps recorded at or after *since_us*, or ``None`` when the question failed."""
        argv = [
            "coredumpctl",
            "--no-pager",
            "--since",
            f"@{since_us // 1_000_000}",
            "--json=short",
            "list",
        ]
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=_LIST_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._logger.debug(f"coredumps: could not read the journal: {exc}")
            return None
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip().splitlines()
            self._logger.debug(f"coredumps: coredumpctl exited {completed.returncode}: {detail[-1] if detail else ''}")
            return None
        return parse_coredumps(completed.stdout)
