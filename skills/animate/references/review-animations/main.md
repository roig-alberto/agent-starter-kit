---
name: review-animations
description: >-
  Reviews animation and motion code against a high craft bar derived from Emil Kowalski's design
  engineering philosophy. Default to flagging; approval is earned. Use when reviewing a diff, PR
  or file that adds or changes transitions, keyframes, springs, gestures or other motion, or to
  critique existing motion. NOT for a codebase-wide audit with plans (improve-animations),
  building motion (animate), or non-motion code.
---

# review-animations - motion review where approval is earned

This skill reviews animation and motion code, and nothing else, against a strict craft bar. Its
bias is toward motion that feels right, not motion that merely runs: a transition that works but
feels sluggish, lands from the wrong origin, fires too often or drops frames is a regression, not
a pass. The bar comes from Emil Kowalski's animation philosophy (animations.dev); the method
(non-negotiable standards, escalation triggers, a remedial hierarchy, tiered output, explicit
approval criteria) is adapted from aggressive code-quality review. Asked to review general code,
decline and point to a general review skill.

## Rules: the ten non-negotiable standards

A violation of any of these is a finding. Exact values to cite live in `references/standards.md`.

1. **Justified motion.** Every animation answers "why does this animate?" (spatial consistency,
   state indication, feedback, explanation, preventing a jarring change); "it looks cool" on a
   frequently seen element is a block.
2. **Frequency-appropriate.** Keyboard-initiated and 100+/day actions get no animation; tens per
   day get reduced motion; occasional gets standard; rare or first-time can have delight.
3. **Responsive easing.** Entrances and exits use `ease-out` or a strong custom curve; `ease-in` on
   UI is a block because it delays the moment the user watches most.
4. **Sub-300ms UI.** Anything slower on a UI element needs a stated reason.
5. **Origin and physical correctness.** Popovers, dropdowns and tooltips scale from their trigger
   (`transform-origin`); nothing starts from `scale(0)` (use `scale(0.9-0.97)` plus opacity).
   Modals are exempt and stay centered.
6. **Interruptibility.** Toasts, toggles and drags retarget from the current state with CSS
   transitions or springs, because keyframes restart from zero.
7. **GPU-only properties.** Only `transform` and `opacity` animate; layout properties and Framer
   Motion `x`/`y`/`scale` shorthands under load are performance findings.
8. **Accessibility.** `prefers-reduced-motion` is honored (gentler, not zero) and hover motion is
   gated behind `@media (hover: hover) and (pointer: fine)`.
9. **Asymmetric enter and exit.** Deliberate actions (a press, a hold, a destructive confirm) are
   slower and system responses snap; symmetric timing there is a finding.
10. **Cohesion.** Motion matches the component's personality and the product; a jarring crossfade
    that a subtle blur would bridge is a finding. When unsure, deleting the motion is often strongest.

## Rules: how to fix

Prefer earlier moves over later ones, because the cheapest correct fix is usually removal.

1. Delete the animation (high-frequency, no purpose, keyboard-triggered).
2. Reduce it: shorter duration, smaller transform, fewer properties.
3. Fix the easing: swap `ease-in` for `ease-out` or a strong cubic-bezier.
4. Fix the origin: correct `transform-origin`; replace `scale(0)` with `scale(0.95)` plus opacity.
5. Make it interruptible: turn keyframes into transitions, or use a spring for gestures.
6. Move it to the GPU: layout properties become `transform`/`opacity`, a shorthand becomes the full
   `transform` string, and programmatic CSS uses WAAPI.
7. Make the timing asymmetric: slow the deliberate phase, snap the response.
8. Polish: blur to mask crossfades, stagger for groups, `@starting-style` for entry, a spring for
   elements that should feel alive.
9. Add accessibility and cohesion: reduced motion, hover gating, personality tuning.

## Gotchas: flag these on sight

- `transition: all` animates unintended properties off the GPU.
- `scale(0)`, or a pure-fade entrance with no initial transform, comes from nowhere.
- `ease-in` on any UI interaction, or weak built-in easing on a deliberate animation, feels sluggish.
- Motion on a keyboard shortcut, a command-palette toggle or a 100+/day action feels slow.
- A UI duration over 300ms with no stated reason feels sluggish.
- `transform-origin: center` on a trigger-anchored popover, dropdown or tooltip scales from nowhere.
- Keyframes on toasts, toggles or anything triggered rapidly restart from zero.
- Animated `width`/`height`/`margin`/`padding`/`top`/`left` costs layout every frame.
- Framer Motion `x`/`y`/`scale` props on motion that runs while the page is busy drop frames.
- A CSS variable updated on a parent to drive a child transform causes a style recalc storm.
- Movement with no `prefers-reduced-motion` handling, or ungated `:hover` motion.
- Symmetric enter and exit timing on a press-and-release or hold interaction.
- Everything entering at once where a 30-80ms stagger belongs.

## Output

Two parts, in order; `references/output-format.md` has the example table.

1. **Findings table (required).** One markdown table, `| Before | After | Why |`, one row per issue,
   never a "Before:/After:" list. Cite `file:line` and pull every value from
   `references/standards.md` rather than approximating.
2. **Verdict (required).** Remaining commentary grouped by tier, highest first, omitting empty
   tiers: feel-breaking regressions, missed simplifications, performance, interruptibility and
   timing, origin and cohesion, accessibility. Close with an explicit decision. **Block** on any
   feel-breaking regression, motion on a keyboard or high-frequency action, `scale(0)` or `ease-in`
   on UI, or a non-GPU animation with an easy GPU fix. **Approve** only with no feel-breaking
   regression, nothing that should be deleted, easing and durations in bounds, interruptibility
   handled where needed, and reduced motion respected.

When feel cannot be judged from code, recommend slow motion, frame-by-frame inspection and fresh
eyes the next day rather than guessing. Prefer CSS transitions, `@starting-style` and WAAPI for
predetermined motion, and JS or springs for dynamic, interruptible, gesture-driven motion.

## References

- `references/standards.md`: the precise values behind each standard (frequency table, easing
  curves, durations, springs, interruptibility, performance, clip-path, gestures, stagger,
  accessibility, debugging, cohesion). Read it whenever a finding needs a value or citation.
- `references/output-format.md`: the example findings table and the verdict tiers in full.
