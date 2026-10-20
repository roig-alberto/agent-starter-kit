# model-tiering history and measurements

## Delegation split loses on a single small task

**Measured: for one bounded task, Opus-plan -> Sonnet-exec costs ~5x MORE than Opus-solo** ($0.23 vs
$0.047). Writing a precise executable ticket cost Opus 3x the whole edit, then the executor stacks on.

## Opus reviewing every diff erases the win

Measured: a Sonnet edit cost $0.055 vs $0.135 for Opus, and an Opus re-read+reason adds ~$0.05-0.07, which
brings it back to Opus-solo. A machine gate is ~$0 on the passes, so the Opus cost is amortised only over
the failure rate.

## Reviewing a diff with Claude: hand it the DIFF, never the repo (measured 2026-09-15)

A Claude agent told to "review the uncommitted changes in this repo" explores: the Paseo reviewer spent
**1,410,000 context tokens over 24 turns** on a 190-line diff, because the whole session context is
re-sent every turn. The same review, diff pasted inline, one turn, no tools: **23k**. About 60x, same
class of findings.

Fed a noisy prompt (a 111KB generated snapshot pasted in), the lean reviewer reported two confident bugs
that did not exist: it could not see the unchanged `db.select().from(routines)` lines that disproved them.

## Measured evidence (agent-tool-bench, `references/plugin-verdicts.md` in agent-tool-bench)

- **Executor A/B (Sonnet-5 vs Opus-4-8 doing a bounded edit), n=3/task:** quality parity (pass^3 = 3/3
  both, trivial and harder tasks, including one needing real reasoning). The cost win is
  WORKLOAD-DEPENDENT: ~59% cheaper on a trivial fix, ~28% on harder ones (Sonnet burns ~2x input tokens as
  difficulty rises).
- **Pipeline (Opus-solo vs Opus-plan -> Sonnet-exec), n=1 directional:** the split was ~5x more expensive
  on one task; the planning stage alone cost 3x the solo edit.
- **Basis for the latency intuition:** the 41min-to-73s ticket case. Wall-clock is roughly tool_calls x
  ~14s, and ~9s per call is model reasoning, so a right-sized model on a self-contained brief is the
  lever; but for a small task the planning tax dominates, so inline wins.
- Box caveat: heavy multi-run `claude -p` matrices OOM this box, so run one arm at a time.

## 2026-10-16: the review format moved to the review skill

The finding format (Must / Should / Could fix, confidence 0-5, at most 5 Act on items, Dismissed with a
reason) and the leads-not-verdicts rule moved to the new `review` skill, together with the trigger
"review this diff". This skill keeps what a review costs: `review-diff` and the per-turn floors.

## Effort cap (2026-10-20)

The user capped effort at high: never `xhigh` or `max`. The low / medium / high split per kind of work comes from
Anthropic's "Spending your effort" post (read 2026-10-20 through a summary): implement and iterate at low, verify and
test on high, and higher effort fixed missed edge cases rather than a wrong approach (one task went from 1 of 5 at
low to 5 of 5 at xhigh, which this cap gives up on purpose). Agent Factory's effort list dropped `max` the same day.
