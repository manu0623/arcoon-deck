"""What a crashed emulator leaves behind, and how to recognise it as this game's.

Steam does not report the exit status of the game it launches: ``RunGame`` is
fire-and-forget, and the systemd scope a flatpak runs in logs only ``Started`` and
``Consumed`` — never ``code=killed`` or ``status=6/ABRT``. Measured on the reference
Deck, the whole record of a PS2 session that died on the way out was two core dumps:

```
Fri 2026-11-13 16:12:44  SIGABRT  /app/bin/pcsx2-qt
Fri 2026-11-13 16:13:24  SIGABRT  /app/bin/pcsx2-qt
```

Nothing in a dump names the game, and the plugin is not the process's parent, so the
link has to be made from *names*: the tokens the ROM's baked launch command carries
(a flatpak app id's last segment, an executable's basename, a libretro core's name)
against the executable path the dump recorded. ``flatpak run net.pcsx2.PCSX2 …``
yields ``pcsx2``, which matches ``/app/bin/pcsx2-qt``; ``flatpak run
org.libretro.RetroArch -L …/pcsx2_libretro.so`` yields ``retroarch`` and ``pcsx2``,
so a dump of either binary belongs to that session.

A dump that matches nothing is not reported: this module answers only what it can
show, and a signal death with no dump (cores disabled, a flatpak's own crash handler)
stays unproven rather than guessed at.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

#: Words a launch command carries that name no emulator: the launcher, the subcommand,
#: and the shell prefixes ES-DE templates use.
_SKIP_WORDS = frozenset({"flatpak", "run", "env", "sh", "bash", "usr", "bin", "app", "exec"})

#: Suffixes stripped from a token before matching, so ``pcsx2_libretro.so`` contributes
#: ``pcsx2`` and ``PPSSPP.AppImage`` contributes ``ppsspp``.
_STRIPPED_SUFFIXES = (".appimage", ".so", ".sh", ".bin")

#: A quoted Path is a ROM or a config file, never an emulator's name.
_QUOTED_RE = re.compile(r'"[^"]*"|\'[^\']*\'')

#: ``sig`` numbers, for a message a person can read without a signal table.
_SIGNAL_NAMES = {4: "SIGILL", 5: "SIGTRAP", 6: "SIGABRT", 7: "SIGBUS", 8: "SIGFPE", 11: "SIGSEGV"}


@dataclass(frozen=True)
class Coredump:
    """One core dump ``coredumpctl`` reported."""

    timestamp_us: int
    pid: int
    signal: int
    exe: str

    @property
    def executable_name(self) -> str:
        """The dump's executable path without its directories, lowercased."""
        return self.exe.rsplit("/", 1)[-1].lower()

    @property
    def signal_name(self) -> str:
        """``SIGABRT`` for 6, or ``signal 15`` for one this module has no name for."""
        return _SIGNAL_NAMES.get(self.signal, f"signal {self.signal}")


def parse_coredumps(text: str) -> tuple[Coredump, ...]:
    """Parse ``coredumpctl --json=short list`` output.

    An empty answer (``[]``, blank) and anything that is not that JSON shape both
    return ``()``: "no dumps" and "not the output this reads" are the same answer to
    the caller, which must not turn an unreadable list into a crash report.
    """
    try:
        rows = json.loads(text or "[]")
    except json.JSONDecodeError:
        return ()
    if not isinstance(rows, list):
        return ()
    dumps: list[Coredump] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        timestamp, signal, exe = row.get("time"), row.get("sig"), row.get("exe")
        if not isinstance(timestamp, int) or not isinstance(signal, int) or not isinstance(exe, str):
            continue
        pid = row.get("pid")
        dumps.append(
            Coredump(timestamp_us=timestamp, pid=pid if isinstance(pid, int) else 0, signal=signal, exe=exe)
        )
    return tuple(dumps)


def emulator_name_tokens(launch_options: str) -> tuple[str, ...]:
    """The names a baked *launch_options* gives the program it starts.

    Quoted arguments are dropped first: a ROM path can contain any word, including one
    that looks like an emulator. Each remaining word contributes its last dotted
    segment or its basename, so a flatpak app id, an AppImage path and a core file all
    answer the name they are known by. Words shorter than three characters are dropped
    as too generic to match on.
    """
    tokens: list[str] = []
    for word in _QUOTED_RE.sub(" ", launch_options).split():
        if not word or word.startswith("-"):
            continue
        lowered = word.lower()
        if lowered in _SKIP_WORDS:
            continue
        candidate = lowered.rsplit("/", 1)[-1]
        if "/" not in word and candidate.count(".") >= 2:
            candidate = candidate.rsplit(".", 1)[-1]
        for suffix in _STRIPPED_SUFFIXES:
            if candidate.endswith(suffix):
                candidate = candidate[: -len(suffix)]
        candidate = candidate.replace("_libretro", "")
        if len(candidate) >= 3 and candidate not in tokens:
            tokens.append(candidate)
    return tuple(tokens)


def crashed_emulator(dumps: tuple[Coredump, ...], tokens: tuple[str, ...]) -> Coredump | None:
    """The first dump whose executable one of *tokens* names, or ``None``."""
    for dump in dumps:
        name = dump.executable_name
        if any(token in name for token in tokens):
            return dump
    return None


def crash_payload(dump: Coredump) -> dict[str, Any]:
    """The crash as the frontend receives it: what died, how, and when."""
    return {
        "exe": dump.exe,
        "pid": dump.pid,
        "signal": dump.signal,
        "signal_name": dump.signal_name,
        "detected_at_us": dump.timestamp_us,
    }
