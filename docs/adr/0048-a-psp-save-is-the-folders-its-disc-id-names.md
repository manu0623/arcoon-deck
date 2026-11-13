# 48. A PSP save is the folders its disc id names

**Status:** Accepted (0.39.0)
**Follows:** 0043 (an owned libretro launch states its own save), 0044 (a standalone
emulator states its own save base), 0046 (the structure is a setting).

## The problem

PSP synced nothing in either direction. Its save is not a file: PPSSPP writes one folder
per game into its memory stick, named after the disc's id (`ULUS10064DATA00` beside
`ULUS10064SETTINGS`). Three separate things then refused to meet.

- **No answer.** The bank directory was only ever named for the plain per-ROM shape, so a
  PSP launch fell through to the ES-DE catalogue — which a device driving its own runtime
  does not have. `save_status` said `unestablished`, and every sync returned
  `save_shape_unsupported` while three of the user's saves sat in `autosave` on the server.
- **No identity.** The folder names are the disc id, and the id is a key inside
  `PSP_GAME/PARAM.SFO`, reachable only by walking the image's ISO 9660 directory tree.
  Nothing about the ROM's path carries it.
- **A doubled redirect.** The generated appendconfig named the layout's whole subdir
  (`saves/psp/PSP/SAVEDATA`), and PPSSPP builds `PSP/SAVEDATA` *inside* whatever folder it
  is handed — so the saves landed at `SAVEDATA/PSP/SAVEDATA/...`, one level below where
  every lookup reads. Measured on the reference Deck, that directory existed and was empty.

## The decision

**The id is read from the image.** `domain.content_identity` gains the two ISO 9660
structures the walk needs (the volume descriptor's root record, one directory record) and a
`PARAM.SFO` table parser; `adapters.content_identity` does the three bounded reads. A
compressed image answers nothing: its sectors are not at the offsets an ISO reader
addresses, and a decompressor this plugin has not measured is a guess with a file format.

**A redirect names the folder the core completes.** `SaveLayout.core_subdir` states the tail
of a platform's subdir that the emulator itself builds. For PSP that is `PSP/SAVEDATA`, so
`savefile_directory` becomes `saves/psp` and the core's own tree lands exactly on the base
the lookup reads. Platforms without a `core_subdir` are handed the bank base, unchanged.

**The answer is a member set.** A PSP save resolves through the existing prefix-bundle rule:
the folders under `SAVEDATA` whose names start with the disc id. The unit is described once
by `domain.save_bank`, restated as a save answer by `unit_answer`, packed into the one
`<rom name>.zip` RomM stores, and extracted back into the tree it came from. That last part
needed two small fixes in shared code: `create_archive` now recurses into a member that is a
folder, and a restored member is tracked by its own relative name rather than its basename,
so a nested file's baseline points at where the file actually landed.

Without an identity the answer stays a `save_id` hole rather than a guess — the same rule the
bank already applies to PS2 cards and Switch profiles.

## Consequences

- PSP syncs both ways on a built-in-runtime Deck: the server's `<title> [timestamp].zip` is
  downloaded, extracted into `SAVEDATA`, and a local save is packed and uploaded as the same
  shape. The launch no longer needs RetroDECK for any of it.
- The `restores_by_extraction` family set now includes prefix bundles, so PS3 (the other user
  of that rule) inherits the extract-on-restore path — which is what its folder sets need.
- A compressed PSP image (`.cso`/`.zso`) still answers no identity: it keeps the honest hole
  until a decompressor is measured. The rest of the ISO path is unchanged.
- Platforms whose layout is a card, a title tree or a card folder (PS2, 3DS, Dreamcast, PS3
  without an RPCS3 tree) still answer holes: the bank directory stays unstated for the
  families no libretro launch has been pointed at, and this change deliberately does not
  open those.
