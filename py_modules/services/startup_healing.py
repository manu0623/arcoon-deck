"""StartupHealingService — startup-time state reconciliation.

Owns the reconciliation steps that run after state is loaded and
adapters are wired: drops ``rom_installs`` rows that no longer reflect
what's on disk, and transitions any ``running`` ``SyncRun`` left behind
by a crash into ``interrupted``. The install prune is skipped when the
RetroDECK home is missing on disk (boot-time SD-card mount race) so
legitimate installs on a card that hasn't finished mounting don't get
wiped on the next reload.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from domain.installed_roms import is_pending_migration_path
from domain.migration_paths import pending_homes_from_kv
from domain.rom_files import is_launchable_target

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Sequence

    from services.protocols import (
        Clock,
        PathExistsReader,
        RelaunchOptionsReader,
        ResolvedPathFn,
        RetroDeckPaths,
        UnitOfWorkFactory,
    )


@dataclass(frozen=True)
class StartupHealingServiceConfig:
    """Frozen wiring bundle handed to ``StartupHealingService.__init__``.

    Carries the runtime logger, the clock, the bundled RetroDECK paths
    provider, the generic path-exists probe, the path resolver that turns a
    stored home marker into the directory it names, and the SQLite Unit-of-Work
    factory (the transactional seam over the ``rom_installs``, ``sync_runs``,
    and ``kv_config`` repositories — the last holding the pending-migration
    previous home marker). The shared ``relaunch_options`` seam builds each
    installed+bound ROM's full launch command (active core, selected disc) so
    the startup launch-options reconcile draws its items from the same resolver
    the RetroDECK-home migration does. Bundled here so the ctor stays within the
    S107 parameter budget and the service stays free of raw filesystem I/O.
    """

    logger: logging.Logger
    clock: Clock
    retrodeck_paths: RetroDeckPaths
    path_probe: PathExistsReader
    resolve_path: ResolvedPathFn
    uow_factory: UnitOfWorkFactory
    relaunch_options: RelaunchOptionsReader
    # The live accept-list per system, so a verdict recorded when the list could not
    # answer can be re-derived at startup (see ``reconsider_launchability``).
    system_extensions: Callable[[str], frozenset[str]]


class StartupHealingService:
    """Reconciles persisted ``rom_installs`` against disk and heals orphaned ``SyncRun``s."""

    def __init__(self, *, config: StartupHealingServiceConfig) -> None:
        self._logger = config.logger
        self._clock = config.clock
        self._retrodeck_paths = config.retrodeck_paths
        self._path_probe = config.path_probe
        self._resolve_path = config.resolve_path
        self._uow_factory = config.uow_factory
        self._relaunch_options = config.relaunch_options
        self._system_extensions = config.system_extensions

    def reconsider_launchability(self) -> None:
        """Promote installs wrongly recorded unlaunchable, now the accept-list answers.

        ``launchable`` is written once, at download, by ``domain.rom_files.
        is_launchable_target``. A verdict of ``False`` recorded against an accept-list
        that could not answer for the system — every owned-platform install before
        ADR-0041, where the inventory's bare ``gba`` never matched ``.gba`` — withholds
        the shortcut's launch command and tells the reader the download has nothing the
        emulator can launch, which is false.

        The re-derivation runs the same predicate over the same recorded path, so it
        is the download's verdict recomputed rather than a second opinion. Only
        ``False → True`` is applied: a genuine unlaunchable install (a ``.pkg``
        installer, a bare disc track) stays unlaunchable, and nothing proven working is
        stripped.
        """
        promoted: list[int] = []
        with self._uow_factory() as uow:
            for install in list(uow.rom_installs.iter_all()):
                if install.launchable:
                    continue
                extensions = self._system_extensions(install.system)
                if not is_launchable_target(install.file_path, install.rom_dir, extensions):
                    continue
                uow.rom_installs.save(replace(install, launchable=True))
                promoted.append(install.rom_id)
        if promoted:
            self._logger.info(f"Reconsidered {len(promoted)} install(s) as launchable: {promoted[:10]}")

    def prune_stale_installed_roms(self) -> None:
        """Remove ``rom_installs`` rows whose files no longer exist on disk.

        Skipped when the RetroDECK home is not yet available on disk —
        almost always a boot-time SD-card-mount race; the next plugin
        reload, with the filesystem ready, will run the prune normally.
        Installs living under any pending migration home (the previous
        home plus any additional hops, #1042) are also preserved because
        RetroDECK has moved away from those paths but the user hasn't
        migrated yet, so the records must survive until they do.
        """
        retrodeck_home = self._retrodeck_paths.retrodeck_home()
        if not retrodeck_home or not self._path_probe.exists(retrodeck_home):
            self._logger.info(
                f"Skipping installed_roms prune: retrodeck home unavailable ({retrodeck_home or 'unset'})"
            )
            return

        with self._uow_factory() as uow:
            installs = list(uow.rom_installs.iter_all())
            stored_homes = pending_homes_from_kv(
                uow.kv_config.get("retrodeck_home_path_previous") or "",
                uow.kv_config.get("retrodeck_home_path_hops"),
            )
        pending_homes = [self._resolve_path(home) for home in stored_homes]
        stale: list[int] = []
        for install in installs:
            file_path = install.file_path
            rom_dir = install.rom_dir
            if self._under_pending_home(file_path, rom_dir, pending_homes):
                self._logger.info(f"Skipping prune of {install.rom_id} ({file_path}): pending migration")
                continue
            if (file_path and self._path_probe.exists(file_path)) or (rom_dir and self._path_probe.exists(rom_dir)):
                continue
            self._logger.info(f"Pruned stale installed_roms entry: {install.rom_id} ({file_path})")
            stale.append(install.rom_id)

        if stale:
            with self._uow_factory() as uow:
                for rom_id in stale:
                    uow.rom_installs.delete(rom_id)

    def _under_pending_home(self, file_path: str, rom_dir: str | None, pending_homes: Sequence[str]) -> bool:
        """Answer whether one install's recorded paths live under a pending home.

        Both sides are resolved before the prefix match, because either can be
        spelled two ways for one directory: a path recorded through
        ``lib.path_safety.safe_join`` is resolved, one an older migration
        relocated carries whatever spelling the home had when it ran
        (``remap_under_current`` joins that home verbatim), and a marker written
        before the roots were resolved carries the other spelling again (#1838).
        A match that misses prunes a record whose files are still on disk, so
        the question has to be about directories rather than strings.

        Resolving the recorded path is safe here in a way it is not in the
        deletion guards: this decides what to KEEP and authorizes nothing. The
        loop already probes each path's existence, so it is no new class of
        cost.
        """
        return is_pending_migration_path(
            self._resolve_path(file_path) if file_path else file_path,
            self._resolve_path(rom_dir) if rom_dir else rom_dir,
            pending_homes,
        )

    def reconcile_orphaned_sync_runs(self) -> None:
        """Transition a ``running`` ``SyncRun`` left by a crash into ``interrupted``.

        A hard crash (process kill, true ``asyncio.CancelledError``) mid-sync
        leaves the run record stuck in ``running`` because no terminal
        transition fired. A backend restart mid-run is an external death, not a
        user Cancel, so on the next startup that orphaned run is marked
        ``interrupted`` in a short write UoW — the sync-run history reflects what
        actually happened rather than an eternally-in-flight sync.
        """
        with self._uow_factory() as uow:
            run = uow.sync_runs.get_running()
            if run is None:
                return
            self._logger.info(f"Healing orphaned sync run {run.id}: marking interrupted (backend restarted mid-run)")
            run.mark_interrupted(at=self._clock.now().isoformat(), reason="interrupted by restart")
            uow.sync_runs.save(run)

    def get_installed_relaunch_options(self) -> list[dict[str, Any]]:
        """Build the relaunch items for every installed+bound ROM so the
        frontend can re-confirm drifted ``launch_options`` at startup (#1043).

        Delegates to the shared ``relaunch_options`` resolver — the same seam
        the RetroDECK-home migration re-bakes through — so the startup reconcile
        and the migration relaunch never carry a divergent build of the list. It
        snapshots the installed+bound rows in one short read UoW it closes before
        resolving the core and disc, so the nested resolver UoW never deadlocks
        (#1154).
        """
        return self._relaunch_options.installed_relaunch_items()
