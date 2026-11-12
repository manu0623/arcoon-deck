"""Finding a RetroArch the plugin can start itself, and the cores it can see.

The owned path needs two facts per launch, and both come from the filesystem rather
than from RetroDECK: which command starts RetroArch, and which directory that
particular RetroArch loads cores from. A flatpak install keeps its cores under
``~/.var/app/<id>/config/retroarch/cores`` — not the sandbox path RetroDECK uses, which
does not exist on the host at all — so the cores directory is chosen together with the
command prefix, never separately.

Candidates are tried in order and the first one that actually holds the requested core
wins. Holding the core is the test, not "is installed": a RetroArch with an empty or
relocated cores directory would start and then fail on ``-L``, and the user would see a
launch that does nothing rather than a game that plays. When no candidate holds the
core this returns ``None`` and the caller keeps the RetroDECK launch it had before —
the degradation costs the ownership, never the launch.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from domain.retroarch_runner import RetroArchRunner

if TYPE_CHECKING:
    import logging

FLATPAK_APP_ID = "org.libretro.RetroArch"

# Where a flatpak keeps per-app data; RetroArch's own config and cores live under it.
_FLATPAK_CORES = os.path.join("config", "retroarch", "cores")
# A distro/EmuDeck install keeps the same layout in the user's config dir.
_NATIVE_CORES = os.path.join(".config", "retroarch", "cores")
_NATIVE_BINARY = "/usr/bin/retroarch"


class RetroArchRunnerAdapter:
    """Resolve the RetroArch to start directly, per requested core."""

    def __init__(self, *, user_home: str, logger: logging.Logger) -> None:
        self._user_home = user_home
        self._logger = logger

    def __call__(self, core_so: str) -> RetroArchRunner | None:
        """A runner holding *core_so*, or ``None`` when no candidate can start it.

        Called per launch rather than cached: the answer is two ``isdir``/``isfile``
        stats, and caching it would mean a user who installs RetroArch (or adds a
        core) mid-session stays on the fallback path until the plugin restarts.
        """
        for runner in self._candidates():
            if os.path.isfile(os.path.join(runner.cores_dir, f"{core_so}.so")):
                return runner
        self._logger.info(f"retroarch_runner: no owned RetroArch holds {core_so}; keeping the RetroDECK launch")
        return None

    def _candidates(self) -> list[RetroArchRunner]:
        """The RetroArch installs to try, most likely first.

        The flatpak comes first because it is what a Deck almost always has, and
        because its prefix needs no executable path to be guessed.
        """
        candidates = [
            RetroArchRunner(
                prefix=f"flatpak run {FLATPAK_APP_ID}",
                cores_dir=os.path.join(self._user_home, ".var", "app", FLATPAK_APP_ID, _FLATPAK_CORES),
                label="RetroArch (Flatpak)",
            ),
            RetroArchRunner(
                prefix=_NATIVE_BINARY,
                cores_dir=os.path.join(self._user_home, _NATIVE_CORES),
                label="RetroArch (system)",
            ),
        ]
        # A cores directory that does not exist cannot hold anything, and checking it
        # here keeps a missing install out of the log as "no core" when it is really
        # "no RetroArch".
        return [candidate for candidate in candidates if os.path.isdir(candidate.cores_dir)]
