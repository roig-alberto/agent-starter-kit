# Plain history

## 2026-10-16: built in phase 1 of the skills redo

Adapted from mattpocock/skills `wait-what`, a three-line skill: "Wait, I don't understand where you've got to
here. Re-pitch that: give me a little bit of context, talk in ASD-STE100 Simplified Technical English, and use
the ubiquitous language from `GLOSSARY.md`." Its docs make two points kept here: the leading word "wait" names the
listener's state, so the model backs up and explains instead of clipping words (an instruction like "be concise"
produces fragments that are shorter and no clearer); and the skill stays short, because a model copies the length
of a skill rather than its request.

Two changes on purpose. Matt hides it from the model (`disable-model-invocation`), arguing only the user knows
when they stopped following; here the user never types skill names, so it loads from the plain words they use.
And the register is the RULES.md reply style, which already is a Simplified Technical English layer.

Evidence, one session on 2026-10-16: the user asked "what do you mean about this?", "what is the purpose of worth
it when?", "what is this?" and "i do not understand this" (twice in that form or close to it), and once replied
"i meant ..." after a reply answered the wrong reading of their question. Step 3 covers that last case.
