# ADR-0054 — A standalone command is baked in the spelling its emulator accepts

**Status:** accepted

## The problem

A standalone launch is baked from free text: whatever an ES-DE `<command>` template,
a distribution's launcher script or a catalogue row says becomes the Steam shortcut's
launch options, verbatim. When that text spells a switch the emulator refuses, the game
never starts and nothing else in the funnel can see why. Measured on the reference
Deck, selecting standalone PCSX2 for a PS2 game produced this shortcut command:

```
/usr/bin/flatpak run net.pcsx2.PCSX2 --fullscreen --nogui -- "/home/deck/.local/share/romm-tender/roms/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso"
```

and PCSX2 2.8.2 answered `Unknown parameter: '--fullscreen'` and exited before the game
was parsed. The same build accepts the single-dash form: its own option list states
`-fullscreen`, `-nogui`, `-batch`, `-bigpicture`, `-fastboot`, `-slowboot`, and keeps a
bare `--` as "no more arguments"; this Deck's ES-DE ps2 entry is `%EMULATOR_PCSX2% -batch
%ROM%` and EmuDeck's launcher line `-batch -fullscreen`.

So the plugin was baking a command that could not start the game, and the stored
shortcut kept it because the baked value *was* that command — the frontend's pre-launch
re-confirm (`src/utils/launchOptionsReconcile.ts`) faithfully copied the broken text
onto the shortcut before every launch.

## The decision

**A standalone command is corrected into the spelling its emulator accepts before it is
baked.** `domain.emulator_switches.normalise_switches` holds the one table of measured
refusals (`SWITCH_SPELLINGS`), keyed on the emulator name token the command itself
carries (`net.pcsx2.PCSX2`, `pcsx2-qt`, `%EMULATOR_PCSX2%` all match `pcsx2`), and
rewrites whole switch tokens only: `--fullscreen` → `-fullscreen`, `--nogui` → `-nogui`,
`--batch` → `-batch`, `--bigpicture` → `-bigpicture`, `--fastboot` → `-fastboot`,
`--slowboot` → `-slowboot`. Quoted paths, `%PLACEHOLDER%`s and a bare `--` pass through
untouched.

It is applied at the two points where command text becomes something a person sees or
Steam runs:

- `domain.emulator_commands.option_to_invocation` — the picker's row bakes the accepted
  spelling, so the menu never advertises a command that cannot start;
- `domain.shortcut_data.build_launch_options` — the single place a launch command becomes
  a shortcut's options, so every bake (launch, platform pin, per-game pin, uninstall
  check) is corrected, and the frontend's pre-launch confirm-set copies the corrected
  value onto the live shortcut. That confirm-set is the mechanism that heals a stored
  shortcut holding a rejected command: it runs before every launch and writes the baked
  value unconditionally.

Only emulators whose refusal was measured are listed. A guess would bake a different
command on no evidence — the same mistake as guessing a save path.

## What this does not do

- It does not change *which* emulator a pick resolves to. The ps2 save layer's
  `the catalogue offers no entry labelled 'LRPS2'` is a separate defect: the label the
  picker stores does not exist among the catalogue's emulator entries, so no save shape
  is ever asked for.
- It does not add a PS2 `SavePoint`. PS2 still answers `save_shape_unsupported`, which
  is why a successful LRPS2 session uploaded nothing.
- It does not rewrite a shortcut whose *emulator* is wrong, only the spelling of the
  switches its emulator refuses. A command naming a different emulator than the one
  baked is replaced wholesale by the confirm-set, not repaired in place.
