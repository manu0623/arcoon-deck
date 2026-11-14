"""In-memory ``ActiveCoreReader`` implementation for service tests.

Lets Phase-5 consumer tests inject a per-ROM active-core seam without standing
up a real ``ActiveCoreResolver`` (UoW + core-info + system resolver). Configure a
default ``(core_so, label)`` and/or per-``rom_id`` overrides; each call is
recorded so a consumer test can assert the seam was queried by ``rom_id``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.shortcut_data import EmulatorInvocation

if TYPE_CHECKING:
    from domain.layout_manifest import ManagedPlatform


class FakeActiveCoreResolver:
    """Maps ``rom_id`` to a configured ``(core_so, label)`` for tests.

    ``per_rom`` takes precedence; any ``rom_id`` absent from it resolves to
    ``default``. ``calls`` records each queried ``rom_id`` so consumer tests can
    assert the seam was reached with the right ROM.

    :meth:`active_emulator_for_rom` is the launch-bake seam. By default it
    projects the same ``(core_so, label)`` tuple config into a libretro
    :class:`EmulatorInvocation` (or ``None`` when the core is ``None``), so the
    existing tuple-configured tests keep working unchanged. To exercise a
    **standalone** emulator (PCSX2, RPCS3, …), pass an explicit
    ``default_emulator`` and/or ``per_rom_emulator`` map — those take precedence
    over the tuple projection.
    """

    def __init__(
        self,
        *,
        default: tuple[str | None, str | None] = (None, None),
        per_rom: dict[int, tuple[str | None, str | None]] | None = None,
        default_emulator: EmulatorInvocation | None = None,
        per_rom_emulator: dict[int, EmulatorInvocation | None] | None = None,
    ) -> None:
        self.default = default
        self.per_rom: dict[int, tuple[str | None, str | None]] = per_rom if per_rom is not None else {}
        self.default_emulator = default_emulator
        self.per_rom_managed: dict[int, ManagedPlatform] = {}
        self.per_rom_save_entry: dict[int, ManagedPlatform] = {}
        self.per_rom_emulator: dict[int, EmulatorInvocation | None] = (
            per_rom_emulator if per_rom_emulator is not None else {}
        )
        self.calls: list[int] = []
        self.emulator_calls: list[int] = []

    def active_core_for_rom(self, rom_id: int) -> tuple[str | None, str | None]:
        self.calls.append(rom_id)
        return self.per_rom.get(rom_id, self.default)

    def managed_entry(self, rom_id: int) -> ManagedPlatform | None:
        """No provisioned entry unless a test says so: the default is unmanaged."""
        return self.per_rom_managed.get(rom_id)

    def managed_save_entry(self, rom_id: int) -> ManagedPlatform | None:
        """The save read defaults to the same entry: unmanaged unless a test says otherwise."""
        return self.per_rom_save_entry.get(rom_id, self.per_rom_managed.get(rom_id))

    def active_emulator_for_rom(self, rom_id: int) -> EmulatorInvocation | None:
        self.emulator_calls.append(rom_id)
        return self._emulator(rom_id)

    def standalone_emulator_identity(self, rom_id: int) -> str | None:
        """The upload tag's source, projected without touching the launch call log.

        A test that asserts ``emulator_calls`` is pinning the LAUNCH seam; asking
        for a tag must not look like a launch resolution.
        """
        invocation = self._emulator(rom_id)
        if invocation is None or invocation.kind != "standalone":
            return None
        return invocation.emulator or invocation.label

    def _emulator(self, rom_id: int) -> EmulatorInvocation | None:
        if rom_id in self.per_rom_emulator:
            return self.per_rom_emulator[rom_id]
        if self.default_emulator is not None:
            return self.default_emulator
        core_so, label = self.per_rom.get(rom_id, self.default)
        if core_so is not None:
            # The identity a libretro entry carries is the core file's own
            # basename, which is what the resolver states for it — so a
            # tuple-configured test gets the identity its core would really have.
            return EmulatorInvocation.libretro(core_so, label, f"{core_so}.so")
        return None
