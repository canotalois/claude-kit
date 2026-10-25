# TypeScript rules

On top of `core.md`, for any TypeScript code, frontend or backend. The `lint` rules are owned by the ESLint config the `node-web` and `node-service` stacks ship (`typescript-eslint` `strictTypeChecked` plus the rules named below); in a repository without a lint gate they are reviewed as `both`.

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `lint-explicit-any` | major | lint | `any` in application code |
| `lint-non-null` | major | lint | `!` non-null assertion |
| `lint-unused` | nit | lint | unused variables and imports |
| `lint-floating-promise` | major | both | promise neither awaited nor handled |
| `lint-format` | nit | lint | formatting |
| `ts-boundary-cast` | major | review | `as` on unvalidated external data |
| `ts-wire-type-once` | major | review | one wire type defined in several places |
| `ts-nullable-api` | major | review | nullable platform getter cast to non-null |
| `ts-unrepresentable-state` | major | review | type permits a state the domain forbids |
| `ts-inline-domain-shape` | minor | review | domain record rebuilt inline with no named type |
| `ts-index-access` | major | both | indexed access silenced instead of handled |
| `ts-exhaustive` | minor | lint | `switch` over a union with no exhaustiveness check |
| `fb-optional-callback` | nit | review | `cb?.()` at every call site |
| `pkg-exports-map` | minor | both | deep import into another package's internals |

---

# Tooling owns these

### lint-explicit-any
scope: typescript, severity: major, enforcement: lint

`any` switches checking off for everything it touches. Use `unknown` and narrow, or write the type.

Owner: `@typescript-eslint/no-explicit-any`.

**Exception**: a `.d.ts` shim for an untyped third-party module, with a comment naming the package.

### lint-non-null
scope: typescript, severity: major, enforcement: lint

`!` asserts what the compiler cannot see. If the value is there, prove it with a guard and the next reader learns why.

Owner: `@typescript-eslint/no-non-null-assertion`.

**Exception**: none in application code. `ts-index-access` covers the array case people reach for `!` to solve.

### lint-unused
scope: typescript, severity: nit, enforcement: lint

Owner: `@typescript-eslint/no-unused-vars`, with `^_` ignored for intentionally unused parameters, and `noUnusedLocals` in the tsconfig.

**Exception**: none.

### lint-floating-promise
scope: typescript, severity: major, enforcement: both

An unawaited promise turns a failure into an unhandled rejection with no stack pointing at your code. An async function passed where a void callback is expected (`onClick={async () => ...}`) does the same.

Owner: `@typescript-eslint/no-floating-promises` and `@typescript-eslint/no-misused-promises`, both type-aware. Lint accepts `void doThing()`; the review half is that a deliberately unawaited promise still has a `.catch` that logs.

**Exception**: none beyond the explicit `void` plus `.catch`. The `void` is the signal that it was a decision.

### lint-format
scope: typescript, severity: nit, enforcement: lint

Formatting is not a review topic. The repository's formatter runs on commit; nobody discusses it again.

**Exception**: none.

---

# Contracts

### ts-boundary-cast
scope: typescript, severity: major, enforcement: review

The TypeScript form of `bnd-validate-once`. `as` on data from outside the process is a claim the compiler believes and nothing checks. The failure lands later, in code whose type says the value cannot be missing.

BAD:
```ts
const user = (await res.json()) as UserResponse
```
GOOD: parse with a schema, once, at the boundary.
```ts
const UserResponse = z.object({ id: z.string(), company: z.object({ name: z.string() }) })
type UserResponse = z.infer<typeof UserResponse>

const user = UserResponse.parse(await res.json())
```
Any Standard Schema library works (zod, valibot, arktype). A hand-written type guard is acceptable only when it checks every field the code goes on to read; a guard that checks one field and asserts the rest is a cast with extra steps.

**Exception**: an `as` that narrows a type the compiler already knows, with no external data involved: `as const`, or narrowing a union already discriminated in the same scope.

### ts-wire-type-once
scope: typescript, severity: major, enforcement: review

One module per boundary holds the shape the server sends; everything else imports it. Two definitions of one payload drift, and the drift stays invisible until they disagree about whether a field is optional. When the client is generated from an OpenAPI or GraphQL document, the generated types are the boundary, and a hand-written interface for a covered endpoint is the copy that will go stale.

**Exception**: a view model assembled from several wire types is not a wire type. It lives next to the component that renders it.

### ts-nullable-api
scope: typescript, severity: major, enforcement: review

`URLSearchParams.get()`, `localStorage.getItem()`, `element.closest()`, `Map.get()` return `T | null` or `T | undefined`; `FormData.get()` returns `FormDataEntryValue | null`, which includes `File`. Casting that away compiles, and moves a missing-field bug from the parse site to wherever the value is used.

BAD: `const email = formData.get('email') as string`
GOOD:
```ts
const email = formData.get('email')
if (typeof email !== 'string' || email.length === 0) {
  return { status: 'invalid', field: 'email' } as const
}
```

No lint rule catches the cast. `@typescript-eslint/consistent-type-assertions` with `assertionStyle: 'never'` can ban assertions in boundary files where that is practical.

**Exception**: none. The guard is three lines and it is where the user-facing validation message belongs.

### ts-unrepresentable-state
scope: typescript, severity: major, enforcement: review

A type that permits a state the domain forbids. It compiles, each line reads fine, and the contradiction is built one call site at a time until two consumers disagree about what the data means. The test: can you write a value of this type that the domain says cannot exist?

The most common shape is several booleans describing one thing. Two booleans encode four states when you meant three, and the fourth is the bug.

BAD: `{ isLoading: boolean; isAuthenticated: boolean; user: User | null }`
GOOD: `{ status: 'loading' } | { status: 'anonymous' } | { status: 'authenticated'; user: User }`

The second shape is a list whose entries must be unique per key. Nothing stops the same key appearing twice with contradictory values, so precedence becomes an undocumented decision every consumer makes differently.

BAD:
```ts
const effective = [
  ...fromRoles.map((rule) => ({ rule, allowed: true })),
  ...overrides.map((o) => ({ rule: o.rule, allowed: o.effect === 'allow' })),
]
```
GOOD: key it, and reconcile once where the data is built.
```ts
const effective = new Map<RuleId, { rule: Rule; allowed: boolean }>()
for (const rule of fromRoles) effective.set(rule.id, { rule, allowed: true })
for (const o of overrides) effective.set(o.rule.id, { rule: o.rule, allowed: o.effect === 'allow' })
```

Other shapes: two fields that can disagree about one fact, an optional field required in half the states, a payload present for the wrong status.

**Exception**: independent flags that genuinely compose (`isOpen` on a drawer next to `isSubmitting` on its form), a wire type that mirrors what the server sends (the reconciliation then belongs at the boundary that maps it inward), and an append-only log where duplicates are the record.

### ts-inline-domain-shape
scope: typescript, severity: minor, enforcement: review

A domain record built inline at two or more sites with no named type. Adding a field updates one site and silently leaves the others behind. The tell is an `as const` on a domain literal inside an object literal, needed only because nothing declares the type.

GOOD: declare `type EffectivePermission = { rule: Rule; allowed: boolean; source: 'role' | 'override' }` once, and type every construction site against it, with an annotation or `satisfies EffectivePermission`.

**Exception**: a local literal with no domain meaning, a single construction site, or a shape a generated type already names, in which case the finding is that the generated type is not used.

### ts-index-access
scope: typescript, severity: major, enforcement: both

With `noUncheckedIndexedAccess` on, `items[0]` is `T | undefined`. Reaching for `!` throws away the one warning you were given, and a length check above the access does not narrow the type.

BAD: `const first = items[0]!`
GOOD:
```ts
const [first] = items
if (first === undefined) return null
```
When emptiness is impossible by contract, encode it in the type (`[Item, ...Item[]]`) at the boundary instead of asserting at the use site.

Owner: `noUncheckedIndexedAccess` plus `lint-non-null` catch the assertion; a reviewer catches a guard that hides a contract question.

**Exception**: a tuple type whose length is part of the type, where indexed access is already non-optional.

### ts-exhaustive
scope: typescript, severity: minor, enforcement: lint

A `switch` over a union with no exhaustiveness check stays silent when a variant is added, and the new case falls through to the default.

Owner: `@typescript-eslint/switch-exhaustiveness-check` (not in any preset; the stacks enable it). Without the lint rule, end the switch with `default: return value satisfies never`.

**Exception**: a switch that deliberately handles a subset with a meaningful `default`, which the lint rule allows when `considerDefaultExhaustiveForUnions` is set.

### fb-optional-callback
scope: typescript, severity: nit, enforcement: review

`props.onChange?.()` repeated at eight call sites handles optionality eight times instead of once. Default it where the object is built, `const onChange = props.onChange ?? noop`, then call `onChange()`.

**Exception**: a single call site. A `noop` default for one use adds a name for nothing.

---

# Packages

### pkg-exports-map
scope: typescript, severity: minor, enforcement: both

`import { x } from '@scope/pkg/src/internal/x'` reaches past the package's contract and breaks when the file moves. Everything importable is declared in the package's `exports`.

Owner: `exports` blocks the import at resolution for consumers that respect it; the stacks add `no-restricted-imports` for `@*/*/src/**` because tsconfig `paths` aliases bypass `exports`.

**Exception**: none. If you need the internal, export it.
