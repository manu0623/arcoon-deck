"""Pure parsers that flatten an emulator's config file into ``key -> value``.

Every emulator states its save directory in its own file format: RetroArch writes a
flat ``key = "value"`` file, PCSX2 and DuckStation INI, melonDS and xemu TOML,
Ryujinx JSON, Cemu XML, RPCS3 YAML. :func:`parse_config` maps a format to a parser and
returns one flat dict, whatever the file looks like.

**Flattening rules, and why the key spelling is ``Section/Key``.** The resolver in
:mod:`domain.save_locations` looks a key up as written and again with its section
stripped, so ``Folders/MemoryCards`` and a bare ``MemoryCards`` answer the same rule.
Flattening rather than returning nested structures keeps that lookup a dict access.

Nested tables collapse the same way (``a/b/c``), except that a *list* is skipped:
no save-directory key is a list, and joining list elements into a path-shaped key
would invent values no emulator wrote.

**A format that cannot be read says so.** RPCS3 and Vita3K configure themselves in
YAML, which this project does not parse — rather than add a dependency for two
families whose save rules are defaults-only, :data:`ConfigFormat.YAML` parses to an
empty dict. That is a stated limitation, not a silent empty file: :func:`is_readable`
lets the adapter record why no configured path was found.

Pure compute: text in, dict out. No file is opened and nothing is logged here.
"""

from __future__ import annotations

import configparser
import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class ConfigFormat(StrEnum):
    """The file format an emulator states its settings in."""

    FLAT = "flat"
    """``key = "value"`` lines — RetroArch's ``retroarch.cfg``, Flycast's ``emu.cfg``."""

    INI = "ini"
    """Sections and ``key = value`` — PCSX2, DuckStation, Dolphin, PPSSPP, yuzu, mGBA."""

    TOML = "toml"
    """melonDS, xemu, Xenia, shadPS4."""

    JSON = "json"
    """Ryujinx's ``Config.json``."""

    XML = "xml"
    """Cemu's ``settings.xml``."""

    YAML = "yaml"
    """RPCS3 and Vita3K — deliberately **not** parsed; see the module docstring."""


ConfigValues = dict[str, str]
Parser = Callable[[str], ConfigValues]


class _CaseSensitiveParser(configparser.ConfigParser):
    """A parser that keeps key case, as every emulator's own INI reader does.

    Overridden rather than assigning ``str`` to ``optionxform``: the attribute is a
    method on the class, and a subclass states the intent where a type checker can
    see it instead of a reassignment it must be told to ignore.
    """

    def optionxform(self, optionstr: str) -> str:
        return optionstr


def _strip_comment(value: str) -> str:
    """Drop an unquoted trailing ``#`` comment from a flat value."""
    quote: str | None = None
    for index, char in enumerate(value):
        if quote is None and char in "\"'":
            quote = char
        elif quote is not None and char == quote:
            quote = None
        elif quote is None and char == "#":
            return value[:index]
    return value


def parse_flat(text: str) -> ConfigValues:
    """Parse ``key = "value"`` lines into one flat dict.

    Quotes are removed because RetroArch strips them on read, so ``"~/saves"`` is a
    path and not a path with quotes in it. A line with no ``=`` — a comment, a blank,
    a truncated write — yields nothing rather than an empty-named key. A repeated key
    keeps its last value, which is what the emulator itself does when it rewrites the
    file.
    """
    values: ConfigValues = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, remainder = line.partition("=")
        if not separator:
            continue
        name = key.strip()
        if not name:
            continue
        cleaned = _strip_comment(remainder).strip()
        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "\"'":
            cleaned = cleaned[1:-1]
        values[name] = cleaned
    return values


def parse_ini(text: str) -> ConfigValues:
    """Parse an INI file into ``Section/Key`` entries, keeping keys' case.

    ``optionxform = str`` is load-bearing: emulator INIs are case-sensitive
    (``MemoryCards`` is not ``memorycards``) and ``configparser``'s default
    lowercasing would rewrite every key into one that matches no rule.

    Keys inherited from a ``[DEFAULT]`` section are stored once, unqualified, and not
    repeated inside every section — otherwise a default from one section would answer
    a rule asking about another.
    """
    parser = _CaseSensitiveParser(strict=False, interpolation=None, allow_no_value=True)
    try:
        parser.read_string(text)
    except configparser.Error:
        return {}
    defaults = parser.defaults()
    values: ConfigValues = {key: (value or "").strip() for key, value in defaults.items()}
    for section in parser.sections():
        for key, value in parser.items(section):
            if key in defaults:
                continue
            values[f"{section}/{key}"] = (value or "").strip()
    return values


def _flatten_into(values: ConfigValues, prefix: str, node: object) -> None:
    """Recursively flatten parsed structures, skipping lists."""
    if isinstance(node, dict):
        for key, value in node.items():
            name = str(key)
            _flatten_into(values, f"{prefix}/{name}" if prefix else name, value)
    elif isinstance(node, list):
        return
    elif isinstance(node, bool):
        values[prefix] = "true" if node else "false"
    elif node is not None:
        values[prefix] = str(node)


def parse_toml(text: str) -> ConfigValues:
    """Parse TOML into ``a/b`` entries, nested tables collapsed."""
    try:
        parsed = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError):
        return {}
    values: ConfigValues = {}
    _flatten_into(values, "", parsed)
    return values


def parse_json(text: str) -> ConfigValues:
    """Parse JSON into ``a/b`` entries, nested objects collapsed."""
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    values: ConfigValues = {}
    _flatten_into(values, "", parsed)
    return values


def parse_xml(text: str) -> ConfigValues:
    """Parse XML into element-path entries from element names and text.

    Cemu's ``settings.xml`` nests sections as elements with one value element per
    setting, so the element *path* is the key and the leaf's text is the value. An
    element that holds children contributes no value of its own.

    ``ElementTree`` is imported here rather than at module scope on purpose: Decky's
    sandboxed Python ships without ``xml.etree``, so a module-level import made this
    whole module — and every reader built on it — fail to import inside the plugin
    (measured on the reference Deck, 0.44.0: ``ModuleNotFoundError: xml.etree`` at
    plugin start). Only a Cemu settings read needs it, and only that read pays.
    """
    import xml.etree.ElementTree as ElementTree

    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return {}
    values: ConfigValues = {}

    def walk(element: ElementTree.Element, prefix: str) -> None:
        name = f"{prefix}/{element.tag}" if prefix else element.tag
        children = list(element)
        if not children:
            text_value = (element.text or "").strip()
            if text_value:
                values[name] = text_value
            return
        for child in children:
            walk(child, name)

    walk(root, "")
    return values


def _parse_yaml(_text: str) -> ConfigValues:
    return {}


_PARSERS: dict[ConfigFormat, Parser] = {
    ConfigFormat.FLAT: parse_flat,
    ConfigFormat.INI: parse_ini,
    ConfigFormat.TOML: parse_toml,
    ConfigFormat.JSON: parse_json,
    ConfigFormat.XML: parse_xml,
    # No YAML parser: declared unreadable rather than half-read, so a configured
    # path can never be invented from a partial parse.
    ConfigFormat.YAML: _parse_yaml,
}


def parse_config(fmt: ConfigFormat, text: str) -> ConfigValues:
    """Parse *text* as *fmt*, returning a flat ``key -> value`` dict.

    Malformed input yields an empty dict rather than raising: a config file the
    emulator itself is mid-way through rewriting is a normal state on a Deck, and
    the caller's next step (falling back to a declared default) is the same either
    way.
    """
    return _PARSERS[fmt](text)


def is_readable(fmt: ConfigFormat) -> bool:
    """Whether *fmt* is parsed at all — ``False`` only for :data:`ConfigFormat.YAML`."""
    return fmt is not ConfigFormat.YAML


# ── Where each emulator states its settings ─────────────────────────────────


@dataclass(frozen=True, slots=True)
class ConfigLayout:
    """One emulator's settings file: where it lives and how it is spelled.

    ``app_dir`` is the directory the emulator keeps under its XDG roots — the same
    name whether the provider is a flatpak (``~/.var/app/<id>/config/<app_dir>``) or a
    native install (``~/.config/<app_dir>``). ``in_data_dir`` is for the emulators
    that keep their settings beside their data instead of in the config root, which
    DuckStation and xemu do.
    """

    app_dir: str
    filename: str
    fmt: ConfigFormat
    in_data_dir: bool = False


# Keyed by definition id, not family: the yuzu lineage shares a save format but each
# fork keeps its own directory (``~/.config/eden``, ``~/.config/citron``), verified on
# the reference Deck for eden and citron.
_LAYOUTS: dict[str, ConfigLayout] = {
    "retroarch": ConfigLayout("retroarch", "retroarch.cfg", ConfigFormat.FLAT),
    "pcsx2": ConfigLayout("PCSX2", "inis/PCSX2.ini", ConfigFormat.INI),
    # Settings live in the data root here, not the config root: this Deck holds
    # ``~/.local/share/duckstation/settings.ini`` and no ``~/.config/duckstation``.
    "duckstation": ConfigLayout("duckstation", "settings.ini", ConfigFormat.INI, in_data_dir=True),
    "dolphin": ConfigLayout("dolphin-emu", "Dolphin.ini", ConfigFormat.INI),
    "primehack": ConfigLayout("primehack", "Dolphin.ini", ConfigFormat.INI),
    "ppsspp": ConfigLayout("ppsspp", "PSP/SYSTEM/ppsspp.ini", ConfigFormat.INI),
    "melonds": ConfigLayout("melonDS", "melonDS.toml", ConfigFormat.TOML),
    # Azahar keeps BOTH roots under ``azahar-emu`` — measured on the reference Deck:
    # ``config/azahar-emu/qt-config.ini`` beside ``data/azahar-emu/{nand,sdmc}``. The
    # ``azahar`` spelling found neither, so its settings read as unconfigured and a save
    # link would have pointed at a directory the emulator does not use.
    "azahar": ConfigLayout("azahar-emu", "qt-config.ini", ConfigFormat.INI),
    "lime3ds": ConfigLayout("lime3ds", "qt-config.ini", ConfigFormat.INI),
    "citra": ConfigLayout("citra-emu", "qt-config.ini", ConfigFormat.INI),
    "eden": ConfigLayout("eden", "qt-config.ini", ConfigFormat.INI),
    "citron": ConfigLayout("citron", "qt-config.ini", ConfigFormat.INI),
    "yuzu": ConfigLayout("yuzu", "qt-config.ini", ConfigFormat.INI),
    "sudachi": ConfigLayout("sudachi", "qt-config.ini", ConfigFormat.INI),
    "ryujinx": ConfigLayout("Ryujinx", "Config.json", ConfigFormat.JSON),
    "cemu": ConfigLayout("Cemu", "settings.xml", ConfigFormat.XML),
    "rpcs3": ConfigLayout("rpcs3", "config.yml", ConfigFormat.YAML),
    "vita3k": ConfigLayout("Vita3K", "config.yml", ConfigFormat.YAML, in_data_dir=True),
    "flycast": ConfigLayout("flycast", "emu.cfg", ConfigFormat.FLAT),
    "mgba": ConfigLayout("mGBA", "config.ini", ConfigFormat.INI),
    "rmg": ConfigLayout("RMG", "mupen64plus.cfg", ConfigFormat.FLAT, in_data_dir=True),
    "xemu": ConfigLayout("xemu", "xemu.toml", ConfigFormat.TOML, in_data_dir=True),
    "xenia": ConfigLayout("xenia", "xenia.config.toml", ConfigFormat.TOML, in_data_dir=True),
    "shadps4": ConfigLayout("shadPS4", "config.toml", ConfigFormat.TOML, in_data_dir=True),
}


def layout_for(emulator_id: str) -> ConfigLayout | None:
    """The settings layout for *emulator_id*, or ``None`` when unregistered.

    ``None`` is a real answer: a definition with no known settings file is one whose
    configured path cannot be read, so its save root must resolve from declared
    defaults only — never from a path guessed at the wrong file.
    """
    return _LAYOUTS.get(emulator_id)


def registered_ids() -> tuple[str, ...]:
    """Every definition id with a settings layout, in table order."""
    return tuple(_LAYOUTS)
