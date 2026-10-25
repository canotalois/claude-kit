# Rust rules

On top of `core.md`, for a Cargo workspace on edition 2024. The `lint` rules are owned by the `[workspace.lints]` and `clippy.toml` the `rust` stack ships; CI runs Clippy with `-D warnings`.

## Core rules in Rust

| Core ID | Rust expression |
| --- | --- |
| `bnd-validate-once` | `serde` into typed structs at the edge; newtypes with a validating constructor for constrained values |
| `fb-domain-default` | `.unwrap_or(default)` or `.unwrap_or_default()` papering over a decision; match both arms instead |
| `err-domain-typed` | `rs-lib-error`: an error enum per library crate |
| `err-swallow` | `let _ = fallible()` or `.ok()` discarding an error that mattered |
| `ts-unrepresentable-state` | the same rule: enums with data instead of flag fields and `Option`s that must agree |

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `rs-unwrap` | major | both | `unwrap` on a fallible value, or `expect` on external data |
| `rs-lint-suppression` | minor | lint | `#[allow]` instead of `#[expect]` with a reason |
| `rs-unsafe` | major | lint | `unsafe` in a crate that inherits the workspace lints |
| `rs-lib-error` | major | review | opaque error type returned from a library crate |
| `rs-error-context` | minor | review | context added at every call site, or nowhere |

---

### rs-unwrap
scope: rust, severity: major, enforcement: both

`.unwrap()` turns any failure into a panic with no context. On data from outside (IO, parsing, network, user input) the failure is expected, so it is propagated with `?`.

Owner: `clippy::unwrap_used`, allowed in tests by `allow-unwrap-in-tests` in `clippy.toml`. The review half: `.expect("...")` is acceptable only for an invariant the program guarantees, and its message states that invariant (`expect("regex is a valid literal")`), never for external data.

**Exception**: tests, and a one-off binary such as a build script where a panic is the intended failure report.

### rs-lint-suppression
scope: rust, severity: minor, enforcement: lint

`#[allow(lint)]` silences a lint forever, even after the code that needed it is gone. `#[expect(lint, reason = "...")]` (stable since Rust 1.81) states why, and warns when the suppression is no longer needed.

Owner: `clippy::allow_attributes` and `clippy::allow_attributes_without_reason`.

**Exception**: none. Fix the cause, or write the reason.

### rs-unsafe
scope: rust, severity: major, enforcement: lint

The workspace sets `unsafe_code = "forbid"`, which no attribute inside a crate can relax. Code that genuinely needs `unsafe` (FFI, a measured hot path) lives in its own crate that does not inherit the workspace lints, sets `unsafe_code = "deny"` with local `#[expect]` exceptions, and denies `clippy::undocumented_unsafe_blocks` so every block carries a `// SAFETY:` comment.

**Exception**: the dedicated crate described above, reviewed as such.

### rs-lib-error
scope: rust, severity: major, enforcement: review

A library crate that returns `Box<dyn Error>` or `anyhow::Error` gives callers nothing to match on. Define an error enum (with `thiserror`) whose variants are the discriminated codes, and keep `anyhow` for the binary at the top, where the only remaining job is context and an exit code.

**Exception**: a crate that is private to one binary and whose errors are only ever reported, never matched.

### rs-error-context
scope: rust, severity: minor, enforcement: review

Context belongs where a failure crosses a boundary: `.map_err(...)` into the crate's error type, or `.context("reading config file")` in the binary. Adding it at every call site buries the cause under repeated wrappers; adding it nowhere leaves `No such file or directory` with no path.

**Exception**: an internal helper whose caller already adds context one level up.
