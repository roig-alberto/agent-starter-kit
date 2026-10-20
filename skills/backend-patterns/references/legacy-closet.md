# Legacy exception: closet (do not copy, do not "fix" unasked)

closet (`~/projects/mycloset`) predates the blessed stack: Vite+Express, single-file
server, JSON-file persistence (`/data/db.json` volume, serialized writes), manual
validation, node-crypto HMAC sessions with `crypto.timingSafeEqual`. It works and is
backed up (JSON dumps); treat its patterns as frozen legacy.

**Its one trap you WILL hit (2026-07-13/17):** `api-dev` and `prod` mount the SAME
`armario_data` volume (one `db.json`) but each holds its OWN in-memory cache. So (a) a
write through one is invisible to the other until that container restarts (`/api/trips`
returned `[]` while `db.json` held the trip - `docker compose restart api-dev`); (b) **a
dev write IS a production write** (see `testing`); (c) never hand-edit `db.json` - 
the next cache flush clobbers it. Reset THROUGH the dev api, then redeploy prod.
