# Core rules

Any language. Examples are TypeScript; the failure is the same elsewhere, and `rust.md` maps the ones whose expression differs.

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `bnd-validate-once` | major | review | external data trusted without validation, or validated at every call site |
| `fb-shape-uncertainty` | major | review | fallback across two possible wire shapes |
| `fb-domain-default` | major | review | fallback inventing a domain decision |
| `fb-stacked` | minor | review | fallback layered on a fallback |
| `err-domain-typed` | major | review | untyped error for a failure the caller must branch on |
| `err-swallow` | major | both | error caught and dropped |
| `err-parse-at-boundary` | minor | review | error bodies parsed at call sites |
| `cfg-fail-fast` | major | review | required configuration falling back silently |
| `cmt-narrative` | nit | review | comment narrating the next line |
| `arch-duplicated-logic` | minor | review | same logic in a third place |
| `arch-divergent-change` | minor | review | one file edited for unrelated reasons |
| `arch-reinvented-wheel` | minor | review | hand-rolled what the platform or a dependency does |
| `obs-failure-traceable` | minor | review | failure leaves no actionable trace |
| `test-subtle-path` | minor | review | only the happy path covered |
| `test-no-weakening` | major | review | test, assertion, or check loosened to get green |
| `sec-hardcoded-secret` | critical | both | credential in source |
| `sec-sensitive-log` | critical | review | token, credential, or personal data logged |

---

# Boundaries and fallbacks

### bnd-validate-once
scope: core, severity: major, enforcement: review

Data from outside the process (network, files, environment, user input, queue messages) is validated once, where it enters, and mapped into the program's own types. Everything downstream trusts those types. Skipping the validation moves the failure far from its cause, into a formatter or a loop, with a type that says the value cannot be missing. Repeating it at every call site is the opposite defect: dead guards that hide which layer owns the contract.

**Exception**: data from a client generated from a schema that already validates at runtime. The generated layer is then the boundary, and the finding would be a second hand-written validation of it.

### fb-shape-uncertainty
scope: core, severity: major, enforcement: review

`data.user_id ?? data.userId` means nobody decided what the server sends. Both shapes ship forever, and the day the backend drops one, nothing fails: the value silently becomes `undefined` and travels.

BAD: `const id = data.user_id ?? data.userId`
GOOD: find out which shape the server sends, type that one, and throw a `ContractError` on anything else.

Escalate to `critical` when the diff removes an existing guard or the server has already changed shape.

**Exception**: a documented migration window, with a link to the ticket that removes the second branch and a date. Without the ticket it is not a migration, it is the bug.

### fb-domain-default
scope: core, severity: major, enforcement: review

`a ?? b` where `a` and `b` mean different things to a user is a product decision written as an operator. Nobody reviewing the diff can tell whether it was decided or defaulted.

BAD:
```tsx
<DeliveryDate value={order.confirmedAt ?? order.requestedAt} />
```
A confirmed delivery date and a requested one are not the same fact. Rendering both the same way tells the customer a date is agreed when it is not.

GOOD: make the distinction explicit where the two differ, then render each state for what it is.
```tsx
const delivery = order.confirmedAt
  ? { date: order.confirmedAt, state: 'confirmed' as const }
  : { date: order.requestedAt, state: 'requested' as const }
```

**Exception**: the two values are interchangeable for the user and a comment says why. "Display name falls back to the handle, both are public identifiers" is a decision. `user.name ?? user.email` is not, because one of those is an email address.

### fb-stacked
scope: core, severity: minor, enforcement: review

A fallback on top of a fallback means the author did not trust the layer below, and the second layer is dead code nobody will see run.

BAD: `case 'VALIDATION_ERROR': return err.fields[0]?.message ?? err.message`

Either a validation error always carries a field, and the fallback hides a contract break, or it does not, and the type is lying. Decide which is true and encode it: `fields: [FieldError, ...FieldError[]]` makes `err.fields[0].message` safe with no fallback and no assertion.

**Exception**: the two sources are genuinely different layers you do not control, for example a library error that may or may not carry a `cause`.

---

# Errors

### err-domain-typed
scope: core, severity: major, enforcement: review

A domain failure is one the calling code handles at runtime: bad credentials, an order the supplier refused, a slot already taken. The caller branches on which one, and a message string is not branchable; it is also user-facing copy, so editing the copy would change control flow.

BAD: `throw new Error('Invalid credentials')`
GOOD:
```ts
export type AuthErrorCode = 'INVALID_CREDENTIALS' | 'ACCOUNT_LOCKED' | 'EMAIL_UNVERIFIED'

export class AuthError extends Error {
  readonly code: AuthErrorCode

  constructor(code: AuthErrorCode, message: string, options?: ErrorOptions) {
    super(message, options)
    this.name = 'AuthError'
    this.code = code
  }
}
```
Before adding an error class, look for the one this repository already has for the same layer. A second hierarchy for one domain is worse than a slightly awkward fit in the existing one.

**Exception**: a programmer error is not a domain error and correctly uses a plain error with a precise message: missing configuration, a hook used outside its provider, a broken internal invariant. The test is who recovers. A developer, by changing code or configuration: plain error. The calling code, at runtime, by doing something different: typed code.

### err-swallow
scope: core, severity: major, enforcement: both

`catch {}` and `.catch(() => undefined)` turn a failure into a wrong result, and the next person debugging it has no line to start from. Log it with enough context to find the call site; better, classify it and decide.

Owner: `no-empty` catches the literal empty block. A `.catch(() => undefined)` or a catch holding only a comment is the review half.

**Exception**: a cleanup path where the failure is irrelevant and a one-line comment says so, for example aborting a request whose result is no longer needed.

### err-parse-at-boundary
scope: core, severity: minor, enforcement: review

The shape of an error body is part of the wire contract, so it is parsed where the response is read, into a typed error, not in each component that catches.

**Exception**: an endpoint with a unique error payload, parsed next to its own client function.

### cfg-fail-fast
scope: core, severity: major, enforcement: review

`process.env.API_URL ?? ''` starts the program and fails later, as an opaque 401 or a request to `https:///users`. Required configuration is read once, validated, and exposed as a typed object; a missing or malformed value stops the process at startup, where CI or the deploy catches it. Domain code receives that object instead of reading the environment itself.

BAD: `const apiUrl = process.env.API_URL ?? ''`
GOOD: one `loadConfig()` at startup that throws `Missing required environment variable API_URL`, and code that takes `config.apiUrl`.

Escalate to `critical` when the silent fallback weakens security: an empty signing secret, auth disabled, a permissive CORS origin.

**Exception**: a genuinely optional integration where absence is a supported mode with a documented no-op path. Analytics keys usually qualify: the program is correct without them.

---

# Comments

### cmt-narrative
scope: core, severity: nit, enforcement: review

A comment inside a function that says what the next line does (`// loop over the orders`) or paraphrases it. It goes stale on the first edit and teaches nothing a name could not.

GOOD: explain the why above the function, type, or constant when it is not obvious; inside a body, comment only a genuine gotcha (a platform quirk, a library workaround, a non-local invariant).

**Exception**: a comment that records why the obvious alternative was rejected. That is a decision, not narration.

---

# Structure and duplication

Rules about what the next change will cost, not what this one breaks. That is why the family sits at `minor` with one stated escalation, under the nit cap. This is also the one family that looks outside the diff, anchored on what the diff adds and never as a free sweep: duplication is invisible inside a patch.

Shotgun surgery is deliberately absent: in a diff it is indistinguishable from a rename or a deliberate refactor, so it costs more false positives than it finds.

### arch-duplicated-logic
scope: core, severity: minor, enforcement: review

Logic that now exists in more than two places. Each copy is defensible and the set is not: copies drift, the next reader cannot tell which is canonical, and a fix lands in one of them.

Counting is the rule. Two copies are acceptable and often better than a premature abstraction. Three is the finding, reported on the new occurrence, with `file:line` for each existing one as evidence. Search for the same shape, not the same name: a helper copied between apps is usually renamed.

Escalate to `major` when the duplicated thing is a domain rule: a price or tax calculation, a permission check, a state transition. Two copies of a price calculation will disagree, and the user sees a wrong number.

**Exception**: duplication across a boundary kept on purpose (a shared package that must not depend on an app, a fixture that must not import the code under test, a generated file). And two is not three.

### arch-divergent-change
scope: core, severity: minor, enforcement: review

One file edited in this diff for two or more unrelated reasons. This replaces any length limit, which this catalog refuses to set: a 700-line translation table is healthy, a 60-line module that changes whenever any of three concerns moves is not. Read it from the hunks: a page that in one diff gains a data fetch, a CSV export, and a permission check.

**Exception**: a registry, barrel, translation map, route table, or generated file, whose job is to change whenever anything registers. Name which kind it is.

### arch-reinvented-wheel
scope: core, severity: minor, enforcement: review

A hand-written version of something the language, the platform, or an installed dependency already does: time zones, Unicode, decimal rounding, URL parsing, deep equality, debouncing, retry with backoff, grouping. Every line is maintained and tested at edges the real implementation already handles.

All three conditions, or it is not this finding:

1. You can name the existing thing: the standard function available in the configured language level (for TypeScript, in the `lib` the tsconfig declares), the platform API, or the installed package and its export. Read the manifest before claiming a dependency exists. Suggesting a new dependency is not this finding.
2. It fits: the semantics needed are the semantics it gives, without a wrapper or a workaround.
3. The custom version is not deliberately narrower. A four-line helper that does one thing on purpose is often better than a general-purpose module.

**Exception**: the inverse is just as real. Pulling a dependency in to replace ten lines you fully understand costs bundle size, supply-chain surface, and upgrades owed forever. When the custom version is small, tested, and narrow, the rule is satisfied.

---

# Observability

### obs-failure-traceable
scope: core, severity: minor, enforcement: review

A failure path that leaves nothing actionable. Two shapes: nothing recorded (the user sees a message, no trace exists, you learn about it from a customer), or recorded without identifiers (`console.error('payment failed', err)` across a thousand payments a day answers nothing).

An actionable trace has the operation, the outcome, and the identifiers that find this one occurrence: a request or correlation id, the acting user or tenant id, the resource id. Never the payload, a token, or personal data: `sec-sensitive-log` wins whenever the two pull apart.

```ts
logger.error('order.confirm.failed', {
  orderId,
  tenantId,
  code: err instanceof ApiError ? err.code : 'UNKNOWN',
})
```

Escalate to `major` where money moves, a permission is granted, or data is deleted.

**Exception**: a failure already traced one layer up (say where), a validation error the user sees and corrects immediately, or a path covered by a named metric or alert.

---

# Tests

### test-subtle-path
scope: core, severity: minor, enforcement: review

The happy path is the one that already works. The value is in the race, the retry, the refresh lock, the revoked token, the empty list, the error variant. This is an absence finding: name the untested path and where its test would go, not "coverage could be better".

Escalate to `major` on a path that moves money, changes authorization, or deletes data.

**Exception**: a diff that adds no behavior, such as a rename or a copy change.

### test-no-weakening
scope: core, severity: major, enforcement: review

A test skipped, deleted, or loosened, an assertion removed, a snapshot regenerated over a real change, a lint rule disabled, a type widened, or a `@ts-expect-error` added, in order to get the suite green. It is the most common way an agent reports success on broken code. A red check is a finding about the code, not an obstacle.

**Exception**: the behavior under test was removed or changed on purpose, and the commit says so. Then the test changes with it, in the same commit.

---

# Secrets and logging

### sec-hardcoded-secret
scope: core, severity: critical, enforcement: both

A credential in source is in git history, build artifacts, and every clone, and stays valid after the line is deleted. Test files and example configuration included. Rotate it; deleting it is not enough.

Owner: a secret scanner (gitleaks in CI, or GitHub push protection) when the repository has one. Without one, this is `review`.

**Exception**: an obviously fake value in a test, such as a token signed with `test-secret` whose payload is visibly synthetic. A real-shaped key is never an exception.

### sec-sensitive-log
scope: core, severity: critical, enforcement: review

Logs reach third-party services and people who must not see a user's token or address. Log the fields you chose, never a whole request, response, or error object that may carry them.

BAD: `logger.error('login failed', { body })`
GOOD: `logger.error('login failed', { status: res.status, code: err.code })`

**Exception**: none. "Only in development" is not one: the line ships.
