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
    ps3_title_id,
    psp_disc_id,
    rvz_gamecube_game_code,
    rvz_wii_game_code,
    wii_game_code,
)
from domain.switch_title_id import title_id_from_nsp

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

# The head a disc image is read through. A PS1/PS2 header often carries the boot line
# close enough to the front that one read answers, and the boot sector of a Dreamcast disc
# is one sector — so a megabyte of margin covers the images that do, without reading an
# image whole. It does NOT cover every PS2 disc: measured on the reference Deck,
# ``Burnout (USA).iso`` keeps its ``SYSTEM.CNF`` at sector 857 (1.75 MiB in), so the head
# alone answered nothing and every save the game wrote was refused. The ISO walk below is
# what answers for those, which is why a miss here is a fallback and not a refusal.
_DISC_HEAD_BYTES = 1 << 20
# ``SYSTEM.CNF`` is a handful of lines naming the boot executable; a page is margin.
_SYSTEM_CNF_MAX_BYTES = 1 << 12
# A consumer of these formats never needs more than a couple of sectors.
_SECTOR_HEAD_BYTES = 0x200
# The NCCH head is read from the partition, and its program id is at 0x118.
_NCCH_HEAD_BYTES = 0x200

# Platforms each reader answers for, in the spellings RomM, ES-DE and this plugin use.
_DISC_SERIAL_PLATFORMS = frozenset({"psx", "ps1", "ps2", "playstation", "playstation2"})
_GAMECUBE_PLATFORMS = frozenset({"gc", "ngc", "gamecube", "gcn"})
# Wii is its own reader: a Wii disc opens with `S<game><region>` where a GameCube boot file
# opens with `G`, so the same six bytes mean two different things.
_WII_PLATFORMS = frozenset({"wii"})
_DREAMCAST_PLATFORMS = frozenset({"dreamcast", "dc"})
_N3DS_PLATFORMS = frozenset({"n3ds", "3ds"})
_PSP_PLATFORMS = frozenset({"psp"})
_PS3_PLATFORMS = frozenset({"ps3"})
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
                return self._disc_serial(path)
            if slug in _PSP_PLATFORMS:
                return self._psp(path)
            if slug in _PS3_PLATFORMS:
                return self._ps3(path)
            if slug in _DREAMCAST_PLATFORMS:
                return dreamcast_product_number(self._read(path, 0, _SECTOR_HEAD_BYTES))
            if slug in _WII_PLATFORMS:
                head = self._read(path, 0, _SECTOR_HEAD_BYTES)
                # The container first, the bare disc second: a `.rvz` is not the disc, and
                # its header carries the id at the offset measured on the reference set.
                return rvz_wii_game_code(head) or wii_game_code(head)
            if slug in _GAMECUBE_PLATFORMS:
                head = self._read(path, 0, _SECTOR_HEAD_BYTES)
                # A `.rvz` is a container, not the disc: its own header carries the
                # disc id, so the container is asked first and the bare reading second.
                return rvz_gamecube_game_code(head) or gamecube_game_code(head)
        except OSError as exc:
            self._logger.warning(f"content_identity: cannot read {os.path.basename(path)}: {exc}")
            return None
        return None

    def _disc_serial(self, path: str) -> ContentIdentity | None:
        """The boot line, read from the image's head and then from its ``SYSTEM.CNF``.

        The head is tried first because on most discs the boot line is inside it, and one
        read is cheaper than a directory walk. When it is not — the measured Burnout image
        keeps ``SYSTEM.CNF`` at sector 857, past the head — the file's own directory says
        where the boot configuration is, so the walk the PSP and PS3 readers already use
        answers here too. A head-only reading is what left every PS2 save on that Deck
        refused as ``save_shape_unsupported``: no serial, so no card folder to name.
        """
        identity = disc_serial(self._read(path, 0, _DISC_HEAD_BYTES).decode("latin-1", errors="replace"))
        if identity is not None:
            return identity
        root = iso9660_root_directory(self._read(path, _ISO_PVD_OFFSET, _ISO_SECTOR))
        if root is None:
            return None
        cnf = self._iso_entry(path, root, "SYSTEM.CNF")
        if cnf is None:
            return None
        return disc_serial(
            self._read(path, cnf[0] * _ISO_SECTOR, min(cnf[1], _SYSTEM_CNF_MAX_BYTES)).decode(
                "latin-1", errors="replace"
            )
        )

    def _psp(self, path: str) -> ContentIdentity | None:
        """Three reads: the volume descriptor, two directory records, then the SFO.

        A PSP image is a plain ISO 9660 disc and the id lives in ``PSP_GAME/PARAM.SFO``,
        so the reader walks the directory tree the image itself describes. Every step
        refuses rather than guessing — a compressed image (``.cso``/``.zso``) is not
        addressable this way, and reading a "sector" out of a compressed stream would
        hand back bytes that mean nothing.
        """
        return self._iso_param_sfo(path, "PSP_GAME", psp_disc_id, "DISC_ID")

    def _ps3(self, path: str) -> ContentIdentity | None:
        """The same walk, one directory name over — unless the game is a folder on disk.

        A PS3 install is either a disc image or a directory whose ``PS3_GAME`` sits beside
        the boot file, and both keep the id in the same ``PARAM.SFO``. Measured on the
        reference Deck: the plugin's own PS3 installs are ``.iso`` files inside a folder
        of the same name, and a folder-boot install is the other shape it can take.
        """
        if os.path.isdir(path):
            parents = (path, os.path.dirname(path))
            for parent in parents:
                sfo_path = os.path.join(parent, "PS3_GAME", "PARAM.SFO")
                if not os.path.isfile(sfo_path):
                    continue
                with open(sfo_path, "rb") as handle:
                    identity = ps3_title_id(handle.read(_SFO_MAX_BYTES))
                if identity is None:
                    self._logger.warning(f"content_identity: no TITLE_ID in {os.path.basename(sfo_path)}")
                return identity
            self._logger.warning(f"content_identity: no PS3_GAME/PARAM.SFO beside {os.path.basename(path)}")
            return None
        return self._iso_param_sfo(path, "PS3_GAME", ps3_title_id, "TITLE_ID")

    def _iso_param_sfo(
        self, path: str, game_dir_name: str, parse: Callable[[bytes], ContentIdentity | None], key: str
    ) -> ContentIdentity | None:
        """Walk ``<game_dir_name>/PARAM.SFO`` in an ISO 9660 image and read *key* out of it."""
        root = iso9660_root_directory(self._read(path, _ISO_PVD_OFFSET, _ISO_SECTOR))
        if root is None:
            self._logger.warning(f"content_identity: no ISO 9660 volume descriptor in {os.path.basename(path)}")
            return None
        game_dir = self._iso_entry(path, root, game_dir_name)
        if game_dir is None:
            self._logger.warning(f"content_identity: no {game_dir_name} directory in {os.path.basename(path)}")
            return None
        sfo = self._iso_entry(path, game_dir, "PARAM.SFO")
        if sfo is None:
            self._logger.warning(f"content_identity: no {game_dir_name}/PARAM.SFO in {os.path.basename(path)}")
            return None
        identity = parse(self._read(path, sfo[0] * _ISO_SECTOR, min(sfo[1], _SFO_MAX_BYTES)))
        if identity is None:
            self._logger.warning(f"content_identity: no {key} in {os.path.basename(path)}")
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
