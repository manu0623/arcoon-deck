"""Where does the PSP answer lose its identity?"""

import asyncio
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

PATH = "/home/deck/Emulation/roms/psp/Burnout Legends.iso"


def _find_rom_info(obj: object, depth: int = 0, seen: set[int] | None = None):
    seen = seen or set()
    if depth > 4 or id(obj) in seen:
        return None
    seen.add(id(obj))
    if type(obj).__name__ == "RomInfoService":
        return obj
    for name in dir(obj):
        if name.startswith("__"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        if isinstance(value, (str, int, float, bytes, dict, list, tuple, set, type(None))):
            continue
        found = _find_rom_info(value, depth + 1, seen)
        if found is not None:
            return found
    return None


async def main() -> None:
    p = Plugin()
    await p._main()
    rom_info = _find_rom_info(p._save_sync_service)
    print("rom_info found:", rom_info is not None)
    if rom_info is None:
        return
    print("content_identity wired:", rom_info._content_identity is not None)
    print("save_bank_dir wired:", rom_info._save_bank_dir is not None)
    print("bank dir for psp:", rom_info._save_bank_dir("psp") if rom_info._save_bank_dir else None)
    print("identity:", rom_info._content_identity(PATH, "psp") if rom_info._content_identity else None)
    answer = rom_info.save_answer(5384)
    print("answer:", answer.state, answer.unestablished, answer.needs, answer.directory)
    print("names:", answer.synced_names)
    info = rom_info.get_rom_save_info(5384)
    print("info:", info)


asyncio.run(main())
