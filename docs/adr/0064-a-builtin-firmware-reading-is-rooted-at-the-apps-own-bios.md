# 0064 — A firmware reading is held to the BIOS root the app's emulator will read

**Status:** Accepted (0.48.23)
**Follows:** 0045 (a built-in runtime answers from the app's own inventory), 0046 (the app's own
tree, and what a structure decides).

## Context

The reference Deck runs `runtime_mode=builtin`, `structure=app`, and has no RetroDECK
installation — but `~/retrodeck` is still there, a tree the flatpak left behind. Measured:

```
runtime: builtin   the app's BIOS root: /home/deck/.local/share/romm-tender/bios
  (holds HdPacks, Mupen64plus, PPSSPP, Ps2, Ps3, azahar, citra, dc, flycast, kronos …)

handle retrodeck               root = /home/deck/retrodeck/bios          ← what was read
handle bare_retroarch_flatpak  root = /home/deck/.var/app/…/retroarch/system
```

Firmware presence was answered from `~/retrodeck/bios`: the adapter took the first installation
`detect()` returned, RetroDECK leads that order wherever it is present, and the RetroDECK marker
(`~/.var/app/net.retrodeck.retrodeck/config/retrodeck/retrodeck.json`) survives the flatpak being
removed. Under the app's own runtime that directory is read by nothing. The emulator the app
launches is handed `system_directory = <app's BIOS root>` in the appendconfig it writes, so a
file downloaded there was reported missing while a file left in the dead tree would have been
reported present.

The same reading is correct under `runtime_mode=retrodeck`: the launch is RetroDECK's, its
RetroArch reads the `system_directory` its own cfg names, and that is the directory the resolver
answered from.

## Decision

The firmware adapters are told the root their readings must be rooted at (`reads_root`), and a
reading taken at any other directory loses its destination half:

```python
FirmwarePlacement(read_elsewhere=True)   # declarations kept, present/caveats/folder/checked dropped
```

- Bootstrap supplies the root only under `RuntimeMode.BUILTIN` (`retrodeck_paths.bios_path()`);
  under `RETRODECK` it supplies `None` and every reading stands as before.
- Roots are compared through `realpath`, so `/home/…` and `/var/home/…` are one directory (#1838).
- The **declarations** stay: who wants the file and at which subdirectory is the emulator's own
  statement and does not change with which directory was read. `relative_path` therefore survives,
  which is what keeps subdirectory placement (`pcsx2/bios`, `dolphin-emu/Sys/…`) intact.
- The **destination half** goes silent, and the row says why. `FirmwareDemand.is_downloaded` then
  answers from the app's own file store at the destination it assembled, which is the path the
  emulator will open.
- A `present` the resolver could not establish at OUR root still reads absent: "could not look"
  is not "it is there", and that rule is unchanged.

## Consequences

- On the reference Deck the BIOS check now reads `~/.local/share/romm-tender/bios`, the directory
  the emulator is pointed at, instead of the leftover RetroDECK tree.
- `structure=retroarch` resolves the app's BIOS root to the flatpak's own `system` directory,
  which is the resolver's root too — there the reading is authoritative, as it always was.
- A folder declaration read elsewhere reports no contents verdict rather than a verdict about
  another directory; the row shows its position as unestablished, which is what it is.
- Under RetroDECK nothing changes. Detection still labels and never picks a winner; choosing among
  several installations for the *declaration* side remains #918.
