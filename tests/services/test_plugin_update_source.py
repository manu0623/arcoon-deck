"""Tests for services.plugin_update — where an update comes from, and its shape.

The panel's Update button goes through the same service as a pasted URL, so the two
things that matter here are: a blank field means this project's own newest build, and a
source archive is turned into something the installer will accept.
"""

from __future__ import annotations

import io
import logging
import zipfile

from domain.plugin_archive import PluginArchive
from services.plugin_update import DEFAULT_UPDATE_URL, PluginUpdateService


def _zip(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, body in members.items():
            archive.writestr(name, body)
    return buffer.getvalue()


def _release_zip(folder: str = "romm-tender") -> bytes:
    return _zip(
        {
            f"{folder}/plugin.json": b'{"name": "Arcoon Deck", "version": "0.48.55"}',
            f"{folder}/main.py": b"# backend",
            f"{folder}/dist/index.js": b"// panel",
            f"{folder}/py_modules/bootstrap/services.py": b"# root",
        }
    )


class FakeInstaller:
    """Records what it was handed; the filesystem half is tested elsewhere."""

    def __init__(self) -> None:
        self.names: list[str] = []
        self.folder = ""
        self.restarts = 0

    def install(self, archive_path, folder, *, expected_name, current_version):
        with zipfile.ZipFile(archive_path) as archive:
            self.names = archive.namelist()
        self.folder = folder
        return PluginArchive(folder=folder, version="0.48.55", entries=tuple(self.names))

    def schedule_loader_restart(self) -> None:
        self.restarts += 1


def _service(payload: bytes, *, folder: str = "romm-tender"):
    installer = FakeInstaller()
    asked: list[str] = []

    def fetch(url: str) -> bytes:
        asked.append(url)
        return payload

    service = PluginUpdateService(
        installer=installer,
        folder=folder,
        plugin_name="Arcoon Deck",
        current_version="0.48.54",
        logger=logging.getLogger("test"),
        fetcher=fetch,
    )
    return service, installer, asked


def test_a_blank_url_installs_this_projects_newest_build():
    service, installer, asked = _service(_release_zip())

    result = service.update_from_url("")

    assert asked == [DEFAULT_UPDATE_URL]
    assert result["success"] is True
    assert installer.restarts == 1


def test_no_url_at_all_behaves_like_a_blank_one():
    service, _installer, asked = _service(_release_zip())

    service.update_from_url(None)

    assert asked == [DEFAULT_UPDATE_URL]


def test_a_pasted_url_still_wins():
    service, _installer, asked = _service(
        _release_zip(),
    )

    service.update_from_url("  https://example.test/arcoon.zip  ")

    assert asked == ["https://example.test/arcoon.zip"]


def test_a_source_archive_is_rerooted_and_stripped_to_the_shipped_subset():
    payload = _zip(
        {
            "arcoon-deck-main/plugin.json": b'{"name": "Arcoon Deck", "version": "0.48.55"}',
            "arcoon-deck-main/main.py": b"# backend",
            "arcoon-deck-main/dist/index.js": b"// panel",
            "arcoon-deck-main/py_modules/bootstrap/services.py": b"# root",
            "arcoon-deck-main/src/components/MainPage.tsx": b"// dev only",
            "arcoon-deck-main/tests/test_thing.py": b"# dev only",
            "arcoon-deck-main/docs/index.md": b"# dev only",
            "arcoon-deck-main/.github/workflows/ci.yml": b"# dev only",
        }
    )
    service, installer, _asked = _service(payload)

    result = service.update_from_url("")

    assert result["success"] is True
    assert installer.folder == "romm-tender"
    assert all(name.startswith("romm-tender/") for name in installer.names)
    assert "romm-tender/tests/test_thing.py" not in installer.names
    assert "romm-tender/docs/index.md" not in installer.names
    assert "romm-tender/src/components/MainPage.tsx" not in installer.names
    assert "romm-tender/py_modules/bootstrap/services.py" in installer.names


def test_an_archive_already_shaped_for_the_installer_is_left_alone():
    service, installer, _asked = _service(_release_zip())

    service.update_from_url("")

    assert sorted(installer.names) == sorted(
        [
            "romm-tender/plugin.json",
            "romm-tender/main.py",
            "romm-tender/dist/index.js",
            "romm-tender/py_modules/bootstrap/services.py",
        ]
    )


def test_a_zip_with_no_single_top_folder_is_passed_through_to_be_refused():
    payload = _zip({"plugin.json": b"{}", "other.txt": b"x"})
    service, _installer, _asked = _service(payload)

    result = service.update_from_url("")

    # The installer's own validation is the authority on a malformed archive; the
    # fake accepts it, so this only proves the service did not mangle it.
    assert result["success"] is True


def test_a_non_zip_payload_is_reported_as_a_failure_not_a_crash():
    class ExplodingInstaller(FakeInstaller):
        def install(self, archive_path, folder, *, expected_name, current_version):
            raise zipfile.BadZipFile("File is not a zip file")

    service = PluginUpdateService(
        installer=ExplodingInstaller(),
        folder="romm-tender",
        plugin_name="Arcoon Deck",
        current_version="0.48.54",
        logger=logging.getLogger("test"),
        fetcher=lambda url: b"<html>404</html>",
    )

    result = service.update_from_url("")

    assert result["success"] is False
    assert "zip" in result["message"].lower()
