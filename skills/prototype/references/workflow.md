# Prototype workflow, phase by phase

The detail behind the steps in `SKILL.md`. Each phase ends with a completion criterion; do not move on
until it holds.

## Phase 1: Scope

One thing per run. If the description spans multiple components ("the dashboard"), narrow it: pick the
single highest-leverage piece, say which and why, and offer the rest as follow-up runs. Restate the brief
in one sentence: what the thing is, where it will live, and what it must do.

## Phase 2: Recon

Before designing anything, map the ground the variants must stand on:

- **Stack**: the framework, the styling system (Tailwind, CSS modules, vanilla), and the motion library if
  any.
- **Tokens**: colors, radii, spacing, fonts, and easing or duration variables. Variants use these, so every
  variant should look like it could ship in this product tomorrow.
- **Personality**: is it a playful consumer app or a crisp dashboard? This bounds how far the boldest
  variant may go.
- **Context**: where the piece renders, against what background, beside what neighbors, and at what sizes.

If there is no project (an empty directory, or the user is just exploring), skip to the standalone branch
in Phase 4 and choose a restrained default look: neutral grays, one accent, and the system font stack.

## Phase 3: Choose directions

Default to **3 variants**, and go up to 5 when the user asks or the design space is genuinely wide. More
than 5 dilutes the comparison.

Before writing any code, list the set with a name and an axis for each. Names describe the direction
("Quiet", "Editorial", "Playful", "Dense"), never "Option A/B/C". If two proposed directions would differ
only in accent color or copy, they are one direction; replace one with a real alternative (a different
layout, a different interaction model, a different motion story).

**Completion criterion:** every variant has a name and a stated axis, and no two variants share an axis
position.

## Phase 4: Build the picker harness

There are two branches, chosen by what exists:

- **In a project with a dev server**, build an isolated route or page (`/prototypes/<slug>`, or the
  framework's equivalent), with one file per variant plus a small harness file. Nothing imports from the
  prototype surface into production code.
- **With no project, or in a static context**, build a single self-contained HTML file (inline CSS and JS)
  that the user can open directly in a browser.

The picker's markup, styles, keyboard wiring, and placement come from `references/picker.md`, verbatim.
Load it now and build exactly that. Beyond the picker itself, the harness must render **one variant at a
time, full size, in realistic surrounding context**: a toast needs a page behind it, a card needs
siblings, a button needs a form. Side-by-side thumbnails distort spacing and scale, so never judge UI at
postage-stamp size. Switching is **instant**: flipping is an action done 100+ times a session, so by the
frequency rule the variant swap gets no animation.

## Phase 5: Verify and hand off

Run the harness. Confirm that every variant renders, every interaction responds, and the console is
clean. Flip through all of them yourself before showing the user. If browser tooling is available,
screenshot each variant.

Then present the set and **stop, because the choice belongs to the user**:

| # | Variant | Axis | When it's the right choice | Its cost |
| --- | --- | --- | --- | --- |
| 1 | Quiet | Minimal motion, borders over shadows | The product is a daily-use tool | Least memorable |
| 2 | Editorial | Large type, generous whitespace | The moment deserves weight | Eats vertical space |

Close with where the picker is running (a URL or a file path) and the keys to flip.

**Completion criterion:** every variant is reachable from the picker and behaves correctly, there are no
console errors, and the table names each variant's tradeoff honestly.

## Phase 6: Promote on selection

When the user picks, integrate that variant where it belongs, following the project's existing
conventions (file layout, naming, token usage), then delete the prototype surface (hard rule 5 in
`SKILL.md`). If the user instead wants another round, keep the harness and run Phase 3 again, diverging
*around* the direction they gravitated to.
