# Routing and delegation

## Lever 1: the session model (biggest, and it is the USER's)

A running session cannot reswap its own model. Launch **Sonnet** for mechanical or bounded sessions and
reserve **Opus** for reasoning-heavy ones: `claude --model sonnet`, or `/model sonnet` in-session.

| Sonnet (mechanical or bounded) | Opus (reasoning-heavy) |
|---|---|
| applying a known change | architecture and design decisions |
| running and reporting commands | root-cause debugging |
| lint, format, typo, and doc edits | ambiguous scoping |
| locate and search | cross-file coherence |
| CRUD or UI from a clear spec | security, money, and date logic |

Rule of thumb: **when unsure, Opus.** Sonnet matches Opus on bounded edits but does MORE work as ambiguity
rises (measured at about 2x input tokens on harder tasks), so a misroute costs rework.

## Lever 2: delegation inside an Opus session (narrow, and it LOSES for a single small task)

The only way to run a WHOLE task on Sonnet from an Opus session is a subagent. For one bounded task, an
Opus plan followed by a Sonnet execution costs about 5x MORE than Opus alone (see `history.md` in this
directory). So **manufacturing a brief solely to hand off one small edit is a net LOSS; do it inline.**

**Reflexive trigger:** the DEFAULT is inline Opus. Flip to a cheaper executor ONLY on a clear **amortize
signal**:

- the SAME change across many files or apps;
- a batch of independent edits runnable in PARALLEL;
- a big refactor whose exact edits are ALREADY decided (a plan you made anyway, or a spec the user handed
  you);
- or CONTEXT isolation (keeping a huge execution out of the Opus thread; a context win, not a cost one).

Executors already wired: `cavecrew-investigator`=haiku (locate), `cavecrew-reviewer`=haiku (review), and
`cavecrew-builder`=sonnet (bounded edit). Each model is the `model:` line of its file in `~/.claude/agents/`. Or
use the `Agent` tool's `model: sonnet|haiku`. Planning stays on the Opus main thread.

When a signal fires, both conditions must hold: (a) the task is bounded and fully specified, and (b) the
brief EMBEDS every value, path, and prior result the executor needs. It starts BLIND and cannot do "log
archaeology" (chasing a number from an earlier run or a terminal it cannot see). An under-briefed cheap
agent guesses and does worse, amplified: Haiku has the least headroom to recover.

## The delegation contract: `accept` must be EXECUTABLE and the gate DETERMINISTIC (not the planner)

This is what keeps the token win from eroding. The plan states acceptance as RUNNABLE checks: assertions
or a test command (`pageCount(10,3)===4`), a `tsc --noEmit` or lint run, or, for structured or LLM output,
a schema `.parse()` plus a grounding rule (the earned Loop `lib/**/*-verify.ts` pattern). **Never prose
like "looks right".** Then verify cheapest-first:

1. The executor edits and returns a receipt, with **no self-grading** (a no-Bash executor cannot wander).
2. A **DETERMINISTIC gate** runs `accept`: a CPU, about 0 model tokens.
3. Escalate to a model ONLY on failure, and to a **CHEAP model first** (a judge on Haiku or Sonnet, like
   the gpt-5.4-mini judge of the axi harness). Use Opus only on real ambiguity or a failed fix.

Why: **Opus reviewing every diff roughly ERASES the win** (the numbers are in `history.md` in this
directory). A machine gate costs about $0 on the passes, so the Opus cost is amortised only over the
failure rate. Bound the re-plan loop: after N retries, Opus does it inline. Acceptance that is genuinely
subjective (no test possible) is the only case a model must judge, and then use the cheap one.
