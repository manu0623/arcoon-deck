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

## What this does not do

- **Other standalone emulators.** Dolphin's cards, a PS2 card, a 3DS title tree: their bank
  layouts describe shapes nothing has pointed those emulators at yet, and pointing them is a
  separate decision per emulator (which card, which profile, which title root).
- **Savestates.** `PPSSPP_STATE` is left alone; `SAVEDATA` is the savedata the sync carries.
- **RetroDECK's sandboxed emulators.** They are reached through its frontend, which is its own
  business.
