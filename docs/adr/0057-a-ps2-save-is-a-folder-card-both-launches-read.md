# ADR-0057 — PS2 saves are a folder card in the bank, and both launches read it

**Status:** accepted

## The problem

PS2 is the one platform where "the save file" is not a per-game object. A PCSX2
**file** card is a single 8 MB image (`Mcd001.ps2`, measured 8,650,752 bytes on the
reference Deck) and every game writes its own save into it. Sharing that one file
between the standalone emulator and the libretro core works — point both at the same
path and each sees the other's saves — but syncing it does not: uploading "this game's
save" ships the whole card, another game's session included, and restoring one game's
save overwrites every other game's.

The plugin already models the shape that can be synced. `domain.save_bank` has a `ps2`
layout of family `PS2_CARD` whose save unit is the game's own subfolder inside a
**folder** card: `Mcd001.ps2/SCUS-97198/`, with `_pcsx2_superblock` holding the
formatted card header. The identity is the disc's serial, which the plugin already reads
from the ISO's `SYSTEM.CNF` `BOOT2` line (`SCUS-97198` for Sly Cooper). What was missing
was any path by which a launch reached that folder card:

- `config/PCSX2/memcards` — the standalone's `[Folders] MemoryCards`, whose slot 1 is
  `Mcd001.ps2`;
- `<retroarch>/system/pcsx2/memcards` — where the libretro core keeps cards, and where
  it still wrote **after** the launch redirected `savefile_directory` into the bank,
  measured on the reference Deck. The core ignores that setting for memory cards.

So the plugin's answer for a ps2 save was `save_shape_unsupported`, and a session played
on one emulator had no save the other could see through sync — exactly what the user hit
when Sly Cooper asked them to create a memory card a second time.

## The decision

**The bank holds a folder card at `saves/ps2/Mcd001.ps2/`, and both launch shapes are
pointed at `saves/ps2`.**

Three pieces, each measured:

1. `SavePoint("pcsx2", in_data_dir=False, subdir=("memcards",))` — the existing
   save-link machinery puts `config/PCSX2/memcards` at `saves/ps2`. The subdir is
   measured from the app's config root, which already ends at `config/PCSX2`; repeating
   the app directory there produced `config/PCSX2/PCSX2/memcards`, a folder nothing reads
   (measured, and why the first wired build linked nothing). PCSX2's ini keeps
   `MemoryCards = memcards`, a relative folder, so the link is what resolves it.
2. `adapters/ps2_memcard.Ps2MemcardAdapter` — when the link pass links PCSX2, the bank
   directory gets a folder card (`Mcd001.ps2/` + a formatted superblock) and
   `<retroarch>/system/pcsx2/memcards` becomes a symlink to `saves/ps2`. Cards the core
   had already written into its own tree are moved into the bank first (`adopted`), and a
   card name that exists on both sides is kept on both sides rather than one being
   dropped.
3. `SaveFamily.PS2_CARD` joins `LAUNCH_REDIRECTED_FAMILIES` — a family may only be listed
   there when a launch is genuinely redirected, which is now true of both: the standalone
   through the link, the core through the system-tree symlink.

**A file card in place is converted — and the image is kept.** The first version of this
decision left the conversion to PCSX2's Memory Card window, on the grounds that only
PCSX2 could do it without losing saves. That was half right: PCSX2 *does* have no
command-line conversion (its Qt binary only ever starts a UI, measured on the reference
Deck), and a card nobody opens that window for is a card that never syncs — the state the
user was left in, with a session played and `uploaded=0`.

So the plugin does the same job itself, because the card's own format says how:
`domain.ps2_file_card` reads the image's superblock, indirect FAT, FAT and directory
entries, and answers each save folder with the byte spans that hold its files. Measured
against the reference card (8,650,752 bytes, `alloc_offset` 41, cluster 0 = page 82), it
extracts `BASCUS-97198YAOTWTD!` holding `icon.sys` (magic `PS2D`), `sly.ico` and
`save1`–`save3`. The adapter writes those files under `Mcd001.ps2/` with a formatted
superblock and moves the image aside to `Mcd001.ps2.file-card-image`, never overwriting
it.

**Extraction is refused rather than approximated.** An image whose geometry does not
parse, or which yields no save folder, leaves the card exactly as it was and returns
`file_card` — a card the plugin does not understand is a save that stays put, not one
that gets rewritten.

## What this does not do

- It does not convert an existing file card. That is a user step in PCSX2 (Memory Card
  manager → convert to folder card), after which the same bank directory holds per-serial
  subfolders and sync can bundle just this game's.
- It does not touch the superblock in an archive, and it does not create the per-serial
  subfolder: PCSX2 writes `SCUS-97198/` when the game saves.
- It does not redirect a second slot (`Mcd002.ps2`). Slot 1 is the measured case; a user
  with saves in slot 2 reaches the bank through the same linked folder but only slot 1's
  card name is created.
