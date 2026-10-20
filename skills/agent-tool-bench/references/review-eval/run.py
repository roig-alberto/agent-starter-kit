#!/usr/bin/env python3
"""Reviewer recall eval: does `review-diff` flag a real bug when shown only the commit that introduced it?

Usage: run.py <arm> <model> <effort> [repeats=2] [case-id ...]
  Each case is reviewed in a throwaway shared clone checked out at the introducing commit, with --base at its parent,
  so the reviewer sees exactly that commit's diff and the repo's REVIEW.md as of the parent. The user's repos are only
  read. Output: out/<arm>/<case>-<n>.txt (the review) and .json (tokens, seconds). Run one arm at a time: several
  claude -p processes at once exhaust this box's memory. Score with judge.py.
"""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    arm, model, effort = sys.argv[1:4]
    repeats = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    only = set(sys.argv[5:])
    cases = [c for c in json.load(open(f"{HERE}/cases.json")) if not only or c["id"] in only]
    out = f"{HERE}/out/{arm}"
    os.makedirs(out, exist_ok=True)
    for c in cases:
        for n in range(1, repeats + 1):
            dst = f"{out}/{c['id']}-{n}"
            if os.path.exists(f"{dst}.json"):
                continue  # resumable: a finished run is never paid for twice
            tmp = tempfile.mkdtemp(prefix="review-eval-")
            try:
                repo = os.path.expanduser(c["repo"])
                subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", repo, f"{tmp}/r"], check=True)
                subprocess.run(["git", "-C", f"{tmp}/r", "checkout", "-q", c["intro"]], check=True)
                t = time.time()
                r = subprocess.run(["review-diff", "--repo", f"{tmp}/r", "--base", f"{c['intro']}^", "--model", model, "--effort", effort],
                                   capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900)
                open(f"{dst}.txt", "w").write(r.stdout)
                json.dump({"case": c["id"], "arm": arm, "model": model, "effort": effort, "exit": r.returncode,
                           "seconds": round(time.time() - t), "usage": r.stderr.strip().splitlines()[-1:] }, open(f"{dst}.json", "w"))
                print(f"{arm} {c['id']}-{n}: exit {r.returncode}, {round(time.time() - t)} s", flush=True)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
