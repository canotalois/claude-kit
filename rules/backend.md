# Backend rules

On top of `core.md`, for a service that owns state: HTTP APIs, Server Actions that write, workers, jobs. Language-agnostic; examples name common TypeScript tools (Fastify, Prisma, Postgres) only where a tool has a gotcha.

Most of these are `critical` on purpose: a bug here costs money or exposes another tenant's data, and shipping a fix does not undo either.

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `api-money` | critical | review | money in floating point, or rounded more than once |
| `api-webhook-signature` | critical | review | webhook processed before its signature is verified |
| `api-idempotent` | critical | review | retried request or redelivered event repeats a side effect |
| `api-tx-multistep` | critical | review | dependent writes outside one transaction, or network calls inside it |
| `api-tenant-scope` | critical | review | query scoped by a request field instead of the session |
| `api-db-invariant` | major | review | invariant guarded only by read-then-write in application code |
| `api-route-schema` | major | review | route that takes input with no declared schema |
| `api-no-internal-leak` | major | review | internal error detail returned to the client |
| `api-migration-reviewed` | major | review | destructive or locking migration applied unreviewed |
| `api-error-mapping` | minor | review | domain errors mapped to HTTP status in each handler |

---

### api-money
scope: backend, severity: critical, enforcement: review

Money is never an IEEE float: `0.1 + 0.2` is not `0.3`, and the error lands in an invoice or a payout. Store integer minor units using the currency's ISO 4217 exponent (2 for EUR, 0 for JPY, 3 for KWD), or an arbitrary-precision decimal (`numeric` in Postgres, `Decimal` in the ORM, a decimal library in code). Rates and percentages are decimals. Round once, with a named rounding mode, at a named step; every intermediate rounding is a cent someone will dispute.

**Exception**: none. Display formatting converts at the edge.

### api-webhook-signature
scope: backend, severity: critical, enforcement: review

An unverified webhook endpoint is an unauthenticated write endpoint for anyone who knows the URL. Verify the signature against the raw request body before parsing, with a constant-time comparison (`crypto.timingSafeEqual`, or the provider's SDK), reject a timestamp outside the provider's tolerance window to stop replays, and do all of it before any side effect. Most frameworks parse JSON before the handler runs, which destroys the raw body: configure raw-body access for that route (in Fastify, a content-type parser that keeps the buffer).

**Exception**: none.

### api-idempotent
scope: backend, severity: critical, enforcement: review

Clients retry, users double-submit, and providers redeliver events, sometimes out of order. Where a repeat would duplicate an external effect (a charge, a refund, an email, a shipment, a credit), the operation is keyed: an idempotency key from the client, or the provider's event id, stored under a unique constraint so a replay is detected and returns the first result. State transitions are monotonic: an event older than the current state is ignored, not applied.

**Exception**: an operation that is naturally idempotent (setting a field to a value, a read). The rule targets effects that accumulate.

### api-tx-multistep
scope: backend, severity: critical, enforcement: review

Writes that must all happen go in one transaction, or a failure between them leaves an order with no lines or a payment with no order. And no network call inside a transaction: a slow payment provider or mail server then holds locks and connections, and a rollback cannot unsend the email. Commit first, then trigger the side effect through an outbox table that a worker drains.

**Exception**: steps that are each meaningful and retriable on their own, with a comment saying how a partial state is reconciled.

### api-tenant-scope
scope: backend, severity: critical, enforcement: review

Every query that reads or writes tenant data is scoped by the tenant derived from the authenticated session (a membership lookup for multi-user tenants), never by an id taken from the body, query, or path. An unscoped query is a horizontal privilege escalation that produces no error. Row-level security in the database is a good second layer, not a substitute.

**Exception**: an admin route behind a verified admin role, where the wide scope is the point. Say so at the call site.

### api-db-invariant
scope: backend, severity: major, enforcement: review

Read-then-write in application code (check the email is free, then insert) is a race by construction: two requests both pass the check. Guard the invariant where it cannot race: a unique index, a conditional update (`UPDATE ... WHERE status = 'pending'` and check the affected row count), or a row lock.

**Exception**: an invariant that cannot be expressed in the database, enforced under a lock or a serializable transaction, with a comment naming it.

### api-route-schema
scope: backend, severity: major, enforcement: review

Every route that takes input declares its request schema (a Fastify JSON schema, zod, TypeBox), so validation happens once at the edge, the handler receives typed input, and the same schema produces the API documentation and any generated client. A route without one is unvalidated and undocumented at once.

**Exception**: none for a route that takes input.

### api-no-internal-leak
scope: backend, severity: major, enforcement: review

A stack trace, an SQL error, a driver message, or an internal hostname returned to the client tells an attacker how the service is built and tells the user nothing. Return the typed error code and a safe message; log the detail with the request id (`obs-failure-traceable`).

**Exception**: development-only error pages that the production build cannot serve.

### api-migration-reviewed
scope: backend, severity: major, enforcement: review

A generated migration is read before it is applied. Dropping or renaming a column, changing a type, or adding a non-null column without a default breaks the running version during a deploy or locks a large table. Destructive changes go through expand and contract: add the new shape, migrate reads and writes, backfill, then remove the old shape in a later release.

**Exception**: a table that is provably empty or not yet read by any deployed version.

### api-error-mapping
scope: backend, severity: minor, enforcement: review

Mapping domain errors to HTTP status codes in every handler drifts: the same `NOT_FOUND` becomes a 404 in one route and a 400 in another. Handlers throw domain errors; one error handler at the boundary maps codes to statuses.

**Exception**: a handler whose status is part of a specific contract, such as a 202 for an accepted async job.
