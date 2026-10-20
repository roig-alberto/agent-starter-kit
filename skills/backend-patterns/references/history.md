# backend-patterns - history

Incidents and measurements behind rules in `SKILL.md` that are not already told in a topic file.

## Provenance

Distilled from the actual code (2026-07-06), not aspiration. Reference implementations:
`~/projects/personal-dash` (Aro) and `~/projects/finance-proj` (Caudal).

## A partial undo degraded prod items (loop, 2026-09-02)

- **An undo/revert must restore the COMPLETE captured snapshot, not just the user-visible field.**
  A revert that puts back only what the user sees leaves invisible derived state wrong - e.g. a
  staleness/ranking timestamp that every ranking reads - so the "undone" row silently rots or
  sinks. Capture the full prior state on the mutation (a snapshot column), restore exactly those
  keys on undo. (loop 2026-09-02: a partial undo degraded 2 prod items; fix was one additive
  migration + a snapshot restore.)

## Grouping to "shrink" a result set SILENTLY DROPS ROWS (superhuman, 2026-07-23)

The bind traps above at least throw. This one returns a plausible number and nothing errors.
Aggregating per-sender, `GROUP BY (sender, is_read, received_at)` + one count per GROUP ROW lost
**24 of 13,597 messages** - every set that collided on all three columns counted once (superhuman,
2026-07-23). No test would have caught it; the screen would simply have understated the user's
backlog forever.

**Rule: when a screen promises real numbers, reconcile the aggregate against `count(*)` of the
source before shipping the query** - and prefer one row per record (13k rows through a JS counter
is nothing) over a GROUP BY that looks tidy. The arithmetic has to close: cached 13,597 + archive
149 + junk 5 = 13,751 scanned, exactly.

## The bind traps (recall 2026-07-11, superhuman 2026-07-17)

Three separate sessions across recall (2026-07-11) and superhuman (2026-07-17, hit
3× in ONE session). `tsc` catches neither; unit tests don't either - an integration
fixture found them. **Rule: `sql\`\`` is for STRUCTURE; values go through drizzle operators.**

## Validation convention (2026-07-06)

`const Body = z.object({...})` declared **in the route/action file itself** (both apps,
50 files) - no central schema module. Parse before touching the DB. This is the actual
convention; docs claiming "shared schemas" are drift.

## The original API-shape summary

Four earned rules, full incidents in `references/api-shape-traps.md`: never inline blobs
(base64 photos) in a list JSON - serve content-hashed immutable URLs (closet, 10MB→16KB);
match identifiers by word/label BOUNDARY, never substring (`appleton` is not Apple, and
`endsWith(brandDomain)` passes `paypal.com.evil.ru`); every default filter must return a
"how much am I hiding?" count (a partial result never triggers the empty-state escape
hatch); no ambient `Math.random` in anything a user re-loads - seeded shuffle + explicit
`variant`.

## The original LLM summary

`strict: true` does NOT prevent truncation - set `max_tokens` AND a `maxLength` on every
free-text field, then re-validate with zod so a cut-off reply is rejected, not half-applied. When
the model must choose from a known list, constrain it to a bounded integer INDEX and resolve that
server-side; echoing an id is where vision models hallucinate a plausible wrong record. Both
recipes, plus the `OPENROUTER_BASE_URL` mock that exercises the path without a funded key:
`references/llm-structured-output.md`.

## 2026-10-16: idempotency keys and expand-contract (skills redo, light edits)

From addyosmani/agent-skills (MIT): `api-and-interface-design` section 6, "Honouring an Idempotency Key" (derive
the key from the intent, claim it atomically with a unique constraint, guard the payload hash, decide what an
in-flight duplicate gets), and `deprecation-and-migration`, "Database Schema Migrations (Expand/Contract)"
(dual-write, batched backfill, a separate later drop, `CREATE INDEX CONCURRENTLY`). The additive-order rule
already existed here; it gained the missing steps.
