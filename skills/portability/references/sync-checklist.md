# FLAG examples (part 1, step 1)

Flag each violation to the user with its fix; never silently accept it. Examples:

- mounts `<alert-token-file>` or `~/.config/...`: "host-absolute path, put it in `./secrets/`
  instead."
- `image: foo:latest`: "unpinned, pin to the running exact version (`docker exec … --version`)."
- adds a named volume with real state: "new stateful volume `X`, add it to the backup pipeline or it is
  lost on a host move."
- a new secret only in `.env`/`./secrets/` on the box: "confirm `secrets-backup.sh` covers this app so it
  reaches the NAS."

# SYNC the rebuild files (dev-system repo)

Keep these current so `REBUILD.md` never lies:

- **New app**: add a row to `REBUILD.md` (repo, dump dir, dump type, restore cmd); add its name to
  `scripts/secrets-backup.sh` `APPS`; add a line to `scripts/restore-test.sh` `APPS` (with a sentinel);
  add a line to `scripts/nas-deadman-check.sh` (`name|dir|glob|max_age|enabled`, confirm the glob, then
  deploy it per `backups-and-alerts` (not in this kit)); register its host port in the `fleet-ops` port registry; mirror its
  `.env` into OpenBao (`security` (not in this kit)).
- **New or changed stateful volume**: cover it in the app's backup (sidecar) and note it in `REBUILD.md`.
- **New host-level piece** (systemd unit, host script, cron): capture it under `host/` or `systemd/` in
  the dev-system repo (with an install note); never leave it only on the live host.
- **Edited host script or unit**: the edit ends with `sudo /bin/sh -c 'install -m 755 <dev-system copy> <deployed path>'`
  and `cmp` of the two, and the pair is listed in `box-checks.py deploy_sync`. A copy edited only in dev-system kept
  research's secrets out of the NAS bundle for weeks (2026-10-26).
- **Image bump**: update the pin in the compose file or Dockerfile AND anywhere `REBUILD.md` lists it; the
  full pin-sync map is in `references/pin-sync.md`.
- **Any `ports:`/binding/tailnet-node-name/serve-target/container-name change**: update the `fleet-ops` port
  registry row in the same commit (its "sync triggers" section). The registry only stays true if every
  infra change carries its row. `~/.claude/FLEET.md` regenerates from the running system
  (`python3 ~/.claude/scripts/fleet-facts.py`), so rerun it after the change.

## Where the rebuild files live

dev-system repo, `~/projects/dev-system`:

- `migrations/ubuntu-native/MIGRATION.md` (the 2026-10-27 move to native Ubuntu, phase by phase)
- `host/bootstrap-ubuntu.sh` (fresh-host bootstrap, run as root) and `host/install-host-services.sh`
- `REBUILD.md` (master runbook)
- `host/` (tg-alert, telegram env example, boot-alert unit, README, claude-spawner, mem-watch,
  docker-restart-alert)
- `systemd/` (restore-test and secrets-backup service/timer, among others)
- `scripts/` (secrets-backup, restore-test, nas-deadman-check)
- `backup-template/`
- `bootstrap/`

Details and rationale are in dev-system `REBUILD.md` and `PLAN.md`.
