# 0039 — The plugin installs the runtime it launches with

## Status

Accepted. Completes the stand-alone story begun in ADR-0035/0036/0037/0038.

## Context

The reference Deck was wiped of emulators on purpose, to test exactly this: does the app
stand alone? With every emulator gone, three things were still missing in sequence — a
runtime to launch (RetroDECK absent means its RetroArch is gone), cores for that runtime
(ADR-0037 supplies them), and a launch form that reaches them.

A fourth gap surfaced while wiring it: the owned RetroArch launch only carries the
plugin's save redirect when the save bank is on, and the bank shipped off by default. So a
standalone Deck could have installed RetroArch and every core and still bake the RetroDECK
form — a launch into a program that no longer exists. The bank is what makes the owned
launch's saves land where the sync layer reads; in a standalone runtime it is not optional.

## Decision

`CoreProvisioningService.ensure_runtime()` installs the owned runtime — the RetroArch
Flatpak — when the runtime is `STANDALONE` and nothing provides one:

    flatpak install --user -y flathub org.libretro.RetroArch

- **`--user`**: no password, so it can happen inside Game Mode. A system-wide install would
  need a prompt nothing in Game Mode can show, and lands where the owned runner does not
  look.
- **`-y`**: answers the one prompt an unattended install cannot.
- **A `RETRODECK` runtime is `skipped`**, not installed: its RetroArch lives inside its own
  flatpak, and a second one would be a program nothing launches.
- Installedness is a directory probe over both flatpak trees, re-checked *after* the
  command: `flatpak install` exits non-zero when the transaction finds nothing to do, and
  the state is what matters, not the exit code.

`ensure_for_system` calls `ensure_runtime` first and reports both outcomes, so one callable
takes a bare Deck from "nothing installed" to "this platform launches". A failed runtime
install does not stop the cores — they are still the right files for whenever a runtime
appears — but it does make the overall answer fail.

The save bank is enabled whenever the runtime is `STANDALONE`, not only when the user turns
it on: the plugin launches that runtime itself, so the redirect is the difference between a
save the sync layer can find and a save written somewhere nothing reads.

## Consequences

- A Deck with no RetroDECK and no emulators can install its runtime and its cores from the
  plugin, needing no terminal.
- Standalone saves live in the plugin's own bank (`<data>/saves/<platform>`), because that
  is what the owned launch redirects to. The `<home>/Emulation/saves` root remains the
  default for emulators that write their own tree (Dolphin's cards, Eden's title folders).
- Standalone emulators are not installed by this: Eden and Dolphin are AppImages or
  Flatpaks the inventory *describes* (ADR-0038), not programs the plugin fetches. Adding an
  install step per emulator is a separate decision, because it means tracking each one's
  release channel.
- Nightly cores are unpinned (ADR-0037), and now so is the runtime, which follows Flathub's
  stable branch.
