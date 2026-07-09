# claude-kit

> Beta. I use it daily and it works, but the structure may still shift and there are rough edges. Feedback and issues welcome.

My Claude Code setup: a language-agnostic trunk (conventions, a hook, skills) plus per-language stacks you start from for anything. Install once, get the same standards everywhere, add a stack when you pick up a new language.

## The shape

```
claude-kit/
  CLAUDE.md            # universal behavior, loaded in every project (any language)
  guidelines/core.md   # the universal "don't" list /review enforces
  hooks/               # PostToolUse AI-tell blocker + PreToolUse destructive-command guard
  skills/              # /review, /ship, /doc-check, /kickoff
  agents/              # reusable subagents: reviewer, ux-auditor, researcher
  settings/            # a balanced permission posture (autopilot.json) + the safety model
  autopilot/           # a /loop maintenance task and scheduled-routine recipes
  stacks/
    node-web/          # TypeScript overlay + strict tsconfig, CI, gitignore
    rust/              # Rust overlay + workspace lints, CI, gitignore
```

Two layers, on purpose:

- **Trunk (universal).** `CLAUDE.md`, `guidelines/core.md`, the hook and the skills apply to any language. "No AI-tells, validate at the boundary, throw early, don't reinvent, typed errors, no mid-code comments, atomic commits" hold in Rust as much as in TypeScript.
- **Stacks (per language).** Each `stacks/<name>/` is a thin overlay: a `GUIDELINES.md` that adds the language's idioms on top of the core, plus its starter config (tsconfig / Cargo, CI, gitignore). Adding a language is one new folder, nothing else moves.

A guideline is written once in the spine and only its *expression* changes per stack:

| Core principle | node-web | rust |
|---|---|---|
| Validate at the boundary | zod, then narrow | `serde` into typed structs |
| Throw early, no stacked fallbacks | no `?? ??` masking | `?`, no `unwrap_or` papering over |
| One typed error per domain | discriminated union `code` | `enum` + `thiserror` |
| Strict by default | `strict`, `noUncheckedIndexedAccess` | `clippy::pedantic`, `-D warnings` |

## Three pieces, three roles

If you are new to Claude Code, this is the whole vocabulary:

| | What it is | When it fires | Here |
|---|---|---|---|
| **Hook** | a script Claude Code runs automatically on an event | every time, deterministic | block `rm -rf /`, strip AI-tells on write |
| **Skill** | a procedure you invoke with `/name` | when called | `/review`, `/ship`, `/kickoff` |
| **Agent** | a specialized sub-Claude with its own context | when delegated a task | `reviewer`, `ux-auditor` |

A hook is a reflex, a skill is a command, an agent is a colleague.

## Install

Two parts, because Claude Code splits them: the **plugin** carries the tools (skills, agents, hooks); the **installer** carries the conventions and the permission posture (those live in settings, a plugin cannot ship them). Run both for the full kit.

Plugin, any OS, inside Claude Code (also the Windows and non-developer path):

```
/plugin marketplace add github:canotalois/claude-kit
/plugin install claude-kit@claude-kit
```

Conventions and permissions, macOS / Linux (clones the kit, symlinks `CLAUDE.md`, merges the hooks and balanced permissions into `~/.claude` with a backup). Read it first with `| less`:

```bash
curl -fsSL https://raw.githubusercontent.com/canotalois/claude-kit/main/bootstrap.sh | bash
```

## Start a new project

`/kickoff` is a plugin skill, so install the plugin first (above).

```bash
/kickoff node-web my-app   # scaffolds the stack and a self-contained GUIDELINES.md
```

No plugin? Pull a stack directly and compose its `GUIDELINES.md` yourself:

```bash
npx degit canotalois/claude-kit/stacks/node-web my-app
```

## Autopilot

The point is to delegate the routine and be asked only about genuine decisions. The lever is permissions, not skills. `settings/autopilot.json` is a balanced posture: reads, edits in source trees, and the test/typecheck/lint/build/commit commands auto-run; `git push`, dependency installs, and `curl` prompt; secrets and `sudo` are denied. `rm -rf` and force-push are not blunt-denied; the `PreToolUse` guard (`hooks/gate-destructive.py`) blocks only the catastrophic cases (`rm -rf /`, `~`, `$HOME`, absolute paths, force-push to main) so `rm -rf node_modules` still works.

- **Delegate task classes** to the subagents in `agents/` (reviewer against the guidelines, ux-auditor, researcher) to keep the main context clean.
- **Recurring work**: `autopilot/loop.md` for a local `/loop` maintenance pass, `autopilot/routines.md` for scheduled cloud routines (daily PR triage, dependency bumps) that open a PR instead of pushing.
- The safety model is written up in `settings/README.md`. Not for use with `--dangerously-skip-permissions`.

## Why

Repetitive manual checks (no em-dash, no filler, no broken links, no forgotten files) are slow and easy to miss. This moves them into hooks and a few skills that run every time, keeps one set of standards across every language, and auto-approves the routine so a human is pulled in only for the irreversible and the outbound.
