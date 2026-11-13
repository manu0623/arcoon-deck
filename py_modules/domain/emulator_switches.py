"""The command-line spellings an emulator accepts, and rewriting commands into them.

A platform's emulator rows are free text: an ES-DE ``<command>`` template, a
distribution's launcher script, a row a catalogue carries for one release. When one
of those spells a switch the emulator refuses, the plugin bakes the text verbatim into
a Steam shortcut and the game never starts. Measured on the reference Deck, a
standalone ps2 launch died with ``Unknown parameter: '--fullscreen'`` from PCSX2 2.8.2
before any game was parsed, while the same build's own ES-DE entry spells it
``-batch`` and EmuDeck's launcher line ``-batch -fullscreen`` — both single-dash.

So a command naming an emulator with a *measured* spelling is rewritten into that
spelling before it is baked. The rule is data (:data:`SWITCH_SPELLINGS`), keyed on a
token the command itself carries — the ES-DE find-rule name, the binary, and the
flatpak id all spell the emulator's name — and it touches whole switch tokens only:
a quoted path, a ``%PLACEHOLDER%`` and a bare ``--`` positional separator pass
through unchanged.

Only emulators whose refusal was measured are listed. Guessing a spelling for an
emulator nobody has run would bake a different command on no evidence, which is the
same mistake as guessing a save path.

PCSX2's own list (https://pcsx2.net/docs/advanced/cli) states the single-dash forms
and keeps ``--`` as the "no more arguments" separator, so ``--`` is never rewritten.

A replacement need not be a respelling of the same switch. ``-nogui`` is rewritten to
``-batch``, which is a *different* switch doing what the caller meant: PCSX2's Qt build
aborts instead of running under ``-nogui`` (the page-fault handler asserts and calls
``abort()``; upstream issue #7620 records that batch mode works where ``-nogui`` does
not), and it was the switch in the command line of two real ``SIGABRT`` dumps on the
reference Deck. Both imply "close when the game shuts down"; only one survives.
"""

from __future__ import annotations

import re

#: Emulator name token -> {rejected switch: switch to bake instead}.
#:
#: The token is matched case-insensitively between alphanumeric boundaries, so
#: ``net.pcsx2.PCSX2``, ``pcsx2-qt`` and ``%EMULATOR_PCSX2%`` all name PCSX2 while an
#: unrelated command that merely contains the letters (``pcsx2nothing``) does not.
#:
#: Both spellings of ``nogui`` are listed: ``--nogui`` is rewritten first, so the bare
#: ``-nogui`` rule only ever sees a command that used the single-dash form.
SWITCH_SPELLINGS: dict[str, dict[str, str]] = {
    "pcsx2": {
        "--batch": "-batch",
        "--bigpicture": "-bigpicture",
        "--fastboot": "-fastboot",
        "--fullscreen": "-fullscreen",
        "--nogui": "-batch",
        "--slowboot": "-slowboot",
        "-nogui": "-batch",
    },
}


def normalise_switches(command: str) -> str:
    """Rewrite *command*'s switches into the spelling the emulator it names accepts.

    A command naming no emulator in :data:`SWITCH_SPELLINGS` — and one already
    spelling its switches correctly — is returned unchanged. Each rejected token is
    replaced only where it stands alone, so ``-fullscreen`` is left alone by the
    ``--fullscreen`` rule and a path containing the same letters is untouched.
    """
    for token, spellings in SWITCH_SPELLINGS.items():
        # Boundaries are alphanumerics, not ``\b``: an underscore is a word character,
        # so ``\bpcsx2\b`` would not match ``%EMULATOR_PCSX2%`` — the very shape an
        # ES-DE command uses to name its emulator — and the rewrite would silently
        # skip every catalogue row.
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])", command, re.IGNORECASE) is None:
            continue
        for rejected, accepted in spellings.items():
            command = re.sub(rf"(?<![\w-]){re.escape(rejected)}(?![\w-])", accepted, command)
    return command
