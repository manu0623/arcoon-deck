# 0069 — A standalone emulator's BIOS folder is pointed at this app's tree

**Status:** Accepted (0.48.31).
**Follows:** 0051 (a standalone emulator's save folder is linked to the plugin's tree), 0064 (a
builtin firmware reading is rooted at the app's own BIOS).

## Context

A PlayStation game was started from its library tile with DuckStation chosen, and the game
window closed about two seconds after it opened. The plugin's own log recorded three attempts
in ten seconds, none of them lasting 2.5 s:

```
[2026-11-13 21:22:12,278][INFO]: [FE] Session start: romId=5416, appId=3341772642
[2026-11-13 21:22:14,059][INFO]: [FE] Session end: romId=5416
```

`coredumpctl` was empty, so nothing crashed. The shortcut's launch command was the right one —
`rom-launcher` handing the AppImage the ROM through `-fullscreen -batch` — and running that
exact command from a shell reproduced the close in a second, with DuckStation's console output
on the terminal:

```
I/BIOS: Searching for a NTSC-U BIOS in '/run/media/deck/SR01T/Emulation/bios'...
W(FindBIOSImageInDirectory): Skipping 'readme.txt': incorrect size
I/InputManager: Device 'SDL-0' disconnected
I/VideoThread: Shutting down video thread...
```

No `I/System: Using BIOS` line, no GPU device: the emulator stopped before boot because it
found no PlayStation image. `-batch` — the flag the shortcut is baked with so the tile's session
ends with the emulator — exits instead of opening the BIOS-missing dialog, which is why the
failure looked like a crash from Game Mode.

The BIOS was not missing from the machine. The plugin had downloaded SCPH-5500/5501/5502 into
`~/.local/share/romm-tender/bios/psx` hours earlier; DuckStation was searching
`/run/media/deck/SR01T/Emulation/bios`, an SD card's per-system tree holding no `scph` file at
all. Pointing `SearchDirectory` at the plugin's folder in the same settings file booted the same
game in 1.0 s:

```
I/BIOS: Searching for a NTSC-U BIOS in '/home/deck/.local/share/romm-tender/bios/psx'...
I/System: Using BIOS: SCPH-5501, 5503, 7003 (v3.0 11-18-96 A)
I/System: System booted in 1010.82ms
```

The cause is the save link's, one asset over. The app's own launch tells RetroArch where its
system directory is, so a libretro core reads the firmware the plugin installed. A standalone
emulator is told nothing: its BIOS folder is its own setting, and nothing in a launch argument
can override it. The plugin was therefore installing firmware that only the cores could see.

## Decision

At startup, after an install, and again before a platform's game is launched, every standalone
emulator that **states a BIOS folder in its settings file** has that folder pointed at
`<bios root>/<platform>` — the same tree the firmware install writes.

`domain/emulator_bios_home.py` holds the one measured fact this rests on, in a table keyed by
emulator id:

```python
BIOS_DIRECTORY_KEYS = {"duckstation": ("BIOS", "SearchDirectory")}
```

An emulator absent from that table is never written to. A guessed section name would have the
plugin editing a file for a reason it cannot state, and the table is the line between the two.

Three refusals keep a working deck working:

- **No BIOS root.** While another runtime drives the machine the plugin installs no firmware
  there, so it names no folder (`owned_bios_root` answers `None`).
- **The folder is missing or empty.** A user whose emulator already finds its own BIOS must not
  be pointed at nothing.
- **No settings file.** An emulator that has never run has written nothing to point; creating
  one would be inventing a config.

The write is one line of an INI the emulator owns, made by walking the text and replacing the
one key inside the one section — DuckStation's `settings.ini` holds its GPU backend, pad
bindings and per-game overrides, and a parser round-trip would reformat all of it. It is written
beside the original and renamed over it, so a crash mid-write cannot leave an emulator with no
settings.

An emulator that plays several systems is left alone rather than half-right: one folder per
emulator cannot be two platforms' BIOS trees, and aiming the PSX search at the PS2 tree would be
worse than the status quo.

## Verification

- On the reference Deck, the same PSX game boots from DuckStation in 1.0 s with the plugin's
  folder named, and closed in under 2 s with the SD card's folder named — reproduced both ways
  before the code was written.
- `tests/domain/test_emulator_bios_home.py`, `tests/adapters/test_emulator_bios_home.py` and
  `tests/services/test_emulator_bios_homes.py` pin the rule, the rewrite (including a same-named
  key in another section and an absent section) and the selection.
- After deployment the plugin's startup pass reports the emulator's folder as `already`, since
  the measurement had already pointed it.

## Consequences

- A BIOS the plugin installs is now readable by the standalone emulator it installed, on the
  first launch rather than after a manual settings change.
- A second emulator that keeps a BIOS folder joins the table once its settings file has been
  read; nothing else changes.
- The emulator's own choice of folder is overwritten while the plugin's tree holds that
  platform's images. A user who keeps BIOS somewhere else and never installs it through the
  plugin keeps their setting, because an empty plugin folder is never pointed at.
