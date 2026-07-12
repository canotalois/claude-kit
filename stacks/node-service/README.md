# Node service starter

A backend TypeScript service preset (HTTP API, workers, jobs) wired to the claude-kit conventions. For a React/web app use `node-web` instead.

## What comes with it

- `GUIDELINES.md`: the "don't" checklist the `/review` skill enforces on a branch, focused on server-side concerns (boundary validation, typed errors and HTTP mapping, transactions, idempotency and concurrency, structured logging without secrets, module boundaries).

This stack ships the guidelines only. Its idioms are framework-agnostic (Express, Fastify, NestJS, a queue worker) and pair with whatever config the target repo already has, so no `tsconfig`/CI is imposed here.

## Use it

Copy `guidelines/core.md` and this `GUIDELINES.md` into the repo root (or vendor them), so `/review` and any review automation read both. A domain-specific service adds its own overlay section below the vendored content (for example a payments service adds a ledger-invariant and no-PAN-in-logs section) rather than editing the shared stack.

## Conventions

`GUIDELINES.md` plus `guidelines/core.md` are the source of truth. Run `/review` before a PR to check the branch against both.
