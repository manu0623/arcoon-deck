"""What a self-update archive must prove before it may replace the running plugin.

The installer runs inside the loader it is replacing, so every refusal here is the
only thing standing between a wrong zip and a panel that opens to an import error.
"""

from __future__ import annotations

import json

import pytest

from domain.plugin_archive import PluginArchive, UpdateRefused, inspect_archive, version_key

_FOLDER = "romm-tender"
_ENTRIES = (
    f"{_FOLDER}/plugin.json",
    f"{_FOLDER}/main.py",
    f"{_FOLDER}/dist/index.js",
    f"{_FOLDER}/py_modules/bootstrap/services.py",
)


def _manifest(**overrides: object) -> bytes:
    payload = {"name": "Arcoon Deck", "version": "0.34.0", "author": "x", "flags": [], "api_version": 1}
    payload.update(overrides)
    return json.dumps(payload).encode()


def _inspect(names=_ENTRIES, manifest=None, current="0.33.0"):
    return inspect_archive(
        list(names),
        _manifest() if manifest is None else manifest,
        expected_folder=_FOLDER,
        expected_name="Arcoon Deck",
        current_version=current,
    )


class TestAValidArchive:
    def test_it_reports_the_version_it_will_install(self) -> None:
        assert _inspect() == PluginArchive(folder=_FOLDER, version="0.34.0", entries=tuple(sorted(_ENTRIES)))

    def test_extra_files_are_carried_not_refused(self) -> None:
        """A build carries docs and assets the validator has no business enumerating."""
        archive = _inspect([*_ENTRIES, f"{_FOLDER}/README.md", f"{_FOLDER}/docs/x.md"])
        assert f"{_FOLDER}/docs/x.md" in archive.entries


class TestRefusals:
    def test_an_empty_archive(self) -> None:
        with pytest.raises(UpdateRefused, match="empty"):
            _inspect([])

    def test_two_top_level_folders(self) -> None:
        """Decky unpacks the top folder; two of them would install half a plugin."""
        with pytest.raises(UpdateRefused, match="exactly one top-level folder"):
            _inspect([*_ENTRIES, "other/plugin.json"])

    def test_a_different_folder_name(self) -> None:
        """Decky derives settings, data and logs from the folder name — a rename moves them."""
        with pytest.raises(UpdateRefused, match="unpacks into"):
            _inspect([f"Arcoon Deck/{name.split(chr(47), 1)[1]}" for name in _ENTRIES])

    def test_another_plugins_archive(self) -> None:
        with pytest.raises(UpdateRefused, match="not 'Arcoon Deck'"):
            _inspect(manifest=_manifest(name="Something Else"))

    def test_a_manifest_that_is_not_json(self) -> None:
        with pytest.raises(UpdateRefused, match="unreadable"):
            _inspect(manifest=b"not json")

    def test_a_missing_version(self) -> None:
        with pytest.raises(UpdateRefused, match="no version"):
            _inspect(manifest=json.dumps({"name": "Arcoon Deck"}).encode())

    def test_the_same_version(self) -> None:
        with pytest.raises(UpdateRefused, match="not newer"):
            _inspect(current="0.34.0")

    def test_an_older_version(self) -> None:
        with pytest.raises(UpdateRefused, match="not newer"):
            _inspect(manifest=_manifest(version="0.32.0"))

    @pytest.mark.parametrize("missing", ["main.py", "dist/index.js", "py_modules/bootstrap/services.py", "plugin.json"])
    def test_a_required_entry_that_is_absent(self, missing: str) -> None:
        names = [name for name in _ENTRIES if f"{_FOLDER}/{missing}" != name]
        with pytest.raises(UpdateRefused, match="would not run"):
            _inspect(names)

    def test_a_top_folder_that_climbs(self) -> None:
        with pytest.raises(UpdateRefused):
            _inspect(["../romm-tender/plugin.json", *_ENTRIES[1:]])


class TestVersionOrdering:
    @pytest.mark.parametrize(
        ("newer", "older"),
        [("0.34.0", "0.33.9"), ("1.0.0", "0.99.99"), ("0.33.10", "0.33.9"), ("0.34.0-beta", "0.33.0")],
    )
    def test_newer_compares_greater(self, newer: str, older: str) -> None:
        assert version_key(newer) > version_key(older)

    def test_suffixes_do_not_change_the_order(self) -> None:
        assert version_key("0.34.0-beta.2") == version_key("0.34.0")
