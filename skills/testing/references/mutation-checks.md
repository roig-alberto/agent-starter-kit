# Mutation checks and completeness tests

A test proves a guard only if it goes red when the guard is gone. Check that with one mutation per guard, and check
a "move everything" refactor with a completeness test, not a hand inventory.

## One mutation per guard: `scripts/mutate.sh`

```bash
~/.agents/skills/testing/scripts/mutate.sh <file> '<exact old text>' '<exact new text>' -- npx vitest run <test file>
```

- Exit 0 = the test went red on the mutant (good); 1 = it stayed green (a weak test: fix the test); 2 = the mutation
  could not be applied or the file could not be restored.
- The replacement is literal and must match exactly once. Hand-written `sed` or `perl -pi` mutations silently did not
  apply here (parentheses, `?` and `|` in code are regex syntax), and "still green" read as a weak test.
- It runs the test under `systemd-run --user --scope -p MemoryMax=2G timeout 120` and always restores the file. An
  unbounded mutation loop crashed the box twice (2026-10-25/26).
- Run an unmutated control first: the plain test command must be green, or every mutant "is caught".

## A completeness test before trusting an inventory

When moving "everything" of a kind into a registry (all prompt builders, all routes, all settings), write the test
that enumerates the real set first (every exported `*Prompt` must be in the registry; every old constant name must be
gone) and let it find the list. A read-only helper's inventory missed 12 builders and called two live constants dead;
the completeness test caught all of it (agent-factory, 2026-10-18).
