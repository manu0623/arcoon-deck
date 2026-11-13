"""Read-only-ish probe: does a PSP save answer, download and land where PPSSPP reads?"""

import asyncio
import os
import sys
import types

sys.path.insert(0, "/home/deck/homebrew/plugins/romm-tender")
sys.path.insert(0, "/home/deck/homebrew/plugins/romm-tender/py_modules")

decky = types.ModuleType("decky")


class _L:
    def __getattr__(self, name):
        return lambda *a, **k: None


decky.logger = _L()
decky.DECKY_PLUGIN_DIR = "/home/deck/homebrew/plugins/romm-tender"
decky.DECKY_PLUGIN_RUNTIME_DIR = "/home/deck/homebrew/plugins/romm-tender/.runtime"
decky.DECKY_PLUGIN_SETTINGS_DIR = "/home/deck/homebrew/settings/romm-tender"
decky.DECKY_USER_HOME = "/home/deck"


async def _emit(*a, **k):
    return None


decky.emit = _emit
sys.modules["decky"] = types.SimpleNamespace(**{k: getattr(decky, k) for k in dir(decky) if not k.startswith("__")})

from main import Plugin  # noqa: E402

ROM = 5384
PSP_SAVEDATA = "/home/deck/.local/share/romm-tender/saves/psp/PSP/SAVEDATA"


def _tree(root: str, depth: int = 3) -> None:
    for parent, dirs, files in os.walk(root):
        level = parent[len(root) :].count(os.sep)
        if level >= depth:
            dirs[:] = []
        print("  " * level + os.path.basename(parent) + "/", len(files), "file(s)")


async def main() -> None:
    p = Plugin()
    await p._main()

    before = await p.get_save_status(ROM)
    res = before.get("save_resolution") or {}
    print("answer:", res.get("state"), "|", res.get("granularity"), "|", res.get("emulator"))
    print("directory:", res.get("directory"))
    print("names:", [c.get("name") for c in (res.get("components") or [])])
    print("local files:", [f["filename"] for f in before.get("files") or []])

    print("sync:", await p.pre_launch_sync(ROM))

    after = await p.get_save_status(ROM)
    print("local now:", [f["filename"] for f in after.get("files") or []])
    print("tree under SAVEDATA:")
    _tree(PSP_SAVEDATA)


asyncio.run(main())
