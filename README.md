# claude-kit

My Claude Code setup: conventions, a hook, and slash commands that make every project faster and more consistent. Install once, get the same standards everywhere, grow it over time.

## What is in here

- `CLAUDE.md`: global conventions loaded in every project (writing style, code rules, UX principles, git hygiene).
- `hooks/`: a `PostToolUse` hook that blocks AI-tells (em-dash, en-dash, middot) and emojis the moment a file is written or edited.
- `skills/`: slash commands.
  - `/review`: strict check of the current branch against the project's `GUIDELINES.md`.
  - `/ship`: typecheck, scan for AI-tells, commit with the co-author trailer, and push, in one command.
  - `/doc-check`: scan every markdown file for AI-tells and broken links, and list docs not covered.
- `templates/nextjs-monorepo/`: a starter (GUIDELINES, strict tsconfig, CI, gitignore, README) to clone into a new project.

## Install

Conventions, loaded in all projects:

```bash
ln -sf "$PWD/CLAUDE.md" ~/.claude/CLAUDE.md
```

Convenience installer (symlinks the convention file and prints the hook config to paste):

```bash
./install.sh
```

As a plugin (skills and hook, versioned, in the projects you choose):

```bash
/plugin marketplace add github:canotalois/claude-kit
/plugin install claude-kit@claude-kit
```

## New project from the template

```bash
npx degit canotalois/claude-kit/templates/nextjs-monorepo my-app
```

## Why

Repetitive manual checks (no em-dash, no filler, no broken links, no forgotten files) are slow and easy to miss. This moves them into a hook and a few skills, so they run every time, automatically.
