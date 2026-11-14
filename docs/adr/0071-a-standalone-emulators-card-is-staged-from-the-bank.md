# 0071 — A standalone emulator's memory card is staged from the bank, one game at a time

**Status:** Accepted (0.48.34).
**Follows:** 0051 (a standalone emulator's save folder is linked to the plugin's tree), 0069 (a
standalone emulator's BIOS folder is pointed at the app's tree), 0070 (a disc serial is read from
`SYSTEM.CNF`).

## Context

A PS1 game played through DuckStation stopped reaching the server. Every session ended:

```
post_exit_sync called for rom_id=5416
post_exit_sync skipped: save_shape_unsupported
```

Nothing was failing on the server. The plugin had no answer for a save written by DuckStation at
all, and DuckStation's own console said why:

```
[MemoryCards] Card1Type = PerGameTitle
Directory = /run/media/deck/SR01T/Emulation/saves/duckstation/saves
I/System: Memory Card 1: …/saves/duckstation/saves/Disney's Tarzan (USA)_1.mcd
```

Two facts, both measured:

- DuckStation's cards live in a folder its **settings** name, not one the plugin could assume.
- With its default `PerGameTitle`, the card's file name comes from the game's title in
  DuckStation's own database — `Disney's Tarzan (USA)_1.mcd`, not the ROM's name and not the
  playlist's. No rule the plugin could derive would find that file again, so nothing could be
  answered for it.

The same launch with `Card1Type = Shared` opened `<Directory>/shared_card_1.mcd`: one fixed name,
whatever the game. That is the lever.

Meanwhile the bank already held the game's save as `saves/psx/Disney's Tarzan.srm` — one 128 KiB
memory-card image, the same format DuckStation writes as `.mcd`, produced by the plugin's own
RetroArch launch and carried by the sync until the emulator changed.

## Decision

The plugin owns the card folder and the card:

- `[MemoryCards] Directory` is pointed at `<saves>/psx`, and `[MemoryCards] Card1Type` is set to
  `Shared`, whose file name is fixed;
- before a launch the game's bank card (`<stem>.srm`) is copied over `shared_card_1.mcd`, and a
  stale slot is cleared when the bank has no card for that game — so a game with no save opens an
  empty card rather than the previous game's;
- after the session the slot is copied back into `<stem>.srm` and removed, and only then does the
  post-exit sync run, so the upload carries this session's save.

`domain/emulator_card_stage.py` holds the declared emulator and its measured keys. Only an
emulator in that table is touched, and only when the launch the machine resolves for the ROM is
that emulator; a ROM launched by a core keeps the launch-redirect path it already had.

The bank file keeps the `.srm` name because both formats are the same card image and every
existing PS1 answer, layout and synced file already uses it: staging translates the name, not the
shape.

## Verification

- On the reference Deck, `Card1Type = Shared` opened `shared_card_1.mcd` (measured), while the
  default per-game-title type opened `Disney's Tarzan (USA)_1.mcd`.
- `tests/domain/test_emulator_card_stage.py` pins the rule and the two card paths;
  `tests/adapters/test_emulator_card_stage.py` pins the two-key settings write (through
  `lib.ini_lines`, so the rest of `settings.ini` survives) and both moves, including clearing a
  stale slot.
- After deployment the startup pass points DuckStation at `<saves>/psx`; the first launch stages
  the existing `.srm` and the post-exit pass adopts it back.

## Consequences

- A PS1 game played in DuckStation now syncs the same file it synced when played by the plugin's
  RetroArch launch, so switching emulator no longer strands the save.
- DuckStation's own per-game cards are no longer used while the plugin is installed: its settings
  say `Shared`, and its tile launches stage the plugin's card. A card DuckStation wrote before
  this change stays where it is and is not adopted automatically.
- Two games never share the staged slot: it is emptied on adopt and cleared on stage.
