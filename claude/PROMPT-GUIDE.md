# PROMPT-GUIDE.md - driving less-capable models (for the human)

Written 2026-07-06 as a handoff from Fable 5. Audience: you, not the model. The
machine-side rules live in `~/.claude/RULES.md` (loaded every session); the scenario
playbooks live as skills (`debugging`, `research-decision`, `portability`). This doc
covers the part only you can do: how to phrase asks and when to distrust output.

---

## Part 1 - What actually separates a top-tier model from lower tiers

Behavioral differences, observable in daily work. Not architecture claims. Each gap
maps to a compensating prompt move in Part 2.

1. **Long-horizon autonomy.** A top-tier model holds a 40-step task without drifting
   or declaring victory at step 12. Lower tiers lose the thread: they forget a
   sub-task, "finish" early, or wander into side quests. The longer the task, the
   wider the gap.

2. **Self-verification instinct.** Top tier runs the code, measures the DOM, re-greps
   after a refactor - *unprompted*. Lower tiers stop at "the code looks right" and
   report success without evidence. This is the single most consequential gap: it's
   the difference between "done" meaning done and "done" meaning "probably".

3. **Ambiguity triage.** Knowing which ambiguities are safe to resolve with a sensible
   default (and saying so) versus which one question is worth asking. Lower tiers get
   this backwards: they either interrogate you about trivia or silently guess the one
   thing they shouldn't have.

4. **Calibration.** Saying "I'm not sure - here's how I'd check" instead of a
   confident wrong answer. Lower tiers are *more* confident when wrong, not less,
   because fluency and accuracy are decoupled. Biggest practical danger.

5. **Context discipline.** Knowing what's already established in the conversation vs
   what needs re-reading. Lower tiers re-read everything (slow, expensive) or forget
   what they read (wrong).

6. **Scope surgery.** Changing exactly what the task needs. Lower tiers "improve"
   adjacent code, reformat files, rename things - every extra line is review burden
   and regression risk.

7. **Tool orchestration.** Batching independent calls, delegating searches to
   subagents, picking the cheap check before the expensive one. Lower tiers work
   serially and pick tools by habit, not fit.

---

## Part 2 - The cheat-sheet: gap → prompt move

| Gap | What you say / do |
|---|---|
| Weak self-verification | End task prompts with: **"run it and paste the output"** / "measure the DOM, don't guess" / "show me the failing test before and passing after". Never accept "should work now". |
| Long-horizon drift | Don't send one mega-prompt. **Split into phases yourself** and gate each ("do phase 1 only, stop for my review") - or just invoke `/plan`, which encodes exactly this. For multi-day work, insist on a plan file on disk (`PLAN.md` / `MIGRATION.md`), never conversation memory. |
| Ambiguity guessing | Pre-empt: "if anything is ambiguous, list your assumptions before coding." When a wrong guess happens, don't just correct the output - correct the *assumption* so it doesn't recur. |
| Overconfidence | For anything factual/fast-moving (library APIs, pricing, versions): **"verify this against the docs/repo, don't answer from memory"**. Ask "how confident, and what would change your answer?" - a good answer names a check; a bad one restates the claim louder. |
| Context loss in long sessions | When a session gets long, run `/handoff` and start fresh rather than pushing a degraded context. Re-state the current goal in one line after any big pause. |
| Scope creep | "Touch only what's needed for X; no drive-by refactors" (RULES.md says this, but repeat it on risky refactors). Review the diff, not the summary: `git diff --stat` first - any file you didn't expect is a flag. |
| Serial/wasteful tool use | "Search with a subagent", "batch the reads". If it's rebuilding/redeploying per tweak, say "batch changes, redeploy once at the end" (the biggest token sink on this box). |

## Part 2b - Picking the model per task shape

- **Lower tier (e.g. Sonnet) is fine for**: one-shot-sized features on an existing
  app (the skill rails carry it), mechanical refactors/renames, running drills,
  doc updates, the scheduled audit. The skills + RULES.md were built precisely so
  this tier performs well here.
- **Top tier for**: migrations (long-horizon), new-app design/grilling,
  debugging where the cause is genuinely unknown, security reasoning, anything
  where a wrong-but-confident answer is expensive.
- Tell: if a lower-tier session starts looping (re-running the same check,
  re-reading the same files) or confidently contradicts a Facts block - stop,
  `/handoff`, and rerun the task on the top tier.

## Part 3 - Standing habits that compensate across the board

- **Make the model state the success criterion before it starts.** "What will you run
  to prove this works?" One sentence up front buys you an honest finish.
- **Trust artifacts over conversation.** Plans, decisions, and migration state go in
  files (the skills enforce this). A lower-tier model with a good plan file on disk
  beats a better model improvising.
- **The skills are the safety net - check they fired.** RULES.md routes scenarios to
  skills. If the model dives into a debugging session without the reproduce-first step
  or edits compose without mentioning portability invariants, say "load the X skill" -
  that's the tell it skipped the router.
- **Confidence is not evidence.** The lower the tier, the more polished the wrong
  answer reads. When something matters, ask for the receipt (output, link, line
  number), not a better explanation.
