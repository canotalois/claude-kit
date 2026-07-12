# Guidelines: Node service (TypeScript backend)

Overlay on `guidelines/core.md`. The core spine (contracts, nullish, errors, comments, don't-reinvent, tests, commits) applies as-is; this file adds the specifics of a server-side TypeScript service (HTTP API, workers, jobs) with a database. No frontend concerns. `/review` checks the branch against both.

Use this stack for a backend that owns state and talks to a network boundary (Express, Fastify, NestJS, a queue worker). For a React/web app use `node-web` instead.

## TypeScript

- Don't cast `unknown` data with `as`. Validate (custom guard, zod), then narrow.
- Don't type a request body, query, or external response as `any` or `Record<string, unknown>`. Define the contract.
- Don't cast `process.env.X` to `string`. It is `string | undefined`. Read it once, validate, expose a typed config.
- Don't use `!` (non-null assertion) to silence the compiler. If you need it, write a guard.
- Don't encode one domain state in two or more booleans. Use a discriminated union with a `status` field.
- Don't disable `strict` or `noUncheckedIndexedAccess`. They stay on.

## Boundary and config

- Do validate every inbound payload (HTTP body, query, params, webhook, queue message) at the edge with a schema, map it once into a domain type, then trust it downstream.
- Do build one typed config object at startup from the environment, validated. Fail at boot on a missing or malformed required value, never a silent fallback to `''` or `0`.
- Don't read `process.env` deep inside domain or business logic. Inject the typed config.

## Errors and HTTP mapping

- Don't raise a bare `Error` for a domain failure. Use a typed error with a discriminated `code` the caller can switch on.
- Don't map errors to HTTP status codes in each handler. Classify once at a single boundary filter/middleware; handlers throw domain errors.
- Don't leak an internal message, stack, or driver error to the client. Return the typed code plus a safe message.
- Don't swallow an error (empty catch, discarded promise). Log with context, then rethrow or classify.

## Persistence and transactions

- Do run one unit of work per command: a handler that mutates several rows wraps them in a single transaction. No half-applied writes.
- Don't issue a fire-and-forget write inside a request without awaiting and handling its failure.
- Do keep migrations explicit and reviewed. Hand-written SQL with a journal beats a blindly generated diff; never let a generator invent a destructive migration unread.
- Don't perform a silent `UPDATE ... SET` on state the domain must be able to audit. Emit the row/event the domain contract requires.

## Concurrency and idempotency

- Do make every state-mutating endpoint idempotent: an idempotency key or a natural unique constraint, so a retried or double-submitted request produces exactly one effect.
- Do assume two requests race. Guard the invariant in the database (unique index, conditional update, row lock), not only in application code.
- Don't rely on read-then-write without a guard; it is a race by construction.

## Logging and secrets

- Do emit structured logs (JSON) with a correlation/request id threaded from the boundary.
- Don't log secrets, tokens, credentials, full auth headers, or PII. Redact at the source, not at the sink.
- Don't put a secret in an error message, a URL, or a log line "just for debugging".

## Modules and dependencies

- Do keep the domain layer pure: no framework imports, unit-testable in isolation. Dependency direction is domain <- application <- infrastructure.
- Do bind ports to adapters at the module edge (dependency injection), so the core depends on an interface, not a driver.
- Don't grow a god file or a god service. Split by bounded context.
- Don't deep-import another package's `src/`. Go through its `exports` map. In a library, keep framework packages as peers, not `dependencies`.

## Tests

- Do cover, for every state-mutating path: the contract (request/response or event schema), idempotency (double-fire produces one effect), and concurrency (two racing calls converge to the invariant).
- Do integration-test against a real dependency (a test database, the real sandbox of a third party) rather than asserting against your own mock of an unspecified contract.
- Don't weaken, skip (`.skip`), or delete a test to make the suite green. A red test is a finding, not an obstacle.
- Do write one test per behavior, named for the behavior.

## Commits and PR

- Do keep commits atomic, messages in English, and write a PR description with scope and a test plan.
- Don't bypass pre-commit or signing hooks.
