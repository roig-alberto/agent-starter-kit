---
name: gh-git-ops
description: >-
  Route git and GitHub actions through the gh CLI on this machine instead of raw git-over-HTTPS or
  hand-configured remotes. Use when you are about to create a GitHub repo, add a remote, push a new
  project, open or review a PR, or otherwise touch GitHub, in any project in the distro (dev-system,
  mycloset, personal-dash, finance-proj, etc.), even if the user only says "push this", "make a repo",
  "put it on GitHub", "add a remote", "open a PR", or "use gh". NOT for a secret or token question
  (use `security` (not in this kit)) or a host-level backup (use `backups-and-alerts` (not in this kit)).
---
---

# gh-git-ops

Do every git and GitHub action through the `gh` CLI rather than raw `git` over HTTPS or hand-edited
remotes. This is the user's standing preference: the distro is already authenticated through gh, so gh
reuses that auth and no token or remote fiddling is needed. The skill also carries the identity,
visibility-default, and auto-classifier gotchas that were learned the hard way.

## Rules

- **Use the gh account `<github-user>`** and confirm it with `gh auth status`. The git protocol is HTTPS
  and the scopes are `gist, read:org, repo`, so gh can create repos and PRs without a new token.
- **Commit as the distro identity** `user.name=<user>`, `user.email=you@example.com` (set
  globally). Some older repos were authored `<user>` from the Windows side; that is fine, and you do not
  rewrite history to "fix" it.
- **Never add a `Co-Authored-By` trailer** on this user's repos. It is their standing rule.
- **Create a repo and push it in one command:**
  `gh repo create <name> --private --source=. --remote=origin --push`. The `--source=.`,
  `--remote=origin`, and `--push` flags wire the remote and push in one shot.
- **Default to `--private`.** Home-infra repos (dev-system and others) carry LAN IPs, tunnel hostnames,
  chat_ids, and NAS host keys, so never use `--public` without an explicit ask.
- **New repos use `main`; an existing repo keeps its branch.** Most local repos here use `master`
  (agent-factory, glow, loop, personal-dash, beszel) and recall, shelf and mycloset use `main`, so run
  `git branch --show-current` and never assume. The rename recipe for a new repo is in
  `references/recipes.md`.
- **Check whether a repo exists with `gh repo view`** instead of guessing. It errors cleanly with
  "Could not resolve to a Repository" when the repo is absent.

## Gotchas

- **The auto-mode classifier blocks `gh repo create`.** It publishes to an external service, so the
  Claude Code auto-mode classifier allows it only when the *user explicitly* asked to create the repo AND
  a visibility was chosen. A standing "use gh" preference is NOT enough on its own; confirm private or
  public with the user, then run it. Pushing to an already-existing remote the user set up does not hit
  this gate.
- **Commits fail with "empty ident name" in a fresh distro repo.** Set the identity once:
  `git config --global user.name <user>; git config --global user.email you@example.com`.
- **`gh repo create` pushed `master` on a new repo.** It pushes the local default branch; rename it with
  the recipe in `references/recipes.md`. Do not rename an existing repo's branch.
- **A gh command wrapped in sudo fails.** rtk and sudo collide on this box; this is irrelevant to gh
  itself, so simply do not wrap gh in sudo.

## References

- `references/recipes.md`: the exact command blocks for creating a repo, adding a remote to an existing
  GitHub repo, renaming `master` to `main`, and working with PRs.
