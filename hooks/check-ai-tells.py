#!/usr/bin/env python3
"""PostToolUse check for AI-tells in the file Claude just wrote with Write or
Edit (`tool_input.file_path`).

Exit 2 does not undo the write: it feeds the report back so the agent fixes
it. Flags em-dash family characters, middot, bullet, and pictographic emoji.
The forbidden characters are built with chr() so this source stays ASCII and
never trips its own check. A payload it cannot read passes silently: a
post-write linter must never break the agent loop.

Also a CLI for skills and CI: `check-ai-tells.py FILE...` exits 1 on a hit.
"""
import json
import os
import sys

EXTS = {
    ".md", ".mdx", ".markdown", ".txt", ".html", ".css", ".scss",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".json", ".yml", ".yaml", ".toml",
    ".py", ".rs", ".go", ".sh", ".sql", ".swift", ".kt",
}

FORBIDDEN = {
    chr(0x2014): "em-dash",
    chr(0x2013): "en-dash",
    chr(0x2012): "figure-dash",
    chr(0x2015): "horizontal-bar",
    chr(0x00B7): "middot",
    chr(0x2022): "bullet",
}

def is_emoji(ch):
    """Pictographs and flags only, so arrows, check marks and the circled-i
    glyph stay allowed."""
    o = ord(ch)
    return 0x1F000 <= o <= 0x1FAFF or o == 0xFE0F


def problems_in(path):
    if os.path.splitext(path)[1].lower() not in EXTS or not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    found = []
    for line_no, line in enumerate(lines, 1):
        names = [name for ch, name in FORBIDDEN.items() if ch in line]
        if any(is_emoji(c) for c in line):
            names.append("emoji")
        found.extend(f"  {path}:{line_no}: {name}" for name in names)
    return found


def report(problems):
    print("AI-tells found. Use plain punctuation and no emoji:", file=sys.stderr)
    print("\n".join(dict.fromkeys(problems)), file=sys.stderr)


def main(argv):
    if argv:
        problems = [p for path in argv for p in problems_in(path)]
        if problems:
            report(problems)
        return 1 if problems else 0
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    path = (payload.get("tool_input") or {}).get("file_path")
    problems = problems_in(path) if isinstance(path, str) else []
    if problems:
        report(problems)
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
