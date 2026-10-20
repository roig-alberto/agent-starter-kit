# research-decision history

## Vendor sites lie by omission (Enable Banking scan, 2026-07-20)

**Vendor sites lie by omission - hit the API before you believe the marketing page.** Two traps, both cost
real time on the Enable Banking scan (2026-07-20):

1. A JS-rendered vendor site returns an EMPTY SHELL to WebFetch, so "no results" may be a rendering
   artifact, not an answer. Use `chrome-devtools-axi` for anything behind client-side rendering.
2. A site's own filters can contradict its API. Their country filter lists banks by HOME country, so
   a neobank was absent under Spain (it is Lithuanian, passporting in), while `/aspsps?country=ES` returned
   it. When a product's API and its website disagree, **trust the API** and record which one you checked.

## Build-versus-buy with an unfixable upstream bug (2026-07-14)

Precedent and concrete recipe: `frontend-interaction-patterns`. Radix Select's scroll-lock broke an iOS
PWA, so the app hand-rolled a portalled dropdown (2026-07-14).

## 2026-10-16: official sources first (skills redo, light edits)

From addyosmani/agent-skills `source-driven-development` (MIT): the source hierarchy (official docs, changelog,
web standards, compatibility tables), what never counts as a primary source, the literal UNVERIFIED line, and
fetched pages treated as untrusted data.
