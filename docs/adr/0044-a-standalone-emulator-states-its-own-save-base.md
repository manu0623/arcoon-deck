# 0044 — A standalone emulator states its own save base

**Status:** Accepted (0.35.28)
**Follows:** 0043 (an owned libretro launch states its own save).

## Context

ADR-0043 fixed save answers for launches the plugin performs with RetroArch: the appendconfig
says where the save goes, so the plugin states `<stem>.srm` in the bank instead of asking a
catalogue that a device without RetroDECK cannot read.

Standalone emulators were left in the old shape, and that is most of a library: Switch is
Eden, GameCube is Dolphin, and a device with no ES-DE had **no** save answer for any of
them. The catalogue lookup answered "no entry labelled `Eden (Standalone)`", sync skipped
with `save_shape_unsupported`, and the fetch never happened — for platforms whose saves are
perfectly well known to the emulator, if not to us.

## Decision

A standalone launch asks the **emulator itself**, through
`adapters/emulator_save_base.py`: the yuzu lineage (Eden, Citron, Sudachi, yuzu) writes
`nand_directory` into `qt-config.ini`, and the saves live under
`<nand>/user/save/<profile>/<title id>`.

- The value is **read, never assumed**. On the reference Deck Eden states
  `/home/deck/Emulation/storage/yuzu/nand`, which is why the same plugin works for an
  AppImage, a flatpak and a native install — `~/.local/share` would have been wrong here.
- A QSettings file writes top-level keys **before** its first `[Section]`, and Eden's has no
  section header at all, so the INI read is tried first and a flat scan answers when it
  cannot parse. Both read the same file, so they cannot disagree.
- `save_bank.describe_unit` gains a `base` override: the switch family's rules
  (`<profile>` discovery, title id naming) apply unchanged to the emulator's own tree, so
  there is one description of the layout, not a second copy.
- The unit is restated as a save answer by `save_answer.unit_answer`, so the sync layer sees
  the same vocabulary as any other answer.

**Everything else still refuses.** PCSX2's cards are shared and card-named, PPSSPP, Cemu and
RPCS3 name saves by their own identities, and none of their keys has been read off a live
config here. Naming a directory this plugin has not verified is how a sync writes a save
where the emulator never looks, so those platforms keep the catalogue's answer; the adapter
returns `None` and a test pins that it does.

## Consequences

- Switch saves resolve on a no-RetroDECK device: the title folder is named from the content
  file's own title id, the profile is discovered from the directory rather than invented, and
  the catalogue is never asked (a test pins that too).
- A profile that has never been created is a `hole` with `needs=("profile",)` — an honest
  refusal, not a guessed path. Opening Eden once creates it.
- Adding another emulator family is now a data-sized change: a key to read and, where its
  tree differs, a layout family already in `domain.save_bank`.
- Platforms with no verified rule keep the pre-existing behaviour exactly, so this cannot
  regress a device whose save locations were already answered by a catalogue.
