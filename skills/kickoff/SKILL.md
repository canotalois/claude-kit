---
name: kickoff
description: Start a new project on a claude-kit stack. Scaffolds the stack files and composes a self-contained GUIDELINES.md (universal core plus the language overlay). Invoke as "/kickoff <stack>", e.g. "/kickoff rust" or "/kickoff node-web".
argument-hint: "<stack> [target-dir]"
---

# kickoff

Bootstrap a new project from a claude-kit stack: pull the stack's starter files and write a `GUIDELINES.md` that is the universal core plus the stack overlay, so the project is self-contained and `/review` works immediately.

## Steps

1. Read the stack name from the argument (`node-web`, `rust`, ...). If missing or unknown, list the available stacks under `stacks/` and stop. Target directory is the second argument, default the current directory.
2. Confirm with the user in one line what will be created (stack, target dir) before writing anything into a non-empty directory.
3. Fetch the stack starter into the target dir:
   `npx degit canotalois/claude-kit/stacks/<stack> <target-dir>`
   (or copy from a local claude-kit checkout if one is present).
4. Fetch the universal spine to a temp path:
   `npx degit canotalois/claude-kit/guidelines <tmp>`
5. Compose `<target-dir>/GUIDELINES.md`: the full body of `core.md`, then the stack's `GUIDELINES.md` with its "Overlay on..." intro line dropped. Delete the now-merged stack `GUIDELINES.md` duplicate if degit placed one, so there is exactly one `GUIDELINES.md` at the root.
6. Verify the global conventions are active: if `~/.claude/CLAUDE.md` is not the claude-kit one, tell the user to run the installer. Do not silently add project-level copies of global rules.
7. Print the remaining language-specific scaffolding the user still owns (workspace manifest, per-package configs), from the stack README.

## Rules

- One `GUIDELINES.md` at the project root, self-contained (core plus overlay). No dangling reference to a file that is not in the new repo.
- Do not overwrite existing files without confirming.
- Keep the stack's `tsconfig` / `Cargo.toml` / CI / gitignore as-is; they are the starting point, not something to regenerate.
