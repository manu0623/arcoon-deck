# 0059 — A collection store that cannot answer is left alone

**Status:** Accepted (0.48.16)
**Follows:** 0034 (the layout is owned by the plugin), 0043 (an owned launch states its own
save) — this one is about Steam's own API, not ours.

## Context

Opening Steam's library on the reference Deck crashed the whole Game Mode UI into a
full-screen React error:

```
TypeError: Cannot read properties of undefined (reading 'values')
  at get userCollections (steamloopback.host/sp.js …)
  at g.computeValue_ / trackAndCompute / get      ← MobX
  at saveCollection (plugins/Arcoon Deck/dist/index.js)
  at createOrUpdateEmulatorCollection
  at async syncEmulatorShortcuts
  Component Stack: … libraries~e8c5e5be4.js …
```

Three facts make this the plugin's fault rather than the client's.

1. `collectionStore.userCollections` is a **MobX computed** over Steam's non-Steam shortcut
   store: its getter reads `deckDesktopApps.values()`. On this client `deckDesktopApps` is
   undefined, so the getter throws exactly that message.
2. **MobX caches a computed's exception.** Our own `try/catch` inside
   `createOrUpdateEmulatorCollection` did catch its copy — the plugin log shows the caught
   error in every run — but the throw had already been recorded on the computed, and Steam's
   library render re-threw it. That is why the library died while the plugin "merely" logged.
3. The emulator-tile feature calls `syncEmulatorShortcuts` on every plugin start, so the
   collection write happens on every boot, before anything the user does. Its reads were
   unconditional: `collectionStore.userCollections.find(...)` in `saveCollection`, and the
   same array in `clearPlatformCollection` / `clearAllRomMCollections`.

## Decision

One guarded read, `readUserCollections()`, used by every path that touches Steam's
collections. It returns `null` — meaning "leave Steam alone" — when `collectionStore` is
absent, when `deckDesktopApps` is not exposed, or when the getter still throws. The three
writers (`saveCollection`, `clearPlatformCollection`, `clearAllRomMCollections`) skip the
operation on `null` and log a warning naming the reason. `emulatorShortcuts.liveShortcutAppIds`
reads the shortcut store the same defensive way.

A `null` is never upgraded to a guess: a collection that cannot be read cannot be
deduplicated against, and creating a second copy of "RomM: Game Boy (deck)" would split the
games already in the first.

## Consequences

- The library renders on this client, because the throwing getter is never evaluated.
- Collections are **not** created, updated or cleared where the store cannot answer; the
  plugin's platform and emulator collections stay exactly as Steam has them, and one warning
  explains why. That is a visible feature regression on such a client, chosen over crashing
  the UI it lives in.
- An exception already cached in a running Steam process survives until Steam restarts, so
  the fix takes effect after a Steam/Game Mode restart rather than a plugin reload alone.
- The gate is on the store the computed derives from, not on an error message: a client that
  exposes `deckDesktopApps` keeps full collection behaviour even though the message above
  would never be seen there.
