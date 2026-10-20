# Method: what the harness can and cannot tell you

## The design limit that decides everything (chosen versus used)

Each condition carries a `command_policy` with `require_any_prefix` / `forbid_any_prefix`. That **forces**
the arm to use its assigned tool.

So the harness measures efficiency-when-used. It structurally **cannot** tell you whether an agent would
pick the tool on its own, because it has removed the alternative.

That distinction is not academic. context-mode was rejected here because the agent called its tools
**zero times** across three runs with the tools loaded and named in the system prompt; it used Bash
instead, because Bash + rtk already do that job. Forced to use them, it cost +37% vs baseline. A
`forbid_any_prefix: ["bash"]` arm would have shown only the +37% and hidden the reason.

**To answer "will it be chosen", add a condition with NO forbid rules and check the tool's own telemetry
for call counts** (context-mode writes `total_calls` to `~/.claude/context-mode/sessions/stats-pid-*.json`).
Zero calls IS the result.

**Two rules this cost us; the full evidence is in `context-mode-verdict.md`:**

1. **Test the tool in the mode it was DESIGNED for before rejecting it.** A first verdict reached on
   MCP-only, plus the reasoning "forcing the tools is the ceiling so hooks can only be worse", was wrong:
   the hooks route SELECTIVELY, which is smarter than a ban-Bash arm. Measured with hooks it was +127%
   tokens; the conclusion held, the argument did not.
2. **Purge shared state between arms or they are not independent.** Two runs isolated by
   `--strict-mcp-config`, separate settings, and separate processes still leaked into each other through a
   shared SQLite store, one arm being served the other's output as its own history. Process isolation is
   not state isolation.

## Method rules the measured runs earned

- **A router or skill eval MUST cap `--max-turns` (2 is enough), or it burns quota doing the whole task.**
  Skill selection happens on turn 1 (the `Skill` tool_use); without a cap the agent keeps going and
  completes the fixture's task for 48-75 turns per run. The cap is ~30-40x cheaper and loses nothing (you
  only read turn 1). Run FEW at a time (3-6), never 15 unattended. `run.sh` now passes `--max-turns 2`.
- **`claude plugin details <name>` reports a plugin's always-on token cost**; use it instead of parsing
  frontmatter. `claude plugin enable|disable <name>` gives a clean A/B with no settings files.
  `claude plugin eval --ablation with-without` runs a no-plugin baseline arm.
- **At n=3, total tokens and cost are CACHE NOISE.** Totals swung 194k-326k within one arm on prompt-cache
  warmth alone, and cost inverted with it. Judge on cache-independent metrics (turns, lines, dependencies
  added, correctness) and quote total tokens as indicative only.
- **Read the vendor's rig, not its headline.** caveman's "65%" is chat-only, output-only, and excludes its
  own always-on cost. ponytail's "-54% LOC" was measured on Haiku and does not replicate on Sonnet, where
  the baseline is already lazy.
- **Verify the output works before scoring it cheap.** Every arm was run against real inputs; a smaller
  diff that drops a trailing-edge call is not a win. `--repeat 3` is the floor, and n goes in the reply.

## When the harness is the wrong instrument

- The tool is not agent-facing (a library for app code): use `research-decision`.
- The tool is broken rather than slow: use `debugging`.
- You need one number now and the decision is reversible: a single
  `claude -p ... --output-format json` run gives `usage` and `total_cost_usd`; say n=1 in the reply. Do
  NOT build a bespoke harness; that is what this skill exists to stop.

## Grading criteria: capability vs regression, pass@3 vs pass^3

Split what you are grading, and hold the two kinds to different bars:

| kind | what it asks | bar |
|---|---|---|
| **capability** | does the new thing work at all | `pass@3` > 90%, succeeds at least once in 3 |
| **regression** | does the existing thing still work | `pass^3` = 100%, succeeds all 3 times |

The asymmetry is the point. A new capability that lands 1 in 3 is promising; an existing behaviour that
lands 2 in 3 is broken. Reporting a single "success %" hides that.

This applies directly to the untested gap in our own system: **nothing checks whether our ~53 skills
actually fire.** A skill-router test is a REGRESSION eval (a router line that matches two prompts in three
is a defect, not a 67%), so it must be graded `pass^3`, not averaged.

Whatever you grade, state n and the bar in the reply. `--repeat 3` is the floor.
