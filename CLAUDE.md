# Global conventions

<!-- Installed as ~/.claude/CLAUDE.md, so it loads in every project. Keep it
under 200 lines, concrete, and free of contradictions: anything procedural
belongs in a skill, anything code-level in rules/. A project's own CLAUDE.md,
or an explicit instruction, overrides this file. -->

## Writing and output

- No emoji in output: docs, comments, commit messages, chat. A showcase README may use them only when explicitly requested.
- No em-dash, en-dash, or middot as separators. Use a comma, colon, semicolon, or parentheses.
- No filler. Say the thing, then stop: no preamble, no "in conclusion", no restating the question.
- Facts over adjectives. A number or an observation instead of "powerful", "seamless", "robust".
- Structure every reply with headings, bullet lists, or tables, even an analysis or a status report. Group by theme and put the conclusion where it is found without reading everything.
- Language: user-facing product copy in the product's language; code, identifiers, comments, and commit messages in English.

## Working loop

- Read the code you are about to change, and its direct callers, before editing it.
- Done means verified with the project's own commands (typecheck, tests, lint). Say which ran; say what was not verified and why.
- Report failures as they are, with the output. Never weaken a test, a lint rule, or a type to get green.
- Stay in scope. A problem noticed outside the task is reported, not fixed in passing.
- Ask only for a genuine decision: product intent, an irreversible action, or anything that leaves the machine (push, deploy, publish, message). Otherwise pick the conventional option and say so.

## Suggestions and reviews

- Frame an improvement as "observed problem, then concrete fix", grounded in what was actually checked. No speculative or over-engineered fix.
- Do not restate the obvious or explain a domain to a domain expert.

## Code (any language)

- Validate external data at the boundary, map it once into your own types, then trust it. Throw early; do not stack defensive fallbacks between layers.
- A failure the caller must branch on gets a typed error with a discriminated code. A programmer error (missing config, misuse, broken invariant) is a plain error with a precise message. Never swallow an error.
- Do not reinvent what the standard library, the platform, or an installed dependency already does. Write a helper only when nothing existing fits.
- No narrative comments inside a function. Explain the why above a function, type, or constant when it is not obvious; keep an inline comment only for a genuine gotcha (platform quirk, library workaround, non-local invariant). Default to zero.
- Lint and type checks stay strict. Do not weaken them to make an error go away.
- The rule catalog with IDs, severities and exceptions lives in the kit's `rules/`; the `rules-review` skill applies it.

## Git

- Atomic commits, one logical change each. Clean history before push. Never `--no-verify`.
- End commit messages with the AI co-author trailer when pair-working with an AI.
- Before delivering docs: no em-dash, middot, or emoji, and no broken internal links.
