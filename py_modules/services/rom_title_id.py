"""Ask an installed PS3 game for its title id.

The parsing lives in ``domain.ps3_title_id`` so it can be tested against bytes; this
module is the part that opens the file the install row names. It is deliberately blind
to why the id is wanted — the save layer asks for it, the launch bake does not.
"""

from __future__ import annotations

import os

from domain.ps3_title_id import title_id_from_image, title_id_from_sfo

PS3_GAME = "PS3_GAME"
PARAM_SFO = "PARAM.SFO"


def ps3_title_id(file_path: str) -> str | None:
    """The title id a PS3 install states, whether it is a folder or an ISO.

    A folder-boot install keeps ``PS3_GAME/PARAM.SFO`` beside the boot file; an image
    keeps the same file inside an ISO9660 tree. Both are read, because a library can
    hold either and the id is the only thing the save folder is named after.
    """
    try:
        if os.path.isdir(file_path):
            sfo = os.path.join(file_path, PS3_GAME, PARAM_SFO)
            if not os.path.isfile(sfo):
                sfo = os.path.join(os.path.dirname(file_path), PS3_GAME, PARAM_SFO)
            if not os.path.isfile(sfo):
                return None
            with open(sfo, "rb") as handle:
                return title_id_from_sfo(handle.read())
        with open(file_path, "rb") as handle:

            def read_at(offset: int, length: int) -> bytes:
                handle.seek(offset)
                return handle.read(length)

            return title_id_from_image(read_at)
    except OSError:
        return None
