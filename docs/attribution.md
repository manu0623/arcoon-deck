# Origin & Attribution

Arcoon Deck is a **modification of [Tender](https://github.com/danielcopper/romm-tender)**, the Decky Loader plugin by
**[Daniel Copper](https://github.com/danielcopper)** that puts a self-hosted RomM library into Steam. Everything that
made Tender worth forking — the library sync, the Steam shortcut layer, SteamGridDB artwork, BIOS management, ROM
downloads, the save-sync engine and its conflict model — is his design and his code.

- **Upstream project:** <https://github.com/danielcopper/romm-tender>
- **Upstream documentation:** <https://danielcopper.github.io/romm-tender/>
- **License:** GNU GPL-3.0, unchanged here. Arcoon Deck is a derivative work distributed under the same terms, and
  `LICENSE` in this repository is Tender's.
- **Looking for the original?** If you want the project as its author maintains it, including its releases and its
  support, use the link above rather than this fork.

This fork keeps Tender's history: the repository's early commits are upstream's, and a single fork-point commit marks
where the modification starts. About 130 commits sit on top of it, all of them save-sync and launch work described
below.

## What this fork changed

Tender states plainly that its save sync covers cartridge saves, and that the memory-card and title-folder systems do
not sync yet. Closing that gap is what this modification is for — the platforms whose save is a *structure* rather than
one `.srm` file, each measured on real hardware before the change was kept:

| Area | What changed |
| ---- | ------------ |
| **PlayStation 2** | A game's save is the folder it owns on a memory card, so the card became the unit: folder cards live in the plugin's own tree, a game's folders are packed as one archive, a card image that arrives from another device has its folders written into the bank, and a standalone PCSX2's card folder is staged out of it |
| **PlayStation Portable** | A save is the `<disc id>*` sibling folders under `SAVEDATA`, with the disc id read from the game's own `PARAM.SFO`. The libretro core is handed the folder *above* `PSP/SAVEDATA`, because handing it the whole path made the core create `SAVEDATA/PSP/SAVEDATA` — one level away from where the lookup reads |
| **GameCube, Wii, Switch, 3DS** | Saves that RomM carries as one archive packed above their own folder now restore into that folder instead of beside it, and archives holding nothing for the save are refused rather than written flat |
| **Standalone emulators** | PPSSPP, PCSX2, RPCS3 and Azahar have their save folders linked to the plugin's tree, and a managed Dolphin launch runs the host flatpak with its user directory pinned, so a game played outside RetroDECK writes where the sync looks |
| **Launches** | A save directory an earlier launch baked into the user's own `retroarch.cfg` is repaired before the next launch, because RetroArch honours that value over the `--appendconfig` the launch passes. A PS2 disc serial is read from `SYSTEM.CNF`, and an emulator's BIOS folder is pointed at the tree this app installs firmware into |
| **Emulator tiles** | Provisioned emulators get the same artwork treatment as games, including tiles that already existed |

The per-system result is on the [Save Sync Support Matrix](user-guide/save-sync-support-matrix.md); the reasoning behind
each of the changes is in this repository's ADRs (`docs/adr/`), which record what was measured, on what device, and why
the alternative was rejected.

## How this is built

The code is written by an **AI coding agent working under the maintainer's direction**. The architecture, the design
decisions and the review belong to the maintainer, and every save-path change is verified on real hardware — two
Deck-class handhelds and a RomM server — by making a save on one device and watching the other load it. That practice
is inherited from Tender, which says the same of itself.

Neither project is on the Decky store, for the same reason: the store does not accept plugins whose code is written with
AI assistance.

## Naming

"Tender" is the upstream project's name and is used here only to refer to it. "Arcoon Deck" is this modification's name.
Paths that still say `romm-tender` — the plugin folder under `~/homebrew/plugins`, its data directory, and the release
assets on upstream's tags — are literal identifiers, not the app's name, and are left as they are so an existing install
keeps working.
