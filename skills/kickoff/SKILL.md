---
name: kickoff
description: Start a new project from a claude-kit stack. Copies the stack's starter files (strict compiler config, CI, gitignore), writes a short project CLAUDE.md with the build and test commands, and optionally vendors the stack's rule catalog into GUIDELINES.md for a team repository. Invoke as "/kickoff <stack> [target-dir] [--vendor-rules]", for example "/kickoff rust" or "/kickoff node-web my-app".
argument-hint: "<stack> [target-dir] [--vendor-rules]"
---

# kickoff

## Locate the kit

This skill's directory is a symlink into a claude-kit checkout, or sits inside the installed plugin. The kit root is two levels above its real path (`realpath` of this directory, then `../..`). Stacks are in `<kit>/stacks/`, rules in `<kit>/rules/`. Without a local checkout, fetch a stack with `npx degit canotalois/claude-kit/stacks/<stack> <target-dir>`.

## Steps

1. Read the stack name. Missing or unknown: list `<kit>/stacks/*` with the first line of each README and stop. The target directory defaults to the current one.
2. If the target is not empty, list what would be overwritten and ask before writing anything.
3. Copy every file of the stack except its `README.md`, keeping relative paths (`.github/`, dotfiles included).
4. Write `<target>/CLAUDE.md`, under 40 lines, from the stack README's "Commands" and "Layout" sections: how to install, typecheck, lint, test, and build, and where code lives. Only facts about this project; the global conventions already load from `~/.claude/CLAUDE.md`.
5. With `--vendor-rules`: write `<target>/GUIDELINES.md` as the concatenation of the rule files the stack README lists under "Rules", in that order, each under its own top-level heading. This is for a team repository whose CI or reviewers do not have the kit. A repository's `GUIDELINES.md` replaces the kit's catalog for `rules-review` (only its security and `critical` floor survives), so without the flag write none.
6. Print what the user still owns, from the stack README's "Then" section (workspace manifest, first package or crate).

## Rules

- Never overwrite without confirmation.
- Copy the starter configs as they are. They are the strict baseline, not something to regenerate or loosen.
