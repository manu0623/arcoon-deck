# 0037 — The plugin supplies the cores its runtime loads

## Status

Accepted. Fills the third coupling named in ADR-0035.

## Context

ADR-0035 gave the plugin its own runtime, ADR-0036 its own inventory. Neither launches
anything: a libretro row needs a `.so` in the cores directory the owned RetroArch loads
from, and on a Deck without RetroDECK that directory is where RetroArch's Flatpak keeps its
cores — real, empty, and unaffected by RetroDECK's own bundle. Measured on the reference
Deck, every libretro row across snes/ps1/nds read `needs_setup / not_installed` for exactly
this reason, and the picker correctly refused to bake them.

## Decision

The plugin downloads cores itself, from the libretro project's build bot
(`.../nightly/linux/x86_64/latest/<core>.so.zip`), into the cores directory the owned
runtime resolves (`domain.runtime`). Nothing is downloaded while RetroDECK drives: its
cores live inside its flatpak, `cores_path()` is empty there, and an empty answer is a
refusal rather than a path — writing relative to the working directory is the failure this
rule prevents.

**Nothing is trusted before it is written.** A download is accepted only when:

1. the bytes open as a ZIP (`not_a_zip`);
2. the requested member is present by exact name, or by a single nested match
   (`no_core_member` — a bundle with two candidates is refused, because which one is the
   core would be a guess);
3. reading the member verifies its CRC against the central directory (`corrupt_member`),
   which is what catches a truncated transfer that still opened;
4. the payload is at least 4 KiB (`too_small`) and starts with the ELF magic
   (`not_elf`).

The write is atomic — `<core>.so.part` then `os.replace` — so a transfer that dies
mid-write leaves nothing RetroArch could try to load, and a retry cannot shadow a working
core.

**What this verifies, stated plainly:** the build bot publishes no per-file digest, so this
is structural verification — container integrity, member identity, format — not a
cryptographic match against a published checksum. It catches a truncated, corrupt, empty,
swapped or error-page download. It does not prove upstream authenticity, and the code says
so rather than implying otherwise.

Which cores a platform needs is read off the inventory (ADR-0036), so adding an emulator to
the document adds its core to this work without code changes. `CoreProvisioningService`
installs only what is missing, one core at a time in the executor, and reports per core:
one unavailable core does not abort the batch, and the response separates `installed`,
`already_present` and `failed` with reasons.

## Consequences

- The trigger is explicit rather than automatic on launch: a launch path that waits on a
  network transfer is a launch that hangs when the network is down, and a core is a
  one-time install per platform. `ensure_platform_cores(system_name)` answers for one
  system and `ensure_all_platform_cores()` sweeps every enabled platform; **Settings →
  Emulators & Cores → Install Missing Cores** is the button that calls the sweep. Until
  that button existed the machinery had no caller in the UI, which is indistinguishable
  from not having it. The sweep reads `enabled_platforms` and falls back to the synced
  platforms when that dict is still empty, and it **names** the platforms it cannot
  install for (no inventory entry, or standalone-only) instead of counting them as done
  — a device told "everything is installed" while four of its platforms were never looked
  at is the failure that makes the button untrustworthy.
- A successful install is visible to everything else without a cache flush:
  `OwnedCatalogueAdapter` probes the cores directory on every answer by design, so the rows
  become bakeable as soon as the file is there.
- The architecture assumption is named in the URL: it is the x86_64 nightly tree. A
  different host architecture needs a different base, which is why it is a parameter of
  `core_url` and of the adapter.
- Nightly builds are not a pinned version: an install today and one next month are
  different binaries. Pinning a release tag would trade freshness for reproducibility; that
  is a decision for a later ADR if a core ever regresses between nightlies.
