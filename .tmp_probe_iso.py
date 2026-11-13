"""Step through the PSP identity walk against the real image."""

import logging
import sys

sys.path.insert(0, "/home/deck/homebrew/plugins/romm-tender/py_modules")

from adapters.content_identity import ContentIdentityAdapter  # noqa: E402
from domain.content_identity import iso9660_entry, iso9660_root_directory, psp_disc_id  # noqa: E402

PATH = "/home/deck/Emulation/roms/psp/Burnout Legends.iso"
SECTOR = 2048


def read(offset: int, size: int) -> bytes:
    with open(PATH, "rb") as handle:
        handle.seek(offset)
        return handle.read(size)


pvd = read(16 * SECTOR, SECTOR)
print("pvd magic:", pvd[0], pvd[1:6])
root = iso9660_root_directory(pvd)
print("root:", root)

if root is not None:
    lba, size = root
    blob = read(lba * SECTOR, size)
    print("root listing bytes:", len(blob))
    print("first record:", blob[0], blob[32:33], blob[33:40])
    game = iso9660_entry(blob, "PSP_GAME")
    print("PSP_GAME:", game)
    if game is not None:
        glba, gsize = game
        gblob = read(glba * SECTOR, gsize)
        sfo = iso9660_entry(gblob, "PARAM.SFO")
        print("PARAM.SFO:", sfo)
        if sfo is not None:
            slba, ssize = sfo
            payload = read(slba * SECTOR, ssize)
            print("sfo magic:", payload[:4], "size:", ssize)
            print("parsed:", psp_disc_id(payload))

adapter = ContentIdentityAdapter(logger=logging.getLogger("probe"))
print("adapter:", adapter(PATH, "psp"))
