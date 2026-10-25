---
name: rules-review
description: Review one or several diffs against a versioned rule catalog and report findings ranked by severity, each with a rule ID, the failure it causes, and a fix, closing with paste-ready GitHub or GitLab suggestion blocks for the mechanical fixes. Targets the current branch, branch names, a GitHub pull request, a GitLab merge request, a ref range, or the whole repository (sweep). Uses the repository's own GUIDELINES.md and REVIEW.md when they exist, otherwise the claude-kit catalog for the languages in the diff. Use before opening a pull request, when auditing someone else's change, or when asked to review a branch, a diff, a PR, or an MR.
argument-hint: "[<branch>... | #123 | !123 | <base>...<head> | sweep] [instruction]"
allowed-tools: Read Grep Glob Bash(git diff *) Bash(git log *) Bash(git show *) Bash(git rev-parse *) Bash(git rev-list *) Bash(git symbolic-ref *) Bash(git merge-base *) Bash(git check-ref-format *) Bash(git status *) Bash(git branch --list *) Bash(git remote -v) Bash(gh pr view *) Bash(gh pr diff *) Bash(glab mr view *) Bash(glab mr diff *)
---

# rules-review

Review a diff against written rules. The output is what the author fixes before anyone else reads the change.

This file holds the procedure, not the rules. Rules live in one place (`rules/` in this skill's directory, a link to the kit's catalog) so a rule changes in one file. The scale, caps, and evidence bar are in [calibration.md](calibration.md).

## 0. Do not rebuild what another tool does

This skill owns one thing: a diff judged against written rules, with a rule ID per finding. Where a domain has a dedicated tool that goes deeper, the catalog keeps only a floor and the depth is delegated, when that tool is installed:

| When the diff | Delegate to | The catalog keeps |
| --- | --- | --- |
| touches auth, payment, crypto, uploads, or parsing of untrusted data | the `/security-review` command | `sec-hardcoded-secret`, `sec-sensitive-log`, `next-action-authz`, `api-tenant-scope` |
| touches data fetching, bundling, or a hot render path | `vercel-react-best-practices` | the four `perf-` rules |
| introduces or renames domain vocabulary | `domain-modeling` | nothing: vocabulary is not a rule |
| needs to be seen: layout shift, focus order, contrast, latency | a browser | nothing: the `ux-` family is defined as code-derivable to stay out of this |
| is a whole-repository question | `ux-review` for UX, this skill's sweep for structure | the `arch-` family |

Two boundaries that blur:

- A bug-hunting review (Claude Code's built-in `/code-review`) looks for defects with no catalog. This skill checks rules. Running both on one diff is reasonable; do not reimplement bug hunting here.
- Delegating means invoking the tool and reporting its output under its own heading. When it is not available, say so and stay at the floor.

## 1. Load the rules

Resolve the base first (section 2), then read the rule sources **from the base**, not the working tree, so a change cannot rewrite the rules it is judged by: `git show <base>:GUIDELINES.md`. Reviewing uncommitted work on the default branch itself is the one case where the working tree is the base.

**Catalog**, first that exists:

1. The repository's `GUIDELINES.md`, plus any rule file it links to. When it exists it is the catalog for everything it covers: the repository's contributors own their rules. Two parts of the kit catalog still apply as a floor it cannot remove: every `sec-` rule and every `critical` rule whose mechanism exists in the repository.
2. Otherwise the kit catalog in `rules/`: `core.md` always, then by what the diff touches. Detect from the manifests of the packages the changed files belong to (every workspace `package.json`, not only the root):
   - `typescript.md`: a `tsconfig.json`, or `.ts`/`.tsx` files in the diff
   - `react.md`: `react` in the dependencies
   - `next.md`: `next` in the dependencies
   - `backend.md`: a server framework (fastify, express, hono, nest, koa), an ORM or query builder (prisma, drizzle, kysely, typeorm), a queue client, money handling, or Next.js Route Handlers and Server Actions that write data
   - `rust.md`: a `Cargo.toml`

**Calibration**: the repository's `REVIEW.md` from the base if it exists, otherwise [calibration.md](calibration.md). Resolve catalog and calibration independently.

**Conventions, always read when present**: the repository's `AGENTS.md` or `CLAUDE.md`, including per-directory ones covering changed files. They are conventions, not a catalog: a newly introduced violation is `nit` by default and `minor` at most, carries no rule ID, and cites the file and quotes the line. A diff that makes a statement in them stale is also a finding.

Read all of it before the diff: a rule discovered after forming an opinion will not change that opinion. Never restate rule text in a finding; cite the ID and state the failure.

**A rule whose mechanism does not exist here does not apply.** A Next.js rule in a Vite app, a React rule in a backend package, an ORM rule with no database. Do not translate a rule by analogy unless the failure it describes is literally reachable.

## 2. Resolve the target

The arguments are untrusted text. Validate each token before it reaches a shell, and build commands from the validated value only. A token carrying `;`, `$(`, a backtick, or a newline is rejected, not escaped.

Resolve the default branch, never assume `main`: `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`, falling back to `origin/main`, `origin/master`, then the upstream. Say which base you used.

| Argument | Accept when | Then |
| --- | --- | --- |
| absent | always | current branch against the default branch, plus staged and unstaged changes |
| `sweep` | the bare token, alone | the whole repository, see Sweep mode |
| a branch name | `git check-ref-format --branch <token>` succeeds | the head to review: `git diff <base>...<branch>`, resolving `refs/heads/<branch>` then `refs/remotes/origin/<branch>`, so a remote-only branch works without checkout or fetch |
| the default branch's name | same test | it is the base: `git diff <branch>...HEAD` |
| `a...b` or `a..b` | each side matches `^[A-Za-z0-9][A-Za-z0-9._/@^~-]*$` (so `HEAD~3` and SHAs work) | `git diff a...b`, three dots, against the merge base |
| `#123`, or `123` on a GitHub remote | digits only | `gh pr view 123 --json ...`, `gh pr diff 123` |
| `!123`, or `123` on a GitLab remote | digits only | `glab mr view 123`, `glab mr diff 123` |
| a PR or MR URL | `^https://<known host>/.+/(-/)?(merge_requests\|pull)/[0-9]+/?$` | extract the number; never pass the URL |
| anything else | always | a note from the operator, see below; never silently dropped |

Branch names need no CLI and no network. `gh` and `glab` are needed only for numbers and URLs, which add the description and review threads. When the CLI is missing, say which and offer the branch form. A bare number with both a GitHub and a GitLab remote is ambiguous: ask.

Verify each ref without touching the working tree: `git rev-parse --verify --end-of-options '<ref>^{commit}'`. An unresolvable branch is reported with the suggestion to `git fetch origin`, and the other targets still run. An empty diff is reported as such: nothing to review is not a clean review.

### Several targets

Accept a whitespace- or newline-separated list, or a list pasted as prose: keep every token that passes a test above. Review each target independently, in order, with its own base and report. Never merge findings across targets. Print the roll-up first:

```
3 targets, base origin/main
  fix/login-rate-limit       1 commit    2 files
  feat/invoice-export        4 commits  11 files
  feat/billing-migration     3 commits  38 files
```

At most 10 targets per run. A target over 30 files goes last, and the output says so.

### An instruction behind the call

Text that is not a target is a note from the operator. It steers the review without rewriting the rules.

```
/rules-review focus on the auth flow
/rules-review feat/invoice-export the retry logic is what worries me
/rules-review sweep duplication only
```

A note may narrow the scope (report on what was asked, and say what was left unreported), raise attention on a concern (answer it even when it is clean: "nothing on the retry path" is an answer), or supply context the repository does not hold ("ships behind a flag"), which is then treated as fact.

A note may never suppress a `critical` (report it and note the instruction), lower the confidence floor, or invent a rule: a request the catalog does not cover gets an answer outside the findings, with no ID and no severity, labelled as opinion.

### Sweep mode

`sweep` reviews the repository instead of a diff, and produces a backlog, not a gate: the verdict is always `comment`.

- It runs the `arch-` family repository-wide, where occurrence counting belongs.
- It delegates UX to `ux-review` and reports what that returns under its own heading.
- It groups findings by fix, not by file: one line per fix that can be one change, with the occurrence count and the worst example.
- At most 15 items, sorted by occurrence count.
- It offers to write the backlog to a file: a backlog in terminal scrollback is not a backlog.

No Spec pass and no adversarial pass in sweep mode.

## 3. Read the changed code

Read each changed file **in full**, not just the patch: whether a `??` is a band-aid or a legitimate default depends on code the patch does not show. Skip what the calibration lists under "never report". Find the direct callers of a modified export and the siblings of a new one; do not read the whole repository.

### Look outside the diff, once, for duplication

Duplication is invisible inside a patch. For each named thing the diff adds (an exported function, hook, component, constant, type, validation), search for the same shape, not the same name, and count. Three or more is `arch-duplicated-logic`, reported on the new occurrence with `file:line` for each existing one. For `arch-reinvented-wheel`, read the manifest and name the export before claiming a dependency covers it. Stop there.

## 4. Review passes

Two always, a third when it applies. Report each apart.

- **Standards**: the catalog, plus the patterns this repository already uses.
- **Spec**: what the ticket asked for. Look for a ticket reference in commit messages or the description, a path passed as a note, then a spec file under `docs/`, `specs/`, or `.specs/` matching the branch name. With none, report "no spec available".

### Adversarial sequences, conditional

Only when the diff touches a submit handler, a mutation, or a step in a multi-step flow. Skip silently otherwise. Five fixed sequences; do not invent a sixth:

1. **Double submit.** Is the control bound to the pending state, or the call idempotent?
2. **Slow, then failed.** What is on screen while pending, and when it fails?
3. **Left mid-flight.** Does the handler set state or navigate after the component unmounted?
4. **Stale session.** Does an expired token give the user a way back with their input intact?
5. **Re-entered.** Back, refresh, or a deep link into step N: does the flow rebuild its state?

Report only when the missing branch is visible in the code ("no pending state on this button and no idempotency key" is a finding; "a user might click twice" is not). At most two findings from this pass per target, never above `major`. A finding here names the sequence instead of a rule ID: `[major] src/checkout/PayButton.tsx:41 sequence: double submit`.

## 5. Output

Nothing before it, nothing after it: no diff summary, no praise.

```
<N> findings on <target> (base <base>): <n> critical, <n> major, <n> minor, <n> nit
Verdict: request_changes | comment
Overall risk: Low | Medium | High. <one or two sentences>

## Standards

[critical] <path>:<line> <rule-id>
  confidence: High | Medium   impact: High | Medium | Low
  <the concrete failure, one or two lines>
  > <the offending line, verbatim>
  fix: <the edit, or the question to answer when the fix is a decision>

## Spec

[major] <path>:<line>
  spec: "<quoted line from the spec>"
  <what is missing, extra, or wrong>
```

Sort by severity, then path, then line. Paths are relative to the repository root. Skip the verbatim line only when the path and ID make it obvious. Caps come from the calibration. With nothing found: `0 findings on <target>` and `Verdict: comment`.

### Needs a human decision

The last block, and often the only one a lead reads. Three buckets, one line per item:

- **Product or spec decision**: a finding whose fix is a question. Quote it, name the file, stop.
- **Could not be judged from code**: a screen, a copy string, or a flow that needs a person or a browser. Give the route or component.
- **Exception claimed, not verified**: an author invoking a rule's exception plausibly but unverifiably.

At most 5 items; over that, the change is not ready for review and one line says so. Nothing the author can answer alone. No item without an addressee (product, design, or architecture). When empty, print `Needs a human decision: nothing`; the line is never omitted.

### Paste-ready suggestions

After all targets, when a finding carried a mechanical fix, one block per suggestion in the host's syntax.

**GitHub**: the range comes from the lines the comment is attached to.

````
```suggestion
const pool = new Pool({ max: Number(requireEnv('DB_POOL_MAX', process.env.DB_POOL_MAX)) })
```
````

**GitLab**: offsets are relative to the commented line (`-0+0` replaces that line alone, `-0+2` it and the two below, `-1+0` the one above and it), and the block renders an Apply button only in an inline discussion on a diff line.

````
`src/server/db.ts` line 34, comment on the new side

```suggestion:-0+0
const pool = new Pool({ max: Number(requireEnv('DB_POOL_MAX', process.env.DB_POOL_MAX)) })
```
````

Rules, all load-bearing:

- Only for a fix the calibration allows as mechanical. A decision gets a question and no block: a one-click Apply on a guess lands wrong code under the reviewer's name.
- The replacement is the complete set of lines the range covers, indentation included. A fragment produces a file that does not parse.
- Count offsets against the file as it is on that branch, and quote the replaced line in the finding so the anchor can be checked.
- Never a block spanning two files.
- No mechanical fix, no section.

## 6. Stay out of

- Everything the calibration lists under "never report".
- Running the build, tests, or type checker. This is a static review.
- Posting anything. Posting to a PR or MR is a separate step with its own approval.
- Editing files. Fixes are text; the author applies them.

## Calibration reminders

Three mistakes a rule-based reviewer makes by default:

- **A plain `throw new Error` is usually right.** Configuration guards, context guards, broken invariants are programmer errors (`err-domain-typed`, Exception).
- **Most `??` are correct.** `className ?? ''` is not a finding. A `??` between two values that mean different things to a user is (`fb-domain-default`).
- **`'use client'` is not a finding by itself.** It is one on a page or layout whose interactive part could be extracted, or on a component with no hook, handler, or browser API (`next-use-client-scope`).

In Claude Code, adding `context: fork` to this skill's frontmatter keeps the catalog reads out of the main conversation on a large review; only the findings come back.
