# Migrating an EXISTING tuned app to shadcn/ui at scale

Proven once end-to-end: recall (Next + Tailwind v4, ~30 files, PR #2, 2026-07-13) went from
hand-rolled primitives to shadcn without a visual regression. `references/interactive-primitives.md` owns the *decision* (hand-roll vs `shadcn add`); this file is the *migration* recipe for an
app that already has its own design tokens and dozens of call sites.

## 1. Setup: do NOT run `shadcn init` on a tuned app

`shadcn init` rewrites `globals.css` and can clobber a hand-tuned token block. Instead:

- **Hand-write `components.json`** (recall's, verified 2026-10-19): `style: "new-york"`,
  `tailwind.cssVariables: true`, `tailwind.css` pointing at the real `src/app/globals.css`,
  aliases mapped to what already exists (`utils: "@/lib/utils"` - the app's own `cn`).
- **Confirm the shadcn CSS vars already exist** in `globals.css` (`--primary`, `--border`,
  `--input`, `--ring`, `--muted-foreground`, ...). Add only the missing ones, mapped to the app's
  token values. Pulled components reference these names; a missing var is an invisible-border bug.
- **Run `npx shadcn add <c>` IN the dev container**, not on the host: the container has network AND
  the installed `node_modules`, and the bind mount persists the written files back to the host. It
  drops sources in `src/components/ui/` and installs the Radix dep.

## 2. Restyle the primitive's BASE to the app's tokens (not each call site)

After pulling a primitive, edit its base classes to the app's `DESIGN_TOKENS.md` once, so the
typical call site becomes `<Input/>` with **no className**. recall: `Input` base
`h-[50px] rounded-2xl` + cobalt focus ring; `Select` trigger on app tokens; `Button` gained
`hero`/`danger`/`surface` variants and `cta`/`pill`/`step` sizes. Anything genuinely one-off stays a
className. Getting this backwards (leaving stock bases + per-call overrides) is what makes a shadcn
migration read as "we now have two design systems".

**Keep a THIN wrapper API over Radix where the app's call sites already have a convention**, e.g.
expose `on`/`onChange` over Radix's `checked`/`onCheckedChange` so 20 existing usages don't churn.

## 3. Fan out ONE `cavecrew-builder` per file, with a shared spec + a LEAVE-UNTOUCHED list

Batches of ~4-9 files, each builder given the SAME spec contract plus an explicit conservative
"do not convert" list: toggle-chips, rating buttons, whole-row selection lists, segmented controls,
`<Link>` CTAs. The builders correctly REFUSED to over-convert, which is what kept layouts intact -
the list is the load-bearing part of the prompt, not the conversion instructions.

## 4. Gate every phase, deploy once

Per phase: in-container `tsc --noEmit` + a live DOM measurement (do a **pixel-parity pilot on one
component first**: same height/radius/color before and after) + commit. Deploy prod once at the end,
not per phase.

## 5. SKIP the mis-fits, with a written rationale

Not every primitive is an upgrade; recall deliberately skipped and recorded why:

| Skipped | Why |
|---|---|
| `Card` | the app's utility divs were already consistent; wrapping them adds indirection, zero a11y gain |
| `RadioGroup` | radios were embedded in a bespoke click-the-whole-row selection list - adopting it means a rebuild, not a swap |
| `Tabs` | the segmented control persists to `localStorage` and is not tab semantics |
| `Progress` | a dynamic tone-gradient bar shadcn `Progress` cannot reproduce |

A skip with a recorded reason is a result. An unrecorded skip becomes next session's "why is this
one different?".
