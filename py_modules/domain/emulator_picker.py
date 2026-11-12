"""Add the externally detected emulators to a platform's picker list.

The picker's rows come from ES-DE's ``es_systems.xml``, which knows the emulators
RetroDECK ships and nothing about an AppImage the user downloaded themselves. On a
Deck that also has EmuDeck, Eden or a flatpak PCSX2, those installs are invisible in
a menu that claims to list what this platform can launch with.

This module appends them, and the rule that matters is **the label**: every row is
the provider-qualified pick key (:meth:`InstalledEmulator.label`), so ``Eden
(AppImage)`` and ``Eden (EmuDeck)`` are distinct rows and a stored pick says which
install's save root applies. An unqualified row would be a pick that cannot answer
where the save goes.

**They are listed, not yet launchable.** The launch layer that runs an external
emulator (its argv, its sandbox, its ROM placeholder) is a separate phase, so each
added row is ``needs_setup`` with reason :data:`EXTERNAL_LAUNCHER_REASON`. That is
the same shape the picker already gives a missing standalone emulator, and it has two
consequences that are the point: the row is visible with a stated reason, and
:func:`domain.emulator_commands.select_default_option` can never make one the
default, so nothing starts launching into a command this phase cannot build.

Rows keep ES-DE's order and the externals are appended after it: a catalogue the
distro curates is a better default than whatever happens to be in ``~/Applications``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.emulator_commands import EmulatorOption

if TYPE_CHECKING:
    from domain.emulator_registry import InstalledEmulator

EXTERNAL_LAUNCHER_REASON = "external_launcher"
"""Why an external row is not bakeable yet: no argv for it exists in this phase."""


def external_option(install: InstalledEmulator) -> EmulatorOption:
    """The picker row for one detected install.

    ``emulator`` carries the definition id — the identity a firmware answer is keyed
    on — and not the label: two providers of one emulator are one emulator to the
    firmware question, and one row each to the picker.

    The command text is the binary followed by ``%ROM%``, stated in the same
    placeholder form the catalogue uses so a later launch phase can classify it
    rather than re-derive it. It is not bakeable today, and the reason says so.
    """
    return EmulatorOption(
        label=install.label,
        kind="standalone",
        core_so=None,
        command=f'"{install.path}" %ROM%',
        status="needs_setup",
        reason=EXTERNAL_LAUNCHER_REASON,
        emulator=install.id,
    )


def external_options(installs: list[InstalledEmulator], platform: str) -> list[EmulatorOption]:
    """Rows for every install that can play *platform*, one per distinct label.

    One per label because two builds of one emulator under one provider (an
    ``rpcs3.AppImage`` beside ``rpcs3.AppImage_old``) are one pick: the picker names
    which emulator under which provider, and choosing between builds is not a
    question this menu asks.
    """
    rows: list[EmulatorOption] = []
    seen: set[str] = set()
    for install in installs:
        if not install.plays(platform):
            continue
        if install.label in seen:
            continue
        seen.add(install.label)
        rows.append(external_option(install))
    return rows


def with_external(options: list[EmulatorOption], extra: list[EmulatorOption]) -> list[EmulatorOption]:
    """Append *extra* rows to *options*, skipping any label already offered.

    A label collision means ES-DE already lists that exact pick — advertising it
    twice would give the menu two entries that store one key, one of them disabled.
    The catalogue's row wins because it is the one that can be baked.
    """
    taken = {option.label for option in options}
    return [*options, *(row for row in extra if row.label not in taken)]
