---
name: prototype
description: >-
  Builds a throwaway prototype that answers one question before real code: several genuinely different
  versions of a UI piece behind a live picker, or a clickable single-file walkthrough of how a flow's states
  behave. Use when the user wants options or proof before choosing: "show me a few versions", "give me
  variants", "prototype this", "try different designs for the toast", "I can't picture it, show me", "does
  this flow make sense", "walk me through what happens when". NOT for a new visual direction for a whole app
  (use frontend-design) or for static wireframes as HTML files (use claude-design-craft).
---

# Prototype

A prototype is throwaway code that answers one question, and the question picks its shape. It prevents two
wastes: three tints of the same idea presented as options, and a flow that looked right on paper and only
feels wrong once real cases go through it, after it is built. It does not review existing UI (that is
`animate`), plan fixes for it (that is `animate`), or choose dependencies (that is
`frontend-interaction-patterns`).

## Pick the branch

- **"What should this look like?"**: several UI variants behind a picker (the steps below and
  `references/workflow.md`).
- **"Does this logic or flow behave right?"**: one self-contained HTML file with buttons that push a state model
  through its tricky cases and show the state after every click (`references/logic.md`). Good for a PM to drive
  on a phone before an agent builds the flow.

If the question is truly unclear and the user is away, pick by the code it sits next to (a page or component
means UI; a backend module or a flow means logic) and state that assumption at the top of the prototype.

## Rules for both

- **Throwaway from the start, and named so.** It lives on a branch `prototype/<slug>` and never deploys; its
  file or route name says "prototype".
- **One command or a double-click to run.** A route on the dev server, or one HTML file.
- **No persistence.** State lives in memory; a real database only when persistence is the question, and then a
  scratch one named so (see `testing`).
- **Show the state.** Every variant switch or button click renders what changed.
- **Hand the answer back.** Every prototype has a Copy button (the picker's, or one on the logic page) that copies
  the user's pick and any values they tweaked as a message to paste into the chat, so choosing on a phone needs no
  typing (`references/picker.md`, Behavior contract).
- **Capture the answer.** When it has answered its question, write the verdict and the question it settled in the
  plan or decision log, fold the validated decision into the real code, and leave the prototype on its branch.

## Rules for UI variants

- **Diverge for real.** Each variant must be a direction you could defend shipping on its own, because the
  user learns nothing by flipping between tints of one idea.
- **Keep the craft bar in every variant.** Each one meets Emil Kowalski's standards: `ease-out` on
  entrances (never `ease-in`), sub-300ms UI motion, correct `transform-origin`, `transform`/`opacity` only,
  and reduced motion handled. A sloppy variant teaches nothing about the direction it represents.
- **Never touch production code during exploration.** Everything lives on the prototype branch, and integration
  happens only for the variant the user picked, so a rejected direction leaves no trace.
- **Prefer the real page.** When the piece lives in an existing page, render the variants there behind a
  `?variant=` switch, keeping its data and layout; a bare route hides problems a populated page exposes. Use an
  isolated route such as `/prototypes/<slug>` only when no page could host it.
- **Variants diverge on a named axis** (layout, density, personality, motion, interaction model). You must
  be able to state each axis in a phrase before building. Sharing the project's tokens is not convergence,
  because variants should feel native to the product.
- **Every variant fully works.** Use real interactions, real motion, and realistic, product-shaped copy with
  plausible names and numbers. No lorem ipsum, no dead buttons, no "imagine this part".
- **The picker is chrome, not a contestant.** Copy its markup, styles, and behavior verbatim from
  `references/picker.md`; its look never adapts to the project, so it always reads as harness.

## Steps (UI variants)

1. **Scope.** Narrow the request to one component and restate the brief in one sentence: what it is, where
   it lives, and what it must do.
   Done when: the one-sentence brief is in the reply.
2. **Recon.** Map the stack, the tokens, the personality, and the render context. With no project, use a
   restrained default look (neutral grays, one accent, the system font stack).
   Done when: you can name the stack, the tokens file and the screen it renders on.
3. **Choose directions.** Default to 3 variants, at most 5. Give each a descriptive name ("Quiet",
   "Editorial") and an axis, and make sure no two share an axis position.
   Done when: every variant has a name and an axis, and no two share one.
4. **Build the harness.** On the host page behind `?variant=`, or an isolated route; without a project, a
   single self-contained HTML file. Render one variant at a time, full size, in realistic context, and switch
   instantly.
   Done when: the picker switches between every variant at full size.
5. **Verify and hand off.** Flip through every variant yourself with a clean console, then present the
   tradeoff table, say where the picker runs and which keys flip it, and stop: the choice is the user's.
   Done when: every variant renders with a clean console, and the table is in the reply.
6. **Promote on selection.** Integrate the picked variant following the project's conventions, then remove the
   prototype surface from the working branch; for another round, keep the harness and diverge around the
   chosen direction.
   Done when: the picked variant is in the real code and the prototype is only on its branch.

The artifact is a running picker (a URL or a file path) plus a table of variant, axis, when it wins, and
what it costs. Phase-by-phase detail and completion criteria are in `references/workflow.md`.

## Invocation variants

| Invocation | Behavior |
| --- | --- |
| `<description>` | Full workflow: scope, recon, 3 variants, picker, then wait for the choice |
| `<description> x5` | The same, with that many variants (capped at 5) |
| `riff <variant>` | A new round: keep the harness and generate a fresh set diverging around the named variant's direction |
| `keep <variant>` | Promote that variant into the codebase and delete the prototype surface |
| `keep <variant>, leave the picker` | Promote, but keep the prototype surface around |

## Gotchas

- **Two variants converged while you built them.** Cut one and say so, because a picker with two truly
  distinct directions beats one padded to three.
- **The user asks which variant you would choose.** Answer with a reason rooted in the product's
  personality and frequency of use, not aesthetics alone, and never pre-pick a favorite in the table.
- **The variant sits at the bottom center (a toast stack, a bottom sheet, a dock).** Set
  `data-position="top"` on the picker so it never covers the work.
- **Variants judged side by side as thumbnails.** Render one at a time at full size, because thumbnails
  distort spacing and scale.
- **The user reviews from a phone.** Send the logic prototype's HTML file as an attachment that renders, or put
  it in the inbox share; for UI variants, give the dev URL or screenshots of each variant.

## References

- `references/workflow.md`: the six UI phases in full, with completion criteria and the hand-off table. Read
  it at the start of every UI run.
- `references/picker.md`: the picker's exact markup, CSS, behavior contract, and reference wiring. Read it
  before building the harness and copy it verbatim.
- `references/logic.md`: the logic branch: the question first, a pure liftable module, the single-file page
  with free-play buttons and guided walkthroughs. Read it for every logic run.
- `references/history.md`: where each part came from.
