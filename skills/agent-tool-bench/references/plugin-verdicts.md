# Measured verdicts: plugins and tools tested on this box

Full evidence behind the verdicts and method rules (`method.md`). Keep new verdicts here, not in
`SKILL.md`. Section signs (§) below cite the old `SKILL.md` numbering; `history.md` maps them to the
current files.

## caveman (2026-09-06, n=3, agentic task)

| arm | total tok | **output tok** | cost | turns |
|---|--:|--:|--:|--:|
| caveman ON | 222,342 | **1,448** | $0.1943 | 4.7 |
| caveman OFF | 281,778 | **1,884** | $0.1499 | 5.3 |

**Holds: output tokens -23%**, consistent across all six runs (answers 2,133-3,399 chars with it
on, 3,116-3,874 off).

**Does NOT hold: the 21% total-token gap is cache noise.** Totals swung 194k-326k *within* arms
purely on prompt-cache warmth (`cache_read` 145k vs 316k), and cost inverted with it - the cheapest
runs were the cache-heavy ones. At n=3 no total-token claim survives.

**Its advertised 65% is chat-only.** Its own rig (`evals/`, snapshot 2026-04-08, opus-4-6) runs 10
conversational Q&A prompts, measures OUTPUT tokens only, and does not count the plugin's own
~1,420 tok always-on. Their README even admits an earlier version's numbers "were inflated".

**Break-even: ~6,200 output tokens of prose per session** (1,420 always-on / 0.23). Long analytical
sessions clear it; short build sessions just pay the 1,420. Verdict: keep, but it is not 65%.

## ponytail (2026-09-06, n=3, code task with two over-build traps)

Task: add `debounce` (tempts lodash) and `formatRelativeTime` (tempts date-fns) to a throwaway repo.

| | src files | code lines | deps | tokens | turns | correct |
|---|--:|--:|--:|--:|--:|:-:|
| ponytail ON | 1-2 | 28 | 0 | 250,006 | **4.3** | 3/3 |
| baseline | 3 | 31 | 0 | 509,278 | **9.0** | 3/3 |

All six verified against real inputs, not line-counted: debounce collapsed 3 calls to 1, and
minute/hour/yesterday strings matched in every run. Nothing traded away for brevity.

**Does NOT hold: the advertised -54% LOC.** Measured -9% (28 vs 31), and ponytail's own runs ranged
19-36 lines - spread wider than the effect.

**The over-build trap never sprang: neither arm installed a single dependency.** Sonnet already
reached for `Intl.RelativeTimeFormat` and a plain closure. Ponytail's benchmark ran on **Haiku
4.5**, where that instinct is real (their date-picker case: 404 lines -> 23). On Sonnet the
baseline is already lazy, so the skill fixes a problem this model largely does not have.

**Holds, larger than claimed: turns 4.3 vs 9.0, tokens halved.** Not cache noise - turn counts are
behavioural and split cleanly (4,4,5 vs 11,7,9). The baseline built extra scaffolding and
self-verified past the brief ("also test index.ts export path resolves under NodeNext-style
tooling"); ponytail did what was asked and stopped.

Verdict: keep for restraint in SCOPE, not for shorter code. **Caution:** RULES demands re-reading
the request and listing unfinished sub-tasks before ending a turn. A skill that trims
self-verification could clip that. Watch it on a task with real sub-parts.

## gh-axi vs raw gh (2026-09-05, n=1, illustrative only)

`pr_then_checks`, sonnet, both arms judged correct:

| condition | input tok | cache% | cost | turns |
|---|--:|--:|--:|--:|
| `cli` raw gh | 78,141 | 64% | $0.1300 | 3 |
| `axi` gh-axi | 78,227 | 87% | **$0.0770** | 3 |

n=1 proves the pipeline, not the tool.

## Three external tools evaluated 2026-09-07 (graphify, tasks-axi, headroom) - all SKIP

Read-only source/doc review + one live graphify head-to-head. No paid benchmark was needed:
each was settled for free before spending a run.

### graphify (code Q&A) - SKIP for code, keep for its own jobs
Built the free AST-only graph of Loop (801 nodes / 2287 edges, no LLM). Head-to-head on one
question with a known answer ("how does undo work across triage/kill/freeze/resurface, what field
does it restore") graded against `loop/CLAUDE.md`:

| | graphify | `cavecrew-investigator` |
|---|---|---|
| answer correct | **no** - located files/symbols, never the fact | yes, matched ground truth |
| body-level fact (`restores lastTouchedAt`) | cannot - AST graph has no function bodies | yes, quoted the line |
| tokens INTO main context | `query`: ~2k unranked nodes, truncated | ~400 (the result) |
| tokens spent | ~0 (free build) | 37.4k out-of-thread |

`explain`/`path` give accurate call edges but need a node id you already know. Verdict: for the
RULES "how does code work" branch the subagent wins; `graphify query` clause cut from the router.
graphify's real jobs (visual map, cross-repo merge, non-code corpora) untested and out of scope.
Gotcha: `uv tool run graphifyy python` fails; the interpreter is the binary's shebang
(`~/.local/share/uv/tools/graphifyy/bin/python`). `detect` must be PERSISTED to
`.graphify_detect.json`, not just printed, or Part A errors.

### tasks-axi - SKIP
`kunchenguid/tasks-axi` (NOT in the axi catalog; there is no repo named `task-axi`). Agent CLI over
a hand-editable `backlog.md`; its pain is "every backlog mutation regenerates markdown through the
model." That does not occur here: the Edit tool already does surgical old_string/new_string diffs,
so a tick/append costs only the changed span. Measured: HARVEST.md = 14 dense PROSE items (~223
tok/line), not terse tasks; FEATURES.md churns ~15x/60d at ~26 lines added. Format mismatch, no
consumer for its dependency/holds/ready graph, and it wants an always-on SessionStart hook. Skip.

### headroom - SKIP on this box (workflow, not billing)
`headroomlabs-ai/headroom` (69k stars). Auth is FINE - `wrap claude` points `ANTHROPIC_BASE_URL` at
a local proxy and keeps subscription OAuth, no API key. **But** (read `headroom/providers/claude/
runtime.py` at HEAD): any non-`api.anthropic.com` base URL DETERMINISTICALLY disables Claude Code
Remote Control for CC >= 2.1.196 (box is 2.1.263) - `/rc` vanishes, upstream gate in the CC binary,
proxy cannot restore it. This box IS RC-driven (phone workflow, `claude-spawner` (not in this kit)). Sibling gates:
on-demand tool loading + the **1M context window** are also base-URL-gated (restorable, 1M only
with `--1m`). And on a coding agent it compresses only tool output/logs/JSON (source + system
prompts pass through) - exactly what rtk already compacts, so the 20% headline is vs UNFILTERED
output, not vs rtk. Trades away RC for a marginal-over-rtk win. Skip. Telemetry beacon on by default
(`HEADROOM_BEACON=off`); `wrap` also registers Serena MCP at user scope as a side effect.

## chrome-devtools-axi vs Playwright MCP vs chrome-devtools-mcp (2026-09-08, n=3, bench-browser)

Sonnet-5, 2 tasks x 3 repeats, all arms judged 3/3 correct (`pass^3` = 100%, no regression).
Built a `playwright-mcp` arm (mirrors the `chrome-devtools-mcp` wiring; needed a one-line
`runner.ts` branch - the runner keys MCP setup on hard-coded condition ids, a new id silently
falls through to the empty-config CLI branch and the server never registers: `mcp_servers:[]`).

| task | arm | input tok | cache% | turns | $/run |
|---|---|--:|--:|--:|--:|
| wikipedia_fact_lookup | chrome-devtools-axi | 115,181 | 89% | 4.0 | 0.0747 |
| | chrome-devtools-mcp | 173,201 | 99% | 3.7 | 0.0481 |
| | playwright-mcp | 236,687 | 99% | 5.3 | 0.0643 |
| github_navigate_to_file | chrome-devtools-axi | 124,992 | 88% | 4.3 | 0.0807 |
| | chrome-devtools-mcp | 189,841 | 99% | 4.0 | 0.0540 |
| | playwright-mcp | 268,937 | 98% | 6.0 | 0.0794 |

**Input tokens (cache-independent, the robust metric):** chrome-devtools-axi uses **~52% fewer than
Playwright MCP** (51-54% across both tasks) and **~34% fewer than chrome-devtools-mcp**. So axi's
published "57% fewer input tokens" replicates against Playwright MCP, NOT against the
chrome-devtools-mcp it names (there it's ~34%). CLI wrapper injects Bash + on-demand `--help`; MCP
arms inject all tool schemas upfront (report says schemas = ~28.5% of MCP input).

**Cost does NOT follow the token count at n=3** - axi is the priciest per run on wikipedia, ~tied on
github, despite the fewest tokens. Mechanism: MCP arms cache their large static schema prefix at
98-99%, axi's more-variable context (bash output, --help) caches at 88%, so a larger fraction of
axi's fewer tokens is full-price. Per the standing rule, cost at this n is cache noise; the token
COUNT is the real signal. "57% fewer tokens" does not mean "57% cheaper."

**Turns:** Playwright MCP took the most (5.3-6.0 vs axi 4.0-4.3) - its snapshot/interaction model
needs more round-trips. Output tokens also highest (888 vs 559 on github).

**Verdict for THIS box:** it measures efficiency-WHEN-USED (§4), not adoption. axi is a CLI, not an
MCP; the incumbent Playwright MCP is wired into verify-ui-live/e2e and drives real multi-step UI
flows. axi halves input tokens on read-oriented browsing but that did not translate to cost here,
and adopting it means a second browser tool alongside Playwright, not a replacement for it. Worth it
only if input-token pressure on browsing is an actual pain - not demonstrated by the read-browsing
benchmark.

**DECISION UPDATED 2026-09-08 - ADOPTED as the browser tool, replacing the Playwright MCP.** The
user chose context/quota room over the cost wash: the 5-hour quota tracks consumption, the whole
context is re-read every turn, so a ~half-size per-turn context (axi, no MCP schema) is the win the
benchmark's DOLLAR wash hid. Playwright MCP removed from `~/.claude.json`; docs re-pointed
(ENVIRONMENT.md, `verify-ui-live` step 0b + top banner, dev-system REBUILD.md). `ui-check` (DOM
measurement) and repo `e2e` (Playwright library) were never the MCP and are unchanged. Revert recipe
(exact MCP block) lives in `verify-ui-live` step 0b and REBUILD.md. Caveat carried forward: only
axi `start/open/snapshot/screenshot` are verified; the auth-cookie / cert / file:// flows are
first-use-verify, not yet run on a real app.

## Graft (trailhq/nanonets, code-graph context layer) - 2026-09-08, FREE GATE PASSED (first in category to)

`@nanonets/graft` 0.16.0, MIT, 6.3k stars, active daily. Same CATEGORY as graphify (code graph) and
context-mode (context engineering) - but materially more serious. Read-only source review (README,
TELEMETRY.md, package.json); NOT yet run.

**Why it's the strongest in this category, and could beat the subagent baseline where graphify didn't:**
- Tree-sitter graph + real LSPs (pyright/gopls/rust-analyzer/clangd/ts-server) = true symbol
  resolution, and `graft_find_code` returns "source inlined." That directly targets graphify's fatal
  weakness (AST-only, couldn't reach body-level facts, so it lost to `cavecrew-investigator`).
- Graph is gitignored local FILES (like node_modules), no daemon, no embeddings; structural refresh
  is ~3ms and `$0` (no LLM). `--deep` LLM enrichment is opt-in and needs a provider key.
- Offers a PULL mode (6 MCP tools, context paid only when asked) - the on-demand pattern that avoids
  context-mode's always-loaded failure.
- Honest benchmark (cache-aware cost, keyword-floor Opus judge): SWE-bench 33/50 vs cold 27/50, ~42%
  fewer tokens. Vendor+generic, so not adoption evidence for this box.
- Telemetry: allowlist contract, buckets/labels only (no code/paths/queries), `DO_NOT_TRACK`, off in
  CI, opt-out in init. Clean.

**Blocker on THIS box:** won't install. Native tree-sitter grammars need a C toolchain to compile
(`gyp ERR! not found: make`) - the box has NO make/gcc/g++/cc, and Node 24.18 has no prebuilt
binaries for the grammars. Needs `sudo apt install build-essential` (system change) or a Node-20
attempt for prebuilds.

**Concerns if adopted:** `graft init` writes hooks + statusline + `.mcp.json` into `.claude/` (adds to
an already hook-heavy box: caveman/ponytail SessionStart, rtk PreToolUse, autopush Stop), and its
deep-integration mode injects context every prompt + rebuilds every turn - the same shape as
context-mode (+127% here). Selecting the `agents` host also writes user-level `~/.codex/` config
affecting every repo (use `--no-global`). The PULL mode (`graft build` + the 6 tools, no init) is the
safe thing to test.

**Verdict: worth a real test, but gated on installing a build toolchain.** If installed, the cheap
first gate is the FREE structural head-to-head: `graft build` (no init, no wiring) then
`graft ask "<the undo question>"` vs the graphify/cavecrew results above - does LSP reach
`lastTouchedAt`? Only if that passes is the paid axi-harness (Graft-pull vs cold vs subagent) worth it.

**UPDATE 2026-09-08 - installed (user added build-essential) and the free gate PASSED, decisively.**
`graft build` on loop: 736 nodes / 1956 edges / 166 cards, structural, no key, seconds. Same undo
question graded vs loop/CLAUDE.md: `graft ask --source` ranked `restorePatch` (undo-snapshot.ts:47)
and INLINED its body, returning the exact ground-truth line
`patch.lastTouchedAt = snapshot.lastTouchedAt ? new Date(...) : null` (RESTORED) next to
`updatedAt: new Date()` (STAMPED) - a ~2.6k-token bundle, no LLM. This is the body-level fact
graphify STRUCTURALLY COULD NOT reach (AST-only), at ~2.6k of ranked+inlined source vs the
cavecrew-investigator subagent's 37k spent. For the "how does the code work" branch, Graft's CLI/pull
mode (`graft ask --source`, `graft_find_code`) beats graphify outright and is cheaper context than the
subagent. n=1, lexical, structural-only (no --deep).

Recommendation: adopt the CLI/pull mode for code Q&A. Do NOT enable the deep auto-inject hooks
blindly - the every-prompt-inject + every-turn-rebuild shape is the context-mode risk on this
hook-heavy box, and the `agents` host writes user-level ~/.codex/ config (use --no-global/--no-hooks).
Paid axi benchmark (Graft-pull vs cold vs subagent, end-to-end + does the agent choose it) is the
remaining confirmation, not run. Loop test footprint reverted (.gitignore, .ignore, graft/ removed).

**Paid benchmark 2026-09-08: INCOMPLETE - environmental blocker (OOM), not a result.** Tried a
3-arm end-to-end code-Q&A comparison (cold / graft / subagent, undo question, n=2). Only the graft
arm completed: 2 turns, 430 output tokens, correct (reached `lastTouchedAt`) - consistent with the
free gate. The cold and subagent arms did not finish: this box (15 GiB, ~9 GiB already held by the
running fleet) went to <600 MiB free running heavy `claude -p` agent subprocesses, and the runs were
killed for memory. **Finding: heavy agent-vs-agent benchmarks are NOT feasible on this box while the
fleet runs** - the axi harness's own runs are lighter (read-only gh tasks), but a full code-Q&A agent
matrix OOMs. To get the paid confirmation: run it when the fleet is stopped, on a bigger host, or one
single run at a time with memory watched. The free-gate evidence (graft reaches body facts at ~2.6k
tokens vs subagent 37k) stands as the basis; the end-to-end token-win-vs-cold confirmation is still
formally unrun.

## Four repos triaged 2026-09-09 (markitdown ADOPT-utility, tgrep / camofox / an answer-style skill SKIP)

User asked "worth it for our workflow - tokens/efficiency/accuracy" on four GitHub repos. **No axi
bench run: none qualified.** agent-tool-bench measures agent-loop/token A-vs-B claims; these lost (or
won) on triage before a paid run was worth the quota. Loop repo = 272 tracked files (the scale figure
that kills tgrep).

- **microsoft/markitdown** - ADOPT as a utility (not an agent-loop tool, so no bench). Python CLI/lib,
  converts PDF/docx/xlsx/pptx/images/audio/html -> clean Markdown. Real fit: user drops files in the
  Samba inbox (`<WINDOWS_HOME>/inbox`); converting to structured md beats dumping raw text on BOTH
  tokens and accuracy (keeps headings/tables). Zero context cost - invoked on demand. Install
  when a conversion need arises: `uv tool install markitdown`. Not yet installed.
- **microsoft/tgrep** - SKIP. Trigram-indexed grep, drop-in rg replacement, client/server daemon. Its
  51.9x win is on gecko-dev (388K files); our repos are ~272 files where rg is already instant. And
  grep's token cost is OUTPUT size, not scan speed - tgrep changes neither. rtk already owns the grep
  token side. No win at our scale, plus a persistent daemon = overhead for nothing.
- **jo-inc/camofox-browser** - SKIP. Stealth Firefox (Camoufox) REST server to bypass
  Cloudflare/bot-detection when scraping HOSTILE third-party sites. Our browser work verifies OUR OWN
  apps behind OUR OWN Cloudflare Access - no detection to evade. Value prop orthogonal to the workflow.
  (Also: switched to chrome-devtools-axi for this job 2026-09-08.) Its ~90%-smaller a11y snapshots are
  the one interesting bit but not worth adopting a stealth stack we have no use for.
- **ayghri/an answer-style skill** - SKIP for install; cherry-picked instead. Response-shaping skill (10 rules:
  action-first, numbered steps, one next-step, cap lists at 5, no preamble). IS in-category (prompt
  style) but redundant with the always-on caveman (density) + ponytail (scope), and 3 of its rules
  fight the box: #6 specific time estimates = guessing (violates verify-before-claiming), #5
  restate-state-every-turn = token padding, #7 make-wins-visible = anti-terse. Stacking a third
  overlapping style skill = drift + conflict. **Action taken: the GOOD structural parts (lead with
  action, numbered steps, one `Next:` line, minus the 3 bad rules) were encoded into RULES.md
  "Answer shape" instead** - own file, always-on, autopushed, update-proof; caveman is vendored
  upstream (JuliusBrussee/caveman) and gitignored, so editing it there would clobber on plugin update
  and die with the box.

## context-mode (mksglu/context-mode, MCP+plugin) - 2026-09-09, SKIP (hard rtk hook collision)

MCP server + CC plugin attacking tool-OUTPUT bloat: sandbox "think in code" tools (ctx_execute etc.),
SQLite/FTS5 session continuity across compaction. Registers 11 MCP tools + 6 hooks (PreToolUse,
PostToolUse, UserPromptSubmit, PreCompact, SessionStart, Stop). ELv2, source-available. Claims
"nothing leaves your machine" (README line 1524, unverified). HN #1, marketing-heavy (fake
Microsoft/Google/... badges, hosted Insight dashboard).

**Disqualifier (source-verified, not assumed): hard PreToolUse collision with the rtk hook.**
`hooks/core/routing.mjs` `routePreToolUse` returns `action:"modify"` with `updatedInput` on Bash
(lines 769/800/813/915/940/994, e.g. `{...toolInput, cwd}`) plus `deny` on several paths
(682/716/878/932). rtk's PreToolUse ALSO rewrites the Bash command. Two PreToolUse hooks both
emitting a modified Bash tool_input = last-wins clobber in CC: either rtk's token-opt rewrite or
context-mode's redirect is silently dropped, non-deterministically, on the Bash pipeline the phone/RC
workflow rides. (NOT an API proxy like headroom, so RC itself likely survives - but the rtk clobber
alone kills the full install.) It only touches UNBOUNDED commands - bounded `git status`/`ls`/
`git diff --stat`/`git log -N` are allowlisted (routing.mjs:244+) - so the collision is scoped to
grep/find/curl/large-read, which is exactly rtk's turf.

**The "strip PreToolUse" modification doesn't save it.** Keeping PostToolUse+PreCompact+SessionStart+
Stop (event capture, no Bash rewrite - no collision) + the MCP tools removes the CONTEXT-SAVING core
(that IS the PreToolUse redirect), leaving a session-logger + MCP toolbox. Worse, `ctx-upgrade`
re-adds the PreToolUse hook every upgrade ("pulls latest, fixes hooks") = perpetual rtk re-break on an
ELv2 auto-upgrader (the portability-drift the RULES warn against). And the surviving half is
redundant here: session-continuity ~= manual /handoff+/clear; context-saving is marginal-over-rtk
(rtk already trims our worst offenders, Playwright MCP already removed) - same shape as the headroom
verdict.

Also: it does NOT solve our measured problem (the ~19k standing routing tax from 54 skill
descriptions + RULES/ENV); it targets long-session OUTPUT accumulation, "the other half," and pushes
standing context the WRONG way (+11 MCP schemas + SessionStart injection) right after we cut Playwright
MCP for exactly that reason.

Verdict: SKIP. Reversible MCP-only trial (`claude mcp add context-mode -- npx -y context-mode`, no
hooks, no rtk collision) available if the sandbox tools are ever wanted, but expect marginal-over-rtk
and +11 standing schemas. Source clone was shallow/scratchpad - no repo footprint.

## cavecrew-builder: Opus-4-8 vs Sonnet-5 on a bounded edit - 2026-09-09, n=3, SONNET ADOPTED

Question (agent-tool-bench §0): efficiency-when-used + regression (does the cheaper model still
produce a CORRECT surgical edit). Motivated by the "Opus plans, cheaper model executes" pattern
(RULES subagent section) - cavecrew-builder currently inherits Opus.

Setup: bench-github harness, but its 17 tasks are read-only gh queries (wrong workload for an EDIT
agent), so: a local throwaway fixture repo (one `src/util.ts` with a planted bug - `clamp` returns
`max` when `v<min`, should return `min`; `chunk` correct, must stay untouched), REPO_URL repointed
at it (one const, reverted after), a `builder` condition injecting cavecrew-builder's exact prompt
as agents_md/CLAUDE.md, task `fix_clamp`. `--agent claude`, `--model claude-opus-4-8` vs
`claude-sonnet-5`, `--repeat 3`. **Purged workspaces + results.jsonl builder rows between arms** -
the runner reuses an existing `workspace/.git`, so sonnet would have inherited opus's already-fixed
file (the §4 "process isolation is not state isolation" trap, hit live).

| metric (n=3) | Opus-4-8 | Sonnet-5 |
|---|--:|--:|
| correctness pass^3 | 3/3 | 3/3 |
| cost/run | $0.135 | $0.055 (~2.4x cheaper) |
| turns | 6 | 4 |
| output tok | 1050 | 721 |
| duration | 19.7s | 18.9s (~equal) |
| input tok / cache% | 65,981 / 88% | 111,838 / 94% |

Findings: (1) **No regression** - Sonnet made the correct minimal edit all 3, judge (codex/gpt-5.4-
mini) confirmed `return min` + chunk untouched. (2) **Cost win is real** - ~2.4x, driven by Opus's
per-token price, larger than the §7 cache-noise band. (3) **Latency ~equal** - the "cheaper=faster"
intuition did NOT hold here; the win is cost, not speed. (4) Input-token delta is cache noise (§7),
don't read it.

Caveats: n=3, ONE task, a trivial off-by-one - a capability FLOOR, not proof across all edit
difficulty. Harder/ambiguous edits may still favor Opus (and RULES already routes ambiguous work to
the Opus main thread, not a cheap executor). Tools were NOT restricted to builder's real toolset
(the arms had Bash; real builder has Read/Edit/Write/Grep/Glob only, so both self-verified with a
Bash run the real agent can't do) - equal across arms, so the comparison holds, but absolute
turns/tokens are inflated vs the real agent.

Decision: `CAVECREW_BUILDER_MODEL=sonnet` (settings.json env) KEPT - justified for bounded,
fully-specified edits, which is exactly cavecrew-builder's scope ("1 file ideal, 3+ refuse").
Investigator/reviewer already haiku; planning stays Opus (main thread). To harden: add 2-3 harder
edit tasks (multi-line, a subtle logic fix) before treating it as universal.

Update 2026-10-16: the env override never took effect. The plugin's SessionStart hook resolved its root
to `src/` and looked for `src/agents/`, so the builder file never got a `model:` line and inherited the
session model. The caveman plugin was then uninstalled and the three agents copied to `~/.claude/agents/`,
with `model: sonnet` written into `cavecrew-builder.md` directly.

### Follow-up 2026-09-09: harder edits (n=3/task) - quality holds, but the COST WIN SHRINKS with difficulty
Added two harder bounded-edit tasks to the same fixture: `fix_pagecount` (Math.floor->ceil, spot
the off-by-one intent) and `fix_mergeranges` (multi-line: the merge loop never sorts input first;
correct fix adds a sort - requires understanding intent, not a one-token flip).

| task | model | pass^3 | cost/run | out tok | dur | turns |
|---|---|---|--:|--:|--:|--:|
| pagecount | Opus-4-8 | 3/3 | $0.125 | 1206 | 25.2s | 7 |
| pagecount | Sonnet-5 | 3/3 | $0.106 | 1124 | 19.6s | 7 |
| mergeranges | Opus-4-8 | 3/3 | $0.146 | 1718 | 30.2s | 7 |
| mergeranges | Sonnet-5 | 3/3 | $0.088 | 1400 | 26.1s | 7 |

Findings: (1) **No regression on harder tasks either - Sonnet 6/6 = Opus 6/6.** The builder->sonnet
decision holds on non-trivial edits, including one needing real reasoning (add the missing sort).
(2) **The cost advantage is WORKLOAD-DEPENDENT and shrinks with difficulty:** ~59% cheaper on the
trivial clamp fix, only **~28% cheaper averaged across the harder pair** ($0.097 vs $0.135). Sonnet
consumed ~2x Opus's input tokens on the harder tasks (more exploration to reach the same answer),
eating into its per-token price edge. n=3, so cost is cache-sensitive (§7) - treat the margin as
directional; the SHRINKING trend is the durable point, and it directly measures the "cheap model
does more work" mechanism.
(3) **This validates the deterministic-gate contract.** If the harder-task win is already only
~28%, adding an Opus review pass on every diff (~$0.05-0.07) would erase it - so verification must
be a $0 machine gate, model escalation on failure only. Measured, not assumed.
(4) Harness gotcha: an unquoted prompt interpolation in axi's runner means **parens in a task
prompt** (`pageCount(total,size)`) crash the agent launch with `/bin/sh: Syntax error: word
unexpected` and a 0-byte/0-turn FAIL - reword prompts to avoid `()`. Cost a false "opus failed"
reading until stderr.txt was read (§3: read agent_output/stderr before believing the table).

### Follow-up 2026-09-09 #2: the PIPELINE (Opus-plan -> Sonnet-exec) vs Opus-SOLO - the split LOSES ~5x on one task
The earlier arms measured executor-model A/B (sonnet vs opus doing an edit from the raw task) - NOT
the orchestration pattern. Measured the real pipeline, n=1 (directional, §8; box OOMs on a 6-run
claude -p script so ran one at a time), same 2-bug task (pageCount floor->ceil + mergeRanges missing
sort), graded by a deterministic node assertion (dogfooding the gate).

| pipeline | correctness | cost |
|---|---|--:|
| Opus solo (plan+do in one) | PASS | $0.047 |
| Opus plan -> Sonnet exec | PASS | $0.233 (plan $0.148 + exec $0.085) |

**The split is ~5x MORE expensive for a single bounded task.** Mechanism: producing a *precise
executable ticket* cost Opus 3x the whole solo edit ($0.148 vs $0.047) - specifying every edit +
acceptance assertion is more reasoning and a long structured OUTPUT (3645 chars, opus-priced) than
a terse 4-turn edit; then Sonnet's exec stacks on. For ONE small task, Opus-solo wins decisively.

**When the split DOES pay** (none true for a single small edit): (1) the plan AMORTIZES - one ticket
drives MANY or PARALLEL executions; (2) the task is big enough that Opus's EXECUTION (not planning)
dominates, so moving the bulk edits to a 1/5-price model beats Opus doing them; (3) CONTEXT
ISOLATION - keeping a huge execution out of the Opus thread (a context win, not a token win). The
naive "cheaper model executes = cheaper" ignores the Opus planning tax, which for small tasks is the
whole cost.

Corrects the framing: builder->sonnet is still right when a ready brief EXISTS (user-given detail,
or a plan Opus made anyway); manufacturing a detailed ticket solely to hand off one small edit is a
net loss - just do it inline.

## Paseo + cross-subscription dispatch (2026-09-15, n=1 real feature) - ADOPTED, with one hard rule

`getpaseo/paseo` 0.8.0 (daemon facts + pairing in ENVIRONMENT.md "Paseo"). Tested by building a real
Aro feature (archive routines: migration + 11 files) with **Codex gpt-5.6-terra as the lead** in a
Paseo git worktree, Claude Sonnet 5 as reviewer, throwaway `aro_test` DB, UI driven headless.

**Result: it works, and it moves the spend off the Claude plan.** One 17-minute run delivered the
feature (48 test files / 487 tests green, tsc 0, migration verified on the copy, real `aro`
untouched). Codex spent **23% of its 5-hour limit** (weekly 98% -> 95%); the Claude plan moved
72% -> 79% of its 5-hour window, and that figure includes the supervising Opus session, not just the
review.

**The hard rule, and the reason this entry exists:** the Claude REVIEWER agent burned **1.41M
context tokens over 24 turns** exploring the repo for a 190-line diff. Same review with the diff
inline, one lean turn: **23k** (~60x less). Never let a Claude agent explore a diff it can be handed
-> `review-diff`, owned by `model-tiering` (which also carries the per-turn context floors: 36,938
normal / 6,449 with `--tools "" --setting-sources "" --strict-mcp-config`, and an always-on ha-mcp
at 1,115/turn, since moved to on-demand `--mcp-config` loading).

Other measured facts from the run:
- **`create_agent` takes ONE combined `provider` string** (`"claude/claude-sonnet-5"`) and no separate
  `model` field. A lead passing a profile's fields literally burns 2 launch attempts. Installing
  Paseo's own orchestration skills cut a repeat run 216s -> 129s and 4 -> 2 attempts, but did not
  eliminate them. Cost is Codex tool calls only, no Claude tokens.
- **Profiles with "when to use" notes DO drive selection**: the Codex lead read them and picked the
  review profile unprompted. A profile with no `modeId` makes it guess a mode the other provider
  lacks (Codex tried to pass its own `auto` to Claude); set `modeId: plan` on a review profile.
- **A lean reviewer invents bugs when the prompt is noisy** (a 111KB generated snapshot in the diff
  produced 2 confident non-bugs). Treat lean findings as leads; keep an exploring reviewer for risky
  changes. Both reviewers independently found the same real gap (server actions could still mutate an
  archived routine), so the cheap one is not weaker on in-diff correctness.
- n=1 on the feature, n=2-3 on the context measurements. Quality of an OpenCode-Go-class lead is
  untested (no subscription yet).

## rtk for OpenCode 2.x (2026-10-16): not measured, stays off

- The question: how efficient is rtk when used (a hook, so OpenCode never chooses it; it always runs).
- State: the 1.x plugin `rtk init --opencode` writes fails to load on OpenCode 2.x (a WARN in its log only), so rtk had
  filtered nothing there since the upgrade. A 2.x port (`~/.claude/scripts/rtk-opencode.ts`,
  `ctx.shell.hook("create.before")`) rewrote a live `git log` (n=1), then was unlinked. Upstream rtk 0.50+ ships its own
  `rtk init --opencode-v2`; this box has 0.43.0.
- Why off: rtk issues #582 (+18% cost in Claude Code), #1351 (more tokens with Codex on terminal-bench) and #3175 (an
  open report for Claude Code) all describe the same loop: filtered output, then raw re-runs and extra tool calls.
  OpenCode's models are weaker than the ones in those reports.
- Not measured: the axi harness has no OpenCode backend (`bench-github/src/cli.ts`: `--agent codex|claude`).
- Would settle it: an OpenCode backend in the harness, then `bench-github` tasks at n=3 with and without the link,
  judged on turns and correctness. The bar: fewer turns and no lost correctness; tokens are indicative only at n=3.

## review-diff reviewer: Sonnet 5.5 medium vs high vs Opus medium (2026-10-20, n=17 real bugs x 2 runs) - SONNET MEDIUM STAYS

The reviewer recall eval (`review-eval/`): each case is the commit that introduced a real bug in our repos. Judged by
Haiku twice per review with judge v2 (reason first, verdict last; same function and mechanism counts, file name not
required). Judge v1 (verdict first, same file required) undercounted: it said NO while its own reasoning described the
bug; v2 agrees with 13 of 13 hand labels (`review-eval/labels.json`) and splits far less (0 to 2 vs 2 to 7).

| arm | caught (v2) | tuning / held-out | avg in / out tokens | avg time | est. cost per review |
|---|--:|--:|--:|--:|--:|
| sonnet, medium | 17/34 (50%) | 12/22, 5/12 | 13.5k / 4.1k | 37 s | about $0.07 |
| sonnet, high | 18/34 (53%) | 12/22, 6/12 | 13.5k / 7.0k | 59 s | about $0.10 |
| opus, medium | 20/34 (59%) | 13/22, 7/12 | 13.5k / 5.1k | 55 s | about $0.16 |

- **Noise:** an arm's two runs disagree on 2 to 3 of 17 cases; a single run's total moves by up to 2.
- **Decision: keep Sonnet at medium** (the `review-diff` default). Opus leads by 3 catches, but its per-run totals
  (11, 9) nearly overlap Sonnet's (9, 8), at about 2.3x the cost; Sonnet high adds 60% time for 1 catch. Rerun with
  more cases before switching. This says nothing about Opus for building or debugging.
- **Prompt round 1** (seven bug-class questions, `review-eval/prompts/p1.txt`): tuning 12 to 16, held-out 5 to 5, +29%
  output tokens. It gains exactly on the classes it names and nothing elsewhere, so by the both-sets rule it does not
  ship. The prompt writer had seen the held-out cases earlier in the session (not blind).
- **Prompt round 2** (a general second pass: trace an input, name removed behavior, state assumptions,
  `prompts/p2.txt`): tuning 12 to 11, held-out 5 to 6, +48% output tokens. Inside the noise: not shipped.
- **Tuning stopped after two rounds** (the eval post's stall rule); the six bugs no arm catches, by cause: a React hook
  after an early return (0/10: a lint rule catches it, `react-hooks/rules-of-hooks`; only shelf's lint has it), a
  node-cron schedule without a tolerance (0/10: library knowledge; a mechanical check fits), a removed empty-day path
  (0/10: needs intent, so the plan or a REVIEW.md line), a learned-memory feedback loop (0/10), a first-match transfer
  leg (2/10, domain), a ref-only lock timer lost on an iOS page discard (2/10, platform). The next gains are checks
  and per-repo REVIEW.md lines, not prompt wording.

