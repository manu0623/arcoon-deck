# 0062 — A provisioner run keeps the platforms it does not name

**Status:** Accepted (0.48.21)
**Follows:** 0034 (the layout is owned by the plugin), 0061 (a managed Dolphin launch).

## Context

`scripts/provision_layout.py` rebuilt `layout.json` from the `--adopt` arguments alone. Running
it to adopt Wii (`--adopt gc=… --adopt wii=…`) therefore wrote a manifest with two platforms
and silently unmanaged Switch, which had been there since the first provisioning.

The plugin then answered Switch from the catalogue instead of the manifest: measured on the
reference Deck, rom 6550's save answer pointed at
`/home/deck/Emulation/storage/yuzu/nand/user/01009d901bc56000` — one level short of
`…/user/save/0000000000000000/93543B1D30E2AEB87D0F28AE30D83730/01009D901BC56000`, the folder
Eden actually writes — and the upload died with `FileNotFoundError` while packing it.

Nothing in the old behaviour was accidental: the script's contract was "write what I was
told". What was wrong is that a *partial* statement unmanages everything it omits, and an
adoption run is by nature partial.

## Decision

A run reads the manifest it is about to replace and keeps every entry for a platform it does
not name:

```python
document = build_manifest(root, adopted, kept=existing_entries(root))
```

`existing_entries` returns `{}` for a missing, unreadable, or wrong-version file — the first
run's state — and copies the platform entries verbatim otherwise, so a kept platform's launch
argv and save path are exactly what the previous run wrote, never re-derived from today's
templates.

## Consequences

- Adopting one platform can no longer unmanage another. Re-running with only `gc` and `wii`
  leaves Switch's entry untouched, which is what the live check asserts.
- A platform can still be *changed* by naming it with a new directory, and the printed count
  now reports the platforms actually written rather than the ones passed on the command line.
- Dropping a platform deliberately still needs a hand edit of `layout.json`: this cut has no
  `--forget` flag, and inventing one without a case that needs it would be a promise about
  the CLI that nothing measures.
