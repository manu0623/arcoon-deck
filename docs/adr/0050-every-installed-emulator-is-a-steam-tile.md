# 50. Every installed emulator is a tile in a Steam collection

**Status:** Accepted (0.43.0)
**Follows:** 0041 (the plugin's own inventory), 0049 (a standalone emulator's source lives in the inventory).

## The problem

Once the app provisions its own runtime, its cores and — from 0.42.0 — a platform's standalone
emulators, the Deck has emulators on it and no way to *open* one. Every shortcut in the library
points at a ROM: there is no tile that starts Azahar or RPCS3, so the only route to an emulator's
own settings, controller bindings or BIOS paths is to launch a game and quit out of it, and the
only way to check that a build runs at all is to find a ROM it happens to accept.

The reader's request is the design brief: **one Steam collection holding the installed emulators,
each launchable on its own, dressed with art like the games.**

## The decision

**A collection, not a menu.** `RomM: Emulators (<hostname>)` — the same machine-scoped naming
every other collection this app writes uses, so the existing sweeps find it, a second Deck's
collection of the same name is left alone, and "clear collections" removes it like the rest.

**Which rows qualify is stated by the domain, not by the surface.** `domain.emulator_shortcut`
offers the two providers whose install *is* a command line:

- `native` — a path on disk (AppImage or binary). Shortcut exe is the file, start dir its
  directory, launch options empty.
- `flatpak` — an application id. Shortcut exe is `/usr/bin/flatpak`, launch options
  `run <app_id>`.

Three things are deliberately excluded, each because the tile would not do what the tile claims:
**EmuDeck launchers** (a script that takes a ROM; run bare it is not a window), **RetroDECK's
bundled emulators** (inside the sandbox, reached through its frontend — the scanner already
declines to report them as installs), and **unidentified binaries** (a title over a guess is worse
than no tile).

**The backend names the rows; Steam does the writing.** What is installed is a filesystem
question; creating a shortcut or a collection is only possible from inside Steam. So
`get_emulator_shortcuts` returns the catalogue, the frontend creates the tiles
(`src/utils/emulatorShortcuts.ts`) and writes the collection.

**The app id each tile became is a binding in settings**, `emulator_shortcuts: {<key>: <app id>}`
keyed by `<definition id>@<provider>` — not by label, which carries spaces and brackets. Without
it, a second run would need a full `RegisterForAppDetails` scan of Steam's shortcut store (~2 s per
shortcut, hundreds on a full library) to know which tiles it already made.

**The binding is a hint; Steam's store is the truth.** A bound app id Steam no longer has (the
user deleted the tile, Steam rebuilt its store) is forgotten and the row is created again. A store
that is *empty* is not evidence of that: at a plugin mount Steam may not have populated its
shortcut map yet, and treating that as "all gone" would add a duplicate tile per emulator on every
boot. The store is only checked once it has something in it.

**It runs at startup, and there is a button.** An emulator appears when it is installed — often by
this plugin's own install action — and a collection the reader must remember to refresh is one that
silently omits the emulator they just added. The startup run is idempotent; the Settings button
(`Emulators & Cores` → **Add Emulators to Steam**) re-runs it on demand and reports what it did.

**Art is best-effort, by name, and never blocks the tile.** SteamGridDB is searched through its
autocomplete endpoint with the emulator's own `display_name` ("PPSSPP", not "PPSSPP (Flatpak)"),
and the four asset types are fetched and applied with the same Steam calls the ROM artwork path
uses (`SetCustomArtworkForApp` for hero/logo/grid, `saveShortcutIcon` + `SetShortcutIcon` for the
icon). No API key, no name match, a failed download: all mean the default tile. The shortcut is the
feature; the picture makes it look like it belongs.

## What this does not do

- **No launching a ROM.** The tile opens the emulator; picking a game inside it is the user's.
- **No removal.** Uninstalling an emulator drops its row from the next run's collection, but the
  shortcut it already made is left in Steam — deleting the user's tiles is their call.
- **No art for a build with no SGDB match.** A curated per-emulator art source would be the next
  step, and is not this one.
