# 0036 — The plugin ships its own emulator inventory

## Status

Accepted. Read as a fallback behind ES-DE's catalogue (ADR-0020 keeps the live
`es_systems.xml` as the primary source while it exists).

## Context

Every emulator the picker offers, and every per-platform default, came out of ES-DE's live
`es_systems.xml`. That file belongs to ES-DE and ships inside RetroDECK, so removing
RetroDECK removes the catalogue as well: `get_emulator_options` answers `available: False`
for every system, `get_default_emulator` returns `None`, and every launch degrades to the
plain launcher that is no longer installed. Measured on the reference Deck, this is total
loss of emulator selection, not a degraded picker.

ADR-0035 made the runtime and its roots a choice. The inventory is the second half of that
decision: a runtime you own is useless if the plugin cannot say what it can launch with.

## Decision

The plugin ships `defaults/emulator_inventory.json` — a curated, in-repo document mapping
each platform to its accept-list and to the emulators it can launch with — and reads it
**only where ES-DE's catalogue cannot answer**. ES-DE stays primary: a device with
RetroDECK keeps resolving from the live catalogue, including any emulator a RetroDECK
update adds.

Two forms make the inventory rows identical to ES-DE rows:

- **libretro** → synthesised into ES-DE's own command shape
  (`%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/<core>.so %ROM%`), so the classifier keeps one
  definition of "libretro" and the bake builds the owned RetroArch command from `core_so`.
- **standalone** → `%EMULATOR_FLATPAK-SPAWN% --host <binary> <args> %ROM%`, the form the
  bake already renders as bare host argv (`domain.shortcut_data._host_argv`). A standalone
  emulator is therefore a binary path plus arguments, not a command only a sandbox can
  resolve.

The document states nothing about a device it cannot know. Two probes decide whether a row
is usable: the binary exists on disk for a standalone, and the core exists in the runtime's
cores directory for a libretro. A miss downgrades the row to `needs_setup` /
`not_installed` — visible with its reason, never the default, never baked. A `RETRODECK`
runtime answers "installed" for every core, because its RetroArch and cores live inside
its flatpak where the probe cannot see them; answering "missing" there would disable every
libretro row on a working device.

Order in the document is preference order, the same rule ES-DE's declaration order already
follows, so the default is the first bakeable entry in both sources.

## Consequences

- A Deck without RetroDECK now has a picker, a per-platform default, and a launch command
  that runs a real binary. Switch resolves to Eden host-direct even with no catalogue.
- The inventory is curated data and will drift from upstream emulator names and arguments.
  It is in-repo (like `config.json`) rather than vendored, because a vendored snapshot
  cannot be refreshed when the upstream file is gone — the reason `bios_registry.json` was
  removed.
- Rows the inventory cannot express stay out: a system the document does not list still
  needs either ES-DE or an inventory entry. A Flatpak-only emulator is no longer one of
  these — see ADR-0038, which gives it a launch form and an installedness probe.
- Cores are still supplied by the user's machine: the owned runtime's cores directory is
  probed, not populated. Provisioning them is the next slice.
