"""Find the emulators actually installed on a Deck, by provider.

Three probes, one value: the AppImages in ``~/Applications``, the launcher scripts
EmuDeck ships in ``Emulation/tools/launchers``, and the flatpaks the system knows
about. Everything they find is identified through :mod:`domain.emulator_registry`
and returned as :class:`~domain.emulator_registry.InstalledEmulator` records, so a
picker can offer "PCSX2 (EmuDeck)" beside "PCSX2 (AppImage)" without knowing how
either was found.

Two design rules make this trustworthy rather than merely convenient.

**A missing directory is a fact, not an error.** A Deck without EmuDeck has no
launchers directory and a Deck whose user never installed a flatpak has no
``flatpak`` binary at all. Both are noted in :attr:`ScanResult.notes` and the scan
continues — an exception here would turn "you don't have EmuDeck" into "the plugin
is broken".

**Unclaimed files are reported, not dropped silently.** ``Freegosy.appimage`` and
``EmuDeck.AppImage`` are real files on the reference Deck that no emulator
definition claims; they come back in :attr:`ScanResult.unrecognised` so the UI can
say "found, not supported" instead of the user wondering why their emulator is
missing from the list.

The probes are injected (``Directories`` / ``list_flatpaks``) because the real ones
touch the filesystem and shell out, while every rule above is pure string work that
must be testable off a Deck.
"""

from __future__ import annotations

import os
import posixpath
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from domain.emulator_registry import (
    EmulatorDef,
    InstalledEmulator,
    Provider,
    dedupe,
    for_platform,
    identify,
    identify_flatpak,
    identify_launcher,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

APPIMAGE_SUFFIXES = (".appimage", ".appimage_old")

# How deep below ``~/Applications`` a binary install is looked for. EmuDeck drops
# ``Ryujinx`` under ``publish/`` and ``Vita3K`` under its own directory; nothing it
# ships nests deeper than that, and a deep walk would turn a scan into a filesystem
# crawl on a card.
NESTED_DEPTH = 2

# The flatpak ids whose *presence* is the installation itself rather than a
# catalogue entry: RetroDECK's emulator list still comes from atlas, which needs
# the frontend rather than the binaries.
RETRODECK_FLATPAK_ID = "net.retrodeck.retrodeck"

FLATPAK_TIMEOUT_SECONDS = 10.0


@dataclass(frozen=True, slots=True)
class Entry:
    """One directory entry, as the probe needs it.

    ``size`` and ``modified`` are what let :func:`dedupe` tell two copies of one
    build from two builds; ``None`` where the reader could not stat the entry.
    """

    name: str
    path: str
    is_dir: bool
    size: int | None = None
    modified: str | None = None
    executable: bool = True


class Directories(Protocol):
    """The one filesystem question this module asks."""

    def list(self, path: str) -> Sequence[Entry]:
        """Entries directly under *path*, or an empty sequence when it cannot be read."""
        ...


class FlatpakLister(Protocol):
    """The installed flatpaks, as ``(app_id, version)`` pairs."""

    def __call__(self) -> Sequence[tuple[str, str | None]]: ...


@dataclass(frozen=True, slots=True)
class ScanResult:
    """What one scan found, and everything it could not establish.

    ``installs`` is deduped and ordered; ``unrecognised`` names files that look
    like emulators but that no definition claims; ``notes`` carries the probe
    failures a log or a diagnostics pane should show rather than swallow.
    """

    installs: tuple[InstalledEmulator, ...] = ()
    unrecognised: tuple[str, ...] = ()
    retrodeck_present: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def for_platform(self, platform: str) -> tuple[InstalledEmulator, ...]:
        """The installs that can play *platform*, in stable order."""
        return tuple(for_platform(list(self.installs), platform))

    def labels_for_platform(self, platform: str) -> tuple[str, ...]:
        """The distinct provider-qualified pick labels available for *platform*."""
        return tuple(dict.fromkeys(install.label for install in self.for_platform(platform)))


def _looks_like_appimage(name: str) -> bool:
    return name.lower().endswith(APPIMAGE_SUFFIXES)


class EmulatorScanner:
    """Scan a Deck's provider surfaces into installed-emulator records."""

    def __init__(
        self,
        *,
        home: str,
        directories: Directories,
        list_flatpaks: FlatpakLister | None = None,
    ) -> None:
        self._home = home
        self._directories = directories
        self._list_flatpaks = list_flatpaks

    # ── public ──────────────────────────────────────────────────────────────

    def scan(self) -> ScanResult:
        """Run every probe and return the deduped result.

        Never raises for a missing directory or a failed ``flatpak`` call: both
        become notes. Only a bug in the registry would raise, and that is a test
        failure rather than a user-facing state.
        """
        notes: list[str] = []
        unrecognised: list[str] = []
        found: list[InstalledEmulator] = []

        found += self._scan_applications(notes, unrecognised)
        found += self._scan_launchers(notes)
        found += self._scan_flatpaks(notes)

        retrodeck = self._retrodeck_present()
        return ScanResult(
            installs=tuple(dedupe(found)),
            unrecognised=tuple(sorted(set(unrecognised))),
            retrodeck_present=retrodeck,
            notes=tuple(notes),
        )

    # ── probes ──────────────────────────────────────────────────────────────

    def _scan_applications(self, notes: list[str], unrecognised: list[str]) -> list[InstalledEmulator]:
        """AppImages at the top of ``~/Applications`` and binaries up to two levels down."""
        root = posixpath.join(self._home, "Applications")
        entries = self._directories.list(root)
        if not entries:
            notes.append(f"no entries under {root} (or it does not exist)")

        found: list[InstalledEmulator] = []
        for entry in entries:
            if entry.is_dir:
                found += self._scan_nested(entry.path, depth=NESTED_DEPTH - 1, notes=notes)
                continue
            if not entry.executable or not _looks_like_appimage(entry.name):
                continue
            definition = identify(entry.name)
            if definition is None:
                unrecognised.append(entry.path)
                continue
            found.append(self._install(definition, "native", entry))
        return found

    def _scan_nested(self, directory: str, *, depth: int, notes: list[str]) -> list[InstalledEmulator]:
        """Binaries inside one ``~/Applications`` subdirectory, e.g. ``publish/Ryujinx``.

        A directory that identifies as a binary layout is not descended into
        further: ``Vita3K/Vita3K`` is the install, and walking its contents would
        report the emulator's own bundled libraries as candidates.
        """
        found: list[InstalledEmulator] = []
        for entry in self._directories.list(directory):
            if entry.is_dir:
                if depth > 0:
                    found += self._scan_nested(entry.path, depth=depth - 1, notes=notes)
                continue
            if not entry.executable:
                continue
            definition = identify(entry.name)
            if definition is None:
                continue
            found.append(self._install(definition, "native", entry))
        return found

    def _scan_launchers(self, notes: list[str]) -> list[InstalledEmulator]:
        """EmuDeck's launcher scripts — the provider's own command surface."""
        root = posixpath.join(self._home, "Emulation", "tools", "launchers")
        entries = self._directories.list(root)
        if not entries:
            notes.append(f"no EmuDeck launchers under {root} (or EmuDeck is not installed)")

        found: list[InstalledEmulator] = []
        for entry in entries:
            if entry.is_dir or not entry.name.endswith(".sh"):
                continue
            definition = identify_launcher(entry.name)
            if definition is None:
                continue
            if definition.family == "retroarch":
                # EmuDeck's ``retroarch.sh`` launches the same flatpak (or native)
                # RetroArch the flatpak probe already reports. Counting it as a
                # second provider would offer one binary twice, under two labels
                # that write to the same save root.
                continue
            found.append(self._install(definition, "emudeck", entry))
        return found

    def _scan_flatpaks(self, notes: list[str]) -> list[InstalledEmulator]:
        """Installed flatpaks, identified by application id."""
        if self._list_flatpaks is None:
            return []
        try:
            flatpaks = self._list_flatpaks()
        except Exception as exc:  # a refused probe is a note, never a crash
            notes.append(f"flatpak list failed: {exc!r}")
            return []

        found: list[InstalledEmulator] = []
        for app_id, version in flatpaks:
            definition = identify_flatpak(app_id)
            if definition is None:
                continue
            found.append(
                InstalledEmulator(
                    definition=definition,
                    provider="flatpak",
                    path=app_id,
                    version_hint=version,
                )
            )
        return found

    def _retrodeck_present(self) -> bool:
        """Whether RetroDECK's flatpak is installed.

        Its emulators are not reported as installs: they are reached through the
        frontend (``flatpak run net.retrodeck.retrodeck -e …``) and their catalogue
        comes from atlas, so a per-binary record would name paths that exist only
        inside the sandbox.
        """
        if self._list_flatpaks is None:
            return False
        try:
            return any(app_id == RETRODECK_FLATPAK_ID for app_id, _ in self._list_flatpaks())
        except Exception:  # already noted by _scan_flatpaks
            return False

    # ── helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _install(definition: EmulatorDef, provider: Provider, entry: Entry) -> InstalledEmulator:
        """One record from an entry."""
        return InstalledEmulator(
            definition=definition,
            provider=provider,
            path=entry.path,
            size=entry.size,
            modified=entry.modified,
        )


class RealDirectories:
    """The ``Directories`` implementation that reads the actual filesystem."""

    def list(self, path: str) -> Sequence[Entry]:
        """Entries under *path*, or empty when it is unreadable.

        ``OSError`` — a missing directory, a permission refusal, a card yanked
        mid-scan — is the ordinary "not there" answer here, which is why it is not
        propagated: every caller of this module treats an empty listing as a probe
        that found nothing.
        """
        try:
            with os.scandir(path) as scan:
                return tuple(self._entry(item) for item in scan)
        except OSError:
            return ()

    @staticmethod
    def _entry(item: os.DirEntry[str]) -> Entry:
        """One scandir entry, stat'ed for the dedupe key, tolerant of failure."""
        size: int | None = None
        modified: str | None = None
        executable = False
        try:
            info = item.stat()
            size = info.st_size
            modified = f"{info.st_mtime_ns}"
            executable = bool(info.st_mode & 0o111)
        except OSError:
            pass
        return Entry(
            name=item.name,
            path=item.path,
            is_dir=item.is_dir(follow_symlinks=False),
            size=size,
            modified=modified,
            executable=executable,
        )


def flatpak_lister() -> list[tuple[str, str | None]]:
    """Ask the system for its installed flatpaks.

    ``flatpak list`` rather than the app stream metadata: this answers what is
    installed for *this* user, and its ``version`` column is the only honest
    freshness signal a flatpak offers. A missing binary or a non-zero exit raises,
    and the scanner turns that into a note.
    """
    binary = shutil.which("flatpak")
    if binary is None:
        raise FileNotFoundError("flatpak is not installed")
    result = subprocess.run(  # fixed argv, no shell, resolved binary
        [binary, "list", "--columns=application,version"],
        capture_output=True,
        text=True,
        timeout=FLATPAK_TIMEOUT_SECONDS,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"flatpak list exited {result.returncode}: {result.stderr.strip()[:200]}")
    rows: list[tuple[str, str | None]] = []
    for line in result.stdout.splitlines():
        app_id, _, version = line.partition("\t")
        if app_id.strip():
            rows.append((app_id.strip(), version.strip() or None))
    return rows


def scan_home(home: str) -> ScanResult:
    """Scan *home* with the real probes — the call a service makes."""
    return EmulatorScanner(
        home=home,
        directories=RealDirectories(),
        list_flatpaks=flatpak_lister,
    ).scan()
