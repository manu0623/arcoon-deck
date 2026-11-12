# The two-layer launcher

Tender's launch chain currently ends at RetroDECK, and its save math is RetroArch's
naming rule. Both are being replaced by two layers this plugin owns. The RomM connection
layer — auth, endpoints, negotiate, slots, version history — is unchanged; only the halves
below it move.

## Why

`domain/save_path.py` answers one question: `<saves root>/<content dir>/[<core>]/<rom stem>.<ext>`.
That is exactly right for the ~150 libretro cores that write one SRAM file named after the
ROM, and exactly wrong for everything else. A memory card is a directory or a fixed card
file many games write; a PSP save is several sibling folders sharing a disc id; a 3DS save
is two directory trees under hardware-derived hex identifiers. `domain/save_answer.py`
therefore classifies every one of those as `shared`, `hole`, or `unestablished` and refuses
to sync it, which is why PlayStation, Dreamcast, GameCube, PSP and 3DS saves do not sync
today.

Argosy does not have that problem because it resolves a save from the game's own identity:
`save_id` (a disc serial, a title id, a product number) becomes a path through a per-platform
rule. **The words "save structure" in this project mean that mapping**, not a folder tree we
happen to like, because a save written under a different rule is a different save unit to
every other client on the server.

## The two layers

**Layer 1 — launch.** Owns the ROM tree, the cores, and the launch chain: which core runs a
ROM, where its BIOS lives, what the process is, and when a session starts and ends. It stops
asking RetroDECK for all four. A session end is what triggers a save upload, so this layer is
also the thing that makes save sync correct rather than merely present.

**Layer 2 — the save bank.** Owns where saves live: one root (`<data dir>/saves`), one
layout per platform, and the unit/hash/archive rules that go with it. Its layouts are ports
of Argosy's handlers, so a Deck and an Argosy handheld produce the same units and the same
archive roots for the same game.

Everything the server sees is unchanged: a save is still a blob keyed by `(rom_id, slot)`
with an `emulator` tag and an md5 content hash. Convergence is a client-side property, which
is precisely why it has to be deliberate.

## The bank's tree

| Platform | Base below `saves/` | Argosy shape it reproduces |
| --- | --- | --- |
| any unlisted | `<slug>/` | `<rom stem>.srm` — the libretro per-ROM default |
| Vita | `vita/` | `<save_id>/` |
| PSP | `psp/PSP/SAVEDATA/` | `<disc id><suffix>/` siblings, bundled as one unit |
| PS3 | `ps3/savedata/` | `<title id><suffix>/` siblings, same bundle rule |
| PS2 | `ps2/` | `<card>.ps2/<prefixed folder>/`, one card per game's entries |
| 3DS | `3ds/sdmc/Nintendo 3DS/` | `<id0>/<id1>/title/<category>/<low>/data` plus `extdata/…` |
| Wii | `wii/title/00010000/` | `<low title id>/` |
| Wii U | `wiiu/mlc01/usr/save/00050000/` | `<low title id>/` under Cemu's own tree |
| Switch | `switch/nand/user/save/` | `<user>/<profile>/<title id>/` |
| GameCube | `gc/Card A/` | the `.gci` set whose headers carry the disc's game code |
| Dreamcast | `dreamcast/` | `<product number>.A1.bin` — port A1's VMU |

The 3DS and Switch trees keep the emulators' own intermediate directories (`id0`/`id1`, user
and profile) because those are hardware identities: they are discovered, never constructed,
and a fabricated one points at a directory nothing reads.

## What the port has to preserve

Five of Argosy's rules are load-bearing and each of them fails silently when dropped:

1. **Usage is the id-to-path contract.** `FOLDER_EXACT`, `FOLDER_PREFIX`, `FILE_EXACT`,
   `FILE_PREFIX`, `FOLDER_SPLIT`. Getting one wrong mismatches saves rather than erroring.
2. **The unit is a member set.** PS2 bundles the game's own folders (never the whole card),
   PSP/PS3 bundle every prefix-sharing sibling, GameCube bundles every matching `.gci`. An
   upload of "the resolved folder" ships a fraction of a save.
3. **Archive roots are wire format.** A 3DS archive is rooted at `data`/`extdata` and never
   names its title, so it matches on the `UNIDENTIFIED` tier and the resolved destination is
   what places it. A PS2 archive is rooted at the card, so it matches by a folder *inside* it.
   Changing what a handler zips invalidates every archive already on a server.
4. **Some identities must be refused.** Two PS2 cards holding the same game is a conflict,
   not a choice; a Switch title with no profile directory has no path. Both answer with the
   missing thing named, so a caller reports a reason instead of writing somewhere wrong.
5. **The container belongs to the layout.** PCSX2 reads a folder card only when its 0x2000-byte
   superblock has `0x6F` at offset `0x16`; an empty or short one is an unformatted card the
   game never sees. Every restore door must leave a formatted card behind, and the superblock
   itself never travels in an archive.

## Where the code is

- `py_modules/domain/save_bank.py` — the pure layer: the platform table, the nine resolution
  rules, the membership and archive-root predicates, and the PS2 superblock. No I/O.
- Adapter and service wiring are not written yet: the adapter supplies a directory scan
  (`path → child names`) and the extracted `save_id`, and the launch layer supplies the ROM
  stem. Both are the next pieces of layer 1, and [launch-layer.md](launch-layer.md) is the work
  order for them.

## Fidelity boundary

The rules above were ported from Argosy's handlers and its `save-id-to-path.md`, not from
observed bytes on a Deck. Two consequences are worth stating plainly: a save unit is only as
good as the `save_id` extracted for it (Argosy derives that from the ROM in `sigil`, which has
no counterpart in this repo yet), and no round trip has been exercised against a live RomM
server. `GET /api/saves` plus a negotiate `no_op` twice per platform is the bar before any of
this is called working.
