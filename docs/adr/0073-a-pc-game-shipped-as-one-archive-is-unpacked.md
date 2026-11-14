# 0073 — A PC game shipped as one archive is unpacked, and its exe is the launch target

- **Status:** Accepted (0.48.45)
- **Follows:** 0009 (the launcher is a wrapper), 0031 (a save is answered by the emulator that writes it)

## Context

`domain.windows_launch` already described the whole chain for a PC game: rank the executables in
the extracted tree, bake the winner as the shortcut's own target so Steam starts it under Proton,
and let the **Launches** row repoint it by hand. What it never got was a tree. Measured on the
reference Deck:

```
rom_installs, platform win:
  7156  Need for Speed: Carbon   rom_dir=NULL
        file_path=/home/deck/.local/share/romm-tender/roms/win/Need for Speed - Carbon.zip
  7178  Link's Awakening DX HD   rom_dir=/home/deck/Emulation/roms/win/Links Awakening DX HD Windows.7z
        file_path=…/Links Awakening DX HD Windows.7z/Links Awakening DX HD Windows.7z
```

Both rows are the same mistake wearing two shapes. A Windows game is uploaded as an archive — a
folder zipped, or a `.7z` as it was published — so RomM serves it as **one file**. That makes
`is_multi_file_download` false (`len(files) > 1` is how RomM decides to zip, and here there is
exactly one), so the download took the *single-file* path: it renamed the archive into place,
recorded it as the game, and `_collect_and_detect_launch_file` — the only caller that ranks
`.exe` files — never ran. The 4.15 GB zip was still sitting there unopened at 18:20, with a Steam
shortcut pointing at it. The `.7z` had been adopted as a directory of its own, which is how a
path came to be `<archive>/<archive>`.

Nothing about this is about the roms root: the app's structure is `app`, so the downloads belong
under `<data>/roms/win/`. The `~/Emulation/roms/win/…` row is older, from before that structure
was chosen — the second failure, not a second cause.

## Decision

**A Windows entry whose served file is a container is unpacked, then the exe is found inside it.**

1. `domain.rom_files.is_pc_archive(platform_slug, file_name)` answers "is this one file a PC
   game's archive", for `windows`/`win` and the extensions `.zip`, `.7z`, `.rar`. It joins
   `is_multi_file_download` as a second reason to take the extraction path — the download
   service computes `unpack = has_multiple or windows_archive` and otherwise behaves exactly as
   it did: extract dir named from the ROM's identity, ES-DE collapse, `detect_launch_file(...,
   windows=True)`, install recorded with `rom_dir` and the exe as `file_path`.
2. `DownloadFileAdapter.extract_archive` reads the container's **first bytes** rather than its
   name — the download path stages every archive under the multi-file path's `.zip.tmp` suffix,
   so a name is not available to ask. `PK\x03\x04` goes to `extract_zip` unchanged. The 7-Zip
   signature (`37 7A BC AF 27 1C`) and `Rar!` go to the system tools measured present on the Deck
   (`/usr/bin/7z`, `/usr/bin/unrar`), and the result is then held to the same rules the ZIP path
   applies to its
   members: everything under the extract dir, no links, and something actually extracted.
3. A container this build cannot read is a **refusal**, not a fallback: unknown magic, a missing
   tool, a tool that exits non-zero (its last line is shown), or an empty result raises
   `ValueError` and the caller removes the directory. Half a game on disk is worse than none,
   because the launch gate would find an exe in it.
4. The ES-DE collapse rename is skipped for Windows. It names the directory after the launch
   file *including its extension*, which would make the install folder `Game.exe/` for a consumer
   (ES-DE) this launch path does not use — the shortcut names the exe itself.

The manual path is unchanged and remains the fallback it was written to be: **ROM File → Launches
→ Change** lists every executable in the installed folder, best-ranked first.

## Consequences

- The 4.15 GB zip already on the Deck unpacks into `roms/win/Need for Speed - Carbon/` and the
  shortcut is repointed at the exe by the ordinary launch bake — no re-download.
- Multi-file Windows games are untouched: they were already on the extraction path, and they now
  accept a `.7z`/`.rar` served in that shape too.
- `unrar` is required for `.rar` and `7z` for `.7z` (both measured present on SteamOS). On a
  system without them the download fails with a sentence naming the tool, and the archive is not
  kept as a fake install.
- A `.msi` or a setup wizard is still an installer, not a game: the exe ranking will pick it and
  it must be run once, then **Change** points the shortcut at the real exe. That is documented in
  the user guide rather than guessed here.
