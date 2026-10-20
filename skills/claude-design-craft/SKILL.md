---
name: claude-design-craft
description: >-
  Design craft rules of the claude.ai Design canvas, copied so any agent can produce wireframes, mockups, artboards, diagrams or print pieces as plain HTML files in a repo or our own board app. Use when an agent must design screens as local HTML: "wireframe this as HTML", "design it in the repo", "make artboards", "design with opencode/codex", "same quality as the Claude design skill", "mockups for the board app", "draw a flowchart/diagram as HTML", "design a poster/flyer PDF". NOT for publishing to the real claude.ai canvas (use the Artifact tool's Design type) or production UI code (use frontend-design).
---

# claude-design-craft - Claude's design-canvas craft, for plain-HTML artboards

This skill gives any agent outside claude.ai the same strict design
craft the Claude app follows. Without it, the agent designs from generic taste and produces templated "AI
slop": gradient washes, Inter, emoji, left-border cards, and filler copy. The craft lives in verbatim
copies of the claude.ai Design references, which are Anthropic text for private use only.

## Steps

1. **Read `references/craft.md` in full before the first artboard**, because it is the skill. Then, only if
   the piece needs it, read `references/diagrams.md` (flowchart, org chart, system map; read it FIRST),
   `references/print.md` (poster, flyer, PDF document; read it FIRST), or `references/questions.md` (how
   many questions to ask before building). Done when: a line in the reply names the references you read.
2. **Translate claude.ai-only mentions as you read.** The references assume the claude.ai editor, so map
   them and never follow them literally:
   - `.dc.html`, `<x-dc>`, `<helmet>`, `DCLogic`, `{{holes}}`, `data-props`, tweaks, the properties panel,
     `support.js`, and `/_blob/` uploads become **plain HTML**: one self-contained `.html` per artboard,
     styles inline or in one `<style>`, and static values written directly.
   - `canvas.json` artboard entries (`x`,`y`,`w`,`h`, `notes`) become the same idea in a local
     `canvas.json` beside the artboards, if the consuming app reads one; otherwise use one file per screen
     named for its state.
   - "Arrow tool", "Play", "Theme menu", and "Share" have no equivalent; ignore them.
   - Anthropic brand colours (Ivory/Slate/Clay) are only for Anthropic-branded work. Our apps each get
     their own look (the user's choice, 2026-10-11).
   Done when: `grep -rlE "x-dc|\{\{" <artboard dir>` finds nothing in the files you wrote.
3. **Settle the look before building** (craft.md "Settle the aesthetic"). When a person is there, ask, or
   show 2-4 genuinely different low-fi direction artboards. In a headless run, commit to one nameable
   direction and state it in one line.
   Done when: the reply holds the one-line named direction (or the 2-4 low-fi artboards exist).
4. **Build the artboards following craft.md.** Use a fixed root for phone, device, and print (phone
   390x844) and a fluid root for PAGEs; flex or grid with `gap`; real `<button>`/`<a>`/`<label>`; contrast
   4.5:1; no filler, no invented stats, `[PLACEHOLDER]` for missing facts; and no fake status bar.
   Done when: every artboard opens as a standalone `.html` file with no console errors.
5. **Apply the hand-off fidelity rule** from `frontend-design`: design hand-offs are hi-fi STATIC
   frames, one per state, never a clickable prototype. This overrides craft.md's prototype guidance when
   the output is a design hand-off.
   Done when: the hand-off folder holds one static frame per state and no click handlers.

## Rules

- **Never copy the reference files into a public repo.** They are Anthropic text for private use only;
  this repo is private, and provenance is recorded in `references/refresh.md`.
- **Do not edit the copied references by hand.** They are verbatim copies, so a local edit is lost or
  conflicts at the next refresh.
- **Refresh the copy when a canvas reports a newer release** than the one in `references/refresh.md`, or
  every few months, because the copy does not auto-update.

## Gotchas

- **The agent follows a claude.ai editor instruction literally** (writes `<x-dc>` or `{{holes}}` into a
  local file). Apply the step 2 translation table instead.
- **A claude.ai Design canvas must go to a builder as plain files.** Use the export recipe in
  `references/export.md`; interactive frames (handlers, `<sc-for>`) need the editor runtime and do not
  export this way.

## References

- `references/craft.md`: the full design craft. Read it in full before every design job.
- `references/diagrams.md`: flowcharts, org charts, system maps. Read it first for any diagram.
- `references/print.md`: posters, flyers, PDF documents. Read it first for any print piece.
- `references/questions.md`: how much to ask before building.
- `references/export.md`: exporting a claude.ai Design canvas to plain HTML and PNG for a builder.
- `references/refresh.md`: provenance, the refresh procedure, and which source files were left out.
