"""Per-ROM save path resolution and local save-file discovery.

Resolves the on-disk save directory for an installed ROM (honouring
RetroArch's ``sort_savefiles_*`` settings and the optional per-core
subdirectory) and enumerates the matching local save files. Pure
filesystem + path-algebra responsibility — no RomM I/O, no state
mutation. Shared by SlotsService, SyncEngine, and StatusService; reads
about whether a save-sort migration is pending live here too because
they share ``_get_rom_save_info``'s decision to honour the previous
layout while a migration is in flight.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from domain.content_identity import save_id_text
from domain.save_answer import (
    SAVE_ID_NEED,
    SAVE_REGION_NEED,
    UNESTABLISHED_NOT_ASKED,
    fill_directory_members,
    fill_gci_set,
    fill_region,
    fill_save_id,
    manifest_answer,
    owned_dolphin_answer,
    owned_libretro_answer,
    unestablished_answer,
)
from domain.save_bank import canonical_platform, restores_by_extraction
from domain.save_layout import InSaveDir
from domain.save_path import resolve_save_dir

# kv_config keys for the cross-run save-sort markers MigrationService writes
# (ADR-0003 Bucket 2): the last-seen observation and the pending pre-change
# snapshot. RomInfoService reads them to honour the previous save layout while
# a save-sort migration is in flight (#238).
_KV_SAVE_SORT = "save_sort_settings"
_KV_SAVE_SORT_PREVIOUS = "save_sort_settings_previous"

if TYPE_CHECKING:
    import logging

    from models.state import SaveSortSettings

    from domain.content_identity import ContentIdentity
    from domain.save_answer import SaveAnswer
    from services.protocols import (
        ActiveCoreReader,
        ContentIdentityFn,
        CoreNameProviderFn,
        RetroDeckPaths,
        SaveBankDirFn,
        SaveFileStore,
        SaveLocationReader,
        SystemResolver,
        UnitOfWorkFactory,
    )


#: Where an archive-carried unit is staged: a dot directory beside the title folder. It
#: cannot live inside the folder it archives, and a dot directory is one no emulator scans.
PACKED_ARCHIVE_DIR_NAME = ".arcoon-archive"


@dataclass(frozen=True)
class PackedSaveUnit:
    """A save RomM carries as ONE archive, packed from a folder that stays the truth.

    ``archive_dir`` is where the zip is written and read from, ``archive_name`` is the
    single filename the sync compares and uploads, and ``source_dir`` is the folder the
    archive was packed from — where a download is extracted back into.
    """

    archive_dir: str
    archive_name: str
    source_dir: str


@dataclass(frozen=True)
class RomInfoServiceConfig:
    """Frozen wiring bundle handed to ``RomInfoService.__init__``.

    Holds the Unit-of-Work factory (the ``rom_installs`` aggregate is the
    source of truth for installed-ROM file records — WS3 — and ``kv_config``
    holds the save-sort markers), the Protocol-typed filesystem adapter, the
    RetroDECK runtime-path accessor, the per-ROM active-core resolver, the
    save-location reader that answers what a game's save consists of, the
    platform-slug-to-system resolver (which, with ``roms.fs_name``, builds the
    path a ROM the library knows but has not installed WOULD occupy — a save
    answer turns on the content file's extension, so omitting the path asks a
    different question), the RetroArch core-name provider, and the
    standard-library logger.
    """

    uow_factory: UnitOfWorkFactory
    save_file_store: SaveFileStore
    retrodeck_paths: RetroDeckPaths
    active_core: ActiveCoreReader
    save_locations: SaveLocationReader
    resolve_system: SystemResolver
    get_core_name: CoreNameProviderFn
    logger: logging.Logger
    # Optional: reads a game's own identity out of its content file, so the resolver's
    # ``<save_id>`` hole can be filled instead of refused. ``None`` keeps every answer a
    # hole exactly as it was.
    content_identity: ContentIdentityFn | None = None
    # Optional: the plugin's own save directory for a platform, when ``save_bank`` is on.
    # It answers the SAME directory the generated appendconfig redirects a launch into, so
    # the two cannot disagree. ``None`` keeps the RetroArch-shaped path math unchanged.
    save_bank_dir: SaveBankDirFn | None = None


class RomInfoService:
    """Resolves per-ROM save paths and discovers local save files on disk."""

    def __init__(self, *, config: RomInfoServiceConfig) -> None:
        self._config = config
        self._uow_factory = config.uow_factory
        self._save_file_store = config.save_file_store
        self._retrodeck_paths = config.retrodeck_paths
        self._active_core = config.active_core
        self._save_locations = config.save_locations
        self._resolve_system = config.resolve_system
        self._get_core_name = config.get_core_name
        self._logger = config.logger
        self._content_identity = config.content_identity
        self._save_bank_dir = config.save_bank_dir

    def get_rom_save_info(self, rom_id: int) -> dict[str, Any] | None:
        """Get save-related info for an installed ROM.

        Returns dict with keys: system, rom_name, saves_dir, platform_slug, file_path
        or None if not installed.
        """
        with self._uow_factory() as uow:
            installed = uow.rom_installs.get(int(rom_id))
        if not installed:
            return None
        system = installed.system
        file_path = installed.file_path
        platform_slug = installed.platform_slug
        if not system or not file_path:
            return None
        rom_name = os.path.splitext(os.path.basename(file_path))[0]

        saves_base = self._retrodeck_paths.saves_path()
        roms_base = self._retrodeck_paths.roms_path()
        sorting = self.current_save_sorting()
        sort_by_content = sorting.sort_by_content
        sort_by_core = sorting.sort_by_core

        # When sort-by-core is active, RetroArch writes per-core subdirs named
        # by the .info ``corename`` field. Resolve it via the dedicated parser.
        # See docs: Config-Source-Parsers wiki page ("one parser per source").
        # Decision: warn-and-fallback (not fail-loud like MigrationService).
        # SaveService is the critical-path sync flow — every game launch
        # depends on it. Fail-loud would take down save sync entirely on any
        # .info hiccup. MigrationService can afford strictness (one-shot),
        # SaveService cannot (continuous). See issue #232 for history.
        core_name: str | None = None
        if sort_by_core:
            rom_filename = os.path.basename(file_path)
            core_name, core_so = self.resolve_retroarch_corename(int(rom_id))
            if core_name is None:
                self._logger.warning(
                    "SaveService: unable to resolve RetroArch corename for "
                    "%s/%s (core_so=%s) while sort_by_core is enabled. "
                    "Falling back to the parent save directory, which will "
                    "not match what RetroArch reads at runtime. Check that "
                    "the core's .info file is readable under the RetroDECK "
                    "Flatpak cores directory.",
                    system,
                    rom_filename,
                    core_so if core_so else "unresolved",
                )

        # The bank wins where it answers, and it answers only when the launch is being
        # redirected into it: this is the second half of one switch, never a second
        # opinion (see ``adapters.save_bank_dir``).
        bank_dir = self._save_bank_dir(platform_slug) if self._save_bank_dir is not None else None
        saves_dir = bank_dir or resolve_save_dir(
            file_path,
            saves_base,
            system,
            roms_base=roms_base,
            sort_by_content=sort_by_content,
            sort_by_core=sort_by_core,
            core_name=core_name,
        )

        return {
            "system": system,
            "rom_name": rom_name,
            "saves_dir": saves_dir,
            "platform_slug": platform_slug,
            "file_path": file_path,
        }

    def is_content_installed(self, rom_id: int) -> bool:
        """Whether this ROM's content is on disk, without resolving where its saves go.

        The same install-row question :meth:`get_rom_save_info` asks first, minus
        the save-directory math behind it — which under ``sort_by_core`` parses a
        core's ``.info`` file. Callers that need only ``content_installed`` for a
        :class:`~domain.save_answer.SaveAnswer` they fabricate themselves ask
        here, so stating an honest install state costs one row read.
        """
        with self._uow_factory() as uow:
            installed = uow.rom_installs.get(int(rom_id))
        return bool(installed and installed.system and installed.file_path)

    def current_save_sorting(self) -> InSaveDir:
        """The subdirectory sorting savefile paths are resolved with right now.

        The single answer to "which savefile layout is current", so every caller
        that has to address a save on disk addresses the same directory. It comes
        from the markers MigrationService records, never from the live
        ``retroarch.cfg``: while a save-sort migration is pending the *previous*
        layout wins, because RetroArch caches its runtime save-path at game-load
        time and the session that just ended still wrote to the old directory.
        Reading the live config here would point every caller at a directory the
        files have not reached yet (#238).

        Falls back to the RetroDECK defaults when nothing has been observed yet.
        Answers only the **sorting**: whether savefiles live under the saves root
        at all is ``savefiles_in_content_dir``, which is a live-config fact with
        no recorded counterpart — MigrationService never writes these markers for
        a ``ContentDir`` machine.
        """
        recorded = self.pending_sort_settings() or self._read_current_sort_settings()
        if not recorded:
            return InSaveDir(sort_by_content=True, sort_by_core=False)
        return InSaveDir(
            sort_by_content=recorded.get("sort_by_content", True),
            sort_by_core=recorded.get("sort_by_core", False),
        )

    def resolve_retroarch_corename(self, rom_id: int) -> tuple[str | None, str | None]:
        """Resolve the RetroArch ``corename`` for a ROM by ``rom_id``.

        Asks the per-ROM ``ActiveCoreReader`` **which** core is active for
        this ROM (the per-game ``emulator_override`` pin folded over the
        system default), then asks the RetroArch ``.info`` parser (via
        ``get_core_name``) **what** RetroArch calls that core in its own
        subsystem — which is the authoritative name used for per-core save
        subdirectories when ``sort_savefiles_enable`` is active.

        One parser per source: the ES-DE label (second element of the
        resolver tuple) is NOT a valid substitute for the RetroArch
        corename. See the Config-Source-Parsers wiki page and the reference
        implementation in ``MigrationService``.

        Returns ``(corename, core_so)``. Either element may be ``None``
        when resolution fails at that step: ``core_so`` is ``None`` when
        the resolver cannot determine the active core, ``corename`` is
        ``None`` when ``.info`` parsing returns nothing. Returning the tuple —
        rather than just ``corename`` — lets callers include ``core_so``
        in diagnostic logs so users can identify which ``.info`` file
        is at fault. Callers choose their own fallback strategy (e.g.
        warn and fall back for critical-path SaveService flows; skip
        and warn for one-shot migrations).
        """
        core_so, _label = self._active_core.active_core_for_rom(rom_id)
        if not core_so:
            return (None, None)
        corename = self._get_core_name(core_so)
        return (corename or None, core_so)

    def save_answer(self, rom_id: int) -> SaveAnswer:
        """What this ROM's save consists of and whether it may be synced at all.

        Read live off the machine on every call, through the emulator this ROM
        would launch with, and always against the ROM's own content path — the
        answer turns on the content file's EXTENSION, so it is a property of the
        ROM and never of its platform. On this machine PUAE answers
        ``save-inside-content`` for an Amiga ``.adf`` and states nothing at all
        for an ``.hdf``, and Genesis Plus GX answers a shared ``scd_*.brm`` for a
        Sega CD ``.chd`` and a per-game ``.srm`` for a ``.bin``. Asking without
        the real path would answer a different question and look like an answer
        to this one.

        An installed ROM is asked about its ``file_path``; a ROM the library
        knows but has not installed is asked about the path it WOULD occupy,
        built from ``roms.fs_name``. Where no path can be formed at all — no
        row, no name, no platform — the answer is ``unestablished``, which is a
        refusal and never a guess.
        """
        info = self.get_rom_save_info(rom_id)
        if info:
            return self._installed_answer(rom_id, info)
        return self._uninstalled_answer(rom_id)

    def _uninstalled_answer(self, rom_id: int) -> SaveAnswer:
        """The answer for a ROM the library holds but the disk does not.

        Its ``fs_name`` carries the extension the answer turns on, so the
        question can still be put — about the path the ROM would occupy once
        installed. Nothing is probed for either way: :meth:`synced_save_names`
        pairs an uninstalled ROM with no directory, because a state is a
        statement about an emulator and a probe needs a file.
        """
        with self._uow_factory() as uow:
            rom = uow.roms.get(int(rom_id))
        if rom is None or not rom.fs_name or not rom.platform_slug:
            # No name, so no extension, so no question — not a statement about
            # any emulator.
            return unestablished_answer(shape=UNESTABLISHED_NOT_ASKED)
        system = self._resolve_system(rom.platform_slug)
        content_path = os.path.join(self._retrodeck_paths.roms_path(), system, rom.fs_name)
        return self._ask_resolver(rom_id, system, content_path, installed=False, platform=rom.platform_slug)

    def _installed_answer(self, rom_id: int, info: dict[str, Any]) -> SaveAnswer:
        """The answer for an installed ROM, asked about the file on disk.

        The system is the NORMALIZED one the install record carries, never the
        raw RomM ``platform_slug`` beside it (ADR-0010): the slug names no
        system any emulator declares, so asking with it answers about nothing.
        One of the two places in THIS service that decide a system and a path —
        :meth:`_uninstalled_answer` is the other — so the leak has two sites to
        guard here rather than one per caller. ``services/migration/save_sort.py`` decides
        its own, off the install record, and is the third site the rule holds at.
        """
        return self._ask_resolver(
            rom_id, info["system"], info["file_path"], installed=True, platform=info["platform_slug"]
        )

    def _ask_resolver(
        self, rom_id: int, system: str, content_path: str, *, installed: bool, platform: str | None = None
    ) -> SaveAnswer:
        """Put the question to the emulator this ROM would launch with.

        *installed* says whether *content_path* is a file on disk or the path
        the ROM would occupy, and rides onto the answer so a surface never
        renders a prediction as an observation.

        The answer's ``<save_id>`` hole is filled from the content file's own bytes
        (:meth:`_fill_save_id`) — the resolver cannot read a game's disc header, and the
        save of every id-keyed platform stays refused until somebody does.
        """
        # The SAVE path, asked of the resolver's pick-agnostic read: the picker chooses
        # which program runs, never where the platform keeps its cards.
        managed = self._active_core.managed_save_entry(int(rom_id))
        stated = manifest_answer(managed, content_installed=installed)
        if stated is not None:
            # The provisioner stated both the launch and the save path, so there is nothing
            # left to ask: this answer IS the truth about a program whose command we wrote.
            return self._fill_save_id(stated, content_path=content_path, platform=platform, installed=installed)
        emulator = self._active_core.active_emulator_for_rom(int(rom_id))
        # An owned launch states where it will write, and that statement outranks any
        # catalogue reading: the catalogue models an emulator's DEFAULT user directory,
        # which on this Deck is not the directory the launched emulator uses.
        bank_dir = self._save_bank_dir(platform) if self._save_bank_dir is not None and platform else None
        # The bank is on only while the launch is redirected into it, and a libretro launch
        # is redirected by the appendconfig this plugin wrote — so the answer is the plugin's
        # own statement, not a catalogue reading. Asking the catalogue here is what made every
        # owned launch report an unestablished save: on a device with no ES-DE there is no
        # entry labelled with the core's name, and sync was skipped for a path we wrote.
        if bank_dir and (emulator is None or emulator.kind == "libretro"):
            answer = owned_libretro_answer(
                bank_dir,
                rom_name=os.path.basename(content_path),
                emulator=emulator.label if emulator is not None else None,
                content_installed=installed,
            )
        elif emulator is not None and emulator.user_dir is not None:
            answer = owned_dolphin_answer(emulator.user_dir, content_installed=installed)
        else:
            answer = self._save_locations.resolve_save_answer(
                system=system,
                content_path=content_path,
                emulator_label=emulator.label if emulator is not None else None,
                content_installed=installed,
            )
        return self._fill_save_id(answer, content_path=content_path, platform=platform, installed=installed)

    def _fill_save_id(
        self, answer: SaveAnswer, *, content_path: str, platform: str | None, installed: bool
    ) -> SaveAnswer:
        """Complete the resolver's id hole from the game file, when there is one to fill.

        Only an installed ROM is read: for one the library holds and the disk does not,
        *content_path* is a path that would exist later, so there are no bytes to read
        and a prediction built from them would be a guess wearing an observation's
        clothes. Everything else — no seam, no hole, no reader for the platform, a header
        that states nothing — returns the answer untouched.
        """
        if self._content_identity is None or not installed or platform is None:
            return answer
        wants_id = SAVE_ID_NEED in answer.needs
        wants_region = SAVE_REGION_NEED in answer.needs
        if not wants_id and not wants_region:
            return answer
        identity = self._content_identity(content_path, platform)
        if identity is None:
            return answer
        self._logger.info(f"SaveService: {platform} save id from the game file ({identity.source}): {identity.save_id}")
        filled = fill_region(answer, identity.region) if wants_region else answer
        if wants_id:
            filled = fill_save_id(filled, save_id_text(identity))
        return self._fill_members(filled, identity=identity, platform=platform)

    def _fill_members(self, answer: SaveAnswer, *, identity: ContentIdentity, platform: str) -> SaveAnswer:
        """Name a member set's files from the directory the answer points at.

        Two platforms carry a folder whose file names the emulator chooses, and each is read
        from its own directory rather than from a table: a GameCube card holds
        ``<maker>-<code>-<internal>.gci`` entries keyed by the disc's code, and an Eden title
        folder holds files named ``0``, ``1``, … keyed by nothing at all. The listing is the
        only honest source in both cases.
        """
        if canonical_platform(platform) == "gc":
            return self._fill_gci_names(answer, identity=identity, platform=platform)
        if answer.granularity == "title-dir":
            return self._fill_directory_members(answer)
        return answer

    def _fill_directory_members(self, answer: SaveAnswer) -> SaveAnswer:
        """Name a managed title directory's files from the directory itself.

        Only a provisioned ``title-dir`` answer reaches this, so the directory is one the
        provisioner adopted (Eden's ``…/user/save/<slot>/<save_id>``) rather than something
        inferred. A folder that does not exist yet lists nothing and keeps its refusal.
        """
        if not answer.directory:
            return answer
        # Regular files only: a member set is restored by extracting into ONE flat
        # directory, so a nested entry is not a member this carry can place — listing it
        # would make the upload fail on a directory instead of leaving it out.
        names = [
            name
            for name in self._save_file_store.listdir(answer.directory)
            if self._save_file_store.is_file(os.path.join(answer.directory, name))
        ]
        return fill_directory_members(answer, names)

    def _fill_gci_names(self, answer: SaveAnswer, *, identity: ContentIdentity, platform: str) -> SaveAnswer:
        """Name a GameCube card's entries from the card folder itself.

        Dolphin files a save as ``GC/<region>/Card A/<maker>-<code>-<internal>.gci`` and
        the resolver refuses the names inside the folder, which left GameCube unable to
        sync in either direction. The listing settles it: the middle component is this
        disc's code, so the entries that carry it are this disc's save. The directory is
        read only once the region hole is filled — before that it names no folder.
        """
        if canonical_platform(platform) != "gc" or not answer.directory:
            return answer
        names = self._save_file_store.listdir(answer.directory)
        filled = fill_gci_set(answer, game_code=identity.save_id, names=names)
        if filled.syncable:
            self._logger.info(f"SaveService: GameCube card entries named from the card: {filled.synced_names}")
        return filled

    def synced_save_names(self, rom_id: int, *, save_answer: SaveAnswer | None = None) -> tuple[list[str], str | None]:
        """The basenames a sync may carry for this ROM, and the directory they sit in.

        Empty names with a ``None`` directory whenever the ROM's save may not be
        synced — every refusing state, and an uninstalled ROM. That pairing is
        what makes a refusal cost no probe: there is nothing to look for and
        nowhere to look.

        *save_answer* is this ROM's reading where the caller already took one in
        the same operation, and it is used instead of taking a second. Live is a
        property of operations rather than of layers, and a reading costs real
        machine I/O on a path that runs at every launch and every exit.

        The directory is still the plugin's own ``resolve_save_dir`` answer
        rather than the resolver's, because retiring that path math is its own
        change; what has moved here is the NAMES, which used to come from a
        hand-maintained per-system extension table.
        """
        info = self.get_rom_save_info(rom_id)
        if not info:
            return ([], None)
        answer = save_answer if save_answer is not None else self._installed_answer(rom_id, info)
        return (list(answer.synced_names), info["saves_dir"] if answer.syncable else None)

    def member_set_dir(self, info: dict[str, Any], answer: SaveAnswer) -> str | None:
        """Where this ROM's save actually sits, or ``None`` when the answer refuses.

        A member set sits BELOW the platform save root — a GameCube card is
        ``GC/<region>/Card A`` under it — so joining a member's name onto the root
        probes a directory the file is not in. Measured on the reference Deck: rom 5319
        reported ``uploaded=0, downloaded=0, errors=0`` while its only ``.gci`` sat in
        the card folder the answer named.

        Every path that reads a save's directory asks this, so the sync matrix and the
        status/launch views cannot disagree about where a member set lives — which they
        did, and which is how the Saves tab emptied out while the sync worked.
        """
        if not answer.syncable:
            return None
        if restores_by_extraction(info["system"]):
            return answer.directory
        return info["saves_dir"]

    def save_unit(self, info: dict[str, Any], answer: SaveAnswer) -> tuple[tuple[str, ...], str | None, str | None]:
        """Where a ROM's save actually lives, as ``(names, directory, extract_dir)``.

        The one answer every reader needs, so a restore and a sync cannot disagree about
        the directory — the split between them is what sent a resolved conflict's download
        into the RetroArch root while the emulator read Eden's folder. *extract_dir* is set
        only for a unit RomM carries as one archive: the zip is staged beside the folder it
        archives, so a download has to name the folder to unpack into.

        A refusing answer keeps its ``None`` directory, and nothing is packed for it.
        """
        unit = self.prepare_packed_unit(info, answer)
        if unit is not None:
            return (unit.archive_name,), unit.archive_dir, unit.source_dir
        return answer.synced_names, self.member_set_dir(info, answer), None

    def prepare_packed_unit(self, info: dict[str, Any], answer: SaveAnswer) -> PackedSaveUnit | None:
        """Pack a ``title-dir`` save into the ONE archive RomM carries, or return ``None``.

        RomM's Switch saves are ``<rom name> [timestamp].zip`` — the server never holds the
        folders members by name. Syncing the members one by one therefore mismatches every
        server row: measured on the reference Deck, six uploads each met a 409 because a
        save already sat in the slot under a name the conflict handler could not pair.

        So the unit synced is the archive: the folder is the truth, the zip is derived from
        it on each sync, and a download is extracted back into the folder (the restore half
        already exists for member sets). The archive is staged in a dot-directory beside the
        title folder — it cannot live inside the folder it archives — where no emulator
        looks and the slot's own listing stays clean.

        Nothing is packed unless the answer is a syncable ``title-dir`` with named members.
        """
        if answer.granularity != "title-dir" or not answer.syncable or not answer.directory:
            return None
        members = tuple(component.name for component in answer.synced_files)
        if not members:
            return None
        source_dir = answer.directory
        archive_dir = os.path.join(os.path.dirname(source_dir), PACKED_ARCHIVE_DIR_NAME)
        archive_name = f"{info['rom_name']}.zip"
        self._save_file_store.create_archive(os.path.join(archive_dir, archive_name), source_dir, list(members))
        self._logger.debug(f"SaveService: packed {len(members)} file(s) into {archive_name}")
        return PackedSaveUnit(archive_dir=archive_dir, archive_name=archive_name, source_dir=source_dir)

    def find_save_files(self, rom_id: int, *, save_answer: SaveAnswer | None = None) -> list[dict[str, str]]:
        """Find local save files for a ROM.

        Returns list of ``{"path": str, "filename": str}``. *save_answer* passes
        a reading the caller already holds through to :meth:`synced_save_names`.
        """
        return self.probe_save_files(*self.synced_save_names(rom_id, save_answer=save_answer))

    def probe_save_files(self, names: list[str], saves_dir: str | None) -> list[dict[str, str]]:
        """Which of *names* are actually on disk under *saves_dir*.

        Public (peer-called): the sync matrix already holds the answer's names —
        it needs them to group server saves onto their canonical targets — and
        asking the resolver a second time for the same ROM costs a live reading
        of the machine. A ``None`` directory is the refusing answer's pairing and
        probes nothing.

        Returns a list of ``{"path", "filename"}``.
        """
        if saves_dir is None or not self._save_file_store.is_dir(saves_dir):
            return []
        results = []
        for name in names:
            save_path = os.path.join(saves_dir, name)
            if self._save_file_store.is_file(save_path):
                results.append({"path": save_path, "filename": name})
        return results

    def expected_save_files(self, rom_id: int) -> list[dict[str, str]]:
        """Project exact save paths for one installed ROM without broad scanning."""
        names, saves_dir = self.synced_save_names(rom_id)
        if saves_dir is None:
            return []
        return [
            {
                "path": os.path.join(saves_dir, name),
                "filename": name,
                "saves_dir": saves_dir,
            }
            for name in names
        ]

    def pending_sort_settings(self) -> SaveSortSettings | None:
        """Return previous save-sort settings if a migration is pending, else None.

        Rejects empty dicts to avoid the half-state where ``get_rom_save_info``'s
        ``or`` fallback would treat ``{}`` as "no pending migration" (and read
        current settings) while ``is_save_sort_changed`` would treat the same
        ``{}`` as "pending" (and gate sync). Both call sites must agree on
        what counts as pending — see #238 review finding 3.
        """
        with self._uow_factory() as uow:
            raw = uow.kv_config.get(_KV_SAVE_SORT_PREVIOUS)
        prev: SaveSortSettings | None = json.loads(raw) if raw is not None else None
        return prev if prev else None

    def _read_current_sort_settings(self) -> SaveSortSettings | None:
        """Return the last-seen RetroArch save-sort observation, ``None`` when unobserved."""
        with self._uow_factory() as uow:
            raw = uow.kv_config.get(_KV_SAVE_SORT)
        return json.loads(raw) if raw is not None else None

    def is_save_sort_changed(self) -> bool:
        """Check if a save sort migration is pending (detected by MigrationService)."""
        return self.pending_sort_settings() is not None
