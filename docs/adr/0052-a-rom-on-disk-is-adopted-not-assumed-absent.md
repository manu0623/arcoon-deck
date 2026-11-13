# 0052 — A ROM on disk is adopted, not assumed absent

**Status:** Accepted (0.47.0)
**Follows:** 0046 (the structure is a setting), 0048 (a PSP save is the folders its disc id
names), 0051 (a standalone emulator is pointed at the save tree)

## Context

The plugin records an install only where its own download put the file. Everything that
follows reads that row: the save layer refuses an uninstalled ROM with `needs: save_id`,
because it will not read a game's header from a path it cannot name, and the launch bake has
no path to bake.

Measured on the reference Deck after 3DS saves were made syncable (0.46.0): the 3DS tree was
linked and the title-id path verified, yet `get_save_status` still answered
`needs: save_id` for every 3DS game — one of them with 128 played sessions — because
`rom_installs` held nothing for the platform. The three `.3ds` files had arrived through
EmuDeck years earlier. A save the plugin can name, for a game the plugin insisted was not
installed.

The library was not wrong to know these games: they are RomM's own rows. What was missing is
that "known to the library" and "placed by this plugin's downloader" had quietly become the
same fact.

## Decision

A startup pass, `services/rom_install_discovery`, adopts a known ROM whose content is already
on disk:

- **Only a file the row names.** The same `fs_name` in the platform's directory, or — when the
  row states a bare name, as RomM often does — a *unique* stem match there, which is how
  `Legend of Zelda A Link Between Worlds` finds the `.3ds` beside it.
- **A tie is not guessed between.** Two files sharing a stem (a patch, two regions) means two
  different games' saves; the row is reported as ambiguous and left alone.
- **A folder-backed ROM is not entered.** Which file inside a directory launches is the
  download path's decision, made with the M3U and collapse rules (ADR-0008, ADR-0019). A
  directory is reported, never adopted.
- **Only roots this plugin owns under some structure it can have shipped** (ADR-0046,
  `roms_roots`), today's root first. A corrupt or foreign path cannot aim the scan at the
  user's home.
- **The launchability verdict is recorded, not enforced.** A file the system cannot launch is
  still a real install with `launchable=False`, exactly as the download path records it
  (#1582): refusing would hide a file the user has nowhere else.
- **The pass is best-effort.** It runs beside the other startup healing, in the executor, and
  a failure is a warning — adopting a file is never worth failing the plugin's start. The
  same pass is exposed on demand as `adopt_roms_on_disk`.

## The packing bug adoption exposed

With the 3DS games finally installed, the first packed unit crashed: `FileNotFoundError` for
`<base>/data` while packing a title whose save was at `<base>/id0/id1/title/.../data`. The
unit had always named a 3DS member `"data"`, an archive root that is only correct when the
member is a child of the answer's directory — which a prefix bundle's folder is and a title
tree's member is not. The rule is now stated where the unit is built: an archive root is the
member's path inside the answer's directory, so packing, the on-disk probe and the restore all
walk the same distance and a download lands where Azahar reads.

## The empty title that could not come back

Uploading worked; restoring did not, for a game that had not saved locally yet. A 3DS unit
with no members reported itself unidentified (the layout carries `identified=False`, because
neither save root names the title), so a download refused with `save_shape_unsupported` for a
game whose id had just been read perfectly well. Measured on the reference Deck by removing
the local title folder after an upload: the save sat on the server and nothing could fetch it.

By the time the rule has split the save id into a category and a low id and discovered the
console's `id0`/`id1`, the title IS named — an empty folder is a game that has not saved yet,
which is exactly the directory a server save unpacks into. The unit says so now, and a fresh
title has a download target.

## Two PS3 games that were two text files

The first pass over the reference Deck adopted five installs: three 3DS games, and
``rpcs3_guide.txt`` and EmuDeck's "Disc Games Can Be Put Here For Automatic Detection.txt"
— the placeholder notes that sit in every EmuDeck ROM folder, whose library rows carry
those very names. Their ``.txt`` suffix is in no emulator's accept-list, and the pass
recorded them anyway because it treated "the file is there and the row names it" as
enough, with ``launchable=False`` as the only trace.

An adoption claims a *game*. A row was only ever matched to a file, and a format this
system cannot read is the one thing on disk that is certainly not the game. Adoption now
requires the platform's own format list to name the suffix; a file the pass cannot vouch
for is left alone and logged. The download path keeps its older, looser rule, because it
recorded a file it placed itself and knows what it is.

## Consequences

- A library that arrived another way becomes syncable without a re-download, which is what
  makes 3DS (and later families) worth their rows on a real device rather than only on a
  freshly downloaded game.
- The plugin now claims files it did not place. That is the point, and it is visible: the
  adopted path is what the game detail, the launch bake and the save answer all state, and an
  install row is how every other surface already knows a game is present.
- Adoption does not move, rename or verify content — it records where the file already is. A
  library with duplicate dumps is left with duplicates; the ambiguous rule keeps that from
  silently becoming the wrong save.
- A ROM whose file is on disk under no root this plugin owns is still not adopted. The
  structure setting is what decides which trees those are (ADR-0046), so a user whose library
  lives outside all of them chooses a custom root, not a guess.
