"""What an update archive must prove before it may replace the running plugin.

The plugin installs itself from inside Decky's loader, which already runs as root —
that is what makes an in-panel update possible without a password. It is also what
makes a bad archive unrecoverable in the ordinary way: the code doing the swap IS the
code being swapped, so a half-trusted archive can leave the panel with nothing to
open. Everything decidable from the archive's own contents is therefore decided here,
before a single byte is written: one top folder, this plugin's name, the entries that
make it runnable, and a version that is actually newer.

Pure: no I/O, stdlib only. The caller supplies the member names and the bytes of
``plugin.json`` it already read.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

# The entries without which the unpacked folder is not a plugin: Decky reads
# plugin.json, the backend starts at main.py, the panel needs dist/index.js, and
# bootstrap is the composition root the backend raises without.
REQUIRED_ENTRIES: tuple[str, ...] = (
    "main.py",
    "plugin.json",
    "dist/index.js",
    "py_modules/bootstrap/services.py",
)


class UpdateRefused(Exception):
    """An archive that must not be installed. The message is shown to the user."""


@dataclass(frozen=True, slots=True)
class PluginArchive:
    """A validated update ready to be unpacked."""

    folder: str
    version: str
    entries: tuple[str, ...]


def version_key(text: str) -> tuple[int, int, int]:
    """Comparable form of a version string, tolerant of suffixes (``1.2.0-beta``).

    The plugin's versions come from release-please and are plain ``x.y.z``; suffixes
    are still tolerated so a prerelease can be installed on purpose. Digits are taken
    per component and everything else ignored — enough to answer "is this newer",
    which is the only question asked, and never a substitute for a real semver
    comparison.
    """
    parts: list[int] = []
    for piece in text.split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return parts[0], parts[1], parts[2]


def _top_folder(names: Sequence[str]) -> str:
    tops = {name.split("/", 1)[0] for name in names if name and not name.startswith("/")}
    if len(tops) != 1:
        raise UpdateRefused("The archive must hold exactly one top-level folder.")
    folder = tops.pop()
    if not folder or folder in {".", ".."} or "/" in folder or "\\" in folder:
        raise UpdateRefused(f"The archive's top-level folder name is not usable: {folder!r}")
    return folder


def inspect_archive(
    names: Sequence[str],
    plugin_json: bytes,
    *,
    expected_folder: str,
    expected_name: str,
    current_version: str,
    allow_equal_version: bool = False,
) -> PluginArchive:
    """Validate an update and say what will be installed, or raise :class:`UpdateRefused`."""
    if not names:
        raise UpdateRefused("The archive is empty.")
    folder = _top_folder(names)
    if folder != expected_folder:
        raise UpdateRefused(
            f"The archive unpacks into {folder!r}, but Decky derives this plugin's settings, data and logs "
            f"from the folder name {expected_folder!r}. Installing it would look like a fresh plugin."
        )

    try:
        manifest: Any = json.loads(plugin_json.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateRefused(f"The archive's plugin.json is unreadable: {exc}") from exc
    if not isinstance(manifest, dict):
        raise UpdateRefused("The archive's plugin.json is not an object.")

    name = manifest.get("name")
    if name != expected_name:
        # A zip of some other Decky plugin would otherwise replace this one wholesale.
        raise UpdateRefused(f"The archive is for {name!r}, not {expected_name!r}.")

    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        raise UpdateRefused("The archive's plugin.json carries no version.")
    if allow_equal_version:
        # A build pushed under the same version is still a different build (the
        # package version is bumped by hand here, and a fix can land without one),
        # so an equal version is installable — a downgrade is not.
        if version_key(version) < version_key(current_version):
            raise UpdateRefused(
                f"The archive is version {version}, which is older than {current_version}."
            )
    elif version_key(version) <= version_key(current_version):
        raise UpdateRefused(f"The archive is version {version}, which is not newer than {current_version}.")

    present = set(names)
    missing = [entry for entry in REQUIRED_ENTRIES if f"{folder}/{entry}" not in present]
    if missing:
        raise UpdateRefused(f"The archive is missing {', '.join(missing)} — it would not run.")

    return PluginArchive(folder=folder, version=version, entries=tuple(sorted(present)))
