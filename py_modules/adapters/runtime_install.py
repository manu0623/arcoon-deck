"""Detecting and installing the owned libretro runtime (the RetroArch Flatpak).

Installedness is a directory probe over the two trees ``flatpak`` itself searches — the
per-user one first, because ``flatpak run`` puts it first and so does the owned runner's
cores path. Installing is a subprocess with a bounded timeout; every failure comes back as
``{"ok": False, "reason": …}`` so a caller can say what happened instead of raising into a
callable the frontend awaits.
"""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from domain.runtime_install import LIBRETRO_RUNTIME_APP_ID, install_command

if TYPE_CHECKING:
    import logging

#: A flatpak install downloads the app plus its runtime; measured at roughly a minute on the
#: reference Deck, so the bound is generous but finite.
_INSTALL_TIMEOUT_SECONDS = 900


class RuntimeInstallAdapter:
    """Answer whether the owned runtime is installed, and install it when it is not."""

    def __init__(
        self,
        *,
        user_home: str,
        logger: logging.Logger,
        app_id: str = LIBRETRO_RUNTIME_APP_ID,
    ) -> None:
        self._user_home = user_home
        self._logger = logger
        self._app_id = app_id

    @property
    def app_id(self) -> str:
        return self._app_id

    def installed(self) -> bool:
        """Whether *app_id* is installed in either flatpak tree."""
        return any(
            os.path.isdir(os.path.join(root, "flatpak", "app", self._app_id))
            for root in ("/var/lib", os.path.join(self._user_home, ".local", "share"))
        )

    def install(self) -> dict[str, object]:
        """Install the runtime for the current user; report rather than raise.

        The probe is repeated after the command because ``flatpak install`` exits non-zero
        for reasons that are not failures in practice (an already-installed app refuses the
        transaction), and what the caller cares about is the resulting state, not the exit
        code.
        """
        if self.installed():
            return {"app_id": self._app_id, "ok": True, "already_present": True}
        argv = install_command(self._app_id)
        self._logger.info(f"runtime_install: installing {self._app_id}: {' '.join(argv)}")
        try:
            completed = subprocess.run(
                list(argv),
                capture_output=True,
                text=True,
                timeout=_INSTALL_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._logger.warning(f"runtime_install: {self._app_id} could not be installed: {exc}")
            return {"app_id": self._app_id, "ok": False, "reason": str(exc)}
        if self.installed():
            self._logger.info(f"runtime_install: installed {self._app_id}")
            return {"app_id": self._app_id, "ok": True, "already_present": False}
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        reason = detail[-1] if detail else f"flatpak exited {completed.returncode}"
        self._logger.warning(f"runtime_install: {self._app_id} not installed after the command: {reason}")
        return {"app_id": self._app_id, "ok": False, "reason": reason}
