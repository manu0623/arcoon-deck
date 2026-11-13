"""Installing the runtime the plugin drives, from data the plugin owns.

Cores were the first half of "the app stands alone" (ADR-0037); this is the other half. A
core is useless without a program to load it, and the owned launch path starts RetroArch
itself — so on a Deck with no RetroDECK and no RetroArch, nothing launches no matter how
many cores are on disk. Both are the plugin's to install.

The runtime is the RetroArch Flatpak, installed **per user**: that needs no password, runs
inside the user's session the way Steam's shortcuts do, and lands in the same tree the
owned runner already probes (``~/.var/app/<id>/config/retroarch/cores``). A system-wide
install would be the same program under a root prompt the user cannot approve from Game
Mode, which is the one thing an unattended install must never need.

This module is pure: it states the command. Running it, and knowing whether the app is
already there, is the adapter's job.
"""

from __future__ import annotations

#: The Flatpak the owned launch path starts (``domain.retroarch_runner``).
LIBRETRO_RUNTIME_APP_ID = "org.libretro.RetroArch"

#: The remote a fresh Deck has configured for the user installation; measured on the
#: reference Deck, where ``flatpak remotes`` lists ``flathub`` for both installations.
FLATHUB_REMOTE = "flathub"


def install_command(app_id: str = LIBRETRO_RUNTIME_APP_ID, *, remote: str = FLATHUB_REMOTE) -> tuple[str, ...]:
    """The argv that installs *app_id* for the current user, unattended.

    ``--user`` is the whole point (see the module docstring); ``-y`` answers the one prompt
    an unattended install cannot, and installs the app's runtime dependencies with it, so a
    first run cannot land half-installed.
    """
    return ("flatpak", "install", "--user", "-y", remote, app_id)
