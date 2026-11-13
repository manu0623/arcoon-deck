"""Where a standalone emulator comes from, stated as a plan the plugin can act on.

The inventory says which emulators a platform offers and how to launch them; this module
answers the question in front of that one — *can this machine get it, and from where?* —
without touching the network, running a command, or knowing what a filesystem is.

Two sources, and the difference between them is the point:

- **A flatpak remote** hands over a signed build that the store keeps current. Installing
  is one argv (``domain.runtime_install``: per user, unattended), and updating it is
  ``flatpak update``.
- **The project's own GitHub release** hands over an AppImage: the newest Linux build the
  project publishes, with no packager in between deciding when it arrives. It is also the
  only channel some of these emulators have — Eden, Citron and DuckStation are not on
  Flathub at all.

``prefer_newest`` states the choice a device makes when a row has both: the release wins,
because a store's copy is only as current as its last manifest bump. Ordering is a
parameter rather than a constant so a caller can ask for the store build deliberately.

Nothing here verifies a download. :func:`matching_asset` is the rule that keeps an
ambiguity from becoming an install — a release attaching both an x86_64 and an arm64
build is not a choice this module may make — and the hash of whatever is fetched is the
adapter's to check before it writes.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.runtime_install import FLATHUB_REMOTE, install_command

if TYPE_CHECKING:
    from collections.abc import Iterable

    from domain.owned_inventory import InventoryEmulator


@dataclass(frozen=True)
class FlatpakInstall:
    """Installed from a flatpak remote, per user, with no password prompt."""

    app_id: str
    remote: str = FLATHUB_REMOTE

    @property
    def argv(self) -> tuple[str, ...]:
        """The command that installs it (``--user -y``, see the runtime's own rule)."""
        return install_command(self.app_id, remote=self.remote)


@dataclass(frozen=True)
class ReleaseInstall:
    """Installed from the project's GitHub release, as the one AppImage it attaches.

    The release is asked for by API rather than guessed from a tag: tag spellings differ
    between projects (``v1.20.4``, ``nightly-linux``, a bare commit hash), and a URL built
    from a wrong tag is a 404 that looks like a network failure.
    """

    repo: str
    asset_pattern: str

    @property
    def release_api(self) -> str:
        """The endpoint that answers the newest tag and its asset names."""
        return f"https://api.github.com/repos/{self.repo}/releases/latest"


InstallPlan = FlatpakInstall | ReleaseInstall


def install_plan(emulator: InventoryEmulator, *, prefer_newest: bool = True) -> InstallPlan | None:
    """How to obtain *emulator*, or ``None`` when the inventory states no source.

    ``None`` is a real answer and not a failure: a libretro core is installed by the core
    provisioner, not here, and a standalone row with no ``install`` block is an emulator
    the user installs themselves — the picker already shows it as ``needs_setup``.
    """
    install = getattr(emulator, "install", None)
    if install is None or emulator.kind != "standalone":
        return None
    flatpak = FlatpakInstall(install.flatpak) if install.flatpak else None
    github = install.github
    release = ReleaseInstall(github.repo, github.asset) if github is not None else None
    return (release or flatpak) if prefer_newest else (flatpak or release)


def matching_asset(names: Iterable[str], pattern: str) -> str | None:
    """The single asset *pattern* names, or ``None``.

    Exactly one, deliberately. A release that attaches an x86_64 build beside an arm64
    one, or a ``v3`` variant for newer CPUs, is ambiguous: taking the first name would
    install a binary this machine may not run, and the failure would look like a broken
    emulator rather than a wrong download.
    """
    matches = [name for name in names if fnmatch.fnmatchcase(name, pattern)]
    return matches[0] if len(matches) == 1 else None


def download_url(repo: str, tag: str, asset: str) -> str:
    """The direct URL for one asset of one release."""
    return f"https://github.com/{repo}/releases/download/{tag}/{asset}"
