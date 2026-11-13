# ADR-0053 — A PS3 save folder is named after the disc, not the file

**Status:** accepted

## The problem

PS3 saves live in one flat directory — `dev_hdd0/home/<user>/savedata` — and each game's
folder is named after its **title id**, never after the game. Measured on the reference
Deck:

```
BCES00301_SAVE_1           BCUS98111-AUTOSAVE        BCUS98111-USERDATA
BCUS98247_SAVE_SLOT_00000  BLUS30443DEMONSS005       NPUB304670
```

The library row says `3D Dot Game Heroes (USA).iso`. Nothing in the row, the filename or the
install path carries `BLUS…`, so a save layer that reads rows alone can see six other games'
saves and no way to pick its own. The game has to be asked.

## The decision

**The id is read from the game's own `PARAM.SFO`.** It is the file the save folder is named
after: measured here, Sly Cooper: Thieves in Time wrote `BCUS98247_SAVE_SLOT_00000` while its
disc states `TITLE_ID=BCUS98247`, and 3D Dot Game Heroes' disc states `BLUS30490`.

Parsing lives in `domain.content_identity.ps3_title_id`, beside the PSP `DISC_ID` reader it
shares a format with — the SFO table is the same file, the key differs — and the walk that
reaches it inside an image is the same ISO 9660 one the PSP reader uses. The adapter
(`adapters.content_identity`) decides which bytes to read and answers for both shapes a PS3
install takes:

- **Disc image** — root directory lists `PS3_GAME` (the reference image answered
  `PS3_DISC.SFB`, `PS3_GAME` and `PS3_UPDATE`, with the game at extent 293), and
  `PARAM.SFO` is one level down.
- **Folder boot** — `<game>/PS3_GAME/PARAM.SFO` on disk.

A `TITLE_ID` value is accepted only as four letters and five digits; anything else is
refused rather than normalised into a guess. An image with no ISO 9660 descriptor (UDF-only,
compressed) answers nothing.

## Where the saves point

`_SAVE_POINTS` gains `rpcs3`: `config/rpcs3` + `dev_hdd0/home/00000001/savedata`, measured on
this Deck — `~/.config/rpcs3` is where `config.yml`, `dev_flash` (142 firmware modules) and
`dev_hdd0` all are, and `~/.config/rpcs3` is not a data-root emulator at all. `00000001` is
the first local user RPCS3 creates and the only one in either tree here. The link adopts what
the emulator already saved before pointing it at `<saves>/ps3/savedata`, so the Sly Cooper
save written before this existed moves rather than disappears.

The bank's own `ps3` layout was already a prefix bundle (`<saves>/ps3/savedata`), and
`PREFIX_BUNDLE` is in `restores_by_extraction`, so the two directions stay symmetric.

## The format the first draft got wrong

The first reader was written against a hand-built `PARAM.SFO` that stated `TITLE_ID` as
`0x0404`, the NUL-terminated UTF-8 form, and refused the real image, which states `0x0204`.
The live probe of `3D Dot Game Heroes (USA).iso` therefore returned nothing at all. The
reader in `content_identity` reads the value length the entry states and does not consult the
format byte, so both forms answer and any other shape is still refused by the id's own syntax.

That first draft also grew its own ISO 9660 walker and SFO parser; both were deleted in favour
of the ones the PSP reader already had. One place reads an identity, one place spends it.

## Consequences

- A PS3 game's identity is read from content, once per sync, and never stored in the row.
- A PS3 launch is not redirected by the plugin (RPCS3 is a standalone emulator), so the bank
  answers only because a save link exists — the same gate as PSP and 3DS.
- The user id is spelled, not discovered: a second RPCS3 user on another Deck would need a
  discovery rule rather than this row.
