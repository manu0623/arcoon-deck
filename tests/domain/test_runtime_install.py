"""The command that installs the runtime the plugin drives."""

from __future__ import annotations

from domain.runtime_install import FLATHUB_REMOTE, LIBRETRO_RUNTIME_APP_ID, install_command


class TestTheInstallCommand:
    def test_it_installs_retroarch_for_the_user(self) -> None:
        assert install_command() == ("flatpak", "install", "--user", "-y", FLATHUB_REMOTE, LIBRETRO_RUNTIME_APP_ID)

    def test_it_never_asks_a_question_game_mode_cannot_answer(self) -> None:
        # `-y` is what makes an unattended install possible; without it flatpak waits.
        assert "-y" in install_command()

    def test_it_installs_per_user_rather_than_system_wide(self) -> None:
        # A system install would need a password prompt nothing in Game Mode can show.
        assert "--user" in install_command()
        assert "--system" not in install_command()

    def test_another_app_can_be_named(self) -> None:
        assert install_command("org.example.Emulator")[-1] == "org.example.Emulator"
