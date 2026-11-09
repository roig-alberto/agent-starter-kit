# Auth recipe (single-user apps on the tailnet)

The full recipe behind the auth rules in `SKILL.md`.

1. Password: `@node-rs/argon2` `verify()`; hash stored **base64-encoded** in
   `AUTH_PASSWORD_HASH` (base64 so the `$`-delimited hash survives env interpolation).
   Generator script per app (`gen:pwhash` / `gen:auth`).
2. Session: HMAC-SHA256 signed cookie (`<payload>.<sig>`) via **Web Crypto** (edge-safe
 - the argon2 native module must NEVER be imported in `middleware.ts`). `httpOnly`,
   `sameSite: lax`, `secure` in prod only, sliding TTL (30-90 days).
3. Gate in `middleware.ts` with an explicit PUBLIC allowlist (`/login`, login API,
   `/manifest.webmanifest`, `/sw.js`, `/icons/*`); unauth API → 401 JSON, unauth page →
   redirect `/login`. Matcher excludes `_next/static` etc. The gate is not the only check: every Server
   Action and route handler is a public POST endpoint and re-reads the session itself, because a matcher
   gap (one that excluded all `*.js`, see `security` (not in this kit)) or a header bypass (CVE-2025-29927, fixed in Next 15.2.3)
   skips middleware entirely.
4. Best-effort in-memory rate limit on the login route (5/min - Caudal
   `app/api/login/route.ts:8`). Known limitation: per-process, resets on restart.
5. The tailnet is the network boundary (only the user's devices reach the Tailscale sidecar, no Funnel),
   and this password is the gate inside it. There is no edge login in front of the app any more, so this
   layer must hold on its own. See `security` (not in this kit).
6. **Moving a preference from localStorage to a cookie? RENAME it - RFC 6265 forbids `:` in a
   cookie NAME** (localStorage keys allow it). Caudal's `caudal:hideAmounts` became
   `caudal_dataset` (`~/projects/finance-proj/lib/db/dataset.ts:21-23`). Browsers are lax here,
   so copying the old name fails INTERMITTENTLY - the worst kind of bug to chase later.
