# INSTALL.md - how this setup gets onto a machine

This machine was set up from the agent starter kit. Its README is the install guide: prerequisites, the "Tools and
plugins" table (rtk, gitleaks, playwright, graft and the rest, one install line each), `install.sh`, and the steps after
install. Keep a clone of the kit, or re-clone it, to look things up.

Quick checks that the wiring works:

```sh
bash ~/.claude/scripts/guards-test.sh            # ends with "guards-test: all passed"
python3 ~/.claude/scripts/knowledge-lint.py      # 0 errors
command -v rtk gitleaks                          # both found; the hooks need them
```
