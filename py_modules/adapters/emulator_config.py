"""Reads an installed emulator's own settings file into a flat value dict.

The save-root resolver asks one question — *where does this emulator write saves?* —
and the emulator's configuration is the authority that answers it. This adapter
locates that file for a **specific install** and hands the values over parsed.

**The provider decides the roots.** The same emulator keeps its settings in a
different place depending on who installed it, and the paths are not
interchangeable:

* ``flatpak`` — the install path *is* the application id, so its settings sit at
  ``~/.var/app/<id>/config/<app dir>`` and its data at ``~/.var/app/<id>/data/<app dir>``.
* ``retrodeck`` — every component shares RetroDECK's sandbox, so the id is
  RetroDECK's own and the app dir names the component
  (verified: ``~/.var/app/net.retrodeck.retrodeck/config/PCSX2/inis/PCSX2.ini``).
* ``native`` — XDG: ``~/.config/<app dir>`` and ``~/.local/share/<app dir>``.
* ``emudeck`` — **both of the above**, because EmuDeck installs some emulators as
  AppImages that use XDG (its PCSX2 writes ``~/.config/PCSX2``, verified) and others
  as flatpaks launched from a script (its Dolphin is ``org.DolphinEmu.dolphin-emu``).
  Rather than guess, the flatpak root is tried first — but only when the definition
  declares a flatpak id — and the first settings file that exists answers.

**Portable mode wins where it exists.** An AppImage run from a folder with its own
settings beside it reads that file, not the XDG one. The portable path is a candidate
like any other; if no file is there, it is simply not chosen.

**No file, no values.** A missing settings file yields an empty dict plus the reason,
because the resolver's next step — the emulator's declared default — is only honest
if "nothing was configured" and "nothing could be read" stay distinguishable.

I/O lives here, parsing lives in :mod:`domain.emulator_config`; both seams
(``read_text``, ``exists``) are injectable so tests need no filesystem.
"""

from __future__ import annotations

import os
import posixpath
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from domain.emulator_config import ConfigFormat, is_readable, layout_for, parse_config

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.emulator_registry import InstalledEmulator

# RetroDECK runs every component inside its own sandbox, so the application id is
# RetroDECK's regardless of which emulator's settings are being read.
RETRODECK_FLATPAK_ID = "net.retrodeck.retrodeck"

# A settings file larger than this is not a settings file; refusing to load it keeps
# a mistaken path from reading a multi-gigabyte image into memory.
MAX_CONFIG_BYTES = 4 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ConfigRoots:
    """The two XDG roots an emulator's layout is expressed against.

    Both are always present: a rule may state ``{config}/memcards`` (PCSX2 keeps cards
    beside its settings) or ``{data}/GC`` (Dolphin keeps cards in its data tree), and
    the resolver must not have to know which root it is being handed.
    """

    config: str
    data: str

    def root_for(self, *, in_data_dir: bool) -> str:
        """The root a layout's ``filename`` is relative to."""
        return self.data if in_data_dir else self.config


@dataclass(frozen=True, slots=True)
class ConfigRead:
    """What was read for one install, and what happened when nothing was.

    ``path`` is the file that answered — carried so a log or a settings row can name
    it, and so ``roots`` can be trusted to belong to the same provider variant.
    ``note`` is ``None`` on success and a short reason otherwise (``no-layout``,
    ``format-unreadable``, ``no-settings-file``, ``unreadable: …``).
    """

    emulator: str
    provider: str
    values: dict[str, str] = field(default_factory=dict)
    path: str | None = None
    fmt: ConfigFormat | None = None
    note: str | None = None
    roots: ConfigRoots | None = None

    @property
    def found(self) -> bool:
        """Whether a settings file was read (an empty-read file still counts)."""
        return self.path is not None


def _read_text_file(path: str) -> str:
    """Read a settings file as UTF-8 text, refusing oversized files."""
    if os.path.getsize(path) > MAX_CONFIG_BYTES:
        raise OSError(f"{path} is larger than {MAX_CONFIG_BYTES} bytes")
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


class EmulatorConfigReader:
    """Locates and parses one installed emulator's settings file."""

    def __init__(
        self,
        *,
        user_home: str,
        read_text: Callable[[str], str] | None = None,
        exists: Callable[[str], bool] | None = None,
    ) -> None:
        self._user_home = user_home
        self._read_text = read_text or _read_text_file
        self._exists = exists or os.path.isfile

    def _flatpak_roots(self, app_id: str, app_dir: str) -> ConfigRoots:
        base = posixpath.join(self._user_home, ".var", "app", app_id)
        return ConfigRoots(
            config=posixpath.join(base, "config", app_dir),
            data=posixpath.join(base, "data", app_dir),
        )

    def _xdg_roots(self, app_dir: str) -> ConfigRoots:
        return ConfigRoots(
            config=posixpath.join(self._user_home, ".config", app_dir),
            data=posixpath.join(self._user_home, ".local", "share", app_dir),
        )

    def root_variants(self, install: InstalledEmulator, *, app_dir: str) -> tuple[ConfigRoots, ...]:
        """Every root pair this install's settings could live under, in probe order.

        EmuDeck appears twice because it installs both kinds; every other provider has
        exactly one answer, and a provider that claims one while the file is in the
        other would report "not configured" for a configured emulator.
        """
        provider = install.provider
        if provider == "flatpak":
            return (self._flatpak_roots(install.path.strip(), app_dir),)
        if provider == "retrodeck":
            return (self._flatpak_roots(RETRODECK_FLATPAK_ID, app_dir),)
        if provider == "emudeck":
            flatpak_id = install.definition.hints.flatpak_ids
            if flatpak_id:
                return (
                    self._flatpak_roots(flatpak_id[0], app_dir),
                    self._xdg_roots(app_dir),
                )
        return (self._xdg_roots(app_dir),)

    def candidates(self, install: InstalledEmulator) -> tuple[tuple[str, ConfigRoots], ...]:
        """Every ``(path, roots)`` pair worth probing, portable settings first.

        The portable pair carries the XDG roots because a portable settings file still
        means the emulator is a native install — a rule's ``{data}`` must not point
        into a flatpak sandbox that is not in play.

        Portable probing is limited to ``native`` installs that are not a shell
        script. EmuDeck's launchers are ``.sh`` files whose directory holds no
        settings, so probing beside one would look for ``launchers/inis/PCSX2.ini`` —
        a path that cannot be a portable install, only a wasted stat.
        """
        layout = layout_for(install.id)
        if layout is None:
            return ()
        pairs: list[tuple[str, ConfigRoots]] = []
        is_portable_candidate = install.provider == "native" and posixpath.isabs(install.path)
        if is_portable_candidate and not install.path.endswith(".sh"):
            portable_roots = self._xdg_roots(layout.app_dir)
            pairs.append((posixpath.join(posixpath.dirname(install.path), layout.filename), portable_roots))
        pairs.extend(
            (posixpath.join(roots.root_for(in_data_dir=layout.in_data_dir), layout.filename), roots)
            for roots in self.root_variants(install, app_dir=layout.app_dir)
        )
        return tuple(pairs)

    def read(self, install: InstalledEmulator) -> ConfigRead:
        """Read the first settings file that exists, parsed by its declared format.

        An unparsed format (YAML) stops before any file is opened: reading it would
        yield an empty dict that looks like an empty file, and the note is the only
        thing that tells those apart afterwards.
        """
        layout = layout_for(install.id)
        emulator, provider = install.id, install.provider
        if layout is None:
            return ConfigRead(emulator=emulator, provider=provider, note="no-layout")
        if not is_readable(layout.fmt):
            return ConfigRead(emulator=emulator, provider=provider, fmt=layout.fmt, note="format-unreadable")

        for path, roots in self.candidates(install):
            if not self._exists(path):
                continue
            try:
                text = self._read_text(path)
            except OSError as exc:
                return ConfigRead(
                    emulator=emulator,
                    provider=provider,
                    path=path,
                    fmt=layout.fmt,
                    note=f"unreadable: {exc}",
                    roots=roots,
                )
            return ConfigRead(
                emulator=emulator,
                provider=provider,
                values=parse_config(layout.fmt, text),
                path=path,
                fmt=layout.fmt,
                roots=roots,
            )
        return ConfigRead(emulator=emulator, provider=provider, fmt=layout.fmt, note="no-settings-file")

    def values_for(self, install: InstalledEmulator) -> tuple[dict[str, str], ConfigRoots | None, str | None]:
        """``(values, roots, note)`` — the shape a caller feeding
        :func:`domain.save_locations.resolve` needs.

        Roots are ``None`` when no file answered; the caller then has no configured
        path to expand and falls back to a declared default.
        """
        read = self.read(install)
        return read.values, read.roots if read.found else None, read.note
