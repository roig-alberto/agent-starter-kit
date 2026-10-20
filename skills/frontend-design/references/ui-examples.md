# The liked-UI examples, described (part 2 of `frontend-design`)

What each image in `references/ui-examples/` shows, so a model briefing a design agent gets the signal
without opening every image. Treat them as taste signal, not as a spec to copy pixel for pixel.

| File | What it shows |
|---|---|
| `ui-examples1.png` | Dark **near-black neutral** surfaces + **fluorescent/neon accent** rings (azure, violet, magenta, aqua, tangerine), bold hero numbers, glowing center-FAB nav, flame-emoji streak, clean rounded cards. A palette-exploration board. |
| `ui-examples2.png` | Same near-black neutral base, glowing progress ring, bold hero number, glowing center-FAB, minimal card chrome - violet/emerald/mint variants. |
| `ui-examples3.png` | Accent-candidate board for the closet packing flow (same screen × 3 accents): coral fuego, amarillo cromo, azul hielo. Each accent carries a soft **halo/glow** on the filled CTA, active step chip, pill tab, slider fill and round `+` button. Note the varying **base black** per column (pure black / neutral / blue-tinted). |
| `ui-examples4.png` | Same board, second accent set: lima eléctrica, rosa neón, cian eléctrico. Captions call out **semantic collision** explicitly - the accent must not fight the green "done" and red "exclude" states. |

## The recurring aesthetic (the actual signal)

The user gravitates to dark, near-black neutral surfaces (no navy); a single vivid **fluorescent or neon
accent** that glows; **bold oversized hero numbers**; minimal, calm, low-chrome cards; a glowing
center-FAB bottom nav; and small celebratory touches (a streak flame). Everything is phone-first.

## Refinements from examples 3 and 4 (the accent is a system, not one colour)

- **The accent always carries a halo.** A soft coloured glow sits behind the filled CTA, the active chip,
  the pill, and the slider thumb. A flat fill of the same hex reads dead here.
- **The accent must survive the semantic palette.** Green means done and red means destructive, so those
  are already spoken for, and an accent close to either gets rejected. Check the clash before proposing a
  colour.
- **The base black is tunable too**, not a constant: pure black, neutral near-black, and a faintly
  blue-tinted black are treated as real choices that shift the whole mood.
- **Recurring furniture:** numbered **step chips** for a wizard, **segmented pill tabs**, a hero number with
  a small uppercase unit label beneath, `−`/`+` round buttons flanking a slider, and one full-width glowing
  CTA pinned at the bottom.
- **The user picks accents by comparison board**, not from a single mock. When proposing a visual
  direction, offer 3 accent variants on the *same* screen with a one-line rationale each, which is exactly
  the shape of these two files.
