# History

## Origin (2026-10-15 and 2026-10-16)

- The user asked for "an architecture MD with architectural decision records to explain what alternatives
  were considered instead of the code that's there, a glossary MD and a thin layer of docs to help the agents
  navigate around the main aspects of the code just to speed up AI exploration".
- User decisions: a reusable skill, proved first on Agent Factory; curated ADRs inside ARCHITECTURE.md (10 to
  20, linking decision-log IDs) while the full dated decision log stays; one CODEMAP.md at the root rather
  than a README per folder.
- Measured on 2026-10-15: none of the user's 9 app repos had an ARCHITECTURE.md, none had a diagram, and the
  architecture lived inside IMPLEMENTATION_PLAN.md files of 15 to 56 KB. Agent Factory's data-model section
  drifted from the code on 2026-10-13 (the old `runs` plan) and was fixed by hand.

## Sources (ideas, rewritten in the house style)

- owainlewis/blueprint `/architecture`: decided versus built status, a required diagram that is rendered and
  checked, numbered system rules with their enforcement, and the rule to update the doc when ownership, data,
  trust boundaries or deployment change.
- mattpocock/skills `domain-modeling` and `GLOSSARY.md`: the glossary entry shape (term, meaning, words to
  avoid, relationships, resolved ambiguities), no implementation detail in the glossary, and the three-test
  filter for an ADR (hard to reverse, surprising without context, a real trade-off).
- The CODEMAP and the path check are this box's own: names instead of line numbers, and a script so the map
  fails loudly instead of misleading an agent.

## First use on Agent Factory (2026-10-16)

A fresh agent wrote Agent Factory's three docs from this skill alone: 18 ADRs, 13 code areas, 3 flows, 158
paths checked with 0 missing. Its notes changed the skill: step 7 now says to check the plan prompt rather
than add it; a gotcha explains what the path check counts as a path; the diagram check names a method
(parse with a pinned `mermaid`); the glossary template shows two bulleted entries; moved sections keep their
heading; ARCHITECTURE.md may reach about 450 lines with ADRs of four to eight lines; the data model names
stores outside the database; and fixing lines the move made stale is part of step 7. Writing the docs also
surfaced a real bug: three server event types were never listened for by the web app.

## REVIEW.md, the fourth file (2026-10-20)

The user asked for a REVIEW.md in every repo, like ARCHITECTURE.md, after reading Anthropic's "Solving code review"
post and Claude Code's Code Review docs. Two choices came from those docs: the four sections, and reading only the
committed copy (never the change's own) so a change cannot soften its own review.
