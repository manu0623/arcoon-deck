# 0065 — A RetroDECK marker is not an installation, at any seam

**Status:** Accepted (0.48.25)
**Amends:** 0030 §1 (the catalogue's chooser), 0064 (which fixed this for firmware alone)

## Context

ADR-0064 moved the firmware question off a RetroDECK handle that answered from a tree nothing
boots. The same handle was still being chosen for every other atlas question, because each seam
spelled the choice itself and only the paths adapter had ever asked whether the app was actually
installed:

```python
# adapters/atlas_catalogue.py — one copy, used by two adapters
def first_detected_installation(user_home):
    installations = detect(user_home)
    return installations[0] if installations else None
```

Detection triggers on an arrangement's config marker, and RetroDECK's marker is the **flatpak's**
own file — `~/.var/app/net.retrodeck.retrodeck/config/retrodeck/retrodeck.json` — so removing the
flatpak leaves the marker, and `~/retrodeck` with it. Measured on the reference Deck, which runs
`runtime_mode=builtin` and has no RetroDECK:

```
~/.var/app/net.retrodeck.retrodeck/config/retrodeck/retrodeck.json   present
detect() → handle kind="retrodeck", root "/home/deck/retrodeck"

retrodeck handle                         bare RetroArch flatpak handle
  firmware_inventory():  0 cores           19 cores
  gba requirements:      0                 7
  systems():             0 systems         12 systems
  savefile_location(genesis,
    genesis_plus_gx_libretro.so):
    dir="/home/deck/retrodeck/saves/genesis"   Unresolved(core-not-installed)
```

Its libretro `.info` directory went with the flatpak, so the handle can state nothing and names
directories nothing writes. `savefile_location` is the one that matters most: a directory named
for an emulator that cannot run is invented, not read, and a sync pointed at it carries nothing —
while the arrangement that *is* installed at least declines honestly.

The paths adapter already had the right rule, measured and documented
(`RetroDeckPathsAdapter.runtime_mode`: presence is the flatpak in either tree, with the config as
the second half). Two of the three atlas seams were not asking it.

## Decision

One chooser, `adapters/atlas_installation.py`, and every atlas seam takes its handle from it:

```python
installation_for_runtime(user_home, *, builtin=<runtime_mode is BUILTIN>)
    → detection's order, with a `retrodeck` handle passed over while `builtin`
```

- **`builtin`** — the app's own runtime launches the emulators, so a RetroDECK handle cannot be the
  arrangement the question is about, and a marker left behind is not evidence to the contrary.
  The next arrangement detection found answers (on the reference Deck the RetroArch flatpak), and
  nothing found is `None`, which readers turn into an unresolved answer — never an empty one.
- **`retrodeck`** — detection's first answer stands: its catalogue is the only place its own core
  labels exist (ADR-0045), and a hand-set `runtime_mode` is honoured even where detection would
  not have offered it.
- The order among the non-RetroDECK arrangements is detection's own; offering several is #918, and
  nothing in `services/` learns which one answered.

Wiring: `bootstrap/adapters.py` builds that closure once and hands it to the ES-DE catalogue, the
save-location adapter and both firmware adapters. The firmware adapters had grown their own copy of
the chooser in 0.48.24 — that copy moves here, so the two cannot drift again.

## Consequences

- **Save locations** stop naming `~/retrodeck/saves/<system>` under the app's own runtime. Where the
  installed arrangement declines (`core-not-installed` — a core the plugin bakes into its own tree
  rather than the flatpak's), the answer is "nothing established", which is what the surfaces
  already render, and the owned answers (bank, stated unit) are consulted before this seam anyway.
- **The ES-DE catalogue tier** now has a handle that can answer: 12 systems instead of 0 on the
  reference Deck. Under `builtin` the app's own inventory still answers first (ADR-0036/0045), so
  this changes only what the fallback tier can contribute.
- **Firmware** keeps 0064's behaviour: declarations from an arrangement that has them, presence
  read at the root the app's own launch states.
- The hand-set `runtime_mode=retrodeck` on a machine with no RetroDECK still yields every handle
  detection found, dead marker included: the user said RetroDECK, and overriding that is the silent
  substitution `domain/runtime.py` exists to prevent. Its answers are honest about it —
  `emulator-catalogue-unreadable`, `info-path-unresolved` — rather than silently replaced.
- **Not changed**: `get_retrodeck_status` still reports the *config* health (`ok` here, on a dead
  install), because that is what its union describes and its docstring says so. A user-visible
  "installed" flag belongs with the runtime indicator, not smuggled into a config discriminant.
