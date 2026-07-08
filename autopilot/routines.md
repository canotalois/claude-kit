# Scheduled cloud routines

Routines are Claude Code sessions that run on Anthropic's infrastructure on a schedule or a trigger (cron, an API call, a GitHub event), with no one at the keyboard. Create one with `/schedule` or at claude.ai/code/routines. Because no human is there to answer a prompt, a routine must be self-contained and should only do reversible work, or open a PR for a human to merge.

## Setup checklist

- **Prompt**: fully self-contained (the routine has no memory of your chats). State the repo, the goal, and the exact output.
- **Repository**: the routine clones it and works on a `claude/*` branch by default. Keep it to opening a PR, not pushing to `main`.
- **Trigger**: a cron schedule (daily, weekly), an API endpoint, or GitHub events (new PR, release) with filters.
- **Guardrails**: the balanced posture does not apply in the cloud (nobody to prompt), so scope the prompt tightly and never ask it to deploy or delete.

## Example: daily PR triage

Trigger: every weekday at 09:00. Prompt:

```
Review every open pull request in this repository that has changed since
yesterday.

For each one:
- Read the diff in full and check it against GUIDELINES.md and guidelines/core.md.
- Post a single review comment: a short blocker checklist (path:line | problem),
  or "LGTM" if clean.
- Do not approve, merge, close, or push anything. Comment only.

At the end, post one summary comment on the newest PR listing which PRs you
reviewed and how many blockers each had.
```

## Example: dependency freshness

Trigger: Monday 08:00. Prompt:

```
Check this repo's direct dependencies for outdated versions. For any minor or
patch update, open one PR on a claude/deps branch that bumps them and runs the
test suite. Do not bump majors; list those in the PR body for a human to decide.
Never touch the lockfile for a major version. One PR, reversible.
```
