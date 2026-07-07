# Global conventions

These apply to every project, in any language. A project's own CLAUDE.md or an explicit instruction overrides them. The detailed, enforceable checklist lives in `guidelines/core.md` (plus a per-stack overlay); this file is the always-loaded behavior.

## Writing and output

- No emojis in output: docs, comments, commit messages, chat. A repository's showcase README may use them only if explicitly requested.
- No em-dash, en-dash, or middot as separators. Use plain punctuation: comma, colon, semicolon, parentheses.
- No filler. Say the thing, then stop. No preamble, no "in conclusion", no restating the question.
- Facts over adjectives. Prefer concrete numbers and observations to "powerful", "seamless", "robust".
- Language: user-facing product copy in the product's language; code, identifiers, comments, and commit messages in English.

## Suggestions and reviews

- Frame improvements as "observed problem, then concrete fix", grounded in what was actually checked. No speculative or over-engineered solutions.
- Do not restate the obvious or explain a domain to a domain expert.

## Code (any language)

- Validate external data at the boundary, map it once, then trust it. Throw early; do not stack defensive fallbacks between layers.
- Use a typed, discriminated error per domain. No bare generic error for a domain failure, no swallowed error.
- Do not reinvent what the standard library, the platform, or an already-installed dependency already does. Reach for a custom helper only when nothing existing fits.
- No narrative comments in the middle of code. Put an explanation above a function, type, or constant when the why is not obvious; keep an inline comment only for a genuine gotcha (platform quirk, library workaround, non-local invariant). Default to zero.
- Lint and type checks stay strict. Do not weaken them to make an error go away.

## Git

- Atomic commits, one logical change each. Clean history before push. No `--no-verify`.
- End commit messages with the AI co-author trailer when pair-working with an AI.
- Verify before delivering: no em-dash, middot, or emoji in delivered docs, and no broken internal links.
