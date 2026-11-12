"""Launching RetroArch directly, instead of through RetroDECK's launcher.

RetroDECK wraps every game in ``run_game.sh`` inside its own sandbox, which means a
launch is only as good as RetroDECK's opinion of it: the core, the save directory and
the emulator binary are all resolved *there*. The owned path removes that middleman —
RetroArch is started directly, with the core the plugin chose and the appendconfig the
plugin generated.

The trade is real and worth stating: RetroDECK's launcher also brings up its
environment (its own config, its own core set, its own BIOS layout). Launched
directly, RetroArch reads **its own** config and its **own** cores directory, which on
a Deck is a different directory than RetroDECK's. So a runner is not just "the same
emulator elsewhere" — it carries the two facts that decide whether a core can start at
all: the command prefix and the directory the core ``.so`` lives in.

:func:`retroarch_command` is the whole of the owned argv:

```text
flatpak run org.libretro.RetroArch -L <cores>/<core>.so --appendconfig=<cfg> %ROM%
```

No ``-e`` and no ``%EMULATOR_RETROARCH%``: those exist because ``run_game.sh`` has to
resolve a placeholder before it can exec anything, and with the middleman gone the
command is a plain argv the launcher can run.

Pure compute: a runner value in, a command string out.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from domain.command_text import appendconfig_flag

# What a launch goes through. ``retrodeck`` is the shipped default and stays the
# fallback for every unreadable or unknown value: a settings file edited by hand must
# not be able to leave a platform with no launch path at all.
LAUNCH_BACKENDS = ("retrodeck", "retroarch")
DEFAULT_LAUNCH_BACKEND = "retrodeck"

LaunchBackend = Literal["retrodeck", "retroarch"]

ROM_PLACEHOLDER = "%ROM%"
"""The trailing content argument, in the same form the catalogue uses.

The launcher substitutes it with the ROM path, so an owned command stays the same
shape as every other baked command and needs no special case at the bake site.
"""


@dataclass(frozen=True, slots=True)
class RetroArchRunner:
    """A RetroArch that the plugin can start without RetroDECK.

    ``prefix`` is the whole command head (``flatpak run <id>`` or an executable path),
    and ``cores_dir`` is where *this* RetroArch keeps its ``.so`` files — deliberately
    not the sandbox path RetroDECK uses, because a directly-started RetroArch cannot
    see inside another flatpak's sandbox.
    """

    prefix: str
    cores_dir: str
    label: str


def resolve_backend(value: object) -> LaunchBackend:
    """The backend a settings value selects, falling back to RetroDECK.

    ``"retroarch"`` is the only value that changes anything, and it is a literal string
    rather than a loose truthiness test: a settings file with ``"launch_backend":
    "yes"`` must not silently reroute every launch in the library.
    """
    return "retroarch" if value == "retroarch" else DEFAULT_LAUNCH_BACKEND


def retroarch_command(runner: RetroArchRunner, *, core_so: str, appendconfig: str | None) -> str:
    """The owned launch command for one core, ending in :data:`ROM_PLACEHOLDER`.

    The appendconfig is dropped when its path cannot ride unquoted (see
    :func:`domain.command_text.representable_in_override`): the command is built as
    plain argv with no shell layer to rejoin a split argument, and a launch that writes
    to the user's own save directory still plays the game.
    """
    core_path = f"{runner.cores_dir}/{core_so}.so"
    return f"{runner.prefix} -L {core_path}{appendconfig_flag(appendconfig)} {ROM_PLACEHOLDER}"
