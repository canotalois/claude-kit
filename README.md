# claude-kit

My Claude Code setup: a language-agnostic trunk (conventions, a hook, skills) plus per-language stacks you branch from to start anything. Install once, get the same standards everywhere, add a stack when you pick up a new language.

## The shape

```
claude-kit/
  CLAUDE.md            # universal behavior, loaded in every project (any language)
  guidelines/core.md   # the universal "don't" list /review enforces
  hooks/               # a PostToolUse hook that blocks emojis and AI-tells on write
  skills/              # /review, /ship, /doc-check, /kickoff
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

## Install

Universal conventions, in every project:

```bash
./install.sh   # symlinks CLAUDE.md into ~/.claude and prints the hook config
```

As a plugin (skills and hook, versioned):

```bash
/plugin marketplace add github:canotalois/claude-kit
/plugin install claude-kit@claude-kit
```

## Start a new project

```bash
/kickoff rust my-app       # scaffolds the stack and a self-contained GUIDELINES.md
/kickoff node-web my-app
```

Or pull a stack directly:

```bash
npx degit canotalois/claude-kit/stacks/node-web my-app
```

## Why

Repetitive manual checks (no em-dash, no filler, no broken links, no forgotten files) are slow and easy to miss. This moves them into a hook and a few skills that run every time, and keeps one set of standards across every language instead of re-deciding them per project.
