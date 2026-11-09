---
name: brandkit
description: Designs a brand identity as one premium brand-board image (logo concept, colours, typography, mockups, imagery in a grid), working out the brand's meaning before drawing anything. Adapted from Leonxlnx/imagegen-skills (MIT). Use when the user wants "a logo", "a brand kit", "a visual identity", "brand guidelines", "a look for my idea", "a brand for the capture page", "colours and fonts for the brand", or a refresh of an existing brand. NOT for an app's UI tokens or visual direction (use frontend-design), clickable variants (use prototype) or a launch video (use launch-motion).
---

# Brandkit

Makes one brand board that reads like a senior identity studio made it, instead of a generic AI logo with random
mockups. The method is strategy first, then a reduced symbolic logo, then a disciplined board. The full art
direction (panel systems, visual modes, palettes, anti-generic rules, the prompt template) is the upstream skill in
`references/upstream.md`.

## Steps

1. **Intake.** Decide whether this is a new identity, an extension of an existing brand, or a refresh. Take the
   name, logo, colours, fonts and references from the conversation and supplied files first; ask one short question
   only for what is missing. Supplied assets win over every default.
   Done when: the mode and the assets to preserve are written in one line.
2. **Strategy.** Infer the category, audience, product function, emotional promise, trust level, visual world, core
   metaphor and what the brand must avoid. For a venture idea, read its `ventures/ideas/<slug>/IDEA.md` in
   `~/projects/research` first: the buyers' own words and the offer are the strategy's raw material.
   Done when: a short strategy block exists with exactly one core metaphor.
3. **Art direction.** Read `references/upstream.md`, then pick the layout (3 x 3 by default), one visual mode, one
   disciplined palette, and a logo concept method (at most two combined).
   Done when: the layout, mode, palette and logo idea are named.
4. **Prompt.** Fill the upstream "Prompt template" with steps 1 to 3 and the requested canvas size or ratio.
   Done when: the complete prompt text exists.
5. **Generate.** Use OpenAI's GPT image model, version 2.5 or newer: the user finds its results better. If the agent
   has no image tool, give the user the prompt to paste into ChatGPT with that model, and say so. Report the real
   output size, never a promised one.
   Done when: an image file exists, or the user has the prompt.
6. **Check.** Compare the image with the upstream "Anti-generic rules" and "Final output standard": one logo used
   consistently, few colours, sparse readable text. Regenerate with a corrected prompt at most twice, then show the
   best one.
   Done when: the user sees the board with the strategy block under it.

## Rules

- Never copy a reference's logo, name, composition or slogan; references set the quality bar and rhythm only. An
  identity has to be ownable.
- Keep text on the board sparse and large. Image models turn long or tiny text into garbage.
- When an app or a page is built from the approved board, hand over to `frontend-design` with the board as its
  reference. The board's palette and type seed `DESIGN_TOKENS.md`, so the product matches its brand.

## References

- `references/upstream.md`: the full upstream skill (strategy table, logo methods, panel systems, visual modes,
  palettes, text and tagline rules, prompt template). Read it at step 3.
- `references/LICENSE`: the upstream MIT licence. Keep it with every copy of this skill.
