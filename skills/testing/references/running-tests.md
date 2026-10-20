# Running the tests

## Where tests live

Tests are colocated: `lib/**/*.test.ts` (Aro), `lib/**/__tests__/*.test.ts` (Caudal),
`src/lib/__tests__/*.test.ts` (closet). The runner config is in each repo's `vitest.config.ts` /
`vite.config.ts`. Each repo's AGENTS.md Commands block is canonical if it diverges from this file.

## Always run inside the container

The deps are Linux-built and the host node_modules differ, so run tests in the container:

```bash
# Aro
docker compose exec web npm test            # or: run --rm web npm run test
docker compose exec web npx tsc --noEmit    # typecheck
# Caudal - npm install first: its dev deps live in a named volume that is only
# populated when the dev profile runs; a bare `compose run` finds it empty (tsc/vitest not found)
docker compose run --rm --no-deps web sh -c "npm install --no-audit --no-fund && npm run test"
docker compose run --rm --no-deps web sh -c "npm install --no-audit --no-fund && npm run typecheck"
# closet
docker compose run --rm dev sh -c "npm run test"
docker compose run --rm dev sh -c "npx tsc -b --noEmit"
```

Safety net: Agent Factory's "Main is red" loop also runs every board repo's checks each Sunday and files a green to
red change to Triage, so drift that lands between sessions surfaces within a week even if no one opens the repo.

## Testing a checkout OUTSIDE the bind mount (worktree, agent copy)

The image's node_modules is STALE. Aro's `web-dev` mounts `./:/app` plus an anonymous `/app/node_modules`
volume, and that volume was populated when the container was created, so it carries the CURRENT deps
while the image does not. Run a Paseo worktree or any other copy through
`docker compose run -v <tree>:/app web-dev` and you get the IMAGE's node_modules: phantom `FAIL` test
files and TS2307 errors, identical on a pristine `master` export.

Winner: mount the live container's own node_modules volume read-only, and give it a fake unreachable DB
(`lib/withings/write.test.ts` throws at import when `DATABASE_URL` is unset):

```bash
VOL=$(docker inspect personal-dash-web-dev-1 --format '{{range .Mounts}}{{if eq .Destination "/app/node_modules"}}{{.Name}}{{end}}{{end}}')
IMG=$(docker inspect personal-dash-web-dev-1 --format '{{.Config.Image}}')
docker run --rm --network none -v "$WT":/app -v "$VOL":/app/node_modules:ro -w /app \
  -e TZ=Europe/Madrid -e DATABASE_URL='postgres://fake:fake@127.0.0.1:1/none' "$IMG" \
  sh -c 'npx vitest run --cache=false; ./node_modules/.bin/tsc --noEmit'
```

Before believing a red on a copy, run the same command on a pristine export of the base commit
(`git archive <sha> | tar -x -C <tmp>`). Same failures on both means environment, not your diff.

## Verifying an endpoint without a browser trips its CSRF guard

A bare `curl -X POST` to an Astro API route returns
`403 Cross-site POST form submissions are forbidden`, because Astro blocks cross-site POST by default. It
looks like a broken endpoint and is not: a real browser sends `Origin` and works. Send it yourself when
verifying headlessly:

```bash
curl -H "Origin: http://127.0.0.1:<port>" -X POST ...
```

This is real CSRF protection, so pass the header and never disable the guard. The same shape applies in
any framework with an origin check.
