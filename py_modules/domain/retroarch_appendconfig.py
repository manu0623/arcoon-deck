"""The generated RetroArch config that points a platform's saves at the bank.

RetroArch is told where to write by its own configuration, so the plugin does not
move files after the fact — it states, at launch, that this platform's saves live in
the bank. The statement is one small file passed as ``--appendconfig``, which
RetroArch loads after the user's ``retroarch.cfg`` and therefore wins.

Measured on a Deck (mGBA core, a GBA title), RetroArch's own log is the proof:

```text
[INFO] [Config] Appending config: ".../retroarch-gba.cfg"
[INFO] [Override] Redirecting save file to ".../saves/gba/<stem>.srm"
```

**Why the sorting keys are switched off here.** The bank is *flat*: one directory per
platform, one file per game, named by the ROM's stem. RetroArch's ``sort_*`` flags
would nest that into ``<Core>/`` or a content directory, which is a different tree
than :mod:`domain.save_bank` describes and than RomM expects. They are disabled
explicitly rather than left to the user's config, because a user who turned sorting
on would otherwise get saves the plugin cannot find.

**The directory must exist before this file is honoured.** Measured on a Deck:
RetroArch accepts a ``savefile_directory`` that is not on disk and then silently writes
to its own default instead — so generating this config is only half the job, and
:mod:`adapters.retroarch_appendconfig` creates the directories before writing.

**And why they are set rather than assumed.** Every key this file writes is written,
including the ones that match today's defaults: an appendconfig derived from the
*current* config would silently keep whichever value was there, and a later RetroArch
default change would move saves out from under the bank with no code change here.

Pure compute: takes the directories as arguments and returns text. Nothing is written,
no path is probed, and the caller decides where the file lives.
"""

from __future__ import annotations

import posixpath
from dataclasses import replace
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from domain.shortcut_data import EmulatorInvocation

# Keys written in this order, always. A stable order is what lets the adapter compare
# text and skip a rewrite, and it makes two generated files for one platform
# byte-identical — a diff of the bank's config is then a diff of its intent.
_SORT_KEYS: tuple[tuple[str, str], ...] = (
    ("savefiles_in_content_dir", "false"),
    ("savestates_in_content_dir", "false"),
    ("sort_savefiles_enable", "false"),
    ("sort_savefiles_by_content_enable", "false"),
    ("sort_savestates_enable", "false"),
    ("sort_savestates_by_content_enable", "false"),
    # A save written beside the ROM is not a save the plugin can sync, so the
    # autosave-on-exit and related "guess a location" behaviours stay off too.
    ("autosave_interval", "0"),
)

STATE_DIR_NAME = "states"
"""Where save states go, beside the bank's own ``saves`` directory.

States are deliberately **not** part of the bank: RomM syncs saves, and a state is a
snapshot of emulator memory rather than a cartridge save. They still get a stated
home so they stop accumulating next to the ROMs, which is where a default RetroArch
puts them.
"""


def appendconfig_name(platform: str) -> str:
    """The file name for *platform*'s generated config (``retroarch-gba.cfg``).

    One file per platform rather than one global file, because the content differs:
    each names its own save directory. A single shared file would be rewritten
    whenever a different platform launched, and two platforms' shortcuts would then
    fight over its contents.
    """
    return f"retroarch-{platform}.cfg"


def _quote(value: str) -> str:
    """Render one config value, quoted the way ``retroarch.cfg`` spells strings.

    RetroArch writes ``key = "value"``. A newline or carriage return cannot be
    represented at all — it would end the setting and start a new line of arbitrary
    config — so it raises here rather than producing a file that says something the
    caller did not ask for.
    """
    if "\n" in value or "\r" in value:
        raise ValueError(f"cannot put a line break in a RetroArch config value: {value!r}")
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_appendconfig(*, save_dir: str, state_dir: str, system_dir: str | None = None) -> str:
    """The complete appendconfig text for one platform.

    *save_dir* and *state_dir* are absolute Deck paths, and both are written: a save
    root with no stated state root is half a contract, and RetroArch would fill the
    other half from the user's config, scattering states next to ROMs on an SD card.

    *system_dir* is added only when the caller has one (a BIOS directory it resolved),
    because writing a guessed BIOS path would send firmware lookups somewhere real. If
    it is absent, RetroArch keeps whatever ``system_directory`` the user's own config
    already states — which is the honest outcome, since the plugin has no opinion on a
    directory it did not resolve.
    """
    lines = [
        "# Generated by Arcoon Deck. Do not edit: the plugin rewrites this file.",
        "# Passed to RetroArch as --appendconfig so this platform's saves land in the bank.",
        "",
        f"savefile_directory = {_quote(save_dir)}",
        f"savestate_directory = {_quote(state_dir)}",
    ]
    if system_dir is not None:
        lines.append(f"system_directory = {_quote(system_dir)}")
    lines.append("")
    lines.extend(f"{key} = {_quote(value)}" for key, value in _SORT_KEYS)
    return "\n".join(lines) + "\n"


@overload
def with_appendconfig(invocation: None, appendconfig: str | None) -> None: ...


@overload
def with_appendconfig(invocation: EmulatorInvocation, appendconfig: str | None) -> EmulatorInvocation: ...


def with_appendconfig(
    invocation: EmulatorInvocation | None,
    appendconfig: str | None,
) -> EmulatorInvocation | None:
    """Attach *appendconfig* to a libretro invocation, leaving everything else alone.

    Only ``kind == "libretro"`` takes it: a standalone emulator is placed-and-harvested
    rather than pointed anywhere, so a path here would be a claim about a program that
    never reads it. An invocation that already carries one is returned unchanged, so
    two callers cannot stack two ``--appendconfig`` flags onto one command.

    ``None`` for the path — no data directory, a platform the generator refused — means
    "bake as before", which is the safe degradation: a launch that writes to the user's
    own RetroArch directory still plays the game.
    """
    if invocation is None or appendconfig is None or invocation.kind != "libretro":
        return invocation
    if invocation.appendconfig is not None:
        return invocation
    return replace(invocation, appendconfig=appendconfig)


REPLAYED_KEYS: tuple[str, ...] = ("savefile_directory", "savestate_directory")
"""The keys a finished launch writes back into the user's ``retroarch.cfg``.

RetroArch saves its config on exit, and the value it saves is the one the launch was
handed — so a redirected launch *bakes its own save directory into the user's config*.
That baked value is what RetroArch then states on the next launch, and measured on a
Deck it wins over the ``--appendconfig`` that launch passes: a PPSSPP launch whose
appended config said ``…/romm-tender/saves/psp`` still resolved
``…/romm-tender/saves/psp/PSP/SAVEDATA``, the one-level-too-deep value an earlier
launch had left behind. The game then read ``SAVEDATA/PSP/SAVEDATA`` and opened with no
save at all.
"""

_DEFAULT = '"default"'


def _value_dir(value: str, user_home: str | None) -> str:
    """The directory a config value names, with a leading ``~`` made absolute."""
    unquoted = value.strip().strip('"')
    if user_home and (unquoted == "~" or unquoted.startswith("~/")):
        unquoted = posixpath.join(user_home, unquoted[2:])
    return posixpath.normpath(unquoted)


def unbake_replayed_paths(text: str, *, data_dir: str, user_home: str | None = None) -> str | None:
    """Restore ``default`` for save/states paths an earlier launch baked into *text*.

    Only values **inside the plugin's own data directory** are touched: those are the
    ones a previous redirected launch wrote, and none of them can be a deliberate user
    setting (the user has no reason to point RetroArch at the plugin's bank instead of
    the plugin doing it per launch). Every other value is left exactly as written — a
    config the user maintains is not this plugin's to rewrite.

    Returns the repaired text, or ``None`` when there is nothing to change, because the
    caller only writes when a launch would otherwise be overridden.
    """
    root = posixpath.normpath(data_dir)
    changed = False
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        key, separator, value = line.partition("=")
        if not separator or key.strip() not in REPLAYED_KEYS:
            continue
        resolved = _value_dir(value, user_home)
        if resolved != root and not resolved.startswith(root + "/"):
            continue
        ending = line[len(line.rstrip("\r\n")) :]
        lines[index] = f"{key.strip()} = {_DEFAULT}{ending}"
        changed = True
    return "".join(lines) if changed else None


def appendconfig_dirs(
    *, data_dir: str, layout_subdir: tuple[str, ...], core_subdir: tuple[str, ...] = ()
) -> tuple[str, str]:
    """The ``(save_dir, state_dir)`` pair the generated file states.

    Split out from :func:`render_appendconfig` so the adapter cannot compose a save
    directory differently from the way the bank does: *layout_subdir* is
    :func:`domain.save_bank.layout_for`'s subdir, passed in rather than re-derived,
    and the state directory mirrors it under ``states/``. The platform is not a
    parameter because the subdir already is it — a second spelling could disagree.

    *core_subdir* is the tail of *layout_subdir* the emulator builds for itself
    (PPSSPP's ``PSP/SAVEDATA``). It is stripped from both directories, because a core
    handed a folder creates that tree inside it: stating the whole subdir made the saves
    land one level below the layout the lookup reads.
    """
    stripped = layout_subdir
    if core_subdir and layout_subdir[-len(core_subdir) :] == core_subdir:
        stripped = layout_subdir[: -len(core_subdir)]
    save_dir = posixpath.join(data_dir, "saves", *stripped)
    state_dir = posixpath.join(data_dir, STATE_DIR_NAME, *stripped)
    return save_dir, state_dir
