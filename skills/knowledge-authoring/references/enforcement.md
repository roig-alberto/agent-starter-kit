# Which mechanism enforces a rule

A rule a script can check is a check, not prose: prose rules drift and the em-dash ban was re-policed by hand for
months before a hook enforced it. Pick the mechanism by when the mistake can first be caught.

| The mistake shows up as... | Mechanism | Where |
|---|---|---|
| A shell command that is dangerous before it runs (sudo, destructive git, staging the user's work) | Pre-command guard, every agent | `~/.claude/scripts/agent-guard.py` (OpenCode adapter `agent-guard-opencode.ts`) |
| Something landing in a repo: the message, the added lines, file names (dashes, trailers, secrets, IBANs, a weakened test) | Global git hook, every agent and the user | `~/.claude/git-hooks/commit-msg`, `pre-push` |
| The shape of a skill, rule, memory or HARVEST entry | Knowledge lint, holds the auto-push | `~/.claude/scripts/knowledge-lint.py` |
| Slow drift on the box (docs missing, deployed copies out of sync, unused skills) | A plain-code loop, weekly, findings to Triage | `~/.claude/scripts/box-checks.py` subcommand, run by Agent Factory's Box checks |
| An app's behavior | That repo's tests, typecheck and lint, plus the Main is red loop | the repo's Commands block |
| A judgment about one diff (scope, missing proof, design) | Automated review | `review-diff` with the repo's `REVIEW.md` |
| Something only inside the agent's own session (its reply text) | An agent hook, only when no mechanism above can see it | agent-specific, so the last resort |
| A judgment no script can make (calibration, when to ask, scope) | Prose | RULES.md or a skill |

## Rules

- Measure before you build: count past breaks of the rule and the false alarms the check would raise today (run its
  pattern over every repo in `~/projects`). A rule nobody breaks needs no check; a check that blocks current
  legitimate files needs an exception first.
- Every guard and git hook rule gets one sample that blocks and one that passes in `~/.claude/scripts/guards-test.sh`.
  A lint rule gets a seeded bad case that fails and passes once fixed. Box checks runs `guards-test.sh` weekly.
- Never print the protected value in a block message (a secret, an IBAN, a personal value): name the file and line.
- Once a check enforces a rule, the prose shrinks to a pointer: RULES.md "Git and secrets" lists what the guards block
  instead of repeating each rule.
