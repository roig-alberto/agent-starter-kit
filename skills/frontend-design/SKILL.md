---
name: frontend-design
description: >-
  The in-house design method plus the user's taste library: distinctive visual direction (typography,
  palette, layout, copy, dark theme), the user's liked-UI reference images, and the fidelity rule for every
  design hand-off. Use WHENEVER designing a new visual surface, picking a visual direction, adding a dark
  theme, writing a DESIGN_BRIEF or DESIGN_TOKENS, assembling a design hand-off for the Claude Design Agent,
  or running the design step of `new-app`. Trigger on "make it look good", 'what look do I want',
  'design the UI', 'hand this to the design agent', 'pick a visual direction', 'wireframes for a hand-off',
  'reference apps'. NOT for making a phone app work on desktop (use `responsive-desktop-port`), NOT for
  drawing the frames as plain HTML files (use `claude-design-craft`).
license: Complete terms in LICENSE.txt
---

# frontend-design - the design method and the taste library

This skill has two parts. Part 1 is the in-house design method: approach each brief as the design lead at
a small studio known for giving every client an identity that could not be mistaken for anyone else's.
Part 2 is the taste library: screens the user flagged as "I like this", plus the standing fidelity rule for
every design hand-off. Together they prevent templated output (the same palette, type, and layout
regardless of subject), a visual direction re-litigated from zero on each project, and the theme bugs that
screenshot reviews miss.

## Steps (every design job)

1. **Offer the choice first on this machine.** Before designing a NEW visual surface in-house, if the user
   has not been asked this session, ASK (AskUserQuestion, **no default, present both equally**): hand the
   brief to the **Claude Design Agent** (external) or do it in-house here. The fork itself is defined in
   `one-shot` (existing app) and the design step of `new-app` (new app); skip the ask only when it was
   answered upstream. Done when: the user has picked external or in-house.
2. **Read the taste library before writing a DESIGN_BRIEF or choosing a visual direction.** Open the images
   in `references/ui-examples/`, read `references/ui-examples.md`, and factor the recurring aesthetic into
   the brief or `DESIGN_TOKENS.md`, because the examples are the user's actual taste signal. Done when: the
   brief names what it takes from the examples, or says why this project departs from them.
3. **External path: assemble the design hand-off bundle** (the `input-<feature>-<project>/` folder in the
   Samba inbox, shape in ENVIRONMENT.md). **Copy `references/ui-examples/*` into the bundle** and reference
   them in `PROMPT.md` as "reference UI the user likes - match this energy, not pixel-for-pixel." Paste the
   fidelity wording from part 2 into `PROMPT.md`. This step is what "remind me to give it to the design
   agent" means. Done when: the bundle folder lists the example images and `PROMPT.md` holds the fidelity
   paragraph.
4. **In-house path: run the part 1 method** below and deliver hi-fi static wireframes per part 2. Done
   when: part 1 step 5 is done.
5. **When the user drops new "I like this" screens** (usually via the Samba inbox), move them into
   `references/ui-examples/`, add a row to the table in `references/ui-examples.md` with a one-line concrete
   description (surface, accent, type, motif), and refresh the recurring-aesthetic paragraph if the taste
   signal shifts. Done when: every image in the folder has a row in the table.

## Part 1: the design method

### Rules

- **Ground the design in the subject.** If the brief does not pin down the product, name one concrete
  subject, its audience, and the page's single job, and state your choice, because distinctive choices
  come from the subject's own materials, instruments, artifacts, and vernacular.
- **Treat the hero as a thesis and typography as the personality.** Open with the most characteristic
  thing in the subject's world, and pair display and body faces deliberately, because a big number with a
  gradient accent and a default font pairing is the template answer.
- **Make structure encode information.** Numbering, eyebrows, dividers, and labels must say something true
  about the content; use numbered markers (01 / 02 / 03) only for a real sequence.
- **Avoid the three AI-default looks where the brief leaves the axis free:** a warm cream background (near
  #F4F1EA) with a high-contrast serif and a terracotta accent; a near-black background with one acid-green
  or vermilion accent; or a broadsheet layout with hairline rules, zero radius, and dense columns. The
  brief's own words always win, including when it asks for one of these.
- **Spend your boldness in one place.** Let one signature element be memorable and keep everything around
  it quiet, because scattered effects (including extra animation) read as AI-generated.
- **Build to a quality floor without announcing it:** responsive down to mobile, visible keyboard focus,
  and reduced motion respected.
- **Scope screen selectors to their own column and write component invariants as direct children**
  (`.tv-toggle > .tv-toggle-knob`), because a screen rule like `.notif-head span` outranks a one-class
  component rule and breaks the component from another file.
- **Audit a new dark theme with measurements, not screenshots.** Run AA contrast on every text and
  background token pair, a pixel scan for old-theme leftovers, and an "invisible elements" pass comparing
  each element's background against its CONTAINER's background, because eyeballing found nothing where
  the three audits found 28 bugs.

### Steps

1. **Brainstorm a compact token system** in your thinking: colour as 4-6 named hex values; type for 2+
   roles (a characterful display face used with restraint, a body face, a utility face if needed); a
   layout concept in one-sentence prose plus ASCII wireframes; and the single signature element. Done
   when: all four parts are written down.
2. **Critique the plan against the brief.** If any part reads like the default you would produce for any
   similar page, revise it and say what you changed and why. Done when: each part survived or was revised.
3. **Build, following the revised plan exactly**, deriving every colour and type decision from it. Watch
   selector specificity so section and element rules (`.section` vs `.cta`) do not cancel each other's
   padding and margins. Done when: no colour or face appears that the plan does not name.
4. **Write the copy deliberately.** Name things by what people control, use active voice ("Save changes",
   not "Submit"), keep an action's name through the flow ("Publish" produces "Published"), and make errors
   and empty states give direction. Done when: no placeholder or system-named label is left.
5. **Critique again with screenshots**, then remove one accessory. Done when: the screens are built and one
   line names the signature element and the risk taken.

## Part 2: the taste library and the hand-off rule

- **Fidelity: hi-fi STATIC wireframes, never an interactive prototype.** This is a standing user
  preference. Every request to a design agent, and every in-house design pass, must say this in the
  prompt, verbatim in substance:

  > Deliver **high-fidelity static wireframes**: fully styled frames with real type, real colour, real
  > spacing and real content - not greyboxes, not lorem ipsum. **One frame per screen state.** Do **NOT**
  > build an interactive or clickable prototype: no wired navigation, no working controls, no
  > hover/press behaviour, no live HTML app. State coverage beats clickability - if a state is only
  > reachable by clicking, it is a missing frame, not a missing interaction.

  Ask for each state in light and dark. The user reviews design as frames side by side, and a clickable
  prototype hides states behind interactions, so they go unreviewed and unbuilt.
- **Treat the examples as taste signal, not a pixel spec.** Copying them literally makes every app look
  the same.
- **Do not hard-lock a new app to this palette unless the user says so.** It is the default gravity,
  overridable per project (for example an app that must NOT look like the others).
- **Propose accents as a comparison board.** Offer 3 accent variants on the same screen with a one-line
  rationale each, because that is how the user picks.

## Red flags

- A design request or `PROMPT.md` without the fidelity paragraph. Agents build a clickable prototype.
- "The dark theme looks fine" from screenshots alone. Eyeballing found nothing where three audits found 28
  bugs.
- A screenshot diff that compares bytes or an old baseline. Both lied on closet.

## Gotchas

- **A switch knob or other component sits a couple of pixels off.** Look for a screen-level selector such
  as `.screen-thing span` matching inside it; fix the specificity, because geometric centring alone
  (`top:50%` + `translateY(-50%)`) does not win. Validate the guard by re-introducing the bug.
- **An element silently lost its background and border.** Grep for colour concatenations such as
  `background: color + '18'` with a `var()`, not just literals, because that is invalid CSS.
- **Dark theme shows a white panel with pale text in one corner of a feature.** Classify rules one by one
  instead of mapping a whole class prefix to one token, and include second-level overlays in capture runs,
  because a prefix like `.pcs-` can span two contexts.
- **"This screen is still dark" after raising theme tokens.** Measure the computed `backgroundColor` of its
  cards first; `rgba(0,0,0,0)` means the content sits directly on the canvas and needs a surface.
- **A screenshot diff reports a change where nothing changed, or no change where one exists.** Count
  pixels, not bytes; capture the baseline immediately before and after `git stash`; and wait for the
  splash with `state='detached'` with animations and caret disabled. Capture and diff mechanics live with
  `verify-ui-live`, which owns DOM measurement.
- **An accent close to green or red gets rejected.** Green (done) and red (destructive) are already spoken
  for, so check the semantic clash before proposing a colour.
- **A flat accent fill reads dead.** In this taste the accent always carries a soft halo or glow on the
  CTA, active chip, pill, and slider thumb.

## References

- `references/design-method.md`: part 1 in full (posture, design principles, two-pass process, restraint,
  copywriting). Read it at the start of any new visual direction.
- `references/ui-examples.md`: part 2, what each image shows, the recurring aesthetic, and the
  accent-system refinements. Read it before any brief or hand-off.
- `references/ui-examples/`: the liked-UI images themselves; copy them into every design hand-off bundle.
- `references/history.md`: the closet incidents behind the selector, dark-theme, and false-green rules, and
  why the fidelity rule exists. Read it when a rule seems excessive.
- `LICENSE.txt`: the license terms for the upstream design text.
