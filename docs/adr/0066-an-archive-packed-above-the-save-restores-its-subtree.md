# 0066 — An archive packed above the save restores the subtree the save owns

**Status:** Accepted (0.48.27)
**Related:** 0048 (a PSP save is the folder its disc id names), 0060 (a Wii save is a title directory)

## Context

The report read like a race: a save uploaded from this Deck, played on another console, and then
the pre-launch sync on the Deck downloaded the newer save while the game started a new one. The
timeline says it was not a race. From `~/homebrew/logs/romm-tender/2026-11-13 19.36.08.log`
(rom 7200, "The Legend of Zelda: Link's Awakening", save id `01006BB00C6F0000`):

```
19:44:06,790  do_sync_rom_saves(7200): local … .zip -> Download
19:44:06,878  Restored 6 card entries into …/93543B1D30E2AEB87D0F28AE30D83730/01006BB00C6F0000
19:44:06,960  [FE] CustomPlayButton: preLaunchSync result: synced=1 conflicts=0 success=true
19:44:07,594  Session start: romId=7200
```

The download finished 700 ms before the session began, and the backend reported it complete. The
bytes were simply in the wrong place. What the restore left on disk:

```
…/93543B1D30E2AEB87D0F28AE30D83730/01006BB00C6F0000/           ← Eden's title folder
  .romm-backup/savedata1_20261114_004406.bin                    ← the local save, quarantined
  01006BB00C6F0000/savedata0.bin, savedata1.bin, …              ← the download, one level too deep
```

Eden reads `nand/user/save/<profile>/<title>/` itself, found it empty of files, and offered a new
game. The nesting came from the archive, not from the restore target: read back from RomM, the save
this Deck uploaded and the save the other device uploaded are the same six files under different
names —

```
456 (this Deck, 19:42:47)   savedata1.bin, screenshot0.bin, …
457 (other device)          01006BB00C6F0000/savedata1.bin, 01006BB00C6F0000/screenshot0.bin, …
```

`prepare_packed_unit` packs `answer.directory` (the title folder), so our archive names the folder's
own contents — a flat set. A client that packs the folder *itself* writes every member under the
folder's name, and those members are relative to the folder's **parent**. The restore extracted them
into `restore_dir` — the title folder — as they were, which recreated the folder inside itself.

Nothing about the emulator's path was wrong, and nothing about the launch was early, so no delay is
part of this change.

### The same shape one level higher: Wii

Inspection of every extraction family on the same server found the identical fault on Wii, where the
unit is the files inside `<title>/data` and the archive can be packed from the title folder itself:

```
rom 6938, newest save: 534d4e45/data/wiimj2d.sav
                       534d4e45/data/banner.bin
                       534d4e45/content/title.tmd        ← Dolphin's installed title metadata
destination:           …/Wii/title/00010000/534d4e45/data
```

Restoring that into the destination writes `…/534d4e45/data/534d4e45/data/wiimj2d.sav`; Dolphin
reads `…/534d4e45/data/` and offers a new save, the same symptom on a different platform. Unlike the
Switch case, the heading here names the destination's **parent**, so a rule that only drops a
heading equal to the destination's own name does not reach it. And the fix cannot be "unpack into the
title folder": `content/title.tmd` is the emulator's installed title, not the game's save, and
writing it would replace emulator metadata with a save file.

## Decision

A restore aligns the archive's heading with the destination's own path, places the members that land
inside it, and refuses the rest.

1. `domain.save_bank.place_archive_members(members, destination)` answers, for an archive whose
   members all sit under ONE heading, the name each member takes under *destination*, plus the
   members that fall outside it (`ArchivePlacement.placements` / `.refused`). The heading is matched
   against the destination's components, deepest occurrence first, and the components below it must
   be the start of every member's tail — so `534d4e45/data/wiimj2d.sav` against
   `…/534d4e45/data` places `wiimj2d.sav`, and `534d4e45/content/title.tmd` is refused.
2. A flat archive (the shape this plugin packs), a mixed one, or an archive headed by a name that is
   not on the destination's path (PSP's `ULUS10064DATA00/` sits *inside* `SAVEDATA`, not above it) is
   read exactly as before: members into the destination, whole.
   An archive that IS packed above the destination but holds nothing that fits it comes back with no
   placements and every member refused. It is never read flat: measured on the reference Deck while
   verifying the deployed build, rom 6938's newest save in its active `autosave` slot holds only
   `534d4e45/content/title.tmd`, and reading that flat wrote Dolphin's title metadata into the save
   folder.
3. `SaveFileStore.extract_archive(..., placements=…)` writes only the placed members, under their
   placed names, and skips everything else. Those names are still resolved against the destination
   through the existing realpath/symlink guard, so a placement can never write outside it. The names
   it returns are the ones that landed, so the per-file baselines name the real paths.
4. `MatrixExecutor._restore_member_set` quarantines what it is about to overwrite before the bytes
   move (unchanged), logs how many members it kept when an archive carried more, and records a
   baseline per restored name.

## Consequences

- The Switch save from the other console restores into `<title>/` and `<title>/<title>/` is never
  created. Verified against RomM save 457: all six flat files are byte-identical to the archive.
- Wii's title-folder archive restores `data/` into `<title>/data/` and never writes `content/`, so
  Dolphin's installed title metadata is left untouched.
- Our own uploads stay flat, so nothing about the archive the plugin sends changes, and a save that
  round-trips through this build needs no placement at all.
- Archives packed two or more levels above the destination, or with two different headings, are still
  read flat — one extra heading is what was measured, and a guess beyond that would move files on the
  server's behalf without proof.
- A save RomM holds from a folder that had only metadata in it restores nothing and says so in the log
  (`Restore skipped …, none of its members belongs in …`). It is not this plugin's save and not this
  plugin's to invent; the slot can be corrected in RomM.
- A save fetched in a differently-packed shape uploads one duplicate version the next sync (RomM's
  content hash is over member names), then reports `Skip` from then on. Measured on Switch: upload,
  then skip.
