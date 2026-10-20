# Prototype history

## 2026-10-16: logic branch merged (skills redo, phase 4)

Until 2026-10-16 the skill built UI variants only, and carried `disable-model-invocation: true`, so it never ran:
the user never types skill names. The flag was removed and a real description written the same day.

Merged from mattpocock/skills `prototype` (MIT, commit 49dd158):

- The branch choice by question: "what should this look like" against "does this logic feel right", and the
  default when the user is away (pick by the surrounding code, state the assumption).
- The logic branch (`references/logic.md`): a pure liftable module, one double-click HTML file, free-play
  buttons and guided walkthroughs, written for a non-developer.
- The shared rules: throwaway and named so, trivial to run, no persistence, surface the state, capture the answer
  and keep the prototype as a primary source on a throwaway branch.
- From its UI branch: prefer variants on the existing page behind `?variant=` over a bare route, because an empty
  route hides design problems.

Kept from the earlier version: the named-axis divergence, Emil Kowalski's craft bar, the verbatim picker
(`references/picker.md`), the six-phase workflow and the invocation table. Changed: "delete the prototype surface"
became "remove it from the working branch and keep it on `prototype/<slug>`", following Matt's capture rule. Added
for this user: hand-off to a phone (an attachment that renders, or the inbox share).

## The Copy button (2026-10-20)

From Anthropic's "The unreasonable effectiveness of HTML" post: two-way pages whose "copy as prompt" button hands the
user's changes back to Claude Code. Added to the picker and the logic page so a pick made on the phone needs no typing.
