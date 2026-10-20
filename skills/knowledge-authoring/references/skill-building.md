# Building and evaluating a skill

Read this when you draft a new skill, run test prompts against one, grade and benchmark it, or tune its
description. It is the measured loop that came from Anthropic's skill-creator (now part of knowledge-authoring).
The house rules in `SKILL.md` and `references/skill-style.md` win over anything generic here.

This loop creates new skills and improves existing ones through a measured loop: draft the skill, run
realistic test prompts with and without it, let the user review the outputs in a viewer, and revise. It
prevents the usual failure of a skill that reads well but was never run, or that only works on the three
examples it was tuned against.

Figure out where the user is in the process and join there. Someone who says "I want to make a skill for X"
needs the interview and a draft; someone with a draft can go straight to the eval loop. If the user says "I
don't need to run a bunch of evaluations, just vibe with me", do that instead. Match your vocabulary to the
user: "evaluation" and "benchmark" are usually fine, but explain "JSON" and "assertion" unless the user
clearly knows them.

## Steps

1. **Capture intent.** Ask what the skill should enable, when it should trigger, what output it produces,
   and whether it needs test cases. If the conversation already contains the workflow ("turn this into a
   skill"), extract the steps, tools, and corrections from it first and have the user confirm. The interview
   questions and research tips are in `references/writing-skills.md`.
2. **Write the draft SKILL.md.** Fill in `name`, a slightly pushy `description` that carries every "when to
   use" cue, and the body. Explain the why instead of shouting MUST, because a model that understands the
   reason generalizes better. The anatomy, progressive disclosure, and writing patterns are in
   `references/writing-skills.md`.
3. **Write two or three test prompts** that a real user would type, confirm them with the user, and save
   them to `evals/evals.json` without assertions yet. The schema is in `references/eval-schemas.md`.
4. **Run every test case with the skill and a baseline in the same turn.** The baseline is no skill for a
   new skill, or a snapshot of the old version (`cp -r <skill-path> <workspace>/skill-snapshot/`) for an
   improvement. Results go in `<skill-name>-workspace/iteration-N/eval-<name>/`. Launching both at once
   makes them finish together, so the comparison is fair.
5. **Draft assertions while the runs are in progress**, and explain them to the user. Save them to each
   `eval_metadata.json` and to `evals/evals.json`.
6. **Save timing as each run completes.** Write `total_tokens` and `duration_ms` from the task notification
   to `timing.json` in the run directory, because the notification is the only place they exist.
7. **Grade, aggregate, analyze, and open the viewer.** Grade with `agents/grader.md`, aggregate with
   `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`, do an analyst pass with
   `agents/analyzer.md`, then launch `eval-viewer/generate_review.py`. The exact commands are in
   `references/eval-loop.md`.
8. **Read `feedback.json` and improve the skill.** Generalize from the feedback instead of overfitting to the
   examples, cut instructions that waste the model's time, and bundle any helper script that every run wrote
   for itself. Rerun into `iteration-<N+1>/` with `--previous-workspace`, and stop when the user is happy,
   all feedback is empty, or progress stalls.
9. **Optimize the description** once the skill is in good shape: build 20 realistic trigger queries, have
   the user review them in `assets/eval_review.html`, then run `python -m scripts.run_loop` in the
   background. See `references/description-optimization.md`.
10. **Package the skill** with `python -m scripts.package_skill <path/to/skill-folder>` only if the
    `present_files` tool is available. See `references/packaging-and-environments.md`.

Add these steps to your TodoList if you have one. In Cowork, specifically add "Create evals JSON and run
`eval-viewer/generate_review.py` so human can review test cases" so the viewer step is not skipped.

## Rules

- Run the scripts from the knowledge-authoring directory (`cd ~/.agents/skills/knowledge-authoring`) with `python -m scripts.<name>`. The modules import each
  other as a package, so running them by file path breaks the imports.
- Generate the eval viewer before you evaluate the outputs yourself. The point is to put the outputs in
  front of the human as early as possible.
- Use `generate_review.py` for the viewer and never write custom HTML. The viewer already handles outputs,
  previous iterations, grades, and feedback.
- Use the `text`, `passed`, and `evidence` fields in every `grading.json` expectation, never `name`, `met`,
  or `details`. The viewer reads those exact field names.
- Check programmatically verifiable assertions with a script instead of eyeballing them. A script is faster,
  more reliable, and reusable across iterations.
- Do not force assertions onto subjective outputs such as writing style or design quality. Those need human
  judgment in the viewer.
- Do not use `/skill-test` or any other testing skill. This loop is self-contained.
- Pass the model ID that powers the current session to `run_loop` with `--model`. The trigger test must
  match what the user actually experiences.
- Never create a skill that contains malware or exploit code, or whose intent would surprise the user if
  described. A roleplay skill is fine; a skill for unauthorized access or exfiltration is not.

## Gotchas

- The viewer cannot open a browser in a headless or Cowork session. Pass `--static <output_path>` to write a
  standalone HTML file; "Submit All Reviews" then downloads `feedback.json`, which you copy into the
  workspace.
- A simple one-step query such as "read this PDF" does not trigger any skill, because the agent handles it
  directly. Write trigger evals that are substantive and multi-step, or they measure nothing.
- A should-not-trigger query that is obviously unrelated tests nothing. Use near misses that share keywords
  with the skill but need something else.
- An installed skill path may be read-only. Copy the skill to `/tmp/skill-name/`, edit there, keep the
  original `name`, and package from the copy.
- `scripts/quick_validate.py` rejects a description with angle brackets or over 1024 characters, and any
  frontmatter key outside `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`.
- On this machine `references/skill-style.md` caps a SKILL.md body at 150
  lines, which is stricter than the generic 500-line guidance in `references/writing-skills.md`.

## References

- `references/writing-skills.md`: read when interviewing the user and drafting or restructuring a SKILL.md.
- `references/eval-loop.md`: read when running test cases, grading, launching the viewer, reading feedback,
  iterating, or doing a blind comparison.
- `references/description-optimization.md`: read when improving a skill's triggering with `run_loop`.
- `references/packaging-and-environments.md`: read when packaging, or when working in Claude.ai or Cowork.
- `references/eval-schemas.md`: read for the JSON shapes of `evals.json`, `grading.json`, `benchmark.json`, and
  the other files the scripts and viewer expect.
- `agents/grader.md`: read when spawning a grader to evaluate assertions against outputs.
- `agents/comparator.md`: read when doing a blind A/B comparison between two outputs.
- `agents/analyzer.md`: read when analyzing benchmark results or why one version beat another.
