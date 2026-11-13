# 0058 — A card that holds nothing is a restore target

**Status:** Accepted (0.48.12)
**Follows:** 0012 (the catalogue is asked, never guessed for), 0034 (the layout is owned by the
plugin), 0057 (a PS2 save is a folder card both launches read).

## Context

GameCube was already carrying saves in one direction. With a card entry present, the answer was
`per_game_files` with the member named from the card itself
(`01-GZ2E-gczelda2.gci`), and a session-end sync uploaded it — measured on the reference Deck,
`uploaded=1` for Twilight Princess (rom 5319, region `USA`).

The other direction did not work. Deleting that one entry and syncing again answered:

```
unestablished / directory_known   gran=gci-folder   caveats=('file-names-unestablished',)
→ post_exit_sync: save_shape_unsupported
```

so the save RomM held was never fetched. The refusal was deliberate in
`domain.save_answer.fill_gci_set` — "a card with no matching entry stays refused: there is
nothing to carry yet" — and it is wrong about the case it hits. An empty card is exactly the
state a restore exists for: the folder is the place the server's save belongs, and the member
names are not needed to fetch it, because the restore reads them out of the archive it
downloads (`_restore_member_set`, and `_restore_bare_member` when RomM holds a single `.gci`
rather than a zip).

## Decision

`fill_gci_set` fills an empty (or other-coded) card as a **syncable `per_game_files` answer
with no members**: the directory stays as the answer stated it, the
`file-names-unestablished` caveat stops being true and is dropped, and the granularity stays
`gci-folder`.

The member selection is unchanged: only entries carrying this disc's game code are ever claimed
as this game's save. A GCI card folder is shared across the region, so another game's
`02-GMSE-*.gci` proves only that *this* game has not written to the card yet — it never names a
member of this game's save, and the empty target is the same answer either way.

Nothing is uploaded for a target with no members. The upload compares the members the card
names; with none, there is nothing to claim, and a folder-shaped upload would carry the whole
region's card.

## Consequences

- A fresh card restores: the server's save is fetched and its entries land under their own
  names in `GC/<region>/Card A`, which is where Dolphin reads a GCI folder.
- `save_shape_unsupported` no longer fires for GameCube on this device, in either direction.
- The rule is the same one PS2 got in 0057 for a blank card and the same one PSP's empty
  memory stick already had (`unit_answer`'s "empty but resolved"): a known directory is a
  target, and only a wrong or unknown directory is a refusal.
