# The standout checklist (part 3 of `frontend-design`)

Walk this before a new app's design is called done, and before a new screen ships in an existing app. It prevents
the "vibe-coded" look: a static, generic app that works but nobody remembers. Source: Chris Raroque (solo developer
of the Ellie, Luna and Amy apps) on Greg Isenberg's channel, "How I Design Apps 10x Better", watched by the user
2026-10-21 (https://www.youtube.com/watch?v=jSWuepkuFrU). His figures are cited, not measured on this box. The user's
recordings and screenshots behind the examples below are kept in `~/projects/lumo/ui/refs/recordings/` and
`~/projects/lumo/ui/refs/purist/`.

Each item is a question for the design or the build. "How" points at the skill that owns the mechanics. The exact
values for every motion below are in the `animate` playbook, section "Patterns from reference recordings".

## 1. Motion and interaction (the number one lever)

- **Does every wait have a designed state?** A "searching" label with a moving gradient and results sliding in,
  instead of a static "Calculating". The same app concept got about 7 likes without it and about 800 waitlist
  sign-ups with it, one day apart. How: `animate`. The user's recording of it (Amy, 2026-10-21): you type a meal as
  a plain line ("In n out shake and burger"), and at the right end of that line, small and grey, the wait tells a
  story in place: "searching" with a light sweeping across the text, then a stack of overlapping source icons
  with "9 sources", then "calculating" with the same sweep, then the result ("970 cal") fades in with a small
  chevron that opens the sources. Each stage replaces the last in the same spot; nothing jumps or spins.
- **Do page changes move?** A short slide with a slight bounce between pages, instead of an instant swap.
- **Do menus and sheets arrive with a bounce?** A menu or sheet slides up from the bottom, overshoots a little and
  settles, with a soft shadow, instead of fading in or appearing flat.
- **Do screens and sheets work as one stack?** The user's recording of Luna (2026-10-21), frame by frame:
  - Tapping a row raises its detail sheet from the bottom in about a fifth of a second. The page behind shrinks a
    little and darkens into a card, so you see the sheet sits on top of it. Closing slides the sheet down and the
    page grows back.
  - A multi-step sheet keeps its place while its steps slide sideways inside it: the add sheet opens on a keypad,
    "Continue" pushes the form in from the right (the amount moves up into the header), the back arrow slides the
    keypad back in from the left.
  - Leaving a category page shrinks it back into the row it opened from, so you land where you started.
  - Switching tabs slides the new screen in from the side of the tab you tapped, with the slight bounce above (as
    he describes it in the talk; too fast to read at the frame rate checked).
- **Does a control turn into its next step instead of opening something new?** The user's reference
  (`ui-examples/ui-examples5.png`, recorded 2026-10-21): tapping the microphone in the chat input makes a black pill
  grow out of the microphone until it fills the input, showing a cancel cross, a sound line, "Listening..." and a
  tick; confirming or cancelling shrinks it back into the microphone. The send icon also turns into a tick.
- **Does the idle screen breathe?** In the same reference, the empty assistant screen shows the mascot with small
  food icons around it that float up and down a few pixels, each slightly out of step, as a slow loop.
  The user's rule (2026-10-21): any empty state, or any screen where an icon would sit still, gets one quiet
  loop: the icon bobs a few pixels, a rocket's flame flickers while it floats, a bell swings a little.
- **Do numbers and charts arrive alive?** The user's recording of Luna (budgeting, 2026-10-21): a chart line draws
  itself from left to right when its tab opens; account rows carry small sparklines; typing an amount on the
  keypad grows a big green number digit by digit ("$45", then "$458"); after saving, that same number travels and
  shrinks into its place in the transactions list, so you see where it went. Tapping a row slides its detail up
  from the bottom as a sheet; tapping a category pushes its page in from the side.
- **Is there one playful moment, tied to a reward?** The user's recording of Amy's streak badges (2026-10-21): a
  streak calendar of green dots sits above a grid of illustrated badges, each with its name ("Ellie, Day 1"), a
  rarity (Common, Epic) and a small progress bar to the next one. Tapping a badge raises a sheet with the badge
  large. Dragging a finger on it tilts the card in 3D toward the finger like a holographic sticker, and the
  drawing cross-fades into the real photo it was drawn from ("View inspiration"); letting go settles it flat
  again. Streaks and badges are the habit loop; the tilt is what people share.
- **Can you describe each motion in plain words?** Agents build these well when the motion is named precisely
  ("slide over, slight bounce"), then tuned for speed and bounce in a few prompts. Naming effects: `animate`.

## 2. Mascot and illustrations (personality)

- **Do the empty states, search, onboarding and splash have a character instead of a bare icon?** An animated,
  illustrated onboarding was the most praised part of his calorie app; one tester signed up twice to see it again.
- **Is the base character original?** Start from original art (commissioned, around $200-300 in his estimate, or
  drawn), then let an image model make the variants. Mixing two or three references gives a more unique result than
  one; never copy an existing brand mascot one for one.
- **Prompt one change at a time.** Asking an image model for several changes at once makes it drift into its
  generic house style. He found ChatGPT better for a first character and Nano Banana better for iterations.
- **Does the mascot move where it matters?** An image-to-video model (he used Midjourney with the still as the
  start frame) turns a still mascot into a loop for the splash or login screen.

## 3. Icons and type (the quickest fix)

- **One icon set, one style.** Outline icons, with the selected tab switching to the filled version, is his
  default; mixing outline and filled icons, or icons from two sets, is a common tell.
- **The user's rule (2026-10-21): icons come from Heroicons, Font Awesome or Nucleo,** one set per app, named in
  `DESIGN_TOKENS.md`. An existing app on another set (Lucide) moves only when the user asks.
- **Is every text size on the type scale,** with weights and greys used for one meaning each? Readability on a
  phone matters more than the typeface.

## 4. Never an empty prompt

- **Does every text box an AI or search sits behind offer starter chips?** For example "What's next" and "Plan my
  day" above the input, chosen by studying how ChatGPT and Claude do it. People facing a blank box do not know what
  to type.

## 5. Presence outside the app (native apps only)

- **Native iOS app: is there a home screen widget, a lock screen widget, a Watch app?** He reports retention more
  than doubled after shipping widgets; the lock screen holds at most 4 widgets, so a slot there is seen many times a
  day. With an agent, a widget took him 4-5 hours instead of 1-2 weeks.
- **The user's apps are PWAs** (`pwa-patterns`; user, 2026-10-21): no widgets, no lock screen, no Watch screens, no
  haptics and no App Store screenshots, because a Home Screen web app gets none of them. Skip sections 5 and 6's store
  item for every PWA; the nearest lever for daily presence is Web Push. Revisit only if an app goes native.

## 6. The first impression

- **For an App Store app: are the store screenshots designed** as carefully as a YouTube thumbnail? They decide
  whether anyone installs it. Reference feed: the "Screenshot First Company" account on X.
- **For any app: would a 20-second concept video of it stop a scroll?** Posting the video before building is a
  cheap validation; rendering one in code: `launch-motion` (not in this kit).

## 7. Keep the eye trained

He studies Mobbin (paid screenshot library), 60fps and Spotted in Prod (motion from top apps), and screen-records an
app he likes, then slows the recording down to see the motion. The agent cannot log into these sites; the user's
screenshots and recordings go in through the taste library (part 2) or `animate` (copy motion from a recording).
