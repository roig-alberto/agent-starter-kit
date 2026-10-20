# Skill style (the shape every SKILL.md follows)

`knowledge-lint.py` enforces the mechanical parts of this file. The rest is judgment.

## Frontmatter

- `name` equals the directory name.
- `description` says what the skill does, then "Use when ..." with the phrases a user says and the symptoms
  that should load it, then `NOT for X (use Y)`. No answers, fixes, commands, dates, or history.
  Aim for 600 characters or fewer; a merge of several skills may use up to 800. The linter rejects more than 800.
- Never summarise the steps in the description. An agent that reads a step summary acts on it and skips the body.
- Never add `disable-model-invocation: true`, and remove it when you find it. The user never types skill names,
  so a skill the model cannot invoke is a skill that never runs.

## Body (150 lines at most, aim for 100, under 15,000 characters)

Agent Factory's skills menu cuts a skill at 15,000 characters (`readSkill` in `server/skills.ts`, verified
2026-10-15), so a longer body loses its tail there.

Use these sections in this order. Drop a section that has nothing to say.

1. **Opening paragraph.** What the skill is for and the failure it prevents, in two or three sentences.
2. **Steps** or **Rules.** Imperative. One rule per bullet: the rule, then one short sentence of why.
   Steps that produce an artifact say what the artifact is. Every step ends in a `Done when:` line that
   names the observable check proving the step is finished (a command output, a file that exists, a count).
3. **Red flags.** A short list, only for mistakes agents really made on this box. Each one is backed by an
   entry in `references/history.md`. No generic red flags: a model already knows them, so they are noise.
4. **Gotchas.** One bullet each: the symptom, then the fix.
5. **References.** One line per `references/*.md` file saying when to read it.

## Writing

- Full sentences with articles and verbs. No fragments, arrows, or invented abbreviations; a weaker
  model misreads compressed text.
- No long dashes. Use a hyphen, a comma, or a new sentence.
- Name the real command, path, flag, or error string. Never a vague description of it.
- Live facts (ports, container names, hostnames, images, volumes) are never restated. Point at
  `~/.claude/FLEET.md`, which a script generates from the running system. A command that needs a container
  name may use it.
- Dates appear only on facts that can go stale, as `verified YYYY-MM-DD`. Nothing else is dated.
- Label claims by evidence when it matters: measured, inferred, or guess.
- Write for every agent (user, 2026-10-16). Say "the agent" or "any agent"; name a specific agent only
  for a fact about that agent (a path, a flag, a limit). Name the repo rules file `AGENTS.md` (in every repo here
  a link to `CLAUDE.md`). Shared files keep their real paths, such as `~/.claude/RULES.md`.

## Where history goes

Incident stories, measurements, costs ("took 20 minutes"), and "first seen on" notes do not belong in the
body. Move them, nearly verbatim, to `references/history.md` and keep the lesson they taught in the body as
one rule plus one sentence of why. When skills merge, `references/history.md` gets one heading per source
skill. Never delete knowledge during a rewrite: every code span, URL, and quoted trigger phrase must survive
somewhere in the skill directory. Check with:

```bash
python3 ~/.claude/scripts/knowledge-preserve.py <skill-name>
python3 ~/.claude/scripts/knowledge-preserve.py <new-skill> <git-ref> --from <old1,old2>   # after a merge
```

## Done means

```bash
python3 ~/.claude/scripts/knowledge-lint.py | grep '<skill-name>/'   # no ERROR lines
python3 ~/.claude/scripts/knowledge-preserve.py <skill-name>        # 0 lost tokens
wc -c ~/.agents/skills/<skill-name>/SKILL.md                         # under 15000
```
