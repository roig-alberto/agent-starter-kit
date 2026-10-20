# Sonner troubleshooting table

Every known Sonner symptom with its cause and fix. `SKILL.md` carries the three most common as gotchas; the rest live only here.

| Symptom | Cause and fix |
| --- | --- |
| Toast never appears | No `<Toaster />` mounted, or it unmounted (conditional render, per-page placement). Mount one at the root. If calling from a server action: `toast()` is client-only - call it with the action's result on the client. |
| Same toast appears twice | Two Toasters mounted (layout **and** page) - keep one. Or `toast()` fired in an effect under React StrictMode's dev double-invoke - fire from the event handler instead, or pass a stable `id` so the second call updates rather than duplicates. |
| Tailwind/CSS classes have no effect | Default styles override them. Mark them `!important`, or use `unstyled` / headless (see the styling ladder in `sonner-usage.md`). |
| Toasts render completely unstyled (common in Astro, view transitions) | Sonner's injected stylesheet was lost - import it explicitly in a layout: `import 'sonner/dist/styles.css'`. |
| Unstyled inside Shadow DOM | Styles land in `document.head`, not the shadow root. Copy the style tag whose text includes `[data-sonner-toaster]` into the shadow root. |
| Toast behind a modal/overlay, or clipped | An ancestor creates a stacking context (`transform`, `filter`, `overflow`) or the overlay out-z-indexes the toaster. Move `<Toaster />` to the document root, outside any dialog/portal container. |
| Dark mode ignored | `theme` defaults to `'light'` - set `theme="system"` or pass the resolved theme (see Theme in `sonner-usage.md`). |
| Success/error look gray, not green/red | That's the default. Add `richColors` to the Toaster. |
| Toast never closes | `duration: Infinity`, `dismissible: false`, or a `toast.promise` whose promise never settles - the loading toast waits forever. |
| `toast.promise` stuck on loading | It needs a promise (or a function returning one) as its first argument, and the promise must actually resolve/reject. |
| Swipe-to-dismiss goes the wrong way / doesn't work | Directions derive from `position`. Override with `swipeDirections` on the Toaster. |
| Toast shows up in every toaster | Multiple toasters need targeting: give each Toaster an `id` and pass `toasterId` in the `toast()` call. |
| Toasts too close to the screen edge on mobile | `offset` (desktop, default 32px) and `mobileOffset` (<600px, default 16px) - numbers, CSS strings, or per-side objects. |
