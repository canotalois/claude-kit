---
name: review
description: Strict check of the current branch against the repo's GUIDELINES.md. Every forbidden pattern is a blocker. Outputs a short checklist. Invoke before a PR, or when the user says "review" or "check" the branch.
---

# review: strict guideline check

Output a short, strict checklist of blockers against `GUIDELINES.md`. Not an essay. A list a dev can act on in ten seconds.

## Steps

1. Read `GUIDELINES.md` from the repo root, plus `guidelines/core.md` if it exists (the universal spine the root file may build on). Together they are the source of truth. If no `GUIDELINES.md` exists, stop and say so.
2. Branch name: `git rev-parse --abbrev-ref HEAD`. Changed files: `git diff --name-only main...HEAD` (use `origin/main` if `main` is stale). On `main`, diff staged plus unstaged against HEAD.
3. Read each changed file in full, not just the patch. Context decides whether a `??` is a real default or a contract band-aid.
4. Every "Don't" line in `GUIDELINES.md` is a blocker. No tiers.
5. Output the checklist below. Nothing else.

## Output

If there are blockers:

```
FAIL: <N> blockers on <branch>

[ ] <path>:<line> | <one-line description> | <category>
[ ] <path>:<line> | <one-line description> | <category>

Categories: TS, Fallback, Errors, React, Network, Packages, UI, Tests, Hygiene.
```

If clean:

```
PASS: 0 blockers on <branch>
```

## Rules

- One line per violation, description under 80 chars. Quote the bad pattern when it makes the issue obvious.
- One blocker per location; the worst rule wins. Relative paths. Sort by path then line.
- Only "Don't" violations. Scope is the diff vs main, not pre-existing issues.
- Do not summarize the diff, suggest fixes inline, praise code, ask questions, or run tests, build, or typecheck.
