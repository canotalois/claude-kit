---
name: ux-review
description: Sweep a React web codebase for UX antipatterns and produce a prioritized backlog with file:line, a catalog rule ID where one exists, and a concrete fix each. Use when asked to audit or review UX, when a screen "feels broken" or "feels buggy", when users report bugs that are really UX defects (a modal that resizes, errors that appear only on submit, a lost form), or at the start of a new dashboard to set the patterns early. Not for a single diff: rules-review covers that.
---

# ux-review

A whole-repository UX sweep. It produces a backlog a human prioritizes, not a gate. The diff-level rules live in the kit catalog (`rules/react.md`, the `ux-` family); this skill finds them across the codebase and adds the antipatterns that only make sense at repository scale.

## Method

1. **Detect the stack** from the manifests: router, form library, data-fetching library, component library. A check whose mechanism is absent does not apply.
2. **Search by signature**, not by reading every file. Each check below gives the signature to grep for. Aim for recall on `major` checks; accept misses on `nit`.
3. **Confirm each hit** by reading the surrounding component. Report only what the code establishes (confidence `High` or `Medium`, as in the `rules-review` calibration). What needs a browser to confirm (measured layout shift, focus order, contrast) goes to "Verify in a browser", never asserted.
4. **Group by fix**: one backlog item per change that fixes every occurrence, with the count and the worst example. Twelve dialogs with the same shell problem are one item.
5. **Order the backlog** by impact, then by how many occurrences one change fixes. Separate sweepable fixes (one pattern, many files, one PR) from one-off refactors.

## Checks with a catalog rule

Severity, exception, and fix are the catalog's; the signature is how to find them at scale.

| Rule | Signature |
| --- | --- |
| `ux-dialog-shell` | dialog content elements with `max-h-[..vh]` plus `overflow-y-auto` and tabs, accordions, or steps inside |
| `ux-dialog-responsive` | dialog content with a fixed `w-[...]` or `min-w-[...]` and no narrow-breakpoint fallback |
| `ux-destructive-close` | `onOpenChange` handlers that reset or close without checking form dirtiness |
| `ux-validation-timing` | `useForm({` on multi-field forms with no `mode` (react-hook-form defaults to `onSubmit`) |
| `ux-autocomplete` | `type="password"`, `type="email"`, and address inputs with no `autoComplete` |
| `ux-error-surfaced` | mutation `onError` handlers that show a fixed string and never read the error's code |
| `ux-empty-state` | `.map(` over fetched data with no zero-length branch above it |
| `ux-locale-format` | `.toFixed(` on money, `toLocaleString()` or `toLocaleDateString()` with no locale, in server-rendered code |
| `ux-flag-fallback` | client flag hooks or boundaries rendering `null` while the flag resolves |
| `lint-a11y-label` | icon-only `<Button size="icon">` or `<button>` whose only child is an icon, with no `aria-label` |
| `lint-router-link` | `<a href="/` for internal routes |

When one of these turns up across many files and the repository has no lint gate for it, the backlog item is the lint rule, not the occurrences.

## Checks that only exist at repository scale

No catalog rule: these need frequency or product intent a single diff cannot show. Severity here is `minor` at most.

| Check | Signature | Fix | Severity |
| --- | --- | --- | --- |
| spinners where the shape is known | spinner component count against skeleton count; a spinner in place of a table, card grid, or form | a skeleton that matches the final layout; keep spinners for in-button and unknown-shape waits | minor |
| no optimistic update on a frequent mutation | toggles, favorites, mark-as-read with no optimistic path | TanStack Query: `onMutate` (cancel queries, snapshot, `setQueryData`, return the snapshot), roll back in `onError`, invalidate in `onSettled`; or React's `useOptimistic` | minor |
| form inside an unmounted tab | `TabsContent` without `forceMount` containing a form | `forceMount` plus hiding the inactive panel, when the form must exist before the tab is opened; verify the password-manager behavior in a browser | minor |
| no autofocus on a modal form | dialog containing a form whose first field has no `autoFocus` | `autoFocus` on the first field | nit |
| no breadcrumbs on deep routes | routes three or more segments deep whose layout renders none | breadcrumbs in the shared layout, built from the route segments | nit |

## Output

```
ux-review: <N> backlog items (<n> major, <n> minor, <n> nit), stack: <router>, <forms>, <data>, <components>

1. [major] ux-dialog-shell, 12 occurrences, worst: src/billing/EditPlanDialog.tsx:48
   <the failure the user sees, one line>
   fix: <the change, once, for all occurrences>

...

Verify in a browser:
  <route or component>: <what to look at>

Start with: <the three items that remove the most user-visible defects per change>
```

Cap the report at 25 items. Offer to write the backlog to `UX_AUDIT.md` and the durable patterns to `UX_GUIDELINES.md`; write them only when the user confirms.

## Stay out of

- Fixing anything. The job is to see; the user prioritizes and splits the work.
- Backend, tooling, CI, and migrations.
- A single requested change ("make this button red"): do it, do not audit.
