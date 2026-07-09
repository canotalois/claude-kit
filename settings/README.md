# Autopilot settings

`autopilot.json` is a balanced permission posture: routine work runs without asking, the irreversible and outbound stays gated, and the human is only pulled in for genuine decisions.

## The three lists

- **allow**: auto-approved. Reads, edits inside source trees (`src`, `app(s)`, `packages`, `crates`, `tests`), read-only shell, the test/typecheck/lint/build commands for pnpm/npm/cargo, `git` up to and including `commit`, and docs domains for `WebFetch`.
- **ask**: always prompts, even though it is common: `git push`, dependency installs (`pnpm add`, `npm install`, `cargo add`), `npx` / `pnpm dlx` (runs arbitrary packages), `curl`, `git reset --hard`.
- **deny**: hard-blocked: `sudo`, and reads of secrets (`.env`, `*.key`, `*.pem`, ssh keys, `secrets/**`).

Edits outside the source trees (root config, CI, lockfiles) are not in `allow`, so they fall through to a prompt. That is deliberate: config changes deserve a look.

## Why `rm -rf` and force-push are not in `deny`

A blunt `deny Bash(rm -rf:*)` would also block `rm -rf node_modules`, which you want. Instead the `gate-destructive.py` PreToolUse hook (shipped with the plugin) blocks `rm -rf` only when it targets `/`, `~`, `$HOME`, an absolute system path, or a `..` traversal, and blocks force-push only to `main`/`master`. Everything else passes to the lists above. That is the point of hooks: decide where a permission glob is too coarse.

## Layering

Settings merge by scope: user (`~/.claude/settings.json`) < project (`.claude/settings.json`) < local (`.claude/settings.local.json`, gitignored) < CLI args. A `deny` in any scope wins; an `ask` prompts even if a lower scope allows. Put this posture in your user settings for everywhere, and tighten per project with a project `.claude/settings.json`.

## Install

`install.sh` merges `autopilot.json` into `~/.claude/settings.json` (with a timestamped backup) after asking. To do it by hand, copy the `permissions` block into your settings and adjust the globs to your stack.

## Unattended variant

`autopilot.json` assumes you are there to answer an `ask`. For a run with nobody at the keyboard (an overnight session), use `unattended.json` instead: it has **no `ask` list** (everything is `allow` or `deny`, and a `deny` never halts the run, Claude just works around it), denies `git push` and arbitrary network on top of the usual secrets/`sudo`, and sets `askUserQuestionTimeout` so any residual prompt auto-continues instead of hanging. See `autopilot/overnight.md` for how to launch one.

## Not for `--dangerously-skip-permissions`

Neither posture should be paired with `--dangerously-skip-permissions` or `defaultMode: bypassPermissions`; those turn every rule into a silent yes. Keep the bypass for isolated CI containers only.
