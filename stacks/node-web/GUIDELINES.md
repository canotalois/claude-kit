# Guidelines: Node / web (TypeScript)

Overlay on `guidelines/core.md`. The core spine (contracts, nullish, errors, comments, don't-reinvent, tests, commits) applies as-is; this file adds the TypeScript, React, and frontend specifics. `/review` checks the branch against both.

## TypeScript

- Don't cast `unknown` data with `as`. Validate (custom guard, zod), then narrow.
- Don't type a response body as `Record<string, string>` or `any`. Define the contract.
- Don't cast `FormData.get()` / `URLSearchParams.get()` / `localStorage.getItem()` to `string`. They return `string | null`. Narrow.
- Don't use `!` (non-null assertion) outside `array[0]!` guaranteed by a length or regex. If you need `!`, write a guard.
- Don't encode one domain state in two or more booleans. Use a discriminated union with a `status` field.
- Don't disable `strict` or `noUncheckedIndexedAccess`. They stay on.

## Nullish and fallbacks (`??`, `||`, `?.`)

- Don't use `??` to mask an undecided contract (`data.x ?? data.X`). Pick one, throw on the other.
- Don't scatter `cb?.()` for an "optional" prop. Default it to a noop at construction and drop the `?.`.
- Do use `??` for a genuine optional config default (`apiBaseUrl ?? "/api"`), and document why.

## React

- Don't `router.push` or `setState` during render. Use an effect.
- Don't put `'use client'` on a server-renderable page root. Isolate client islands.
- Don't pass a fresh object to a Context provider every render. Memoize.
- Don't put derivable logic in `useState` plus `useEffect`. Derive during render.
- Do keep pure calculations outside components, memoized on their inputs.

## Network and contracts

- Don't hardcode `/api/...` paths in components or hooks. Centralize in one data module.
- Do validate the response shape at the boundary with zod. Throw on mismatch.
- Do throw at module load for a missing required env var, no silent fallback to `''`.

## Packages (monorepo)

- Don't put `react` / `react-dom` in a library's `dependencies`. Peer only.
- Don't deep-import into another package's `src/`. Go through its `exports` map.
- Do keep shared packages framework-agnostic and a single version of each dependency across the workspace.

## UI and design system

- Don't hardcode color, spacing, or radius in JSX. Use theme-backed utilities.
- Don't reinvent an accessible primitive (dropdown, tooltip, dialog, popover, datepicker). Use a reliable headless lib and style it. One wrapper file per primitive.

## UX and perceived performance

- No layout shift. Errors float, anchored to the field, never a banner that pushes content. Skeletons match the final size exactly.
- No skeleton flash on a fast or cached load: keep previous data, show the skeleton only past ~200 ms.
- No input accepting out-of-domain characters (letters in a date or amount). Filter at the input.
- Never crash on malformed input: parsers return NaN/null, a root ErrorBoundary catches the rest.
- Mobile is not optional. Tap targets >= 44px on touch, no horizontal overflow, inputs >= 16px to avoid iOS zoom, tap-reachable equivalents for anything hover-only.

## Test tooling

- Do use Vitest plus MSW for the network, memory adapters otherwise.

## Pull requests

- Do write a PR description with scope, test plan, and screenshots for UI.
