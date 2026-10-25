# React rules

On top of `core.md` and `typescript.md`, for React on the web (React 19). Next.js specifics are in `next.md`. Examples use Tailwind and shadcn/ui where a class name or a component makes the point; the failure does not depend on them.

## Index

| ID | Severity | Enforcement | What |
| --- | --- | --- | --- |
| `lint-hook-rules` | critical | lint | hook called conditionally |
| `lint-hook-deps` | major | lint | effect dependency array wrong or suppressed |
| `lint-a11y-label` | minor | both | control with no accessible name |
| `lint-router-link` | minor | lint | internal navigation through a raw anchor |
| `react-render-side-effect` | critical | both | navigation or external mutation during render |
| `react-context-value` | minor | review | fresh provider value every render, without React Compiler |
| `perf-waterfall` | major | review | independent async work run in sequence |
| `perf-await-late` | minor | review | awaiting before a cheap guard |
| `perf-barrel-import` | minor | review | barrel import pulling a whole package |
| `perf-dynamic-heavy` | minor | review | heavy component in the initial bundle |
| `ux-destructive-close` | major | review | dialog closes and discards unsaved input |
| `ux-locale-format` | major | review | money or actionable time rendered without explicit locale and zone |
| `ux-error-surfaced` | minor | review | actionable server error never reaches the user |
| `ux-validation-timing` | minor | review | multi-field form validates only on submit |
| `ux-empty-state` | minor | review | list with no empty branch |
| `ux-autocomplete` | minor | review | auth or address input without an autofill token |
| `ux-dialog-shell` | minor | review | dialog height follows its content |
| `ux-dialog-responsive` | minor | review | dialog with a fixed width and no narrow fallback |
| `ux-flag-fallback` | minor | review | client flag boundary renders nothing while resolving |
| `arch-component-responsibility` | minor | review | fetch, state, and presentation in one client component |
| `pkg-react-peer` | major | review | `react` in a library's `dependencies` |
| `pkg-browser-in-shared` | major | review | top-level browser access in a shared package |

---

# Tooling owns these

### lint-hook-rules
scope: react, severity: critical, enforcement: lint

A hook behind a condition desynchronizes React's hook order and corrupts state across renders, with a symptom far from the cause.

Owner: `react-hooks/rules-of-hooks`.

**Exception**: none. `use()` is not a hook in this sense and may be called conditionally.

### lint-hook-deps
scope: react, severity: major, enforcement: lint

A missing dependency makes an effect read a stale value; an extra one re-runs it. To read the latest value of something without re-running the effect, move that read into a `useEffectEvent` (React 19.2) instead of dropping it from the array.

Owner: `react-hooks/exhaustive-deps`, part of `eslint-plugin-react-hooks` `recommended`, which also carries the React Compiler rules.

**Exception**: none. A suppression comment is the finding.

### lint-a11y-label
scope: react, severity: minor, enforcement: both

An icon-only button, an icon-only link, an input without a label: a screen reader announces "button" and a voice-control user cannot name it.

Owner: `eslint-plugin-jsx-a11y`. Two settings are required for it to see anything in a component-library codebase: `control-has-associated-label` is off in the `recommended` preset and must be enabled, and design-system components must be mapped (`settings['jsx-a11y'].components = { Button: 'button', Input: 'input' }`), since the plugin only knows DOM elements. The review half: the label matches the action, and changes when the action does (a sort control announces the column and the direction it will apply).

**Exception**: a decorative element with `aria-hidden="true"` next to a labelled control.

### lint-router-link
scope: react, severity: minor, enforcement: lint

Internal navigation through `<a href="/...">` triggers a full document load: the app reboots, client state empties, scroll position is lost.

Owner: a `no-restricted-syntax` entry on `JSXOpeningElement[name.name='a'] > JSXAttribute[name.name='href'][value.value=/^\//]`, shipped in the `node-web` ESLint config. Next's `no-html-link-for-pages` only resolves a `pages/` directory and does not cover the App Router.

**Exception**: a link that must leave the app (a download, a deliberate hard reload after sign-out to clear in-memory state). Both are decisions; the second deserves a comment.

---

# Rendering

### react-render-side-effect
scope: react, severity: critical, enforcement: both

Navigation, an external mutation, or another component's state update during render runs on every render pass, including discarded ones, and twice in development. The symptom is a redirect loop or a render that fights itself.

BAD:
```tsx
if (!user) router.replace('/login')
return <Dashboard user={user} />
```
GOOD: decide before rendering. In Next.js, redirect from a server layout with `redirect('/login')`, or in `proxy.ts`. In a client-only app, render a guard component that navigates from an event or an effect.

Owner: the React Compiler lint rules catch part of it; a call inside a plain `if` in the body is the review half.

**Exception**: updating the same component's own state during render, guarded by a comparison with the previous value. React documents this as the way to adjust state when a prop changes, and prefers it to an effect.

### react-context-value
scope: react, severity: minor, enforcement: review

Without React Compiler, a fresh object in `<Ctx value={{ user, signOut }}>` re-renders every consumer on every parent render. Memoize it: `const value = useMemo(() => ({ user, signOut }), [user, signOut])`.

**Exception**: React Compiler is enabled. It memoizes this already; add no manual memoization, and keep what exists, since removing it can change compiled output.

---

# Performance

Narrowed from Vercel Engineering's React guidance to what recurs in real diffs.

### perf-waterfall
scope: react, severity: major, enforcement: review

Two independent awaits in sequence cost the sum of both round trips. In a Server Component that is added to time to first byte.

BAD:
```ts
const customer = await getCustomer(id)
const invoices = await getInvoices(id)
```
GOOD: `const [customer, invoices] = await Promise.all([getCustomer(id), getInvoices(id)])`, or start both promises and pass them to children that read them with `use()` under `Suspense`, so each part streams when ready.

Follows Vercel `async-parallel`.

**Exception**: the second call needs the first one's result. That is a dependency, not a waterfall; say so in a comment if it looks independent.

### perf-await-late
scope: react, severity: minor, enforcement: review

When a branch needs a cheap synchronous condition and an awaited value, check the cheap one first, or the network call is paid on the path where it can never matter.

BAD: `const flag = await getFlag('beta'); if (flag && isBetaRoute(pathname)) { ... }`
GOOD: `if (isBetaRoute(pathname)) { const flag = await getFlag('beta'); if (flag) { ... } }`

Follows Vercel `async-cheap-condition-before-await`.

**Exception**: the condition is not cheap, depends on the awaited value, or the side effects must run in a fixed order.

### perf-barrel-import
scope: react, severity: minor, enforcement: review

Importing from a package root that re-exports everything pulls the whole barrel into the module graph, and tree shaking does not always remove it.

Follows Vercel `bundle-barrel-imports`.

**Exception**: the package is optimized by the bundler (in Next.js, listed in `optimizePackageImports` or in Next's default list, which covers libraries such as `lucide-react` and `date-fns`), or its `exports` map declares a small root on purpose.

### perf-dynamic-heavy
scope: react, severity: minor, enforcement: review

A chart library, a rich editor, or a map in the initial bundle costs every visitor who never opens it. Load it behind the interaction that needs it: `next/dynamic` in Next.js, `React.lazy` elsewhere. `ssr: false` is only allowed from a Client Component.

Follows Vercel `bundle-dynamic-imports`.

**Exception**: the component is above the fold on the page's main path. Deferring it trades bundle size for a visible pop-in.

---

# Interaction and perceived correctness

What the user experiences when they click. Nine rules. Three properties define this family; a candidate missing one does not belong:

1. The failure is visible to the user.
2. It is derivable from the code: the missing branch, prop, or binding is in the diff. Anything that needs a browser to confirm (measured layout shift, real focus order, contrast, perceived latency) is raised as a question or checked in a browser, never asserted from reading.
3. Catching it in review is meaningfully cheaper than after release.

**No `ux-` rule is ever `critical`.** Something genuinely critical is a correctness, security, or data rule with its own entry.

Five antipatterns are deliberately not diff findings, because they need frequency or product intent that a single diff does not show. The `ux-review` skill handles them in a whole-repository sweep:

| Left out | Why it is not a diff finding |
| --- | --- |
| tabs that unmount a form | fires on roughly one component per product |
| spinners where skeletons belong | a ratio over a codebase, meaningless on one diff |
| no optimistic update on a frequent mutation | "frequent" is a product fact, not readable from code |
| no autofocus on the first field of a modal form | polish whose argument is cumulative |
| no breadcrumbs on a deep route | navigation architecture, a product decision |

### ux-destructive-close
scope: react, severity: major, enforcement: review

A dialog, drawer, or sheet that closes on backdrop click or Escape while its form is dirty destroys what the user typed, with no undo.

BAD: `onOpenChange={(next) => { if (!next) resetForm() }}`
GOOD:
```tsx
onOpenChange={(next) => {
  if (!next && form.formState.isDirty) {
    setConfirmingClose(true)
    return
  }
  setOpen(next)
}}
```

**Exception**: nothing worth losing (one field retyped in two seconds), or a dialog that persists its draft. Say which.

### ux-locale-format
scope: react, severity: major, enforcement: review

Money, or a date or time the user acts on, rendered on the server without an explicit locale, currency, and time zone. `toFixed(2)` drops the currency; `toLocaleString()` with no argument in a Server Component or during SSR uses the server's locale and zone, shows the wrong value, and mismatches on hydration. A delivery slot in the wrong zone is a support ticket the user is right about.

GOOD: one `Intl.NumberFormat` and one `Intl.DateTimeFormat` per concern, with locale, currency, and `timeZone` passed explicitly, shared by every call site.

`minor` for a display-only timestamp such as "created at" in an internal list.

**Exception**: client-only formatting that intends the viewer's own locale and zone, and a value that is already a server-formatted string (then the finding, if any, is that two layers format).

### ux-error-surfaced
scope: react, severity: minor, enforcement: review

A failed mutation whose actionable cause never reaches the user. "Something went wrong" sends them to retry the same thing or to support. The code-level twin is `err-swallow`: this one loses the error to the user while the console has it.

BAD: `onError: () => toast.error('Something went wrong')`
GOOD: map the typed error's `code` to copy the user can act on, and fall back to a generic line only for codes with no mapping.

Raise to `major` when the cause is the user's only way forward: payment declined, quota reached, a conflict with someone else's edit.

**Exception**: an error whose message is not safe or useful to show (an internal failure, a 500). The generic copy is then correct, and the finding, if any, is that the real error is not logged with context. Never show a raw internal message.

### ux-validation-timing
scope: react, severity: minor, enforcement: review

A multi-field form that reveals what is wrong only after submit. The user fixes one field, submits, gets the next error, once per round trip. Surface the first error when a field loses focus, then clear it as they type. With react-hook-form that is `mode: 'onBlur'` (`reValidateMode` already defaults to `onChange`).

Raise to `major` on sign-up and login, where users abandon instead of persevering.

**Exception**: one-field forms such as a search box, validation only knowable on submit (uniqueness, payment authorization), and forms submitted through a React Action whose validation runs on the server.

### ux-empty-state
scope: react, severity: minor, enforcement: review

A list rendered from server data with no zero-length branch shows nothing at all, which the user reads as broken. Give it a line of explanation and, when a creation action exists, the button that fills it.

**Exception**: a list that cannot be empty by construction, a parent that already handles the empty case, and decorative repetition.

### ux-autocomplete
scope: react, severity: minor, enforcement: review

Auth and address inputs without `autoComplete` tokens. Password managers and browser autofill read them; without them the user types a password by hand, or the manager saves the wrong field.

| Input | `type` | `autoComplete` |
| --- | --- | --- |
| login identifier | `email` or `text` | `username` |
| login password | `password` | `current-password` |
| new password and its confirmation | `password` | `new-password` |
| one-time code | `text`, `inputMode="numeric"` | `one-time-code` |
| phone | `tel` | `tel` |
| street, single-line inputs | `text` | `address-line1`, `address-line2` |
| street, one textarea | | `street-address` |
| postal code | `text` | `postal-code` |
| card number, expiry, security code | `text`, `inputMode="numeric"` | `cc-number`, `cc-exp`, `cc-csc` |

**Exception**: a field that must not be filled from saved data, such as a search box or another person's details, takes an explicit `autoComplete="off"`, which is a decision rather than an omission (browsers may still ignore it on credential fields).

### ux-dialog-shell
scope: react, severity: minor, enforcement: review

A dialog whose height follows its content jumps every time the user switches a tab or opens an accordion inside it, and the control they were about to click moves. A `max-h` cap with scrolling on the content element does not fix it: below the cap, the height still follows the content.

GOOD, when the content varies: a fixed-height shell, header and footer fixed, the middle row scrolling.
```tsx
<DialogContent className="grid h-[min(85vh,640px)] grid-rows-[auto_1fr_auto] overflow-hidden">
  <DialogHeader />
  <div className="overflow-y-auto">{children}</div>
  <DialogFooter />
</DialogContent>
```
When the repository repeats the shape, the finding is to extract the shell once.

**Exception**: content that cannot change height while open, such as a confirmation with one sentence and two buttons.

### ux-dialog-responsive
scope: react, severity: minor, enforcement: review

A dialog with a fixed width or minimum width (`w-[720px]`, `min-w-[640px]`) and no narrow fallback overflows a phone, and the submit button becomes unreachable. A `max-w` cannot cause this; a fixed width can. Below the small breakpoint a bottom sheet is usually the better component.

**Exception**: an internal tool with a written desktop-only policy. Say where it is written.

### ux-flag-fallback
scope: react, severity: minor, enforcement: review

A client-evaluated feature-flag boundary that renders nothing while the flag resolves. The page paints, then a section appears or disappears under the user's eyes; on a call to action it reads as a broken button. Pass an explicit fallback per call site: the gated content's skeleton when it is likely on, nothing when it is likely off and the layout does not shift.

**Exception**: a flag evaluated on the server or bootstrapped into the first paint, so there is no unresolved window. Say where.

---

# Structure

### arch-component-responsibility
scope: react, severity: minor, enforcement: review

A client component whose body holds data fetching, state orchestration, and presentation at once. It cannot be tested without a network, reused with another source, or rendered in isolation. The finding is not size: it is that the presentation is not extractable because the JSX reads values that exist only because of the fetch and the state machine above it.

**Exception**: a page or route component whose job is to compose (fetch at the top, pass down), and an async Server Component that fetches through the data access layer and renders, which is the intended shape in an App Router codebase.

---

# Packages

### pkg-react-peer
scope: react, severity: major, enforcement: review

`react` in a library's `dependencies` lets the package manager install a second copy, and two Reacts in one tree fail at runtime with an error that does not mention the cause. Libraries declare `react` and `react-dom` in `peerDependencies`.

**Exception**: none for a library. An application correctly depends on `react`.

### pkg-browser-in-shared
scope: react, severity: major, enforcement: review

A shared package that touches `window`, `document`, or `localStorage` at module top level breaks when a Server Component or a native app imports it. Access inside a function that only runs in the browser is not this finding. Inject the capability (a storage port passed in), mark a browser-only module with `import 'client-only'`, or expose it through a `browser` export condition.

**Exception**: a file behind an explicit browser-only entry in the `exports` map, so importing it is the consumer's choice.
