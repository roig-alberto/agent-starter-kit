# Code review

## Scope commands

Default target, the repo's whole local change (run from the repo root):

```bash
base=$(git merge-base HEAD master)        # or main; the repo's default branch
git log --oneline "$base"..HEAD           # commits on this branch
git diff "$base"                          # those commits plus staged and unstaged work
git ls-files --others --exclude-standard  # untracked files are part of the change
```

`review-diff` collects the same thing: `review-diff --base master` for a branch, plain `review-diff` for
uncommitted work only. A named target (a commit, a file, a ref range) replaces the default. Check that the
ref resolves (`git rev-parse <ref>`) and the diff is not empty before starting a reviewer.

## The reviewer's order

The `review-diff` prompt already asks for this; a subagent reviewer gets it in its brief.

1. **Broad view.** Does the change belong, match what was asked, and deliver one reviewable result? A
   mismatch is reported before any detail.
2. **Main behavior.** The files and flows that deliver the result: failures, security boundaries,
   interfaces, compatibility, migrations, concurrency.
3. **Every human-written changed line**, with enough surrounding code to judge it. For generated files,
   check the source and spot-check the output.
4. **The proof.** Tests cover the changed behavior and its failure paths, assert what a caller can observe,
   do not copy the implementation's logic, and would fail if the code broke. Each plan `AC-n` has a check that proves
   it; one without proof is a finding that names the ID.
5. **The repo's rules.** A change that breaks a rule in `ARCHITECTURE.md` "System rules" is Must fix and
   names the ID (RULE-n). Pass that file as `--context` when the repo has one.
6. **Specialist gaps.** Security, privacy, concurrency, accessibility. A risk the reviewer cannot judge is
   listed under Unverified; it is `Blocked` when it could break a rule and nobody qualified covers it.

## The test check (by the lead, in step 4)

Run it when the change adds a condition or branch in tested logic, or when the reviewer says a test would
stay green if the code broke. It settles that claim by experiment instead of by reading.

1. Never mutate the user's working tree; other uncommitted work sits there. Make a scratch copy:

   ```bash
   git worktree add --detach <scratch>/rv HEAD
   git diff HEAD > <scratch>/rv.patch && git -C <scratch>/rv apply <scratch>/rv.patch   # plus: copy the untracked files
   # On a box with the rtk hook, write `rtk proxy git diff`: rtk compacts `git diff`, so apply gets no patch.
   ln -s "$PWD/node_modules" <scratch>/rv/node_modules  # Node repos
   ```

2. Invert one condition the change adds (drop a negation, swap `&&` for `||`, change `<` to `<=`).
3. Run only the narrowest test file for it.
4. Still green means a finding (Should fix): name the missing test case. Red means the test earns its
   place.
5. Remove the copy: `git worktree remove --force <scratch>/rv`.

If the narrowest test cannot run in the copy within a few minutes, skip the check and list it under
Unverified.

## Agent Factory tasks

A task's Review step runs its own prompt from `server/review.ts`, inside the task's worktree. This skill is
for a chat agent reviewing that work, or any other repo. Pass the task's plan (`docs/plans/<KEY>.md`) as
`--context`.
