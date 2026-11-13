# 0060 — A Wii save is a title directory in Dolphin's user tree

**Status:** Accepted (0.48.17)
**Follows:** 0034 (the layout is owned by the plugin), 0043 (an owned launch states its own
save), 0058 (a card that holds nothing is a restore target).

## Context

Wii answered `unestablished` for every ROM — the save layer asked a catalogue that has no
Dolphin entry on this device, while Dolphin itself was writing the save. What it wrote was
measured on the reference Deck by playing a Wii game and saving:

```
~/.var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu/Wii/title/
    00010000/53423445/data/GameData.bin
    00010000/53423445/data/banner.bin
    00000001/00000002/data/{play_rec.dat,state.dat,setting.txt}   ← the console's own settings
```

Three facts come out of that tree.

- **The directory name is the disc's game code in hex.** `53423445` is `SB4E`, which is what
  the ROM's own `.rvz` header states at 0x58 (`SB4E01`, measured for Mario Galaxy 2; the New
  Super Mario Bros Wii file states `SMNE01` and Dolphin keeps that one under `534d4e45`).
- **The save is `data/`, beside a `content/title.tmd` the emulator writes with it.** The two
  files in `data/` are the game's progress; the console-level titles (`00000001/…`) are not a
  game's save at all and must never be carried per ROM.
- **The tree is the flatpak's own data directory, not a folder the plugin chose.** The baked
  launch for these Wii shortcuts is `/usr/bin/flatpak run org.DolphinEmu.dolphin-emu -b -e
  "<rom>"` — measured, it carries no `-u`, so the emulator's compiled-in default decides. That
  default is where the session actually wrote, which is what an answer has to state.

## Decision

Wii is a **managed platform** in the layout manifest (`scripts/provision_layout.py --adopt
wii=…`), with:

```json
"wii": {
  "emulator": "Dolphin (Standalone)",
  "launch": ["%EMULATOR_DOLPHIN%", "-b", "-e", "%ROM%"],
  "save_dir": "<adopted>/<save_id>/data",
  "save_unit": "title-dir",
  "needs": ["save_id"]
}
```

The adopted directory is `…/Wii/title/00010000` — the category Dolphin files disc titles
under. `<save_id>` is filled from the ROM's own header by a new
`IdentityKind.WII_GAME_CODE`: the four-character code read at 0x00 of a bare disc or 0x58 of
an `.rvz`, spelled as its ASCII bytes in hex (`wii_title_dirname`), which is the directory
name Dolphin uses.

The unit is `data/` rather than the whole title folder. A `title-dir` unit is named from one
flat directory's listing, and restoring into `data/` puts back exactly the files the game
reads; `content/title.tmd` is the emulator's own record that it installed the title, and a
sync that overwrote it with another device's copy would be carrying metadata as progress.

## Consequences

- A Wii save syncs in both directions: `<rom>.zip` holding this title's `data/` files up, the
  same archive extracted back into `…/<title id>/data` down.
- The console-level titles under `Wii/title/00000001` are never touched: they belong to no
  ROM, and the manifest names one path per game.
- WiiWare titles, which Dolphin files under `00010001`, are **not** covered: the measured
  tree is a disc title, and guessing the second category from the first is the sort of path
  this project refuses to invent.
- `user_dir_for("wii")` still returns `<saves>/wii/User`, and it is still unused: the pin is
  only applied to a command that carries an ES-DE emulator token, and this build bakes a
  direct flatpak command. The gap is real and recorded here — pointing these launches is the
  next cut, and the answer above follows the emulator rather than the wish until then.
