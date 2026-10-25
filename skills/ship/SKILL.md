---
name: ship
description: Run the project's quality gate, scan the changed files for AI-tells, commit the change atomically with the co-author trailer, and push the branch. Invoke as "/ship [commit message]" when a change is finished and the user wants it committed and pushed.
argument-hint: "[commit message]"
---

# ship

Gate, commit, push. Stop at the first failure and show its output. Never push code that fails the gate.

## Steps

1. Nothing changed (`git status --porcelain` empty): say so and stop. On the default branch: stop and ask for a branch name, unless the user said to push there.
2. Run the gate the project itself uses. Read it from CI first (`.github/workflows/*`, `.gitlab-ci.yml`), then from the manifests:
   - `package.json`: its `typecheck`, `lint`, and `test` scripts, through the package manager the lockfile names.
   - `Cargo.toml`: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`.
   - `pyproject.toml`: the configured type checker, then `pytest`.
3. Scan the changed and untracked text files: `python3 scripts/check-ai-tells.py <files>` from this skill's directory. A hit stops the run until fixed.
4. Group the changes. One logical change is one commit: when the diff mixes unrelated changes, propose the split and stage each group by path (`git add <paths>`), never `git add -A` over unrelated work.
5. Commit with the user's message, or one written from the diff: imperative subject under 72 characters, a body only when the why is not obvious, then the AI co-author trailer.
6. Push the current branch (`git push -u origin HEAD` the first time). Report the short SHA of each commit and the branch.

## Rules

- Never `--no-verify`, `--no-gpg-sign`, or a force push. A failing pre-commit hook is fixed, not bypassed.
- No emoji or AI-tells in commit messages.
- Do not fix gate failures silently inside the ship run: report them, then fix as a separate step the user sees.
