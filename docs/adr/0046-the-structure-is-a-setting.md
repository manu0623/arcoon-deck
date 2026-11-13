# 0046 — The structure is a setting, and the app folder is its default

**Status:** Accepted (0.37.0)
**Follows:** 0045 (the plugin is the default runtime)

## Context

With ADR-0045 the built-in runtime is what a fresh install runs on, but its *tree* was
still the EmuDeck shape: `<home>/Emulation/{roms,saves,bios,states}`. That was chosen when
the app was an add-on to a Deck that already had that folder, and it answers a different
question than the one the app asks now: not "where would a Deck keep this?" but "where can
this app guarantee it can read back what it wrote?"

The measured Deck shows the cost. `~/Emulation` is a location other tools also write to —
EmuDeck's launchers, ES-DE, CloudSync — and `Emulation/saves/*` is a symlink farm into each
emulator's real directory, so a backup of it preserves nothing. A user who removes those
tools is left with an app whose data sits in a folder it does not own.

There is also no way to say "use the tree I already have" other than editing four paths by
hand, and no way at all to say "use RetroArch's own folders".

## Decision

`structure` is a setting with four shapes, and `app` is the shipped default:

| structure | roms | saves / states / bios | cores |
|---|---|---|---|
| `app` (default) | `<data>/roms` | `<data>/{saves,states,bios}` | `<data>/cores` |
| `emudeck` | `<home>/Emulation/roms` | `<home>/Emulation/{saves,states,bios}` | RetroArch's |
| `retroarch` | `<data>/roms` | RetroArch's `{saves,states,system}` | RetroArch's |
| `custom` | the per-root settings, falling back to the `emudeck` shape | same | same |

`<data>` is the plugin's own data directory — the one path it already owns, creates and can
write. The four per-root overrides (`roms_dir`, `saves_dir`, `bios_dir`, `cores_dir`) still
win on top of any structure, so "app folder, but BIOS on the card" is expressible.

**`retroarch` keeps ROMs in the app folder** because RetroArch has no ROM root to adopt. The
alternative was inventing one, which is the guessing this codebase refuses elsewhere.

## What a structure change does not do

It does not move files. Existing installs keep their recorded absolute paths (the DB holds
`RomInstall.file_path`), existing saves stay where they are, and the new shape answers for
what is downloaded or launched next. Moving a library is a migration with its own risks —
interrupted copies, a card that unmounts mid-move — and silently starting one because a
dropdown changed is worse than a split tree the user can see.

## Consequences

- A fresh install writes everything it manages under its own data directory. That is the
  app-directory requirement, made true by the default rather than by a one-off.
- A Deck with an EmuDeck library points the app at it with one choice instead of four path
  edits, and keeps its saves where ES-DE and CloudSync expect them.
- A user who wants other RetroArch tooling to see the same saves picks `retroarch` and gets
  RetroArch's own folders — at the cost of the app no longer being the only writer there.
- Cores move with the `app` structure, which means a device upgrading from 0.36.x has its
  cores in RetroArch's directory and finds them "missing" until they are provisioned again.
  The cores are re-downloadable by one button, and that is the honest cost of the change;
  the migration is documented rather than hidden in a shim.
- The structure is read on every path question through `resolve_roots`, so the next launch
  honours a change without a restart. Nothing caches a root it computed in another shape.
