---
name: doc-check
description: Scan every versioned markdown file for AI-tells (em-dash, middot, emojis) and broken internal links, and list docs not covered. Invoke before delivering a repo.
---

# doc-check

Audit the repository's markdown for delivery. Output a short report. Use a script, not eyeballing.

## Steps

1. List versioned markdown: `git ls-files '*.md' '*.mdx'`. Flag any you did not review this session.
2. For each file, check for AI-tells: em-dash (U+2014), en-dash (U+2013), middot (U+00B7), bullet (U+2022), pictographic emojis. Report file:line for each hit.
3. Resolve every relative markdown link (`](./...)`, `](../...)`); report any target that does not exist.
4. Report file paths cited in prose (`src/...`, `deploy/...`) that do not exist on disk.

## Output

```
doc-check: <N> markdown files

AI-tells:
  <path>:<line> <what>
Broken links:
  <path> -> <target>
Not covered:
  <path>

PASS if all three sections are empty.
```

Report only; do not fix anything unless asked.
