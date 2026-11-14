#!/usr/bin/env python3
"""Provision the plugin-owned layout and write the manifest it describes (ADR-0034).

This is the first half of the two-part app: the part that decides where things live. The
plugin is the second half — it reads `layout.json`, bakes each managed platform's launch
from it, and answers that platform's save question from the same entry.

Usage, once per device:

    python3 scripts/provision_layout.py --check                       # change nothing
    python3 scripts/provision_layout.py \\
        --adopt gc=/home/deck/retrodeck/saves/gc/User/GC/<region>/Card A

Why `--adopt`: a save that already exists must not have to move for this to help. Adoption
is an explicit manifest entry naming the directory the save is in today, which is the whole
reason it is a flag rather than a rule — the script does not go looking for saves, and
nothing here guesses where an emulator keeps them.

The launch each entry states names the programs **this device** has, not the ones the device
this was measured on had: the flatpak executable and the Eden binary are discovered from the
plugin's own inventory of candidate paths (ADR-0067), and every `~/…` candidate is expanded
against the home the run was pointed at. A platform whose program is not found is refused —
with the paths that were searched — instead of baking an argv that cannot exec, and a refusal
changes nothing on disk.

The manifest is written LAST, after the tree exists and each path has been checked, so a run
that fails part-way leaves the plugin on its unmanaged behaviour rather than pointing it at
directories that are not there.

Deliberately not in this cut: fetching cores, writing emulator configuration, migrating an
adopted directory into the owned root. Those are later steps, and each needs its own
measurement (the GameCube `-C GDIFolderAPath` question in particular).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Run from a checkout or from inside the installed plugin, this script has to agree with the
# plugin about where the data directory is — so it asks the same domain function instead of
# spelling the path a second time. Getting this wrong is not a broken run, it is a manifest
# the plugin never reads.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py_modules"))

from domain.owned_inventory import InventoryEmulator, parse_inventory  # noqa: E402
from domain.user_data_location import data_root  # noqa: E402

MANIFEST_NAME = "layout.json"
MANIFEST_VERSION = 1
SUBDIRECTORIES = ("library", "cores", "saves", "bios", "art", "mods", "cache")
GC_PLATFORMS = ("gc", "ngc")
SWITCH_PLATFORMS = ("switch", "nsw")
WII_PLATFORMS = ("wii",)

# What a managed entry's launch names, and where that answer comes from: the plugin's own
# inventory — the document its picker already answers from (ADR-0041), so the candidate
# binary paths and the flatpak id are stated once for both readers instead of twice for one
# device. Nothing here spells a home directory: every `~/…` candidate is expanded against the
# home this run was pointed at, the rule `adapters/owned_catalogue.py` already states.
INVENTORY_PATH = Path(__file__).resolve().parent.parent / "defaults" / "emulator_inventory.json"

# The rows a launch is read from, by the inventory's own spelling of platform and emulator.
SWITCH_ROW = "switch"
DOLPHIN_ROW = "gc"
SWITCH_ID = "eden"
DOLPHIN_ID = "dolphin"

# The flatpak executable: named absolutely when it is there, because the launcher's PATH is
# Steam's, not a login shell's — the rule `adapters/owned_catalogue.py` uses.
FLATPAK_PATH = "/usr/bin/flatpak"


class ProvisionError(RuntimeError):
    """A managed entry cannot be written because this device does not have its program."""


@dataclass(frozen=True, slots=True)
class HostBinaries:
    """The programs a managed launch runs, as this device states them.

    ``None`` is "not found where the inventory says it can be", and the platforms needing
    that program are refused rather than baked into an argv that cannot exec. ``searched``
    is what the refusal quotes, so a missing install is diagnosable from the message.
    """

    flatpak: str | None = None
    eden: str | None = None
    searched: tuple[str, ...] = ()


def _expand(candidate: str, home: Path) -> Path:
    """One inventory candidate against *home*, not against ``$HOME``.

    The document is written for one user and has to resolve on another, so ``~`` is a
    placeholder rather than the reading machine's directory.
    """
    if candidate == "~":
        return home
    if candidate.startswith("~/"):
        return home / candidate[2:]
    return Path(candidate)


def _row(emulator_id: str, *, platform: str) -> InventoryEmulator:
    """The inventory's row for *emulator_id* on *platform*, read through the domain parser."""
    try:
        document = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ProvisionError(f"cannot read {INVENTORY_PATH}: {exc}") from exc
    entry = parse_inventory(document).get(platform)
    for emulator in () if entry is None else entry.emulators:
        if emulator.emulator == emulator_id:
            return emulator
    raise ProvisionError(f"{INVENTORY_PATH} names no {emulator_id!r} emulator for {platform!r}")


def eden_candidates(*, home: Path) -> tuple[str, ...]:
    """Every Eden binary the inventory says can be installed, as paths on this device."""
    return tuple(str(_expand(candidate, home)) for candidate in _row(SWITCH_ID, platform=SWITCH_ROW).host_binaries)


def discover_flatpak(
    *, isfile: Callable[[str], bool] = os.path.isfile, which: Callable[[str], str | None] = shutil.which
) -> str | None:
    """The flatpak executable this device has, or ``None`` when there is none."""
    if isfile(FLATPAK_PATH):
        return FLATPAK_PATH
    return which("flatpak")


def discover_eden(*, home: Path, isfile: Callable[[str], bool] = os.path.isfile) -> str | None:
    """The first Eden binary the inventory names that exists under *home*, or ``None``."""
    return next((candidate for candidate in eden_candidates(home=home) if isfile(candidate)), None)


def resolve_hosts(*, home: Path) -> HostBinaries:
    """What this device has, asked once so a run states one answer per program."""
    return HostBinaries(
        flatpak=discover_flatpak(),
        eden=discover_eden(home=home),
        searched=eden_candidates(home=home),
    )


def dolphin_launch(flatpak: str) -> list[str]:
    """Dolphin's argv: the host-spawn form, running the flatpak *this* device has (ADR-0061).

    A managed argv is baked as a `standalone` invocation, which the shortcut layer wraps in
    `flatpak run net.retrodeck.retrodeck -e "<command>"`; RetroDECK's launcher then resolves
    `%EMULATOR_DOLPHIN%` to ITS Dolphin, and a device without RetroDECK execs nothing. The
    spawn form bakes bare argv, so the plugin's own Dolphin — the flatpak it installed — runs.
    `-C Core/GCIFolderAPath` is still the open question ADR-0034 records, so no save-path flag
    rides here and adopting a directory stays the only shape this script writes.
    """
    row = _row(DOLPHIN_ID, platform=DOLPHIN_ROW)
    if not row.flatpak:
        raise ProvisionError(f"{INVENTORY_PATH} states no flatpak id for {DOLPHIN_ID!r}")
    return ["%EMULATOR_FLATPAK-SPAWN%", "--host", flatpak, "run", row.flatpak, *row.host_args, "%ROM%"]


def switch_launch(eden: str) -> list[str]:
    """Eden's argv: the host form, so Steam's own environment (and display) reaches it.

    Measured: going through RetroDECK's sandbox instead produced audio with no picture.
    """
    return ["%EMULATOR_FLATPAK-SPAWN%", "--host", eden, *_row(SWITCH_ID, platform=SWITCH_ROW).host_args, "%ROM%"]


def _required_flatpak(hosts: HostBinaries) -> str:
    if hosts.flatpak is None:
        raise ProvisionError(
            f"no flatpak executable: {FLATPAK_PATH} is absent and `flatpak` is not on PATH, and a "
            "managed Dolphin launch runs the flatpak this device has"
        )
    return hosts.flatpak


def _required_eden(hosts: HostBinaries) -> str:
    if hosts.eden is None:
        searched = ", ".join(hosts.searched) or "the inventory's candidate paths"
        raise ProvisionError(
            f"no Eden binary at {searched} — install it from the plugin's Emulators & Cores, or "
            "provision Switch on the device that has it"
        )
    return hosts.eden

def existing_entries(root: Path) -> dict[str, dict]:
    """The managed entries an existing manifest already holds, or nothing.

    A run only states the platforms it was told about, and a platform it does not mention must
    keep the entry it has: measured on the reference Deck, re-running this script to adopt Wii
    dropped the Switch entry that was already there, and the plugin then answered Switch from
    the catalogue — which resolved a save folder under ``nand/user`` that Eden never writes.
    An unreadable file yields an empty mapping, which is exactly the state a first run is in.
    """
    path = root / MANIFEST_NAME
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(document, dict) or document.get("version") != MANIFEST_VERSION:
        return {}
    platforms = document.get("platforms")
    if not isinstance(platforms, dict):
        return {}
    return {key: value for key, value in platforms.items() if isinstance(value, dict)}


def build_manifest(
    root: Path,
    adopted: dict[str, str],
    *,
    kept: dict[str, dict] | None = None,
    hosts: HostBinaries | None = None,
) -> dict:
    """The manifest document this run would write, given what was adopted.

    *kept* is an existing manifest's entries: a platform this run does not name keeps the
    entry it already states, so adopting one platform can never unmanage another.

    *hosts* is what this device has. ``None`` asks the device itself (this user's home), and
    a platform whose program is missing raises :class:`ProvisionError` before anything is
    written — a launch line naming a binary that is not there is the failure ADR-0067 exists
    for, so it is never produced silently.
    """
    if hosts is None:
        hosts = resolve_hosts(home=Path(os.path.expanduser("~")))
    platforms: dict[str, dict] = dict(kept or {})
    for platform, directory in adopted.items():
        if platform in WII_PLATFORMS:
            # Dolphin files a Wii save as `Wii/title/<category>/<title id>/data`, and the title id
            # is the disc's four-character code in hex — read off the ROM, so it is a hole here.
            # Measured on the reference Deck: Mario Galaxy 2 (`SB4E01`) writes into
            # `Wii/title/00010000/53423445/data` with its `GameData.bin` beside `banner.bin`.
            platforms[platform] = {
                "emulator": "Dolphin (Standalone)",
                "launch": dolphin_launch(_required_flatpak(hosts)),
                "save_dir": f"{directory.rstrip('/')}/<save_id>/data",
                "save_unit": "title-dir",
                "needs": ["save_id"],
            }
            continue
        if platform in SWITCH_PLATFORMS:
            # Eden files a title's save under its own title id, so the adopted directory is
            # the SLOT (…/user/save/<user>/<slot>) and the id is the last segment. The id is
            # read off the ROM, which is why it is stated as a hole rather than a path part.
            platforms[platform] = {
                "emulator": "Eden (Standalone)",
                "launch": switch_launch(_required_eden(hosts)),
                "save_dir": f"{directory.rstrip('/')}/<save_id>",
                "save_unit": "title-dir",
                "needs": ["save_id"],
            }
            continue
        platforms[platform] = {
            "emulator": "Dolphin (Standalone)",
            "launch": dolphin_launch(_required_flatpak(hosts)),
            "save_dir": directory,
            "save_unit": "gci-set",
            "needs": ["region"],
        }
    return {"version": MANIFEST_VERSION, "root": str(root), "platforms": platforms}


def missing_subdirectories(root: Path) -> list[Path]:
    return [root / name for name in SUBDIRECTORIES if not (root / name).is_dir()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--root",
        default=None,
        help="the plugin data directory the layout is built inside (default: the plugin's own data root)",
    )
    parser.add_argument(
        "--home",
        default=os.path.expanduser("~"),
        help="the user home the inventory's `~/…` candidates and the default root are read against",
    )
    parser.add_argument(
        "--adopt",
        action="append",
        default=[],
        metavar="PLATFORM=SAVE_DIR",
        help="name an existing save directory as a managed platform's save path, instead of the owned one",
    )
    parser.add_argument("--check", action="store_true", help="verify the tree and the manifest, changing nothing")
    args = parser.parse_args(argv)

    home = Path(args.home).expanduser()
    root = Path(args.root).expanduser() if args.root else Path(data_root(str(home)))
    adopted: dict[str, str] = {}
    for item in args.adopt:
        platform, _, directory = item.partition("=")
        if not platform or not directory:
            parser.error(f"--adopt wants PLATFORM=SAVE_DIR, got {item!r}")
        if platform in GC_PLATFORMS or platform in SWITCH_PLATFORMS or platform in WII_PLATFORMS:
            adopted[platform] = directory
        else:
            parser.error(f"this cut provisions GameCube, Wii and Switch only; {platform!r} has no entry to write")

    try:
        hosts = resolve_hosts(home=home)
        # Built before anything is created, so a device missing a program changes nothing.
        document = build_manifest(root, adopted, kept=existing_entries(root), hosts=hosts)
    except ProvisionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        absent = missing_subdirectories(root)
        manifest_path = root / MANIFEST_NAME
        print(f"root: {root}")
        for path in [root / name for name in SUBDIRECTORIES]:
            print(f"  {'ok  ' if path.is_dir() else 'miss'} {path}")
        for label, found in (("flatpak", hosts.flatpak), ("eden", hosts.eden)):
            print(f"  {'ok  ' if found else 'miss'} {label}: {found or 'not found'}")
        if manifest_path.is_file():
            print(f"manifest: {manifest_path}")
            try:
                json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                print(f"  unusable: {exc}")
                return 1
        else:
            print(f"manifest: missing ({manifest_path})")
        return 0 if not absent else 1

    root.mkdir(parents=True, exist_ok=True)
    for name in SUBDIRECTORIES:
        (root / name).mkdir(exist_ok=True)
    # Written last, and atomically: a reader either sees the previous file or the new one.
    manifest_path = root / MANIFEST_NAME
    handle, tmp_name = tempfile.mkstemp(dir=root, prefix=".layout-", suffix=".json")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as tmp:
            json.dump(document, tmp, indent=2)
            tmp.write("\n")
        os.replace(tmp_name, manifest_path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    print(f"root: {root}")
    print(f"manifest: {manifest_path} ({len(document['platforms'])} managed platform(s))")
    for platform, directory in adopted.items():
        state = "exists" if Path(directory.replace("<region>", "USA")).parent.parent.parent.is_dir() else "MISSING"
        print(f"  {platform}: adopted {directory} ({state})")
        print(f"    launch: {' '.join(document['platforms'][platform]['launch'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
