# Guidelines: Rust

Overlay on `guidelines/core.md`. The core spine (contracts, nullish, errors, comments, don't-reinvent, tests, commits) applies as-is; this file maps each principle to Rust idioms. `/review` checks the branch against both.

## Types and safety

- Don't `#![allow(...)]` a lint to make a warning disappear. Fix the cause or justify the allow in one line above it.
- Don't reach for `unsafe`. The workspace forbids it; a genuine need is a reviewed exception with a `// SAFETY:` note.
- Do make illegal states unrepresentable with enums and newtypes rather than validating primitives everywhere.

## Errors (the `Result` discipline)

- Don't `.unwrap()` or `.expect()` on anything fallible that comes from outside (IO, parsing, network, user input). Propagate with `?`.
- Don't return `Box<dyn Error>` or `anyhow::Error` from a library crate. Define a typed error enum (`thiserror`) whose variants are the discriminated codes.
- Do keep `anyhow` for the binary / top layer only, where you just want context and exit.
- Do add context at the boundary (`.map_err(...)` / `.context(...)`), not at every call site.

## Ownership and fallbacks

- Don't `.clone()` to dodge the borrow checker without a reason. Borrow, or restructure.
- Don't `.unwrap_or(default)` to paper over a decision that should be explicit. Match the `Option`/`Result` and handle both arms.
- Do prefer `?` and iterator combinators over manual loops and early-return ladders.

## Boundaries

- Do validate external input with `serde` into typed structs at the edge, then trust the types.
- Do fail fast at startup for missing required config (no empty-string default).

## Packages (workspace)

- Don't grow a single `lib.rs`/`main.rs` past a screen or two. Split into modules and crates.
- Do use a Cargo workspace with shared `[workspace.lints]` so strictness is enforced in one place.

## Comments and docs

- Do write `///` doc comments above public items when the why is not obvious. No mid-function narration.

## Tests

- Do put unit tests in `#[cfg(test)] mod tests` and cross-crate tests in `tests/`. Cover the error variants, not just `Ok`.
