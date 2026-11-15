# 0074 — A PC game's saves are one folder in its Proton prefix

- **Status:** Accepted (0.48.49), prototype scope
- **Follows:** 0031 (a save is answered by the emulator that writes it), 0073 (a PC game is unpacked and run under Proton)

## Context

Save sync is built around a *battery file*: one file, named after the ROM, in a directory derived
from the system. For a Windows game that model describes nothing. The game runs under Proton, and
everything it writes lands inside its own Wine prefix — `steamapps/compatdata/<appId>/pfx`. Measured
on the reference Deck, after a session of *Need for Speed: Most Wanted* (rom 7159, appid
2169565722):

```
do_sync_rom_saves(7159): system=win, saves_dir=/home/deck/.local/share/romm-tender/saves/win, server_saves=0
```

The directory exists, RomM holds no save for the ROM, and the game had written its profile
somewhere else entirely — inside the prefix. The emulator pipeline will keep answering "nothing to
do" for every PC game forever, because it is looking in a directory no Windows game has ever
written to.

## Decision

The two save hooks (`pre_launch_sync`, `sync_rom_saves`) check the platform first. A `win` ROM is
served by a PC path instead of the battery-file pipeline, and that path treats a game's saves as
**one folder, carried as a zip**:

- **Which folder.** The folders under `drive_c/users/steamuser/{Documents,Saved Games,AppData/…}`
  are surveyed, empty ones and Windows housekeeping (`Microsoft`, `Packages`, `Temp`, …) are
  dropped, and the rest are scored by how many of the folder's own words appear in the game's
  title — `NFS Most Wanted` scores 2/3 against *Need for Speed: Most Wanted*. A name match beats
  recency, because two games only share a prefix by accident; with no match at all the most
  recently written folder wins, which is the one just played from. The pick is remembered in
  `kv_config` as `pc_save_dir:<rom_id>`, **relative** to the prefix, so a game that saves into
  `AppData` keeps doing so and a rebuilt prefix under the same appId still resolves.
- **On exit.** The folder is zipped (`DownloadFileAdapter.zip_dir`, sorted, symlinks skipped) into
  `<data>/pc-saves/<rom_id>.zip` and uploaded with `emulator="proton"`, slot `default`. RomM then
  holds one save entry per PC game, visibly separate from any libretro core's saves.
- **On launch.** The newest server save by `updated_at` is downloaded and unzipped back over the
  same folder with `extract_zip`'s ZIP-slip protection rooted at the prefix's user directory.

Neither hook may ever block a launch or fail a session: a listing, download or upload error is logged
and answered with `synced/uploaded = 0`, and the game starts with whatever is on disk.

**Amended in 0.48.49.** The exit does not arrive through the `sync_rom_saves` handler — a session ends
through `SessionLifecycleService`, which holds its own `post_exit_sync` collaborator. Measured: after
the first real session (rom 7159, 239 s, save written to `Documents/NFS Most Wanted/Manu`), the exit
logged `post_exit_sync called` and then `do_sync_rom_saves(7159): system=win … server_saves=0`, with
no PC-path line at all: the branch was correct and never called. The lifecycle therefore receives a
`PcSaveSyncExitHook` that routes Windows ROMs to the PC folder and everything else to the emulator
service, so the two entry points cannot disagree. A Windows game with nothing to carry yet answers
with the benign `SAVE_SHAPE_UNSUPPORTED_REASON`, which raises no toast.

## Consequences

- A Windows game now syncs, and the folder it used is in the log (`PC save folder for rom N: …`),
  so a wrong pick is a one-line diagnosis rather than a bisect.
- **Not covered, deliberately:** saves a game keeps in the Windows registry (there is no file to
  carry), and games that scatter progress across two folders — the prototype carries one folder per
  ROM. A game whose folder is none of the surveyed roots (`Documents/My Games`, for instance, sits
  one level deeper) is picked only when the name match finds it there.
- The prefix belongs to the shortcut's appId. Re-creating the shortcut with a new appId orphans the
  save folder until the game is played once more; the stored relative path then fails to resolve
  and a fresh pick is made.
- This is a prototype for one game. Making it general needs the folder choice to be visible in the
  UI, and a second slot for games with genuinely separate profiles.
