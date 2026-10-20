---
name: plain
description: >-
  Re-explains something the user did not follow: backs up, adds the context they were missing, and says it
  again in plain words. Use when the user says "I don't understand", "what do you mean", "what is this",
  "what is the purpose of X", "explain that again", "wait, what", "you lost me", or quotes part of your
  reply back with a question. NOT for explaining how code works (use the code-question row in the router)
  or for a decision the user has not made yet (ask it with a recommendation).
---

# Plain

Wait: the user stopped following. Back up to where they got lost, give the context they never saw, and say it
again in the reply style of `~/.claude/RULES.md` (the shared rules every agent loads). It prevents the usual
failure: a shorter version that is just as unclear, because it cut words instead of adding the missing premise.

## Steps

1. **Find what lost them.** If they quoted a passage, that is the target; otherwise it is your last reply. Ask
   yourself which premise they never saw: the problem it solves, where it fits, or a word you invented.
   Done when: you can name the missing premise in one sentence.
2. **Re-say it.** First what it is and why it matters to them, then the point. Use the words the repo's
   `GLOSSARY.md` uses, or everyday words; define any other term or drop it. Give one concrete example from
   their own work. Do not repeat the parts they already understood.
   Done when: every term is defined or replaced, and the reply answers "what is this, and why should I care".
3. **If you misread their earlier message,** say so in one line and answer what they meant instead.
   Done when: the reply addresses their actual question.

## References

- `references/history.md`: the requests that created this skill and where the idea came from.
