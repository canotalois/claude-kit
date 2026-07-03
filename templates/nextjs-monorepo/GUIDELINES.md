# Guidelines

Short checklist. Every "Don't" is a blocker: if you catch yourself doing it, stop and reconsider before committing.

When in doubt: throw early, type strictly, trust the layer below. No defensive code for cases the layer below promised not to produce. The `/review` skill checks the current branch against this file in strict mode.

## TypeScript

- Don't cast `unknown` data with `as`. Validate (custom guard, zod), then narrow.
- Don't type a response body as `Record<string, string>` or `any`. Define the contract.
- Don't cast `FormData.get()` / `URLSearchParams.get()` / `localStorage.getItem()` to `string`. They return `string | null`. Narrow.
- Don't use `!` (non-null assertion) outside `array[0]!` guaranteed by a length or regex. If you need `!`, write a guard.
- Don't encode one domain state in two or more booleans. Use a discriminated union with a `status` field.
- Don't disable `strict` or `noUncheckedIndexedAccess`. They stay on.

## Nullish and fallbacks

- Don't use `??` to mask an undecided contract (`data.x ?? data.X`). Pick one, throw on the other.
- Don't use `??` to invent a domain default that should be a real decision.
- Don't scatter `cb?.()` for an "optional" prop. Default it to a noop at construction and drop the `?.`.
- Do use `??` for a genuine optional config default (`apiBaseUrl ?? "/api"`), and document why.
- Do prefer `throw` over a silent fallback when the value is required to work.

## Errors

- Don't `throw new Error(message)` for a domain error. Use a typed error class with a discriminated `code`.
- Don't write `catch (err) {}` or `.catch(() => undefined)`. Log at least; classify if you can.
- Do keep one error class per domain, with a `code` the UI can switch on.
- Do parse error responses at the boundary, not at the call site.

## React

- Don't `router.push` or `setState` during render. Use an effect.
- Don't put `'use client'` on a server-renderable page root. Isolate client islands.
- Don't pass a fresh object to a Context provider every render. Memoize.
- Don't put derivable logic in `useState` plus `useEffect`. Derive during render.
- Do keep pure calculations outside components, memoized on their inputs.

## Network and contracts

- Don't accept several response shapes "just in case". The contract is the contract.
- Don't hardcode `/api/...` paths in components or hooks. Centralize in one data module.
- Do validate the response shape at the boundary with zod. Throw on mismatch.
- Do throw at module load for missing required env vars, no silent fallback to `''`.

## Packages (monorepo)

- Don't put `react` / `react-dom` in a library's `dependencies`. Peer only.
- Don't deep-import into another package's `src/`. Go through its `exports` map.
- Do keep shared packages framework-agnostic: no dependency on the host app or routing.
- Do keep a single version of each dependency across the monorepo.

## UI and design system

- Don't hardcode color, spacing, or radius in JSX. Use theme-backed utilities.
- Don't reinvent an accessible primitive (dropdown, tooltip, dialog, popover, datepicker). Use a reliable headless lib and style it. One wrapper file per primitive.
- Do extract repeated patterns into reusable primitives. Reuse, don't duplicate.

## UX and perceived performance

- No layout shift. Errors float, anchored to the field, never a banner that pushes content. Skeletons match the final size exactly.
- No skeleton flash on a fast or cached load: keep previous data, show the skeleton only past ~200 ms.
- No stale data under a new label. Past the threshold, show the skeleton, not the stale value.
- No input accepting out-of-domain characters (letters in a date or amount). Filter at the input.
- Never crash on malformed input: parsers return NaN/null, a root ErrorBoundary catches the rest.

## Comments

- Don't write narrative comments in the middle of a function (a `// do X then Y` line above a statement). Explicit naming and small functions carry the intent.
- Don't write a comment that paraphrases the line below it.
- Do put an explanation in a JSDoc block above a function, type, or constant, when the why is not obvious.
- Do keep an inline comment only for a genuine gotcha: a browser quirk, a library workaround, a non-local invariant. Default to zero.

## Tests

- Don't test only the happy path. Cover the subtle behavior and the edge cases.
- Don't test against your own mocks of an unspecified contract. Match the real contract.
- Do write one test per behavior, named in the `it()`.

## Commits and hygiene

- Don't ship 16k lines in two commits. Atomic commits, one logical change each.
- Don't use `--no-verify` or `--no-gpg-sign`.
- Do write a PR description with scope, test plan, and screenshots for UI.
- No emojis, em-dashes, or middots in code, docs, or commit messages.
