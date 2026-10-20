---
name: agent-tool-bench
description: >-
  Measure whether an agent tool (MCP server, CLI wrapper, plugin, skill, prompt style) is worth
  adopting, with the axi harness at ~/projects/axi. Use when the question is "is X worth it", "does X
  save tokens", "should I install X", "is X faster/cheaper than Y", "A vs B", "benchmark this",
  "measure this", "prove it", "test it", "is it worth it", "compare them", or when about to adopt or
  remove any agent-facing tool. NOT for debugging a broken tool (use `debugging`), choosing libraries
  for app code (use `research-decision`), or auditing a tool's OUTPUT shape against the AXI principles
  (read `~/projects/axi/principles.yaml` directly).
---

# agent-tool-bench

Measure the tool instead of arguing about it. This prevents two failures: adopting a token-saving tool on
a vendor's benchmark, and rejecting one on a hand-rolled n=1. The instrument is the axi harness in
`~/projects/axi` (a shallow clone of `kunchenguid/axi`).

## Steps

1. **Decide FIRST which question you have, and say it out loud before running anything,** because the
   two questions need different setups and getting this wrong wastes every run.

   | Your question | Can the harness answer it? |
   |---|---|
   | "How efficient is tool X **when used**?" | YES, this is what it is built for |
   | "**Will** the agent choose X over what it already has?" | **NO, by design**; see `references/method.md` |

   Done when: you have written the question as one of the two rows above in your reply.

2. **Pick the harness.** `bench-github/` has 17 read-only tasks against the public `openclaw/openclaw`,
   with no browser and no daemon; it is the cheapest, so **start here** when proving the pipeline works.
   `bench-browser/` has 14 browsing tasks and needs Chrome plus a daemon lifecycle. Setup is in
   `references/harness.md`.

   Done when: `cd ~/projects/axi/bench-github && npm run bench` prints the command reference.
3. **Add a condition or a task if you need one.** Both are declarative YAML with no code
   (`config/conditions.yaml` and `config/tasks.yaml`); copy the nearest existing arm and edit it.

   Done when: the new `name` or `id` appears in the YAML file and its first run leaves a folder under
   `results/`.
4. **Run the matrix** with `npm run bench -- matrix --condition cli,axi --task pr_then_checks
   --repeat 3 --agent claude --model claude-sonnet-5`, then `npm run bench -- report`.

   Done when: `results/report.md` lists every condition and task you asked for, each with 3 runs.
5. **Read the results before believing the table.** Start with `results/report.md`, and on any failure
   read the run's `agent_output.txt` first. Correctness is LLM-judged, so a cheap arm that is WRONG is
   caught rather than scored as a win.

   Done when: every FAIL row has had its `agent_output.txt` read and its cause named.
6. **Record the verdict** in `references/plugin-verdicts.md`, with n and the bar stated.

   Done when: the new entry exists in that file with the numbers, n, and the decision bar.

## Rules

- **To answer "will it be chosen", add a condition with NO forbid rules and check the tool's own telemetry
  for call counts.** Each condition's `command_policy` forces the arm to use its tool, which removes the
  alternative. Zero calls IS the result.
- **Test the tool in the mode it was DESIGNED for before rejecting it.** A tool with hooks routes
  selectively, which a ban-Bash arm does not reproduce.
- **Purge shared state between arms, or they are not independent.** Process isolation is not state
  isolation; a tool with a cross-session store needs a hard purge in the runner.
- **Inject anything that lives in `~/.claude` settings through the condition's `agents_md`.** Runs use
  `claude --setting-sources ''`, so caveman, rtk, and RULES.md do not apply inside a run.
- **Cap a router or skill eval at `--max-turns 2` and run few at a time (3-6).** Skill selection happens on
  turn 1; without the cap the agent does the whole task and burns quota.
- **Judge on cache-independent metrics at n=3:** turns, lines, dependencies added, and correctness. Total
  tokens and cost are cache noise at that n, so quote them as indicative only.
- **Read the vendor's rig, not its headline,** and **verify the output works before scoring it cheap.**
  `--repeat 3` is the floor, and n goes in the reply.
- **Grade capability at `pass@3` and regression at `pass^3`.** A new capability landing 1 in 3 is
  promising; an existing behaviour landing 2 in 3 is broken. A skill-router test is a regression eval.
- **Never build a bespoke harness.** If you need one number now and the decision is reversible, a single
  `claude -p ... --output-format json` run gives `usage` and `total_cost_usd`; say n=1 in the reply.

## Gotchas

- **Every run returns `FAIL | 0 turns | $0.0000` in about 2s.** The default agent is `codex`; pass
  `--agent claude`, which is mandatory. The artifact says *"The 'claude-sonnet-5' model is not supported
  when using Codex with a ChatGPT account."*
- **`npm i -g gh-axi` reports success but nothing is runnable.** npm's global bin is NOT on PATH on this
  box; symlink it into `~/.local/bin` as shown in `references/harness.md`.
- **A claude run fails at the judging step.** The judge runs on codex (`gpt-5.4-mini`), so codex auth must
  work even for a claude run.
- **Several `claude -p` runs at once crash the box.** Heavy multi-run matrices OOM this box; run one arm
  at a time.
- **Prove a setting by its effect, not by its presence in a config file:** run one headless `claude -p --model haiku` and check that `modelUsage` shows the expected model. A plugin env setting was documented as live for five weeks while its hook patched the wrong folder.

## References

- `references/harness.md`: where the harness lives, setup, running, result paths, adding conditions and
  tasks, and arm isolation.
- `references/method.md`: the chosen-versus-used design limit, the method rules, when the harness is the
  wrong instrument, and capability versus regression grading.
- `references/plugin-verdicts.md`: every measured verdict (caveman, ponytail, gh-axi, graphify,
  tasks-axi, headroom, chrome-devtools-axi, Graft, context-mode, the Sonnet executor, Paseo). Add new ones
  here.
- `references/context-mode-verdict.md`: the worked context-mode evidence behind the designed-mode and
  shared-state rules.
- `references/router-eval/README.md`: the router eval (does a prompt load the right skill?): the baseline,
  when to run the free check, a per-skill run or a full sweep, and the write-proofing it must keep.
- `references/review-eval/README.md`: the reviewer recall eval (17 real bugs from our repos): run it before changing
  `review-diff`'s prompt, model or effort, and when the `sonnet` alias moves.
- `references/history.md`: dated incidents and a map from the old section numbers to the current files.
