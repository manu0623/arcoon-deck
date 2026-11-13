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
  answers instead of the plugin's own inventory, so the machine that most needs the standalone
  path is exactly the one that never exercises it.

A user who removes RetroDECK gets the app's own world by accident. A user who keeps it never
does.

## Decision

The shipped defaults are the plugin's own runtime:

| setting | shipped default | meaning |
|---|---|---|
| `runtime_mode` | `"standalone"` | the plugin owns its tree (`<home>/Emulation/*`, overridable per root) |
| `launch_backend` | `"retroarch"` | the plugin starts RetroArch with its own core path and appendconfig |

`"retrodeck"` and `"auto"` remain selectable — RetroDECK is a **fallback the user chooses**,
never a requirement and never the default. The choice is surfaced in Settings → Emulators &
Cores as three buttons, so it is reversible without editing `settings.json`.

`_migrate_v13_to_v14` applies this to existing installs: a stored `"auto"` (the old default,
which no user typed) becomes `"standalone"`; a stored `"retrodeck"` or `"standalone"` is an
answer the user gave and is left alone.

## What this does not change

- **The save bank gate.** `save_bank_enabled()` already returned true under a standalone
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
  standalone keeps its library under `<home>/Emulation`. That is the intended shape, and the
  existing per-root overrides (`roms_dir`, `saves_dir`, `bios_dir`, `cores_dir`) are how a
  user points it at the tree that already has their ROMs.
