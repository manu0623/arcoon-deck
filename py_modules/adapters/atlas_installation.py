"""Which emulator arrangement answers — the one place a detected handle is chosen.

The vendored resolver never picks a winner: :func:`atlas.detect` returns every
arrangement it found, highest-priority first, because more than one can coexist
and ambiguity is a truthful result. Every question this plugin puts to a handle
therefore needs somebody outside the resolver to choose, and that choice used to
be spelled three different ways in three places — which is how one of them kept
asking a RetroDECK that was no longer installed.

**A marker is not an installation.** Detection triggers on each arrangement's own
config marker, and RetroDECK's is the *flatpak's* file:

```
~/.var/app/net.retrodeck.retrodeck/config/retrodeck/retrodeck.json
```

Removing the flatpak leaves that file, and ``~/retrodeck`` with it. Measured on
the reference Deck, which runs the app's own runtime and has no RetroDECK: the
marker was present, the handle resolved to ``~/retrodeck``, and it answered, for
every question asked of it —

- ``firmware_inventory()``: **0 cores**, ``info-path-unresolved`` (the ``.info``
  directory went with the flatpak) and ``~/retrodeck/bios`` as the BIOS root;
- ``firmware_for_system("gba")``: 0 requirements; the RetroArch flatpak beside it
  answered 19 cores and 7 gba requirements;
- ``systems()``: 0 systems, where the flatpak answered 12;
- ``savefile_location(genesis, genesis_plus_gx_libretro.so)``: a placement under
  ``~/retrodeck/saves/genesis`` — a directory nothing writes.

A directory named for an emulator that cannot run is invented, not read, and a
save sync pointed at it carries nothing. So the rule is one rule, applied wherever
a handle is chosen: **under the app's own runtime, a ``retrodeck`` handle is
passed over**, and the next arrangement detection found answers. That is the same
decision :meth:`adapters.retrodeck_paths.RetroDeckPathsAdapter.runtime_mode`
already makes for the roots themselves — presence is the *app* being installed,
with the config as the second half of the answer — and the two must not disagree,
or the plugin reads its paths from one arrangement and its answers from another.

**Which non-RetroDECK arrangement answers is not a decision this makes.** It takes
detection's own order among the survivors (user flatpak, system flatpak, native),
and offering the others is #918. Nothing here reorders or scores them.

**Nothing found is not "nothing wanted".** A ``None`` from either function means
no arrangement could answer, which readers turn into an unresolved answer — never
an empty one, which downstream reads as a green "this machine needs nothing".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from _vendor.atlas import detect

if TYPE_CHECKING:
    from collections.abc import Callable

#: The arrangement kind a removed flatpak leaves behind. Detection's own spelling.
_RETRODECK_KIND = "retrodeck"


def first_detected_installation(user_home: str, *, find: Callable[[str], list[Any]] | None = None) -> Any | None:
    """The highest-priority arrangement detected under *user_home*, or ``None``.

    RetroDECK leads that order wherever its marker exists, which is the answer a
    RetroDECK-driven device wants and the wrong one wherever it does not — see
    :func:`installation_for_runtime`, which is what the plugin's own wiring passes.

    *find* is the detection seam, defaulted to :func:`detect`; only a test passes
    one.
    """
    installations = (find or detect)(user_home)
    return installations[0] if installations else None


def installation_for_runtime(
    user_home: str,
    *,
    builtin: bool,
    find: Callable[[str], list[Any]] | None = None,
) -> Any | None:
    """The arrangement a question is put to, given the runtime being driven.

    ``builtin`` is the app's own runtime, and it passes over every ``retrodeck``
    handle: a marker left behind by a removed flatpak is not an installation, and
    a handle in that state states nothing while naming directories nothing reads
    (the measurements are in this module's docstring).

    While RetroDECK drives, detection's first answer stands — its catalogue is the
    only place its own core labels exist (ADR-0045) — and a hand-edited
    ``runtime_mode`` is honoured either way, so a user who chose RetroDECK gets
    RetroDECK even where detection would not have offered it.
    """
    installations = (find or detect)(user_home)
    if builtin:
        installations = [installation for installation in installations if installation.kind != _RETRODECK_KIND]
    return installations[0] if installations else None
