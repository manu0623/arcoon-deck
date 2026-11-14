# 0072 — A PS2 save that arrives as a card image is written into the bank's folder card

- **Status:** Accepted (0.48.35)
- **Supersedes:** nothing. Extends 0048's card rule to the other client's shape.

## Context

A PS2 memory card has two on-disk shapes, and this plugin launches from one of them:

- the **file card** — one 8,650,752-byte image holding every game's saves;
- the **folder card** — a directory (`Mcd001.ps2/`) with `_pcsx2_superblock` and one folder
  per game, named after the disc's serial and the game's own title (`BASLUS-20307Burn`).

The bank keeps a folder card, converts a file card into one at startup, and uploads the
game's own folder as one archive (`<rom name>.zip`). That is this device's unit, and the
sync matrix only places files its answer carries.

Another client uploads the other shape. Measured on the reference server, rom 5338
(Grand Theft Auto: Liberty City Stories):

| save | emulator key | received (UTC) | shape |
|---|---|---|---|
| 479 | `pcsx2` | 05:38:48 | `… (USA).zip`, 77 KB — this Deck |
| 480 | `armsx2` | 05:47:57 | `… (USA).ps2`, 8,650,752 B |
| 481 | `aethersx2` | 08:30:10 | `autosave […].ps2`, 8,650,752 B |

The Deck's own record for that ROM read `latest_updated_at: 08:30:10` — it saw the newest
save correctly. It still launched with the 00:38 save, because a `.ps2` target is not a
file the PS2 answer carries: `iter_matrix_outcomes` logged `server save '… .ps2' is not a
file this emulator's answer carries — leaving both copies alone` and downloaded nothing.
The same line appears for rom 5365 (Sly Cooper) and rom 5335 (Burnout).

The image is not a foreign format. `read_file_card` already parses it — measured on the
handheld's file for rom 5338, which yielded one folder, `BASLUS-20307Burn`, with five
files, the same folder the bank's card holds. Nothing needs translating; only the shape
had to be noticed.

## Decision

Before a launch, if the **newest** save in the ROM's slot is a card image, the plugin
downloads it, reads the game's folder out of it, backs up the files it is about to replace
through the sync layer's quarantine, and writes them into the card folder the launch reads
(`saves/ps2/<card>/<game folder>/`).

Three rules make that safe:

1. **Only the newest save in the slot** — checked across every emulator's rows, because a
   handheld uploads under its own key. A card older than what this device already has is
   history; writing it would roll the player back.
2. **Only the ordinary slot.** `autosave` and the no-slot bucket qualify; a named slot is a
   deliberate checkpoint and is never overwritten by an import.
3. **Bytes compared first, backup first.** A card whose files already match is a no-op
   rather than an 8 MB copy per launch, and a file whose backup fails is not written.

The folder is chosen by name (`read_file_card` → `select_folder`): a card holding exactly
one folder is that game's save; a card holding several and none of them the expected name
is ambiguous and refused, since guessing writes one game's progress over another's.

### The sync decides, not a hook before it

The first version applied the newest card in the plugin's own pre-launch hook, before the
sync looked at the bank. Measured on the reference Deck: the imported bytes then looked
like an unexplained local change while the server also had a newer save, so the sync raised
a conflict between a save and itself — reporting the server's own save as "local" — and
"keep local" was refused as stale on every retry. So the row is admitted as a target by
`RomInfoService.server_target_filter` and the matrix downloads it like any other, which
records the applied bytes as this device's copy of that save. Which save wins stays the
sync's decision, and the import cannot disagree with the bookkeeping that follows it.

### Which folder, and which card

A PS2 answer's directory is the **card folder** (`…/saves/ps2/Mcd001.ps2`), and every member
carries the game's folder as its first path segment (`BASLUS-21423GTA30001/icon.sys`). So
the import is told the card and takes the folder from the answer's own members; a card
holding several games is read by that name, and a card holding one game needs no name. A
restore that arrives without an answer (a bare member in the matrix) can only be placed
when its card holds a single game.

### Restoring an older version, and the PUT that follows

The version switch restores the chosen save and then re-sends it so RomM bumps
`updated_at`. For a unit RomM carries as one archive there is no local file at the unit's
name — the restore wrote the folder the archive is packed from — so the switch downloads
the chosen version once more beside it and sends that copy. Without this the switch ended
in `PUT to bump updated_at failed … No such file or directory` and reported "restored, but
the server didn't update" while the save itself had already been applied.

## Consequences

- Android → Deck works for PS2 saves: the newest card becomes the save the launch reads,
  and the post-exit sync uploads it back in this plugin's own unit as before.
- Deck → Android is unchanged. What this plugin uploads stays a `<rom name>.zip`, so the
  direction that already worked keeps working; changing it to a card image is a separate
  decision that has to be measured against the receiving client first.
- The import is best-effort: a card that cannot be downloaded, read or backed up logs and
  leaves the ordinary sync to decide, so a launch is never blocked by it.
- The card's own bytes are read once per cycle, not per launch: after the import, this
  device's upload is the newest save in the slot, so the next launch sees a `.zip` and the
  import does nothing.
- A restoring device and a launching device take the same path: the version switch uses the
  same import, so "restore this version" no longer writes an 8 MB card image into the card
  folder as if it were a save.
