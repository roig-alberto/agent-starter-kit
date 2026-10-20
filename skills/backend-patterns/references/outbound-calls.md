# Outbound calls and mutation queues

## Every outbound call needs an explicit timeout (`fetch` has NONE)

Node's `fetch` waits forever by default, and a retry loop only fires on a RESPONSE - a
connection that never returns is not a 5xx, so the retry never triggers and the caller
awaits indefinitely. recall 2026-07-12: a queued free-tier OpenRouter request stalled a
`gradeMockSession` >3 min with **zero** `llm_calls` rows logged (the first call simply never
came back). Applies to every outbound hop from our apps - LLM providers, Graph/a smartwatch/
TickTick, webhooks, the NAS/HTTP sidecars.

**Rule: per-ATTEMPT `AbortController` timeout, and treat the abort as transient (retry it
like a 5xx).** Proven shape, `~/projects/recall/src/lib/llm/openrouter.ts` `chat()`
(landed cff0758, verified present 2026-10-19):

```ts
const ctrl = new AbortController();
const timer = setTimeout(() => ctrl.abort(), REQUEST_TIMEOUT_MS); // 30_000
try { res = await fetch(url, { ...init, signal: ctrl.signal }); }
catch (e) {
  lastErr = (e as Error)?.name === "AbortError" ? `timed out after …` : `failed: …`;
  if (attempt === MAX_ATTEMPTS) throw new Error(lastErr);
  await sleep(Math.min(2 ** attempt * 1000, 8000)); continue;   // backoff, retry
} finally { clearTimeout(timer); }
```

Per-attempt, not per-call, so the timer resets each retry; `clearTimeout` in `finally` or the
timer leaks. Harmless on a fast paid API, load-bearing on anything free/queued.

## A mutation QUEUE must classify the response, not just pass/fail it

Sibling of the timeout rule: that one is about a call that never returns, this one about a call
that returns "not now". A queue that marks every non-2xx `failed` LOSES WORK the moment the
provider throttles you, and it looks like your feature is broken rather than like rate limiting.

superhuman's Graph flusher did exactly that (2026-07-23): `status:"failed"` was terminal (only a
manual retry pass revived it), so a several-hundred-message bulk delete would come back part-429,
those ops would die, and their mail would **reappear** in the inbox. Small batches (12, 320) never
tripped it, so it sat latent for months.

**Rule: classify every response into ok / TRANSIENT / permanent before writing status.**
- transient = 429, 5xx, network throw, and *no response for that item* in a batch (no proof it
  applied - never treat a missing sub-response as success if success deletes local state)
- transient stays `pending` with an attempt counter; a `MAX_ATTEMPTS` cap stops the queue wedging
- permanent (404/403/400) fails immediately - it will never fix itself
- on a 429, **stop that account/tenant for the tick**: the poll interval becomes the backoff.
  Continuing to drain is what turns throttling into mass failure
- cap ops per tick so one bulk action cannot starve the sync running after it

Keep the decision pure and tested (`lib/sync/flush-policy.ts`), SQL in the caller - the retry/fail
split is exactly the logic you cannot exercise against a live API on demand.
