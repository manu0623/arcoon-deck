# Packaged defaults

Reference data that ships inside the plugin. The Decky CLI flattens this directory into the plugin root at package time,
so the runtime reads these files by their bare name (no `defaults/` prefix); do not move or rename them.

## `config.json` — in-tree default

The platform-slug map and other default configuration. It is maintained in this repo (not vendored) and carries no
checksum gate.

## `emulator_inventory.json` — the plugin's own catalogue (ADR-0036)

Platform → accept-list and the emulators it can launch with, read only where ES-DE's
`es_systems.xml` cannot answer (a device without RetroDECK). A standalone entry states
binary candidates and/or a Flatpak app id; a libretro entry states the core name. Order is
preference order. Editing this file needs no code change.

## What used to live here

`bios_registry.json` — a frozen snapshot of which firmware files each platform and libretro core wanted — was vendored
here from an [emu-atlas](https://github.com/danielcopper/emu-atlas) release and read at runtime by `FirmwareService`. It
is gone: the file no longer exists upstream, so the snapshot could never be refreshed again and drifted a little further
with every RetroDECK update. Firmware requirements are now read live off the installed cores through the vendored
resolver (`py_modules/_vendor/atlas/`, provenance in [`_vendor/README.md`](../py_modules/_vendor/README.md)), which is
data no snapshot has to keep in step.
