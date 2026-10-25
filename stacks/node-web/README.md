# node-web

A pnpm monorepo for a React web app on Next.js (App Router), with shared packages. Verified with TypeScript 6.0, ESLint 9.39, typescript-eslint 8.72, and eslint-config-next 16.4.

TypeScript 7 is not used yet: its npm package ships no JavaScript API, and typescript-eslint's type-aware rules need one (it supports `typescript <6.1`). ESLint stays on 9 because the plugins `eslint-config-next` bundles do not declare ESLint 10.

## Files

| File | Role |
| --- | --- |
| `tsconfig.base.json` | strictness shared by everything: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax` |
| `tsconfig.app.json` | apps: bundler resolution, `noEmit`, DOM, the Next.js plugin |
| `tsconfig.lib.json` | publishable packages: `NodeNext` resolution and declaration emit, so consumers on any resolution mode can import them |
| `eslint.config.mjs` | owns every `lint` rule of the catalog: `strictTypeChecked`, Next core-web-vitals, React hooks and Compiler rules, jsx-a11y with design-system components mapped, exhaustive switches, router links, exports-map imports |
| `package.json`, `pnpm-workspace.yaml` | root scripts that fan out to the workspace |
| `.github/workflows/ci.yml` | typecheck, lint, test, build on Node 24 |

## Commands

- Install: `pnpm install` (commit `pnpm-lock.yaml`; CI installs with `--frozen-lockfile`)
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Test: `pnpm test`
- Build: `pnpm build`

## Layout

- `apps/<name>/`: Next.js apps, each with a `tsconfig.json` extending `../../tsconfig.app.json`
- `packages/<name>/`: shared packages, each extending `../../tsconfig.lib.json`, importable only through their `exports` map

## Rules

`core`, `typescript`, `react`, `next`

## Then

- Create the first app with `pnpm create next-app apps/web`, then point its `tsconfig.json` at `../../tsconfig.app.json` and delete the ESLint config it generates: the root one applies.
- Give every workspace package `typecheck`, `test`, and `build` scripts so the root commands reach it.
