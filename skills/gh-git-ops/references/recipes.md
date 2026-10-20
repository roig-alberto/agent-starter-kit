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
