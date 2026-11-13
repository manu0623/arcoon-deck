"""One-shot edit script for P3 (auto-adopt the newest server save). Deleted after it runs."""

from pathlib import Path


def edit(path: str, pairs: list[tuple[str, str]], *, required: bool = True) -> None:
    p = Path(path)
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if required:
            assert old in t, (path, old[:70])
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("patched", path)


# ── 1. the pure decision ─────────────────────────────────────────────────────
Path("py_modules/domain/save_adoption.py").write_text(
    '''"""Which server slot a freshly downloaded game adopts without being asked.

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
''',
    encoding="utf-8",
)
print("wrote py_modules/domain/save_adoption.py")

# ── 2. the wizard answers it, and can act on it ──────────────────────────────
edit(
    "py_modules/services/saves/slots/setup.py",
    [
        (
            "from domain.save_sync_state import RomSaveSyncState",
            "from domain.save_adoption import newest_named_server_slot\nfrom domain.save_sync_state import RomSaveSyncState",
        ),
        (
            '''        # Pre-computed wizard recommendation: auto-confirm the default slot only
        # when there are local saves and the server has no slots yet. Every other
        # combination needs the wizard so the user can choose. The
        # ``server_unreachable`` branch returns early above — reaching this point
        # means the server answered, so an empty ``server_slots`` is authoritative.
        recommended_action = (
            "auto_confirm_default" if (len(local_files) > 0 and len(server_slots) == 0) else "show_wizard"
        )''',
            '''        # What the callers should do without asking (ADR-0047):
        #
        # - nothing local, server has saves → adopt the newest one. There is no local
        #   save to lose, so a question here buys nothing and costs the "press Play and
        #   it is up to date" experience.
        # - local saves, nothing on the server → confirm the default slot.
        # - both sides have saves → the wizard, because that is a genuine divergence.
        #
        # The ``server_unreachable`` branch returns early above — reaching this point
        # means the server answered, so an empty ``server_slots`` is authoritative.
        auto_slot = newest_named_server_slot(server_slots)
        if not local_files and auto_slot is not None:
            recommended_action = "auto_adopt_server"
        elif len(local_files) > 0 and len(server_slots) == 0:
            recommended_action = "auto_confirm_default"
        else:
            recommended_action = "show_wizard"''',
        ),
        (
            '''            "recommended_action": recommended_action,
            "server_query_failed": False,
        }''',
            '''            "recommended_action": recommended_action,
            # Which slot "auto_adopt_server" means. ``None`` on every other action.
            "auto_slot": auto_slot if recommended_action == "auto_adopt_server" else None,
            "server_query_failed": False,
        }''',
        ),
        (
            "    async def confirm_slot_choice(",
            '''    async def auto_adopt_server_slot(self, rom_id: int) -> dict[str, Any]:
        """Confirm the slot holding the newest server save for a fresh install.

        The case this exists for: a game was just downloaded, this machine holds no save
        for it, and the server does. Adoption is a metadata flip — no migration, no
        download — so the sync that follows pulls the files, and the wizard never appears
        for a decision with nothing at stake.

        It refuses whenever a local save exists, because that is exactly the divergence
        the wizard is for. A failed server query also refuses rather than treating an
        empty list as authoritative: an unproven server view must not confirm a slot.
        """
        rom_id = int(rom_id)
        local_files = await self._loop.run_in_executor(None, self._rom_info.find_save_files, rom_id)
        if local_files:
            return {"adopted": False, "reason": "local_saves_present", "slot": None}

        game_state, device_id = await self._loop.run_in_executor(None, self._read_setup_inputs, rom_id)
        if game_state is not None and game_state.slot_confirmed and game_state.active_slot:
            return {"adopted": False, "reason": "already_confirmed", "slot": game_state.active_slot}

        try:
            server_saves: list[dict[str, Any]] = await self._loop.run_in_executor(
                None,
                lambda: self._retry.with_retry(lambda: self._romm_api.list_saves(rom_id, device_id=device_id)),
            )
        except Exception as e:
            self._logger.warning(f"auto_adopt_server_slot({rom_id}): listing server saves failed: {e}")
            return {"adopted": False, "reason": "server_unreachable", "slot": None}

        slots: dict[str | None, list[dict[str, Any]]] = {}
        for save in server_saves:
            slots.setdefault(save.get("slot"), []).append(save)
        summaries = [
            {
                "slot": slot,
                "latest_updated_at": max(
                    (s.get("updated_at", "") for s in saves),
                    key=lambda u: parse_iso_to_epoch(u) or 0.0,
                    default=None,
                ),
            }
            for slot, saves in slots.items()
        ]
        slot = newest_named_server_slot(summaries)
        if slot is None:
            return {"adopted": False, "reason": "no_named_slot", "slot": None}

        result = await self.confirm_slot_choice(rom_id, slot, migrate=False)
        return {"adopted": bool(result.get("success")), "reason": None, "slot": slot}

    async def confirm_slot_choice(''',
        ),
    ],
)

# ── 3. passthroughs ─────────────────────────────────────────────────────────
edit(
    "py_modules/services/saves/slots/service.py",
    [
        (
            "    async def confirm_slot_choice(",
            '''    async def auto_adopt_server_slot(self, rom_id: int) -> dict[str, Any]:
        """Confirm the newest server slot for a ROM with nothing local (ADR-0047)."""
        return await self._setup.auto_adopt_server_slot(rom_id)

    async def confirm_slot_choice(''',
        ),
    ],
)

edit(
    "py_modules/services/saves/service.py",
    [
        (
            '''    async def get_save_setup_info(self, rom_id: int) -> dict[str, Any]:
        """Get info needed for the first-sync setup wizard."""
        return await self._slots.get_save_setup_info(rom_id)''',
            '''    async def get_save_setup_info(self, rom_id: int) -> dict[str, Any]:
        """Get info needed for the first-sync setup wizard."""
        return await self._slots.get_save_setup_info(rom_id)

    async def auto_adopt_server_slot(self, rom_id: int) -> dict[str, Any]:
        """Confirm the newest server slot when this machine holds no save (ADR-0047)."""
        return await self._slots.auto_adopt_server_slot(rom_id)''',
        ),
    ],
)

# ── 4. the callable, and adoption on download completion ────────────────────
edit(
    "main.py",
    [
        (
            '''    async def confirm_slot_choice(''',
            '''    async def auto_adopt_server_slot(self, rom_id):
        """Adopt the newest server save slot when no local save exists (ADR-0047)."""
        return await self._save_sync_service.auto_adopt_server_slot(rom_id)

    async def confirm_slot_choice(''',
        ),
        (
            '''        if event == "download_complete" and payload is not None and payload.get("rom_id") is not None:''',
            '''        if event == "download_complete" and payload is not None and payload.get("rom_id") is not None:''',
        ),
        (
            '''        try:
            await decky.emit(event, *args)''',
            '''        if event == "download_complete" and payload is not None and payload.get("rom_id") is not None:
            # A game that just landed on the device should already be pointed at the save
            # the user last played elsewhere (ADR-0047). Scheduled rather than awaited: the
            # frontend is waiting on this event, and the launch path runs the same adoption
            # again before Play, so a slow server here cannot delay either.
            self._schedule_save_adoption(int(payload["rom_id"]))
        try:
            await decky.emit(event, *args)''',
        ),
        (
            '''    def _schedule_playtime_flush(self):''',
            '''    def _schedule_save_adoption(self, rom_id: int) -> None:
        """Run the fresh-install save adoption in the background, logging failures."""

        async def run() -> None:
            try:
                result = await self._save_sync_service.auto_adopt_server_slot(rom_id)
                self._debug_logger(f"[save-adoption] rom {rom_id}: {result}")
            except Exception as e:  # never let a save fetch break a download event
                self._debug_logger(f"[save-adoption] rom {rom_id} failed: {e}")

        self.loop.create_task(run())

    def _schedule_playtime_flush(self):''',
        ),
    ],
)

# ── 5. the feature is on by default ─────────────────────────────────────────
edit(
    "py_modules/adapters/persistence.py",
    [
        (
            '    "save_sync_enabled": False,',
            '''    # Save sync is on out of the box: the point of the app is that a game launches
    # with the save the user last played elsewhere, and a toggle that defaults off makes
    # every first launch a setup chore (ADR-0047).
    "save_sync_enabled": True,''',
        ),
    ],
)

# ── 6. the frontend follows the new recommendation ──────────────────────────
edit(
    "src/types/saves.ts",
    [
        (
            '  recommended_action: "auto_confirm_default" | "show_wizard" | "server_unreachable" | "not_found";',
            '''  // "auto_adopt_server" (ADR-0047) means this machine holds no save and the server
  // does: confirm ``auto_slot`` instead of asking. It is a recommendation, not a
  // guarantee — a caller that skips it still launches on the local (empty) state.
  recommended_action:
    | "auto_confirm_default"
    | "auto_adopt_server"
    | "show_wizard"
    | "server_unreachable"
    | "not_found";
  // Which slot "auto_adopt_server" means; null on every other action.
  auto_slot?: string | null;''',
        ),
    ],
)

edit(
    "src/utils/saveSetup.ts",
    [
        (
            '''  if (info.recommended_action === "auto_confirm_default") {
    return { kind: "auto_confirm", slot: info.default_slot };
  }''',
            '''  if (info.recommended_action === "auto_confirm_default") {
    return { kind: "auto_confirm", slot: info.default_slot };
  }
  // Nothing local, saves on the server: adopt the newest one (ADR-0047). This is a
  // metadata flip on the backend's side — the sync that follows pulls the files — so
  // the first launch is current instead of asking a question with nothing at stake.
  if (info.recommended_action === "auto_adopt_server") {
    return { kind: "auto_confirm", slot: info.auto_slot ?? info.default_slot };
  }''',
        ),
    ],
)
print("backend and frontend done")
