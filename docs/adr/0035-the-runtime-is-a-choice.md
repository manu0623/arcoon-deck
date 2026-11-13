# 0035 — The runtime is a choice, and the plugin can drive its own

## Status

Accepted. First slice implemented: recorded here so the remaining slices have a spine.

## Context

Measured on the reference Deck with the app's own adapters, not assumed:

- With RetroDECK's config unreadable, `RetroDeckPathsAdapter` does not fail — it answers
  `~/retrodeck/{roms,saves,bios}`. Those directories exist only because RetroDECK is
  installed. Uninstalling RetroDECK therefore leaves every root pointing at nothing while
  every caller above keeps reporting success.
- The owned launch path already finds a RetroArch without RetroDECK
  (`flatpak run org.libretro.RetroArch`, or `/usr/bin/retroarch` with
  `~/.config/retroarch/cores`) — but that RetroArch held none of the cores the library
  needs, because RetroDECK's cores live inside RetroDECK's own flatpak and leave with it.
- Two libraries coexist on the measured Deck: `/home/deck/retrodeck/roms` and
  `/home/deck/Emulation/roms`. Eden's saves are already under `Emulation`.

So the dependency is real, silent, and worth naming: the app was written to *read*
RetroDECK, not merely to launch through it.

## Decision

The runtime is a value, `domain.runtime.RuntimeMode` — `retrodeck`, `standalone`, or
`auto` — decided from the user's setting and what is installed, and read everywhere.

- **Roots**: `auto` follows the installation. A standalone runtime owns an EmuDeck-shaped
  `<home>/Emulation` tree (`roms`, `saves`, `bios`, `states`) with the owned runtime's
  cores directory, and each root can be overridden by a `<root>_dir` setting. A cleared
  override falls back rather than pointing at an empty string.
- **Launcher**: `resolve_launch_backend` reads the setting through the runtime, so a
  standalone Deck bakes the owned RetroArch launch instead of a
  `flatpak run net.retrodeck.retrodeck` that cannot exec. An explicit `"retroarch"` always
  wins.
- **An explicit choice outranks detection.** A user who selects `retrodeck` keeps it even
  when the probe sees nothing, because the probe reads one config path and the user may
  point at another tree.

Chosen for the standalone tree: `/home/deck/Emulation`, because it already exists on a
Deck whose standalone emulators (Eden, Dolphin, Cemu) keep their saves there; RetroArch
Flatpak as the owned runtime, because the runner adapter already starts it directly; and
cores supplied by the plugin itself, because RetroDECK's depart with RetroDECK.

## Consequences

- Nothing changes on a device that has RetroDECK: `auto` resolves to `retrodeck`, the
  roots are the same ones `retrodeck.json` names, and the launcher is unchanged.
- The remaining RetroDECK couplings are now named work, in dependency order:
  1. **inventory** — the emulator list and per-platform defaults still come from the live
     `es_systems.xml`; without it the picker is empty and defaults vanish;
  2. **launch argv** — every non-host font still bakes
     `flatpak run net.retrodeck.retrodeck -e`, so standalones other than the
     `--host` form (Switch) need real binary argv from the manifest or the scanner;
  3. **cores** — the plugin must download and update the cores its owned runtime loads,
     with integrity checks, or a fresh Deck has a RetroArch that can run nothing.
- `states_path` has no override key yet; it follows the tree. Adding one is a one-line
  change when a surface needs it.
