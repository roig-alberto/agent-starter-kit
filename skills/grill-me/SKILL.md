---
name: grill-me
description: >-
  Interview the user relentlessly about a plan, design, or feature until both sides share one
  understanding of it, in rounds of plain-word questions, each with a recommended answer. Use when the user
  wants to stress-test a plan before building, says "grill me", "interview me", "are we sure?",
  "stress-test my thinking", invokes /grill-me, or uses any 'grill' trigger phrases; also when an ask
  is missing who, why, or what done looks like and you are about to fill the gaps silently. NOT for
  writing the plan file and phases (use plan) or for a whole feature from ask to close-out (use
  one-shot, which calls this skill).
---

# grill-me

Interview the user about every decision in a plan until both of you share one understanding of it. It
prevents two failures: a build that trips over a decision nobody made, which costs a rewrite, and a
question the user cannot follow, which gets a guessed answer or "i do not understand".

## Steps

1. **Find the facts yourself.** Read the project's `AGENTS.md` (the same file as
   `CLAUDE.md`), `FEATURES.md`, the plan or ask, and the code it touches. For an area you have not mapped, send a read-only subagent (Explore or
   `cavecrew-investigator`) and keep asking the questions that do not depend on its answer: a running lookup holds
   back only the questions downstream of it. Facts (what
   the code does, what exists, what a library supports) are your job. Decisions (what to build, what to
   give up) are the user's.
   Done when: you hold a list of open decisions, and none of them is a fact you could look up.
2. **Write your hypothesis.** In one plain sentence, say what you think the user wants, and in a second
   sentence what is still missing (who it is for, why now, what done looks like, the hard limit).
   Done when: the hypothesis is in your reply, so the user can correct it before any question.
3. **Lock the foundations first on a new project or a fresh design.** Follow the order in "Foundations"
   below before you walk the feature tree.
   Done when: the stack, the reference apps, the one excellent thing, and the parked wants are settled.
4. **Ask in rounds, shaped as in "How to ask".** Map the open decisions as a design tree: each decision
   branches into the ones that hang off it. The *frontier* is every decision whose prerequisites are
   settled. Ask the whole frontier in one round, numbered, then wait. A question whose answer depends on
   another question still open belongs to a later round. Each answer moves the frontier outward;
   recompute it before the next round.
   Done when: the frontier is empty: every branch visited, nothing silently assumed.
5. **Ask only material questions.** A question is material when two capable builders would build
   different things depending on the answer (what the user sees, the data, security, cost, or how it is
   proven). Decide small, reversible details yourself and list them as assumptions.
   Done when: no open decision is left that would change what gets built.
6. **Restate the scope and get an explicit yes.** Write it in plain words: what we build, what we do not
   build, how we will know it is done (the check), and the riskiest part. Ask the user to confirm or
   correct it. If they correct it, fold the change in and restate again.
   Done when: the user says yes to the restated scope. "Sounds good", "whatever you think", and silence
   are not a yes to the restate (see Gotchas).
7. **Hand back.** Called by `one-shot` or `plan`, return to that step with the confirmed scope. Run on its
   own, stop the turn, and offer the next step (`plan` for phased work, `one-shot` for a feature on an
   existing app) without starting it.
   Done when: the confirmed scope is in the reply and no build work has started unasked.

## How to ask

Every question uses this shape:

```
Round 2

Q1. When a run fails at night, should the app retry it by itself?
- Retry once, then tell you in the morning (my recommendation). You wake up to fewer failed cards, and
  a second failure still reaches you.
- Never retry. Every failure waits for you, so you see every problem, but you start the day with a pile.
Example: the 02:00 dependency check fails because the network blinked. With a retry it passes at 02:05.

Q2. ...

Answer per number ("1 yes, 2 no, keep both"), or "yes" to take every recommendation.
```

- Write the question so "yes" takes your recommendation. Agreeing should never mean typing "no".
- Put your recommendation first, and say why in one sentence.
- Each option says what changes for the user (what they see, do, wait for, or pay), not how the code
  differs.
- Give a concrete example whenever an option is abstract (a real screen, a real card, a real day).
- Use everyday words. Define a technical term the first time, or replace it with what the user would
  notice. Two or three options at most.

## Foundations (new project or fresh design)

Lock the foundations that are expensive to revisit, in this order, before you walk the feature tree.

1. **Platform and stack, especially the UI toolkit.** Do not stop at "Tailwind"; pin the actual component
   layer (for example daisyUI, shadcn, or a headless library) now, so it is never re-litigated mid-build.
   Pin the framework, the database and ORM, auth, and the deploy target the same way.
2. **Reference apps.** Ask "Which 1-3 existing apps do you admire, and what *specifically* about each?"
   These anchor the visual direction and reliably surface features the user actually wants. For a finance
   app that meant YNAB's "give every euro a job", Monarch's net-worth trend, and Copilot's
   auto-categorization. Capture them, because they feed the design step.
3. **The one thing that must be excellent**, and, for apps used infrequently, **how effortless the core
   flow has to be to keep someone coming back.** Treat ease of use as a first-class requirement from the
   start, not as polish.
4. **Adjacent "tempting but out-of-scope" wants.** Park each one in a backlog with a reason, so it neither
   creeps into v1 nor gets forgotten.

Resolving these up front is what stops every later question from tripping over an unmade foundational
decision.

## Rules

- Ask the whole frontier per round and wait for the answers. A round is only questions that are answerable
  now; never a question whose options would change after another answer in the same round.
- Give your recommended answer with every question. The user can accept it in one word, which keeps the
  interview fast.
- Never cap the number of questions. Understanding is the stopping condition, never a count; the user
  prefers over-clarifying to a rebuild.
- When the user answers in convention words ("scalable", "the standard way", "clean"), ask what they would
  want if they did not have to justify it to anyone. Convention answers hide the real want.

## Red flags

- A numbered list of options with jargon and no example. The user answered "i do not understand 1, 2, 4"
  to exactly that; see `references/history.md`.

## Gotchas

- **The user says "yes" to a question or a round.** That takes your recommendation (every one in the
  round); record it and move on. A partial answer settles only the numbers it names; ask the rest again
  in the next round.
- **The user says "whatever you think" or "sounds good" to the restate.** That delegates, it does not
  confirm. Re-ask with two concrete options, or ask "Anything you would change?".
- **The user says "i do not understand".** Re-ask the same decision with fewer options, plainer words,
  and one concrete example. Never repeat the same wording.
- **Several rounds pass and you still cannot predict the next answer.** Something foundational is
  missing. Say so and ask whether to step back to the goal.
- **No user is there to answer** (an Agent Factory step, a loop, a headless `claude -p` run). Do not
  wait and do not interview. A decision that is cheap to undo (a name, a layout detail, a model for a
  step): take your recommendation and list it as an assumption in the report. A decision that is hard
  to undo (production data, a schema, publishing, deleting, anything on the NAS): leave it as an open
  question with your recommendation in the report, and keep working on everything it does not block.

## References

- `references/history.md`: the past chats behind the plain-words rule and the red flags.
