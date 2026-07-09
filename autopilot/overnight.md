# Overnight run (local)

Let Claude work while you sleep on your own machine, without it stalling on a prompt you cannot answer. Two ingredients make the "do not block me" behavior real:

- `askUserQuestionTimeout` (set to `"2m"` in `settings/unattended.json`): an unanswered dialog auto-continues instead of hanging forever.
- The unattended posture has **no `ask` list**. Everything is `allow` (proceed) or `deny` (hard block). A `deny` does not halt the run: Claude is told it cannot, logs it, and moves on.

## Setup

1. Use the unattended posture instead of the balanced one: merge `settings/unattended.json` (it denies `git push`, secrets, `sudo`, arbitrary network; allows the dev loop and installs).
2. Turn on auto mode so there are no per-tool prompts.
3. Work on a **dedicated branch** (`git switch -c claude/overnight`), never on `main`. You review the diff in the morning; nothing is pushed.

## Launch

Give it a verifiable target with `/goal` (it keeps working until the condition holds, checked by a separate model each turn), and tell it to set aside anything it cannot do:

```
/goal every task in TODO.md is implemented with passing tests, and `pnpm -r typecheck && pnpm -r test` is green

Work through TODO.md top to bottom on this branch. Commit after each task with a
clear message. If you hit something you cannot do (a denied action, a design
call that needs me, a failing external dependency), append one line to
NEEDS-REVIEW.md with the task and the reason, then move on to the next task.
Never wait for me, never push.
```

In the morning you read `NEEDS-REVIEW.md`, skim `git log` on the branch, and merge or discard.

## When to prefer a cloud routine instead

A local overnight run needs your machine awake and the session alive, and an 8-hour unattended run can drift or burn tokens. If you want it to run with the laptop closed and hand you a pull request, use a scheduled **routine** (see `routines.md`): it runs on Anthropic's cloud, expects no human, and opens a PR you review with coffee.
