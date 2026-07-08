#!/usr/bin/env python3
"""PreToolUse guard: exit 2 (block) only on catastrophic Bash, so the allow-list
can stay generous. It stops `rm -rf` aimed at /, ~, $HOME, an absolute or
parent-traversing path, and force-push to main/master. Everything else passes
through to the normal permission rules.
"""
import json
import re
import sys


def load_command():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    if data.get("tool_name") != "Bash":
        return None
    return (data.get("tool_input") or {}).get("command", "")


def is_catastrophic_rm(cmd):
    if not re.search(r"\brm\b", cmd):
        return False
    if not re.search(r"-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|--recursive|--force", cmd):
        return False
    dangerous = [
        r"\s/(\s|$|\*)",       # the root, bare or globbed
        r"\s~(/|\s|$)",        # home
        r"\$HOME|\$\{HOME\}",
        r"\s/(etc|usr|bin|var|opt|lib|system|library)\b",
        r"\.\.(/|\s|$)",       # parent-dir traversal
    ]
    return any(re.search(p, cmd, re.IGNORECASE) for p in dangerous)


def is_force_push_to_main(cmd):
    if not re.search(r"\bgit\s+push\b", cmd):
        return False
    if not re.search(r"--force(?!-with-lease)|\s-f\b|\s\+", cmd):
        return False
    return bool(re.search(r"\b(main|master)\b", cmd)) or "origin" in cmd and not re.search(
        r"\b(feat|feature|fix|chore|claude)/", cmd
    )


def main():
    cmd = load_command()
    if not cmd:
        return 0
    if is_catastrophic_rm(cmd):
        print(
            "Blocked: recursive delete of a system, home, or absolute path. "
            "Delete a project-relative path instead, or run it yourself.",
            file=sys.stderr,
        )
        return 2
    if is_force_push_to_main(cmd):
        print(
            "Blocked: force-push to main/master. Push to a feature branch, "
            "or run it yourself if this is intentional.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
