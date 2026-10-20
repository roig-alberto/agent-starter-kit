# context-mode: the worked verdict (2026-09-05/06)

The full evidence behind the two rules in `method.md` (chosen versus used), which `SKILL.md` also
states - test the tool in the mode it was
designed for, and purge shared state between arms. Kept here because it is a long narrative, not
a rule.

**And test the tool in the mode it was DESIGNED for before rejecting it.** The first context-mode
verdict here was reached on MCP-only, and the claim that "forcing the tools is the ceiling, so
hooks could only be worse" was reasoning, not measurement - the plugin's hooks route SELECTIVELY
(an allowlist of trivial commands, a size threshold, hard redirects only for curl/wget), which is
strictly smarter than the ban-Bash-entirely arm that stood in for them. The user caught it. Run
with hooks, n=3, purged between runs, same task, all correct:

| arm | tokens | turns | ctx calls |
|---|--:|--:|--:|
| baseline, no hooks, no MCP | 102,102 | 4.3 | 0 |
| ctx hooks + MCP, no rtk | **231,734** | 10.0 | 1.0 |
| ctx hooks + MCP + rtk | 107,802 | 3.0 | **0** |

Conclusion held, for a better reason: hooks make it **+127% tokens**, and on THIS box rtk's
PreToolUse hook (listed second) wins the rewrite and neutralises context-mode's routing entirely -
zero tool calls, back to baseline. Installing the plugin here would be inert.

**Purge shared state between arms or they are not independent.** Two runs isolated by
`--strict-mcp-config` and separate settings files still contaminated each other through
context-mode's shared SQLite store: arm C's `ctx_search` served back arm A's captured output as
that session's own "prior session" history, with the numbers misattributed. Any tool with a
cross-session store needs a hard purge in the runner, not just process isolation.
