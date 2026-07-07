# Next.js monorepo starter

A pnpm workspace preset for a strict TypeScript monorepo, wired to the claude-kit conventions.

## What comes with it

- `GUIDELINES.md`: the "don't" checklist the `/review` skill enforces on a branch.
- `tsconfig.base.json`: strict base config (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`). Each package extends it.
- `.github/workflows/ci.yml`: typecheck, test, and build across the workspace on push and PR (skips markdown-only changes).
- `.gitignore`: sensible defaults for a Next.js + pnpm workspace.

## Use it

```bash
npx degit canotalois/claude-kit/stacks/node-web my-app
cd my-app
```

Then scaffold the workspace:

- `pnpm-workspace.yaml` listing `packages/*` and `apps/*`.
- A root `package.json` with `typecheck`, `test`, `build` scripts that fan out (`pnpm -r ...`).
- Per-package `tsconfig.json` files that `extends` `../../tsconfig.base.json`.

## Conventions

`GUIDELINES.md` is the source of truth. Run `/review` before a PR to check the branch against it, and `/ship` to typecheck, scan for AI-tells, commit, and push.
