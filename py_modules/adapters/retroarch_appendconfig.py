"""Writes the per-platform RetroArch appendconfig into the plugin's data directory.

:mod:`domain.retroarch_appendconfig` decides what the file says; this adapter decides
that it exists and is current. Two properties matter more than speed:

**Idempotent.** The text is compared before writing, so a launch that changes nothing
does not touch the file. That keeps the file's mtime meaningful — a timestamp that
moves on every launch would say the intent changed when it did not — and avoids
rewriting a file another process (a second ROM launching concurrently) is reading.

**The directories are created, and that is not cosmetic.** Measured on a Deck:
RetroArch reads ``savefile_directory`` from the appendconfig, finds that the directory
does not exist, and **silently falls back to its own default** — the log then says
``Redirecting save file to ~/.var/app/…/saves/…`` while our config said otherwise,
with no error anywhere. Creating the week-one directory is therefore part of the
contract: redirect a platform whose bank directory is missing and every save it makes
lands somewhere the plugin never reads, which is indistinguishable from a sync bug for
as long as it takes someone to read the log.

**The user's own config can still win, and is repaired.** RetroArch saves its config on
exit, so a redirected launch bakes the save directory it was handed into
``retroarch.cfg``. Measured on a Deck, that baked value then beats the next launch's
``--appendconfig`` (a PPSSPP launch appended ``…/saves/psp`` and still resolved
``…/saves/psp/PSP/SAVEDATA``), which silently sends the core to the wrong tree. Every
launch therefore restores the two path keys to ``default`` when they point inside the
plugin's own data directory, and leaves any other value alone.

**Never fatal.** A save root is a nice-to-have at bake time and a hard requirement at
sync time. If the directories cannot be created, this returns ``None`` and logs, and
the caller bakes the launch without an appendconfig: the game still starts against the
user's own RetroArch config. Raising here would turn "the plugin's data directory is
read-only" into "this game will not launch", which is a worse trade than a save that
lands in the old place and shows up as drift.

One file per platform, because each states its own save directory; see
:func:`domain.retroarch_appendconfig.appendconfig_name`.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from domain.retroarch_appendconfig import appendconfig_dirs, appendconfig_name, render_appendconfig
from domain.save_bank import canonical_platform, layout_for

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

# Sits beside the bank: the generated configs are part of the same intent, and a user
# debugging "where do my saves go" can read both from one place.
APPENDCONFIG_DIR_NAME = "retroarch"


class RetroArchAppendConfigAdapter:
    """Generates and maintains the appendconfig files under one data directory."""

    def __init__(
        self,
        *,
        data_dir: str,
        logger: logging.Logger,
        enabled: Callable[[], object] | None = None,
        repair_config: Callable[[], object] | None = None,
    ) -> None:
        self._data_dir = data_dir
        self._logger = logger
        # Repairs the value a previous launch baked into RetroArch's own config (see
        # ``unbake_replayed_paths``); it belongs to the adapter that knows every config
        # path this machine may hold. ``None`` means a caller with no RetroArch to
        # repair, which only ever skips the repair.
        self._repair_config = repair_config
        # The same switch the save lookup reads (``save_bank``). ``None`` means "always"
        # for a caller that has no settings to consult, but the composition root passes
        # the live setting: a redirect the lookup does not follow is a save that vanishes.
        self._enabled = enabled

    def path_for(self, platform: str) -> str:
        """Where *platform*'s generated config lives, whether or not it exists yet."""
        return os.path.join(
            self._data_dir,
            APPENDCONFIG_DIR_NAME,
            appendconfig_name(canonical_platform(platform)),
        )

    def render_for(self, platform: str, *, system_dir: str | None = None) -> str:
        """The text *platform*'s config should hold, without writing anything."""
        layout = layout_for(platform)
        save_dir, state_dir = appendconfig_dirs(
            data_dir=self._data_dir, layout_subdir=layout.subdir, core_subdir=layout.core_subdir
        )
        return render_appendconfig(save_dir=save_dir, state_dir=state_dir, system_dir=system_dir)

    def ensure(self, platform: str, *, system_dir: str | None = None) -> str | None:
        """Make sure *platform*'s config exists and is current; return its path.

        ``None`` means "bake without it": the data directory could not be written, or
        the platform's own directory names cannot be represented in a config value.
        Both are logged with the reason, because a save landing outside the bank is
        the kind of thing that is only ever explained afterwards.
        """
        if self._enabled is not None and not self._enabled():
            return None
        path = self.path_for(platform)
        try:
            text = self.render_for(platform, system_dir=system_dir)
        except ValueError as exc:
            self._logger.warning(f"Cannot generate RetroArch appendconfig for {platform}: {exc}")
            return None
        try:
            # Both directories first: RetroArch ignores a savefile_directory that does
            # not exist and writes to its own default instead, without an error.
            self._make_save_dirs(platform)
            self._repair_retroarch_config()
            existing = self._read(path)
            if existing == text:
                return path
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        except OSError as exc:
            self._logger.warning(f"Cannot write RetroArch appendconfig at {path}: {exc}")
            return None
        return path

    def _repair_retroarch_config(self) -> None:
        """Undo a save directory an earlier launch baked into RetroArch's own config.

        RetroArch saves its config on exit and that saved value beats the appendconfig
        (measured, see this module's docstring), so one redirected launch would
        otherwise pin this platform's directory for every later one. The repair itself
        lives in :meth:`adapters.retroarch_config.RetroArchConfigAdapter.restore_bank_paths`
        because it knows every ``retroarch.cfg`` this machine may hold, and the launched
        installation's is not always the first one found.

        Failure is logged and ignored: a launch that cannot repair the config still
        plays the game, and the worst case is the drift this method exists to remove.
        """
        if self._repair_config is None:
            return
        try:
            self._repair_config()
        except Exception as exc:
            self._logger.warning(f"Cannot repair the RetroArch config: {exc}")

    def _make_save_dirs(self, platform: str) -> None:
        """Create the save and state directories this platform's config states.

        Raises ``OSError`` to the caller rather than swallowing it, because a config
        written for a directory that does not exist is worse than no config: it looks
        like the redirect is in place while RetroArch quietly writes elsewhere.
        """
        layout = layout_for(platform)
        save_dir, state_dir = appendconfig_dirs(
            data_dir=self._data_dir, layout_subdir=layout.subdir, core_subdir=layout.core_subdir
        )
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(state_dir, exist_ok=True)

    @staticmethod
    def _read(path: str) -> str | None:
        """The current text, or ``None`` when the file is absent or unreadable.

        An unreadable file is treated as absent rather than as an error: the next
        write repairs it, which is better than refusing to redirect saves because a
        stale file could not be read first.

        ``UnicodeDecodeError`` is caught as well as ``OSError`` — it is not one, and a
        half-written or truncated file from a power loss would otherwise escape this
        whole adapter and fail the launch it was supposed to improve.
        """
        try:
            with open(path, encoding="utf-8") as handle:
                return handle.read()
        except (OSError, UnicodeDecodeError):
            return None
