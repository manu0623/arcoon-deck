"""Reads the `layout.json` contract the provisioner wrote, or answers that there is none.

The parsing rules live in :mod:`domain.layout_manifest` and are tested there; this adapter
owns only the part that touches the disk: find the file under the plugin's data directory,
read it, and re-read it when it changes.

**A missing or unreadable file is not an error.** Every branch that cannot produce a
manifest answers ``None``, which callers treat as "this platform is unmanaged" and hand
back to the behaviour that already works (ADR-0034). A provisioner that has not run yet is
indistinguishable from one this plugin has never heard of.

Re-reading is keyed on ``(mtime, size)`` rather than done per call: a sync asks about a
platform more than once per operation, and a provisioner rewrites the file rarely. The key
is compared, never cached by elapsed time, so a file replaced within the same second still
reloads.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from domain.layout_manifest import MANIFEST_FILENAME, LayoutManifest, ManagedPlatform, parse_layout_manifest

if TYPE_CHECKING:
    import logging


class LayoutManifestAdapter:
    """The plugin's own implementation of the layout-manifest seam."""

    def __init__(self, *, data_dir: str, logger: logging.Logger) -> None:
        self._path = os.path.join(data_dir, MANIFEST_FILENAME)
        self._logger = logger
        self._key: tuple[int, int] | None = None
        self._manifest: LayoutManifest | None = None
        self._reported_missing = False

    def entry_for(self, platform_slug: str | None) -> ManagedPlatform | None:
        """The managed entry for *platform_slug*, or ``None`` when it is not managed."""
        self._reload_if_changed()
        return self._manifest.entry_for(platform_slug) if self._manifest is not None else None

    def _reload_if_changed(self) -> None:
        try:
            stat = os.stat(self._path)
        except OSError:
            if not self._reported_missing:
                self._logger.info(f"layout manifest: none at {self._path}; every platform is unmanaged")
                self._reported_missing = True
            self._key, self._manifest = None, None
            return
        key = (stat.st_mtime_ns, stat.st_size)
        if key == self._key:
            return
        try:
            with open(self._path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            self._logger.warning(f"layout manifest: cannot read {self._path}: {exc}")
            self._key, self._manifest = key, None
            return
        manifest = parse_layout_manifest(text)
        if manifest is None:
            # A file that cannot be trusted leaves every platform on today's behaviour. That
            # is the degradation ADR-0034 promises, and it is loud rather than silent.
            self._logger.warning(f"layout manifest: {self._path} is not usable; every platform is unmanaged")
            self._key, self._manifest = key, None
            return
        self._logger.info(
            f"layout manifest: {self._path} manages {', '.join(entry.platform for entry in manifest.platforms)}"
        )
        self._key, self._manifest = key, manifest
        self._reported_missing = False
