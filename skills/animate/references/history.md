# History

## 2026-10-16: six skills folded in, word for word

On 2026-10-15 a skills redo merged review-animations, improve-animations, find-animation-opportunities,
animation-vocabulary, emil-design-eng and apple-design into this skill and rewrote their text. The user did
not want that: these skills hold specific ideas that work in their projects and must not be generalised. On
2026-10-16 all seven were restored byte for byte from the skills repo (commit `a94a9c0`), and the user chose
to keep one skill: animate's own text unchanged, the six others copied byte for byte into
`references/<name>/` (each `SKILL.md` renamed `main.md` so no client loads a nested copy as a second skill),
and only animate's description widened so the six still trigger. Rule for future edits: never rewrite the
text of these guides; add new material as new files.

The user's Linear motion work (2026-10-14, copied frame by frame from iPhone screen recordings) was in
`~/projects/agent-factory/docs/UI-PLAYBOOK.md` and moved word for word into `references/ui-playbook/main.md` on
2026-10-16 (user: the skill is the source for motion); `references/copy-motion-from-recording.md` holds the general
method. The old description of animate, before it was widened: "Build a web animation from scratch, deciding
in order whether it animates, why, the tool, properties, curve, duration and exit."

## 2026-10-16: `animate-expo` and `write-swift` deleted

The user approved deleting both skills. Checked first: no project under `~/projects` or the Windows
projects folder uses Expo or React Native, and the only Swift on disk is in a third-party clone
(openclaw) with no commits by the user. Both stay in the skills repo's git history if a native app starts.
