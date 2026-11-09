# Bitter lesson: debugging

Why each tagged line in `SKILL.md` exists, and when a "soft" line may go. Read only when evaluating the skill,
never during a debugging session. Tags: `invariant` keeps the line for good (a feedback signal, a fact about
this box, or a rule of the user's); `soft` is reasoning coaching a stronger model may not need. Checked by
`~/.claude/scripts/bitter_lesson.py` through `knowledge-lint.py`; plan in `~/.claude/BITTER-LESSON-PLAN.md`.

| Item | Tag | Why | Review | Delete when | Ablation |
|---|---|---|---|---|---|
| 1. Build the red command | invariant | The red command is the feedback signal the whole loop runs on. | | | |
| 2. Read the error verbatim | soft | Coaching: quote output, cut inputs one at a time. A strong model may do it unprompted. | 2027-04-27 | A with/without run on real debugging prompts shows the same quoting and minimizing. | |
| 3. Rank 3 to 5 guesses | soft | Coaching against anchoring on the first guess. | 2027-04-27 | A with/without run shows several ranked guesses either way. | Opus 2026-10-27: no difference (user graded 20 blind pairs, 15 same, the rest split both ways); Sonnet, Haiku and OpenCode Go models not tested, so kept. |
| 4. Instrument one prediction | soft | Coaching: one change per run, tagged temporary logs. | 2027-04-27 | A with/without run shows one change per run either way. | |
| 5. Fix the root cause, test-first | invariant | A test that fails without the fix is a feedback signal. | | | |
| 6. Prove it and clean up | invariant | Rerunning the red command is the proof the user asks for (RULES.md non-negotiable 1). | | | |
| Rules: label every claim | invariant | The user's reporting rule, not model coaching. | | | |
| Rules: pick the layer | invariant | Facts earned on this box's apps (store-first, count-the-rows). | | | |
| Rules: redact | invariant | A safety rule for real secrets in this box's logs. | | | |
| You want to fix before reproducing | soft | Repeats step 1 as a reminder. | 2027-04-27 | Step 1 alone holds in a with/without run. | |
| You changed three things | soft | Repeats step 4 as a reminder. | 2027-04-27 | Step 4 alone holds in a with/without run. | |
| The urge to refactor mid-debug | soft | Scope coaching; RULES.md already says touch only what the task requires. | 2027-04-27 | A with/without run shows no mid-debug refactors. | |
