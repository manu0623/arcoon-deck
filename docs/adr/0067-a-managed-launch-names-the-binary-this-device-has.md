# 0067 — A managed launch names the binary this device has

**Status:** Accepted (0.48.28)
**Follows:** 0034 (the layout is owned by the plugin), 0061 (a managed Dolphin launch runs the
installed flatpak), 0062 (a provisioner run keeps the platforms it does not name).

## Context

A portability audit asked whether this plugin could be installed fresh on another device. The
runtime answered well — settings ship with no paths, the data root is the plugin's own, device
identity is read from the host, and a standalone save base is read out of the emulator's own
config. One file did not: `scripts/provision_layout.py`, the only thing that writes a managed
platform's launch, spelled this machine's directories outright.

```python
SWITCH_LAUNCH = ["%EMULATOR_FLATPAK-SPAWN%", "--host", "/home/deck/Applications/Eden.AppImage", "-f", "-g", "%ROM%"]
DOLPHIN_LAUNCH = ["%EMULATOR_FLATPAK-SPAWN%", "--host", "/usr/bin/flatpak", "run", "org.DolphinEmu.dolphin-emu", …]
```

A managed entry's argv is baked into the shortcut verbatim, so a device whose user is not
`deck`, whose Eden lives elsewhere, or whose flatpak is not at `/usr/bin/flatpak` got a launch
line that cannot exec — the manifest would be written successfully and the game would exit at
once. The failure is silent until someone presses Play, and it is the one class of bug the
manifest exists to prevent: ADR-0061 already removed a placeholder nothing resolved from these
same lines.

## Decision

The provisioner discovers the two programs it names, once per run, before it writes anything.

- **Candidates come from the plugin's own inventory**, read through `domain.owned_inventory`
  (ADR-0041: the document has one reader). Eden's `host.binaries` are `~/Applications/Eden.AppImage`
  and `~/Applications/eden.AppImage`; Dolphin's flatpak id is `org.DolphinEmu.dolphin-emu`.
  `~/…` is a placeholder expanded against `--home`, never against the reading process's home —
  the same rule `adapters/owned_catalogue.py` already states for this document.
- **The flatpak executable follows the rule the plugin already uses**: `/usr/bin/flatpak` when
  it is a file, else `flatpak` from `PATH`. The absolute form wins because the launcher's `PATH`
  is Steam's, not a login shell's.
- **A missing program refuses the run.** The document is built before the tree is created, so a
  refusal changes nothing on disk; the message names the paths that were searched.
- **`--home`** was added so a run can be pointed at the user it is provisioning for; `--root`
  now defaults to that home's data root.
- **Nothing else about the argv changes.** Dolphin keeps its host-spawn form (`--host <flatpak>
  run <app id> -b -e`) and Eden keeps the AppImage form that was measured to reach Steam's
  display. Only *which* binary they name is now the device's answer.

The scripts' functions take a `HostBinaries` value, so every caller states what the device has
rather than asking the filesystem inside `build_manifest`; the tests pass it explicitly and no
test depends on the machine running it.

## Consequences

- A device whose home is not `/home/deck` provisions a Switch entry that names its own Eden
  install, and a GameCube/Wii entry that names its own flatpak.
- A flatpak-only Eden install is **refused**, not guessed: the inventory states a flatpak id for
  Eden, but the measured Switch launch form is the AppImage, and inventing a second form here
  would be a claim no measurement supports. The refusal names the AppImage paths it looked for,
  so the remedy (install the AppImage from Emulators & Cores, or provision on the device that
  has it) is readable from the message.
- The `.AppImage` a Switch entry names is the inventory's own first candidate, so an AppImage
  installed by the plugin under that name is found without configuration.
- Existing manifests are untouched by this: a run that does not name a platform keeps its entry
  (ADR-0062), including one written with an old absolute path.
