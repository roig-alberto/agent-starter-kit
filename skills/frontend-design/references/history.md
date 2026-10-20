# frontend-design - incident history

The stories behind the rules and gotchas in `SKILL.md`, kept nearly verbatim. Read them when a rule seems
excessive; each one cost real time or reached the user. One heading per source skill, because this skill
merged two on 2026-10-15.

# From frontend-design (part 1, the design method)

## A screen's CSS reached a component inside it (closet, 2026-07-21)

`.notif-head span { margin-top: 2px }` (one class + one element) beat `.tv-toggle-knob` (one class) and
pushed a switch knob 2px off-centre - it read as a broken component, caused by a rule in another file.
Two habits prevent it: scope screen selectors to their own text column (`.notif-head-txt span`, never a
bare `.screen-thing span` any child can match), and write a component's invariants as a DIRECT CHILD
(`.tv-toggle > .tv-toggle-knob`, two classes) so no foreign `.something span` outranks them. **Geometric
hardening alone does NOT save you** - tested: centring with `top:50%` + `translateY(-50%)` while leaving
the offending rule in place, still off-centre. Specificity has to win. Guard: measure every instance in
both themes and **validate the guard by re-introducing the bug** (closet `e2e/controls.py` catches it).

## Adding a dark theme: three audits found 28 real bugs (closet, 2026-07-21)

Eyeballing screenshots found nothing. Three audits over the built pages found 28 real bugs:

1. **AA contrast on every text/background token PAIR** - not "does it look readable". Caught 2 tokens
   below AA, both carrying 9px mono text.
2. **Pixel scan for leftovers of the old theme** - count light-theme-colored pixels on the dark captures.
   Caught nothing real (0.33% max, all photos), which is exactly the point: it PROVED no leaks instead of
   assuming.
3. **"Invisible elements" audit - the one that pays.** For every element with its own background, compute
   contrast against the background of its CONTAINER (not against text). Caught **26**: a switch knob
   darker than its own track (1.4), and dark semantic tints `#241a10` on card `#161614` (1.06) that made
   chips vanish. No visual review sees these; the element is there, just gone.

## Colour concatenation with a var() (closet, 2026-07-21)

`background: color + '18'` where `color` is a `var()` is invalid CSS, so the element silently loses
background AND border - here a 1.5px border loss made the page 2px shorter. A literals-only grep misses
every one of these.

## One class prefix spanned two contexts (closet, 2026-07-21)

Treating all of `.pcs-` (a colour picker) as "sits on top of the photo" and mapping its whites to
`--ink-on-media` (deliberately white in both themes) was wrong, because that one prefix spans TWO
contexts: the markers and loupe DO sit on the photo, but the result panel is ordinary INTERFACE. Dark
theme got a white panel with pale text, plus a CTA in white-on-yellow. A prefix is a naming convention,
not a context. **The user found this in production**, because route-based screenshot sweeps never reached
it - the screen only exists two clicks deep inside an edit overlay. Automated capture runs must include
second-level overlays, not just routes.

## "This screen is still dark" after a token change (closet, 2026-07-22, 3 rounds with the user)

A contrast pass remapped card/muted-text/border tokens and three screens stayed black anyway: their
content was photo+text straight on the canvas with no surface underneath, so there was no token to raise.
Measuring the computed `backgroundColor` of its cards first (it read `rgba(0,0,0,0)`) showed the cause.
The fix is giving the content a surface, not pushing the theme further.

## Two checks that lied

- **Comparing screenshots by BYTES.** Two captures identical on screen differ by tens of bytes from the
  PNG encoder (4 of 27 files). A diff must count PIXELS (drawable in a Chromium canvas via Playwright, no
  PIL needed).
- **Comparing against a baseline captured "a while ago"** when the screen has live content (an hourly
  weather strip re-renders). The honest baseline is captured WITH the change and then immediately again
  after `git stash`. Also: a baseline is contaminated if the splash is still up - a "there is text" check
  passes anyway because the content is already in the DOM underneath. Wait for `state='detached'` and
  disable animations/caret.

# From ui-design-references (part 2, the taste library)

`ui-design-references` was a separate skill until 2026-10-15. It held the liked-UI images, their table
(then `references/examples.md`, now `references/ui-examples.md`), and the hand-off fidelity rule. Before the
merge, part 1 pointed at it for the hand-off wording, and the "offer the choice first" rule pointed at
`new-project` Phase 3 for the new-app fork; that skill is now `new-app`. Its old description triggered on new-project Phase 3
or bootstrap-orchestrator's design step, or 'what look do I want / make it look good'.

## Design agents build clickable prototypes by default

The fidelity rule is a standing user preference, and it is the one thing a design agent gets wrong by
default: asked for "a design", it builds an interactive or clickable prototype. The user reviews design as
a set of frames side by side. A clickable prototype hides states behind interactions, so states go
unreviewed and unbuilt, and the prototype's code is not the app's code: it is throwaway work priced as a
deliverable. Hence the verbatim wording in every `PROMPT.md` and every in-house pass.

## "Remind me to give it to the design agent"

The user asked to be reminded to hand the liked-UI examples to the design agent. The concrete meaning is
the bundle step: copy `references/ui-examples/*` into every design hand-off bundle. The reminder lives in
this skill and fires whenever it loads for a design task.

## How the accent gets picked

The user picks accents by comparison board, not from a single mock (`ui-examples3.png` and
`ui-examples4.png` are exactly that shape). Accents close to green or red were rejected because green
(done) and red (destructive or exclude) are already spoken for.
