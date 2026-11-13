"""Installing an emulator: the store command, and a release that is verified before it lands.

The network is faked at the one seam the adapter uses (``urllib.request.urlopen``) and the
flatpak command at ``subprocess.run``, so what these tests pin is the adapter's own
behaviour: what it writes, where, and everything it refuses to write.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import subprocess

import pytest

from adapters.emulator_install import EmulatorInstallAdapter
from domain.owned_inventory import InventoryEmulator, InventoryGithubSource, InventoryInstall

_LOGGER = logging.getLogger("test_emulator_install")
_BYTES = b"#!ELF an emulator\n"
_SHA = hashlib.sha256(_BYTES).hexdigest()


def _emulator(*, flatpak: str | None = None, github: InventoryGithubSource | None = None) -> InventoryEmulator:
    return InventoryEmulator(
        label="PPSSPP (Standalone)",
        emulator="ppsspp",
        kind="standalone",
        host_binaries=("~/Applications/PPSSPP.AppImage", "/usr/bin/PPSSPPSDL"),
        flatpak="org.ppsspp.PPSSPP",
        install=InventoryInstall(flatpak=flatpak, github=github),
    )


class _Response(io.BytesIO):
    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _release(assets: list[dict]) -> dict:
    return {"tag_name": "v1.20.4", "assets": assets}


def _asset(name: str, digest: str | None = _SHA) -> dict:
    payload: dict = {"name": name}
    if digest is not None:
        payload["digest"] = f"sha256:{digest}"
    return payload


def _patch_release(monkeypatch: pytest.MonkeyPatch, release: dict, *, body: bytes = _BYTES) -> list[str]:
    """Serve *release* as JSON and *body* for its download; return the URLs asked for."""
    asked: list[str] = []

    def fake_urlopen(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else str(request)
        asked.append(url)
        if url.endswith("/releases/latest"):
            return _Response(json.dumps(release).encode())
        return _Response(body)

    monkeypatch.setattr("adapters.emulator_install.urllib.request.urlopen", fake_urlopen)
    return asked


@pytest.fixture
def adapter(tmp_path) -> EmulatorInstallAdapter:
    return EmulatorInstallAdapter(user_home=str(tmp_path), logger=_LOGGER)


class TestAReleaseBuild:
    def test_it_lands_under_the_name_the_launch_probes(self, adapter, tmp_path, monkeypatch) -> None:
        _patch_release(monkeypatch, _release([_asset("PPSSPP-v1.20.4-anylinux-x86_64.AppImage")]))

        result = adapter.install(
            _emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-*-anylinux-x86_64.AppImage"))
        )

        target = tmp_path / "Applications" / "PPSSPP.AppImage"
        assert result["ok"] is True
        assert result["already_present"] is False
        assert os.path.isfile(target)
        assert target.read_bytes() == _BYTES
        assert not os.path.exists(f"{target}.part")
        if os.name == "posix":
            assert os.access(target, os.X_OK)

    def test_a_mismatched_hash_is_discarded(self, adapter, tmp_path, monkeypatch) -> None:
        _patch_release(monkeypatch, _release([_asset("PPSSPP-x86_64.AppImage")]), body=b"tampered")

        result = adapter.install(_emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-*.AppImage")))

        assert result["ok"] is False
        assert result["reason"] == "hash_mismatch"
        assert not os.path.exists(tmp_path / "Applications" / "PPSSPP.AppImage")
        assert not os.path.exists(tmp_path / "Applications" / "PPSSPP.AppImage.part")

    def test_an_asset_without_a_digest_is_refused(self, adapter, tmp_path, monkeypatch) -> None:
        """Nothing is written: a binary nobody can vouch for is not an install."""
        _patch_release(monkeypatch, _release([_asset("PPSSPP-x86_64.AppImage", digest=None)]))

        result = adapter.install(_emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-*.AppImage")))

        assert result["ok"] is False
        assert result["reason"] == "no_digest"
        assert not os.path.exists(tmp_path / "Applications")

    def test_two_matching_assets_are_refused(self, adapter, tmp_path, monkeypatch) -> None:
        assets = [_asset("PPSSPP-x64.AppImage"), _asset("PPSSPP-x64-v3.AppImage")]
        _patch_release(monkeypatch, _release(assets))

        result = adapter.install(_emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-x64*.AppImage")))

        assert result["ok"] is False
        assert result["reason"] == "asset_unresolved"
        assert not os.path.exists(tmp_path / "Applications")

    def test_an_installed_copy_at_the_same_version_is_left_alone(self, adapter, tmp_path, monkeypatch) -> None:
        target = tmp_path / "Applications" / "PPSSPP.AppImage"
        target.parent.mkdir(parents=True)
        target.write_bytes(_BYTES)
        asked = _patch_release(monkeypatch, _release([_asset("PPSSPP-x86_64.AppImage")]))

        result = adapter.install(_emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-*.AppImage")))

        assert result["already_present"] is True
        assert all(url.endswith("/releases/latest") for url in asked), asked

    def test_an_older_copy_is_replaced(self, adapter, tmp_path, monkeypatch) -> None:
        target = tmp_path / "Applications" / "PPSSPP.AppImage"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"old build")
        _patch_release(monkeypatch, _release([_asset("PPSSPP-x86_64.AppImage")]))

        result = adapter.install(_emulator(github=InventoryGithubSource("hrydgard/ppsspp", "PPSSPP-*.AppImage")))

        assert result["ok"] is True
        assert target.read_bytes() == _BYTES

    def test_no_release_row_has_no_install_path(self, adapter, monkeypatch) -> None:
        _patch_release(monkeypatch, _release([_asset("PPSSPP-x86_64.AppImage")]))
        emulator = InventoryEmulator(
            label="Vita3K",
            emulator="vita3k",
            kind="standalone",
            host_binaries=("/usr/bin/Vita3K",),
            install=InventoryInstall(github=InventoryGithubSource("Vita3K/Vita3K", "*.AppImage")),
        )

        result = adapter.install(emulator)

        assert result["ok"] is False
        assert result["reason"] == "no_install_path"


class TestAStoreBuild:
    def test_it_runs_the_unattended_user_install(self, adapter, tmp_path, monkeypatch) -> None:
        calls: list[list[str]] = []

        def fake_run(argv, **kwargs):
            calls.append(list(argv))
            if "install" in argv:
                (tmp_path / ".local" / "share" / "flatpak" / "app" / "org.ppsspp.PPSSPP").mkdir(parents=True)
            return subprocess.CompletedProcess(argv, 0, "", "")

        monkeypatch.setattr("adapters.emulator_install.subprocess.run", fake_run)

        result = adapter.install(_emulator(flatpak="org.ppsspp.PPSSPP"))

        # The install, then the access grant the emulator needs to read the ROM it was
        # installed to play (measured: PCSX2's flatpak ships with no filesystem access).
        assert calls == [
            ["flatpak", "install", "--user", "-y", "flathub", "org.ppsspp.PPSSPP"],
            ["flatpak", "override", "--user", "--filesystem=host", "org.ppsspp.PPSSPP"],
        ]
        assert result["ok"] is True
        assert result["already_present"] is False
        assert result["sandbox_host_access"] is True

    def test_an_installed_app_is_not_reinstalled_but_gets_its_access(self, adapter, tmp_path, monkeypatch) -> None:
        (tmp_path / ".local" / "share" / "flatpak" / "app" / "org.ppsspp.PPSSPP").mkdir(parents=True)
        calls: list[list[str]] = []

        def fake_run(argv, **kwargs):
            calls.append(list(argv))
            return subprocess.CompletedProcess(argv, 0, "", "")

        monkeypatch.setattr("adapters.emulator_install.subprocess.run", fake_run)

        result = adapter.install(_emulator(flatpak="org.ppsspp.PPSSPP"))

        # No install — but the grant still runs, because a build that predates the
        # access rule is exactly the one that cannot see the ROM tree.
        assert calls == [["flatpak", "override", "--user", "--filesystem=host", "org.ppsspp.PPSSPP"]]
        assert result == {
            "label": "PPSSPP (Standalone)",
            "ok": True,
            "already_present": True,
            "app_id": "org.ppsspp.PPSSPP",
            "sandbox_host_access": True,
        }

    def test_a_refused_access_grant_is_reported_without_failing_the_install(
        self, adapter, tmp_path, monkeypatch
    ) -> None:
        def fake_run(argv, **kwargs):
            if "override" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "error: app not installed\n")
            (tmp_path / ".local" / "share" / "flatpak" / "app" / "org.ppsspp.PPSSPP").mkdir(parents=True)
            return subprocess.CompletedProcess(argv, 0, "", "")

        monkeypatch.setattr("adapters.emulator_install.subprocess.run", fake_run)

        result = adapter.install(_emulator(flatpak="org.ppsspp.PPSSPP"))

        assert result["ok"] is True
        assert result["sandbox_host_access"] is False

    def test_a_command_that_installs_nothing_reports_why(self, adapter, monkeypatch) -> None:
        monkeypatch.setattr(
            "adapters.emulator_install.subprocess.run",
            lambda argv, **kwargs: subprocess.CompletedProcess(argv, 1, "", "error: app not found\n"),
        )

        result = adapter.install(_emulator(flatpak="org.ppsspp.PPSSPP"))

        assert result["ok"] is False
        assert result["reason"] == "error: app not found"
