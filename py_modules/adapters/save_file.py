"""Filesystem adapter for local save file operations.

Owns the raw POSIX, ``open()``, ``tempfile``, and ``hashlib``-on-file
calls used by SaveService and its sub-services when reading, writing,
backing up, hashing, and removing local save files under the RetroDECK
saves directory. Path construction, platform-specific extension lookup,
and slot/sync policy remain a service or domain concern; this adapter
exposes only the I/O seams declared by
``services.protocols.SaveFileStore``.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import shutil
import tempfile
import zipfile
import zlib
from typing import TYPE_CHECKING

from adapters.descriptor_paths import claim_source, ensure_directory, rename_claimed
from domain.save_hash import combine_zip_entry_hashes

if TYPE_CHECKING:
    import logging
    from collections.abc import Iterator, Mapping

    from models.prune import MutationOutcome, SourceClaim

_MD5_CHUNK_SIZE = 8192

# Zip-decode failures a positive ``zipfile.is_zipfile`` sniff can still hit once
# the archive is actually read (the sniff only inspects the End-Of-Central-
# Directory record): a corrupt / truncated central directory or a bad entry CRC
# (``BadZipFile``), a compressed stream ``zlib`` cannot inflate (``zlib.error``),
# or an entry this runtime cannot decode — an encrypted member or a compression
# method the stdlib lacks (``RuntimeError``; the unknown-method
# ``NotImplementedError`` is a ``RuntimeError`` subclass, e.g. a save zipped with
# zstd, which ``zipfile`` only learns to read in 3.14). ``OSError`` is
# deliberately excluded so a genuine I/O fault (a vanished / unreadable file)
# still surfaces, matching the non-zip branch and ``checksum_md5``;
# ``LargeZipFile`` is excluded as an unreachable write-time ZIP64 guard.
_ZIP_READ_ERRORS = (zipfile.BadZipFile, zlib.error, RuntimeError)


class SaveFileAdapter:
    """Synchronous filesystem operations for local save files.

    Implements the ``SaveFileStore`` Protocol. Methods are
    synchronous — services that call from an async context offload via
    ``loop.run_in_executor``.
    """

    def __init__(self, *, logger: logging.Logger) -> None:
        self._logger = logger
        # Per-run content-hash memo, live only inside ``hash_memo_scope``.
        # ``None`` outside a scope so non-sync callers never populate a
        # process-lifetime cache; a fresh dict per outermost scope bounds it to
        # one sync run. Keyed ``(path, mtime_ns, size)`` so a save overwritten
        # mid-run (a download) re-hashes on its new stat instead of returning a
        # stale digest. ``_hash_memo_depth`` makes nested scopes share one memo.
        self._hash_memo: dict[tuple[str, int, int], str] | None = None
        self._hash_memo_depth = 0

    def exists(self, path: str) -> bool:
        """Return True when *path* refers to an existing file or directory."""
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        """Return True when *path* exists and is a regular file."""
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        """Return True when *path* exists and is a directory."""
        return os.path.isdir(path)

    def is_symlink(self, path: str) -> bool:
        return os.path.islink(path)

    def canonical_path(self, path: str) -> str:
        return os.path.realpath(path)

    def is_within(self, path: str, root: str) -> bool:
        try:
            return os.path.commonpath((os.path.realpath(path), os.path.realpath(root))) == os.path.realpath(root)
        except ValueError:
            return False

    def make_dirs(self, path: str) -> None:
        """Create *path* and any missing parents. Idempotent."""
        os.makedirs(path, exist_ok=True)

    def remove_file(self, path: str) -> None:
        """Delete *path*. Idempotent: a missing file is not an error."""
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)

    def listdir(self, directory: str) -> list[str]:
        """Return the entry names in *directory*; empty list if it does not exist."""
        try:
            return os.listdir(directory)
        except FileNotFoundError:
            return []

    def rename(self, src: str, dst: str) -> None:
        """Atomically rename *src* to *dst*, replacing any existing file at *dst*."""
        os.replace(src, dst)

    def list_archive(self, archive_path: str) -> tuple[str, ...]:
        """Return the regular-file member names of *archive_path*, in archive order.

        Used before a restore so every file about to be overwritten can be
        quarantined first (#965): the backup has to happen before the bytes move,
        and a caller cannot enumerate an archive without reading it.
        """
        with zipfile.ZipFile(archive_path, "r") as archive:
            return tuple(info.filename for info in archive.infolist() if not info.is_dir())

    def create_archive(self, archive_path: str, directory: str, names: list[str]) -> None:
        """Write *names* from *directory* into *archive_path*, members at the archive root.

        The counterpart of :meth:`extract_archive`, and the reason a per-title folder can
        be carried at all: RomM holds a Switch save as ONE zip named after the ROM, so the
        emulator's folder has to become that archive before it is compared or uploaded.
        Members go in flat, exactly as ``extract_archive`` places them back.

        Written through a ``.tmp`` and renamed, so a sync never reads a half-written
        archive, and created last-writer-wins: the folder is the truth and the archive is
        derived from it on every sync.
        """
        if not names:
            return
        os.makedirs(os.path.dirname(archive_path) or ".", exist_ok=True)
        tmp_path = archive_path + ".tmp"
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in names:
                source = os.path.join(directory, name)
                if os.path.isdir(source):
                    # A member that is a folder (a PSP save is ``<DISC_ID>DATA00`` beside
                    # ``<DISC_ID>SETTINGS``) ships its tree: writing the directory entry
                    # alone would archive two empty names and restore nothing.
                    for parent, _dirs, files in os.walk(source):
                        for file_name in files:
                            path = os.path.join(parent, file_name)
                            archive.write(path, arcname=os.path.relpath(path, directory))
                    continue
                archive.write(source, arcname=name)
        os.replace(tmp_path, archive_path)

    def extract_archive(
        self, archive_path: str, dest_dir: str, *, placements: Mapping[str, str] | None = None
    ) -> tuple[str, ...]:
        """Extract *archive_path*'s regular files into *dest_dir*; return their names.

        The archive arrives from a server, so its member names are untrusted
        input: a member that would land outside *dest_dir* (an absolute name or
        one climbing with ``..``) is refused rather than written, and so is one
        whose target is a symlink — writing through a link would put save bytes
        anywhere on the device. Directories are created as needed.

        *placements* maps each member this save owns to the name it takes under *dest_dir*,
        for an archive that was packed above the destination or carries more than the save
        (ADR-0066). A member with no placement is not written at all — an over-packed archive
        carries the emulator's own files, and those are not this save's to replace.
        """
        real_dest = os.path.realpath(dest_dir)
        written: list[str] = []
        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                if placements is not None:
                    if name not in placements:
                        continue
                    name = placements[name]
                target = os.path.realpath(os.path.join(real_dest, name))
                if target != real_dest and not target.startswith(real_dest + os.sep):
                    raise ValueError(f"ZIP member {info.filename!r} would extract outside {dest_dir!r}")
                if os.path.islink(target):
                    raise ValueError(f"ZIP member {info.filename!r} would extract through a symlink")
                parent = os.path.dirname(target)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with archive.open(info) as source, open(target, "wb") as destination:
                    shutil.copyfileobj(source, destination)
                written.append(name)
        return tuple(written)

    def claim_source(self, path: str, safe_root: str) -> SourceClaim:
        return claim_source(path, safe_root)

    def ensure_directory(self, path: str, safe_root: str) -> None:
        ensure_directory(path, safe_root)

    def rename_claimed(self, src: str, dst: str, safe_root: str, claim: SourceClaim) -> MutationOutcome:
        return rename_claimed(src, dst, safe_root, claim)

    def get_mtime(self, path: str) -> float:
        """Return the mtime of *path* as a Unix timestamp."""
        return os.path.getmtime(path)

    def get_size(self, path: str) -> int:
        """Return the size of *path* in bytes."""
        return os.path.getsize(path)

    def checksum_md5(self, path: str) -> str:
        """Return the hex-encoded MD5 digest of *path*'s contents.

        Streams the file in fixed-size chunks so memory use stays
        bounded for large save files. Non-security use: MD5 here is the
        drift baseline that ``compute_sync_action`` compares against
        ``last_sync_hash`` to decide whether a local save changed since
        the last sync. ``usedforsecurity=False`` documents this and
        silences Sonar S4790.
        """
        h = hashlib.md5(usedforsecurity=False)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(_MD5_CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest()

    def content_hash(self, path: str) -> str:
        """Return RomM's content hash for *path* — zip-aware, MD5-based.

        Matches the server's ``compute_content_hash`` so a save's local and
        server hashes agree and save-sync converges. Dispatch mirrors RomM
        exactly: a file that *is* a zip archive (``zipfile.is_zipfile`` — a
        content sniff, not the extension) is hashed per entry and combined via
        :func:`domain.save_hash.combine_zip_entry_hashes`; any other file is the
        plain streamed MD5 of :meth:`checksum_md5`. Directory entries inside the
        archive are skipped. A positive sniff over a file that cannot be read as
        a zip falls back to the plain MD5 rather than raising (see
        :meth:`_compute_content_hash`). Non-security use, like ``checksum_md5``.

        Inside a :meth:`hash_memo_scope` the digest is memoized by the file's
        ``(path, mtime_ns, size)`` so one sync run's repeated hashings of the
        same save (negotiate inventory, the newest-wins matrix, the post-op
        baseline write) read it once. Outside a scope every call reads the file.
        """
        memo = self._hash_memo
        if memo is None:
            return self._compute_content_hash(path)
        st = os.stat(path)
        key = (path, st.st_mtime_ns, st.st_size)
        cached = memo.get(key)
        if cached is not None:
            return cached
        digest = self._compute_content_hash(path)
        memo[key] = digest
        return digest

    def _compute_content_hash(self, path: str) -> str:
        """Read *path* and compute its zip-aware RomM content hash (no memo).

        A file that ``zipfile.is_zipfile`` accepts but that cannot be read as a
        zip (``_ZIP_READ_ERRORS``) falls back to the plain streamed MD5 of
        :meth:`checksum_md5`. RomM's server degrades the same file to
        ``content_hash=None``, so the kernel's truthiness guards reject a
        ``None``-side identity match and the fallback can never manufacture a
        false byte-identical match — it only keeps the local drift baseline
        working. Both sides of the memo see the fallback value: the public
        :meth:`content_hash` memoizes whatever this method returns under the
        file's stat key.
        """
        if not zipfile.is_zipfile(path):
            return self.checksum_md5(path)
        try:
            with zipfile.ZipFile(path, "r") as zf:
                entries = [
                    (name, hashlib.md5(zf.read(name), usedforsecurity=False).hexdigest())
                    for name in zf.namelist()
                    if not name.endswith("/")
                ]
        except _ZIP_READ_ERRORS as exc:
            self._logger.debug("content_hash: %s sniffed as zip but unreadable (%s); MD5 fallback", path, exc)
            return self.checksum_md5(path)
        return combine_zip_entry_hashes(entries)

    @contextlib.contextmanager
    def hash_memo_scope(self) -> Iterator[None]:
        """Bound a :meth:`content_hash` memo to a single sync run.

        Within the scope, ``content_hash`` caches each save's digest keyed by
        ``(path, mtime_ns, size)`` so the several passes of one run that hash the
        same file read it once. The memo is discarded when the outermost scope
        exits, so it is never a process-lifetime cache; a file overwritten
        mid-run gets a new stat key and re-hashes. Reentrant — nested scopes
        share one memo and only the outermost clears it — so the engine can open
        it at both the sweep and per-ROM levels. The engine opens exactly one
        (outermost) scope per device-gated save-sync run, so within-scope hashing
        is single-threaded; callers outside a scope hash directly and never touch
        the memo.
        """
        self._hash_memo_depth += 1
        if self._hash_memo is None:
            self._hash_memo = {}
        try:
            yield
        finally:
            self._hash_memo_depth -= 1
            if self._hash_memo_depth == 0:
                self._hash_memo = None

    def make_temp_path(self, suffix: str = "") -> str:
        """Return a fresh, unique path safe to write to.

        Backed by ``tempfile.mkstemp`` so the file is created atomically
        (``O_EXCL``) before the fd is closed. The caller owns the file
        and is responsible for removing it.
        """
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        return path

    def read_bytes(self, path: str) -> bytes:
        """Return the contents of *path* as raw bytes."""
        with open(path, "rb") as f:
            return f.read()
