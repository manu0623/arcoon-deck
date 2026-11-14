# 0066 — An archive that packed the folder restores into it, not beside it

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
…/93543B1D30E2AEB87D0F28AE30D83730/01006BB00C6F0000/           <- Eden's title folder
  .romm-backup/savedata1_20261114_004406.bin                    <- the local save, quarantined
  01006BB00C6F0000/savedata0.bin, savedata1.bin, …              <- the download, one level too deep
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

## Decision

A restore drops a heading that names the folder it is restoring into, and only that heading.

1. `domain.save_bank.archive_members_under(members, folder_name)` answers the members' names
   relative to *folder_name* when **every** member sits under exactly that one heading, and `None`
   otherwise. A flat archive, a mixed archive, or a sibling whose name merely starts with the same
   text (`01006BB00C6F00001/…`) is not rooted there, so nothing moves on a shape the plugin cannot
   prove.
2. `SaveFileStore.extract_archive(..., strip_root=…)` refuses a member outside the heading and
   writes the rest under their stripped names. Stripping is a rename, never a wider destination:
   every byte still lands inside `target_dir`, through the same realpath/symlink guard as before.
   The stripped names are what `extract_archive` returns, so the per-file baselines name the path
   the file actually landed at.
3. `MatrixExecutor._restore_member_set` passes `strip_root` only when the archive is rooted at
   `basename(target_dir)` — the folder the answer already named — so GameCube cards, PSP's
   `<DISC_ID>DATA00/<file>` members and the flat Switch archive keep the reading they had.

## Consequences

- A save uploaded by a client that packed the title folder restores into that folder. Measured
  against RomM save 457: the six members land in `<title>/` and `<title>/<title>/` is never created.
- Our own uploads stay flat, so nothing about the archive the plugin sends changes — a save
  round-trips through this build with no heading to strip.
- A mixed archive (some members under the heading, some not) is read flat, exactly as before. Neither
  reading is a guess the plugin is allowed to make on the server's behalf.
- Quarantine still runs per member before the bytes move, so the save that was overwritten is
  recoverable from `.romm-backup/` — it was in this incident, and it is how the 19:41 session's save
  survived a restore that put the download in the wrong place.
