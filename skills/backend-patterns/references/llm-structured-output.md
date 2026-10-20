# LLM structured output - two traps that look like model bugs

## Bound the output or `strict: true` still truncates mid-JSON

OpenRouter with `response_format: { json_schema, strict: true }` will still return unclosed JSON
if a chatty model overruns the default output cap - the parse fails and it looks intermittent
(glow's first two calls passed on short reasons; the third truncated).

**You need BOTH:** `max_tokens` on the request AND `maxLength` on every free-text field in the
schema. `max_tokens: 500` + `reason: { type: "string", maxLength: 240 }` fixed it. Re-validate
the parsed object with zod so a truncated reply is rejected outright rather than half-applied.
(glow, 2026-08-07 - cost one wasted grade round)

## Make the model return an INDEX, never an id

When the model must pick one item from a known list, constrain the schema to a bounded integer
index into a numbered list - `pick: { type: "integer", minimum: 0, maximum: N }` with `0 = none`
 - and resolve it server-side against the ACTUAL catalog, mapping out-of-range to null.

Echoing a long id or uuid is precisely where vision models hallucinate, and a hallucinated id
resolves to a plausible wrong record instead of an error. glow's look-advisor uses this. Pairs
with the truncation fix above. (glow, 2026-08-11 - logged as a first-try win)

## Testing the whole path without a funded key

Add an `OPENROUTER_BASE_URL` env override so the vision path can run against a tiny mock server
returning a canned completion plus `usage.cost`. That exercises parse → resolve → metering →
budget gate → UI end to end; only real-model quality stays gated on a live key.
