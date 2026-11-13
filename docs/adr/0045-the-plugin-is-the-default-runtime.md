# 0045 — The plugin is the default runtime

**Status:** Accepted (0.36.0)
**Follows:** 0035 (the runtime is a choice), 0039 (the plugin installs its runtime), 0043 (an owned launch states its own save)

## Context

ADR-0035 made the runtime a value, and gave `"auto"` as the shipped default: follow what is
installed, which on a Deck with RetroDECK means RetroDECK. `launch_backend` shipped as
`"retrodeck"` for the same reason. Both were honest while this plugin was an add-on to a
RetroDECK install — and both are backwards for what it is now: an app that brings its own
runtime, its own cores, its own inventory and its own save answers.

The cost of that inversion is not theoretical. With `"auto"` on a RetroDECK Deck, the two
things this plugin does best become unreachable:

- **Roots.** Every path comes out of `retrodeck.json`. The plugin's own save bank, appendconfig
  and core tree are still built and written, but nothing launches through them.
- **Answers.** The ES-DE catalogue — which exists only inside RetroDECK or an EmuDeck install —
  answers instead of the plugin's own inventory, so the machine that most needs the built-in
  path is exactly the one that never exercises it.

A user who removes RetroDECK gets the app's own world by accident. A user who keeps it never
does.

## Decision

The shipped defaults are the plugin's own runtime:

| setting | shipped default | meaning |
|---|---|---|
| `runtime_mode` | `"builtin"` | the app's own libretro runtime and cores (`<home>/Emulation/*`, overridable per root) |
| `launch_backend` | `"retroarch"` | the plugin starts RetroArch with its own core path and appendconfig |

Under `"builtin"` the emulator catalogue is asked in the app's own order — shipped inventory
first, ES-DE second — and nothing RetroDECK-shaped is consulted for a question the app can
answer itself. A `"retrodeck"` runtime flips that order back.

`"retrodeck"` and `"auto"` remain selectable — RetroDECK is a **fallback the user chooses**,
never a requirement and never the default. The choice is surfaced in Settings → Emulators &
Cores as three buttons, so it is reversible without editing `settings.json`.

**The vocabulary is load-bearing:** *built-in* means the libretro runtime and cores this app
downloads and launches itself; *standalone* means an emulator the app did not install (Eden,
RPCS3, a flatpak). A runtime called "standalone" would collide with the second meaning, which
is why the mode is `"builtin"`.

`_migrate_v13_to_v14` applies this to existing installs: a stored `"auto"` (the old default,
which no user typed) becomes `"builtin"`; a stored `"retrodeck"` is an
answer the user gave and is left alone. A file holding `"standalone"` — the 0.36.0 spelling
of the same decision — is read as `"builtin"` (both by the migration and by the resolver).

## What this does not change

- **The save bank gate.** `save_bank_enabled()` already returned true under a built-in
  runtime; this ADR does not change that expression, it changes which runtime a fresh install
  is on when it is evaluated.
- **RetroDECK support.** Every path that worked under `"retrodeck"` still does. Nothing is
  deleted, only demoted.
- **The catalogue's existence.** ES-DE and the atlas vendor tree stay as the last-resort tier
  for platforms the plugin's inventory cannot answer — with the owned answers ahead of them
  (ADR-0041, ADR-0043, ADR-0044).

## Consequences

- A fresh install launches through RetroArch with our core and our appendconfig, so its save
  answer is the one the sync layer can act on — the "own-first" claim becomes true on the
  first play, not after an uninstall.
- A RetroDECK user who *wants* RetroDECK's launcher has one extra step; the alternative was
  every other user paying that cost silently.
- The migration cannot distinguish "never decided" from "deliberately chose auto". It favors
  the former because `"auto"` was the default for every install that holds it, and the
  setting is one click away from being restored.
- Two roots can now disagree in a new way: a Deck with RetroDECK installed but running
  built-in runtime keeps its library under `<home>/Emulation`. That is the intended shape, and the
  existing per-root overrides (`roms_dir`, `saves_dir`, `bios_dir`, `cores_dir`) are how a
  user points it at the tree that already has their ROMs.
