# Undo over append-only history, and read-only prod scripts

## Undo over an append-only history (lumo, 2026-10)

- **Postgres jsonb reorders object keys.** A layer stored inside a history row never `JSON.stringify`-equals
  the same row read from its table. Compare with sorted keys (a canonical stringify).
- **"Undo = go to seq p-1" walks time, not content.** After undo, a new edit, undo, undo, the step you undid
  comes back. Resolve the undo target through the undo row's `restores`, and keep redo as a stack replayed
  from the base. Three plan reviews missed this; tracing one sequence by hand found it. Write that sequence
  as a test.

## A script that must only read a prod database (finance-proj, 2026-10)

Enforce it in the connection, never in a comment. Append `?default_transaction_read_only=on` to the
postgres.js URL (unknown URL params become connection parameters). A write then fails with SQLSTATE 25006
(measured on `caudal_demo`). Set the env before the module that opens the pool is imported, which means a
dynamic `await import`. A review pass flagged the comment-only version.
