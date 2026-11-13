"""Where libretro cores come from, which ones are missing, and when a download is real.

A standalone runtime starts its own RetroArch, and that RetroArch can only load cores that
are on disk. On a Deck without RetroDECK there are none: every libretro row in the picker
reads ``not_installed`` and nothing can be launched. The plugin supplies them itself, from
the project's own build bot, into the runtime's cores directory.

Cores are downloaded, never trusted. A ``.so`` is code the plugin will hand to RetroArch,
so the archive is checked before it is written: the ZIP must open, every member must pass
its CRC, the member must be the core that was asked for, and its first bytes must be an ELF
header. A download that fails any of those is discarded and reported — a half-written core
in the cores directory is worse than a missing one, because the runtime will happily try to
load it.

What this verification is, and is not: the build bot publishes no per-file digest, so this
is structural verification (container integrity, identity, format) rather than a
cryptographic match against a published checksum. It catches a truncated or swapped
download and a corrupt mirror response; it does not prove upstream authenticity, and no
comment here should claim it does.

This module is pure: bytes in, verdict out. The network and the filesystem live in the
adapter that calls it.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

#: The libretro build bot's nightly tree, per host architecture. The Deck is x86_64; a
#: different machine needs a different prefix, which is why the base is a parameter.
BUILDBOT_NIGHTLY = "https://buildbot.libretro.com/nightly/linux/x86_64/latest"

#: Every ELF object starts with these four bytes. A libretro core is a shared object, so
#: this is the cheapest statement that the payload is the kind of thing that can load.
ELF_MAGIC = b"\x7fELF"

#: A libretro core is never a few bytes; anything this small is an error page or a stub.
MINIMUM_CORE_BYTES = 4096


@dataclass(frozen=True)
class CoreVerification:
    """The verdict on a downloaded archive, and the member inside it when it stands."""

    ok: bool
    reason: str | None = None
    member: bytes | None = None
    size: int = 0


def core_url(core_so: str, *, base: str = BUILDBOT_NIGHTLY) -> str:
    """The build-bot URL for a bare core name (``snes9x_libretro``)."""
    return f"{base}/{core_so}.so.zip"


def missing_cores(cores: Iterable[str], *, installed: Callable[[str], bool]) -> list[str]:
    """The cores worth downloading, in the order they were asked for, without repeats.

    Deduplicated because one core can back several inventory rows and several platforms
    (``mgba_libretro`` serves both gba and gbc), and downloading it twice is a wasted
    transfer that the second write then has to overwrite.
    """
    wanted: list[str] = []
    for core in cores:
        if not core or core in wanted:
            continue
        if not installed(core):
            wanted.append(core)
    return wanted


def verify_core_archive(data: bytes, *, core_so: str) -> CoreVerification:
    """Check a downloaded core archive and return the bytes of the core inside it.

    The order of the checks is the order of the costs: the container is opened once, the
    requested member is looked for by name, its CRC is verified by reading it, and the
    first bytes are inspected. A failure states which check refused it, because "the
    download failed" is not something a user can act on.
    """
    if not data:
        return CoreVerification(ok=False, reason="empty_download")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            name = _core_member(archive, core_so)
            if name is None:
                return CoreVerification(ok=False, reason="no_core_member")
            # Reading the member verifies its CRC against the central directory, which is
            # what catches a truncated transfer that still opened as a ZIP.
            try:
                payload = archive.read(name)
            except (zipfile.BadZipFile, OSError):
                return CoreVerification(ok=False, reason="corrupt_member")
    except (zipfile.BadZipFile, OSError):
        return CoreVerification(ok=False, reason="not_a_zip")
    if len(payload) < MINIMUM_CORE_BYTES:
        return CoreVerification(ok=False, reason="too_small")
    if not payload.startswith(ELF_MAGIC):
        return CoreVerification(ok=False, reason="not_elf")
    return CoreVerification(ok=True, member=payload, size=len(payload))


def _core_member(archive: zipfile.ZipFile, core_so: str) -> str | None:
    """The archive member holding *core_so*, or ``None`` when it is not there.

    The exact name is preferred; a build that nests the file (some archives ship it under
    a directory) is accepted only when exactly one member ends in the asked-for name, so a
    bundle carrying several cores can never be written under a name it does not own.
    """
    names = [info.filename for info in archive.infolist() if not info.is_dir()]
    expected = f"{core_so}.so"
    if expected in names:
        return expected
    matches = [name for name in names if name.endswith("/" + expected)]
    return matches[0] if len(matches) == 1 else None
