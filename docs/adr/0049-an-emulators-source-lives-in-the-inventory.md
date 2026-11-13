# 49. A standalone emulator's source lives in the inventory

**Status:** Accepted (0.40.0)
**Follows:** 0037 (the app installs its own runtime), 0041 (the plugin's own inventory),
0045 (a built-in runtime asks its own inventory first), 0048 (a PSP save is its folder set).

## The problem

The app installs its own libretro runtime and its cores, but not the emulators the picker
offers as standalone. On the reference Deck the consequence is visible as a directory of
hand-downloaded AppImages (`~/Applications` holds DuckStation, Citron, Eden, azahar and
shadPS4) and as picker rows that say `needs_setup` until the user copies a file there
themselves. In Game Mode there is no way to do that: no browser download, no terminal.

Stating "where the binaries come from" in code was the option this ADR rejects. It puts a
list that changes every release inside a Python file, and it cannot express the two real
facts about a platform's channels:

- **Some emulators are only stores.** Dolphin's own download page offers Linux users a
  flatpak and no AppImage; its official write-up says so.
- **Some emulators are not in any store.** Eden, Citron and DuckStation have no Flathub
  listing at all — measured on the reference Deck (`flatpak remote-info --user flathub`
  answers nothing for all three), even though the inventory named an id for each. Those
  rows now say "release only", which is the truth, and the old ids survive only as
  detection hints for an install that already exists.

## The decision

**The inventory row states its source, and the source is one of two kinds.** A new
`install` block beside the launch data holds either a `flatpak` app id, or a `github`
repository plus an asset glob. `domain.emulator_install` turns it into one of two plans:
`flatpak install --user -y` (the argv `domain.runtime_install` already owns) or the
release API endpoint plus the pattern the AppImage is found by.

**A release is asked for by API, never by a guessed tag.** Tag spellings differ per
project (`v1.20.4`, `nightly-linux`, a bare commit hash), so a URL built from an assumption
is a 404 that reads like a network failure. `matching_asset` then requires **exactly one**
asset to match the glob: a release that attaches an x86_64 build beside an arm64 or a `v3`
variant is a CPU decision this layer may not make, and taking the first name would install
a binary this machine maybe cannot run.

**The release wins when a row has both.** A store's copy is only as current as its last
manifest bump — PPSSPP spent months on Flathub at 1.18.1 while releases moved on — and the
AppImage channel has no packager in between. The order is a parameter
(`prefer_newest`), so asking for the store build stays possible; it is not a constant
hidden in the adapter.

**A source is not a detection hint.** `host.flatpak` says "if this id is installed, run it
through `flatpak run`"; `install` says "this is how to get one". Keeping them one field is
what produced three rows naming store ids that do not exist — a bug that had already gone
unnoticed because nothing read them for anything but detection.

## Consequences

- Nine systems now have an emulator the plugin can fetch: GameCube and Wii (Dolphin), PS2
  (PCSX2), PSP (PPSSPP), PSX (DuckStation), Switch (Eden, Citron), PS3 (RPCS3), 3DS
  (azahar) and Wii U (Cemu), split six store builds to five releases.
- Three platforms the save layer already understood — `ps3`, `n3ds`, `wiiu` — now have
  inventory rows, so they resolve to an emulator at all. Before this they answered
  `unestablished` because no row existed to answer with.
- Vita is deliberately **not** added. Vita3K's command line takes a *title id* (`-r
  PCSB00952`), and a path handed to it is an install, not a boot, so a path-based shortcut
  cannot launch a downloaded `.vpk`. A row that cannot launch is worse than a missing one.
## The install itself

`adapters.emulator_install` carries out one plan:

- **A store build** is `flatpak install --user -y flathub <id>` — the runtime installer's
  own command, so nothing is written by this plugin and the store's signatures are the
  verification. The resulting state decides success, not the exit code: `flatpak` exits
  non-zero for a transaction it refused because the app is already installed.
- **A release build** is fetched only after the release metadata states a hash for it
  (`assets[].digest: "sha256:…"`). The download streams into `<target>.part` while being
  hashed, a mismatch deletes the partial and leaves any existing install untouched, and an
  asset with **no digest is refused** — a program that launches games is not something to
  run on TLS alone. A local file whose hash already equals the release's is reported
  `already_present` without downloading a byte, which is also how an update starts.
- **The file name is the row's own first `~/Applications/*.AppImage` candidate**, never the
  asset's. Assets are versioned (`PPSSPP-v1.20.4-anylinux-x86_64.AppImage`); installing
  under that name would leave the emulator correct on disk and undetectable in the picker,
  which is a worse failure than not installing it at all.

`services.emulator_provisioning` iterates a system's rows that name a source, installs
serially in the executor, and reports rows with no source under `manual` — "this plugin
cannot fetch it" is an answer a surface can show, not an error. `main.ensure_platform_emulators`
exposes it, mirroring `ensure_platform_cores`.

## What the sources answered, measured on the reference Deck

Four rows were checked against the live API before any of this was called done, and two
of the assumptions did not survive:

- **PPSSPP** — `v1.20.4`, `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`, digest published.
- **DuckStation** — the release attaches `DuckStation-x64.AppImage` **beside**
  `DuckStation-x64-SSE2.AppImage`, so the first glob (`*x64*.AppImage`) matched two and was
  refused by the ambiguity rule; the row now names the baseline build exactly. The digest is
  published.
- **Citron** — `citron-neo/emulator` answers 404 on both endpoints, and the builds live in
  their CI repository as a **nightly** release, which `/releases/latest` never returns. That
  is why the listing fallback exists; the x86_64 baseline asset is
  `citron_nightly-*-linux-x86_64-use-nopgo.AppImage` (the `_v3` build beside it needs a
  newer CPU, so it is not the default).
- **Eden** — GitHub answers **451** for `eden-emulator/Releases`, and the `emuall/eden`
  mirror carries no releases. Eden's own host is a Forgejo instance, whose API is not the
  GitHub one; rather than ship a row that can only fail, Eden is left without a source and
  reported as `manual`.

## What is still not done

The save-folder link (an emulator's own path pointing at the bank) is the next change, and
this one deliberately leaves it out: an install that rearranges the user's saves before it
has ever launched the emulator would be doing two risky things at once.
