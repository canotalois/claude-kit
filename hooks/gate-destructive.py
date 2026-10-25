#!/usr/bin/env python3
"""PreToolUse guard for Claude Code's Bash tool (`tool_input.command`).

Exit 2 blocks the command and feeds stderr back to the agent. It blocks two
accident classes and nothing else, so the permission allow-list can stay
generous:

- a recursive `rm` whose target resolves outside the project (the hook's cwd)
  and outside the system temp directories, or onto the project root, home, or
  an unresolvable variable or command substitution;
- a history-rewriting or deleting push to main/master (`--force`,
  `--force-with-lease`, `+refspec`, `--mirror`, `--delete`, `:branch`).

It is a seatbelt for common mistakes, not a sandbox: an agent that wants to
delete something can still find a way. Real isolation comes from the agent's
sandbox and permission rules.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

PROTECTED_BRANCHES = {"main", "master"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|&\n]")
WRAPPERS = {"sudo", "command", "nice", "nohup", "time", "env", "xargs"}


def read_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def tokenize(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def strip_wrappers(tokens):
    while tokens and (tokens[0] in WRAPPERS or re.fullmatch(r"\w+=\S*", tokens[0])):
        tokens = tokens[1:]
    return tokens


def safe_roots(cwd):
    roots = {os.path.realpath(cwd), os.path.realpath(tempfile.gettempdir())}
    roots.update(os.path.realpath(p) for p in ("/tmp", "/private/tmp", "/var/tmp"))
    return roots


def is_within(path, root):
    return path != root and path.startswith(root.rstrip(os.sep) + os.sep)


def dangerous_rm_target(target, cwd):
    if "$(" in target or "`" in target:
        return "a command substitution"
    expanded = os.path.expanduser(os.path.expandvars(target))
    if "$" in expanded:
        return "an unset variable"
    resolved = os.path.realpath(os.path.join(cwd, expanded.rstrip("*") or "."))
    home = os.path.realpath(os.path.expanduser("~"))
    if resolved in {os.path.realpath(cwd), home, os.sep}:
        return resolved
    if any(is_within(resolved, root) for root in safe_roots(cwd)):
        return None
    return resolved


def check_rm(tokens, cwd):
    if not tokens or os.path.basename(tokens[0]) != "rm":
        return None
    flags = [t for t in tokens[1:] if t.startswith("-") and t != "--"]
    recursive = any(
        f == "--recursive" or (not f.startswith("--") and re.search(r"[rR]", f))
        for f in flags
    )
    if not recursive:
        return None
    targets = [t for t in tokens[1:] if not t.startswith("-")]
    for target in targets:
        reason = dangerous_rm_target(target, cwd)
        if reason:
            return (
                f"Blocked: recursive delete of {reason}. Delete a path inside the "
                "project or a temp directory, or run it yourself."
            )
    return None


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "symbolic-ref", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def push_destinations(args, cwd):
    """Branches a `git push` writes to. With no refspec the current branch is
    pushed, which is git's default `push.default=simple` behaviour."""
    positional = [a for a in args if not a.startswith("-")]
    refspecs = positional[1:]
    if not refspecs:
        return [current_branch(cwd)], False
    destinations, has_plus = [], False
    for spec in refspecs:
        has_plus |= spec.startswith("+")
        spec = spec.lstrip("+")
        dest = spec.split(":", 1)[1] if ":" in spec else spec
        if dest == "HEAD":
            dest = current_branch(cwd)
        destinations.append(dest)
    return destinations, has_plus


def check_push(tokens, cwd):
    if len(tokens) < 2 or os.path.basename(tokens[0]) != "git":
        return None
    args = tokens[1:]
    while args and args[0] in {"-C", "-c"}:
        args = args[2:]
    if not args or args[0] != "push":
        return None
    args = args[1:]
    rewriting = any(
        a in {"--force", "--mirror", "--delete"}
        or a.startswith("--force-with-lease")
        or re.fullmatch(r"-[a-zA-Z]*[fd][a-zA-Z]*", a)
        for a in args
    )
    destinations, has_plus = push_destinations(args, cwd)
    deletes = any(a.startswith(":") for a in args if not a.startswith("-"))
    if not (rewriting or has_plus or deletes):
        return None
    hit = [d.removeprefix("refs/heads/") for d in destinations if d]
    if any(d in PROTECTED_BRANCHES for d in hit) or "--mirror" in args:
        return (
            "Blocked: force-push or delete on main/master. Push to a feature "
            "branch, or run it yourself if this is intentional."
        )
    return None


def main():
    payload = read_payload()
    if not payload or payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str):
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    for segment in SEGMENT_SPLIT.split(command):
        tokens = strip_wrappers(tokenize(segment.strip()))
        reason = check_rm(tokens, cwd) or check_push(tokens, cwd)
        if reason:
            print(reason, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
