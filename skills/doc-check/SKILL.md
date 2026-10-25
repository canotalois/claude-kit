---
name: doc-check
description: Audit every versioned Markdown file for AI-tells (em-dash, en-dash, middot, emoji), broken relative links, and repository paths cited in prose that do not exist. Report only. Invoke before delivering or publishing a repository's docs.
---

# doc-check

A delivery gate for documentation. Scripts decide, not eyeballing.

## Steps

1. List the docs: `git ls-files '*.md' '*.mdx'`.
2. AI-tells: `python3 scripts/check-ai-tells.py <files>` from this skill's directory. It prints `path:line: kind` for each hit.
3. Links: for every relative Markdown link `[text](target)` (skip `http`, `mailto:`, and pure `#anchor`), resolve the target against the file's directory, strip any `#anchor`, and check that it exists.
4. Cited paths: for every backticked token that looks like a repository path (contains `/` or ends in a known extension, no spaces, no `<placeholder>`), check that it exists from the repository root. Skip paths under `~`, absolute paths, and paths inside fenced code blocks that show commands for another repository.

## Output

```
doc-check: <N> files

AI-tells:
  <path>:<line> <kind>
Broken links:
  <path> -> <target>
Missing cited paths:
  <path>: `<cited>`

PASS
```

Print `PASS` only when all three sections are empty, and omit empty sections. Do not fix anything unless asked.
