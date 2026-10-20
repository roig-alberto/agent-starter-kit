# Plan review

A plan review happens before code, when a wrong choice costs one message instead of a rewrite. The same
method reviews a repo's `ARCHITECTURE.md` against its code (the weekly architecture review).

## The reviewer's brief

Give a fresh read-only subagent the plan file path, the repo's `AGENTS.md`, `ARCHITECTURE.md` and
`CODEMAP.md` when they exist, and this brief:

> Review this plan before any code is written. Read only the plan, the repo docs named, and the code a
> traced case passes through. Do not edit files, do not delegate, do not load the review skill.
>
> 1. State the problem, the person affected, the intended result, how success is measured, the scope and
>    the main tradeoff. Report any the plan leaves unclear.
> 2. Trace one real case from input to what the person sees: who owns each step, validation, state
>    changes, side effects, failure, retry, cleanup. Treat the plan's claims about current code as
>    unverified until you read the code.
> 3. Check the plan against every rule in `ARCHITECTURE.md` "System rules"; a plan that breaks one is a
>    Blocking finding naming the ID (RULE-n), unless the plan proposes changing that rule on purpose.
> 4. Challenge the design: boundaries, data, migration and rollback, partial failure and concurrency, auth
>    and untrusted input, and how each acceptance check is proven. Look for a simpler design with the same
>    result and proof.
> 5. Check size ("too much"): name every part the goal does not need yet (a layer, a setting, an
>    abstraction with one user, a phase for a later need) and what removing it saves.
> 6. Return findings and material questions, then a verdict and what you could not verify. Do not
>    rewrite the plan or review code style.

For an architecture review, replace the plan with `ARCHITECTURE.md` and ask in step 2 whether the code
still matches each part, ADR and main flow, and in step 5 whether any part has grown bigger than its job.

## Material questions

Report a question only when two capable builders could answer it differently in a way that changes users,
data, interfaces, security, cost or proof. Each one gets a recommended answer when the evidence supports
one.

- **Blocking:** building should not start without the answer.
- **Important:** the plan should record the answer; the recommended default is safe meanwhile.

Leave out questions about style, choices safely local to one builder, out-of-scope work, and scale the
plan never claims.

## Findings

- **Blocking:** the choice is unsafe, contradicts the goal or the current code, or cannot recover from an
  important failure.
- **Important:** the plan allows materially different builds, or leaves a real risk in behavior, security,
  operations or proof. A "too much" item is Important when removing it changes the phases.

Each finding names its place in the plan, the failure or ambiguity, its effect, the evidence and the
smallest fix. The priority and confidence rules in `SKILL.md` still apply; Blocking maps to Must fix and
Important to Should fix for the verdict.

## Verdict

`Approve` when no Blocking or Important item remains; `Request changes` for a fixable one; `Blocked` when
the context, the code evidence or an independent reviewer is missing. Never approve because the plan is
long or every template section is filled.
