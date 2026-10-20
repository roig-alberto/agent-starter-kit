---
name: animate
description: >-
  Build, review, audit and name web motion, find what should animate, and copy motion from a screen
  recording; Emil Kowalski and Apple craft inside. Use when animating something, adding motion or a transition,
  and on "opens too abruptly", "make it feel nicer/smoother", "feels janky/rough", "the animation feels
  off", "improve the animations", "audit the motion", "make this app feel better", "what could be
  animated here?", "make this feel more alive", "what's it called when…", "the bouncy thing when a
  popover opens", "the iOS rubber-band scroll", "polish this", "feels cheap", "make it feel premium",
  "component craft", "design-engineering review". Wins over frontend-interaction-patterns for how a sheet,
  drawer, dialog, toast or nav moves. NOT for React Native (no skill here covers it).
---

# animate - build one animation that passes review

This skill turns a request for motion into an implementation that would survive a strict
`review-animations` pass the first time. The bar is Emil Kowalski's animation philosophy. It
prevents two failures, and the first is worse: animating something that should not animate, and
animating the right thing with the wrong ingredients (`ease-in` on an entrance, `scale(0)`,
keyframes on a toast, a duration that makes a dropdown feel sluggish). It does not audit a codebase
(`improve-animations`), critique a diff (`review-animations`), hunt for places that could animate
(`find-animation-opportunities`), or build for React Native.

## Steps

Run them in order. Steps 1 and 2 gate everything, and producing zero lines of code is a valid
result. The full tables live in `references/build-sequence.md`.

1. **Gate on frequency.** An action seen 100+ times a day or started from the keyboard gets no
   animation, ever; tens of times a day gets near-imperceptible motion or nothing; occasional UI
   (modals, drawers, toasts) gets standard motion; rare or first-time moments hold the delight
   budget. Raycast has no open/close animation, which is correct for something opened hundreds of
   times a day. If the request fails, say so and offer an instant state change instead.
2. **Name the purpose in one word**: feedback, spatial consistency, state indication, preventing a
   jarring change, explanation (marketing and onboarding only), or delight (rare tier only). If you
   cannot name it, do not build it. Data the user is reading or acting on does not move for style.
3. **Pick the cheapest tool that works.** Walk down: CSS transition, CSS `@starting-style`, CSS
   animation, WAAPI (`element.animate()`), then Motion (`motion.dev`) for springs, layout, exit and
   gesture values. CSS runs off the main thread, while `requestAnimationFrame` animation drops
   frames when the page is busy. If the task needs a component (toast, drawer, command menu,
   dropdown), stop and invoke `pick-ui-library`, because hand-rolled ones lose focus management.
4. **Animate `transform` and `opacity` only.** They skip layout and paint; `clip-path` is the
   sanctioned fourth and `height` is tolerated only for accordions. Start entrances from
   `scale(0.9-0.97)` plus `opacity: 0`, set `transform-origin` to the trigger
   (`var(--transform-origin)` in Base UI; modals stay centered), and prefer percentages such as
   `translateY(100%)` over hardcoded pixels.
5. **Choose the easing and duration, or a spring.** Entering or exiting uses `ease-out`, moving on
   screen uses `ease-in-out`, hover and color use `ease`, constant motion uses `linear`. UI stays
   under 300ms. Use a spring for drag with momentum, interruptible gestures, or decorative mouse
   tracking: `{ type: "spring", duration: 0.5, bounce: 0.2 }`, bounce 0.1-0.3.
6. **Plan interruption and exit.** Use transitions, not keyframes, for anything a user can fire
   twice in a second, because transitions retarget while keyframes restart from zero. Exit the way
   it entered, and time it asymmetrically: slow where the user decides, fast where the system answers.
7. **Ship reduced motion and hover gating with it.** Reduced motion means fewer and gentler
   animations, not zero, and touch devices fire false hovers on tap.

## Rules

- **Never approximate a value.** Every curve, duration and spring comes from the tables; never
  invent `cubic-bezier(0.4, 0, 0.2, 1)` because it looks familiar.
- **Extend the codebase's tokens, do not fork them.** If `--ease-out` or a duration scale exists,
  use it, because a parallel system is a defect.
- **Use the strong curves, not the built-in ones.** Built-in CSS easings are too weak for
  deliberate motion. When a curve is missing, take one from [easing.dev](https://easing.dev/) or
  [easings.co](https://easings.co/) rather than hand-rolling it.

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* strong ease-out for UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* strong ease-in-out for on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);     /* iOS-like drawer curve (Ionic) */
```

- **Make the call yourself.** Never present motion options as a menu; state the reasoning in one
  line and write the code, because the user asked for an answer, not a survey.
- **Start from a recipe when one matches.** Button press, dropdown, tooltip, modal, drawer, toast,
  accordion, stagger, hold-to-confirm, tab indicator, scroll reveal and drag-to-dismiss already
  exist in `references/recipes.md`, so a blank file only reinvents them worse.

## Gotchas

Each of these is an automatic block in `review-animations`. Check them before you finish.

- A `transition: all` animates properties you never meant to; name the exact properties.
- A `transform: scale(0)` entrance looks like it came from nowhere; use `scale(0.95)` with `opacity: 0`.
- An `ease-in` on a UI element delays the moment the user watches; use `ease-out` or a strong curve.
- A built-in `ease-out` on a deliberate animation lacks punch; use `cubic-bezier(0.23, 1, 0.32, 1)`.
- Motion on a keyboard shortcut or a 100+/day action feels slow; remove it.
- A UI duration over 300ms with no reason feels sluggish; use 150-250ms.
- A `transform-origin: center` on a trigger-anchored popover scales from the wrong point; use
  `var(--transform-origin)` (modals are exempt).
- Keyframes on toasts, toggles or other rapidly triggered elements restart from zero; use CSS transitions.
- Animating `width`/`height`/`margin`/`padding`/`top`/`left` costs layout every frame; use
  `transform` and `opacity`.
- Motion `x`/`y`/`scale` props drop frames under load; use the full string,
  `animate={{ transform: "translateX(100px)" }}`.
- A child's transform driven from a CSS variable on the parent recalculates every child; set
  `transform` on the element directly.
- An ungated `:hover` motion fires on tap; wrap it in `@media (hover: hover) and (pointer: fine)`.
- A missing `prefers-reduced-motion` branch hurts motion-sensitive users; add a gentler variant,
  not zero (`useReducedMotion()` in JS).
- Everything entering at once reads as a flash; stagger by 30-80ms.

## Output

Write the code, then at most a few lines: the gate result (frequency tier and named purpose, plus
anything rejected and why), the ingredients (tool, properties, curve, duration or spring config,
one line each), and what to feel-check. When feel depends on something code cannot settle (a
crossfade, a spring's bounce, the opacity and height balance in an entering list), say so and
point at the check: play it at 2-5x duration or in the DevTools animation inspector, step it frame
by frame, test gestures on a real device, and look again the next day. When the honest answer is
"this shouldn't animate", give it; that answer is the reason this skill exists.

## References

- `references/build-sequence.md`: the seven steps with every table (frequency, tools, easing,
  duration, spring configs, reduced-motion code). Read it when a step needs an exact value.
- `references/recipes.md`: ready-to-build CSS and JS for the common components and gestures. Read
  it whenever the request matches one of them.
- `references/copy-motion-from-recording.md`: how to copy an animation frame by frame from an iPhone screen
  recording (the method used for the Linear work). Read it when the user sends a recording to match.

## The other animation guides inside this skill

The six skills below now live inside this one, each copied word for word into its own folder (its
`SKILL.md` is renamed `main.md`; its own `references/` paths are relative to that folder). Where the text
above names one of them, read its `main.md`.

- `references/review-animations/main.md`: review a diff or critique existing motion against the strict bar.
- `references/improve-animations/main.md`: audit a whole codebase's motion and write plans for other agents.
- `references/find-animation-opportunities/main.md`: find places that should animate, and reject the rest.
- `references/animation-vocabulary/main.md`: name an effect the user describes.
- `references/emil-design-eng/main.md`: Emil Kowalski's polish philosophy ("polish this", "feels cheap").
- `references/apple-design/main.md`: Apple's fluid, physical motion, materials and typography.
- `pick-ui-library` (named above) is now `references/library-list.md` in `frontend-interaction-patterns`.
- `references/ui-playbook/main.md`: the user's own motion playbook, moved word for word from Agent Factory
  (2026-10-16): the decision gate, the motion tokens and the whole motion catalogue, with the Linear iOS 26
  motion copied frame by frame (exact values and code). Reuse its recipes before inventing new ones. A motion
  fix in any app updates this file; the look and iPhone fixes stay in `~/projects/agent-factory/docs/UI-PLAYBOOK.md`.
