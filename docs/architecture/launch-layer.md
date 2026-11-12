# The launch layer

Status: **plan**. Only the save bank it depends on is built
([two-layer-launcher.md](two-layer-launcher.md)). This page is the work order.

## The three decisions this page records

1. **RetroDECK stops being the host.** Tender reads its `retrodeck.json` and `es_systems.xml`
   today; both go. RetroDECK's flatpak remains a supported *last* fallback for installs that
   still use it.
2. **No launcher and no emulator build of our own.** RetroArch is the runner for every platform
   that has a core. We do not ship RetroArch, ship cores, or build an updater for either.
3. **Switch is the exception, and it is an emulator entry, not an architecture.** Eden is the only
   actively developed Switch emulator left; it runs as an external runner alongside RetroArch.

EmuDeck is **optional detection**, never a dependency: if it is installed its launcher scripts are
a usable command surface and its `romsPath` is a hint. Tender does not read its save tree, and does
not use its CloudSync.

## What this layer owns

1. **Which runner plays a ROM.** Resolved per platform and per game, from what is installed.
2. **Where the saves land.** The bank's unit, applied to whichever runner is chosen.
3. **When the session ended.** So the upload happens even if Steam did not stop the game.
4. **What each game's configuration is.** Per-game overrides on top of a shared base.
5. **Whether motion reaches the emulator.** Steam Input by default, DSU where the emulator reads it.

Everything else stays where it is: RomM connection, shortcuts, downloads, BIOS status, the QMK
side, and the bank's own layout rules.

## Runner resolution

One resolver answers "what can play this platform", in this order:

| Order | Runner | How it is found | Used for |
| --- | --- | --- | --- |
| 1 | RetroArch | flatpak `org.libretro.RetroArch`, native `~/.config/retroarch`, or `Emulation/tools/launchers/retroarch.sh` | every platform with a core |
| 2 | External emulator | `~/Applications/<Name>*.AppImage`, `Emulation/tools/launchers/<name>.sh`, `flatpak list`, PATH | the platforms with no core |
| 3 | RetroDECK | flatpak `net.retrodeck.retrodeck` | existing installs, unchanged behaviour |

The catalogue is ours. RetroArch's `.info` files say what extensions and firmware a core wants;
nothing says which core is a platform's sensible default, and nothing says what save layout that
core writes. Both are our data, keyed by **emulator and platform**, because two emulators for one
platform do not share a save format.

Selection precedence stays what the code already has — per-game pick → per-platform pick →
catalogue default — and every level is a label resolved to a concrete invocation at launch, so a
stale pick degrades loudly instead of launching something else.

`domain/emulator_registry.py` holds the emulator half of that data: the definitions a Deck can
offer, the AppImage / launcher / flatpak names that identify each of them, and the
provider-qualified label a pick stores. The same emulator under two providers is two labels —
`PCSX2 (EmuDeck)` and `PCSX2 (RetroDECK)` — because it is two binaries and two save roots, and a
pick that named only "PCSX2" could not answer where the save goes.

### Platforms that have no core

From this repo's own core audit: **Switch, Wii U, PS3, Vita, Xbox, Xbox 360** have no libretro core
at all. Everything else does, including PS2 (LRPS2), 3DS (Azahar), GameCube and Wii (Dolphin's core).
So the external-runner path exists for six platforms, and today only Switch needs it.

## The save contract

This is the part that matters, and it has two shapes.

**Libretro pods can be pointed at the bank.** Launch carries a generated appendconfig, applied after
the user's own config:

```text
<retroarch> -L "<core>" --config "<data>/config/retroarch/retroarch.cfg" \
  --appendconfig "<data>/run/<rom_id>.cfg" "<rom>"
```

```ini
savefile_directory = "<data>/saves/<platform>"
savestate_directory = "<data>/states/<platform>"
sort_savefiles_enable = "false"
sort_savestates_enable = "false"
system_directory = "<data>/bios"
```

That works identically whether RetroArch came from flatpak, from a native install, or from EmuDeck,
which is the point of resolving a runner instead of owning one. Keys Tender manages are therefore
not editable in RetroArch's menu, and the UI says so.

### Generated appendconfig: what is built, and what is measured

`domain/retroarch_appendconfig.py` renders the file and `adapters/retroarch_appendconfig.py` writes it
under `<data>/retroarch/retroarch-<platform>.cfg` — one file per platform, because each states its own
save directory, and rewriting one shared file on every launch would let two platforms' shortcuts fight
over its contents. `EmulatorInvocation.libretro(..., appendconfig=...)` carries the path into the baked
`-e` string as `--appendconfig=<path>` between the core and `%ROM%`, the `=` form being the one that
needs no second token inside an already-quoted argument. A path containing whitespace, a quote or a
backslash is **refused** rather than escaped: the whole override is one double-quoted string, and no
escaping survives `run_game.sh` re-parsing it, so such a launch bakes unredirected instead of broken.

Three things were measured on a Deck (mGBA core, a GBA title), and each one changed the code:

1. **It works, and RetroArch says so.** Verbose output states
   `Appending config: "…/retroarch-gba.cfg"` and then
   `Redirecting save file to "…/saves/gba/<stem>.srm"` — the flat `<stem>.srm` the bank's
   `LIBRETRO_FILE` family expects.
2. **A missing directory is silently ignored.** With the config pointing at a directory that did not
   exist, RetroArch redirected to its *own* default with no error of any kind. So the adapter creates
   the save and state directories before writing, and a failure to create them returns `None` (bake
   unredirected) rather than a config RetroArch will quietly disregard.
3. **A per-core/content override loads after the appendconfig.** `config/mGBA/gba.cfg` is applied
   last, so an override that names a save directory would win over ours. On this Deck it names none
   and ours took effect; the case is recorded rather than defended against, because the guard would
   be to rewrite the user's own override files.

4. **RetroDECK's sandbox can see it.** The open question about whether a host path survives today's
   launch was answered by reading the flatpak's own declaration — `filesystems=…;host;` — and then
   checking inside it: `~/homebrew/data/<plugin>` was listed **and** writable from within
   `flatpak run --command=sh net.retrodeck.retrodeck`. So the baked `--appendconfig` path resolves for a
   launch that goes through RetroDECK as well as for one that does not.

**Wired at exactly one seam.** `ActiveCoreResolver.active_emulator_for_rom` attaches the file to a
resolved libretro invocation via `domain.retroarch_appendconfig.with_appendconfig`, and the three bake
sites inherit it because they all draw their invocation from that resolver. `CoreService`'s pin path
bakes its own invocation from a label, so it attaches the same file itself — a re-bake that dropped it
would leave a re-pinned shortcut writing saves somewhere else, with nothing to show for it but drift.
Both wrap the generator so an exception is logged and treated as "no appendconfig": a save redirection
is never allowed to be the reason a game does not start.

**One switch, two halves.** `save_bank` (default `false`) gates the redirect *and* the lookup, because a
redirect the lookup does not follow is a save that vanishes. With it off, `ensure()` writes nothing at all
and `resolve_save_dir` keeps answering the RetroArch-shaped directory; with it on, the generated config
names `<data>/saves/<platform>` and `RomInfoService` reads that same directory through
`adapters/save_bank_dir.py`. Measured on the Deck: off → `ensure()` returns `None` with no directory
created and the lookup answers the RetroArch path; on → the config is written and the lookup answers
`<data>/saves/gba`, the exact path the config states.

Off by default on purpose: turning it on moves where **new** saves are written while existing saves still
sit where the old path math looks, so enabling it without a migration first would look like lost progress.
The migration is the missing piece, not the switch.

**Still unproven end to end:** no game has been launched through a real Steam shortcut with this build,
so the claim is that the command *renders* with the flag and that RetroArch honours such a file (both
measured) — not that a shortcut on the Deck writes into the bank. That is the next thing to check, and
it does not need the owned launch path.

### The owned launch path

`launch_backend` (`settings.json`, default `"retrodeck"`) selects what a libretro launch goes through.
Set to the literal `"retroarch"`, the baked command stops mentioning RetroDECK at all:

```text
flatpak run org.libretro.RetroArch -L <cores>/<core>.so \
  --appendconfig=<data>/retroarch/retroarch-<platform>.cfg %ROM%
```

No `-e`, no `%EMULATOR_RETROARCH%`, no `run_game.sh`: the plugin resolves the core and the emulator
itself, so nothing in the process tree has to be told what to run.

- `domain/retroarch_runner.py` holds the argv (`retroarch_command`) and the backend choice
  (`resolve_backend`), and is pure: a runner in, a command string out.
- `adapters/retroarch_runner.py` finds the runner: the flatpak first, then the system install, and the
  first one that **actually holds the requested core** wins. Holding the core is the test rather than
  "is installed", because a RetroArch with an empty or relocated cores directory would start and then
  fail on `-L` — a launch that does nothing looks worse than one that falls back.
- The cores directory travels *with* the command prefix, never separately: a directly-started flatpak
  cannot see RetroDECK's `/var/config/retroarch/cores`, so that path would bake a launch that cannot
  find its own core.
- `CoreService`'s pin path applies the same swap, for the same reason the appendconfig does: a re-pin
  must not silently move a shortcut back through RetroDECK.
- No `--config` is passed. The owning RetroArch's own config stays in charge of controllers, shaders
  and everything else the user set there; the appendconfig only pins the keys this plugin manages.
  Seeding an owned base config would take those settings away to gain nothing the appendconfig does
  not already settle.
- **The redirect is a prerequisite, not a companion.** Started directly, RetroArch reads its *own*
  config and writes into its *own* directory — not the directory the save lookup reads — so an owned
  launch without an appendconfig would lose saves silently. `_maybe_owned` therefore refuses to swap in
  a runner for an invocation that carries no appendconfig, which makes `save_bank` off mean "no owned
  launch" and the two opt-ins arrive together.

**Measured on a Deck** (mGBA, a GBA title, the flatpak RetroArch started directly): the core loads from
`~/.var/app/org.libretro.RetroArch/config/retroarch/cores`, `Appending config:` names
`~/.local/share/romm-tender/retroarch/retroarch-gba.cfg`, and the save redirect lands in
`~/.local/share/romm-tender/saves/gba/`. RetroDECK appears nowhere in the command. The per-core
override still loads afterwards and stayed harmless: it sets input and shader keys, not save paths.

**One trap worth remembering.** A flatpak app gets a private `/tmp`, so an appendconfig written to
`/tmp/x.cfg` is accepted on the command line and then silently skipped — the log simply never says
`Appending config:`. The plugin's data root is under `$HOME` and is visible inside the flatpak
(measured with a real run), which is why the file lives there and not in a scratch directory.
`auto_overrides_enable = "false"` does **not** suppress the per-core override (also measured), so it
is not a lever against one.

**Not done yet:** there is no UI toggle for the backend (the settings key is the only switch), the
default is unchanged, and no game has been started through a real Steam shortcut — the measurements
above are a direct run of the same argv with a headless video driver, not a shortcut launch.
`rc=134` at teardown in those runs is the null driver, not a failure of the launch.

**Standalone emulators cannot be pointed anywhere.** Dolphin, Cemu, RPCS3, Ryujinx and Eden take a
game path, not a save directory. For them the bank is applied **place-and-harvest**: stage the
game's save into the emulator's own location before launch, take it back after exit. This is what
makes standalone support look different from core support, and it is why those platforms come last.

**Switch, specifically.** Eden is a yuzu fork, so it writes the yuzu-line layout:

```text
<eden data>/nand/user/save/<user>/<profile>/<title id>/
<eden data>/keys/prod.keys          # required for commercial titles
```

`save_bank.py` already implements that family (`SaveFamily.SWITCH_TITLE`, base
`("switch", "nand", "user", "save")`), discovers the user and profile levels rather than
constructing them, and answers `needs=("profile",)` when it cannot. Eden is a layout mapping and a
base directory, not new save code.

Two gates before a Switch game is playable, both honest refusals rather than guesses:

- **Title id.** `.nsp`/`.xci` identification needs the user's `prod.keys`. Without them the save unit
  cannot be named, so the game shows why instead of syncing to a guessed folder.
- **Firmware.** Eden installs firmware through its own UI from a ZIP or NCA folder. Tender does not
  provision it and must not ship keys.

Ryujinx-line emulators (Ryujinx, kenjinx) are a *different* family — `bis/user/save/<folder id>/0/`,
with title ids resolved through `imkvdb.arc`. Not supported initially; it needs an index reader on
top of everything else.

## Cores update, without us owning them

The original plan built a core store, an updater with channels, and rollback. That goes away with
the emulator build: RetroArch's Online Updater and EmuDeck's Manage Emulators already do it, and
duplicating it was the most expensive part of the plan.

What survives is the part that protects saves: **record the sha256 of the core each game actually
ran with, and when it changes, say so before the next sync.** A core bump can change a save format,
and that is the one update nobody can roll back from the outside. `StatusService.check_core_change`
is already the shape of this check.

## Per-game configuration

Four layers, with an explicit winner:

| Layer | Where | Edited by | Beats |
| --- | --- | --- | --- |
| base | `config/retroarch/retroarch.cfg` (ours) | user, in-emulator | nothing |
| platform | generated into `run/<rom_id>.cfg` | Tender | base |
| per-game | `rom_launch_config` rows → same file | Tender | platform |
| emulator's own per-game override | RetroArch's `config/<Core>/<Game>.cfg` in our tree | user, in-emulator | everything above, for keys Tender does not manage |

Two generated layers and one emulator-owned layer in separate files, because Tender rewrites the
generated file on every launch and would otherwise clobber the user's in-emulator edits.

Storage: `rom_launch_config(rom_id, scope, key, value)` with `scope` `"game"` or `"platform"`, never
touched by the sync UPSERT. Per-game: emulator pick, core options, video, latency, motion mode,
controller mapping, profile or memory-card selection. Not per-game: anything that moves the save
unit, because that is the bank's decision and two clients stop agreeing the moment a row can change it.

## Motion

RetroArch's Linux input drivers do not give accelerometer or gyro data to cores, and in Game Mode
Steam Input owns the controller, so there are two working mechanisms and no third:

- **Steam Input (default).** Gyro mapped to stick or mouse per game; works with every core and every
  external emulator; the plugin already writes per-app Steam Input mode through
  `adapters/steam_config.py`.
- **DSU (native motion).** A bridge on UDP `127.0.0.1:26760`, started by the session wrapper and
  killed with it, for emulators that speak cemuhook — Dolphin and Cemu today. It needs the IMU free,
  so it composes with the existing per-app `steam_input_mode: "force_off"`. Eden's motion support is
  unverified and is not claimed until checked.

`motion_mode` is per game (`off` / `steam_input` / `dsu`) with a platform default, and the picker
only offers `dsu` for entries whose catalogue row declares it.

## Session end

`rom-launcher` stays a pure `exec "$@"` (ADR-0009); ownership is detected by the `/bin/rom-launcher`
suffix, so it does not move. Session recording goes in a second binary named by `launch_options`:

```text
/data/bin/rom-launcher  "/data/bin/tender-session 42 -- /data/scripts/eden.sh -g /roms/switch/Game.nsp"
```

`tender-session` writes `run/42.json`, starts the DSU bridge when asked, execs the runner, and on
exit writes the status and removes the entry. The backend treats a dead pid with no exit status as
evidence of an unclean exit: recover the save, then clear it. Startup clears stale entries.

## Phases

**1 — runner resolution.** `LaunchCatalogue` behind a Protocol with the RetroDECK implementation
moved behind it unchanged; a catalogue keyed by (emulator, platform); detection for RetroArch's
three install shapes; `launch_backend` in settings defaulting to `"retrodeck"`. Ships with no
behaviour change.

**2 — point RetroArch at the bank.** Generated appendconfig, `system_directory`, saves and states
landing in the bank, and the owned launch path behind `launch_backend`. Base config seeding was
dropped deliberately: the owning RetroArch's own config stays in charge, and the appendconfig settles
the keys the plugin manages. Done when a GBA game launches through RetroArch with no RetroDECK process
in the tree and writes `saves/gba/<stem>.srm` — the launch half is measured, the `.srm` half still
needs a real shortcut launch.

**3 — save identity.** `domain/content_identity.py` + `adapters/content_identity.py`: PS1/PS2 disc
serials, Dreamcast IP.BIN, the GameCube disc game code and 3DS title ids — the four the bank's families
actually key on. Without it most of the interesting platforms cannot resolve. Done when a save lookup
spends these ids; the reader itself is finished and measured (below). PSP is deliberately out until a
`PARAM.SFO` reader exists, because its id is only reachable by walking the ISO tree.

### Reading a game's identity

Every non-libretro row in [the save structure](save-structure.md) is keyed by an id the content path
does not carry: a PS2 folder is named after the disc serial, a GameCube set is chosen by game code, a
3DS title writes under its 16-hex title id, a Dreamcast VMU is named after the IP.BIN product number.
The reader is split the way the rest of the plugin is — pure parsers over bytes in `domain`, one
adapter that decides which bytes to read — so the parsing is testable without a ROM and the reading is
bounded by each format's own layout rather than by grabbing a file whole.

Three things came out of measuring it against real carts (three `.3ds` images, plus fixtures for the
formats this Deck has no content for):

1. **The NCCH magic is at 0x100 of the partition, not at its start.** The NCSD header points at the
   NCCH *including* its 0x100-byte signature block, so a reader looking for `NCCH` at the partition
   offset logs "no NCCH" on every real cart — which is exactly what the first version did before the
   dumps said otherwise.
2. **The program id is the title id.** 8 bytes little-endian at 0x118, rendered as 16 lowercase hex:
   `0004000000054000` for Super Mario 3D Land (USA), `00040000000EC300` for A Link Between Worlds,
   `00040000001B4000` for Fire Emblem Echoes. Those three agree with the published ids.
3. **Only the application category counts.** `00040000` is the application high word; `00040130` is a
   system title, which writes no save this bank could place, so it refuses rather than naming a folder
   the emulator never writes to.

**Wired into the save lookup.** `RomInfoService` fills the resolver's hole: when an answer carries
`needs=("save_id",)` and the ROM's content is installed, the adapter reads the game file and
`domain.save_answer.fill_save_id` completes the directory, the backing directory and every component,
then re-derives the state. Only an installed ROM is read — for an uninstalled one the answer's path is a
prediction about bytes that do not exist yet. Everything else (no seam, no hole, a platform with no
reader, a header stating nothing) returns the answer untouched, so the hole semantics stay intact.

Measured on the Deck through the real Azahar card and a real cart: `Super Mario 3D Land (USA).3ds`
turns `hole` with `…/title/<save_id>/data` into `per_game_files` at
`…/title/00040000/00054000/data`, synced name `00000001`; with the seam absent the answer is the same
hole with the same template. 3DS **extdata** stays a hole of its own — it is keyed by an id the title id
does not fill, so filling one need does not make the answer syncable. PSP, PS3 and Vita stay unread
until a `PARAM.SFO` reader exists.

**4 — per-game configuration.** The table, the generated files, the precedence, the game-detail UI.

**5 — session end and motion.** The wrapper, `run/` registry, the exit watcher firing the existing
`finalize(rom_id)`, Steam Input composition, and the DSU bridge for Dolphin/Cemu.

**6 — external runners: Eden first.** Detection, argv, the yuzu-line base directory, place-and-harvest,
the keys and firmware gates, and `.nsp`/`.xci` title-id reading. Then Cemu, RPCS3, Vita3K, Xemu, Xenia
as catalogue entries.

**7 — opt-in and retreat.** A per-platform switch to the owned path (today's switch is global), then
the `launch_backend` default flips. RetroDECK stays selectable.

## Risks

- **Two clients, one save.** The bank owns the unit and the archive roots; no other layer composes a
  path.
- **A frozen launch command.** `launch_options` is baked per shortcut; the three existing bake sites
  are the only writers, and the new path must not add a fourth.
- **Core drift.** A core update can change a save format; the recorded hash is the warning, not a fix.
- **Switch's legal weather.** Yuzu and Ryujinx are gone, Citron was disrupted, thirteen projects were
  DMCA'd in one wave. Detect Eden, never bundle or install it, and never ship keys.
- **EmuDeck's save tree is a symlink farm.** `Emulation/saves/<emulator>` points at each emulator's
  real directory, so backing it up does not preserve saves and its CloudSync collides on per-device
  folder numbering. Detecting EmuDeck's launchers is useful; adopting its save layout is a regression.

## Explicit non-goals

Shipping or updating emulators and cores, bundling anything not distributable, EmuDeck's CloudSync,
save states (core- and version-coupled, which is why Tender already refuses them), netplay, shader
packs, and per-core option UIs beyond what the per-game table needs.
