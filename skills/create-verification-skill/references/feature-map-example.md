# Feature map example (shape only)

Adapted from pstack's worked example. Every feature file starts with an H1 and one paragraph of user-visible
behavior, then exactly these four H2 sections in order.

```markdown
# Create a note

Create note lets a user save a titled note from the browser, cancel an unfinished draft, and confirm the saved
note from a second view.

## Sub-features

- `create-open` opens a blank editor from each entry point.
- `create-save` persists a title and body.
- `create-cancel` discards an unfinished draft.

## How to get to it (user POV)

- Choose the `New note` button in the toolbar.
- Press `n` while focus is outside an editable field.

## Driving it with chrome-devtools-axi

Preconditions:

- Doctor passes and no note is titled `Release checklist`.

- **Open editor.** Choose `New note`: `snapshot`, then `click @<uid of New note>`. A form named `Note editor` appears with focus in `Title`.
- **Save note.** `fill @<Title uid> "Release checklist"`, re-snapshot, `click @<Save uid>`. A status `Note saved` appears.
- **Confirm persistence.** Reopen the note from `All notes`; the editor shows the saved values.
- **Proof.** `screenshot <evidence-dir>/create-note/list.png` showing the list with the new note.

## Gotchas

- Pressing `n` inside a textbox types the character instead of opening the editor.
- A save status alone is not proof; reopen the note from the list.
- Remove the note during cleanup but keep the screenshot.
```
