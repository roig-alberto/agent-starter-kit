# Close-out checklist (step 6)

1. **Tick or append `FEATURES.md`** with the date and a one-line note.
2. **Update the project AGENTS.md** if a convention or a fact changed, and `ARCHITECTURE.md`, `GLOSSARY.md`
   or `CODEMAP.md` (skill `architecture`) if the change moved ownership, stored data, a trust boundary,
   deployment, a main folder or a domain word, and `REVIEW.md` if the change added a system rule or a bug
   class a reviewer should now check; then run its path check.
3. **Run the harvest check.** Read the "## Pending" section of `~/.claude/HARVEST.md`. It is the durable
   inbox: flags land there the moment a trigger fires, so it survives compaction and /clear, and it may
   also hold entries a PREVIOUS session never processed. Then sweep the triggers one final time: more
   than 5 minutes that a recipe would erase, a failed approach, a repeat from another project, a settled
   library-versus-alternative question, or a clean first-try win worth making the default. Offer to
   process each one with `retro` (it writes accepted ones through `knowledge-authoring`), and tick the
   processed lines.
4. **Record feature-level decisions where they survive.** If this feature involved a real fork (you chose
   A and rejected B), add it to the "Rejected / parked" section of the project's IMPLEMENTATION_PLAN.md in
   the `new-app` format: Decision, Why not B, and **what would change the answer**. Without this, the
   next session re-litigates B.
5. **Report** what shipped, an evidence summary, and anything deliberately left out of scope.
6. **Tear down the dev environment.** If verifying in step 5 required bringing up a dev container, or a
   dev container is left running only for this work, remind the user and offer to stop it
   (`docker compose stop <dev services>`). Idle hot-reload dev containers leak GBs of RAM on this box (see
   `fleet-ops`), so do not leave one running past the task. Never auto-stop it, because the user may still
   be looking.
7. **Offer, never auto-run,** a commit, and a prod redeploy if the user wants it live. The batch-redeploy
   rule applies: do not rebuild per tweak.
