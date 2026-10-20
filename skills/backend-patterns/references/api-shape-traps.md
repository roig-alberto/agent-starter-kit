# API-shape traps - a correct implementation that lies to the user

Distilled from real incidents on this fleet (closet + superhuman, 2026-07). Pointer lives in
`SKILL.md`.

- **Never inline blobs (base64 images) in a list JSON.** closet's `/api/items` carried
  `photoDataUrl` per item → ~10MB for 55 items, re-downloaded whole on every open, and
  busted by ANY single edit (one giant cache entry). **Winner (2026-07-17, list 10MB→16KB,
  reopen = 0 photo network):** keep the base64 in the store (backup unchanged, no blob
  migration), but have GET swap each field to `/api/items/:id/photo?v=<contentHash>`; a
  dedicated endpoint serves DECODED BINARY (−33% vs base64) with
  `Cache-Control: immutable, max-age=1y`. Key server trick that made the frontend need ZERO
  changes: **on write, PRESERVE the stored bytes whenever the incoming photo field is not a
  fresh `data:` URL** (a metadata edit spreads the GET'd item and carries the URL back - 
  don't clobber). A re-crop bumps the hash → new URL → refetch. SW side in `pwa-patterns`.
- **Matching identifiers by substring is a false-positive generator - use boundaries.**
  Brand names hide inside ordinary words: `"appleton recruiting".includes("apple")` flagged
  a legit recruiter as impersonating Apple (also "Pineapple Design", "Amazonas Tours",
  "Googleplex Cafe"). For a DOMAIN, "wears the brand" means the brand is a whole **label**
  (`paypal-verify.ru` → `paypal|verify|ru`), not a run of characters. Inverse trap in the
  same file: `endsWith(brandDomain)` passes `paypal.com.evil.ru` - ownership must be
  `domain === bd || domain.endsWith("." + bd)`. Both directions need a test.
- **Any default filter needs a "how much am I hiding?" count.** superhuman search shipped
  the wireframe's 12-month default; on the real mailbox almost everything is older. The
  empty state offered "Search all mail" - but the DANGEROUS case is a search returning SOME
  results (28 of 687): it never looks empty, the escape hatch never appears, 659 hits are
  silently withheld. Return the in-range AND unranged counts, and offer the widen whenever
  the range is holding matches back - not only at zero. A default that's right for the
  designer's data lies by omission on the user's.
- **No ambient `Math.random` in anything a user re-loads.** closet's recommender used it,
  so the base proposal "changed by itself" on every reload and the tests went flaky.
  Pattern: **deterministic by default + variety EXPLICIT** - a SEEDED shuffle with a
  `variant` param (`0` = canonical), the seed persisted in the model, and "give me another"
  = a seed bump (stable until the next). For natural rotation, vary the seed by day/index
  (`variant*K + day`), never per call.

## An edit form that rounds on save rewrites imported precision (personal-dash)

A form that normalises numbers on save (`Math.round`) silently rewrites imported values with more precision, even when
the user only edited another field. Round to the precision the source uses, and apply the same rounding in the client's
dirty check.
