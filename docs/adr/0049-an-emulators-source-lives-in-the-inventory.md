# 49. A standalone emulator's source lives in the inventory

**Status:** Accepted (0.40.0)
**Follows:** 0037 (the app installs its own runtime), 0041 (the plugin's own inventory),
0045 (a built-in runtime asks its own inventory first), 0048 (a PSP save is its folder set).

## The problem

The app installs its own libretro runtime and its cores, but not the emulators the picker
offers as standalone. On the reference Deck the consequence is visible as a directory of
hand-downloaded AppImages (`~/Applications` holds DuckStation, Citron, Eden, azahar and
shadPS4) and as picker rows that say `needs_setup` until the user copies a file there
themselves. In Game Mode there is no way to do that: no browser download, no terminal.

Stating "where the binaries come from" in code was the option this ADR rejects. It puts a
list that changes every release inside a Python file, and it cannot express the two real
facts about a platform's channels:

- **Some emulators are only stores.** Dolphin's own download page offers Linux users a
  flatpak and no AppImage; its official write-up says so.
- **Some emulators are not in any store.** Eden, Citron and DuckStation have no Flathub
  listing at all — measured on the reference Deck (`flatpak remote-info --user flathub`
  answers nothing for all three), even though the inventory named an id for each. Those
  rows now say "release only", which is the truth, and the old ids survive only as
  detection hints for an install that already exists.

## The decision

**The inventory row states its source, and the source is one of two kinds.** A new
`install` block beside the launch data holds either a `flatpak` app id, or a `github`
repository plus an asset glob. `domain.emulator_install` turns it into one of two plans:
`flatpak install --user -y` (the argv `domain.runtime_install` already owns) or the
release API endpoint plus the pattern the AppImage is found by.

**A release is asked for by API, never by a guessed tag.** Tag spellings differ per
project (`v1.20.4`, `nightly-linux`, a bare commit hash), so a URL built from an assumption
is a 404 that reads like a network failure. `matching_asset` then requires **exactly one**
asset to match the glob: a release that attaches an x86_64 build beside an arm64 or a `v3`
variant is a CPU decision this layer may not make, and taking the first name would install
a binary this machine maybe cannot run.

**The release wins when a row has both.** A store's copy is only as current as its last
manifest bump — PPSSPP spent months on Flathub at 1.18.1 while releases moved on — and the
AppImage channel has no packager in between. The order is a parameter
(`prefer_newest`), so asking for the store build stays possible; it is not a constant
hidden in the adapter.

**A source is not a detection hint.** `host.flatpak` says "if this id is installed, run it
through `flatpak run`"; `install` says "this is how to get one". Keeping them one field is
what produced three rows naming store ids that do not exist — a bug that had already gone
unnoticed because nothing read them for anything but detection.

## Consequences

- Nine systems now have an emulator the plugin can fetch: GameCube and Wii (Dolphin), PS2
  (PCSX2), PSP (PPSSPP), PSX (DuckStation), Switch (Eden, Citron), PS3 (RPCS3), 3DS
  (azahar) and Wii U (Cemu), split six store builds to five releases.
- Three platforms the save layer already understood — `ps3`, `n3ds`, `wiiu` — now have
  inventory rows, so they resolve to an emulator at all. Before this they answered
  `unestablished` because no row existed to answer with.
- Vita is deliberately **not** added. Vita3K's command line takes a *title id* (`-r
  PCSB00952`), and a path handed to it is an install, not a boot, so a path-based shortcut
  cannot launch a downloaded `.vpk`. A row that cannot launch is worse than a missing one.
- Nothing downloads yet: this change states the plan and leaves fetching, hash checking,
  writing and the save-folder link to the adapter that follows. A plan with no consumer
  would be dead code, so `install_plan` is tested against the shipped document — including
  the rule that every platform expected to be installable carries a source.
