"""Core provisioning: the URL, the missing set, and what a real core archive must pass."""

from __future__ import annotations

import io
import zipfile

from domain.core_provision import (
    BUILDBOT_NIGHTLY,
    MINIMUM_CORE_BYTES,
    core_url,
    missing_cores,
    verify_core_archive,
)

ELF = b"\x7fELF" + b"\x02\x01\x01" + b"\x00" * (MINIMUM_CORE_BYTES + 64)


def _archive(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


class TestWhereCoresComeFrom:
    def test_a_core_name_becomes_the_build_bot_archive(self) -> None:
        assert core_url("snes9x_libretro") == f"{BUILDBOT_NIGHTLY}/snes9x_libretro.so.zip"


class TestWhichCoresAreMissing:
    def test_only_what_is_absent_is_downloaded(self) -> None:
        installed = {"mgba_libretro"}
        assert missing_cores(["snes9x_libretro", "mgba_libretro"], installed=installed.__contains__) == [
            "snes9x_libretro"
        ]

    def test_one_core_backing_two_platforms_is_fetched_once(self) -> None:
        assert missing_cores(["mgba_libretro", "mgba_libretro"], installed=lambda _core: False) == [
            "mgba_libretro"
        ]

    def test_an_empty_core_name_is_not_a_download(self) -> None:
        assert missing_cores(["", None], installed=lambda _core: False) == []  # type: ignore[list-item]


class TestWhatCountsAsAVerifiedCore:
    def test_a_matching_elf_core_is_accepted(self) -> None:
        verdict = verify_core_archive(_archive({"snes9x_libretro.so": ELF}), core_so="snes9x_libretro")
        assert verdict.ok
        assert verdict.member is not None and verdict.member.startswith(b"\x7fELF")
        assert verdict.size == len(ELF)

    def test_a_core_nested_in_a_directory_is_accepted(self) -> None:
        verdict = verify_core_archive(_archive({"linux/snes9x_libretro.so": ELF}), core_so="snes9x_libretro")
        assert verdict.ok

    def test_an_archive_holding_another_core_is_refused(self) -> None:
        verdict = verify_core_archive(_archive({"gambatte_libretro.so": ELF}), core_so="snes9x_libretro")
        assert (verdict.ok, verdict.reason) == (False, "no_core_member")

    def test_a_bundle_with_two_candidates_is_refused(self) -> None:
        # Two members ending in the asked-for name: which one is the core is unknowable.
        payload = _archive({"a/snes9x_libretro.so": ELF, "b/snes9x_libretro.so": ELF})
        assert verify_core_archive(payload, core_so="snes9x_libretro").reason == "no_core_member"

    def test_a_non_zip_response_is_refused(self) -> None:
        verdict = verify_core_archive(b"<html>not found</html>", core_so="snes9x_libretro")
        assert (verdict.ok, verdict.reason) == (False, "not_a_zip")

    def test_an_empty_download_is_refused(self) -> None:
        assert verify_core_archive(b"", core_so="snes9x_libretro").reason == "empty_download"

    def test_a_stub_member_is_refused(self) -> None:
        verdict = verify_core_archive(_archive({"snes9x_libretro.so": b"\x7fELF"}), core_so="snes9x_libretro")
        assert (verdict.ok, verdict.reason) == (False, "too_small")

    def test_something_that_is_not_an_elf_is_refused(self) -> None:
        payload = _archive({"snes9x_libretro.so": b"MZ" + b"\x00" * MINIMUM_CORE_BYTES})
        verdict = verify_core_archive(payload, core_so="snes9x_libretro")
        assert (verdict.ok, verdict.reason) == (False, "not_elf")

    def test_a_corrupt_member_is_refused(self) -> None:
        payload = bytearray(_archive({"snes9x_libretro.so": ELF}))
        # Damage the compressed body so the CRCs no longer agree.
        payload[40:60] = b"\x00" * 20
        assert verify_core_archive(bytes(payload), core_so="snes9x_libretro").ok is False
