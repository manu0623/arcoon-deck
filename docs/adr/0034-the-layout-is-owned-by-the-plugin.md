# The layout is owned by the plugin, and a provisioner writes it down

## Status

**Proposed, partially implemented.** The contract, its reader (`domain/layout_manifest.py`,
`adapters/layout_manifest.py`), the launch bake and the save answer it feeds, and a provisioner v0
(`scripts/provision_layout.py`, with `--check` and explicit `--adopt`) are in the tree and tested. What is **not** yet
established is that a real launch obeys the manifest end to end on the reference Deck — the first increment, GameCube
only, which is what proves or falsifies the direction. Two things remain explicitly unmeasured: whether this Dolphin
build accepts a save-path override on its command line (`-C Core/GCIFolderAPath=…`), and whether that override's region
segment behaves the way the catalogue says a configured template does. The reference Deck was off the network when
this was written, which is why the open question is answered by a test rather than an argument.

**Builds on [ADR-0031](0031-a-save-is-answered-by-the-emulator-that-writes-it.md)** — a save is answered by the
emulator that writes it — and states the consequence that ADR did not: the plugin does not choose that emulator, so it
cannot always know it. **Does not touch [ADR-0031/the data one](0031-user-data-lives-outside-the-plugin-directory.md)
or [ADR-0033](0033-the-shipped-folder-name-is-chosen-here.md):** nothing here moves Decky's directories or the shipped
folder name.

## Context

On the reference Deck, one GameCube ROM's save sync failed in a way that took four separate measurements to explain,
and none of them was a bug in the sync itself.

The plugin baked `%EMULATOR_DOLPHIN% -b -e %ROM%` into the shortcut and handed it to RetroDECK
(`roms.applied_launch_options`). RetroDECK resolved that placeholder after the plugin stopped looking, so **two facts
the save layer needed were decided by a program it cannot see**: which emulator runs, and where that emulator keeps its
user directory.

The machine then answered differently from every model of it:

| Where the save actually was | What said so |
| --- | --- |
| `…/retrodeck/saves/gc/User/GC/USA/Card A/01-GZ2E-gczelda2.gci` | the file the session wrote at 14:59:23, and the only `.gci` with a current mtime |
| `…/retrodeck/saves/gc` | the resolved answer — it held one file, the stale `…(USA).zip` from an earlier attempt, and the sync skipped it as already synced: `uploaded=0, downloaded=0, errors=0` |
| `…/.var/app/net.retrodeck.retrodeck/data/dolphin-emu/GC/USA/Card A` | the standalone Dolphin answer — the folder was **empty** |
| `…/saves/gc/User/Config/Dolphin.ini` | an empty `[Core]` section, so the card folder is that user dir's compiled-in default |

Three candidate directories, one of which held the save, and the plugin resolved the wrong one because it resolves an
emulator's **default** layout while the launched emulator used another. The catalogues are not wrong: they model
Dolphin, and Dolphin was not the binary that wrote the file. The plugin simply had no way to know what it launched.

A second measurement shaped this decision. The first pilot pinned the emulator's user directory with `-u`. That works,
and it adopts the existing tree with no migration — but `-u` relocates the emulator's **entire user tree**: `Config`,
controller profiles, GBA BIOS, shaders, `GameSettings`. On a fresh install that hands the user an emulator with no
controller mapping, and on an existing one it moves settings out of the place they expect to find them. A save path is
a smaller, safer thing to own than a user directory.

## Decision

**1. One root, owned by the plugin, with every kind of file under it.**

```text
<data>/romm-tender/
  library/<platform>/     roms, or links to them
  cores/<platform>/       core binaries the provisioner fetched
  saves/<platform>/       every save the plugin syncs
  bios/  art/  mods/  cache/  db/
  layout.json             the contract below
```

`<data>` is the directory ADR-0031 already established, so this adds structure inside it and moves nothing. A root the
plugin owns is the whole point: no path in it is inherited from RetroDECK, EmuDeck or a distro package, so none of
them can change it out from under a save.

**2. `layout.json` is the contract between the provisioner and the plugin.**

Per platform, what was decided and what the plugin must honour:

```json
{
  "version": 1,
  "platforms": {
    "gc": {
      "emulator": "Dolphin (Standalone)",
      "launch": ["%EMULATOR_DOLPHIN%", "-C", "Core/GCIFolderAPath={root}/saves/gc/GC/%g", "-b", "-e", "%ROM%"],
      "save_dir": "{root}/saves/gc/GC/<region>/Card A",
      "save_unit": "gci-set",
      "needs": ["region"]
    }
  }
}
```

The plugin bakes `launch` verbatim (substituting `{root}` and leaving `%ROM%` and `%EMULATOR_*%` as placeholders for
RetroDECK's launcher) and answers the save question from `save_dir`, `save_unit` and `needs` — through the same
`SaveAnswer` and the same fills every other answer uses, so nothing downstream learns a second vocabulary.

**3. A platform absent from the manifest is not managed, and behaves exactly as today.**

This is what keeps the decision reversible and the blast radius per-platform. Every platform the manifest does not
mention keeps the live catalogue answer from ADR-0031, unchanged, and every test that pins today's answers keeps
passing. Adding a platform is adding a key.

**4. A provisioner writes the manifest; the plugin never infers a managed layout.**

The provisioner — a script first, a desktop app later if it earns it — creates the tree, fetches the cores, writes the
per-emulator configuration that points saves into the root, and writes `layout.json`. The plugin consumes it. Neither
side guesses about the other's half, which is precisely the failure measured above: the plugin guessed what
RetroDECK's placeholder would become.

**5. The manifest states a save PATH, never a user directory.**

The override goes through each emulator's own path setting — Dolphin's `-C Core/GCIFolderAPath`, RetroArch's
`--appendconfig`, PCSX2's memcard settings — so the user's emulator configuration stays where it is and keeps its
controller mappings. `-u`-style relocation is rejected for the reason measured above: it buys a save path at the price
of the user's settings.

**6. The manifest is data with a version, and unknown keys are ignored.**

A newer provisioner may write keys an older plugin does not read; an older provisioner may omit keys a newer plugin
could use. Both degrade to today's behaviour rather than failing, because the plugin is the component that is updated
by an in-panel updater while a user's tree may have been laid out months earlier.

**7. The first increment is GameCube, and its manifest is an adoption entry.**

One platform proves the contract end to end — bake, launch, answer, upload, restore — before a second one is added. The
provisioner v0 writes that entry from an explicit `--adopt gc=<existing card folder>`, because a save that already
exists must not have to move for this to help, and because the script is not allowed to go looking for saves. The
`-C` question above is answered by the same run: until it is, no entry names a directory inside the owned root for a
platform whose saves already live elsewhere.

## Consequences

- **Save sync becomes deterministic for managed platforms.** The directory is not resolved, modelled or observed; it
  is the string the plugin itself put in the launch command. That removes the entire class of failure measured here.
- **A fresh install is deterministic too.** The provisioner creates the tree before the first launch, so the first
  save lands in the right place rather than being discovered a session later.
- **RomM compatibility is untouched.** The server side still sees saves through the same API, slots and versioning; the
  manifest lives entirely on the device.
- **Adoption is a manifest entry, not a migration, where the shapes agree.** Pointing `save_dir` at an existing tree
  adopts it with no copy — which is why the GameCube increment should name
  `…/retrodeck/saves/gc/User/GC/<region>/Card A` while the user's save is there, and move to the owned root only with a
  one-time migration the repo can make explicit.
- **Two sources of truth exist, and the split is by platform.** A managed platform ignores the catalogue; an
  unmanaged one ignores the manifest. What must not happen is a platform consulting both and taking whichever agrees
  with what it already believes — that is how the wrong directory was resolved in the first place.
- **The provisioner is new surface with its own failure modes.** A half-written tree, a failed core download, a
  manifest that names a directory the plugin cannot write. Writing the manifest **last**, after the tree exists, makes
  a partial run a run that changed nothing, and the plugin's absent-platform rule keeps a damaged manifest harmless.
- **A managed platform can still refuse.** A card folder with no matching entry, a region the disc does not state, a
  save shape that is not per-game — the manifest says where to look, not that anything is there. The refusing states
  and their benign skip stay exactly as ADR-0031 defined them.

## Alternatives considered

**Keep the catalogue as the only source and fix the resolution instead.** Teach the plugin which emulator RetroDECK
actually launches. It would have fixed tonight's symptom, and it leaves the plugin depending on another program's
defaults for the thing it must never be wrong about. It also cannot answer the next case: a user on EmuDeck, whose
layout differs again.

**Adopt RetroDECK's tree with `-u`, which is what the first pilot did.** Works today with no migration, and was
rejected on the consequence measured above: it relocates the emulator's whole user tree, so the plugin would own the
user's controller configuration as a side effect of carrying their saves.

**Let the plugin relocate saves into its own root without a manifest.** Fewer moving parts, and it makes the plugin the
provisioner: every emulator's path setting would need hand-coded knowledge of that emulator's flags, in code, updated
with each emulator release. The manifest keeps that knowledge as data the provisioner can change without a release.

**Put the provisioner's work in the plugin itself.** Decky plugins run as root and can download, so it is technically
possible. It was rejected because the work is not per-session: it happens once, is best done with a visible log, and
benefits from being re-runnable from a terminal when a download fails. A plugin is the wrong place for a job whose
failures a user needs to read.

## Related

- [ADR-0031 — a save is answered by the emulator that writes it](0031-a-save-is-answered-by-the-emulator-that-writes-it.md)
  — the live answer this ADR makes unnecessary for managed platforms.
- [ADR-0030 — the emulator catalogue is read by the vendored resolver](0030-the-emulator-catalogue-is-read-by-the-vendored-resolver.md)
  — where the catalogue, and therefore the unmanaged answer, comes from.
- [ADR-0031 — user data lives outside the plugin directory](0031-user-data-lives-outside-the-plugin-directory.md) —
  which root this layout is built inside.
- [`docs/architecture/save-structure.md`](../architecture/save-structure.md) — the measured GameCube failure, the
  owned launch, and the fills that settle a card folder.
