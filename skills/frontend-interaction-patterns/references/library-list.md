# The curated library list

The deliberate, taste-driven picks that `SKILL.md` recommends from. One library per task; stay on this list unless the user asks for an alternative or the task is not covered.

This list came from the old `pick-ui-library` skill. Its failure mode is a menu of generic alternatives
where the list already has a clear answer.

## How to use it

1. **Identify the task, not the library the user named.** "I need to show a dropdown" is a UI-primitives
   task, even if they asked about something else, because the list is indexed by task.
2. **Check what is already installed.** Look at `package.json` first. If the project already uses a listed
   library, use it. If it uses a competitor (for example react-window instead of Virtuoso), flag the
   recommendation but do not churn the dependency without being asked, because a swap is its own decision.
3. **Look the task up below.** Do not substitute alternatives outside the list unless the user asks for one
   or the task genuinely is not covered.
4. **Recommend one library**, state what it is for in one sentence, and install or wire it up if that is
   part of the request. Do not present a menu of options when the list has a clear answer.
5. **If the task is not covered, say so explicitly** and recommend from your own knowledge, making it clear
   that you have left the curated list. A real "X vs Y" decision goes to `research-decision`.

## Where this box overrides the list

- **Unstyled primitives: shadcn + Radix, not base-ui.** Aro, recall and Agent Factory already ship shadcn +
  Radix, and `interactive-primitives.md` holds the traps for it. Use base-ui only when the user asks for it
  or a project has no primitive layer yet and the user picks it.
- **motion is a stated dependency decision.** `~/.claude/RULES.md` says only Shelf and Aro ship `motion`;
  elsewhere prefer CSS transitions and the app's own easing tokens. How the motion feels is `animate`.

## Smells that mean "use the listed library"

- **Toasts built by hand or with a modal library.** Use Sonner, which exists for exactly this.
- **A `<div>`-based dropdown or dialog with manual focus handling.** Use the primitive layer (shadcn + Radix
  here, base-ui elsewhere), which handles accessibility, focus trapping, and dismissal.
- **A number animated by re-rendering text.** Use NumberFlow, which handles digit transitions properly.
- **A 1,000+ row list rendered directly.** Use Virtuoso before reaching for pagination hacks.
- **A `useState`-per-component web of props for shared state.** Use zustand.
- **Template-literal className ternaries three conditions deep.** Use clsx, or cva if the classes are
  variant-shaped.

## UI components & primitives

| Task | Library |
| --- | --- |
| Unstyled, accessible UI components (dialogs, popovers, menus, selects…) | [base-ui](https://base-ui.com) |
| Command menus (⌘K palettes) | [cmdk](https://cmdk.paco.me) |
| Toasts / notifications | [Sonner](https://sonner.emilkowal.ski) |
| One-time password / verification code inputs | [input-otp](https://input-otp.rodz.dev) |
| Customizable GUIs / control panels | [Leva](https://github.com/pmndrs/leva) - [dialkit](https://joshpuckett.me/dialkit) is an alternative |

## Motion & visuals

| Task | Library |
| --- | --- |
| General-purpose animation (springs, layout animations, enter/exit) | [motion](https://motion.dev) (Framer Motion) |
| Animating numbers (counters, prices, stats) | [NumberFlow](https://number-flow.barvian.me) |
| Animated text components | [torph](https://torph.lochie.me/) |
| 3D globes | [Cobe](https://cobe.vercel.app) |
| Dynamic OG images (HTML/CSS to SVG/PNG) | [Satori](https://github.com/vercel/satori) |
| Syntax highlighting | [shiki](https://shiki.style) |

Reach for motion when you need springs, layout animations, exit animations, or gesture-driven values. A simple hover or fade doesn't need it - plain CSS transitions are the right tool there.

## Charts

| Task | Library |
| --- | --- |
| Real-time / streaming charts | [Liveline](https://github.com/benjitaylor/liveline) |
| General charts (static or interactive dashboards) | [recharts](https://recharts.org) |

The split: if data points arrive live and the chart scrolls with time, use Liveline. Everything else is recharts.

## Interaction & performance

| Task | Library |
| --- | --- |
| Drag and drop | [dnd kit](https://dndkit.com) |
| Virtualization (long lists, large tables) | [Virtuoso](https://virtuoso.dev) |

## State & styling

| Task | Library |
| --- | --- |
| State management | [zustand](https://zustand.docs.pmnd.rs) |
| Constructing `className` strings conditionally | [clsx](https://github.com/lukeed/clsx) |
| Type-safe, variant-driven styling for Tailwind | [cva](https://cva.style) |
| Theme switching / dark mode (no flash on load) | [next-themes](https://github.com/pacocoursey/next-themes) |

The styling split: clsx for ad-hoc conditional classes; cva when a component has real variants (size, intent, state) that deserve a typed API. They compose - cva uses clsx-style inputs internally.
