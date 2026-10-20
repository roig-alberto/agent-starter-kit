---
name: apple-design
description: >-
  Apple's approach to interface design and fluid, physical motion, translated for the web. Use
  when building or reviewing gesture-driven UI, spring animations, drag/swipe/sheet interactions,
  momentum and interruptible transitions, translucent materials and depth, typography (optical
  sizing, tracking, leading), reduced-motion, or the design foundations (feedback, spatial
  consistency, restraint) behind Apple-style interfaces. NOT for picking the sheet or gesture
  library (frontend-interaction-patterns) or building one specific animation (animate).
---

# apple-design - fluid, physical interfaces on the web

This skill carries Apple's design and motion guidance from the WWDC design talks, chiefly
*Designing Fluid Interfaces* (WWDC 2018), translated to CSS, Pointer Events,
`requestAnimationFrame` and spring libraries such as Motion. The through-line: **an interface
feels alive when motion starts from the current on-screen value, inherits the user's velocity,
projects momentum forward, and can be grabbed and reversed at any instant.** It prevents
interfaces that feel like a computer: lag on press, elements that jump when grabbed, animations
that must finish before input works, and hard walls at boundaries. Apple frames design as serving
four needs (safety and predictability, understanding, achievement, joy), and every rule serves one.

## Rules: motion and gestures

- **Respond on pointer-down, not on release.** Directness "falls off a cliff" the moment lag
  appears, so audit debounces, artificial timers and the ~300ms tap delay on the input path.
- **Keep feedback continuous during the interaction.** A drag, slider or drawer tracks the pointer
  1:1 the whole way, because animating only at the end feels dead.
- **Track 1:1 and respect the grab offset.** Use `setPointerCapture` and keep a short position and
  timestamp history, because snapping to the element's center on grab breaks the illusion and
  you need velocity at release.
- **Make every animation interruptible.** Never lock input during a transition and always start
  from the presentation (live on-screen) value, because starting from the target causes a jump.
- **Use springs for anything a user can touch.** New input only changes the target, so motion
  stays continuous; CSS transitions and `@keyframes` cannot be grabbed and reversed mid-flight.
- **Think in damping ratio and response.** Default to damping `1.0` (no overshoot); use ~`0.8`
  only when the gesture carried momentum, because overshoot on a faded-in menu feels wrong. Apple
  ships move `1.0`/`0.4`, rotation `0.8`/`0.4`, drawer `0.8`/`0.3`; in Motion that is roughly
  `{ type: 'spring', bounce: 0, duration: 0.4 }`.
- **Hand the release velocity to the spring.** The animation must continue at the finger's exact
  speed, which is the detail that most separates "fluid" from "fine".
- **Project momentum before choosing a snap point.** Use Apple's `project()` function
  (deceleration `0.998`) and snap to the target nearest the projected point, so a flick throws.
- **Decide reverse versus commit from the velocity sign at release, not the position**, because
  the direction the user was moving is their intent.
- **Enter and exit along the same path, anchored to the source.** Set `transform-origin` to the
  trigger and mirror the easing on reversible transitions, so the spatial story holds.
- **Rubber-band at edges.** Use the `rubberband()` resistance function, because a hard stop reads
  as frozen while rising resistance reads as "nothing more here".
- **Wait for intent, then track.** Use ~10px of hysteresis before committing to a direction,
  detect plausible gestures in parallel from the first move, and pay the double-tap delay only
  where double-tap exists.

## Rules: materials, feedback, type, foundations

- **Use translucent layers for chrome, weighted by hierarchy.** Heavier materials separate
  regions, lighter ones mark interactive elements, and bigger surfaces read thicker.
- **Dim to focus, separate to keep flow.** A modal task gets a scrim; a parallel panel gets
  translucency and offset without one.
- **Fire motion, sound and haptics on the same frame, on the causal event, and only where they
  earn it**, because lag between senses destroys the illusion and over-feedback gets ignored.
- **Honor three signals**: `prefers-reduced-motion` (cross-fades instead of slides and springs),
  `prefers-reduced-transparency` (solid surfaces) and `prefers-contrast: more` (solid with a border).
- **Make tracking and leading size-specific.** Large text gets negative tracking and tight leading,
  body stays near `0`, and spacing in `rem` lets the layout scale with the user's text size.
- **Reason with the eight principles**: purpose, agency, responsibility, familiarity, flexibility,
  simplicity (not minimalism), craft, delight. Delight is the result of the other seven.
- **Prototype interactively and design motion with the visuals**, because an interactive demo
  is worth "a million static designs" and motion is not a layer added afterwards.

## Gotchas

- A reversal looks like it hits a brick wall: one animation was replaced by another at the turn.
  Use a spring that re-targets from the current velocity.
- A diagonal drag desyncs: a single spring on the 2D distance. Use independent X and Y springs.
- A flick lands short or far: you used the textbook `v²/(2·decel)`. Use the exponential-decay
  `project()` form.
- Text over glass is unreadable: a light translucent surface sits on another one. Never stack
  them, and use heavier, higher-contrast text over translucency.
- A fixed toolbar or dock with `backdrop-filter` scrolls with the page in an iOS PWA (WebKit). On
  fixed bars use an opaque background (`frontend-interaction-patterns` ios-layout-traps; `ios-pwa-dock`
  for the dock).
- One `letter-spacing` for every size is wrong somewhere. Tighten headings (`-0.02em`), keep body
  near `0`.

## References

- `references/motion.md`: sections 1-11 (response, direct manipulation, interruptibility, springs
  and Apple's values, velocity handoff math, `project()`, spatial consistency, rubber-banding,
  gesture checklist, frame smoothness) and the quick-reference table.
- `references/materials-and-accessibility.md`: translucent materials and depth, the three rules
  of multimodal feedback, and the reduced-motion, reduced-transparency and contrast CSS.
- `references/typography.md`: tracking, leading, weight hierarchy, Dynamic Type and the system font.
- `references/foundations.md`: the eight principles in full, the tactical feedback, wayfinding
  and labelling rules, and the design process.
