# Unattended work

How to hand an agent a batch of work and review the result later, without paying for idle turns or waking up to a pushed `main`. Claude Code flags and limits as documented on 2026-10-25; re-check them when the docs move.

## Principles

- **A run has a hard ceiling.** Turns and dollars are capped on the command line, not hoped for in the prompt.
- **Nothing leaves the machine.** `git push` is denied, not merely absent from an allow list: auto mode approves pushes to any branch, the default branch included, unless a deny rule says otherwise.
- **The result is a branch to review.** Work happens in a worktree on a `claude/` branch; one task per commit; anything blocked is written down, not waited on.
- **No timers for work that has no trigger.** A `/loop 10m` fires a full-context turn every ten minutes whether or not there is anything to do. Prefer an event (CI finished, PR opened) or a nightly cloud task.

## Local batch, laptop open

Headless print mode is the documented unattended path. An interactive session left open stops when the process exits and has no spend cap.

```bash
claude -p "$(cat <<'EOF'
Work through TODO.md top to bottom on a new branch named claude/batch-<date>.
Commit after each task. If a task needs a decision or a denied action, append
one line to NEEDS-REVIEW.md with the task and the reason, then continue.
Stop when TODO.md is done or nothing actionable is left.
EOF
)" \
  --worktree batch \
  --permission-mode auto \
  --permission-prompts none \
  --max-turns 80 \
  --max-budget-usd 10 \
  --output-format json > batch.json
```

- `--permission-prompts none` denies anything that would prompt instead of hanging on it, and removes the question tool.
- Add `"Bash(git push *)"` to `permissions.deny` in the project's `.claude/settings.json` for the run. The kit's posture only asks for push, which is right when you are at the keyboard.
- `--max-budget-usd` is a client-side estimate; read `total_cost_usd` in the JSON afterwards.
- `/goal <condition>` is worth it only with a condition a reader can check from the transcript and a bound: "`pnpm test` exits 0 and `git status` is clean, or stop after 20 turns". Its evaluator is a small model; the main turns are the cost.
- Do not use `--bare`: it skips `CLAUDE.md`, and with it the conventions.

## Nightly, laptop closed

A cloud scheduled task (`/schedule`, or claude.ai/code/routines; formerly "routines") runs on Anthropic's infrastructure, starts in auto mode, and pushes only to `claude/`-prefixed branches. Runs count against the plan's usage; the minimum interval is one hour.

```
Take the top unchecked item in BACKLOG.md. Implement it on a claude/ branch
with tests, run the project's typecheck and tests, and open a draft PR that
links the item. If it is too ambiguous to build, open a draft PR containing
only a short "needs decision" note. One item per run. Never touch main.
```

One item per run keeps each PR reviewable and each run's cost bounded.

## PR review

Do not build a scheduled task that reviews every PR: that duplicates Claude Code's Code Review product and the `anthropics/claude-code-action` GitHub Action, which already handle triggers, inline comments, and spend limits. Pick one:

- Code Review, set to run once after PR creation (the default "after every push" multiplies cost).
- The GitHub Action with `--max-turns` in `claude_args`, prompted to run the `rules-review` skill so findings carry the catalog's rule IDs.

## Spend levers

| Lever | Use |
| --- | --- |
| `/clear` between unrelated tasks | free, and stops paying for stale context |
| `model: haiku` on a fan-out subagent | search and summarization do not need the main model |
| `--effort` | medium is the default on current models; `max` tends to overthink |
| `/usage` | per-skill, per-subagent, and per-loop attribution after the fact |

## Sandbox

`sandbox.enabled` adds OS-level isolation for shell commands on macOS, Linux, and WSL2, and blocks shell reads of `.env` files that a `Read` deny rule cannot see (`grep -r`, a script opening the file). It is not on in the kit's posture because on macOS `git` over SSH fails inside it even for an allowed host. Turn it on per project when the remote is HTTPS, or for a batch run that never pushes.
