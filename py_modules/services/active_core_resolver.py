"""ActiveCoreResolver — the single read-path core-resolution seam per ROM.

The one place that answers "which RetroArch core will this ROM actually launch
with?", combining the per-game ``emulator_override`` and per-platform core
selection (the two deviations the plugin owns) with the system-layer
ES-DE/RetroDECK resolution. Every per-game core read consumer and every
launch-bake site draws from this seam so the read-path core never diverges from
the launched core.

Precedence (three layers, then the plain launch): DB ``emulator_override`` (top)
→ ``settings.json`` per-platform core → the live es_systems default → ``None``.
An ES-DE ``<alternativeEmulator>`` or ``<altemulator>`` never moves that default
— the promotion is discarded where the catalogue is read (ADR-0012) — and there
is no offline snapshot below the live default. A pinned per-game or
per-platform label that no longer resolves to a bakeable emulator degrades to
the next layer rather than raising — so a stale label never blocks a read or
bakes a bogus ``-e`` override. The per-game/per-platform label may name a
**standalone** emulator (not just a libretro core); it resolves the same way.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from domain.emulator_commands import label_to_invocation
from domain.owned_dolphin import is_owned_dolphin, with_user_dir
from domain.retroarch_appendconfig import with_appendconfig
from domain.retroarch_runner import resolve_backend
from domain.rom_files import folder_boot_root
from domain.shortcut_data import EmulatorInvocation

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

    from domain.emulator_commands import EmulatorOption
    from domain.layout_manifest import ManagedPlatform
    from domain.rom import Rom
    from domain.rom_install import RomInstall
    from services.protocols import (
        CoreInfoProvider,
        ManagedLayoutFn,
        PlatformCoreReader,
        RetroArchAppendConfigFn,
        RetroArchRunnerFn,
        SandboxLauncherFn,
        SystemResolver,
        UnitOfWorkFactory,
    )


@dataclass(frozen=True)
class ActiveCoreResolverConfig:
    """Frozen wiring bundle handed to ``ActiveCoreResolver.__init__``.

    Carries the SQLite Unit-of-Work factory (to read the ROM's
    ``platform_slug`` + ``emulator_override``), the core-info read seam (the
    classified emulator options + the system-layer default), the sandbox-launcher
    seam the folder-boot rewrite resolves through, the per-platform core reader
    (the ``settings.json`` ``platform_cores`` map), the platform-slug-to-system
    resolver, and the logger used to warn on a stale label.
    """

    uow_factory: UnitOfWorkFactory
    core_info: CoreInfoProvider
    sandbox_launcher: SandboxLauncherFn
    platform_core_reader: PlatformCoreReader
    resolve_system: SystemResolver
    logger: logging.Logger
    # Optional: without it every libretro launch bakes exactly as before. With it, a
    # resolved core also carries the platform's generated ``--appendconfig``, so the
    # save is written where the bank reads it.
    retroarch_appendconfig: RetroArchAppendConfigFn | None = None
    # Which launch path to bake: ``retrodeck`` (default) keeps ``run_game.sh`` in the
    # process tree, ``retroarch`` starts RetroArch directly when a runner can hold the
    # chosen core. A callable, not a value, because settings change while the resolver
    # is alive and a value would pin the choice to whatever was set at startup.
    launch_backend: Callable[[], object] | None = None
    retroarch_runner: RetroArchRunnerFn | None = None
    # Optional: a platform's candidate user directory for an owned standalone launch. A
    # callable, because the answer follows the live saves root rather than a value
    # captured at startup. ``None`` keeps every standalone launch exactly as before.
    standalone_user_dir: Callable[[str], str | None] | None = None
    # Optional: the provisioner's manifest (ADR-0034). A managed platform's launch is baked
    # from the entry, so neither the emulator nor its save path is inferred.
    managed_layout: ManagedLayoutFn | None = None


class ActiveCoreResolver:
    """Resolve the active RetroArch core for one ROM by ``rom_id``."""

    def __init__(self, *, config: ActiveCoreResolverConfig) -> None:
        self._uow_factory = config.uow_factory
        self._core_info = config.core_info
        self._sandbox_launcher = config.sandbox_launcher
        self._platform_core_reader = config.platform_core_reader
        self._resolve_system = config.resolve_system
        self._logger = config.logger
        self._appendconfig = config.retroarch_appendconfig
        self._launch_backend = config.launch_backend
        self._retroarch_runner = config.retroarch_runner
        self._standalone_user_dir = config.standalone_user_dir
        self._managed_layout = config.managed_layout

    def standalone_emulator_identity(self, rom_id: int) -> str | None:
        """The emulator a standalone launch of ``rom_id`` names, or ``None`` otherwise.

        The upload tag's source, and a projection of :meth:`active_emulator_for_rom`
        rather than a second resolution: only a standalone invocation has an emulator
        of its own to stamp, because a libretro launch is RetroArch by definition and
        its core is what distinguishes one from another.

        The identity is whichever name the invocation carries — a registry id
        (``eden``) or a picker label (``Dolphin (Standalone)``) — and
        :func:`domain.emulator_tag.emulator_tag` normalises either to the spelling the
        server files saves under (ADR-0063).
        """
        invocation = self.active_emulator_for_rom(rom_id)
        if invocation is None or invocation.kind != "standalone":
            return None
        return invocation.emulator or invocation.label

    def active_emulator_for_rom(self, rom_id: int) -> EmulatorInvocation | None:
        """Return the :class:`EmulatorInvocation` the ROM ``rom_id`` will launch with.

        The launch-bake seam. Reads the ROM's ``platform_slug`` +
        ``emulator_override`` once, then applies the three-layer precedence:

        1. Per-game DB ``emulator_override`` (an emulator LABEL from the picker,
           libretro OR standalone) → its invocation when the label resolves to a
           bakeable command.
        2. Per-platform ``settings.json`` core (also a LABEL, libretro OR
           standalone) → its invocation when it resolves.
        3. The live es_systems default via ``get_default_emulator`` — the first
           safely-bakeable command, which may itself be standalone (PCSX2, RPCS3,
           Dolphin, …) or libretro.

        Returns ``None`` when the platform has no resolvable emulator at all —
        including when ``es_systems.xml`` cannot be read — so the caller bakes
        the plain launch and lets RetroDECK resolve the emulator. A stale
        per-game/per-platform label is never fatal — it degrades to the next
        layer with a WARNING.

        Final step: a resolved **standalone** emulator whose install is a
        folder-boot layout (PS3 — ``…/PS3_GAME/USRDIR/EBOOT.BIN``) is rewritten
        to the ``direct`` sandbox form (ADR-0019). RetroDECK's ``run_game.sh``
        reinterprets a directory ``%ROM%`` as an ES-DE "directory as a file" and
        can never launch a bare game folder, so a folder-boot game must run its
        emulator launcher directly inside the sandbox instead. The rewrite keys
        off :func:`folder_boot_root` — the same fact the disc/bake-path seam uses
        to fold the target to the game folder — so the invocation form and the
        baked path are always decided from one layout fact. A libretro emulator,
        a non-folder install, or an unresolvable sandbox launcher all leave the
        invocation unchanged.
        """
        rom, install = self._read_rom_and_install(rom_id)
        if rom is None:
            self._logger.warning("active_core_resolver: no ROM for rom_id=%s; resolving to plain launch", rom_id)
            return None

        managed = self._managed_entry(rom)
        if managed is not None:
            # The manifest states the emulator AND the command, so the catalogue is not
            # consulted at all for a managed platform: there is nothing left to resolve.
            return EmulatorInvocation.standalone(
                managed.launch_command, label=managed.emulator, emulator=managed.emulator
            )

        system = self._resolve_system(rom.platform_slug)
        options = self._core_info.get_emulator_options(system)["options"]
        emulator = self._resolve_by_precedence(rom, rom_id, system, options)
        emulator = self._maybe_folder_boot_direct(emulator, install, rom_id)
        emulator = with_appendconfig(emulator, self._appendconfig_for(rom.platform_slug))
        return self._maybe_owned(emulator, rom.platform_slug)

    def managed_save_entry(self, rom_id: int) -> ManagedPlatform | None:
        """The entry that governs ``rom_id``'s SAVE PATH, which no pick changes.

        Deliberately not :meth:`managed_entry`: that one answers "which program runs",
        and the user's pick decides it. Where a platform's saves live is a property of
        the platform's own card/tree layout, not of which program opens it — measured on
        the reference Deck, RetroDECK runs the libretro Dolphin core inside Dolphin's user
        tree, so both emulators write ``saves/gc/User/GC/<region>/Card A``. Letting the
        pick move the save path is what made the save layer look in a folder the launch
        never wrote.
        """
        rom, _install = self._read_rom_and_install(rom_id)
        if rom is None or self._managed_layout is None:
            return None
        return self._managed_layout(rom.platform_slug)

    def managed_entry(self, rom_id: int) -> ManagedPlatform | None:
        """The manifest entry that governs ``rom_id``, or ``None`` when none does.

        The save layer asks this rather than reading the manifest itself: whether a
        managed entry applies is one question with one answer, and the launch and the
        save path must never answer it differently — they are the same statement.
        """
        rom, _install = self._read_rom_and_install(rom_id)
        return None if rom is None else self._managed_entry(rom)

    def _managed_entry(self, rom: Rom) -> ManagedPlatform | None:
        """Whether the provisioner's entry governs this ROM, given what the user chose.

        **An explicit choice outranks the manifest.** ``emulator_override`` is the
        per-game picker's answer and the per-platform core is the same statement one
        level up; either one is the user saying which emulator should run, and the
        manifest's job is to describe the layout when nobody has said. It cannot be
        combined with them either: the entry's command and its save path are one
        sentence, so honouring a different emulator while keeping the manifest's
        directory would point the save layer at a place the launch never writes.
        """
        if self._managed_layout is None:
            return None
        if rom.emulator_override is not None:
            return None
        if self._platform_core_reader.get_platform_core(rom.platform_slug) is not None:
            return None
        return self._managed_layout(rom.platform_slug)

    def _maybe_owned(
        self, emulator: EmulatorInvocation | None, platform_slug: str | None = None
    ) -> EmulatorInvocation | None:
        """Swap in a direct RetroArch launch when the settings ask for one.

        Only a libretro invocation can be owned: standalone emulators already run from
        their own command, and there is nothing RetroDECK adds to them that this path
        would remove. Everything else — no backend configured, a backend that is not
        ``retroarch``, no runner holding the core — returns the invocation untouched,
        so the owned path is a strict opt-in whose failure mode is today's launch.
        """
        if emulator is None:
            return emulator
        # A standalone launch can be owned too, and for the same reason: the user
        # directory the emulator writes into is then a fact of OUR command. Measured on
        # the reference Deck — RetroDECK's placeholder command left the save one folder
        # away from where the save layer looked, and it was never carried.
        if self._standalone_user_dir is not None and is_owned_dolphin(emulator.label, emulator.emulator):
            user_dir = self._standalone_user_dir(platform_slug or "")
            owned = with_user_dir(emulator, user_dir) if user_dir is not None else None
            if owned is not None:
                return owned
        if emulator.kind != "libretro" or emulator.core_so is None:
            return emulator
        # An owned launch without a redirect is a save the plugin cannot find: started
        # directly, RetroArch reads its OWN config and writes to its own directory, which
        # is not the directory the save lookup reads. The redirect only exists with the
        # bank switched on, so the two opt-ins travel together.
        if emulator.appendconfig is None:
            return emulator
        if self._launch_backend is None or self._retroarch_runner is None:
            return emulator
        if resolve_backend(self._launch_backend()) != "retroarch":
            return emulator
        try:
            runner = self._retroarch_runner(emulator.core_so)
        except Exception as exc:  # an owned launch is never worth failing a launch over
            self._logger.warning(f"active_core_resolver: no owned runner for {emulator.core_so}: {exc}")
            return emulator
        return emulator if runner is None else replace(emulator, runner=runner)

    def _appendconfig_for(self, platform_slug: str) -> str | None:
        """The generated RetroArch config for *platform_slug*, or ``None``.

        A save redirection is never worth failing a launch over, so a generator that
        raises is treated as one that has nothing to offer — logged, then baked
        unredirected. That is the same degradation as a data directory that cannot be
        written, and both end with the game running and the save landing where the
        user's own RetroArch config says.
        """
        if self._appendconfig is None:
            return None
        try:
            return self._appendconfig(platform_slug)
        except Exception as exc:  # a save nicety must never break a launch
            self._logger.warning(f"active_core_resolver: no appendconfig for {platform_slug}: {exc}")
            return None

    def _resolve_by_precedence(
        self, rom: Rom, rom_id: int, system: str, options: list[EmulatorOption]
    ) -> EmulatorInvocation | None:
        """Apply the per-game → per-platform → system-default precedence chain.

        Returns the resolved :class:`EmulatorInvocation` before the folder-boot
        rewrite. A stale per-game/per-platform label warns and degrades to the
        next layer; the bottom is the live es_systems default (or ``None``).
        """
        override = rom.emulator_override
        if override is not None:
            invocation = label_to_invocation(options, override)
            if invocation is not None:
                return invocation
            self._logger.warning(
                "active_core_resolver: per-game override '%s' for rom_id=%s no longer resolves on %s; "
                "degrading to the per-platform/system default",
                override,
                rom_id,
                system,
            )

        platform_label = self._platform_core_reader.get_platform_core(rom.platform_slug)
        if platform_label is not None:
            invocation = label_to_invocation(options, platform_label)
            if invocation is not None:
                return invocation
            self._logger.warning(
                "active_core_resolver: per-platform core '%s' for %s (rom_id=%s) no longer resolves; "
                "degrading to the system default",
                platform_label,
                rom.platform_slug,
                rom_id,
            )

        return self._core_info.get_default_emulator(system)

    def _maybe_folder_boot_direct(
        self, emulator: EmulatorInvocation | None, install: RomInstall | None, rom_id: int
    ) -> EmulatorInvocation | None:
        """Rewrite a standalone *emulator* to the folder-boot ``direct`` form when warranted.

        Fires only for a **standalone** emulator whose *install* is a folder-boot
        layout (:func:`folder_boot_root` returns a game root). Resolves the
        emulator's sandbox launcher via the es_find_rules probe and returns a
        ``direct`` invocation. Leaves the emulator unchanged for a libretro core,
        a non-folder install, a missing install, or an unresolvable launcher —
        the last is logged (the baked ``run_game`` form will fail to launch a
        folder until a later re-bake heals it).
        """
        if emulator is None or emulator.kind != "standalone" or emulator.command is None:
            return emulator
        if install is None or folder_boot_root(install.file_path, install.rom_dir) is None:
            return emulator
        launcher = self._sandbox_launcher(emulator.command)
        if launcher is None:
            self._logger.warning(
                "active_core_resolver: folder-boot rom_id=%s resolves to standalone '%s' but its sandbox "
                "launcher is unresolvable; keeping the run_game form (launch will fail until healed)",
                rom_id,
                emulator.label,
            )
            return emulator
        return EmulatorInvocation.direct(emulator.command, launcher, emulator.label, emulator.emulator)

    def active_core_for_rom(self, rom_id: int) -> tuple[str | None, str | None]:
        """Return the ``(core_so, label)`` the ROM ``rom_id`` will launch with.

        The read-path projection of :meth:`active_emulator_for_rom`, kept for the
        ``.so``-space consumers (BIOS status, per-core save dir, save-emulator
        tag, core-change detection, the cores menu's active marker). A **libretro**
        emulator yields its ``(core_so, label)``; a **standalone** emulator yields
        ``(None, label)`` — those consumers already degrade on a ``None`` core
        exactly as they did for the old ``(None, None)`` resolution, so the
        read-path core never disagrees with the (now possibly standalone) launch.
        """
        emulator = self.active_emulator_for_rom(rom_id)
        if emulator is None:
            return (None, None)
        return (emulator.core_so, emulator.label)

    def _read_rom_and_install(self, rom_id: int) -> tuple[Rom | None, RomInstall | None]:
        with self._uow_factory() as uow:
            return (uow.roms.get(rom_id), uow.rom_installs.get(rom_id))
