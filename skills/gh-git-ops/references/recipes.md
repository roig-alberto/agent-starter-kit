# gh-git-ops recipes

## Create a repo and push a local project

```bash
cd <repo>
gh repo create <name> --private --source=. --remote=origin --push
```

Default to `--private`. The `--source=.`, `--remote=origin`, and `--push` flags wire the remote and push
in one shot. Confirm the visibility with the user first, because the auto-mode classifier blocks this
command otherwise.

## Add a remote to an existing GitHub repo

```bash
gh repo view <owner>/<name>            # confirm it exists
git remote add origin https://github.com/<owner>/<name>.git
git push -u origin main
```

## Branch naming

New repos use **`main`** (this matches the `~/.agents/skills` repo). An existing repo keeps its branch:
run `git branch --show-current` and never assume. Most local repos here use `master` (agent-factory, glow,
loop, personal-dash, beszel), and recall, shelf and mycloset use `main`. For a NEW repo, `gh repo create`
may push the local default branch (`master`). Normalize it like this:

```bash
git branch -m master main
git push -u origin main
gh repo edit --default-branch main
git push origin --delete master
```

## Pull requests

```bash
gh pr create --fill            # or --title/--body
gh pr view --web
gh pr checks
```

## Make a repo public

1. **Review the whole tree, not a diff.** A diff-by-diff review missed the weak-spot map (accepted holes, vault
   access, services that skip the gate) that one full-tree review found.
2. **Rewrite commit metadata first.** Commits carry the real email. Rewrite to the GitHub no-reply address
   before publishing (the repo-local git config in `~/.claude/ENVIRONMENT.md`'s starter-kit entry shows it).
3. **Change visibility with the API.** This box's `gh repo edit` has `--visibility` but no
   `--accept-visibility-change-consequences`, so it cannot run headless. Use:

   ```bash
   gh api -X PATCH repos/<owner>/<repo> -f visibility=public
   ```

   Checked against `gh api --help` (`-X`, `-f`) on 2026-11-10; read `gh repo edit --help` through `rtk proxy`.
