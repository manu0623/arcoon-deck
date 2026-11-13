# 0043 — An owned launch states its own save

**Status:** Accepted (0.35.27)
**Follows:** 0035 (owned roots), 0039 (the plugin installs its runtime), 0042 (the owned
command carries no placeholder).

## Context

Save sync asks one question per ROM: where does this game's save live, and is it a file
per game? `services/saves/rom_info.py` put it to the live catalogue — an ES-DE / RetroDECK
installation — through `AtlasSaveLocationAdapter`, with the emulator's **label** as the key.

That is the right question when an emulator the catalogue knows is doing the writing. On a
device with no RetroDECK it is unanswerable: the catalogue is not installed, and the label
being asked about (`VBA-M`, `PPSSPP (libretro)`) is the plugin's own inventory spelling, not
one any `es_systems.xml` declares. The adapter answered "not established", every sync path
skipped with `save_shape_unsupported`, and `post_exit_sync skipped: save_shape_unsupported`
was logged after every session. Meanwhile the plugin had *already written the answer*: the
generated `--appendconfig` sets `savefile_directory` to the platform's bank directory, and
RetroArch writes `<stem>.srm` there (its own log: `[Override] Redirecting save file to
".../saves/gba/<stem>.srm"`).

So a save the plugin had placed was described as unplaceable, and nothing was synced in
either direction — the fetch included.

## Decision

When the save bank is enabled — the one switch that says the launch is redirected into it —
and the ROM's emulator is a libretro core (or unresolved, which cannot launch a standalone
without a catalogue anyway), the answer comes from
`domain.save_answer.owned_libretro_answer`: state `per-game files`, directory the bank,
components `<stem>.srm` and `<stem>.rtc`.

This is the same shape as `owned_dolphin_answer`, and for the same reason: a program whose
invocation this plugin wrote is not a thing to ask a catalogue about. **The catalogue is not
consulted at all** on that path, which is the point — a test pins that it is never asked.

`content_installed` still rides on the answer, so an uninstalled ROM is not described as
observed. Standalone emulators keep their existing answers (`manifest_answer` for a
provisioned unit, `owned_dolphin_answer` for a pinned user directory); the bank never claims
a save for them.

`.rtc` is listed beside `.srm` because a core with a real-time clock writes both, and only
files that exist are probed for upload — a core without one simply has none. A core that
keeps its save under some other name is not matched by these, so the sync carries nothing
rather than a wrong file.

## Amendment (0.48.12) — Wii is pinned as well

GameCube is no longer the only platform this pin covers. Dolphin is one program and writes both
systems' saves, so a Wii launch is pinned to `<saves>/wii/User` exactly as a GameCube launch is
pinned to `<saves>/gc/User` (`domain.owned_dolphin.user_dir_for`, whose map is now per platform).
The statement is about OUR command either way: a directory we pass with `-u` is not a guess
about where an emulator might write.

The *save inside* that tree is a different question, and it is not answered here. Measured on
the reference Deck, a Dolphin user directory holds an empty `Wii/title` beside `Wii/sys`,
`Wii/ticket` and `Wii/shared1`, and no session has yet written a Wii save into it — so the title
category, the title id spelling and the files under `data/` stay unmodelled until one has.
Until then the answer for a Wii ROM stays the refusal it is today, and a card-shaped answer is
never returned for a Wii launch (the owned-Dolphin branch of `_ask_resolver` is gated on the
GameCube layout family for exactly that reason).

## Consequences

- Save sync has a shape on a no-RetroDECK device: a server save for a GBA title downloads to
  `<stem>.srm` in the bank, and a session's save uploads from it.
- The `save_shape_unsupported` skip disappears for owned launches; it remains for platforms
  this plugin genuinely cannot model (a shared memory card, a save inside the content).
- With the bank off, nothing changes: the catalogue is still asked, and a device that has
  one still gets the catalogue's own answer.
