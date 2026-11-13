# 51. A standalone emulator's save folder is the plugin's save folder

**Status:** Accepted (0.44.0)
**Follows:** 0048 (a PSP save is the folder set its disc id names), 0049 (a standalone emulator's source lives in the inventory).

## The problem

Measured on the reference Deck after 0.43.0 installed PPSSPP and gave it a Steam tile: the
plugin held the game's save at
`~/.local/share/romm-tender/saves/psp/PSP/SAVEDATA/ULUS10025SAVE000`, and the standalone
PPSSPP — opened from its own tile, exactly as the collection intends — offered a first-run
save. Two directories, one game, no overlap.

The asymmetry was already there before the tiles existed. The plugin redirects the runtime it
owns: a generated appendconfig makes its RetroArch write PSP savedata into
`<saves>/psp/PSP/SAVEDATA`. Nothing was ever said to an emulator the plugin merely *installed*.
So a game played in the standalone emulator wrote into `~/.config/ppsspp/PSP/SAVEDATA`, which
no sync reads, and a save the sync had downloaded was invisible to it.

## The decision

**The plugin points the standalone emulator's save folder at the tree it syncs, with a
symlink.** `<emulator config root>/PSP/SAVEDATA` becomes a link to
`<saves>/psp/PSP/SAVEDATA`, so the emulator and the sync address one directory.

Why a link rather than an emulator setting: PPSSPP 1.20.4's `ppsspp.ini` carries
`MemStickInserted` and `MemStickSize` and **no memory-stick path**, so there is no key to write.
The filesystem is the only lever, and it is the one lever that works the same for a native
AppImage (`~/.config/ppsspp`) and a flatpak (`~/.var/app/org.ppsspp.PPSSPP/config/ppsspp`),
because the link is made inside whichever root the provider keeps.

**Adopt, then link — never link over.** A deck that played the emulator before this existed
holds real progress in that folder. Its entries are moved into the plugin's tree first; only
then is the empty folder replaced. A name held on both sides is a merge conflict: that entry
stays where the emulator put it, still reachable in the emulator, and is named in the result
rather than overwritten in either direction.

**Three states are refused rather than repaired**: a folder that is already a link to somewhere
else (someone decided that), a name that exists but is not a folder (a broken install, not
something to delete), and a merge with any conflicting entries (the folder stays, so nothing is
hidden by the link).

**Which emulators take part is a one-entry table** (`domain/emulator_save_link`): PPSSPP is the
family whose core launch the plugin already redirects into a bank directory. A family whose save
root nothing has redirected has nothing to be pointed at yet, and is not guessed at.

**Only `native` and `flatpak` installs are linked.** An `emudeck` record is a launcher script, and
the emulator behind it may be a flatpak that is not installed at all — measured on the reference
Deck, linking it created `~/.var/app/org.ppsspp.PPSSPP` for a sandbox nothing had ever launched.
A provider that cannot say which install it means does not get a link.

**It runs at startup and right after an install**, because the window that matters is the first
launch: an emulator opened before the link exists writes a save the next sync cannot see.

## The answer, not just the link

Pointing the folder was only half of it, and the second half was measured the same evening:
the save did not reach the server. `[saves] psp: the catalogue offers no entry labelled
'PPSSPP (Standalone)'` and `post_exit_sync skipped: save_shape_unsupported` — the save layer asks
an installed emulator catalogue where a launch writes, this Deck has no ES-DE, so every launch
through a standalone emulator was refused in both directions.

So `services/saves/rom_info` now answers a **standalone launch the plugin has pointed at the
bank** from the bank, exactly as it answers an owned libretro launch from the appendconfig: the
emulator's directory *is* the bank directory, the platform's layout rule names the members (a PSP
save is the `<DISC_ID>*` folders read from the disc's `PARAM.SFO`), and the sync carries them.
The gate is `domain.emulator_save_link.links_emulator`, which reads the same table the link pass
reads, so a launch whose folder nothing points keeps the catalogue's answer — and its refusal —
because the bank would describe a program that writes somewhere else.

## 3DS, and the second emulator in the table

Azahar is the second row, and it made two things general that the PSP row had got away with:

- **The table is keyed by emulator, not family, and says which root the saves hang off.**
  Azahar keeps its settings in `config/azahar-emu` and its NAND in `data/azahar-emu` —
  measured on the reference Deck — so a row that only names a subdirectory of the *config*
  root would have pointed at a directory the emulator never reads. A row is now
  `(data-or-config, subdir)`. Keying by id rather than family matters for the same reason:
  Citra shares Azahar's save format but not its directory, so an unverified sibling gets no
  row instead of inheriting one.
- **The discovery tree is as deep as the layout needs.** The 3DS rule enumerates
  `id0/id1/title/<category>/<low id>/data` rather than inventing a level, which is seven
  levels of listing; the two levels that were enough for a PSP prefix rule returned a
  title with no members and no reason. `SaveLayout.tree_depth` states that fact next to the
  layout instead of leaving it in the caller.
- **A bank directory is not a redirect.** With 3DS answered, the bank-directory lookup had
  to stop answering by family alone: a *libretro* 3DS core is not pointed anywhere by this
  plugin, so the save answer now requires the family the appendconfig redirects for a
  libretro launch and a linked emulator for a standalone one. The two sets live in
  `domain.save_bank.LAUNCH_REDIRECTED_FAMILIES` and `domain.emulator_save_link`.

Azahar's own settings directory was also wrong before this: `_LAYOUTS` said `azahar`, and
the flatpak keeps both roots under `azahar-emu`. Its `qt-config.ini` was therefore never
found, so its emulator entry read as unconfigured.

**The restore half had to follow the upload half.** The unit the sync carries is one
archive (a `title-dir` answer is what decides packing), and `restores_by_extraction` decides
what a download does with it. PSP, GameCube and Switch were in that set; 3DS was not, so the
same save would have uploaded as an archive and come back as a zip renamed next to the title
tree — the exact failure the rule was written for, in the one direction nobody had tried yet.
A 3DS title now restores by extraction like the rest of the member sets.

**The title-id path was verified before anything was moved**, which is the rule this table
now lives by: reading each installed `.3ds` on the reference Deck through the content
identity adapter gave `00040000000ec300` (A Link Between Worlds) and `00040000000a0600`…
`0004000000054000` (Super Mario 3D Land), and both ids exist as
`title/<category>/<low id>` folders inside Azahar's `sdmc` — the same folders the title
tree rule then resolved, with the neighbouring title (`00054000`, `0001d1e00`) excluded.
An id that matched no folder would have meant the emulator was looked at through the
wrong root, and the link would have moved saves nothing could name.

## What this does not do

- **Other standalone emulators.** The mechanism generalises — one table row plus the bank answer
  above — but each family has to be *verified* before its row exists, and they fall into three
  groups:
  - **A straight directory match, so a row is all it needs once checked on a device**:
    RPCS3's `dev_hdd0/home/00000001/savedata`, Dolphin's `Wii/title/00010000`, Cemu's
    `mlc01/usr/save`, Citra's and Lime3DS's own `sdmc`. Each needs its path read on the
    device before its row exists — Azahar's row is the example of what that verification
    costs and buys.
  - **Answered already, unlinked**: the yuzu lineage's Switch tree is read from the emulator's own
    settings today (`_stated_platform_unit`), so it syncs without a link.
  - **Needs more than a link**: PS2 and GameCube saves are *cards* (one file holding many games),
    Dreamcast's is a set of VMU images, melonDS names its saves its own way — each needs its
    card/file shape modelled in the bank first, which is the same work ADR-0048 did for PSP.
- **Savestates.** `PPSSPP_STATE` is left alone; `SAVEDATA` is the savedata the sync carries.
- **RetroDECK's sandboxed emulators.** They are reached through its frontend, which is its own
  business.
