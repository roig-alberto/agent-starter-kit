# A change that keeps behaviour (refactoring)

For a change that reshapes code without changing what anyone sees: a rename, a split, moving code, replacing an API,
deleting dead code. If the cleanup finds a bug or a missing feature, split it out and ship the structure first,
against the pin. Adapted from pstack's refactoring playbook (2026-10-16).

1. **Pin the behaviour before moving anything:** a test that already covers the area, or a characterization test, a
   snapshot or a script that records today's outputs. A typecheck and lint are not a pin.
2. **Delete before adding:** dead code, one-caller wrappers, duplicate checks. The smallest reshape that reaches the
   target wins; a cleanup that only "might help" is reverted.
3. **Move every caller and delete the old shape in the same change.** No shim, and no old and new paths side by side.
4. **After a rename, grep the old name everywhere,** strings, docs, comments and config included: a rename misses those
   silently (the same ripple check as `knowledge-authoring`).
5. **Prove the outputs are unchanged on the real thing:** the pin green, and for a bigger reshape a diff of old against
   new outputs on the same input.
6. **Keep it only if the code got easier to read** (fewer branches, fewer states, fewer files to open for one task);
   otherwise revert it.
7. **Commit in order:** the deletions, then the reshape, then any cleanup, each one green.
