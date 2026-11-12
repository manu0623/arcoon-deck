"""Save-root resolution, pinned to config values read off a real Deck.

The configured paths in these tests are the literal strings found in that Deck's
own emulator configs — including the SD-card paths EmuDeck wrote, which is the case
where "the config says so" and "the data is somewhere else" both have to be true at
once.
"""

from __future__ import annotations

from domain.save_locations import (
    ResolvedSaveRoot,
    SaveRootRule,
    UnresolvedSaveRoot,
    all_rules,
    resolve,
    rule_for,
)

HOME = "/home/deck"
FLATPAK_RA = f"{HOME}/.var/app/org.libretro.RetroArch/config/retroarch"
PCSX2_CFG = f"{HOME}/.config/PCSX2"
DUCK_CFG = f"{HOME}/.local/share/duckstation"
SD = "/run/media/deck/SR01T/Emulation/saves"


def _none(_path: str) -> bool:
    return False


def _all(_path: str) -> bool:
    return True


def _only(*paths: str):
    wanted = set(paths)
    return lambda path: path in wanted


class TestConfiguredWins:
    def test_retroarch_savefile_directory_is_used_verbatim(self) -> None:
        """The Deck's flatpak writes an absolute SD-card path; it must survive intact."""
        answer = resolve(
            family="retroarch",
            platform="gba",
            values={"savefile_directory": f"{SD}/retroarch/saves"},
            home=HOME,
            data=FLATPAK_RA,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{SD}/retroarch/saves"
        assert answer.source == "config"

    def test_a_configured_path_that_does_not_exist_is_still_the_answer(self) -> None:
        """First launch: the emulator will create it. Absence is reported, not hidden."""
        answer = resolve(
            family="retroarch",
            platform="snes",
            values={"savefile_directory": f"{SD}/retroarch/saves"},
            home=HOME,
            data=FLATPAK_RA,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.exists is False

    def test_pcsx2_memory_cards_key(self) -> None:
        """``Folders/MemoryCards`` as PCSX2.ini spells it, and bare as a flattener may."""
        for values in ({"Folders/MemoryCards": f"{SD}/pcsx2/saves"}, {"MemoryCards": f"{SD}/pcsx2/saves"}):
            answer = resolve(
                family="pcsx2",
                platform="ps2",
                values=values,
                home=HOME,
                data=PCSX2_CFG,
                exists=_none,
            )
            assert isinstance(answer, ResolvedSaveRoot)
            assert answer.path == f"{SD}/pcsx2/saves"

    def test_duckstation_memory_card_directory(self) -> None:
        answer = resolve(
            family="duckstation",
            platform="psx",
            values={"MemoryCards/Directory": f"{SD}/duckstation/saves"},
            home=HOME,
            data=DUCK_CFG,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{SD}/duckstation/saves"

    def test_a_tilde_path_is_expanded(self) -> None:
        answer = resolve(
            family="retroarch",
            platform="gb",
            values={"savefile_directory": "~/saves"},
            home=HOME,
            data=FLATPAK_RA,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{HOME}/saves"

    def test_blank_values_are_not_paths(self) -> None:
        """PCSX2.ini writes ``BlockDumpSaveDirectory = `` — empty, not a directory."""
        answer = resolve(
            family="pcsx2",
            platform="ps2",
            values={"Folders/MemoryCards": "   "},
            home=HOME,
            data=PCSX2_CFG,
            exists=_only(f"{PCSX2_CFG}/memcards"),
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.source == "default"


class TestDefaults:
    def test_first_existing_default_wins(self) -> None:
        answer = resolve(
            family="duckstation",
            platform="psx",
            values={},
            home=HOME,
            data=DUCK_CFG,
            exists=_only(f"{DUCK_CFG}/saves"),
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{DUCK_CFG}/saves"
        assert answer.source == "default"
        assert answer.exists is True

    def test_no_default_present_still_answers_the_first_to_create(self) -> None:
        """A fresh install must be launchable: the session layer creates the directory."""
        answer = resolve(
            family="pcsx2",
            platform="ps2",
            values={},
            home=HOME,
            data=PCSX2_CFG,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{PCSX2_CFG}/memcards"
        assert answer.exists is False

    def test_dolphin_is_defaults_only(self) -> None:
        """This Deck's Dolphin.ini names no card path, so no key is encoded."""
        rule = rule_for("dolphin")
        assert rule is not None
        assert rule.keys == ()
        answer = resolve(
            family="dolphin",
            platform="gc",
            values={},
            home=HOME,
            data=f"{HOME}/.var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu",
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path.endswith("/GC/USA/Card A")


class TestRefusals:
    def test_an_unknown_family_is_a_refusal(self) -> None:
        answer = resolve(
            family="retroarch-plus",
            platform="ps2",
            values={},
            home=HOME,
            data="",
            exists=_all,
        )
        assert isinstance(answer, UnresolvedSaveRoot)
        assert answer.reason == "unknown-family"

    def test_a_platform_the_family_does_not_serve_is_a_refusal(self) -> None:
        answer = resolve(
            family="duckstation",
            platform="ps2",
            values={},
            home=HOME,
            data=DUCK_CFG,
            exists=_all,
        )
        assert isinstance(answer, UnresolvedSaveRoot)
        assert answer.reason == "platform-not-served"

    def test_ryujinx_uses_the_config_root_not_the_data_root(self) -> None:
        """Measured: bis/ and games/ live in ``~/.config/Ryujinx``, with no data dir."""
        answer = resolve(
            family="ryujinx",
            platform="switch",
            values={},
            home=HOME,
            data=f"{HOME}/.local/share/Ryujinx",
            config=f"{HOME}/.config/Ryujinx",
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{HOME}/.config/Ryujinx"

    def test_the_yuzu_lineage_uses_the_data_root(self) -> None:
        """Measured: eden keeps nand/ under ``~/.local/share/eden``."""
        answer = resolve(
            family="yuzu",
            platform="switch",
            values={},
            home=HOME,
            data=f"{HOME}/.local/share/eden",
            config=f"{HOME}/.config/eden",
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{HOME}/.local/share/eden"

    def test_the_retroarch_wildcard_serves_any_platform(self) -> None:
        answer = resolve(
            family="retroarch",
            platform="arcade",
            values={},
            home=HOME,
            data=FLATPAK_RA,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)


class TestRuleTable:
    def test_every_rule_declares_candidates(self) -> None:
        for rule in all_rules():
            assert rule.keys or rule.defaults, rule.family

    def test_every_rule_declares_a_platform(self) -> None:
        for rule in all_rules():
            assert rule.platforms, rule.family

    def test_families_are_unique(self) -> None:
        families = [rule.family for rule in all_rules()]
        assert len(families) == len(set(families))

    def test_every_registry_family_has_a_rule(self) -> None:
        """A family the scanner can find but the save layer cannot locate is unplayable."""
        from domain.emulator_registry import all_definitions

        missing = sorted({d.family for d in all_definitions()} - {rule.family for rule in all_rules()})
        assert missing == []

    def test_templates_use_only_known_tokens(self) -> None:
        for rule in all_rules():
            for template in rule.defaults:
                assert any(token in template for token in ("{home}", "{config}", "{data}")) or template.startswith(
                    "/"
                ), (rule.family, template)

    def test_config_and_data_roots_are_distinct(self) -> None:
        """PCSX2 keeps cards beside its settings; the token must say so."""
        answer = resolve(
            family="pcsx2",
            platform="ps2",
            values={},
            home=HOME,
            data=f"{HOME}/.local/share/PCSX2",
            config=PCSX2_CFG,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{PCSX2_CFG}/memcards"

    def test_config_defaults_to_data_for_a_single_root_caller(self) -> None:
        answer = resolve(
            family="retroarch",
            platform="gba",
            values={},
            home=HOME,
            data=FLATPAK_RA,
            exists=_none,
        )
        assert isinstance(answer, ResolvedSaveRoot)
        assert answer.path == f"{FLATPAK_RA}/saves"

    def test_rule_lookup(self) -> None:
        assert isinstance(rule_for("pcsx2"), SaveRootRule)
        assert rule_for("nope") is None
