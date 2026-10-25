# node-service

A TypeScript backend: HTTP API, worker, or job runner on Node 24. No framework imposed. Verified with TypeScript 6.0, ESLint 9.39, and typescript-eslint 8.72.

Source runs directly on Node through type stripping (`node src/index.ts`, `node --test`), so the tsconfig sets `erasableSyntaxOnly` (no enums, namespaces, or parameter properties) and `rewriteRelativeImportExtensions` (imports name the `.ts` file; the build rewrites them to `.js`).

## Files

| File | Role |
| --- | --- |
| `tsconfig.json` | strict, `NodeNext`, type-stripping compatible |
| `tsconfig.build.json` | the build, without test files |
| `eslint.config.mjs` | owns the `lint` rules of `typescript.md`: `strictTypeChecked`, exhaustive switches, exports-map imports, `node:test` calls exempt from the floating-promise rule |
| `package.json` | scripts and toolchain versions |
| `.github/workflows/ci.yml` | typecheck, lint, test, build on Node 24 |

## Commands

- Install: `pnpm install` (commit `pnpm-lock.yaml`)
- Run: `node src/index.ts`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Test: `pnpm test` (`node --test`, files named `*.test.ts`)
- Build: `pnpm build` (to `dist/`)

## Layout

- `src/`: source and colocated `*.test.ts` files
- one module reads the environment and builds a typed config at startup (`cfg-fail-fast`); everything else receives it

## Rules

`core`, `typescript`, `backend`

## Then

- Add the HTTP framework and database driver the service needs, and a request schema on every route (`api-route-schema`).
