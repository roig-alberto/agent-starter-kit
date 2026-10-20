# Logic prototype

Adapted from mattpocock/skills `prototype` LOGIC.md (MIT, commit 49dd158). One self-contained HTML file that lets
anyone drive a state model by clicking buttons. Use it when the question is about business logic, state changes
or data shape: the kind of thing that reads fine on paper and only feels wrong once real cases go through it.
Because it is one file with nothing to install, the user can open it on a phone and feel the model before an
agent builds it.

## When it is the right shape

- "I'm not sure this flow handles the case where X happens and then Y."
- "Can this data model represent the case where..."
- "What should the API look like?" before writing it.
- Anything where someone wants to press buttons and watch the state change.

## Steps

1. **State the question.** One paragraph, visible at the top of the page, not only in a comment: which state
   model, and which question it answers. A prototype for the wrong question is pure waste.
   Done when: the question is the first thing on the page.
2. **Isolate the logic in a pure module.** One `<script>` block that could be lifted into the real code later.
   Pick the shape the question needs: a reducer `(state, action) => state` for discrete events; a state machine
   when "which actions are legal right now" is part of the question; plain functions over a data type when there
   is no current state; a small class when the logic truly owns ongoing state. No DOM, no `document`, no button
   handlers inside it: the page calls in, nothing flows back.
   Done when: the module has no reference to the page.
3. **Build the page for a non-developer.** Plain HTML, CSS and JS inline: no framework, bundler or server, so it
   opens by double-click and survives being sent around. Every label in the product's words, not the code's.
   Top to bottom:
   1. the title and the one-line question;
   2. the current state as a readable panel of labelled fields (not a raw JSON dump), re-rendered after every
      click, with what just changed called out;
   3. free-play buttons, one per action, always available;
   4. guided walkthroughs, one tab per scenario: a short description of the situation and what to watch for,
      then the ordered buttons to press. Starting a walkthrough resets to a known state, so it runs the same way
      every time. Cover the happy path, a tricky edge case, and an attempt at something that should be illegal.
   5. a "Copy what I found" button: it copies the question, the clicks so far and the current state as a message
      to paste into the chat, so a finding on the phone ("this transition should not be possible") reaches the
      agent without typing. Same clipboard fallback as `picker.md`.
   Clean and restrained: clear type, generous spacing, one accent color, no animation.
   Done when: every walkthrough runs start to finish and the state panel changes on every click.
4. **Hand it over.** Send the file so it renders on the user's phone, or put it in the inbox share. The useful
   moments are "wait, that shouldn't be possible" and "I assumed X would differ": those are bugs in the idea.
   Add actions or scenarios when asked.
5. **Capture.** The validated module goes into the real code; the page stays on the `prototype/<slug>` branch,
   still runnable by double-click; the verdict goes in the plan or decision log.

## Anti-patterns

- **Tests.** A prototype that needs tests is no longer a prototype.
- **The real database.** In-memory state, unless persistence is the question.
- **Generalizing.** It answers one question; no "what if we later support X".
- **Logic mixed into the page.** A module that touches the DOM is no longer liftable.
- **A framework, bundler or dev server.** It defeats "open the file".
- **Shipping the page.** It is built for clicking through by hand; only the module is worth keeping.
