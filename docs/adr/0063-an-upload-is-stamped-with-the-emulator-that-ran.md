# 0063 — An upload is stamped with the emulator that ran, not a launcher

**Status:** Accepted (0.48.22)
**Follows:** 0045 (a built-in runtime answers from the app's own inventory), 0061 (a managed
Dolphin launch runs the installed flatpak).

## Context

Switching to Eden on the reference Deck produced this line, and this save on the server:

```
Uploaded save: The Legend of Zelda- Link's Awakening .zip (emulator=retroarch)
save 455  The Legend of Zelda- Link's Awakening  [2026-11-13_18-19-22].zip  emulator=retroarch
```

There is no RetroArch Switch core, and the game ran in Eden. The cause is one function:

```python
emulator = build_emulator_tag(core_so)   # sync_engine/matrix.py
```

`build_emulator_tag` takes a libretro core `.so` and returns `retroarch-<core>`, falling back
to the bare string `retroarch` when there is no core. A standalone launch has no core, so every
Eden, Dolphin and PCSX2 upload was stamped `retroarch`.

RomM files a save under `saves/{system}/{rom_id}/{emulator}/`, so this is not cosmetic. The
same server holds the same ROM's saves under `eden`, `edenduo`, `dolphin` and `retroarch-dolphin`
for saves other clients wrote — measured on roms 5319 (GameCube: `dolphin`, `retroarch`,
`retroarch-dolphin`), 6938 (Wii: `dolphin`, `freegosy`, `retroarch_64`) and 7200 (Switch:
`eden`, `edenduo`). An upload stamped `retroarch` therefore lands beside those saves rather than
versioning them, and a client that reads its own emulator's folder never sees it.

## Decision

The tag is the emulator that actually ran:

```python
emulator_tag(core_so, identity=<resolver's name for the emulator>)
```

- A **standalone** invocation answers its own identity, as the resolver names it — a registry
  id (`eden`, `dolphin`) or a picker label (`Dolphin (Standalone)`). `normalize_emulator_identity`
  drops a parenthesised provider and hyphenates the rest, so both spell the same tag.
- A **libretro** invocation keeps `retroarch-<core>`, because RetroArch *is* the emulator there
  and the core is what distinguishes one from another.
- `retroarch` remains only for a ROM whose launch cannot be resolved at all.

The identity comes from `ActiveCoreResolver.active_emulator_for_rom`, read through
`SyncEngine._standalone_emulator_identity` and handed to the matrix executor at construction —
the same resolver the launch uses, so the tag and the launch cannot disagree about which program
ran. A resolver that fails answers `None` rather than failing the upload: the tag is metadata,
and a save that exists is worth more than a correct label.

## Consequences

- A save written in Eden is filed under `eden`; one written in Dolphin under `dolphin`.
- Saves already uploaded with the wrong tag (455 on the reference Deck) keep it: RomM's upload
  path takes the emulator as part of the target, so re-tagging means a new save, not a rename.
- The `retroarch` fallback still exists for an unresolved ROM. It is now a statement about the
  plugin's knowledge, not a claim that RetroArch ran.
- Nothing here changes which files are carried or where they are restored — only the label the
  server files them under.
