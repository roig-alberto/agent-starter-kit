# Bitter lesson: one-shot

Why each tagged line in `SKILL.md` exists, and when a "soft" line may go. Read only when evaluating the skill,
never while building a feature. Tags: `invariant` keeps the line for good (a feedback signal, a fact about this
box, or a rule of the user's); `soft` is workflow coaching a stronger model may not need. Checked by
`~/.claude/scripts/bitter_lesson.py` through `knowledge-lint.py`; plan in `~/.claude/BITTER-LESSON-PLAN.md`.

| Item | Tag | Why | Review | Delete when | Ablation |
|---|---|---|---|---|---|
| Run the steps IN ORDER | soft | Rigid-workflow coaching: write "nothing applies" instead of skipping. | 2027-04-27 | A with/without run on small features still walks every step that applies. | |
| 0. Load the ground truth | invariant | Each repo's facts and commands live only in its docs. | | | |
| 1. Clarify with grill-me | invariant | The user's rule: over-clarify rather than rebuild. | | | |
| 2. Run the implication sweep | invariant | The table holds this box's implications (secrets, backups, migrations) no model can infer. | | | |
| 3. Plan, sized to the change | soft | Coaching on when a change needs a written plan. | 2027-04-27 | A with/without run sizes plans the same way. | |
| 5. Verify with evidence | invariant | The full suite and the verify skills are the feedback signal. | | | |
| 6. Close out | invariant | The user's doc contract (FEATURES.md, AGENTS.md, harvest). | | | |
| Never silently invent a new visual direction | invariant | The user's design rule for existing apps. | | | |
| Always request hi-fi STATIC wireframes | invariant | A standing user rule for design hand-offs. | | | |
| Use the narrowest honest check | invariant | This box's cost and memory limits: no prod rebuild per edit. | | | |
| Never step around a pre-existing red check | invariant | The user's quality bar, earned by the typecheck drift in references/history.md. | | | |
| You are about to hand-roll a domain concept | soft | Earned by the Caudal incident, but it is coaching to grep first. | 2027-04-27 | A with/without run on a feature that touches an existing concept finds the existing function either way. | |
| A dev container is still running | invariant | A fact about this box: idle dev containers leak RAM. | | | |
