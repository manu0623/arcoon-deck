# 0068 — A tile's art is applied when it is missing, not when the tile is created

**Status:** Accepted (0.48.28); the portrait slot added in 0.48.29.
**Follows:** 0050 (every installed emulator is a Steam tile).

## Context

The emulator collection created its shortcuts correctly and dressed none of them. Every plugin
mount logged the same line, and Steam's grid directory agreed with it:

```
[FE] Emulator collection "Emulators": 0 added, 13 present, 0 images applied
```

Thirteen tiles were bound in `emulator_shortcuts`, all still live in Steam, and not one of
their app ids had a single file in `userdata/<user>/config/grid` — so every tile wore Steam's
default grid picture while the games beside it carried their covers.

The cause was a call site, not the art path. `syncEmulatorShortcuts` applied artwork inside the
branch that *creates* a shortcut:

```ts
    if (appId === null) {
      …create, bind…
      art += await applyEmulatorArtwork(row, created);
    } else {
      existing++;
    }
```

An existing tile therefore never asked. That is invisible on a device whose very first run had
a SteamGridDB key: the tiles were created and dressed in the same pass. On this Deck the
bindings predate the artwork code (and the key), so the one pass that would have fetched art
had already happened — and every later run took the `existing++` branch and left it undressed.
The same shape would strand any tile whose first fetch failed (a no-match, a dropped
connection, a missing key), which is why this is not only about upgrade order.

## Decision

Art is requested for **every** row in the catalogue, and the backend answers from the grid
directory instead of the network when the asset is already there.

- `EmulatorShortcutService.artwork` returns `{"base64": None, "no_api_key": False,
  "present": True}` when the bound app id's grid file exists for that asset type, before any
  SteamGridDB call. The file is the truth: it is also what a user's own custom art leaves
  behind, so hand-picked art is never overwritten.
- Which filename counts is `domain.artwork_paths.asset_grid_filenames`, built on the same
  suffix/extension table the grid cleanup already uses (`_hero`, `_logo`, `_icon`, portrait
  `p`, bare wide) — measured on a live grid directory, not assumed. Each slot is its own
  file: the wide capsule is the bare name and the portrait is `p`, so a tile carrying one is
  not reported as carrying the other.
- The service takes Steam's grid directory as a `grid_dir` reader. `None` means *cannot tell*
  and every asset is fetched as before, so a missing answer never reads as "already applied".
  The same three-way rule covers no binding (no tile yet) and an unknown asset type.
- The frontend calls `applyEmulatorArtwork` once per row, after the create-or-reuse decision,
  and keeps its "best-effort" contract: a missing key, a no-match or a failed download still
  costs a picture and never a shortcut.

## Consequences

- The first run after this change dresses the tiles that already exist, once. Later runs cost
  four `exists()` calls per emulator and no request at all.
- Steam's grid directory becomes the record of what has art. There is no second ledger to keep
  in sync, and deleting a grid file is enough to have the next run re-fetch that asset.
- A device with no SteamGridDB key keeps the default tiles and logs the reason once per row,
  as before — the key check still runs before the presence check, so nothing about a keyless
  device changes.
- Art applied through Steam's own UI is respected rather than replaced, which is a behaviour
  change worth naming: the plugin no longer assumes it was the only writer.

## The portrait slot, measured after the first release

Shipping the above exposed what the first audit had read too shallowly. Twelve of the thirteen
tiles carry `_hero`, `_logo`, the wide bare `.png` and `_icon`, and **none** carried `p`: the
asset the collection was missing is the portrait cover, the `{app_id}p.png` a ROM tile's cover
occupies. Steam's custom-art call writes the wide slot, so a type 3 fetch could never produce
it, and the collection showed its emulators without the picture every game beside them has.

So the portrait is its own asset type — `5`, named `cover`, on SGDB's grid endpoint asked for
portrait dimensions (`600x900,342x482`) — and it is applied the way every ROM tile's cover is:
the backend decodes the PNG and writes `{app_id}p.png` into the grid directory. No Steam call
is involved, because Steam reads that directory itself; `save_shortcut_cover` is the callable,
and `steam_config.write_shortcut_cover` the write.

Two gaps this does **not** close, both SGDB coverage rather than plumbing: Dolphin has no hero
asset on its SGDB entry, and the search term `Citron` matches nothing there at all, so that
tile stays on Steam's default picture until the name it searches for changes.
