# 0038 — A Flatpak emulator is a host command, not a missing binary

## Status

Accepted. Amends ADR-0036 (which listed flatpak-only emulators as unsupported).

## Context

The inventory described a standalone emulator as a binary path plus arguments, and a
standalone whose binary was not found read `needs_setup / not_installed`. Many emulators on
a Deck are installed as a Flatpak and never place a binary anywhere the plugin can see —
measured on the reference Deck, Dolphin and PPSSPP are installed exactly this way, and
their GameCube and PSP rows were unusable for no reason beyond the inventory's vocabulary.

## Decision

A standalone entry may state a Flatpak application id (`host.flatpak`). Resolution tries
the binary paths first and the Flatpak second, in one row: one emulator is one pick, however
it happens to be installed.

The launch form is `%EMULATOR_FLATPAK-SPAWN% --host <flatpak> run <app-id> <args> %ROM%`,
which the existing bake rule (`domain.shortcut_data._HOST_SPAWN_RE`) renders as bare host
argv — `flatpak run org.DolphinEmu.dolphin-emu -b -e <rom>`. Nothing in the bake changes:
"host" means the launcher's own process runs the command directly, and `flatpak` is a host
program. The Flatpak's own sandbox is the application's, entered by `flatpak run`, which is
exactly how the user launches it by hand.

Installedness is a directory probe, not a subprocess: `/var/lib/flatpak/app/<id>` or
`~/.local/share/flatpak/app/<id>`. The picker asks on every menu open and `flatpak list`
spawns a process per row; two `isdir` calls do not. The executable is named absolutely
(`/usr/bin/flatpak`) when present, because the shortcut's `PATH` is Steam's rather than a
login shell's.

## Consequences

- GameCube and PSP rows on a Deck with only the Flatpak builds become bakeable, and their
  default launches that build — verified on the reference Deck, where both Flatpaks are
  installed and no binary exists.
- An application id is data: a wrong id is never a crash, only a row that stays
  `not_installed`. Ids are stated in the inventory document and can be corrected there
  without code changes.
- A Flatpak that is installed but whose app id the document omits is still missed. The
  scanner (`adapters/emulator_scan.py`) knows about installed flatpaks for the picker's
  external rows; joining that inventory to this one would remove the guesswork, and is not
  part of this cut.
