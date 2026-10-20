# Refreshing the copied references, and what was left out

The copied files under `references/` (craft, diagrams, print, questions) do not auto-update. The live
claude.ai skill changes when Anthropic ships a new Design release; this copy does not.

## Provenance

The four files are verbatim copies of the claude.ai Design artifact type (release `1791586906-56be`),
read 2026-10-11 from the private source canvas `https://claude.ai/artifact/RGtNwJ4KpNJWeapVq166Fv`
("design-reference"). They are Anthropic text for **private use only**: this repo (`claude-skills`) is
PRIVATE (verified 2026-10-11), and these files must never be copied into a public repo.

## How to refresh

1. Run the Artifact tool `read` on the source canvas with
   `paths: ["artifact-type/reference/craft.md", ".../diagrams.md", ".../print.md", ".../questions.md"]`.
2. Overwrite `references/*.md`, keeping the provenance header comment (the new release id and the date).
3. Commit.

Refresh when a canvas reports a newer release than `1791586906-56be`, or every few months.

## Files deliberately NOT copied

These are claude.ai-editor-only: `SKILL.md` (publishing mechanics), `format.md` (.dc.html syntax),
`design-system-components.md`, `view-state.md`, and `brand-colors.md` / `brand-typography.md`
(Anthropic's own brand).
