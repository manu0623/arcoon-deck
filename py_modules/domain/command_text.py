"""Text that has to survive being carried in a launch command.

Two renderers now build a launch string: the RetroDECK ``-e`` override and the owned
RetroArch argv. Both can carry an ``--appendconfig`` path, and both refuse the same
characters for the same reason — neither has a shell layer behind it that could rejoin
an argument split on whitespace, or survive a quote that reopens the string. The rule
therefore lives here once rather than being restated (and eventually diverging) in each
renderer.
"""

from __future__ import annotations

# Characters that cannot ride inside the launch command. Whitespace would split the
# argument into extra argv entries with no quoting layer left to rejoin them; quotes and
# backslashes would end or reopen the argument depending on how the launcher parses the
# string, which is not a guess worth baking into every shortcut.
_UNREPRESENTABLE = frozenset(" \"'\\\t\n\r")


def representable_in_override(path: str) -> bool:
    """Whether *path* can ride inside a launch command without changing its meaning.

    The RetroDECK form is one double-quoted argument — ``-e "…"`` — so a path holding a
    double quote would end it early, and one holding whitespace would split into two
    argv entries. There is no escaping that survives ``run_game.sh`` parsing the string,
    so such a path simply does not get an appendconfig: the launch still happens, just
    unredirected, which degrades to the user's own RetroArch config rather than to a
    broken command.
    """
    return bool(path) and not (_UNREPRESENTABLE & set(path))


def appendconfig_flag(path: str | None) -> str:
    """The `` --appendconfig=<path>`` fragment, or ``""`` when one cannot be carried.

    ``--appendconfig=FILE`` rather than a spaced ``--appendconfig FILE`` precisely
    because the RetroDECK override is already inside one quoted argument: the ``=`` form
    needs no second token and matches how RetroArch documents it. The owned argv has no
    such constraint, but keeps the same shape so one rule covers both.
    """
    if path is None or not representable_in_override(path):
        return ""
    return f" --appendconfig={path}"
