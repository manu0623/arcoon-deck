# 0042 — The owned launch command carries no placeholder

**Status:** Accepted (0.35.24)
**Follows:** 0039 (the plugin installs its own runtime), 0037 (its own cores).

## Context

`%ROM%` is ES-DE's placeholder. On the RetroDECK path it is the launcher's job:
`run_game.sh` substitutes the ROM path for the trailing placeholder in the `-e` override.
Every bake rule is written around that — a bakeable command must end in `%ROM%`
(`domain.emulator_commands`), and `build_launch_options` then appends the quoted path for
the paths where nothing substitutes anything.

The owned launch (`domain.retroarch_runner.retroarch_command`) kept the placeholder and
also got the appended path, because it is rendered by the same
`resolve_emulator_invocation` → `build_launch_options` pair. The shortcut therefore read:

```
flatpak run org.libretro.RetroArch -L …/mgba_libretro.so --appendconfig=…/retroarch-gba.cfg %ROM% "/home/deck/Emulation/roms/gba/…gba"
```

RetroArch takes the first non-flag argument as the content path, so it tried to load a file
called `%ROM%`. Measured on the reference Deck: the game did not start, Steam returned to
the library, and RetroArch wrote no log at all — the process dies on the bogus content
before it opens one. Nothing in the plugin's own log showed the failure either; the
shortcut text was the only evidence.

The host-binary path already had this rule (`_host_argv` strips the trailing placeholder
and says why: "nothing substitutes placeholders on this path any more"). The owned
libretro path was the one that did not.

## Decision

`retroarch_command` stops at the appendconfig: it renders `prefix -L <core>.so` plus the
optional `--appendconfig=`, and `build_launch_options` supplies the content path as it does
for every other composition. A test pins `"%ROM%" not in command`, so the placeholder
cannot come back by accident.

## Consequences

- An owned launch is plain argv: `flatpak run org.libretro.RetroArch -L <core> [--appendconfig=…] "<rom>"`.
  The cores dir is still spelled out, because the flatpak's RetroArch is the one that owns it.
- Shortcuts baked before this release carry the broken form. The startup reconcile compares
  each shortcut's applied options against the freshly computed ones, so a plugin reload
  rewrites them; nothing has to be re-downloaded or re-synced.
- The RetroDECK path is untouched: it still ends in `%ROM%` inside `-e`, which is what
  `run_game.sh` substitutes.
