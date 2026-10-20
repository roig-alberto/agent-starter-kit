# Phase 3: design

Ask the user with AskUserQuestion how to produce the design. Present both paths **equally, with no
default**.

## Path A: the Claude Design Agent (external)

Confirm DESIGN_BRIEF.md is self-contained, then **PAUSE** and tell the user to run the **Claude Design
Agent** on it. **Hand it the reference apps and any screenshots** (from Phase 1, in the brief's "References
& inspiration" section) alongside the brief, so the visual direction targets something concrete rather
than abstract. To get a machine-usable result back instead of prose you must re-transcribe, give the
design agent the **token-export request below**, adapting the framework, the semantic roles, and any
domain-specific accent roles to this project. Crucially, it also asks for the **app icon as SVG**.

**File exchange, one folder per feature.** The user drops what they give the agent into
`ui/inbox/<feature-slug>/` with an **`input-`** prefix (`input-design-brief.md`, `input-refs/`). The
`<feature-slug>` keeps multiple features and projects from colliding. The prompt ends by telling the agent
to write everything back into the **same** folder with an **`output-`** prefix, so input and output are
obvious at a glance.

> Export the complete design-token set for this design as code I can drop into a
> **<CSS framework - e.g. Tailwind CSS + daisyUI>** project. Specifically give me:
>
> 1. **Two theme objects** - `<project>-light` and `<project>-dark` - with every semantic
>    role mapped to its hex: `primary, secondary, accent, neutral, base-100, base-200,
>    base-300, base-content, info, success, warning, error`, plus the matching
>    `--rounded-box`, `--rounded-btn`.
> 2. **A `tailwind.config` `theme.extend` block** with: `colors` (all custom hexes with
>    names, both themes), `fontFamily` (display + mono), `borderRadius` scale, `boxShadow` scale.
> 3. **A type scale table**: for each text role (largest hero figure, H1, H2, body, caption,
>    mono label/code) give font-family, px size, weight, letter-spacing, line-height.
> 4. **The semantic color meanings**: which token = positive/success, negative/error, warning,
>    informational - plus any **domain-specific accent roles** in this product.
> 5. **Any gradients** as exact CSS (e.g. a status/pace line).
> 6. **The spacing scale** and the **icon library** name + stroke weight (e.g. Lucide vs Heroicons).
> 7. **The application icon as inline SVG** - a primary version and a full-bleed/maskable-safe
>    variant - plus the exact brand colors it uses.
> 8. Output as plain code blocks (CSS variables + JS config + SVG), not prose.
> 9. **Deliver hi-fi STATIC wireframes, not an interactive prototype.** Fully styled frames
>    (real type, colour, spacing, content), **one frame per screen state** (default, each
>    filter/sort state, each sheet open, every empty state, each row variant, light + dark).
>    No wired navigation, no working controls, no clickable/live HTML app. State coverage
>    beats clickability: a state only reachable by clicking is a missing frame.
> 10. **Read every `input-*` file in `ui/inbox/<feature-slug>/` as the source of truth, and write
>     every deliverable (wireframes + the code blocks above) back into that SAME folder with an
>     `output-` prefix** - nothing elsewhere, nothing without the prefix.

When the `output-*` files land in `ui/inbox/<feature-slug>/`:

1. Save the visual reference under `ui/`.
2. Save the icon SVGs under the app's public assets, and generate the PWA icon set if it is a web or PWA
   app.
3. For an installable phone app, also apply the `ios-pwa-dock` §1 shell checklist before the first
   screen (see `history.md` in this directory for why).
4. Extract the tokens into **DESIGN_TOKENS.md** as the theme source of truth.
5. Reconcile the product name, and fold token references into the canonical docs: point `DESIGN_BRIEF.md`
   at `DESIGN_TOKENS.md`, with no drifting copies.

## Path B: in-house

Load the **`frontend-design`** skill first (intentional aesthetic direction, which avoids templated "AI
slop" defaults). Then generate the wireframes yourself (SVG or HTML; the visualize tool is an option),
derive **DESIGN_TOKENS.md** from the brief, and **design the app icon as an SVG** (primary and maskable
variants), generating the PWA icon set and manifest if it is a web or PWA app.

## Either path

Produce **DESIGN_TOKENS.md** (machine-usable: the exact values that become the Tailwind or CSS theme), and
reconcile it so `DESIGN_BRIEF.md` points to it, with no drifting copies.

## Iteration protocol (both paths)

Put this in the design-agent hand-off, and follow it in-house too.

1. **Palette first.** The *first* iteration is a **color-palette preview only**: a small set of
   representative screens rendering the proposed palette in context, plus the draft light and dark token
   values, so the user can review and adjust colors before any full build. Do **not** produce the full
   wireframe set or finalize tokens in this first pass.
2. **Gate on palette approval.** Do not build out the full set of screens (or lock `DESIGN_TOKENS.md`)
   until the user has **explicitly confirmed the color palette**.
3. **Non-destructive iteration.** Never modify, delete, or restyle a wireframe that was already created
   or approved unless the user explicitly asks. **Add** new screens rather than altering existing ones,
   and treat approved wireframes as immutable.

**Gate:** the user has confirmed the **color palette**; then DESIGN_TOKENS.md exists and the full visual
direction is agreed.
