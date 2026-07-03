#!/usr/bin/env python3
"""PostToolUse hook: block AI-tells in files that were just written or edited.

Reads the tool payload as JSON on stdin, looks at the written file, and exits 2
with a report if it finds an em-dash, en-dash, figure-dash, horizontal bar,
middot, bullet, or a pictographic emoji. Exit 2 surfaces the report back to the
model so it fixes it.

Forbidden characters are built with chr() from their code points, so this source
file stays pure ASCII and never trips its own check.
"""
import json
import os
import sys

# Extensions worth checking.
EXTS = {
    ".md", ".mdx", ".markdown", ".txt", ".ts", ".tsx", ".js", ".jsx",
    ".css", ".scss", ".json", ".yml", ".yaml", ".html", ".vue",
}

# Basenames allowed to contain emojis (e.g. a showcase README). Empty by default.
ALLOW_EMOJI = set()

# Hard blockers: punctuation that reads as an AI-tell, by code point.
HARD = {
    chr(0x2014): "em-dash",
    chr(0x2013): "en-dash",
    chr(0x2012): "figure-dash",
    chr(0x2015): "horizontal-bar",
    chr(0x00B7): "middot",
    chr(0x2022): "bullet",
}


def is_emoji(ch):
    """Pictographic emojis and regional flags, plus the emoji variation selector.
    Scoped to avoid arrows, check marks, or the circled-i tooltip glyph."""
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
