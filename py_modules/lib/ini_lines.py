"""Set one key in an INI file without rewriting anything else.

An emulator's settings file holds its GPU backend, pad bindings, per-game overrides and
hotkeys the user may have rebound. A parser round-trip reformats all of that, so the write
here walks the text line by line, replaces the one key inside the one section, and leaves
every other line — order, comments, blank lines — exactly as it was.

An absent key is added at the end of its section and an absent section at the end of the
file, which is where the emulator's own defaults would put them. A same-named key in a
different section is never touched: the section is part of the address.
"""

from __future__ import annotations


def rewrite_value(text: str, *, section: str, key: str, value: str) -> str:
    """*text* with ``[section] key`` set to *value*."""
    out: list[str] = []
    in_section = False
    seen_section = False
    written = False

    def add_key() -> None:
        # End of the section, above the blank lines that close it.
        blanks: list[str] = []
        while out and not out[-1].strip():
            blanks.append(out.pop())
        out.append(f"{key} = {value}")
        out.extend(blanks)

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_section and not written:
                add_key()
                written = True
            in_section = stripped[1:-1].strip() == section
            seen_section = seen_section or in_section
            out.append(line)
            continue
        if in_section and not written and "=" in stripped and stripped.split("=", 1)[0].strip() == key:
            out.append(f"{key} = {value}")
            written = True
            continue
        out.append(line)
    if in_section and not written:
        add_key()
    if not seen_section:
        if out and out[-1].strip():
            out.append("")
        out.extend((f"[{section}]", f"{key} = {value}"))
    return "\n".join(out) + "\n"
