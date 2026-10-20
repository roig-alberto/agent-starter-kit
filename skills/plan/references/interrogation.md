# Interrogation (mode 1)

This is the most important mode. The goal is to extract every detail the user has not thought about yet.
Most feature requests arrive underspecified, so find the gaps before they become bugs or rewrites.

## How to interrogate

Run the questions through `grill-me`: one plain-word question per message, a recommended answer with
each, worded so "yes" takes the recommendation, and facts looked up by you rather than asked. The
AskUserQuestion tool can carry up to 4 questions per call; that is a tool limit, NOT a budget, and the
user's standing rule is one question at a time. Ask as many rounds as needed. The user's standing
preference is to over-clarify rather than rebuild: there is no cap on total questions, and understanding,
never a count, is the stopping condition. Do not move on until you are confident you understand the full
picture.

**Ask only material questions.** A question is material when two capable builders would build different
things depending on the answer, in a way that changes what the user sees, the data, interfaces, security,
scale, cost, compatibility, or how it is proven. Skip questions that are stylistic or safely local to the
implementation; decide those yourself and list them as assumptions.

**Be adversarial.** If the user says "add a settings page", do not just accept it. Ask what settings, who
can access them, what happens to existing users, what the validation rules are, and what the error states
look like. If an answer is vague, push back. If the design has a flaw, say so directly.

**Push back on bad ideas.** If the user wants something that violates engineering best practice, creates
unnecessary complexity, or will cause pain later, say so, explain why, and propose an alternative. That is
being responsible, not rude; the user explicitly wants disagreement when it is warranted.

## The checklist: what they have not mentioned

The most important questions are the ones the user did not think to answer:

- Edge cases and error states.
- Data model implications: new tables, columns, indexes, migrations.
- Authorization and access control.
- Backwards compatibility: existing data, existing users, existing API consumers.
- Concurrency and race conditions: what happens if two requests hit this at once?
- Performance and scale: N+1 queries, unbounded result sets, missing pagination, hot paths.
- Limits, failure and success, for every outside call (an API, a model, a CLI, git push, an alert channel):
  - Rate limits and budgets: what happens when a rate limit, a usage window, a daily token cap or a spend cap
    is hit, before the start and halfway through? Does the work wait and resume, skip and tell the user, or
    fail? Ask what the call reports live: Claude over ACP reports only the conversation size during a turn and
    its cost at the turn's end (Agent Factory D146), so a "total tokens" cap cannot stop a run halfway.
  - Failure: what the user sees, whether partial work is kept or rolled back, how many retries with what
    backoff, and whether a retry is safe to repeat (idempotent). A retry must not overlap itself or a manual
    action on the same item.
  - Success: what is recorded and what moves forward (a "last seen" marker, a cursor). Move it only after a
    real success, never after a failure or an unreadable result.
  - Restart: state kept only in memory dies with the process; say what survives a restart or a deploy.
  - The alert path itself: a failed notice is silent unless something checks it. On this box `tg-alert`
    failed for weeks from a file permission before anyone noticed.
- This box's own traps (each one has cost real time here):
  - Time: the Europe/Madrid zone and its clock change; timers drift on WSL2 (the node-cron facts are in
    `~/.claude/ENVIRONMENT.md`); a run that fell due while the server was down is caught up or skipped, by choice.
  - Where a write lands: in apps whose dev and prod share one database (FLEET.md "Database:" per app), a dev write is a prod write.
    How is it proven without touching real data (skill `testing`)?
  - Backups: new data (a volume, a file, a secret) reaches the NAS backup, and a restore of it has been tried.
  - The event loop: anything slow (a build, many fetches, a scan) runs in a child process or a worker, never in
    the server's thread. A 25-second snapshot build would have frozen Agent Factory.
  - Untrusted text in front of a model (chat excerpts, outside repos, issues, web pages) goes inside a block
    marked as data, and the block cannot be closed from inside it.
  - Host users and file modes: which user runs it, and can that user read and write what it needs?
  - Retention: what is deleted, when, and what keeps the disk from filling (snapshots, trash, logs, worktrees).
  - The user's tap: what runs by itself and what waits for approval, above all anything that spends money or
    quota or writes to something shared.
  - Host paths, systemd units and secrets outside `.env`: load skill `portability`.
- Validation and input handling: what is the contract at every boundary?
- Observability: how will anyone know this broke in production (logs, metrics, alerts)?
- Security: injection, secrets handling, PII, rate limiting, audit trails.
- Testing strategy: what proves this actually works, and at what level (unit, integration, e2e)?
- Rollout and rollback: a feature flag? the migration order? can it be undone safely?
- Usability fit: is this the *simplest* thing that works for how often the app is actually used? An
  infrequently used app rewards an effortless flow over a powerful but fiddly one, so weigh every new
  control against the cost of relearning it on each visit.

You do not need to ask about every item; use judgment about what is relevant to *this* feature. But scan
the whole list every time, because the dangerous gaps are the ones nobody is thinking about.

If a tempting *adjacent* feature surfaces mid-interrogation (related, but not the thing being built), do
not absorb it into scope. Park it in the plan's Non-goals or backlog with a one-line reason.

## Calibrate the depth

Match the interrogation to the size of the work. A one-line copy change does not need a concurrency
analysis; a new payments flow needs all of it. If the request is genuinely trivial, say so and offer to
skip straight to implementation rather than performing ceremony.
