"""The per-format parsers, with inline fixtures in each emulator's own spelling.

The fixtures are trimmed copies of the shapes these files actually take: RetroArch's
quoted flat pairs, PCSX2's ``[Folders]`` section, melonDS's TOML tables, Ryujinx's
JSON object, Cemu's XML sections. Every case here is pure text in, dict out.
"""

from __future__ import annotations

from domain.emulator_config import (
    ConfigFormat,
    is_readable,
    layout_for,
    parse_config,
    parse_flat,
    parse_ini,
    parse_json,
    parse_toml,
    parse_xml,
    registered_ids,
)


class TestFlat:
    def test_quoted_values_are_unquoted(self) -> None:
        text = 'savefile_directory = "/run/media/deck/SR01T/Emulation/saves/retroarch/saves"\n'
        assert parse_flat(text)["savefile_directory"] == "/run/media/deck/SR01T/Emulation/saves/retroarch/saves"

    def test_comments_and_blanks_are_skipped(self) -> None:
        text = '# a comment\n\nsort_savefiles_enable = "true"\n'
        assert parse_flat(text) == {"sort_savefiles_enable": "true"}

    def test_a_line_without_equals_yields_nothing(self) -> None:
        assert parse_flat("garbage line\n") == {}

    def test_a_comment_after_a_value_is_dropped(self) -> None:
        assert parse_flat('savefile_directory = "/saves" # where\n')["savefile_directory"] == "/saves"

    def test_a_hash_inside_quotes_is_part_of_the_value(self) -> None:
        assert parse_flat('savefile_directory = "/saves#1"\n')["savefile_directory"] == "/saves#1"

    def test_the_last_write_wins(self) -> None:
        assert parse_flat('k = "a"\nk = "b"\n')["k"] == "b"

    def test_an_empty_value_is_kept_as_empty(self) -> None:
        assert parse_flat("savefile_directory = \n")["savefile_directory"] == ""


class TestIni:
    def test_section_keys_are_qualified_and_case_kept(self) -> None:
        text = "[Folders]\nMemoryCards = /run/media/deck/SR01T/Emulation/saves/pcsx2/saves\n"
        assert parse_ini(text)["Folders/MemoryCards"] == "/run/media/deck/SR01T/Emulation/saves/pcsx2/saves"

    def test_duckstation_memory_card_section(self) -> None:
        text = "[MemoryCards]\nCard1Type = PerGameTitle\nDirectory = /run/media/deck/SR01T/saves\n"
        values = parse_ini(text)
        assert values["MemoryCards/Directory"] == "/run/media/deck/SR01T/saves"
        assert values["MemoryCards/Card1Type"] == "PerGameTitle"

    def test_defaults_are_not_repeated_inside_sections(self) -> None:
        text = "[DEFAULT]\nshared = 1\n[Folders]\nMemoryCards = /saves\n"
        values = parse_ini(text)
        assert values["shared"] == "1"
        assert "Folders/shared" not in values

    def test_a_valueless_key_is_empty_not_missing(self) -> None:
        assert "Core/GCMPath" in parse_ini("[Core]\nGCMPath =\n")

    def test_malformed_ini_is_empty(self) -> None:
        assert parse_ini("[[[not ini\n") == {}


class TestToml:
    def test_nested_tables_collapse(self) -> None:
        text = '[Save]\nPath = "/home/deck/saves"\n[General]\nEnabled = true\n'
        values = parse_toml(text)
        assert values["Save/Path"] == "/home/deck/saves"
        assert values["General/Enabled"] == "true"

    def test_lists_are_skipped(self) -> None:
        values = parse_toml('Paths = ["/a", "/b"]\n[Save]\nPath = "/s"\n')
        assert "Paths" not in values
        assert values["Save/Path"] == "/s"

    def test_malformed_toml_is_empty(self) -> None:
        assert parse_toml("this is not toml = = =\n") == {}


class TestJson:
    def test_nested_objects_collapse(self) -> None:
        values = parse_json('{"Saves": {"SaveRoot": "/home/deck/saves"}, "Port": 1}')
        assert values["Saves/SaveRoot"] == "/home/deck/saves"
        assert values["Port"] == "1"

    def test_a_non_object_is_empty(self) -> None:
        assert parse_json("[1, 2]") == {}

    def test_malformed_json_is_empty(self) -> None:
        assert parse_json("{nope") == {}


class TestXml:
    def test_element_paths_carry_the_value(self) -> None:
        text = "<settings><Save><SaveDirectory>/home/deck/saves</SaveDirectory></Save></settings>"
        assert parse_xml(text)["settings/Save/SaveDirectory"] == "/home/deck/saves"

    def test_a_parent_element_contributes_no_value(self) -> None:
        values = parse_xml("<r><a><b>1</b></a></r>")
        assert "r/a" not in values
        assert values["r/a/b"] == "1"

    def test_malformed_xml_is_empty(self) -> None:
        assert parse_xml("<r><a></r>") == {}


class TestFormatTable:
    def test_yaml_is_declared_unreadable(self) -> None:
        assert parse_config(ConfigFormat.YAML, "a: b\n") == {}
        assert is_readable(ConfigFormat.YAML) is False

    def test_every_other_format_is_readable(self) -> None:
        for fmt in (ConfigFormat.FLAT, ConfigFormat.INI, ConfigFormat.TOML, ConfigFormat.JSON, ConfigFormat.XML):
            assert is_readable(fmt) is True

    def test_every_registry_definition_has_a_layout(self) -> None:
        """A definition with no settings file cannot read its own configured path."""
        from domain.emulator_registry import all_definitions

        missing = sorted({d.id for d in all_definitions()} - set(registered_ids()))
        assert missing == []

    def test_layouts_name_a_file(self) -> None:
        for emulator_id in registered_ids():
            layout = layout_for(emulator_id)
            assert layout is not None
            assert layout.filename
            assert layout.app_dir

    def test_an_unknown_id_has_no_layout(self) -> None:
        assert layout_for("no-such-emulator") is None
