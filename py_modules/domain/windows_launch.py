"""Windows-platform launch facts — which file in an extracted game *is* the game.

A RomM ``windows`` entry is not a ROM: it is an installed PC game, usually a
folder holding the game's own tree (``Game.exe`` beside its ``Data/``,
``Binaries/`` …), and sometimes a single installer. No emulator plays it, so the
plugin's usual answers do not apply — there is no core, no BIOS and no
appendconfig. Steam runs the ``.exe`` itself, and since the October 2026 client a
Windows binary registered as a non-Steam shortcut is started under Proton by
default, which is the whole launch chain on a Deck.

That leaves exactly one hard question on this platform: **which file is the
game.** :func:`pick_game_exe` answers it on download, and the same ranking orders
the list the manual picker shows, so an automatic guess and a hand-picked
override are chosen by one rule rather than two.

The ranking is a heuristic and is allowed to be wrong, which is why the manual
picker exists: a folder can hold a launcher, an uninstaller, a suite of
diagnostics tools and the real game, and nothing in a filename proves which one a
person wants to press. What it must not do is pick something that is *never* the
game — an uninstaller, a redistributable installer, a crash reporter — because
those are the guesses that look confident and can never work.

Pure path algebra plus name matching, stdlib only.
"""

from __future__ import annotations

import posixpath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

#: The RomM platform slugs this module governs. ``windows`` is RomM's own slug;
#: ``win`` is the shorthand some servers and legacy imports use.
WINDOWS_PLATFORM_SLUGS: frozenset[str] = frozenset({"windows", "win"})

#: What a launch target may be on this platform. ``.exe`` is the game; ``.bat``
#: and ``.cmd`` are the small scripts some repacks ship as their entry point and
#: Steam executes them under Proton just the same.
LAUNCH_EXTENSIONS: tuple[str, ...] = (".exe", ".bat", ".cmd")

# Names that are never the game. Matched against the file's stem, lowercased:
# a *prefix* match for the installers and redistributables (``unins000``,
# ``setup``, ``vcredist_x64``, ``dxsetup`` …), a *substring* match for the
# reporters bundled by engines (``UnityCrashHandler64``,
# ``CrashReportClient``) and an exact set for archivers that ride along.
_JUNK_PREFIXES: tuple[str, ...] = (
    "unins",
    "uninst",
    "setup",
    "install",
    "redist",
    "vc_redist",
    "vcredist",
    "dxsetup",
    "dxwebsetup",
    "directx",
    "dotnetfx",
    "ndp",
    "oalinst",
    "openal",
    "ue4prereq",
    "ue5prereq",
    "prereq",
    "python",
    "quicktime",
    "physx",
)
_JUNK_SUBSTRINGS: tuple[str, ...] = (
    "crashhandler",
    "crashreport",
    "crashpad",
    "uninstall",
    "eula",
    "readme",
    "license",
)
_JUNK_EXACT: frozenset[str] = frozenset({"7z", "7za", "winrar", "isuninst", "dxdiag", "msiexec"})


def is_windows_platform(platform_slug: str | None) -> bool:
    """Whether *platform_slug* names the Windows platform this module governs.

    The slug, not the resolved ES-DE system: the two are the same string today
    (``defaults/config.json`` maps no ``windows`` entry), and the slug is what
    every caller already holds — the ROM row, the install record, the download
    detail. Reading the system instead would make the answer depend on which
    catalogue happened to be installed.
    """
    return (platform_slug or "").strip().lower() in WINDOWS_PLATFORM_SLUGS


def is_windows_launch_file(path: str | None) -> bool:
    """Whether *path* is something Steam can start as a Windows program."""
    return bool(path) and posixpath.splitext(path or "")[1].lower() in LAUNCH_EXTENSIONS


def pick_game_exe(files: Sequence[tuple[str, int]]) -> str | None:
    """The file to launch for a Windows game, or ``None`` when none qualifies.

    *files* is ``(absolute_path, size_bytes)`` for everything extracted, which is
    what the download path already holds before it records the install.

    Candidates are the :data:`LAUNCH_EXTENSIONS` entries, minus the names
    :func:`_is_junk` rejects. They are then ranked by, in order:

    1. **Depth** — anything sitting at the shallowest level wins. A PC game's
       entry point is its root executable; nesting is what distinguishes an
       asset or a tool from the thing a shortcut would name.
    2. **Name similarity to the game** — among equally shallow candidates, the
       one whose stem overlaps the ROM's own name wins (``Skyrim`` →
       ``SkyrimLauncher.exe`` over ``BethesdaNet.exe``).
    3. **Size, largest first** — the last resort, and usually right: a game
       binary dwarfs the helpers beside it.

    The name used for (2) is the deepest directory component shared by every
    candidate — the game's own folder name, which is what RomM names a Windows
    entry after. Deriving it here rather than taking a parameter keeps the answer
    the same for the download path and the manual picker's ordering.

    Returns ``None`` when no candidate survives, which the caller records as an
    install with no launch target rather than a guess.
    """
    candidates = _candidates(files)
    if not candidates:
        return None
    hint = _name_hint([path for path, _size in candidates])
    return min(candidates, key=lambda entry: _rank(entry, hint))[0]


def ranked_exe_paths(files: Sequence[tuple[str, int]]) -> list[str]:
    """Every launchable Windows file among *files*, best first.

    The manual picker's order, drawn from the same ranking
    :func:`pick_game_exe` uses so the automatic pick is the list's first row.
    Junk names are **not** removed here: a picker that hid the user's own game
    would be lying about what is on disk, so they sort last instead.
    """
    hint = _name_hint([path for path, _size in _candidates(files, include_junk=True)])
    ranked = sorted(_candidates(files, include_junk=True), key=lambda entry: _rank(entry, hint))
    return [path for path, _size in ranked]


def shortcut_for_exe(exe_path: str) -> tuple[str, str]:
    """The ``(exe, start_dir)`` a Steam shortcut for *exe_path* carries.

    The exe is the game itself — not the plugin's ``rom-launcher`` wrapper — and
    that is load-bearing: Steam decides whether to start a shortcut under Proton
    from what the exe is, so a wrapper script would run natively and the game
    would never start. The start directory is the game's own folder, where most
    PC games resolve their data from.
    """
    return (exe_path, posixpath.dirname(exe_path))


def relative_to_install(install_dir: str, path: str) -> str | None:
    """*path* relative to *install_dir*, or ``None`` when it is outside it.

    The manual picker accepts a relative path and this is the guard that keeps
    one from naming anything outside the install — the same reasoning the
    download path applies to every server-supplied name. Both sides are
    normalised first, so ``..`` and a redundant separator cannot walk out.
    """
    if not install_dir or not path:
        return None
    root = posixpath.normpath(install_dir)
    target = posixpath.normpath(posixpath.join(root, path))
    if target == root or not target.startswith(root + "/"):
        return None
    return posixpath.relpath(target, root)


def _candidates(files: Sequence[tuple[str, int]], *, include_junk: bool = False) -> list[tuple[str, int]]:
    """The launchable files among *files*, optionally keeping junk names."""
    found = [(path, size) for path, size in files if is_windows_launch_file(path)]
    if include_junk:
        return found
    return [(path, size) for path, size in found if not _is_junk(path)]


def _is_junk(path: str) -> bool:
    """Whether *path*'s name is one no shortcut should ever be pointed at."""
    stem = posixpath.splitext(posixpath.basename(path))[0].lower()
    compact = _compact(stem)
    if compact in _JUNK_EXACT:
        return True
    if any(compact.startswith(prefix.replace("_", "")) for prefix in _JUNK_PREFIXES):
        return True
    return any(marker in compact for marker in _JUNK_SUBSTRINGS)


def _compact(value: str) -> str:
    """Lowercase *value* with every non-alphanumeric character dropped.

    ``VC_redist.x64`` and ``vcredistx64`` must compare equal for the junk lists,
    and so must ``CrashReport Client`` and ``CrashReportClient`` — the same name
    is spelled with separators in some releases and without in others.
    """
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _name_hint(paths: Sequence[str]) -> str:
    """The game's own name, read off the folder every candidate shares.

    The deepest directory common to all candidates, which for an extracted game
    is the game's folder (``…/Skyrim/…``) and for a single-file install is the
    platform directory — in that case the stem of the only candidate is used,
    since a platform folder name says nothing about which game it holds.
    """
    if not paths:
        return ""
    if len(paths) == 1:
        return posixpath.splitext(posixpath.basename(paths[0]))[0]
    directories = [posixpath.dirname(path) for path in paths]
    try:
        common = posixpath.commonpath(directories)
    except ValueError:
        # Two candidates on different roots share no folder to read a name off.
        return ""
    return posixpath.basename(common) if common else ""


def _rank(entry: tuple[str, int], hint: str) -> tuple[int, int, int, int]:
    """Sort key for one candidate — smaller is better, in the documented order."""
    path, size = entry
    depth = len([part for part in path.split("/") if part])
    stem = posixpath.splitext(posixpath.basename(path))[0]
    hint_key = _compact(hint)
    stem_key = _compact(stem)
    similar = 0 if hint_key and (hint_key in stem_key or stem_key in hint_key) else 1
    return (1 if _is_junk(path) else 0, depth, similar, -size)
