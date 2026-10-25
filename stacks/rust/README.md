# rust

A Cargo workspace on edition 2024 with strictness declared once. The config is checked by this kit's own CI, which builds and lints a sample crate against it.

## Files

| File | Role |
| --- | --- |
| `Cargo.toml` | workspace root: resolver 3, edition 2024, `rust-version` 1.85, `[workspace.lints]` (unsafe forbidden, Clippy `all` denied and `pedantic` warned, `unwrap_used`, `#[expect]` with a reason required) |
| `clippy.toml` | `unwrap` allowed in tests |
| `.github/workflows/ci.yml` | `cargo fmt --check`, `cargo clippy -D warnings`, `cargo test` |

## Commands

- Format: `cargo fmt --all`
- Lint: `cargo clippy --workspace --all-targets -- -D warnings`
- Test: `cargo test --workspace`
- Build: `cargo build --workspace`

## Layout

- `crates/<name>/`: one crate per bounded concern; libraries return their own error enum, the binary uses `anyhow` at the top

## Rules

`core`, `rust`

## Then

- Create the first crate with `cargo new crates/<name>` and add to its `Cargo.toml`:

  ```toml
  [package]
  edition.workspace = true
  rust-version.workspace = true

  [lints]
  workspace = true
  ```
