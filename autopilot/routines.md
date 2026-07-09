# Scheduled cloud routines

A routine is a saved Claude Code config (a prompt, one or more repos, connectors) that runs on Anthropic's cloud, so it works with your laptop closed. There are no permission prompts during a run: what it can reach is set by the repos you pick, their branch-push setting, the environment's network access, and the connectors you include. It clones each repo from the default branch and works on `claude/`-prefixed branches; you review the run and open a PR from it.

Requires Pro / Max / Team / Enterprise with Claude Code on the web (research preview). Create one with `/schedule` in the CLI (scheduled triggers) or at claude.ai/code/routines (also for API and GitHub triggers).

## Triggers

- **Scheduled**: recurring (hourly minimum, or nightly/weekly) or a one-off at a set time.
- **API**: POST to the routine's `/fire` endpoint with a bearer token, with optional `text` context (an alert body, a failing log). For alerting and deploy pipelines.
- **GitHub**: on `pull_request` or `release` events, with filters (author, base/head branch, labels, draft, merged).

Because it runs unattended, the prompt must be self-contained and should only do reversible work or open a PR. Scope the environment and connectors to what it actually needs.

## Example: nightly backlog worker

Scheduled, every weeknight. Prompt:

```
Take the top unchecked item in BACKLOG.md. Implement it on a claude/ branch
with tests, run `pnpm -r typecheck && pnpm -r test`, and open a draft PR that
links the backlog item. If it is too ambiguous to build, open a draft PR with a
short "needs decision" note instead. One item per run, never touch main.
```

## Example: bespoke PR review

GitHub trigger on `pull_request.opened`, filter `is draft = false`. Prompt:

```
Review this pull request against GUIDELINES.md and guidelines/core.md. Leave
inline comments for real blockers (path:line | problem), and one summary comment.
Do not approve, merge, or push. Comment only.
```
