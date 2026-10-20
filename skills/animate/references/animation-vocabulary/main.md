---
name: animation-vocabulary
description: >-
  Reverse-lookup glossary that turns a vague description of a web animation or motion effect into
  its exact term ("the bouncy thing when a popover opens" is Pop in; "the iOS rubber-band scroll"
  is Rubber-banding). Use when the user asks "what's it called when…", or describes a motion
  effect without knowing its name and wants the right word to prompt an AI or designer with. For
  naming an effect only, NOT for designing or building one (use animate).
---

# animation-vocabulary - name the effect the user is describing

This skill turns a loose description of a motion effect into the precise term, so the user knows
what to ask an AI or a designer for. It prevents two failures: an invented name that nobody will
recognise, and an essay where the user wanted one word. The authoritative term list is
`references/glossary.md`; read it on every use, because the answer must quote it.

## Steps

1. **Read for intent, not keywords.** Users describe what they see or feel ("springy", "slides
   off", "draws itself in"), not the technical name, so map the sensation to a glossary entry.
2. **Quote the glossary entry verbatim.** Its descriptions are authoritative; paraphrasing them
   drifts the meaning the user will later prompt with.
3. **Answer in the fixed format.** Lead with the bold term and its glossary line:

   ```
   **Stagger** - Animate several items one after another with a small delay between each, creating a cascade.
   ```

4. **Add alternates only when several terms fit.** Put the best match first, then one or two
   alternates with a one-line note on how they differ, so the user can pick.
5. **Stop.** A naming question wants a name; expand only if the user asks.

## Rules

- **Disambiguate close terms explicitly.** Pairs such as *Clip-path* vs *Mask*, *Pop in* vs
  *Bounce*, and *Shared element transition* vs *Layout animation* are easy to confuse, so
  contrast them in the alternates.
- **Say plainly when the match is approximate.** Name the closest term, or describe the effect in
  the glossary's own words ("that's a *stagger* of *scale-in* entrances"), because a confident
  wrong name is worse than an honest near miss.
- **Stay within the glossary.** If a term is genuinely not there, say so rather than inventing
  one; you may still explain the concept using the glossary's words.

## Gotchas

- The user describes one image turning into another: that can be *Morph*, *Crossfade* or *Shared
  element transition*. Give *Morph* first and the other two as alternates, as in
  `references/examples.md`.
- The glossary mirrors the vendor project's `/vocabulary` page. If the two disagree, the glossary
  file in this skill is the one you quote, and the mismatch is worth reporting.

## References

- `references/glossary.md`: every term with its authoritative description, grouped by entrances
  and exits, sequencing, transforms, state transitions, scroll, feedback, easing, springs, looping,
  polish, performance and principles. Read it on every use.
- `references/examples.md`: three worked answers (feel-based, disambiguation, physics feel). Read
  it when unsure how much to write.
