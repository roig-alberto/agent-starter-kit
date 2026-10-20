# Web Push recipe (Aro + Caudal, `web-push` lib)

1. **Keys.** A `gen:vapid` script writes `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `VAPID_SUBJECT` to
   `.env`. **`VAPID_SUBJECT` must be a real `mailto:`, because Apple rejects placeholders** (documented in
   Aro's `.env.example`).
2. **Routes.** `api/push/subscribe` stores the subscription in a `pushSubscriptions` table, `api/push/vapid`
   serves the public key, and `api/push/test` does a manual send.
3. **Send.** `lib/push/send.ts` calls `setVapidDetails(...)`, iterates subscriptions, and **prunes rows on
   404/410**, because dead endpoints accumulate otherwise.
4. **Dedupe by device on subscribe.** The client sends `navigator.userAgent` as `device_label`; after the
   upsert, `delete` other rows with the same `device_label` and a different `endpoint`. This collapses a
   device to its latest subscription and self-heals on the next app open. It needs a `device_label`
   column: **Aro has it; Caudal and recall do NOT yet** (they upsert by endpoint with no device key), so the
   same duplicate bug is latent there.
5. **SW side.** The `push` handler calls `showNotification` (icon/badge 192, `data.url`);
   `notificationclick` focuses an existing window and navigates, else calls `openWindow`.
6. **iOS reality.** Web Push works only for the INSTALLED PWA over real HTTPS (the tunnel provides it), and
   `navigator.vibrate` is unsupported, so never promise haptics.

## Why the 404/410 prune is not enough on iOS

iOS mints a **brand-new endpoint** on every PWA reinstall, iOS update, or re-add, so
`onConflictDoUpdate(target: endpoint)` inserts a NEW row each time. The old rows are NOT dead (Apple keeps
delivering to them), so the 404/410 prune never fires and `sendToAll` fans the push to every stale
same-device subscription. The prune alone only catches endpoints the *browser* dropped, never iOS's
still-live stale duplicates. The Aro incident is in `references/history.md`.
