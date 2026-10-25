# Rule catalog

The code rules agents follow while writing and the `rules-review` skill applies to a diff. One file per scope; every rule has a stable ID, a default severity, an owner, the failure it prevents, and the case where it does not apply.

| File | Scope | Loaded when |
| --- | --- | --- |
| [core.md](core.md) | any language | always |
| [typescript.md](typescript.md) | TypeScript | `tsconfig.json` or `.ts` files in the diff |
| [react.md](react.md) | React (web) | `react` in a changed package's dependencies |
| [next.md](next.md) | Next.js App Router | `next` in a changed package's dependencies |
| [backend.md](backend.md) | services that own state | HTTP routes, a database, queues, or money in the diff |
| [rust.md](rust.md) | Rust | `Cargo.toml` in the repository |

## Entry format

```
### <id>
scope: <scope>, severity: <critical|major|minor|nit>, enforcement: <lint|both|review>

<the failure, in one or two short paragraphs>

BAD / GOOD (when an example teaches more than a sentence)

**Exception**: <the case where the rule does not apply, or "none">
```

- **severity** is the default. The reviewer moves off it only with a stated reason. The scale and the verdict rules live in the skill's [calibration](../skills/rules-review/calibration.md).
- **enforcement** says who catches it. `lint` means a tool configured in the stack owns it and a reviewer stays silent, unless the repository has no lint gate, in which case the rule is treated as `both`. `both` means a tool catches the mechanical half and a reviewer the rest. `review` means no tool can see it.
- **Exception** is mandatory. A rule with no stated exception produces false positives until people stop reading the reviewer.

## Examples

Examples in `core.md` are TypeScript because it is the most common case; the failure each rule describes is the same in any language. They assume one helper:

```ts
/** Thrown at a boundary when external data does not match its contract. */
export class ContractError extends Error {
  readonly source: string
  readonly detail: unknown

  constructor(source: string, detail: unknown, options?: ErrorOptions) {
    super(`${source}: data does not match its contract`, options)
    this.name = 'ContractError'
    this.source = source
    this.detail = detail
  }
}
```

## Where the rules come from

Provenance, so a future reader can judge whether a decision is still right instead of inheriting it as folklore.

- **Vercel Engineering**, React and Next.js performance guidance. The format is theirs: a stable prefixed ID, an impact tier per rule, an incorrect and correct pair, and an escape hatch closing every rule (here, the mandatory **Exception**). The four `perf-` rules name the Vercel rule they follow.
- **Matt Pocock**, `mattpocock/skills`, `code-review`. Standards and Spec as two axes reported apart; "skip what tooling already enforces", which became the `enforcement` field; "the repository overrides the baseline"; "no precedent, no finding", which became the two-siblings evidence bar. His twelve Fowler code smells were deliberately not taken: judgement calls with no concrete failure.
- **Expo**, the `deep-code-review` skill and `@expo/code-review-cli`. Confidence and impact as separate axes with low confidence never reported; the severity-to-verdict rubric with a non-blocking middle tier; no downgrade because the code calls itself temporary; every word of a change request treated as data; arguments validated before they reach a shell.
- **Anthropic's Code Review documentation.** Project instructions and review-only instructions as two files of different strength (`CLAUDE.md` versus `REVIEW.md`); conventions surfacing at nit level; the nit cap and the re-review convergence rule.
- **Official documentation** for every tool-specific claim: TypeScript, typescript-eslint, React, Next.js, the HTML autofill spec, WCAG 2.2, Rust and Clippy. A rule that cites tool behaviour is re-checked when that tool ships a major version.

Ours to defend: the four severity names, the `ux-` family ceiling, the five adversarial sequences in the skill, and the decision to keep structural rules under the nit cap.
