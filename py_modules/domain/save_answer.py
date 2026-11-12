"""What a game's save consists of, where it lives, and whether this plugin may sync it.

The vocabulary the resolver's savefile answer is translated into, and the rule
that turns one such answer into exactly one of five states. Adapters read the
machine; this module decides what the reading MEANS, so the decision is pure and
testable without a machine, and so ``services/`` never sees a resolver type.

The five states are the whole point. Save sync copies a per-game file to a
per-ROM record on the server, and that model is simply wrong for most of what
emulators actually write — a card many games share, a directory whose contents
nobody enumerated, a path or a name half of which is the game's own identity.
Only
:data:`SAVE_STATE_PER_GAME_FILES` is a save this plugin can carry; the other four
are refusals, and each says something different about why. Every one of them is
an honest "we are not touching this", never "there is nothing here".

**Scope is the emulator, never the platform.** Two emulators for one system
answer differently — the same PS2 game is a shared memory card under standalone
PCSX2 and could be per-game under a libretro core — so an answer names the
emulator it is about and means nothing without it.

The value vocabularies below (roles, granularities, file-set states, caveat
codes) are the resolver's own, restated here as plain strings because ``domain/``
may not import ``_vendor``. ``tests/adapters/test_atlas_saves.py`` asserts each
one against the resolver's exported constant, so an upstream rename fails there
rather than silently classifying everything as a refusal.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal

from domain.owned_dolphin import gc_card_dir
from domain.save_layout import SAVE_SYNC_CONTENT_DIR_REASON

if TYPE_CHECKING:
    from collections.abc import Sequence

# The five states. Exactly one holds for any ROM.
SAVE_STATE_PER_GAME_FILES = "per_game_files"
SAVE_STATE_SHARED = "shared"
SAVE_STATE_INSIDE_CONTENT = "inside_content"
SAVE_STATE_HOLE = "hole"
SAVE_STATE_UNESTABLISHED = "unestablished"

SaveState = Literal[
    "per_game_files",
    "shared",
    "inside_content",
    "hole",
    "unestablished",
]

# The three shapes inside ``unestablished``. They are kept apart because they
# are three different sentences to a user, and the fifth state is where every
# doubt lands, so collapsing them would make one message stand for all of them.
#
# ``not_asked`` is the one that is easy to lose: the question was never put, so
# the emulator is not implicated at all. RetroArch writing saves to the content
# directory reaches it, and so does a ROM with no resolvable emulator. Without
# it those payloads are byte-identical to an unaudited core's, and a page would
# tell a user their emulator is a mystery when the truth is that the plugin
# never asked.
UNESTABLISHED_NOTHING = "nothing_established"
UNESTABLISHED_DIRECTORY_KNOWN = "directory_known"
UNESTABLISHED_NOT_ASKED = "not_asked"

UnestablishedShape = Literal["nothing_established", "directory_known", "not_asked"]

# Roles that are the emulator's configuration rather than the player's progress.
# A configuration file is never synced: it is machine-local by nature, and
# carrying one between devices overwrites settings the user chose there.
#
# **Stated as the roles to EXCLUDE, and that is the decision rather than the
# shape it happens to have.** The resolver's vocabulary has a value for a file
# no declaration described (``unknown``) and a component carries ``None`` where
# no group claimed it — two ways of saying nobody said what this file is — and
# both must be carried, because dropping a file that turns out to be progress
# loses a player's game and carrying one that turns out to be configuration
# costs a settings file the user can set again. An allow-list of the roles to
# carry inverts exactly that: it drops every file the vocabulary has not named
# yet, silently, on the day upstream adds one.
CONFIGURATION_ROLES = frozenset({"settings", "notes"})

# Granularities where one file holds many games' progress.
_SHARED_GRANULARITIES = frozenset({"shared-card", "shared-file"})

# The resolver states this when it refuses to guess what the files are called.
_FILE_SET_UNKNOWN = "unknown"

# The hole a caller can fill: the game's own identity, which the resolver cannot read
# from a content path because it is inside the file (see ``domain.content_identity``).
SAVE_ID_NEED = "save_id"
_SAVE_ID_TOKEN = "<save_id>"

# The other hole a caller can fill: Dolphin files a GameCube card under the disc's
# region (``GC/<region>/Card A``), which the resolver states as a token because the
# running disc is what replaces it. The region is readable from the same header the
# game code comes from, so it is fillable on the same terms.
SAVE_REGION_NEED = "region"
_REGION_TOKEN = "<region>"

# Caveats that place the save inside the game's own file, so there is no
# separate file to carry.
_INSIDE_CONTENT_CAVEATS = frozenset({"save-inside-content", "save-inside-image"})

# The caveat for a directory that is known while the names inside it are not.
_FILE_NAMES_UNESTABLISHED = "file-names-unestablished"

# Canonical ``reason`` slug for the benign-skip outcome the four refusing states
# produce. Lives here beside the states that cause it, for the same reason
# ``SAVE_SYNC_CONTENT_DIR_REASON`` lives beside the layout that causes that one:
# every service routes on the SAME value without a service-to-service import.
# It says the SHAPE of this game's save is not one the plugin can carry per
# game, which is a statement about the emulator and never about the server.
SAVE_SHAPE_UNSUPPORTED_REASON = "save_shape_unsupported"

# Every ``reason`` slug that means "the sync did not run, and that is fine".
# Both are statements about the machine, not failures, so no surface may report
# one as an error: the launch path proceeds silently and the post-exit path
# raises no toast. A reason outside this set IS a failure. Kept here, beside the
# state that produces the second one, so every consumer routes on one list
# rather than growing its own equality test — which is exactly how the
# post-exit toast came to fire for half the mapped systems. The frontend keeps
# its own copy in ``src/types/saves.ts`` because the wire carries slugs and not
# this set; ``TestTheBenignSkipListsAgreeAcrossTheWire`` reads that file and
# fails if the two ever disagree.
BENIGN_SYNC_SKIP_REASONS: frozenset[str] = frozenset(
    {
        SAVE_SYNC_CONTENT_DIR_REASON,
        SAVE_SHAPE_UNSUPPORTED_REASON,
    }
)


@dataclass(frozen=True, slots=True)
class SaveGroup:
    """One directory's worth of a save, as the resolver decomposed it.

    ``files`` is ``None`` when the resolver states that save data lives in
    ``directory`` and refuses to name it — never "the directory is empty".
    """

    directory: str
    files: tuple[str, ...] | None
    role: str | None
    granularity: str | None


@dataclass(frozen=True, slots=True)
class SaveComponent:
    """One named file a save consists of, and what that file is.

    ``role`` is the resolver's word for what the file holds (``battery``,
    ``memory-card``, ``settings``, …), its own ``unknown`` for a file on the
    machine that no declaration describes, or ``None`` where no group claimed it
    at all.
    """

    name: str
    directory: str
    role: str | None
    granularity: str | None

    @property
    def is_progress(self) -> bool:
        """Whether this file is the player's progress rather than configuration.

        A role nobody named — the resolver's ``unknown``, or no role at all —
        answers ``True`` and the file is carried. That is the decision and not
        an accident of the test's shape: the two failures are not symmetric, and
        a settings file carried onto another device costs a setting the user can
        make again where a battery file left behind costs a save nothing can
        restore. :data:`CONFIGURATION_ROLES` says why the test is a denial.
        """
        return self.role not in CONFIGURATION_ROLES


@dataclass(frozen=True, slots=True)
class SaveAnswer:
    """Where one ROM's save lives, what it consists of, and what may be done with it.

    ``state`` is the verdict and the only thing a sync path may act on;
    ``unestablished`` discriminates the three shapes of
    :data:`SAVE_STATE_UNESTABLISHED` and is ``None`` for every other state.
    ``emulator`` names whose answer this is. ``directory`` is the directory the
    emulator opens — the one to read and write through — while
    ``backing_directory`` is where a link resolves to and answers identity
    questions only. ``components`` are the concrete files, configuration
    included, so a caller can show a file it will not sync. ``needs`` names the
    holes a name could not be completed from, ``granularity`` is how this
    emulator groups save data, and ``caveats`` carries the resolver's stable
    codes verbatim for the log and for a later rendering.

    ``content_installed`` says whether this ROM's content is on disk. It is
    ``False`` for a ROM the library holds but has not installed — the question
    was then about the path the ROM WOULD occupy, so every name in the answer is
    a prediction. It describes the ROM, never what the resolver came back with:
    an installed game whose emulator establishes nothing is still installed, and
    a caller fabricating a refusal fills the field in from the install row
    rather than leaving it at its default. A surface that renders the names
    without reading it tells a user their uninstalled game already has three
    save files.
    """

    state: SaveState
    unestablished: UnestablishedShape | None
    emulator: str | None
    directory: str | None
    backing_directory: str | None
    granularity: str | None
    needs: tuple[str, ...]
    components: tuple[SaveComponent, ...]
    caveats: tuple[str, ...]
    content_installed: bool

    @property
    def syncable(self) -> bool:
        """Whether save sync may run at all for this ROM."""
        return self.state == SAVE_STATE_PER_GAME_FILES

    @property
    def owned_files(self) -> tuple[SaveComponent, ...]:
        """Every file this ROM keeps under its own name — configuration included.

        What a move of the save directory has to carry: leaving an emulator's
        per-game configuration file behind is as broken as leaving the battery
        file behind. Empty for every refusing state, where nothing was
        established that a move could act on.
        """
        return self.components if self.syncable else ()

    @property
    def synced_files(self) -> tuple[SaveComponent, ...]:
        """The components a sync may carry — progress only, and only when syncable.

        Narrower than :attr:`owned_files` by exactly the configuration files:
        those are machine-local by nature, so carrying one to another device
        overwrites settings the user chose there. Empty for every refusing
        state, which is what keeps a refusal from probing — there is nothing to
        look for.
        """
        return tuple(component for component in self.owned_files if component.is_progress)

    @property
    def synced_names(self) -> tuple[str, ...]:
        """The basenames of :attr:`synced_files`, for callers that only name files."""
        return tuple(component.name for component in self.synced_files)


# One sentence per refusing state, for the skip result's ``message``. Neutral by
# design: none of these is an error, and three of the four are permanent facts
# about the emulator rather than anything the user did.
_STATE_MESSAGES: dict[str, str] = {
    SAVE_STATE_SHARED: "Save sync is unavailable: this emulator keeps one save card that all games share.",
    SAVE_STATE_INSIDE_CONTENT: "Save sync is unavailable: this emulator writes saves inside the game file itself.",
    SAVE_STATE_HOLE: (
        "Save sync is unavailable: this emulator files saves under an identity of the game "
        "that this plugin cannot read."
    ),
    SAVE_STATE_UNESTABLISHED: "Save sync is unavailable: what this emulator writes could not be established.",
}


def owned_dolphin_answer(user_dir: str, *, content_installed: bool) -> SaveAnswer:
    """The answer for a GameCube ROM launched by the plugin's OWNED Dolphin command.

    Not a reading of the emulator, and deliberately so: when the plugin pins the user
    directory with ``-u``, the card folder follows from the command by the emulator's own
    default, so asking a catalogue where a program might write would be a less certain
    answer about a program whose invocation we already wrote. Measured on the reference
    Deck: the session wrote into ``…/saves/gc/User/GC/USA/Card A`` while every resolved
    answer pointed elsewhere, and the save was never carried.

    The region stays a hole and the names stay unestablished — the disc states the first
    and the folder listing the second — so the same fills that serve a resolved answer
    serve this one, and neither is guessed here.
    """
    return SaveAnswer(
        state=SAVE_STATE_HOLE,
        unestablished=None,
        emulator="Dolphin",
        directory=gc_card_dir(user_dir),
        backing_directory=None,
        granularity="gci-folder",
        needs=(SAVE_REGION_NEED,),
        components=(),
        caveats=("file-names-unestablished",),
        content_installed=content_installed,
    )


def manifest_answer(entry: object, *, content_installed: bool) -> SaveAnswer | None:
    """The answer a managed entry states, or ``None`` when it states none this plugin carries.

    Only a ``gci-set`` entry is answered today: the folder is one the provisioner named and
    the entries are named by the emulator itself, which is the shape the GameCube fills
    settle. Every other unit returns ``None`` — not a refusal — so the caller falls back to
    the live catalogue answer it would have used anyway. Answering a half-modelled unit with
    a directory this plugin cannot name files in would be worse than not managing it at all.
    """
    save_unit = getattr(entry, "save_unit", None)
    save_dir = getattr(entry, "save_dir", None)
    if entry is None or save_unit != "gci-set" or not isinstance(save_dir, str) or not save_dir:
        return None
    raw_needs = getattr(entry, "needs", ())
    needs = tuple(SAVE_REGION_NEED if need == "region" else need for need in raw_needs) or (SAVE_REGION_NEED,)
    return SaveAnswer(
        state=SAVE_STATE_HOLE,
        unestablished=None,
        emulator=getattr(entry, "emulator", None) or "Dolphin",
        directory=save_dir,
        backing_directory=None,
        granularity="gci-folder",
        needs=needs,
        components=(),
        caveats=("file-names-unestablished",),
        content_installed=content_installed,
    )


def save_shape_message(answer: SaveAnswer) -> str:
    """The sentence a refusal is reported with, named after the emulator it is about."""
    sentence = _STATE_MESSAGES.get(answer.state, _STATE_MESSAGES[SAVE_STATE_UNESTABLISHED])
    return f"{sentence} ({answer.emulator})" if answer.emulator else sentence


def pick_download_name(known_names: Sequence[str], computed: str) -> str:
    """Where a server save lands: the name the answer holds, else the computed one.

    *computed* is the path math's ``<rom stem>.<server file_extension>``, which
    is right only where the emulator's own name has exactly that shape. It is
    not always: Opera writes ``<stem>.0.srm``, Caprice32 ``<stem>.dsk.sav``,
    DOSBox-Pure ``<stem>.pure.zip`` — and a server row carrying extension
    ``srm`` would otherwise be downloaded to ``<stem>.srm``, a file the core
    never opens.

    So the server's extension is read as a POINTER into what the emulator
    writes: the one answer name that starts with the computed stem and ends
    with the computed extension wins. Where nothing matches, or where more than
    one does and picking would be a guess, the computed name stands — this
    corrects a name the resolver can improve on and invents none.
    """
    if computed in known_names:
        return computed
    stem, _, extension = computed.rpartition(".")
    if not stem or not extension:
        return computed
    matches = [name for name in known_names if name.startswith(f"{stem}.") and name.endswith(f".{extension}")]
    return matches[0] if len(matches) == 1 else computed


def fill_save_id(answer: SaveAnswer, save_id: str | None) -> SaveAnswer:
    """Complete every ``<save_id>`` hole in *answer* with *save_id*, or return it as-is.

    The resolver states an id-keyed save as a template plus a ``save_id`` need — a 3DS
    title's directory reads ``…/title/<save_id>/data/00000001`` and asks whoever knows
    the title id to fill it. This is that fill, applied to the directory, the backing
    directory and every component, and it is deliberately a separate step rather than a
    parameter of the question: the resolver never reads game files, and a caller that has
    not read one must get the hole it always did.

    Nothing is filled when *save_id* is empty, so a caller with no identity keeps the
    honest refusal. The state is re-derived afterwards: a hole that was the answer's only
    need becomes an ordinary per-game save, while one need left unfilled keeps it a hole.
    """
    if not save_id or SAVE_ID_NEED not in answer.needs:
        return answer
    remaining = tuple(need for need in answer.needs if need != SAVE_ID_NEED)
    components = tuple(
        replace(
            component,
            name=component.name.replace(_SAVE_ID_TOKEN, save_id),
            directory=component.directory.replace(_SAVE_ID_TOKEN, save_id),
        )
        for component in answer.components
    )
    state, shape = _state_after_fill(answer, remaining=remaining, components=components)
    return replace(
        answer,
        state=state,
        unestablished=shape,
        directory=None if answer.directory is None else answer.directory.replace(_SAVE_ID_TOKEN, save_id),
        backing_directory=(
            None if answer.backing_directory is None else answer.backing_directory.replace(_SAVE_ID_TOKEN, save_id)
        ),
        needs=remaining,
        components=components,
    )


def fill_region(answer: SaveAnswer, region: str | None) -> SaveAnswer:
    """Complete every ``<region>`` hole in *answer* with *region*, or return it as-is.

    Dolphin's card folder is ``GC/<region>/Card A``: the region segment belongs to the
    disc being played, so the resolver states it as a hole rather than reading a
    configured template literally. The value is Dolphin's own directory spelling
    (``USA``/``JAP``/``EUR``), not the library's region vocabulary — a filled path that
    says ``Europe`` points at a folder Dolphin never creates.

    Nothing is filled when *region* is empty, so an unread header keeps the refusal.
    """
    if not region or SAVE_REGION_NEED not in answer.needs:
        return answer
    remaining = tuple(need for need in answer.needs if need != SAVE_REGION_NEED)
    components = tuple(
        replace(
            component,
            name=component.name.replace(_REGION_TOKEN, region),
            directory=component.directory.replace(_REGION_TOKEN, region),
        )
        for component in answer.components
    )
    filled = replace(
        answer,
        directory=None if answer.directory is None else answer.directory.replace(_REGION_TOKEN, region),
        backing_directory=(
            None if answer.backing_directory is None else answer.backing_directory.replace(_REGION_TOKEN, region)
        ),
        needs=remaining,
        components=components,
    )
    state, shape = _state_after_fill(filled, remaining=remaining, components=components)
    return replace(filled, state=state, unestablished=shape)


def gci_names_for(names: Sequence[str], game_code: str) -> tuple[str, ...]:
    """The card entries belonging to *game_code*: ``<maker>-<code>-<internal>.gci``.

    Two of the three components are readable only from the file's own header, but the
    code in the middle is the disc's, so a card folder's listing is enough to find this
    game's save — and a hack and its base disc, which share a filename, are still
    separated by it. Anything not shaped like a card entry is not ours to claim.
    """
    code = game_code.strip().upper()
    found: list[str] = []
    for name in names:
        stem, dot, extension = name.rpartition(".")
        if not dot or extension.lower() != "gci":
            continue
        parts = stem.split("-")
        if len(parts) >= 3 and parts[1].strip().upper() == code:
            found.append(name)
    return tuple(found)


def fill_gci_set(answer: SaveAnswer, *, game_code: str | None, names: Sequence[str]) -> SaveAnswer:
    """Name a GameCube folder card's files from the card itself, or return *answer*.

    The resolver refuses these names on purpose — a ``.gci`` is called
    ``<maker>-<code>-<internal>.gci`` from the save's own directory entry, which follows
    from nothing in the content path — and that refusal alone is what kept GameCube
    from syncing in either direction. The listing resolves it: every entry carrying this
    disc's code IS this disc's save, so the set is the answer.

    A card with no matching entry stays refused, which is right: there is nothing to
    carry yet, and the download path places the members by their own names.
    """
    if not game_code or not answer.directory:
        return answer
    if _FILE_NAMES_UNESTABLISHED not in answer.caveats:
        return answer
    wanted = gci_names_for(names, game_code)
    if not wanted:
        return answer
    components = tuple(
        SaveComponent(name=name, directory=answer.directory, role="memory-card", granularity=answer.granularity)
        for name in wanted
    )
    caveats = tuple(caveat for caveat in answer.caveats if caveat != _FILE_NAMES_UNESTABLISHED)
    filled = replace(answer, caveats=caveats, components=components)
    state, shape = _state_after_fill(filled, remaining=answer.needs, components=components)
    return replace(filled, state=state, unestablished=shape)


def _state_after_fill(
    answer: SaveAnswer,
    *,
    remaining: tuple[str, ...],
    components: tuple[SaveComponent, ...],
) -> tuple[SaveState, UnestablishedShape | None]:
    """The state that holds once the id is filled in.

    :func:`_classify`'s first two steps cannot apply here: they outrank a hole, so an
    answer that was one was neither inside the content nor an unstated file set. What is
    left is the same order it uses — a need still missing, then a shared card, then a
    directory whose names nobody established, then the syncable case.
    """
    if remaining:
        return (SAVE_STATE_HOLE, None)
    if answer.granularity in _SHARED_GRANULARITIES:
        return (SAVE_STATE_SHARED, None)
    if _FILE_NAMES_UNESTABLISHED in answer.caveats:
        return (SAVE_STATE_UNESTABLISHED, UNESTABLISHED_DIRECTORY_KNOWN)
    if not components:
        return (SAVE_STATE_UNESTABLISHED, UNESTABLISHED_NOTHING)
    return (SAVE_STATE_PER_GAME_FILES, None)


def unestablished_answer(
    *,
    emulator: str | None = None,
    caveats: tuple[str, ...] = (),
    shape: UnestablishedShape = UNESTABLISHED_NOTHING,
    content_installed: bool = False,
) -> SaveAnswer:
    """The answer for a question that could not be put, or was put and refused.

    All of them refuse the sync; *shape* is what separates them for a reader.
    :data:`UNESTABLISHED_NOT_ASKED` where no question reached the resolver — no
    emulator resolved, nothing detected, no catalogue entry under that label,
    saves written to the content directory. :data:`UNESTABLISHED_NOTHING` where
    it was asked and could establish nothing, including where it declined or
    raised.

    *content_installed* still describes the ROM, not whether anything came back:
    an installed game whose entry declines is installed all the same, so a
    caller that knows the ROM is on disk passes ``True`` here. It defaults to
    ``False``, which is right for the callers that reach this with no ROM row
    and so no path at all.
    """
    return SaveAnswer(
        state=SAVE_STATE_UNESTABLISHED,
        unestablished=shape,
        emulator=emulator,
        directory=None,
        backing_directory=None,
        granularity=None,
        needs=(),
        components=(),
        caveats=caveats,
        content_installed=content_installed,
    )


def build_save_answer(
    *,
    emulator: str | None,
    directory: str,
    backing_directory: str | None,
    granularity: str | None,
    needs: tuple[str, ...],
    file_set_state: str,
    files: tuple[str, ...],
    groups: tuple[SaveGroup, ...],
    caveats: tuple[str, ...],
    content_installed: bool,
) -> SaveAnswer:
    """Classify one resolved savefile placement into a :class:`SaveAnswer`.

    Takes the placement's fields as plain values so the rule stays free of the
    resolver's types. ``groups`` decomposes the save by directory and role and is
    the richer source; ``files`` is the placement's own primary list and is used
    where no group was given.
    """
    components = _components(directory, files, groups)
    state, shape = _classify(
        granularity=granularity,
        needs=needs,
        file_set_state=file_set_state,
        groups=groups,
        caveats=caveats,
        components=components,
    )
    return SaveAnswer(
        state=state,
        unestablished=shape,
        emulator=emulator,
        directory=directory,
        backing_directory=backing_directory,
        granularity=granularity,
        needs=needs,
        components=components,
        caveats=caveats,
        content_installed=content_installed,
    )


def _components(
    directory: str,
    files: tuple[str, ...],
    groups: tuple[SaveGroup, ...],
) -> tuple[SaveComponent, ...]:
    """The concrete files the answer names, each with what it is and where it sits.

    Built from the groups where there are any: they carry the role and their own
    directory, and in every reading taken so far they cover the placement's own
    file list and then some. A placement with no groups still names files — the
    plain per-game case — and those take the placement's directory and no role.
    """
    if not groups:
        return tuple(SaveComponent(name=name, directory=directory, role=None, granularity=None) for name in files)
    return tuple(
        SaveComponent(name=name, directory=group.directory, role=group.role, granularity=group.granularity)
        for group in groups
        for name in (group.files or ())
    )


def _classify(
    *,
    granularity: str | None,
    needs: tuple[str, ...],
    file_set_state: str,
    groups: tuple[SaveGroup, ...],
    caveats: tuple[str, ...],
    components: tuple[SaveComponent, ...],
) -> tuple[SaveState, UnestablishedShape | None]:
    """Decide the one state that holds, in a fixed precedence.

    The order is what makes "exactly one" well defined, and each step outranks
    the next for a reason:

    1. The save being inside the game's own file outranks everything — it is a
       positive statement that makes the directory answer meaningless.
    2. A file set the resolver refuses to state is nothing to reason further
       about.
    3. A hole outranks a shared card: an answer with both cannot be completed
       either way, and naming the hole says more about what is missing.
    4. Shared reads the placement's own granularity, not a group's. A group may
       be shared inside a per-game answer — MAME's emulator-wide ``default.cfg``
       sits beside per-game files — and that does not make the game's save
       shared.
    5. A stated directory whose names are not established is the second shape of
       "not established", and it outranks the bare form because it says more.

    Everything left names files with no hole, which is the one syncable state.
    """
    if not _INSIDE_CONTENT_CAVEATS.isdisjoint(caveats):
        return (SAVE_STATE_INSIDE_CONTENT, None)
    if file_set_state == _FILE_SET_UNKNOWN:
        return (SAVE_STATE_UNESTABLISHED, UNESTABLISHED_NOTHING)
    if needs:
        return (SAVE_STATE_HOLE, None)
    if granularity in _SHARED_GRANULARITIES:
        return (SAVE_STATE_SHARED, None)
    if _FILE_NAMES_UNESTABLISHED in caveats or any(group.files is None for group in groups):
        return (SAVE_STATE_UNESTABLISHED, UNESTABLISHED_DIRECTORY_KNOWN)
    if not components:
        return (SAVE_STATE_UNESTABLISHED, UNESTABLISHED_NOTHING)
    return (SAVE_STATE_PER_GAME_FILES, None)
