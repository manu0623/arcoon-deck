# Save structure, measured on a real Deck

Status: **measured**. Every path and number here was read from a live Steam Deck running
SteamOS 7.2.7 with EmuDeck, RetroDECK and the RetroArch flatpak installed. Where a platform has no
saves on that machine, the rule comes from the emulator's own layout and is marked unverified.

This page answers one question: **what exactly does Tender hand to RomM, per platform?** RomM
takes one file per save row (`POST /api/saves?rom_id&emulator&slot`); a directory-shaped save
becomes a canonical zip. So every rule below reduces to "what is the unit, and does it upload raw
or zipped".

## What was actually on the machine

Three RetroArch save trees, one of which is empty:

| Tree | Contents |
| --- | --- |
| `<home>/retrodeck/saves/<platform>/<stem>.srm` | the live one — RetroDECK's platform-keyed tree, carries Tender's own `.romm-backup/` markers |
| `<home>/.var/app/org.libretro.RetroArch/config/retroarch/saves/` | 2 files: the same game twice (flat, and under `mGBA/`), **different md5s** |
| `/run/media/deck/SR01T/Emulation/saves/retroarch/saves` | what `retroarch.cfg` currently points at — **0 files** |

And EmuDeck's `Emulation/saves/*` is mostly bookkeeping, not saves:

| Directory | Files | Real content |
| --- | --- | --- |
| `melonds/saves/` | 17 | `.sav` per ROM — genuine saves |
| `pcsx2/saves/` | 1 | `Mcd001.ps2`, one memory card for the whole library |
| `duckstation/states/` | 22 | `*_resume.sav` — resume states, not saves |
| `retroarch/`, `yuzu/`, `citra/`, `dolphin/`, `ppsspp/` | 1–3 each | only `.hash`, `.fail_upload`, `.fail_download` — EmuDeck CloudSync markers, and on this Deck CloudSync has been *failing* |

Two consequences follow immediately, and both are rules this page adopts:

1. **Dotfiles and CloudSync markers are not saves.** A scan that walks a saves directory and takes
   every file uploads `.hash` and `.fail_upload` as if they were save data.
2. **`sort_savefiles_enable` is not enough on its own.** A machine can hold the same game's save in
   two layouts at once, with divergent bytes. Choosing one silently is the bug, not the fix.

## The sync key

One row is identified by `(rom_id, emulator_tag, slot)` — the server's own key, mirrored by
`rom_save_sync_state` (`emulator`, `active_slot`) and by `models/sync.py` ("per `(rom_id, slot)`").

`emulator_tag` already exists for cores (`domain/emulator_tag.py`): `mgba_libretro` → `retroarch-mgba`,
with `retroarch` as the fallback. Standalone emulators need the same treatment, one slug each, because
the server path is `saves/{system}/{rom_id}/{emulator}/` — two emulators for one platform must not
collide there, or a DuckStation card overwrites a SwanStation one.

## The unit, per platform

`raw` uploads as the one file RomM stores; `zip` is a directory zipped with entries named relative to
the unit root. Measured rows are marked ●; the rest are the emulator's layout, unverified here.

| Platform | Runner | Path on disk | Unit | RomM form |
| --- | --- | --- | --- | --- |
| gb / gbc / gba / nes / snes / md / … | RetroArch core | `saves/<stem>.srm` **or** `saves/<Core>/<stem>.srm` ● | one file | raw |
| nds | melonDS (core or standalone) | `saves/<stem>.sav` ● | one file | raw |
| psx | DuckStation / SwanStation | `memcards/<serial>.mcd` | one card | raw |
| ps2 | PCSX2 / LRPS2 | `saves/Mcd001.ps2` ● | shared card, or one folder card | raw |
| psp | PPSSPP | `PSP/SAVEDATA/<ULUS…>/` | directory | zip |
| gc | Dolphin | `GC/<Region>/Card A/<code>.gci` | the `.gci` set matching the disc's game code | raw if one, else zip |
| wii | Dolphin | `Wii/title/00010000/<id>/data` | directory | zip |
| wiiu | Cemu | `mlc01/usr/save/00050000/<id>/…` | directory | zip |
| n3ds | Azahar | `sdmc/Nintendo 3DS/<id0>/<id1>/title/00040000/<id>/data` | directory | zip |
| switch | Eden / Citron / yuzu line | `nand/user/save/<user>/<profile>/<title id>` | directory | zip |
| dreamcast | Flycast | `saves/<product>.A1.bin` | one file | raw |
| ps3 | RPCS3 | `dev_hdd0/home/00000001/savedata/<TITLEID>` | directory | zip |
| vita | Vita3K | `ux0/user/00/savedata/<TITLEID>` | directory | zip |

The two rows worth naming as hard cases:

- **PS2's `Mcd001.ps2`** is one card for the entire library. Uploading it as any single game's save
  makes every other PS2 game look synced when it is not; the bank's `PS2_CARD` family with
  `preferred_card` exists for this, and the honest default is to sync the card as a library-level
  unit and say so, not to pretend it is per-game.
- **Switch** needs a title id, which needs the user's `prod.keys`. Without them the save unit cannot
  be named and the game says so (`needs=("save_id",)`), which is the correct outcome rather than a
  guessed directory.

### Where a save id comes from

Every row above is keyed by an identity the path never carries, so it is read from the game file:
`domain/content_identity.py` parses bytes and `adapters/content_identity.py` decides which bytes (bounded
reads, never a scan of a 2 GiB image).

| Platform | Rule | Offset |
| --- | --- | --- |
| psx / ps2 | serial on the `BOOT`/`BOOT2` line of `SYSTEM.CNF` → `SLUS-20312` | inside the first 1 MiB |
| dreamcast | IP.BIN product number → `T-97063D` | 0x40 of the boot sector |
| gc | disc game code → `GMSE` | 0x00 of `boot.bin`, or 0x58 of a `.rvz` container's header |
| n3ds | NCCH program id → `0004000000054000` | 0x118 of the NCCH, whose base the NCSD header states at 0x120 in media units |

Two details are the whole reason this is a module rather than four inline expressions. The `NCCH` magic
sits **0x100 bytes into** the partition the header points at — the partition begins with the NCCH's
signature block, not with its magic — so a reader that looks for `NCCH` at the partition offset finds
nothing on every real cart. And the PS1/PS2 serial is taken from the boot line specifically: an image's
padding and licence text both hold serial-shaped strings, and only the boot line is the one the console
follows.

A GameCube ROM is often stored as Dolphin's compressed `.rvz`, whose first byte is `R`, not `G`, so the disc
reading answers nothing at all and the save had no id — measured on the reference Deck's Twilight Princess,
where every GameCube sync refused for that reason alone. The container's own header carries a copy of the
disc id as plain text: on that file, `GZ2E01` sits at 0x58 and the file begins `RVZ` + `\x01`. The reader asks
the container first and the bare disc second, and it **validates** the six bytes there by the same test a real
`boot.bin` passes, so a container whose layout differs answers nothing rather than a plausible-looking string
out of somebody's hash table. Decompressing the first data group instead was tried and abandoned: the group's
offset is not stated unambiguously by the header fields (the measured values do not match any published layout),
and an uncompressed scan of the first 4 MiB found no decompressible frame at all.

Refusal is the normal outcome: a header without the expected magic returns no id, which the bank reports
as `needs=("save_id",)` rather than pointing a save at another game's folder. PSP, PS3 and Vita are not
read here — their ids live in a `PARAM.SFO` that is reachable only by walking the ISO's directory tree,
and guessing an offset for it would read zeroes on some images and a title id on others.

The resolver states an id-keyed save as a template plus that need, and the id is filled in afterwards by
`domain.save_answer.fill_save_id`: the directory, the backing directory and every component get the id,
and the answer's state is re-derived. Filling one need never rescues an answer that still has another —
3DS extdata keeps its own id, so a 3DS answer with both stays a hole.

Where a save is **read** is now one switch with the launch: with `save_bank` on, the lookup answers
`<data>/saves/<platform>` — the directory the generated appendconfig redirects a libretro launch into —
and with it off the RetroArch path math above stands unchanged. Two names for one directory would be a
save that lands where nothing looks, which is why they are wired together rather than configured
separately; existing saves still live under the old path, so switching it on without migrating them
first reads as lost progress.

## A member set is restored by extracting it

A save whose unit is a *set* of files travels as one archive, and the archive is the unit — for GameCube,
every `.gci` whose header carries the disc's game code. Writing that archive into the emulator's directory
is a silent failure of the worst kind: measured on the reference Deck, RomM held
`01-GZ2E-gczelda2.gci`, the plugin placed `…/saves/gc/Legend of Zelda, The - Twilight Princess (USA).zip`, and
Dolphin — in GCI-Folder mode, `SlotA = 8` — read `GC/USA/Card A/`, found it empty and offered a new card while
the save sat beside it unread.

So a member-set platform restores by **extracting the archive's members into the directory the answer names**,
quarantining each file it is about to overwrite first, and tracking each restored name on its own. The rule is
asked of the bank (`restores_by_extraction`), not of a file extension: only a family whose members live flat in
one directory qualifies, because a nested family would need its tree rebuilt rather than its names restored.

A member set can arrive **packed above the folder it belongs in**: a client that packs the folder rather
than its contents names every member `<folder>/<file>`, and those members are relative to the folder's
parent. Extracting them into the folder recreated it inside itself — measured on the reference Deck, a
Switch save uploaded by another device restored to `<title>/01006BB00C6F0000/savedata1.bin`, and Eden read
`<title>/`, found it empty and started a new game while the save sat one level down.

The same shape sits one level higher on Wii, where the unit is `<title>/data` and a save can be packed from
the title folder itself: RomM holds rom 6938 as `534d4e45/data/wiimj2d.sav` beside
`534d4e45/content/title.tmd`. Here the heading names the destination's *parent*, and `content/title.tmd` is
Dolphin's installed title metadata — not the game's save, and not something a restore may replace.

So the restore asks the bank (`place_archive_members`) to align the archive's one heading with the
destination's own path and to name the members that land inside it; the rest are refused.
`extract_archive(placements=…)` writes only those, under those names, through the same guard that keeps
bytes inside the destination. A flat archive — the shape this plugin packs — a mixed one, one headed by a
name that is not on the destination's path (a PSP `<DISC_ID>DATA00` folder sits *inside* `SAVEDATA`), or a
sibling whose name merely starts the same way is read exactly as before (ADR-0066).

Restoring is only half of it: a GameCube save still has to be *named* before anything can be uploaded, and the
resolver refuses names inside the card folder on purpose (`file-names-unestablished`) since it will not guess
what a directory holds. Two fills settle that, both in `domain/save_answer.py` and both driven from the single
content read `services/saves/rom_info.py` already performs:

- `fill_region` completes `GC/<region>/Card A` from the disc's region byte — `E` is `USA`, `J` is `JAP`, and
  everything else is `EUR`, because Dolphin only ever creates those three folder names.
- `fill_gci_set` lists the card folder and adopts the entries whose middle component is the disc's code in
  Dolphin's `<maker>-<code>-<internal>.gci` naming, so `01-GZ2E-gczelda2.gci` is this disc's save and
  `02-GMSE-other.gci` is not. An empty card, or one holding only another game's entries, stays refused —
  there is nothing to upload yet, and a download places members by the names the archive carries.

Naming the unit is not enough: the sync has to **probe where the unit is**. The matrix joins each save name
onto one directory, and for a member set that directory is the one the answer names, not the platform save
root — a card entry lives in `GC/USA/Card A/` under `saves/gc`, so probing the root found no file, the run
ended `uploaded=0, downloaded=0, errors=0` with nothing reported wrong, and the save sat one folder away
(measured on the reference Deck, rom 5319). Every other platform still probes the platform root.

Where that directory is, an owned launch now settles by construction. Measured failure, on the reference Deck: the
plugin baked RetroDECK's placeholder command (`%EMULATOR_DOLPHIN% -b -e %ROM%`), so the emulator's user
directory was chosen after the plugin stopped looking — the session wrote
`~/retrodeck/saves/gc/User/GC/USA/Card A/01-GZ2E-gczelda2.gci` while every resolved answer pointed elsewhere
(`saves/gc` held only the old misplaced zip, `.var/app/…/dolphin-emu/GC/USA/Card A` was empty), and the sync
skipped the zip as already synced. So a standalone Dolphin launch is now **owned**: the plugin adds
`-u <user dir>` to the command it bakes, and the save answer is derived from that pin
(`domain/owned_dolphin.py`, `domain.save_answer.owned_dolphin_answer`) instead of from the catalogue's model of
where the emulator might write. The pin is refused where the command already states its own `-u`, and PrimeHack
— Dolphin's fork, with its own user tree — is never pinned. The answer still keeps its `<region>` hole and its
unnamed entries, so the two fills above settle it exactly as they settle a resolved one.

Where a platform is provisioned, none of that inference happens at all: `layout.json` (ADR-0034) states the launch and
the save path together, and the plugin bakes one and answers the other from the same entry. A platform absent from the
manifest keeps everything above, unchanged. A platform whose emulator the user has picked is a narrower case: the pick
owns the launch, and the entry still supplies the **save path**, because the picker chooses a program while the folder
belongs to the platform. Measured on the reference Deck — RetroDECK runs the libretro Dolphin core inside Dolphin's own
user tree, so both emulators write `saves/gc/User/GC/<region>/Card A`, and a pick that moved the save path made the sync
look in `saves/gc` while the game wrote the card folder. The provisioner writes the file last, after the tree exists and every path
has been checked, so a run that fails part-way leaves the plugin on the behaviour it had before the run; and the reader
treats an unusable file as "nothing managed" rather than as an error, for the same reason.

```sh
python3 scripts/provision_layout.py --check
python3 scripts/provision_layout.py --adopt gc=/home/deck/retrodeck/saves/gc/User/GC/<region>/Card A
```

Where a member set lives is one question with one answer: `RomInfoService.member_set_dir` — the answer's directory for a
platform that restores by extraction, the platform root otherwise. The sync matrix and the status/launch views all ask
it, because they did not, and the Saves tab read "no saves" while the sync was writing into the card folder. The upload
409 backstop also recognises a member set as a unit: RomM renames an uploaded entry to the ROM's own name, so the entry's
own name can never match the server's row, and a same-extension save in the slot is treated as this unit's save with the
hash comparison still deciding which side wins.

A member set also travels without its container: an upload sends the `.gci` itself, so the download of it is
one bare file rather than a zip. The restore therefore reads the download as an archive first — RomM's older
copies of a card are zips — and, when that fails, places the file under its own name after quarantining what
it replaces. Refusing a bare member would throw away a save RomM holds.

## The three rules that make it RomM-compatible

1. **One file per upload.** `upload_save(rom_id, file_path, emulator, slot=…)` is multipart with a
   single file; `PUT /api/saves/{id}` updates in place, `POST` stacks versions. Directory units are
   zipped before upload, never sent as several files.
2. **Hash the way RomM hashes.** A raw file is its own md5; a zip is hashed **per entry** —
   `name:md5` lines sorted by name, joined with `\n`, md5 of that block. That is
   `domain/save_hash.py`'s `combine_zip_entry_hashes`, already implemented, because RomM's own
   `_compute_zip_hash` does exactly this and container framing is not stable.
3. **`emulator` is a tag, not a platform.** `retroarch-mgba` and `duckstation` are different rows even
   for the same ROM and the same slot.

## How a save root is found

`domain/save_locations.py` answers one question per (family, platform): *which directory does this
emulator write saves to?* It answers from the emulator's **own configuration** first, because that is
what the emulator acts on, and only then from a declared default. The adapter parses each format (INI,
TOML, XML, JSON, a flat `key = "value"` file) into a flat dict of values; the resolver stays pure and
is testable without any emulator installed.

| Family | Config key(s) read | Fallback | Verified how |
| --- | --- | --- | --- |
| `retroarch` | `savefile_directory` | `{data}/saves` | `retroarch.cfg` on the reference Deck |
| `pcsx2` | `Folders/MemoryCards` | `{data}/memcards`, `{data}/saves` | `PCSX2.ini` on the reference Deck |
| `duckstation` | `MemoryCards/Directory` | `{data}/memcards`, `{data}/saves` | `settings.ini` on the reference Deck |
| `dolphin` | — (none: `Dolphin.ini` states no card path) | `{data}/GC/<Region>/Card A`, `{data}/GC` | observed absence in `Dolphin.ini` |
| `ppsspp`, `melonds`, `citra`, `yuzu`, `ryujinx`, `cemu`, `rpcs3`, `vita3k`, `flycast`, `mgba` | — | per-emulator tree | data roots confirmed on the Deck, layout from `save_bank` |
| `mupen64plus`, `xemu`, `xenia`, `shadps4` | — | documented tree | **not yet confirmed** on a Deck |

Fallback templates name one of three roots: `{home}`, `{config}` or `{data}`. Two roots exist because
emulators disagree about which they write into — PCSX2 keeps memory cards beside its settings
(`{config}/memcards`) while Dolphin keeps them in its data tree (`{data}/GC`) — and the same emulator moves
between them by family: Ryujinx holds its whole tree under `~/.config/Ryujinx`, while Eden holds `nand/`
under `~/.local/share/eden`. Both measured on the reference Deck.

The values themselves come from `adapters/emulator_config.py`, which locates an install's own settings
file by provider and parses it into a flat `key -> value` dict (see
[Config Source Parsers](config-source-parsers.md)); no rule reads a file.

Resolution order, and what each step is for:

1. **Configured path**, `~`-expanded and normalised. Returned even when the directory is absent —
   the emulator will create it, and a first launch is not an error. `exists` is reported beside the
   answer rather than folded into the choice.
2. **First default that exists**, in rule order; with none present the first is returned with
   `exists=False` so the session layer knows to create it. Refusing here would make a fresh install
   unplayable.
3. **A refusal** (`UnresolvedSaveRoot`) when the family has no rule, the platform is not one the
   family serves, or the rule declares no candidates. The picker refuses the pick rather than
   syncing a directory nobody chose.

Measured consequence: **the same emulator under two providers resolves to two different roots.**
RetroDECK's `PCSX2.ini` names `/home/deck/retrodeck/saves/ps2/pcsx2/memcards`; EmuDeck's names
`/run/media/deck/SR01T/Emulation/saves/pcsx2/saves`. Both exist, both are `source="config"`. A
save root therefore belongs to a **provider-qualified emulator**, never to an emulator id alone —
which is why the picker key is `PCSX2 (EmuDeck)` and not `pcsx2`.

`exists=True` is also not evidence of saves: the reference Deck's RetroArch target directory exists
and holds zero files, while its flatpak-local directory holds the only real save. That gap is what
harvest exists to close.

## What the measurements change

- **Layout duplication is normal, so resolution must be explicit.** With `sort_by_core` on, a save
  lives under `<Core>/`; with it off, flat. A machine that flipped the flag keeps both. Rule: resolve
  against the *configured* layout (`save_layout.py` already models `InSaveDir(sort_by_core, …)`), and
  if the other location also holds the same stem, surface a choice instead of picking. The Deck in
  question needs exactly that today.
- **Configured directory and written directory can differ.** `retroarch.cfg` pointed at a near-empty
  SD card while the flatpak's own default directory held the only saves. A save root that does not
  exist, or exists and is empty while another tree has content, is a reportable state — not a
  silent "no saves".
- **RetroDECK's tree is platform-keyed and flat** (`saves/<platform>/<stem>.srm`). That is the
  normalization being lost when RetroDECK goes, and the files carrying Tender's `.romm-backup`
  markers are exactly the ones a migration has to adopt into the bank.
- **EmuDeck's tree is not a structure.** Symlinks plus CloudSync markers, failing on this machine.
  Detect its launchers; do not adopt its save layer.

## Switch (Eden), measured 2026-11-12

Eden is not a model this plugin carries yet: `savefile_location('switch', 'Eden (Standalone)')` returns
`standalone-unsupported`, the sync returns `save_shape_unsupported`, and nothing is read or written. The
measurements below are what a managed entry would have to state.

**The server's unit is a zipped folder.** `/api/saves?rom_id=7200` returns
`The Legend of Zelda_ Link's Awakening [2026-10-25_17-11-10].zip`, emulator `eden_duo`, slot `autosave` —
RomM names a save after the ROM and zips whatever the emulator's save unit is. So a Switch save is carried
as one archive of a directory, not as a file set.

**The local unit is a per-title directory two levels down.** Eden's `nand_directory` (read from
`~/.config/eden/qt-config.ini`) is `/home/deck/Emulation/storage/yuzu/nand`, and saves live at
`<nand>/user/save/<user>/<slot>/<title id>/`. On the Deck measured here that is
`…/user/save/0000000000000000/93543B1D30E2AEB87D0F28AE30D83730/<title id>/`, with a second, older slot
(`00000000000000000000000000000000`) beside it holding one title. **The slot is not guessable and must not
be guessed**: the rule is an exact match on `<title id>` under the root, one match or a decline.

**The title id is in the ROM file, not inferred from the emulator.** A `.nsp` is a PFS0 archive whose
string table names its ticket `01006bb00c6f00000000000000000008`; the first 16 hex digits are the title id
(`01006BB00C6F0000`). Eden logged exactly that when it booted the same file, so the read is verifiable
against the emulator's own statement rather than against a guess. Reading it costs one small read of the
archive header — the string table carries the name, so no NCA parsing and no decryption is involved.

**How the manifest states it.** The provisioner adopts Eden's slot directory
(`--adopt switch=…/user/save/<user>/<slot>`) and writes a `title-dir` entry whose `save_dir` ends in
`<save_id>` and whose `needs` is `["save_id"]` — the id is a hole because it belongs to the game, not to
the layout:

```json
"switch": {
  "emulator": "Eden (Standalone)",
  "launch": ["%EMULATOR_FLATPAK-SPAWN%", "--host", "/home/deck/Applications/Eden.AppImage", "-f", "-g", "%ROM%"],
  "save_dir": "/home/deck/Emulation/storage/yuzu/nand/user/save/0000000000000000/<slot>/<save_id>",
  "save_unit": "title-dir",
  "needs": ["save_id"]
}
```

The `launch` names the **host** binary rather than a RetroDECK placeholder: the `--host` form is baked as
the binary itself, so the game inherits Steam's environment and its display. Measured failure that
settled it: spawned through the sandbox, Eden booted and played audio with no picture while Steam's UI
stayed up.

**What carries it.** Three pieces, each measured rather than assumed:

1. `domain/switch_title_id.py` reads the id from the `.nsp`'s PFS0 ticket name (one bounded 64 KiB read,
   no decryption). A `.xci` is a different container and answers `None` — the three Switch ROMs on the
   reference Deck are two `.nsp` and one `.xci`, so that refusal is exercised, not theoretical.
2. `manifest_answer` answers a `title-dir` entry, and `fill_directory_members` names its members from the
   directory's own listing — regular files only, because the restore places members into ONE flat
   directory. Verified on the Deck against rom 7200: `01006BB00C6F0000` resolves and
   `savedata0.bin, savedata1.bin, savedata3.bin, screenshot*.bin` become the member set.
3. `restores_by_extraction("switch")` is true, so RomM's zip is extracted into the title directory
   instead of being renamed into place — the same rule GameCube needed for its card entries.

A title with no local folder yet stays refused (there is nothing to name), which is the honest state for
a game that has never been saved on this device.

**The unit synced is the archive, not the members.** Measured the hard way: with the answer naming six
members, the sync uploaded six files and RomM answered 409 on each — the slot held eight saves, every one a
ROM-named `.zip`, and the backstop could not pair a `savedata0.bin` with any of them. RomM's Switch unit is
one archive named after the ROM, so the folder is packed into exactly that: `prepare_packed_unit` writes
`.arcoon-archive/<rom name>.zip` beside the title folder (a zip cannot live inside the folder it archives,
and a dot directory is one no emulator scans) and the matrix syncs that single file. Downloads come back as
that zip and are extracted into the title folder, which is what `restore_dir` names on the download path — a
zip that packed the folder itself has its `<title>/` heading dropped first (ADR-0066). The
folder stays the truth; the archive is derived from it on every sync, and repacking the same bytes yields the
same content hash, so an unchanged save does not re-upload. Verified on the Deck: six members pack, repack
byte-stable, source untouched.

## Open questions this page does not settle

- Whether a shared PS2 card should sync as one library-level row or prompt for per-game cards.
- Where the bank root lives when ROMs are on a removable card but saves are small enough to keep
  internal — the Deck measured here has 34G of ROMs internal and a 938G card nearly empty.
- Multi-profile Switch/3DS: the unit is the active profile's directory, so a profile switch changes
  which bytes are "the save".
