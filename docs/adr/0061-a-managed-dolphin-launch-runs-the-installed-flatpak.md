# 0061 — A managed Dolphin launch runs the installed flatpak, not RetroDECK's placeholder

**Status:** Accepted (0.48.20)
**Follows:** 0034 (the manifest states the layout), 0043 (an owned launch states its own save),
0060 (a Wii save is a title directory in Dolphin's user tree).

## Context

ADR-0060 made Wii a managed platform, and the next launch of Mario Galaxy 2 died: the plugin
log shows `Session start` at 18:02:49.301 and `Session end` at 18:02:49.436 — 135 ms — and
Dolphin's own log stayed empty at 0 bytes, so the emulator never started.

The shortcut's stored launch options say why:

```
/home/deck/.local/share/romm-tender/bin/rom-launcher
  flatpak run net.retrodeck.retrodeck -e "%EMULATOR_DOLPHIN% -b -e %ROM%" "<rom>"
```

A managed platform's argv comes straight from the manifest (`active_core_resolver` returns it
before consulting the catalogue), and the provisioner wrote Dolphin's ES-DE command
`%EMULATOR_DOLPHIN% -b -e %ROM%` — copied from the GameCube row that predates the plugin
installing Dolphin itself. The shortcut layer bakes every `standalone` invocation as
`flatpak run net.retrodeck.retrodeck -e "<command>"`, and inside RetroDECK's sandbox
`%EMULATOR_DOLPHIN%` resolves to RetroDECK's own Dolphin. This Deck has no such install: the
Dolphin that plays these games is the host flatpak (`org.DolphinEmu.dolphin-emu`) the plugin
provisioned. So the wrapper execs a binary that is not there and exits at once.

The command that works was already on the machine: the New Super Mario Bros Wii shortcut,
written before the manifest existed, carries

```
/usr/bin/flatpak run org.DolphinEmu.dolphin-emu -b -e "<rom>"
```

Measured working: that title ran a session and wrote a save with it.

## Decision

The manifest's Dolphin argv — for GameCube and Wii alike — is the host-spawn form:

```json
"launch": [
  "%EMULATOR_FLATPAK-SPAWN%", "--host", "/usr/bin/flatpak",
  "run", "org.DolphinEmu.dolphin-emu", "-b", "-e", "%ROM%"
]
```

`resolve_emulator_invocation` recognises the spawn token and bakes bare argv
(`/usr/bin/flatpak run org.DolphinEmu.dolphin-emu -b -e`), and `build_launch_options` appends
the real ROM path itself — the same string the working shortcut holds. A test loads
`scripts/provision_layout.py` and asserts that the argv it writes renders to exactly that
prefix for both platforms, so the provisioner and the shortcut layer cannot drift apart
again.

## Consequences

- A newly provisioned GameCube or Wii launch runs the flatpak the plugin installed, needing no
  RetroDECK install at all.
- The `%EMULATOR_DOLPHIN%` spelling is gone from the provisioner. It was a claim about
  RetroDECK's sandbox that stopped being true the moment the plugin installed its own Dolphin.
- `-b -e %ROM%` is the flag pair measured on this Deck's working shortcuts; the `-C
  Core/GCIFolderAPath` question ADR-0034 records as open is still open, so no save-path flag
  rides here.
- An existing shortcut keeps whatever it holds until the Play funnel re-confirms it, which it
  does on every press; the stored value above was overwritten by that same mechanism, so the
  fix reaches the device without a manual edit of `shortcuts.vdf`.
