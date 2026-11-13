"""Downloading a libretro core into the runtime's own cores directory.

The decision rules live in :mod:`domain.core_provision`; this adapter is the network and
the disk. Two things it owns that the domain cannot:

- **A refusal to guess where cores go.** The runtime's cores directory comes from
  ``domain.runtime``, and it is empty while RetroDECK drives — its cores live inside its own
  flatpak. Downloading into ``""`` would scatter ``.so`` files relative to the working
  directory, so an empty answer is a refusal, not a path.
- **An atomic write.** The core is written to ``<name>.so.part`` in the same directory and
  ``os.replace``d into place, so a transfer that dies mid-write leaves no half file that
  RetroArch would try to load, and a partial retry cannot shadow a working core.
"""

from __future__ import annotations

import contextlib
import os
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

from domain.core_provision import BUILDBOT_NIGHTLY, core_url, verify_core_archive

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

USER_AGENT = "arcoon-deck core-provisioning"
_TIMEOUT_SECONDS = 120
#: A core is a few megabytes; this cap only exists so a mis-served URL cannot fill memory.
_MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024


class CoreInstallAdapter:
    """Fetch and install one core, synchronously (services offload to an executor)."""

    def __init__(
        self,
        *,
        cores_dir: Callable[[], str],
        logger: logging.Logger,
        base_url: str = BUILDBOT_NIGHTLY,
    ) -> None:
        self._cores_dir = cores_dir
        self._logger = logger
        self._base_url = base_url

    def install(self, core_so: str) -> dict[str, object]:
        """Download, verify and install *core_so*; report rather than raise.

        Every failure — no cores directory, a network error, a refused archive, a write
        failure — comes back as ``{"ok": False, "reason": …}`` so a caller installing
        several cores can report the ones that worked and say why the others did not.
        """
        directory = self._cores_dir()
        if not directory:
            return {"core": core_so, "ok": False, "reason": "no_cores_dir"}
        url = core_url(core_so, base=self._base_url)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
                data = response.read(_MAX_DOWNLOAD_BYTES)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            self._logger.warning(f"core_install: {core_so} download failed from {url}: {exc}")
            return {"core": core_so, "ok": False, "reason": f"download_failed: {exc}"}
        verdict = verify_core_archive(data, core_so=core_so)
        if not verdict.ok or verdict.member is None:
            self._logger.warning(f"core_install: {core_so} refused from {url}: {verdict.reason}")
            return {"core": core_so, "ok": False, "reason": verdict.reason or "unverified"}
        target = os.path.join(directory, f"{core_so}.so")
        partial = f"{target}.part"
        try:
            os.makedirs(directory, exist_ok=True)
            with open(partial, "wb") as handle:
                handle.write(verdict.member)
            os.replace(partial, target)
        except OSError as exc:
            self._logger.warning(f"core_install: {core_so} could not be written to {directory}: {exc}")
            with contextlib.suppress(OSError):
                os.remove(partial)
            return {"core": core_so, "ok": False, "reason": f"write_failed: {exc}"}
        self._logger.info(f"core_install: installed {core_so} ({verdict.size} bytes) into {directory}")
        return {"core": core_so, "ok": True, "bytes": verdict.size, "path": target}
