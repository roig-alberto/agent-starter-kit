# Sonner usage: wiring, picking the call, recipes, styling

How to wire Sonner, which `toast()` call fits, the common recipes, and the styling escalation ladder.
Answer Sonner questions from these files, not from memory; `sonner-api.md` has every exact prop name,
type and default.

## Wiring: the two pieces

Sonner ([sonner.emilkowal.ski](https://sonner.emilkowal.ski)) is two pieces, a mounted `<Toaster />` and
a `toast()` function. Nearly every failure is one of those two placed wrong: toasts that never show,
show twice, lose their styles or sit behind a modal.

- **Mount exactly one `<Toaster />`, once, as close to the root as possible.** In Next.js that is
  `layout.tsx`, where it works inside server components. A second Toaster duplicates every toast, and a
  conditional or per-page one unmounts and drops them.
- **Call `toast()` only from client code**: event handlers, effects, callbacks. It needs no hook or
  provider but does nothing on the server, so a server action returns its result and the client that
  receives it calls `toast()`.

```jsx
import { Toaster } from 'sonner'; // once, in layout
import { toast } from 'sonner';   // anywhere client-side
```

- **Pick the call by intent.** Plain `toast('Title')` (with `{ description }`), typed
  `toast.success('…')` / `toast.error('…')`, `toast.loading('…')` updated by id,
  `toast.promise(promise, { loading, success, error })`, an `{ action: { label, onClick } }` button, or
  headless `toast.custom((t) => <jsx />)`. The full table is below.
- **Update a toast by calling `toast()` again with the same `id`**; only the props you pass change, and
  `toast.success(…, { id })` changes the type. Persist with `{ duration: Infinity }`, dismiss with
  `toast.dismiss(id)` or `toast.dismiss()`, and read active toasts with `useSonner()` or
  `toast.getActiveToasts()`.
- **Climb the styling ladder only as far as the change needs** (below). Jumping straight to headless is
  fine and is the recommended end state for a design-system toast; lingering in the middle, marking many
  classes important, is not.
- **Set the theme explicitly.** `theme` defaults to `'light'` and does not follow the OS, so pass
  `theme="system"` or `<Toaster theme={resolvedTheme} />` from `next-themes`.

## Picking the right call

| You want | Call |
| --- | --- |
| Plain message | `toast('Title')` - add `{ description }` for a second line |
| Success / error / info / warning icon | `toast.success('…')`, `toast.error('…')`, etc. |
| Spinner while you manage state yourself | `toast.loading('…')`, then update it by id |
| Loading, then success or error, tied to a promise | `toast.promise(promise, { loading, success, error })` - success/error accept functions receiving the resolved value/error |
| Button that does something | `{ action: { label, onClick } }` - closes the toast unless `onClick` calls `event.preventDefault()`; `cancel` is the secondary variant |
| Custom JSX, default toast shell | `toast(<jsx />)` |
| Custom JSX, no styles at all | `toast.custom((t) => <jsx />)` - headless, `t` gives you the id to dismiss |

## Recipes

**Update a toast** - call `toast()` again with the same `id`; only the props you pass change. Switching to `toast.success(…, { id })` changes the type. This is how loading → success flows work without `toast.promise`:

```jsx
const id = toast.loading('Uploading…');
toast.success('Uploaded', { id });
```

**Persist** - `{ duration: Infinity }`. **Dismiss** - `toast.dismiss(id)`, or `toast.dismiss()` for all. **Read active toasts** - `useSonner()` in React, `toast.getActiveToasts()` outside it.

**Links or components in the text** - pass a function for the title or description: `toast(() => <a href="…">View</a>)`.

**Multiple toasters** - give each an `id` and target with `toast('…', { toasterId: 'canvas' })`. Without `toasterId`, every toaster renders the toast.

**Close callbacks** - `onDismiss` fires on close button or swipe; `onAutoClose` fires on timeout. They are separate; there is no single "closed" callback.

## Styling - the escalation ladder

Climb only as far as the change requires; jumping to the top rung too early is fine (it's the recommended end state), lingering in the middle is not.

1. **Defaults** - plus `richColors` on the Toaster for colorful success/error, `invert` to flip against the theme.
2. **Inline tweaks** - `toastOptions={{ style: {…} }}` on the Toaster for all toasts, or `style` per `toast()` call.
3. **Classes on parts** - `toastOptions={{ classNames: { toast, title, description, actionButton, cancelButton, closeButton } }}`. Sonner's injected styles win the cascade, so every class needs `!important` (Tailwind: `!text-red-900`). If you're marking more than a few things important, stop - go headless.
4. **Headless** - `toast.custom()` with your own JSX, keeping Sonner's positioning, stacking, and swipe. The recommended approach for a design-system toast: wrap it in your own `toast()` abstraction. (`unstyled: true` exists as a halfway house, but headless gives more control for the same effort.)

**Icons** - swap defaults per-type with the Toaster's `icons` prop, per-toast with `icon`, remove with `null`.

**Theme** - `theme` defaults to `'light'` and does not track the OS. Pass `theme="system"`, or wire your theme provider: `<Toaster theme={resolvedTheme} />` from `next-themes`.

