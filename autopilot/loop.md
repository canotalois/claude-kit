# Maintenance loop

Copy this to a project's `.claude/loop.md`. Then `/loop 10m` runs it every ten minutes in the open session (omit the interval to let the model self-pace). It stays local and stops when the session closes.

Each pass, do only what is needed and report one tight status line:

1. Detect the toolchain and run the fast checks: typecheck and the quick test suite (`pnpm -r typecheck` and `pnpm -r test`, or `cargo check` and `cargo test`). Skip the slow end-to-end suite.
2. If something fails, fix the smallest cause, re-run that check, and note what you changed. Do not start unrelated work.
3. If everything is green and there is nothing to do, say so in one line and wait for the next pass. Do not invent work.
4. Never push, deploy, or run a destructive command from the loop. Surface anything that needs a human decision instead of acting on it.
