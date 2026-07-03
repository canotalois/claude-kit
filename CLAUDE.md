# Global conventions

These apply to every project. A project's own CLAUDE.md or an explicit instruction overrides them.

## Writing and output

- No emojis in output: docs, comments, commit messages, chat. A repository's showcase README may use them only if explicitly requested.
- No em-dash, en-dash, or middot as separators. Use plain punctuation: comma, colon, semicolon, parentheses.
- No filler. Say the thing, then stop. No preamble, no "in conclusion", no restating the question.
- Facts over adjectives. Prefer concrete numbers and observations to "powerful", "seamless", "robust".
- Language: user-facing product copy in the product's language; code, identifiers, comments, and commit messages in English.

## Suggestions and reviews

- Frame improvements as "observed problem, then concrete fix", grounded in what was actually checked. No speculative or over-engineered solutions.
- Do not restate the obvious or explain a domain to a domain expert.

## Code

- TypeScript strict, `noUncheckedIndexedAccess` on. No `as any`, no non-null `!` without a guard.
- Validate external data at the boundary (zod or a guard), map once, then trust it. Throw early; do not stack defensive fallbacks between layers.
- One error class per domain with a discriminated `code`. No bare `throw new Error` for domain errors, no empty `catch`.
- Do not reinvent accessible primitives (dropdown, tooltip, dialog, popover, datepicker). Use a reliable headless lib and style it. Centralize each lib behind one local wrapper.
- Do not reinvent what the platform gives you (Intl, URL, structuredClone, crypto.randomUUID, Array methods) or an already-installed dependency. Reach for a custom helper only when nothing existing fits.
- No narrative comments in the middle of code. Put an explanation in a JSDoc block above a function, type, or constant when the why is not obvious; keep an inline comment only for a genuine gotcha (browser quirk, library workaround, non-local invariant). Default to zero comments.

## UX (when there is a UI)

- Zero layout shift. Validation errors float (anchored to the field), never a banner that pushes content. Skeletons match the final content size.
- Delayed loading: keep previous data visible, show a skeleton only past ~200 ms. A cached load swaps instantly.
- Never crash on bad input: parsers return NaN/null, an ErrorBoundary catches the rest.

## Git

- Atomic commits, one logical change each. Clean history before push. No `--no-verify`.
- End commit messages with the AI co-author trailer when pair-working with an AI.
- Verify before delivering: no em-dash, middot, or emoji in delivered docs, and no broken internal links.
