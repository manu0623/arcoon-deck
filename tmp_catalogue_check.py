"""Ask the vendored catalogue the same two questions the plugin's save resolver asks."""

import sys

sys.path.insert(0, "/home/deck/homebrew/plugins/romm-tender/py_modules")

from adapters.atlas_catalogue import first_detected_installation  # noqa: E402

ROM = "/home/deck/Emulation/roms/gc/Legend of Zelda, The - Twilight Princess (USA).rvz"

installation = first_detected_installation("/home/deck")
print("installation:", type(installation).__name__ if installation is not None else None)
if installation is None:
    raise SystemExit("no installation detected")

answer = installation.emulators_for("gc", content_path=ROM)
print("labels:", [entry.label for entry in getattr(answer, "entries", ())])

for entry in getattr(answer, "entries", ()):
    placement = entry.savefile_location(content_path=ROM)
    print(f"{entry.label}: {placement!r}")
