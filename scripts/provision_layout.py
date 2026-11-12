#!/usr/bin/env python3
"""Provision the plugin-owned layout and write the manifest it describes (ADR-0034).

This is the first half of the two-part app: the part that decides where things live. The
plugin is the second half — it reads `layout.json`, bakes each managed platform's launch
from it, and answers that platform's save question from the same entry.

Usage, on the Deck, once:

    python3 scripts/provision_layout.py --check                       # change nothing
    python3 scripts/provision_layout.py \\
        --adopt gc=/home/deck/retrodeck/saves/gc/User/GC/<region>/Card A

Why `--adopt`: a save that already exists must not have to move for this to help. Adoption
is an explicit manifest entry naming the directory the save is in today, which is the whole
reason it is a flag rather than a rule — the script does not go looking for saves, and
nothing here guesses where an emulator keeps them.

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
import sys
import tempfile
from pathlib import Path

# Run from a checkout or from inside the installed plugin, this script has to agree with the
# plugin about where the data directory is — so it asks the same domain function instead of
# spelling the path a second time. Getting this wrong is not a broken run, it is a manifest
# the plugin never reads.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py_modules"))

from domain.user_data_location import data_root  # noqa: E402

MANIFEST_NAME = "layout.json"
MANIFEST_VERSION = 1
SUBDIRECTORIES = ("library", "cores", "saves", "bios", "art", "mods", "cache")
GC_PLATFORMS = ("gc", "ngc")

# The launch this cut bakes for GameCube, with the save path it implies. The emulator token
# and `%ROM%` stay placeholders: RetroDECK's launcher resolves them, exactly as it did before
# this script existed. `-C Core/GCIFolderAPath` is the measured question ADR-0034 records as
# open; until it is answered, adopting a directory is the only shape this script writes.
GC_LAUNCH = ["%EMULATOR_DOLPHIN%", "-b", "-e", "%ROM%"]


def build_manifest(root: Path, adopted: dict[str, str]) -> dict:
    """The manifest document this run would write, given what was adopted."""
    platforms = {
        platform: {
            "emulator": "Dolphin (Standalone)",
            "launch": list(GC_LAUNCH),
            "save_dir": directory,
            "save_unit": "gci-set",
            "needs": ["region"],
        }
        for platform, directory in adopted.items()
    }
    return {"version": MANIFEST_VERSION, "root": str(root), "platforms": platforms}


def missing_subdirectories(root: Path) -> list[Path]:
    return [root / name for name in SUBDIRECTORIES if not (root / name).is_dir()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--root",
        default=data_root(os.path.expanduser("~")),
        help="the plugin data directory the layout is built inside (default: the plugin's own data root)",
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

    root = Path(args.root).expanduser()
    adopted: dict[str, str] = {}
    for item in args.adopt:
        platform, _, directory = item.partition("=")
        if not platform or not directory:
            parser.error(f"--adopt wants PLATFORM=SAVE_DIR, got {item!r}")
        if platform in GC_PLATFORMS:
            adopted[platform] = directory
        else:
            parser.error(f"this cut provisions GameCube only; {platform!r} has no entry to write")

    if args.check:
        absent = missing_subdirectories(root)
        manifest_path = root / MANIFEST_NAME
        print(f"root: {root}")
        for path in [root / name for name in SUBDIRECTORIES]:
            print(f"  {'ok  ' if path.is_dir() else 'miss'} {path}")
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
    document = build_manifest(root, adopted)
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
    print(f"manifest: {manifest_path} ({len(adopted)} managed platform(s))")
    for platform, directory in adopted.items():
        state = "exists" if Path(directory.replace("<region>", "USA")).parent.parent.parent.is_dir() else "MISSING"
        print(f"  {platform}: adopted {directory} ({state})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
