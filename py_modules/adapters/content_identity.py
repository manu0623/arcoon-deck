"""Reading a content file's own identity off disk, bounded and per platform.

The parsers in :mod:`domain.content_identity` take bytes; this adapter decides which
bytes. Every read is bounded by the format's own layout — a header excerpt, a boot
sector, the first megabyte of an ISO where ``SYSTEM.CNF`` lives — so identifying a 2 GiB
cart image costs two small reads rather than a scan of the file.

Nothing here is fatal. A file that cannot be opened, a platform with no reader, a header
that does not carry the expected magic: all of them return ``None``, which the caller
reads as "this save has no derivable id" and reports as such. That is deliberately the
same answer a refused format gives, because from the save bank's point of view they are
the same situation: no id, so no path it could honestly build.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from domain.content_identity import (
    ContentIdentity,
    IdentityKind,
    disc_serial,
    dreamcast_product_number,
    gamecube_game_code,
    iso9660_entry,
    iso9660_root_directory,
    n3ds_partition_offset,
    n3ds_title_id,
    psp_disc_id,
    rvz_gamecube_game_code,
)
from domain.switch_title_id import title_id_from_nsp

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

# The head a disc image is read through. SYSTEM.CNF sits a few sectors into the ISO —
# sector 16 is the primary volume descriptor, the directory records follow it — so a
# megabyte of margin covers the layouts seen in practice without reading an image whole.
_DISC_HEAD_BYTES = 1 << 20
# A consumer of these formats never needs more than a couple of sectors.
_SECTOR_HEAD_BYTES = 0x200
# The NCCH head is read from the partition, and its program id is at 0x118.
_NCCH_HEAD_BYTES = 0x200

# Platforms each reader answers for, in the spellings RomM, ES-DE and this plugin use.
_DISC_SERIAL_PLATFORMS = frozenset({"psx", "ps1", "ps2", "playstation", "playstation2"})
_GAMECUBE_PLATFORMS = frozenset({"gc", "ngc", "gamecube", "gcn"})
_DREAMCAST_PLATFORMS = frozenset({"dreamcast", "dc"})
_N3DS_PLATFORMS = frozenset({"n3ds", "3ds"})
_PSP_PLATFORMS = frozenset({"psp"})
_SWITCH_PLATFORMS = frozenset({"switch", "nsw"})
# An ``.nsp`` keeps its ticket list in the PFS0 header's string table, which sits in the
# first few kilobytes; 64 KiB is margin, not a scan.
_NSP_HEAD_BYTES = 0x10000
# ISO 9660, for the PSP disc id: one sector for the volume descriptor, whole directories
# for the two records the walk reads, and one file for the SFO. Every bound is a real
# limit rather than a scan — a PSP_GAME directory listing is a few sectors, and a
# PARAM.SFO is a few hundred bytes.
_ISO_SECTOR = 2048
_ISO_PVD_OFFSET = 16 * _ISO_SECTOR
_ISO_DIRECTORY_MAX = 1 << 16
_SFO_MAX_BYTES = 1 << 16


class ContentIdentityAdapter:
    """Resolve the identity of one content file for one platform."""

    def __init__(self, *, logger: logging.Logger, reader: Callable[[str, int, int], bytes] | None = None) -> None:
        self._logger = logger
        # Injectable so the adapter can be exercised without real files, and so a future
        # caller can read through an existing file handle rather than opening twice.
        self._read = reader if reader is not None else _read_head

    def __call__(self, path: str, platform: str) -> ContentIdentity | None:
        """The identity *path* states on *platform*, or ``None`` when nothing reads.

        The platform decides the reader rather than the file extension: an ``.iso`` can
        be a PS1, PS2 or GameCube image, and only the caller knows which system it was
        installed for. A wrong reader refuses on its magic instead of returning a
        plausible-looking id from the wrong offset.
        """
        slug = platform.strip().lower()
        try:
            if slug in _N3DS_PLATFORMS:
                return self._n3ds(path)
            if slug in _SWITCH_PLATFORMS:
                return self._switch(path)
            if slug in _DISC_SERIAL_PLATFORMS:
                return disc_serial(self._read(path, 0, _DISC_HEAD_BYTES).decode("latin-1", errors="replace"))
            if slug in _PSP_PLATFORMS:
                return self._psp(path)
            if slug in _DREAMCAST_PLATFORMS:
                return dreamcast_product_number(self._read(path, 0, _SECTOR_HEAD_BYTES))
            if slug in _GAMECUBE_PLATFORMS:
                head = self._read(path, 0, _SECTOR_HEAD_BYTES)
                # A `.rvz` is a container, not the disc: its own header carries the
                # disc id, so the container is asked first and the bare reading second.
                return rvz_gamecube_game_code(head) or gamecube_game_code(head)
        except OSError as exc:
            self._logger.warning(f"content_identity: cannot read {os.path.basename(path)}: {exc}")
            return None
        return None

    def _psp(self, path: str) -> ContentIdentity | None:
        """Three reads: the volume descriptor, two directory records, then the SFO.

        A PSP image is a plain ISO 9660 disc and the id lives in ``PSP_GAME/PARAM.SFO``,
        so the reader walks the directory tree the image itself describes. Every step
        refuses rather than guessing — a compressed image (``.cso``/``.zso``) is not
        addressable this way, and reading a "sector" out of a compressed stream would
        hand back bytes that mean nothing.
        """
        root = iso9660_root_directory(self._read(path, _ISO_PVD_OFFSET, _ISO_SECTOR))
        if root is None:
            self._logger.warning(f"content_identity: no ISO 9660 volume descriptor in {os.path.basename(path)}")
            return None
        game_dir = self._iso_entry(path, root, "PSP_GAME")
        if game_dir is None:
            self._logger.warning(f"content_identity: no PSP_GAME directory in {os.path.basename(path)}")
            return None
        sfo = self._iso_entry(path, game_dir, "PARAM.SFO")
        if sfo is None:
            self._logger.warning(f"content_identity: no PSP_GAME/PARAM.SFO in {os.path.basename(path)}")
            return None
        identity = psp_disc_id(self._read(path, sfo[0] * _ISO_SECTOR, min(sfo[1], _SFO_MAX_BYTES)))
        if identity is None:
            self._logger.warning(f"content_identity: no DISC_ID in {os.path.basename(path)}")
        return identity

    def _iso_entry(self, path: str, extent: tuple[int, int], name: str) -> tuple[int, int] | None:
        """One directory record inside *extent*, read from the image it describes."""
        lba, size = extent
        if size <= 0 or size > _ISO_DIRECTORY_MAX:
            return None
        return iso9660_entry(self._read(path, lba * _ISO_SECTOR, size), name)

    def _switch(self, path: str) -> ContentIdentity | None:
        """One bounded read: a PFS0 head, whose ticket names carry the title id.

        A ``.xci`` is a different container — its root is a partition table with no ticket
        list — so it answers ``None`` rather than an id read from the wrong offset. Measured
        on the reference Deck: the ``.nsp`` for Link's Awakening states ``01006BB00C6F0000``,
        the same id Eden logged when it booted that file.
        """
        title = title_id_from_nsp(self._read(path, 0, _NSP_HEAD_BYTES))
        if title is None:
            self._logger.warning(f"content_identity: no Switch title id in {os.path.basename(path)}")
            return None
        return ContentIdentity(save_id=title, kind=IdentityKind.SWITCH_TITLE_ID, source="Switch NSP ticket")

    def _n3ds(self, path: str) -> ContentIdentity | None:
        """Two reads: the NCSD header, then the NCCH the first partition points at.

        A bare NCCH (``.cxi``/``.app``) is tried directly when the NCSD magic is absent,
        so both shapes of 3DS content answer without the caller telling them apart.
        """
        head = self._read(path, 0, _NCCH_HEAD_BYTES)
        offset = n3ds_partition_offset(head)
        if offset is None:
            return n3ds_title_id(head)
        identity = n3ds_title_id(self._read(path, offset, _NCCH_HEAD_BYTES))
        if identity is None:
            self._logger.warning(f"content_identity: no 3DS title id at 0x{offset:x} in {os.path.basename(path)}")
        return identity


def _read_head(path: str, offset: int, size: int) -> bytes:
    """Read at most *size* bytes from *offset*, returning what exists.

    A short file is not an error: the parsers refuse on their own magic and length
    checks, and returning the short read keeps that decision in one place.
    """
    with open(path, "rb") as handle:
        handle.seek(offset)
        return handle.read(size)
