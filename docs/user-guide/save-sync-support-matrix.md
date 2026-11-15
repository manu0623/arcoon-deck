# Save sync support by platform

Save sync works **per game**: when a game is installed, its save is uploaded to RomM and pulled back before launch, so
you can carry on across devices. Standard cartridge saves work automatically. A few consoles store saves differently —
this page shows what syncs for each system today, and what's planned.

## How reliable is this page?

**The plugin no longer decides what a save is from a table like this one.** It asks your machine, per game and per the
emulator that will launch it, every time it syncs — so the answer follows your actual core choice and your actual core
options rather than a row written in advance. This page is now background reading: it explains why a platform behaves
the way it does, and the plugin's own answer is what governs.

Two things still matter when you read a row:

- **A ❌ often means "not with the settings that ship", not "impossible".** Several cores can write per-game saves if
  you change a core option — the rows below say which. Turning that on is not yet something the plugin does for you, but
  it does now **notice**: change the option and the next sync reads the new answer.
- **Rows are stated for each platform's _default_ core.** You can override the core per system and per game, and a
  different core can behave differently — which is exactly why the plugin asks per game. RetroArch's
  `savefiles_in_content_dir` still moves saves out of where the plugin looks, and that is reported separately.

Most of this table is derived from libretro's documentation and from reading core source, not from watching each core
write a save. Where the [emu-atlas](https://github.com/danielcopper/emu-atlas) audit has corrected an earlier
assumption, this page reflects the audit.

## When save sync does nothing, and why

Where the plugin cannot carry a game's saves it now says so instead of quietly finding nothing. There are four reasons,
and they mean different things:

- **The emulator keeps one save card that all games share.** Syncing it per game would copy other games' progress onto
  this one's record. PlayStation 2 no longer fits this case — the plugin gives it a folder card in its own tree, which
  both PCSX2 and the LRPS2 core write to — but an emulator the plugin does not link still keeps its shared card to itself.
- **The save is written inside the game file itself.** There is no separate file to carry.
- **The emulator files saves under the game's own identity** — in the file name for Dreamcast, in the folder name for
  GameCube. The plugin reads that identity out of the game file itself: the disc's own code for Dreamcast, GameCube and
  Wii, the `SYSTEM.CNF` serial for PlayStation and PlayStation 2, `PARAM.SFO` for PlayStation 3 and PlayStation Portable,
  the title id for Nintendo 3DS and Switch. A 3DS title's `data` tree and, when it has one, its `extdata` tree are both
  part of the save. Wii U and Vita ids are still unread, so those two answer nothing yet.
- **What the emulator writes could not be established** — either nobody has audited that core yet, or the folder is
  known and the names inside it are not.

None of these is an error, and none of them stops a game launching. If you change the emulator for a game, the answer is
read again for the new one.

### Windows games

A Windows game is the fifth case, and it is answered differently: it runs under Proton, so a libretro save directory describes
nothing about it. Its saves are one folder inside its own prefix, and the plugin carries that folder as a zip — uploaded to
RomM as a `proton` save when you finish playing, and the newest one put back before the next launch. The folder is picked by
name against the game's title (falling back to the one last written) and remembered per game; the log names it, so a wrong
pick is visible. Saves a game keeps in the Windows registry, and games that spread progress over two folders, are not carried
yet — see [ADR 0074](../adr/0074-a-pc-games-saves-are-one-folder-in-its-prefix.md).

## Categories

|    | Meaning                                                                                                                                                                                                                                                        |
| -- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ | **Synced today.** Your saves for this system carry across devices automatically. A few systems answer differently for a disc image than for a raw dump — where that is so, the note says which file gets you the per-game save.                                |
| 🔜 | **Planned.** This save type isn't synced yet, but it fits the model and is on the way in a future release.                                                                                                                                                     |
| ❌ | **Not synced yet.** This system's default core writes a _shared_ card (one file for many games), keeps saves outside the per-game save folder, or hasn't been pinned down yet — so it doesn't fit per-game sync today. Handled differently in a later release. |
| ⚪ | **No save data.** This system's emulator has no in-game save to sync (you can still use save states locally).                                                                                                                                                  |

## What syncs today ✅

Standard per-game cartridge saves sync automatically. That covers the large majority of systems — Nintendo (NES, SNES,
Game Boy / Color / Advance, N64, DS), Sega (Master System, Game Gear, Genesis / Mega Drive), PC Engine / TurboGrafx,
WonderSwan, Atari Lynx, Virtual Boy, and more.

**Sega CD depends on your game file.** A raw `.bin` dump saves per game and syncs; a `.chd`, `.cue` or `.iso` disc image
puts the save on a shared BRAM card that all your Sega CD games write to, which cannot be carried per game. Amiga is the
same story with different answers: a `.chd` CD32 image saves per game, while an `.adf` floppy writes into the disk image
itself, a `.lha` names a `WHDSaves` folder whose contents the core does not list, and an `.hdf` hard-disk image cannot
be established at all.

3DO and Neo Geo are named right and still not found: those emulators keep saves in a per-emulator subfolder that the
plugin does not yet look in.

The systems whose default core has been **watched writing a save on a stock RetroDECK install** are Game Boy / Color /
Advance, N64, Saturn, Neo Geo Pocket (Color) and Pokémon Mini. The rest of the ✅ rows follow the same standard `.srm`
convention and are expected to behave identically, but haven't been observed one by one.

## Standalone emulators

A standalone emulator keeps its saves outside RetroArch, so taking it over is a separate job from the redirect a libretro
launch gets — and it is done for the emulators whose folder has been measured on a Deck:

| Emulator | Its save folder                   | What the plugin does                                       |
| -------- | --------------------------------- | ---------------------------------------------------------- |
| PPSSPP   | the memstick's `PSP/SAVEDATA`     | links it to the plugin's PSP folder                        |
| PCSX2    | `memcards`                        | links it to the plugin's PS2 card folder, which it formats |
| RPCS3    | `dev_hdd0/home/00000001/savedata` | links it to the plugin's PS3 folder                        |
| Azahar   | `sdmc/Nintendo 3DS`               | links it to the plugin's 3DS tree                          |

The link is a symlink of the emulator's own folder rather than a setting inside the emulator, so the emulator keeps its
configuration and the files it reads become the files the plugin syncs. Only installs the plugin can name take part — a
native install or a flatpak. An EmuDeck launcher script is deliberately left out: it names an installation behind it that
the plugin cannot identify, and linking the script created a sandbox nothing had ever launched.

**Dolphin** is covered the other way round, because a GameCube or Wii save is a card entry rather than a folder: a launch
the plugin manages pins Dolphin's user directory, so the card folder it writes is the one the sync reads.

## Coming soon 🔜

Per-game saves for these systems fit the sync model and are planned for a future release:

| System      | Notes                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| PlayStation | Memory-card saves. The cores write them per game, but under a name the plugin doesn't probe yet.            |
| 3DO         | The Opera core writes per-game NVRAM into its own `opera/per_game/` subfolder, under a versioned name.      |
| Neo Geo     | FinalBurn Neo writes a per-game save into its own `fbneo/` subfolder, which the plugin doesn't look in yet. |

!!! warning "3DO was listed as syncing here before — it wasn't"

    Until this revision, 3DO showed as ✅ on the assumption that the Opera core writes a plain `<game>.srm` into the
    save folder. The core audit disproved that: Opera writes its NVRAM to `opera/per_game/` with a version number in
    the filename, and exposes no save RAM to RetroArch at all — so there was never a `.srm` for the plugin to find.
    **If you have 3DO games, your saves have not been backed up to RomM.** Copy them off the device yourself until
    this is supported.

A few less-common systems (some DOS, PICO-8, ST-V) may also gain support pending confirmation.

## Not synced yet ❌

These systems' default cores write a **shared card** — a single file holding the saves for _all_ your games — keep saves
outside the per-game save folder, or haven't been pinned down yet. A shared card can't be split per game without risking
other games' saves, so it doesn't fit per-game sync today. We're looking at safe ways to handle these in a future
release.

| System         | Why it doesn't sync today                                                                                                                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dreamcast      | Flycast ships with **Per-Game VMUs off**, so every game shares `vmu_save_A1.bin` and its siblings in RetroDECK's system folder. The core _can_ write per-game VMUs; the names it uses then aren't pinned down yet.      |
| Neo Geo CD     | Ships writing one shared save. The core has a per-content mode; which one wins when loading isn't confirmed.                                                                                                            |
| Nintendo 3DS   | The Azahar core appears to use its own save subtree. Not confirmed on-device yet.                                                                                                                                       |
| Arcade (MAME)  | NVRAM is stored separately by the emulator, not as a file named after your ROM.                                                                                                                                         |
| Amiga          | PUAE keeps an `.adf` floppy's save inside the disk image itself, so there is no separate file to carry. A `.lha` names a `WHDSaves` folder whose contents the core does not list, and an `.hdf` is not answered at all. |

## No save data ⚪

Many computer, arcade, and homebrew systems have no in-game battery save at all — there's simply nothing to sync (save
states still work locally). See the full table for specifics.

## Full platform list

??? note "Every platform (149)"

    Status of each platform's default emulator core. Some platforms offer alternative cores that may behave differently.

    | Platform | Status | Notes |
    | --- | --- | --- |
    | `amiga` | ❌ | An `.adf` floppy keeps the save inside the disk image; a `.lha` names a folder whose contents the core does not list; an `.hdf` is not answered |
    | `amstradcpc` | ❌ | Not synced |
    | `apple2` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `apple2gs` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `arcade` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `arcadia` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `astrocde` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `atomiswave` | ❌ | Shared VMU card (Flycast default; the core has a per-game mode) |
    | `consolearcade` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `cps` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `cps1` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `cps2` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `cps3` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `crvision` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `daphne` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `doom` | ❌ | Not synced |
    | `dreamcast` | ❌ | Shared VMU card (Flycast default; the core has a per-game mode) |
    | `easyrpg` | ❌ | Not synced |
    | `fmtowns` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `gamate` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `gameandwatch` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `gamecom` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `gmaster` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `gx4000` | ❌ | Not synced |
    | `laserdisc` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `lcdgames` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `mame` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `mess` | ❌ | Not synced |
    | `model2` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `n3ds` | ❌ | Azahar core's own save subtree — not confirmed on-device |
    | `naomi` | ❌ | Shared VMU card (Flycast default; the core has a per-game mode) |
    | `naomi2` | ❌ | Shared VMU card (Flycast default; the core has a per-game mode) |
    | `naomigd` | ❌ | Shared VMU card (Flycast default; the core has a per-game mode) |
    | `neogeocd` | ❌ | Shared save (the core has a per-content mode) |
    | `neogeocdjp` | ❌ | Shared save (the core has a per-content mode) |
    | `ps2` | ✅ | A folder memory card in the plugin's own tree: a game's save is the folder it owns on that card, and a card image that arrives from another device has its folders written into the bank |
    | `psp` | ✅ | `PSP/SAVEDATA/<disc id>*` under the memstick the launch hands the core; the disc id is read from the game's own `PARAM.SFO`, and the save is every sibling folder sharing that prefix |
    | `pv1000` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `scummvm` | ❌ | Not synced |
    | `scv` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `supracan` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `switch` | ✅ | `nand/user/save/<user>/<slot>/<title id>` inside Eden's NAND, with the id read from the ROM's own ticket — an `.xci` carries no ticket list, so its id is not read |
    | `vsmile` | ❌ | Saves are stored separately by the emulator (MAME) |
    | `wii` | ✅ | `Wii/title/00010000/<code in hex>/data` inside Dolphin's own data tree |
    | `x68000` | ❌ | Not synced |
    | `3do` | 🔜 | Per-game NVRAM, but in the Opera core's own `opera/per_game/` subfolder with a versioned name |
    | `amiga1200` | 🔜 | Planned |
    | `amiga600` | 🔜 | Planned |
    | `atarijaguar` | 🔜 | Planned |
    | `cdimono1` | 🔜 | Under review |
    | `cdtv` | 🔜 | Planned — pending platform mapping (#907) |
    | `dos` | 🔜 | Planned |
    | `neogeo` | 🔜 | Per-game saves, but in the FinalBurn Neo core's own `fbneo/` subfolder |
    | `pc` | 🔜 | Planned |
    | `pico8` | 🔜 | Planned |
    | `psx` | 🔜 | Planned |
    | `quake` | 🔜 | Planned |
    | `saturnjp` | 🔜 | Planned |
    | `stv` | 🔜 | Planned |
    | `wasm4` | 🔜 | Under review |
    | `windows3x` | 🔜 | Planned |
    | `windows9x` | 🔜 | Planned |
    | `amigacd32` | ✅ | A `.chd` disc image saves per game; a raw `.bin` is not answered |
    | `atari2600` | ✅ | Synced |
    | `c64` | ✅ | Synced |
    | `famicom` | ✅ | Synced |
    | `fbneo` | ✅ | Synced |
    | `fds` | ✅ | Synced |
    | `gamegear` | ✅ | Synced |
    | `gb` | ✅ | Synced |
    | `gba` | ✅ | Synced |
    | `gbc` | ✅ | Synced |
    | `gc` | ✅ | Dolphin's GameCube card folder in GCI mode (`GC/<region>/Card A`); the entry is chosen by the disc's own game code, and a card holding nothing yet still restores from the server |
    | `genesis` | ✅ | Synced |
    | `mark3` | ✅ | Synced |
    | `mastersystem` | ✅ | Synced |
    | `megacd` | ✅ | A raw `.bin` dump saves per game; a disc image uses a shared BRAM card |
    | `megacdjp` | ✅ | A raw `.bin` dump saves per game; a disc image uses a shared BRAM card |
    | `megadrive` | ✅ | Synced |
    | `megadrivejp` | ✅ | Synced |
    | `megaduck` | ✅ | Synced |
    | `multivision` | ✅ | Synced |
    | `n64` | ✅ | Synced |
    | `n64dd` | ✅ | Synced |
    | `nds` | ✅ | Synced |
    | `nes` | ✅ | Synced |
    | `ngp` | ✅ | Synced |
    | `ngpc` | ✅ | Synced |
    | `pc88` | ✅ | Synced |
    | `pcengine` | ✅ | Synced |
    | `pcenginecd` | ✅ | Synced |
    | `pcfx` | ✅ | Synced |
    | `plus4` | ✅ | Synced |
    | `pokemini` | ✅ | Synced |
    | `satellaview` | ✅ | Synced |
    | `saturn` | ✅ | Synced |
    | `sega32x` | ✅ | Synced |
    | `sega32xjp` | ✅ | Synced |
    | `sega32xna` | ✅ | Synced |
    | `segacd` | ✅ | A raw `.bin` dump saves per game; a disc image uses a shared BRAM card |
    | `sfc` | ✅ | Synced |
    | `sg-1000` | ✅ | Synced |
    | `sgb` | ✅ | Synced |
    | `snes` | ✅ | Synced |
    | `snesna` | ✅ | Synced |
    | `sufami` | ✅ | Synced |
    | `supergrafx` | ✅ | Synced |
    | `supervision` | ✅ | Synced |
    | `tg-cd` | ✅ | Synced |
    | `tg16` | ✅ | Synced |
    | `tic80` | ✅ | Synced |
    | `vic20` | ✅ | Synced |
    | `virtualboy` | ✅ | Synced |
    | `wonderswan` | ✅ | Synced |
    | `wonderswancolor` | ✅ | Synced |
    | `arduboy` | ⚪ | No save data |
    | `atari5200` | ⚪ | No save data |
    | `atari7800` | ⚪ | No save data |
    | `atari800` | ⚪ | No save data |
    | `atarilynx` | ⚪ | No save data |
    | `atarist` | ⚪ | No save data |
    | `atarixe` | ⚪ | No save data |
    | `bbcmicro` | ⚪ | No save data |
    | `chailove` | ⚪ | No save data |
    | `channelf` | ⚪ | No save data |
    | `colecovision` | ⚪ | No save data |
    | `fba` | ⚪ | No save data |
    | `intellivision` | ⚪ | No save data |
    | `j2me` | ⚪ | No save data |
    | `lowresnx` | ⚪ | No save data |
    | `lutro` | ⚪ | No save data |
    | `moto` | ⚪ | No save data |
    | `msx` | ⚪ | No save data |
    | `msx1` | ⚪ | No save data |
    | `msx2` | ⚪ | No save data |
    | `msxturbor` | ⚪ | No save data |
    | `odyssey2` | ⚪ | No save data |
    | `palm` | ⚪ | No save data |
    | `pc98` | ⚪ | No save data |
    | `ports` | ⚪ | No save data |
    | `spectravideo` | ⚪ | No save data |
    | `to8` | ⚪ | No save data |
    | `uzebox` | ⚪ | No save data |
    | `vectrex` | ⚪ | No save data |
    | `videopac` | ⚪ | No save data |
    | `vircon32` | ⚪ | No save data |
    | `x1` | ⚪ | No save data |
    | `zmachine` | ⚪ | No save data |
    | `zx81` | ⚪ | No save data |
    | `zxspectrum` | ⚪ | No save data |

---

_Coverage is reviewed against the emulator cores RetroDECK ships. PlayStation Portable and PlayStation 2 rows are now
watched on a Deck rather than derived: PSP on 2026-11-14, when a save made on a second handheld loaded from the plugin's
own redirect, and PS2 against real cards and saves. The rest of the per-system list still follows the emu-atlas core
audit. Last reviewed 2026-11-14, against the [emu-atlas](https://github.com/danielcopper/emu-atlas) core audit as of
2026-07-24._
