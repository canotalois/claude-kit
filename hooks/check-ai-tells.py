#!/usr/bin/env python3
"""PostToolUse hook: exit 2 (which surfaces a report to the model) if a
just-written file contains an AI-tell, an em-dash family character, middot,
bullet, or a pictographic emoji. The forbidden characters are built with chr()
so this source stays pure ASCII and never trips its own check.
"""
import json
import os
import sys

EXTS = {
    ".md", ".mdx", ".markdown", ".txt", ".ts", ".tsx", ".js", ".jsx",
    ".css", ".scss", ".json", ".yml", ".yaml", ".html", ".vue",
}

# Basenames exempt from the emoji rule (e.g. a showcase README).
ALLOW_EMOJI = set()

HARD = {
    chr(0x2014): "em-dash",
    chr(0x2013): "en-dash",
    chr(0x2012): "figure-dash",
    chr(0x2015): "horizontal-bar",
    chr(0x00B7): "middot",
    chr(0x2022): "bullet",
}


def is_emoji(ch):
    """Pictographic emojis and flags only, scoped to spare arrows, check marks,
    and the circled-i tooltip glyph."""
    o = ord(ch)
    return (0x1F000 <= o <= 0x1FAFF) or (0x1F1E6 <= o <= 0x1F1FF) or o == 0xFE0F


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    path = (payload.get("tool_input") or {}).get("file_path")
    if not path or not os.path.isfile(path):
        return 0
    if os.path.splitext(path)[1].lower() not in EXTS:
        return 0

    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return 0

    problems = []
    allow_emoji = os.path.basename(path) in ALLOW_EMOJI
    for line_no, line in enumerate(text.splitlines(), 1):
        for ch, name in HARD.items():
            if ch in line:
                problems.append("  {}:{}: {}".format(path, line_no, name))
        if not allow_emoji and any(is_emoji(c) for c in line):
            problems.append("  {}:{}: emoji".format(path, line_no))

    if not problems:
        return 0

    print(
        "AI-tells found. Remove them: plain punctuation only, no emojis.",
        file=sys.stderr,
    )
    seen = set()
    for p in problems:
        if p not in seen:
            print(p, file=sys.stderr)
            seen.add(p)
    return 2


if __name__ == "__main__":
    sys.exit(main())
