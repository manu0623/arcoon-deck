# 0041 — The accept-list is dot-prefixed in both sources

**Status:** Accepted (0.35.23)
**Supersedes:** nothing. Follows 0036 (the inventory read only where ES-DE cannot answer).

## Context

`domain.rom_files.is_launchable_target` decides whether a download left something the
system can boot. It compares `os.path.splitext(file_path)[1].lower()` — `.gba` — against
the target system's accept-list, and its docstring already states that contract: ES-DE's
per-system `<extension>` set, "lowercased and dot-prefixed".

ES-DE's `es_systems.xml` spells them `.gba .agb .bin`, so the ES-DE path always agreed.
`defaults/emulator_inventory.json` (ADR-0036), written by hand, spells them bare —
`"gba"`, `"sfc"`, `"iso"` — because that reads better in a data file. The adapter passed
the tokens through unchanged, so on a device with no ES-DE the accept-list was
`{"gba", "agb", "bin"}` and `.gba` was absent from it.

The consequences were not cosmetic:

- Every download from an owned platform was recorded `launchable=0`, its shortcut was
  baked with no launch command, and pressing Play raised *"This download has no file the
  emulator can launch. The files are on disk"* — for a plain single-file `.gba` ROM.
- `system_supports_m3u` asks `".m3u" in get_supported_extensions(...)`, so every
  owned platform answered "no playlists" and multi-disc `.m3u` handling never engaged.

The empty-list case hid this in review: `is_launchable_target` returns `True` for an
empty accept-list ("a missing answer must never turn a working install into an
unlaunchable one"), and the old tests exercised only the ES-DE spelling.

## Decision

The dot is applied **in the adapter** (`OwnedCatalogueAdapter.get_supported_extensions`),
not in the data file. One seam owns the spelling, both sources answer in the shape their
callers already expect, and the inventory stays readable. The normaliser is idempotent
(`.GBA` → `.gba`, `gba` → `.gba`), so a future hand edit that adds the dot cannot
double it.

A verdict written before the fix is repaired at startup:
`StartupHealingService.reconsider_launchability` re-runs the same predicate over the same
recorded path for every install stored `launchable=False`, and applies only
`False → True`. That is a recomputation of the download's verdict, not a second opinion,
so a genuine withhold (a `.pkg` installer, a bare disc track) survives — those tokens are
still absent from their system's list. Nothing is ever demoted: a proven working install
never loses its command to a later list change.

## Consequences

- A downloaded ROM is launchable again on a device with no ES-DE, which is the whole
  point of standing on the inventory rather than RetroDECK.
- `.m3u` playlist handling now engages on owned platforms, because the same list answers.
- Repairs happen at startup, before anything reads a shortcut's launch command, so a
  sync or a shortcut re-bake sees the corrected verdict without the reader doing anything.
- The accept-list's spelling is now a property of one method; a second source added later
  must answer dot-prefixed or add itself to that method.
