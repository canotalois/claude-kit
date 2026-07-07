# Rust stack starter

A Cargo workspace preset wired to the claude-kit conventions.

## What comes with it

- `GUIDELINES.md`: the Rust overlay on `guidelines/core.md`, the "don't" list `/review` enforces.
- `Cargo.toml`: a workspace root with shared `[workspace.lints]`, unsafe forbidden, clippy pedantic, `unwrap`/`expect` flagged. Each crate opts in with `[lints] workspace = true`.
- `.github/workflows/ci.yml`: `cargo fmt --check`, `clippy -D warnings`, and `cargo test` on push and PR (skips markdown-only changes).
- `.gitignore`: `target/` and the usual noise.

## Use it

```bash
npx degit canotalois/claude-kit/stacks/rust my-app
cd my-app
```

Then add crates under `crates/*`, each with `[lints]\nworkspace = true` in its `Cargo.toml`.

## Conventions

`GUIDELINES.md` plus `guidelines/core.md` are the source of truth. Run `/review` before a PR and `/ship` to check, commit, and push.
