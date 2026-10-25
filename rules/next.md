# Next.js rules

On top of `react.md`, for the App Router (Next.js 16). Rules about Server Actions apply to any React Server Functions; the Next.js APIs named are the ones current in version 16.

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `lint-web-vitals` | minor | lint | Next.js core-web-vitals lint set |
| `next-action-authz` | critical | review | Server Action or Route Handler without its own auth check |
| `next-server-only` | major | review | server data or modules reaching the client |
| `next-use-client-scope` | minor | review | `'use client'` wider than the interactive part |
| `next-revalidate-after-mutation` | major | review | mutation of cached data with no revalidation |
| `next-public-env` | major | review | `NEXT_PUBLIC_` variable read dynamically |

---

### lint-web-vitals
scope: next, severity: minor, enforcement: lint

Owner: `eslint-config-next` `core-web-vitals`, run through the ESLint CLI with flat config. `next lint` was removed in Next.js 16 and `next build` no longer lints, so CI runs ESLint itself. Covers `<img>` instead of `next/image`, synchronous scripts, and similar patterns.

**Exception**: a per-rule disable with a reason, for example an SVG sprite where `next/image` adds nothing.

### next-action-authz
scope: next, severity: critical, enforcement: review

A Server Action is reachable by a direct POST, whether or not the UI that renders it checked anything. A page-level auth check does not extend to the actions defined in it, and a `proxy.ts` matcher is not an authorization layer. Every Server Action and Route Handler verifies authentication and authorization itself, inside the action or in the server-only data access layer it calls, including ownership of the specific resource (otherwise an authenticated user deletes someone else's record by changing an id).

BAD: an action that calls `db.post.delete({ where: { id } })` because the page above it redirected anonymous users.
GOOD: the action, or the DAL function it delegates to, loads the session, rejects when there is none, loads the resource, and rejects when the caller does not own it.

**Exception**: an action that is public by design (a newsletter sign-up), with input validation and rate limiting, and a comment saying it is public.

### next-server-only
scope: next, severity: major, enforcement: review

A module that reads secrets, the database, or `process.env` server variables, imported somewhere that ends up in a Client Component, or a whole database record passed as a prop to a `'use client'` component. Every field of a prop crosses to the browser, and a Server Action's return value is serialized to the client the same way.

GOOD: modules that touch secrets or data start with `import 'server-only'`, which turns a client import into a build error. Only the data access layer reads `process.env` secrets. Client props and action return values are minimal DTOs holding only the fields the UI renders.

Escalate to `critical` when a secret, a token, or another user's private field reaches a client prop or a return value.

**Exception**: none for secrets. A DTO with public fields only is the satisfied form of the rule.

### next-use-client-scope
scope: next, severity: minor, enforcement: review

`'use client'` on a page or layout makes its whole subtree client code: data fetching moves to the browser, and the bundle grows. It belongs on the smallest interactive leaf.

The finding is a page or layout marked `'use client'` whose interactive part could be extracted into a child, or a `'use client'` component with no hook, no handler, and no browser API.

**Exception**: an interactive leaf component, which is exactly where the directive belongs.

### next-revalidate-after-mutation
scope: next, severity: major, enforcement: review

A Server Action or Route Handler that changes data shown from a cache, with no revalidation. The write succeeds and the user keeps seeing the old value, which reads as "my save did not work".

GOOD, by the semantics needed:
- `updateTag(tag)` in a Server Action when the user must see their own write immediately (forms, settings).
- `revalidateTag(tag, 'max')` for stale-while-revalidate on content that tolerates a background refresh. The single-argument form is deprecated in Next.js 16.
- `revalidatePath(path)` when the data is not tagged.
- `refresh()` in a Server Action for uncached data shown elsewhere on the page.

**Exception**: the mutated data is not cached anywhere (fully dynamic rendering), which is the default without `'use cache'`.

### next-public-env
scope: next, severity: major, enforcement: review

`NEXT_PUBLIC_` variables are inlined into the client bundle at build time, and only where the code reads them literally as `process.env.NEXT_PUBLIC_API_URL`. A helper that looks them up dynamically (`process.env[name]`) works on the server and ships `undefined` to the browser.

BAD: `requireEnv('NEXT_PUBLIC_API_URL')` that reads `process.env[name]` inside the helper.
GOOD: `requireEnv('NEXT_PUBLIC_API_URL', process.env.NEXT_PUBLIC_API_URL)`, passing the literal access so the build can inline it, with `cfg-fail-fast` applied to the result.

Anything prefixed `NEXT_PUBLIC_` is public: never a secret.

**Exception**: none.
