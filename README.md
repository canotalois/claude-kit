# claude-kit

How I work with Claude Code, packaged so it installs in one command: conventions loaded in every project, a code rule catalog with IDs and exceptions, review and shipping skills, two safety hooks, and strict project starters.

## How I work

I orchestrate; Claude executes. An agent applies whatever it is given literally, so a vague or outdated instruction becomes a bug written in good faith. Everything here follows from that.

- **Instructions are short, concrete, and checkable.** [`CLAUDE.md`](CLAUDE.md) holds only what applies to every project, under 50 lines: output style, a working loop (read before editing, done means verified, report failures as they are, ask only for real decisions), and code principles.
- **Code rules carry their failure and their exception.** The [catalog](rules/README.md) has 74 rules, each with an ID, a default severity, who enforces it, the failure it prevents, and when it does not apply. A rule without an exception produces false positives until people stop reading the reviewer.
- **Tools enforce what tools can see.** Each stack ships the ESLint, TypeScript, or Clippy config that owns the mechanical rules; review covers only what no tool catches. Two hooks catch the rest: a guard against catastrophic deletes and force-pushes to `main`, and a check for AI-tells in written files.
- **Review is a separate pass with its own catalog.** `rules-review` judges a diff against the rules, reads them from the base branch so a change cannot rewrite its own rules, and separates "does it follow the rules" from "does it do what the ticket asked". The built-in `/code-review` hunts bugs alongside it, not instead of it.
- **Unattended work is bounded.** Hard turn and spend caps, a denied `git push`, a branch to review in the morning ([docs/unattended.md](docs/unattended.md)).
- **Claims about tools are checked, not remembered.** Rules and configs that cite tool behavior were verified against current documentation and by running the tools; the kit's CI re-runs the stacks' configs on sample code.

## Layout

```
CLAUDE.md               conventions loaded in every project
rules/                  the code rule catalog: core, typescript, react, next, backend, rust
skills/
  rules-review/         diff review against the catalog, with paste-ready suggestions
  ux-review/            whole-repository UX sweep into a backlog
  ship/                 gate, atomic commits, push
  doc-check/            AI-tells and broken links in docs
  kickoff/              start a project from a stack
hooks/                  destructive-command guard, AI-tell check, and their tests
settings/               the permission posture
stacks/                 node-web, node-service, rust: strict configs and CI
docs/unattended.md      bounded batch and nightly runs, and what they cost
```

## Install

macOS or Linux, with `git` and `python3`. Read it first: `curl -fsSL https://raw.githubusercontent.com/canotalois/claude-kit/main/install.sh | less`.

```bash
curl -fsSL https://raw.githubusercontent.com/canotalois/claude-kit/main/install.sh | bash
```

It clones the kit to `~/.claude-kit`, links `CLAUDE.md` and the skills into `~/.claude`, then asks before merging the hooks and the permission posture into `~/.claude/settings.json`. Anything it replaces is moved to `~/.claude-kit-backups/<timestamp>/`. Re-run it to update. From a checkout, run `./install.sh`.

Plugin only (skills and hooks; a plugin cannot ship global instructions or permissions):

```
/plugin marketplace add canotalois/claude-kit
/plugin install claude-kit@claude-kit
```

Use the installer or the plugin, not both: the skills and hooks would load twice.

## Start a project

```
/kickoff node-web my-app
```

It copies the stack's starter files and writes a short project `CLAUDE.md` with the build and test commands. `--vendor-rules` also writes the stack's rules into `GUIDELINES.md`, for a team repository whose reviewers do not have the kit. Without the kit: `npx degit canotalois/claude-kit/stacks/node-web my-app`.

| Stack | For | Rules |
| --- | --- | --- |
| [node-web](stacks/node-web/README.md) | Next.js monorepo with shared packages | core, typescript, react, next |
| [node-service](stacks/node-service/README.md) | TypeScript API, worker, or job on Node 24 | core, typescript, backend |
| [rust](stacks/rust/README.md) | Cargo workspace on edition 2024 | core, rust |

## Maintaining it

- CI runs the hook tests, shellcheck on the installer, the AI-tell check and an offline link check on the docs, and each stack's typecheck, lint, and tests on sample code.
- `/doctor prompt-audit` checks the instruction files for contradictions and stale references.
- Versions verified on 2026-10-25: TypeScript 6.0, ESLint 9.39, typescript-eslint 8.72, Next.js 16.4, Node 24, Rust edition 2024. The stack READMEs say why TypeScript 7 and ESLint 10 are not used yet.

## License

[MIT](LICENSE)
