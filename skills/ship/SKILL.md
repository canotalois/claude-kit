---
name: ship
description: Typecheck, scan changed files for AI-tells, commit with the co-author trailer, and push, in one command. Invoke with an optional commit message, e.g. "/ship fix the chart legend".
argument-hint: "<commit message>"
---

# ship

Run the quality gate, then commit and push. Stop and report on the first failure. Do not push broken code or code with AI-tells.

## Steps

1. If nothing is staged or changed, say so and stop.
2. Detect the toolchain from the repo and run its gate, stop on failure and print the output:
   - `pnpm-lock.yaml` / `package.json`: `pnpm -r typecheck` (or `typecheck` / `tsc --noEmit`), then `pnpm -r test` if a test script exists.
   - `Cargo.toml`: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`.
   - `pyproject.toml` / `uv.lock`: the project's typecheck (`mypy` / `pyright`) and `pytest`.
   - Fall back to whatever the project's CI runs.
3. Scan changed files (`git diff --name-only HEAD` plus untracked) for AI-tells: em-dash, en-dash, middot, emojis. If any, list them and stop so they get fixed.
4. Stage everything (`git add -A`), commit with the user's message (or a concise message inferred from the diff), and append the AI co-author trailer.
5. Push the current branch. Report the short SHA and the branch.

## Rules

- Never use `--no-verify` or `--no-gpg-sign`.
- One logical change per commit. If the diff mixes unrelated changes, warn before committing.
- No emojis or AI-tells in the commit message.
