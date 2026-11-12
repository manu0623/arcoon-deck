"""The `layout.json` contract: one platform's launch and save shape, stated by us.

See [ADR-0034](../../docs/adr/0034-the-layout-is-owned-by-the-plugin.md). A provisioner
writes this file after it has created the tree it describes; the plugin reads it and stops
inferring where a third-party emulator keeps things.

Two rules shape everything here.

**A platform that is not in the manifest is not managed.** It keeps the live catalogue
answer the plugin has today — unchanged, refusal states and all. That is what makes this
additive and reversible, and it is why every malformed entry degrades to *absent* rather
than to an error: the worst case of a corrupt file must be the behaviour that already
works.

**The manifest states a save PATH, never a user directory.** `-u`-style relocation moves
the emulator's whole user tree — controller profiles, config, shaders — which is a price
measured on the reference Deck and refused (ADR-0034, Context).

Pure compute: no filesystem, no settings, no I/O. The adapter reads the file; this module
parses what it read.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from domain.save_bank import canonical_platform

#: The file name the provisioner writes at the root of the tree it created.
MANIFEST_FILENAME = "layout.json"

#: The manifest version this reader understands. A newer file is not guessed at.
SUPPORTED_VERSION = 1

#: The token a launch argument or a save directory uses for the layout's own root.
ROOT_TOKEN = "{root}"

#: What a save unit means for the answer this plugin builds from it.
#: ``single-file`` is one file at ``save_dir/<name>``; ``gci-set`` is a folder whose entries
#: are named by the emulator itself (GameCube's ``<maker>-<code>-<internal>.gci``);
#: ``directory`` is a whole folder carried as a unit.
KNOWN_SAVE_UNITS = frozenset({"single-file", "gci-set", "directory"})

_DEFAULT_SAVE_UNIT = "single-file"


@dataclass(frozen=True)
class ManagedPlatform:
    """One platform the provisioner manages, exactly as the manifest states it.

    ``launch`` is the argv the plugin bakes, with ``%ROM%`` and any ``%EMULATOR_*%``
    left in place for RetroDECK's launcher — the plugin substitutes ``{root}`` and
    nothing else, because everything else is RetroDECK's job and was never ours.

    ``save_dir`` already has ``{root}`` substituted. It may still carry the resolver's
    ``<region>`` hole, which is what ``needs`` says.
    """

    platform: str
    emulator: str | None
    launch: tuple[str, ...]
    save_dir: str
    save_unit: str
    needs: tuple[str, ...]

    @property
    def launch_command(self) -> str:
        """The baked command text — argv joined, placeholders intact."""
        return " ".join(self.launch)


@dataclass(frozen=True)
class LayoutManifest:
    """A parsed manifest: the root it was written for, and the platforms it manages."""

    root: str
    platforms: tuple[ManagedPlatform, ...]

    def entry_for(self, platform_slug: str | None) -> ManagedPlatform | None:
        """The managed entry for *platform_slug*, or ``None`` when it is not managed.

        Looked up by the manifest's own key first, then by the plugin's canonical spelling
        (``ngc`` and ``gc`` are one platform; a provisioner may have written either), so a
        file naming a platform the plugin's vocabulary spells differently still applies.
        """
        if not platform_slug:
            return None
        wanted = {platform_slug, canonical_platform(platform_slug)}
        for entry in self.platforms:
            if entry.platform in wanted or canonical_platform(entry.platform) in wanted:
                return entry
        return None


def parse_layout_manifest(text: str) -> LayoutManifest | None:
    """Parse *text* into a :class:`LayoutManifest`, or ``None`` when it cannot be trusted.

    ``None`` covers every unusable shape: not JSON, not an object, a version this reader
    does not know, no usable root, no platform entries. Each of those means the same thing
    to a caller — behave as though no manifest exists — so they share one answer rather
    than four that callers would have to agree on.

    A single malformed **entry** is dropped rather than failing the file: a typo in one
    platform must not switch every other managed platform back to inference, and a dropped
    entry is exactly the state the plugin already handles (that platform is unmanaged).
    """
    try:
        document = json.loads(text)
    except (TypeError, ValueError):
        return None
    if not isinstance(document, dict):
        return None

    version = document.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version != SUPPORTED_VERSION:
        return None

    root = document.get("root")
    if not isinstance(root, str) or not root.strip():
        return None

    platforms = document.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        return None

    entries = [entry for entry in (_parse_entry(key, value, root) for key, value in platforms.items()) if entry]
    if not entries:
        return None
    return LayoutManifest(root=root.strip(), platforms=tuple(entries))


def _parse_entry(platform: Any, value: Any, root: str) -> ManagedPlatform | None:
    """One platform entry, or ``None`` when it does not state what a launch needs.

    ``launch`` and ``save_dir`` are required and have no defaults: a managed platform that
    does not say what to run has nothing to offer over the catalogue answer, and one that
    does not say where the saves go is the exact guess this manifest exists to replace.
    """
    if not isinstance(platform, str) or not platform.strip() or not isinstance(value, dict):
        return None

    launch = value.get("launch")
    if not isinstance(launch, list) or not launch:
        return None
    argv = tuple(_with_root(item, root) for item in launch if isinstance(item, str) and item.strip())
    if len(argv) != len(launch):
        return None

    save_dir = value.get("save_dir")
    if not isinstance(save_dir, str) or not save_dir.strip():
        return None

    save_unit = value.get("save_unit", _DEFAULT_SAVE_UNIT)
    if not isinstance(save_unit, str) or save_unit not in KNOWN_SAVE_UNITS:
        return None

    declared_needs = value.get("needs", ())
    if isinstance(declared_needs, str):
        needs = (declared_needs,) if declared_needs else ()
    elif isinstance(declared_needs, (list, tuple)):
        needs = tuple(item for item in declared_needs if isinstance(item, str) and item)
    else:
        return None

    emulator = value.get("emulator")
    if emulator is not None and not isinstance(emulator, str):
        return None

    return ManagedPlatform(
        platform=platform.strip(),
        emulator=emulator.strip() if isinstance(emulator, str) else None,
        launch=argv,
        save_dir=_with_root(save_dir.strip(), root),
        save_unit=save_unit,
        needs=needs,
    )


def _with_root(value: str, root: str) -> str:
    """*value* with every ``{root}`` replaced by *root*.

    Substitution happens here, once, so no consumer has to remember that a manifest path is
    a template — and so a path that legitimately contains the literal characters ``{root}``
    cannot appear by accident.
    """
    return value.replace(ROOT_TOKEN, root.rstrip("/"))
