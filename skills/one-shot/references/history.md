# one-shot history

## Hand-rolled domain concept (Caudal, 2026-07-10)

Hand-rolling a concept the codebase already solves is the classic waste. Caudal 2026-07-10 hand-rolled
traspaso leg-pairing before finding the existing `detectTraspasoPairs` (the naive version also failed on
real data). The user caught it, not the recon. One "does X already exist?" line in the recon brief would
have erased it. That is why step 0 makes the recon brief grep the concept, not just "where does the data
live."

## Pre-existing typecheck drift (2026-07-06)

A **pre-existing** red check (there before your change) is never something to step around silently: fix it
if it is small (the quality bar), otherwise flag it as a finding in your report. "Unrelated, so I ignored
it" is how the 2026-07-06 typecheck drift sat unnoticed.

## Review through review-diff, not an exploring reviewer

Step 5 used to suggest an independent review by `cavecrew-reviewer`. It now hands the diff to `review-diff`
(see `model-tiering`), because a reviewer that explores the repo costs far more: Agent Factory measured
1.41M tokens for an exploring review against 23k for one turn with the diff inline (cited from Agent
Factory's CLAUDE.md, "Verify runs the repo's own commands first").

## Skill renames in the 2026-10-15 redo

Older docs and chats name skills that were merged on 2026-10-15. Read them as the new name:

- `phased-plan` is now `plan`.
- `app-testing` and `isolated-test-db` are now `testing`.
- `new-project` and `bootstrap-orchestrator` are now `new-app`.
- `security-posture` and `openbao-secrets` are now `security` (not in this kit).
- `docker-ports-and-tunnels`, `docker-fleet-maintenance` and `selfhosted-panels` are now `fleet-ops`.
- `proxmox-portability`, `app-migration` and `dependency-updates` are now `portability`.
- `nas-offsite-backup`, `syno-nas-sftp-ops` and `telegram-alerts` are now `backups-and-alerts` (not in this kit).
- `ui-design-references` is now part of `frontend-design`.
