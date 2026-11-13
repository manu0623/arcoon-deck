"""Installing a standalone emulator from the source its inventory row states.

Two paths, and both end with the file the picker already probes:

- **A store build** is ``flatpak install --user -y`` — the same unattended, per-user
  command the runtime's own installer runs. Nothing is written by this plugin, and the
  store's signatures are the verification.
- **A release build** is the project's own AppImage, and it is *verified before it is
  written*: the hash comes from the release metadata (``digest: "sha256:…"``), the
  download is streamed into ``<target>.part`` while being hashed, and a mismatch removes
  the partial and leaves whatever was installed alone. An asset with no digest is refused
  rather than trusted, because a binary that launches games is not something to run on
  TLS alone.

The file name is the row's own first ``~/Applications/*.AppImage`` candidate, never the
asset's name: assets are versioned (``PPSSPP-v1.20.4-…AppImage``), and installing under it
would make the emulator undetectable the moment it landed. That is also why re-running an
install is cheap — an existing target whose hash already matches the release is reported
``already_present`` without downloading anything.

Every failure comes back as ``{"ok": False, "reason": …}`` so a caller installing several
emulators reports the ones that worked and says why the others did not.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import stat
import subprocess
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

from domain.emulator_install import (
    FlatpakInstall,
    ReleaseInstall,
    appimage_path,
    digest_from_asset,
    download_url,
    install_plan,
    matching_asset,
)

if TYPE_CHECKING:
    import logging
    from collections.abc import Iterable

    from domain.owned_inventory import InventoryEmulator

USER_AGENT = "arcoon-deck emulator-provisioning"
#: A release download is an emulator binary: a few hundred megabytes at most, and this cap
#: only exists so a mis-served URL cannot fill the disk behind the caller's back.
_MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024
_DOWNLOAD_TIMEOUT_SECONDS = 300
_RELEASE_TIMEOUT_SECONDS = 30
#: A flatpak install fetches the app plus its runtime; the runtime's own installer allows
#: fifteen minutes for the same work, and an emulator pulls the same freedesktop runtime.
_FLATPAK_TIMEOUT_SECONDS = 900
_CHUNK = 1024 * 1024


class EmulatorInstallAdapter:
    """Fetch and install one standalone emulator, synchronously.

    Services call this from an executor: both paths block for as long as a download does.
    """

    def __init__(self, *, user_home: str, logger: logging.Logger, system_flatpak_root: str = "/var/lib") -> None:
        self._user_home = user_home
        self._logger = logger
        self._system_flatpak_root = system_flatpak_root

    def install(self, emulator: InventoryEmulator) -> dict[str, object]:
        """Obtain *emulator* from its stated source, or say why it could not be."""
        plan = install_plan(emulator)
        if plan is None:
            return self._failure(emulator, "no_source")
        if isinstance(plan, FlatpakInstall):
            return self._install_flatpak(emulator, plan)
        return self._install_release(emulator, plan)

    # -- a store build ------------------------------------------------------

    def _install_flatpak(self, emulator: InventoryEmulator, plan: FlatpakInstall) -> dict[str, object]:
        if self._flatpak_app_installed(plan.app_id):
            return {"label": emulator.label, "ok": True, "already_present": True, "app_id": plan.app_id}
        argv = plan.argv
        self._logger.info(f"emulator_install: installing {plan.app_id}: {' '.join(argv)}")
        try:
            completed = subprocess.run(
                list(argv),
                capture_output=True,
                text=True,
                timeout=_FLATPAK_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._logger.warning(f"emulator_install: {plan.app_id} could not be installed: {exc}")
            return self._failure(emulator, f"install_failed: {exc}", app_id=plan.app_id)
        # The probe decides, not the exit code: ``flatpak install`` exits non-zero for a
        # transaction it refused because the app is already there, and what the caller
        # cares about is the resulting state.
        if self._flatpak_app_installed(plan.app_id):
            self._logger.info(f"emulator_install: installed {plan.app_id}")
            return {"label": emulator.label, "ok": True, "already_present": False, "app_id": plan.app_id}
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        reason = detail[-1] if detail else f"flatpak exited {completed.returncode}"
        self._logger.warning(f"emulator_install: {plan.app_id} not installed after the command: {reason}")
        return self._failure(emulator, reason, app_id=plan.app_id)

    def _flatpak_app_installed(self, app_id: str) -> bool:
        """Whether *app_id* is installed in either tree ``flatpak`` searches."""
        return any(
            os.path.isdir(os.path.join(root, "flatpak", "app", app_id))
            for root in (self._system_flatpak_root, os.path.join(self._user_home, ".local", "share"))
        )

    # -- a release build ----------------------------------------------------

    def _install_release(self, emulator: InventoryEmulator, plan: ReleaseInstall) -> dict[str, object]:
        target = appimage_path(emulator, user_home=self._user_home)
        if target is None:
            return self._failure(emulator, "no_install_path", repo=plan.repo)
        releases = self._releases(plan)
        if not releases:
            return self._failure(emulator, "release_unreachable", repo=plan.repo)
        chosen, undigested = self._choose(plan, releases)
        if chosen is None:
            # Zero matches and two matches are the same refusal: this plugin will not pick
            # a CPU architecture or guess a filename. An asset that matched but published
            # no hash is the other refusal, and a different thing to say.
            if undigested is not None:
                self._logger.warning(f"emulator_install: {undigested} has no digest; refusing to install it")
                return self._failure(emulator, "no_digest", asset=undigested, repo=plan.repo)
            return self._failure(emulator, "asset_unresolved", repo=plan.repo, releases=len(releases))
        release, asset_name, expected = chosen
        tag = release.get("tag_name")
        version = tag if isinstance(tag, str) else None
        if os.path.isfile(target) and self._sha256_file(target) == expected:
            return {
                "label": emulator.label,
                "ok": True,
                "already_present": True,
                "path": target,
                "version": version,
                "sha256": expected,
            }
        if not isinstance(tag, str) or not tag:
            return self._failure(emulator, "release_unreachable", repo=plan.repo)
        return self._download(emulator, plan, target, download_url(plan.repo, tag, asset_name), expected, version)

    def _choose(self, plan: ReleaseInstall, releases: list[dict]) -> tuple[tuple[dict, str, str] | None, str | None]:
        """The first release that states both a matching asset and its hash.

        Newest first, and a release whose asset carries no digest is skipped rather than
        installed unverified — if an older one still has one, that is the build this can
        honestly vouch for. The second half of the answer names the asset that matched but
        could not be vouched for, so the caller can say *that* rather than "no asset".
        """
        undigested: str | None = None
        for release in releases:
            assets = release.get("assets") if isinstance(release.get("assets"), list) else []
            names = [
                asset.get("name")
                for asset in assets
                if isinstance(asset, dict) and isinstance(asset.get("name"), str)
            ]
            asset_name = matching_asset(names, plan.asset_pattern)
            if asset_name is None:
                continue
            asset = next(item for item in assets if isinstance(item, dict) and item.get("name") == asset_name)
            expected = digest_from_asset(asset)
            if expected is None:
                undigested = undigested or asset_name
                continue
            return (release, asset_name, expected), None
        return None, undigested

    def _releases(self, plan: ReleaseInstall) -> list[dict]:
        """The newest release, or the recent listing when ``latest`` answers nothing.

        ``/releases/latest`` is 404 for a project whose newest builds are all marked
        pre-release (Citron's nightlies), so a listing is asked for before the source is
        written off. Drafts are dropped; pre-releases are kept, because for a nightly-only
        project they are the builds.
        """
        payload = self._get(plan.release_api)
        if isinstance(payload, dict):
            return [payload]
        listing = self._get(plan.releases_api)
        if not isinstance(listing, list):
            return []
        return [entry for entry in listing if isinstance(entry, dict) and not entry.get("draft")]

    def _get(self, url: str) -> object:
        """JSON from *url*, or ``None`` when it cannot be read."""
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=_RELEASE_TIMEOUT_SECONDS) as response:
                return json.loads(response.read(4 * 1024 * 1024))
        except (urllib.error.URLError, OSError, ValueError) as exc:
            self._logger.warning(f"emulator_install: {url} could not be read: {exc}")
            return None

    def _download(
        self,
        emulator: InventoryEmulator,
        plan: ReleaseInstall,
        target: str,
        url: str,
        expected: str,
        version: str | None,
    ) -> dict[str, object]:
        """Stream *url* into ``<target>.part``, verify it, then move it into place."""
        partial = f"{target}.part"
        digest = hashlib.sha256()
        written = 0
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as response, open(
                partial, "wb"
            ) as handle:
                while chunk := response.read(_CHUNK):
                    written += len(chunk)
                    if written > _MAX_DOWNLOAD_BYTES:
                        raise ValueError(f"asset is larger than {_MAX_DOWNLOAD_BYTES} bytes")
                    digest.update(chunk)
                    handle.write(chunk)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            self._logger.warning(f"emulator_install: {plan.repo} download failed: {exc}")
            with contextlib.suppress(OSError):
                os.remove(partial)
            return self._failure(emulator, f"download_failed: {exc}", repo=plan.repo)
        actual = digest.hexdigest()
        if actual != expected:
            self._logger.warning(
                f"emulator_install: {plan.repo} asset hash mismatch (expected {expected}, got {actual}); discarding"
            )
            with contextlib.suppress(OSError):
                os.remove(partial)
            return self._failure(emulator, "hash_mismatch", repo=plan.repo, expected=expected, actual=actual)
        try:
            os.chmod(partial, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            os.replace(partial, target)
        except OSError as exc:
            self._logger.warning(f"emulator_install: {plan.repo} could not be written to {target}: {exc}")
            with contextlib.suppress(OSError):
                os.remove(partial)
            return self._failure(emulator, f"write_failed: {exc}", repo=plan.repo)
        self._logger.info(f"emulator_install: installed {emulator.label} {version or ''} at {target} ({written} bytes)")
        return {
            "label": emulator.label,
            "ok": True,
            "already_present": False,
            "path": target,
            "version": version,
            "sha256": actual,
            "bytes": written,
        }

    @staticmethod
    def _sha256_file(path: str) -> str | None:
        """The file's sha256, or ``None`` when it cannot be read."""
        digest = hashlib.sha256()
        try:
            with open(path, "rb") as handle:
                while chunk := handle.read(_CHUNK):
                    digest.update(chunk)
        except OSError:
            return None
        return digest.hexdigest()

    @staticmethod
    def _failure(emulator: InventoryEmulator, reason: str, **extra: object) -> dict[str, object]:
        return {"label": emulator.label, "ok": False, "reason": reason, **extra}


def labels(results: Iterable[dict[str, object]]) -> list[str]:
    """The labels of the results that succeeded, for a caller's one-line report."""
    return [str(result.get("label")) for result in results if result.get("ok")]
