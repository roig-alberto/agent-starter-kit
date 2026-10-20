---
name: model-tiering
description: >-
  Choose which Claude model and effort level does a piece of work, when delegating to a cheaper model
  pays, and what a review costs. Use when deciding Sonnet vs Opus for a task, whether to delegate a build to
  cavecrew-builder or a subagent, or picking a session's model, or the user says "should this be
  sonnet", "run it on the cheaper model", "use sonnet to save tokens", "is delegating worth it", "opus
  plans sonnet executes", "why did that agent cost so much". NOT for the general subagent
  context-filter rule (RULES tool-discipline), choosing a library or tool (use `research-decision` or
  `agent-tool-bench`), or running a review (use `review`).
---

# model-tiering

Pick which model does the work so tokens drop without quality dropping. It prevents two measured
failures: (1) splitting a single small task into an Opus plan and a Sonnet execution, which costs about
5x MORE than Opus just doing it; and (2) misrouting an ambiguous or hard task to Sonnet, where the rework
costs more than the saving.

## Rules

- **The session model is the biggest lever, and it is the USER's.** A running session cannot reswap its
  own model. Launch **Sonnet** for mechanical or bounded sessions and reserve **Opus** for
  reasoning-heavy ones, with `claude --model sonnet` or `/model sonnet` in-session. The routing table is
  in `references/routing-and-delegation.md`.
- **When unsure, choose Opus.** Sonnet matches Opus on bounded edits but does MORE work as ambiguity
  rises, so a misroute costs rework.
- **Inside an Opus session, do the work inline by default.** Manufacturing a brief solely to hand off one
  small edit is a net LOSS, because writing a precise executable ticket costs more than the edit itself
  and the executor's cost stacks on top.
- **Flip to a cheaper executor ONLY on a clear amortize signal:** the SAME change across many files or
  apps; a batch of independent edits runnable in PARALLEL; a big refactor whose exact edits are ALREADY
  decided (a plan you made anyway, or a spec the user handed you); or CONTEXT isolation, which keeps a
  huge execution out of the Opus thread (a context win, not a cost one).
- **When a signal fires, the task must be bounded and fully specified, and the brief must EMBED every
  value, path, and prior result the executor needs.** The executor starts BLIND and cannot do "log
  archaeology", so an under-briefed cheap agent guesses and does worse; Haiku has the least headroom to
  recover.
- **Use the executors already wired:** `cavecrew-investigator` on haiku (locate), `cavecrew-reviewer` on
  haiku (review), and `cavecrew-builder` on sonnet (bounded edit), or the `Agent` tool's
  `model: sonnet|haiku`. Planning stays on the Opus main thread.
- **Make `accept` EXECUTABLE and the gate DETERMINISTIC, never the planner.** The plan states acceptance
  as runnable checks, never prose like "looks right"; a machine gate costs about $0 on the passes, while
  Opus reviewing every diff roughly erases the win. The contract and its cheapest-first verification
  order are in `references/routing-and-delegation.md`.
- **Verify that Sonnet or Haiku holds quality on a NEW task class with `agent-tool-bench`.** Never assume
  it. When the `sonnet` or `opus` alias moves to a new model, rerun the reviewer eval
  (`agent-tool-bench/references/review-eval/`) before trusting the old verdicts.
- **Effort is capped at high (user, 2026-10-20): never `xhigh` or `max`,** in a session, a subagent, or an
  Agent Factory step. Use **low** to sketch, plan or iterate, **medium** for ordinary implementation (Claude
  Code's default), and **high** to verify, fix a bug in existing code, or review. Higher effort catches
  missed edge cases, not a wrong approach, so a wrong approach needs a new plan, not more effort.

## What a review costs

- **Hand the reviewer the DIFF, never the repo.** An agent told to "review the uncommitted changes"
  explores, and the whole session context is re-sent every turn; the same review with the diff inline,
  one turn, and no tools costs about 60x less with the same class of findings. Use `review-diff`
  (`review-diff [--base master] [--model sonnet] [--focus "money paths"]`); its flags and the per-turn
  floors are in `references/diff-review.md`. The finding format, the triage and when an exploring
  reviewer is worth it are in the `review` skill.

## Gotchas

- **A lean reviewer reports confident bugs that do not exist.** It was fed a noisy prompt (a large
  generated file). Keep generated blobs out of the diff; `review` verifies every finding.
- **Heavy multi-run `claude -p` matrices OOM this box.** Run one arm at a time.

## References

- `references/routing-and-delegation.md`: the Sonnet versus Opus routing table, the wired executors, and
  the full delegation contract with its cheapest-first verification order.
- `references/diff-review.md`: `review-diff` usage and flags, and the per-turn context floors.
- `references/history.md`: the measurements behind every rule (executor A/B, pipeline split, the 1.41M
  token review, the latency case).
- `references/plugin-verdicts.md` in `agent-tool-bench`: the full benchmark records.
