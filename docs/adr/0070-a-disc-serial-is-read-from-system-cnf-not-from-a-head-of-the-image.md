# 0070 — A disc serial is read from `SYSTEM.CNF`, not from a head of the image

**Status:** Accepted (0.48.33).
**Follows:** 0051 (a standalone emulator's folders are pointed at the plugin's tree), 0064 (a builtin
firmware reading is rooted at the app's own BIOS).

## Context

A PS2 game (Burnout) was played twice on the reference Deck. Both sessions ended with the same
line and no sync at all:

```
post_exit_sync called for rom_id=5335
post_exit_sync skipped: save_shape_unsupported
```

The save itself existed and was in the right place: PCSX2 had written
`saves/ps2/Mcd001.ps2/BASLUS-20307Burn` — the game's own folder on the bank's folder card — so the
launch redirect and the card link both worked. What failed was the answer that names the save.

A PS2 save unit is the game's folder inside the card, keyed by the disc's serial, and the serial is
read from the content file. On this image that read answered `None`, which marks the unit with
`needs=("save_id",)` and makes the answer a hole — the sync then refuses rather than carry nothing:

```
identity: None -> None
unit base: .../saves/ps2 members: [] needs: ('save_id',)
syncable: False state: hole
```

The reader took one megabyte of the image and looked for the boot line in it. Burnout's
`SYSTEM.CNF` sits at **sector 857** — 1.75 MiB in — so the boot line was not in that head, and the
reader never looked further. The file itself says where the boot configuration is: its ISO 9660
root directory holds a record for `SYSTEM.CNF` with an extent and a length. Reading that extent
answers immediately:

```
BOOT2 = cdrom0:\SLUS_203.07;1
disc_serial(cnf) -> ContentIdentity(save_id='SLUS-20307', source='PS2 BOOT2 line')
```

The same walk was already in this adapter for PSP and PS3, whose ids live inside the image's
directory tree; PS1/PS2 were the two readers that assumed a fixed head was enough.

## Decision

A PS1/PS2 identity is read from the image's head first — most discs keep the boot line there, and
one read is cheaper than a walk — and, when that answers nothing, from the `SYSTEM.CNF` the image's
own root directory names, bounded to a page.

Nothing else changes: a compressed image (`.cso`/`.zso`) still answers `None`, because a sector read
out of a compressed stream means nothing, and an image whose directory holds no `SYSTEM.CNF` still
refuses. The refusal is the honest answer; guessing a serial would point a save at another game's
card folder.

## Verification

- On the reference Deck, `Burnout (USA).iso` now answers `SLUS-20307`, its card folder
  `BASLUS-20307Burn` is matched, and the same call to `describe_unit` + `unit_answer` that answered
  `hole` answers a syncable unit rooted at the card.
- `tests/adapters/test_content_identity.py` gains an image whose `SYSTEM.CNF` sits at the measured
  sector (857, past the head) and one whose directory lists no `SYSTEM.CNF`; 47 identity tests pass.

## Consequences

- PS2 saves are no longer refused for an identity the image states but the head did not carry.
- PS1 images with a late `SYSTEM.CNF` are answered by the same fallback, which is the same file in
  the same place.
- The reader can now be asked about a disc whose boot line is past the first megabyte without
  widening the head to read more of a multi-gigabyte image.
