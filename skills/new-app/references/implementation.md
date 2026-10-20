# Phase 4: implementation

Invoke the **plan** skill. Build the plan from the spec and design docs, with approval gates
between phases.

1. The recommended first phase is always the **scaffold** (project config, the theme wired from
   DESIGN_TOKENS.md, the schema and first migration, run and build), verified to build before any feature
   work.
2. **Then, before feature work, prove the load-bearing external dependency from Phase 1 end to end** (for
   example a real push notification landing on the target device). If the thing the whole model depends
   on does not work, that changes the plan, and it is cheapest to learn now.
3. Then implement feature by feature, verifying each one (typecheck, tests, run) and keeping AGENTS.md and
   the plan updated as decisions land. **After each feature is verified, tick it off in `FEATURES.md`**
   (mark it `[x]` with a one-line note) so the tracker always reflects reality.

## If wireframes were provided, they are the exact spec

Match them 1:1. The user invests significant time in wireframes, so treat every provided screen as the
authoritative target and reproduce it **pixel-close, exactly as drawn, unless the user explicitly says to
deviate.** Do **not** simplify, re-interpret, re-arrange, or add or remove elements. Do not approximate
from the prose README when the actual wireframe markup exists: **open the real wireframe source (for
example the design HTML or SVG) and read the exact layout, sizes, colors, and structure per screen**, then
build to that. When your build diverges from the wireframe, that is a defect to fix, not a judgment call.
Confirm the match visually (a screenshot review with the user) before considering a screen done.

## Reproduce the wireframes faithfully, not just structurally

This is repeatedly under-done. When translating a screen to code it is easy to nail the layout and logic
while quietly dropping the visual detail that actually carries the UX and UI quality. Before coding each
screen, study the wireframe specifically for these, and then verify your build against them:

- **shadows and elevation**, and **gradients** (including multi-stop and *stroke* gradients on charts and
  lines);
- **backgrounds and surface tints**, **blur and translucency**, and the exact **border radii**;
- **animations and transitions** (bottom-sheet slide-ins, hero or signature motion, hover and press
  states);
- **empty, loading, and error states**, and the exact **spacing rhythm**.

These come straight from the wireframe and DESIGN_TOKENS.md; skipping them makes the result feel flat and
"almost right." If a clean framework component and the wireframe's bespoke look diverge, keep the
wireframe's **intent** (color meaning, hierarchy, motion), even when you realize it with the framework
component. When in doubt, open the wireframe and compare side by side rather than approximating from
memory.

**Gate:** the scaffold builds and runs; subsequent phases proceed under the approvals of the plan skill.

## Wrap-up

When pausing or finishing a session, offer to run the **handoff** skill so the next agent can continue
cleanly. Keep the canonical docs current as the project evolves, because they are the contract. Confirm
**`FEATURES.md` is up to date** (everything shipped this session is ticked off, and any new scope added)
before wrapping; it is the project's authoritative "what's left" list.
