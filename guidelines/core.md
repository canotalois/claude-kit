# Core guidelines (language-agnostic)

The universal spine. Every stack's `GUIDELINES.md` starts from this and adds its own idioms. Each "Don't" is a blocker: if you catch yourself doing it, stop and reconsider before committing.

When in doubt: throw early, validate at the boundary, trust the layer below. No defensive code for cases the layer below promised not to produce.

## Contracts and boundaries

- Don't accept several response shapes "just in case". The contract is the contract.
- Do validate external data (network, files, env, user input) at the boundary, map it once into your own types, then trust it downstream.
- Do fail at startup for a missing required config value. No silent fallback to an empty value.

## Nullish and fallbacks

- Don't invent a default for a value that should be a real decision. Make the decision, or throw.
- Don't use a fallback to paper over an undecided contract (reading two possible field names and hoping). Pick one, reject the other.
- Don't stack fallbacks across layers. Once you trust the source, the second guard downstream is dead code.
- Do prefer throwing over a silent default when the value is required to work.

## Errors

- Don't raise a bare generic error for a domain failure. Use a typed error with a discriminated code the caller can switch on.
- Don't swallow an error (empty catch, discarded result). Log at least; classify if you can.
- Do parse and classify error responses at the boundary, not at each call site.

## Comments

- Don't write narrative comments in the middle of a function (a line that just says what the next line does). Explicit naming and small functions carry the intent.
- Don't write a comment that paraphrases the line below it.
- Do put an explanation above a function, type, or constant (doc-comment) when the *why* is not obvious.
- Do keep an inline comment only for a genuine gotcha: a platform quirk, a library workaround, a non-local invariant. Default to zero.

## Don't reinvent

- Don't hand-roll what the standard library or platform already gives you.
- Don't hand-roll what an already-installed dependency already does well.
- Do reach for a custom helper only when nothing existing fits, and centralize it in one place.

## Tests

- Don't test only the happy path. Cover the subtle behavior and the edge cases.
- Don't assert against your own mocks of an unspecified contract. Match the real contract.
- Do write one test per behavior, named for the behavior it checks.

## Commits and hygiene

- Don't ship a huge diff in two commits. Atomic commits, one logical change each.
- Don't bypass the pre-commit or signing hooks.
- Do write a change description with scope and a test plan.
- No emojis, em-dashes, or middots in code, docs, or commit messages.
