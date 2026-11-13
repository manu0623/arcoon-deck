# ADR-0053 — A PS3 save folder is named after the disc, not the file

**Status:** accepted (identity reader only; the link is not wired yet)

## The problem

PS3 saves live in one flat directory — `dev_hdd0/home/<uid>/savedata` — and each game's
folder is named after its **title id**, never after the game. Measured on the reference
Deck:

```
BCES00301_SAVE_1         BCUS98111-AUTOSAVE      BCUS98111-USERDATA
BCUS98247_SAVE_SLOT_00000  BLUS30443DEMONSS005   …
```

The library row says `3D Dot Game Heroes (USA).iso`. Nothing in the row, the filename or the
install path carries `BLUS…`, so a save layer that reads rows alone can see six other games'
saves and no way to pick its own. Reading the file name is therefore not an option; the game
has to be asked.

## The decision

**Ask the game.** The title id is in `PS3_GAME/PARAM.SFO` inside the image, and both shapes
a PS3 install takes can be read without a third-party library:

- **Folder boot** — `PS3_GAME/PARAM.SFO` sits beside the boot file on disk.
- **Disc image** — the reference image is a plain ISO9660 tree whose root lists
  `PS3_DISC.SFB`, `PS3_GAME` and `PS3_UPDATE` (PVD at sector 16, `PS3_GAME` at extent 293).
  One level down is `PARAM.SFO`.

Parsing lives in `domain/ps3_title_id.py` and takes a `read_at(offset, length)` callable, so
the byte-level work is testable against synthetic bytes and the file handle stays in
`services/rom_title_id.py`. A `TITLE_ID` value is accepted only as four letters and five
digits; anything else is refused rather than normalised into a guess.

**UDF-only images answer nothing.** The reference image carries ISO9660 as well, so the plain
walk covers it; an image with no `CD001` descriptor returns `None` and the save layer will
report that it cannot place the game rather than inventing a folder.

## What is still missing

The link itself has two unmet prerequisites, both measured on this Deck:

1. **The data root.** RPCS3's data here is `~/Emulation/storage/rpcs3` (EmuDeck's `storage/`
   convention), not `~/.config/rpcs3` — which does not exist. `SavePoint` resolves against a
   config or data root the registry computes for `native`/`flatpak` providers, and neither
   names that directory.
2. **The user id.** `dev_hdd0/home/00000001` — one directory, but not a constant.

Until both are answered, PS3 stays out of `_SAVE_POINTS`; the reader is shipped because it is
the part that cannot change once measured, and because a save layer that guesses a title id is
worse than one that refuses.

## Consequences

- A PS3 game's identity is read from content, once per sync, not stored in the row.
- Citra/Lime3DS-style caution applies to PS3 too: no family enters `_SAVE_POINTS` until its
  directory was seen on a device and its identity can be read.
