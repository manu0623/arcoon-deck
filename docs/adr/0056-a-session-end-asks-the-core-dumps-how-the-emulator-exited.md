# ADR-0056 — A session end asks the core dumps how the emulator exited

**Status:** accepted

## The problem

A session ends when Steam stops reporting the game as running (`SteamUIStore.RunningApps`
goes empty). That signal is identical whether the player quit or the emulator died, and
nothing in the plugin could tell the difference: after a PS2 session that aborted on the
way out, the log recorded a clean end — reconciled playtime, a released lease, a normal
`post_exit sync` — while the emulator had in fact died of `SIGABRT` twice and the Deck
hard-reset minutes later.

The plugin is not the emulator's parent, so there is no `wait()` and no exit status to
collect. Steam's `RunGame` is fire-and-forget, and the systemd scope a flatpak runs in
logs only `Started` and `Consumed` — measured, never `code=killed` or `status=6/ABRT`.

What a signal death *does* leave is a core dump, and the listing is readable without
elevation:

```
$ coredumpctl --since @1794604000 --json=short list
[{"time":1794604364085378,"pid":273611,"sig":6,"exe":"/app/bin/pcsx2-qt","corefile":"inaccessible"}]
```

## The decision

**At session finalize, ask `coredumpctl` for dumps since the session began, and report one
whose executable the ROM's own baked launch command names.** A dump carries no game id, so
the link is made from names: `domain.emulator_crash.emulator_name_tokens` reduces the
baked command to the names it starts (`flatpak run net.pcsx2.PCSX2 …` → `pcsx2`;
`… -L …/pcsx2_libretro.so` → `retroarch`, `pcsx2`) and a dump matches when its
executable's basename contains one of them. The comparison runs against the *baked
command* rather than a hard-coded emulator table because that command is the one fact
that says which program this ROM's session actually started.

The question is asked **before** the playtime recorder, which clears the session marker
the window is dated from.

The answer is three-valued, and the distinction matters:

- a matching dump → `crash` in the finalize result, and a `[session] rom N: the emulator
  crashed (SIGABRT, exe=…, pid=…)` line in the log;
- no dump → nothing reported (a clean exit, or cores disabled — this cannot tell, and does
  not pretend to);
- the question could not be put — no session marker, no baked command, no `coredumpctl`,
  unreadable rows → `None`, treated exactly like the previous case. "Could not ask" is
  never reported as a crash, and never as a clean exit either.

A failing probe is logged and swallowed: the playtime, save-sync and migration steps of
the finalize must still run.

## What this does not do

- It does not recover the emulator's exit *code*: that number is not available to anyone
  outside the process. Only signal deaths that left a dump are visible, which is what
  the original failure was.
- It does not repair the crash. It names it — the actual fix for the PS2 abort was the
  launch command's `-nogui`, rewritten in ADR-0054.
- It does not surface a toast. The crash is returned to the frontend (`crash` on the
  finalize result) and written to the session log; nothing in the UI reads it yet.
