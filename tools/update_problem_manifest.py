#!/usr/bin/env python3
"""
Update a problem's own manifest.json (problems/batch/Mock_K/N/manifest.json) after adding or changing tests.
That file lists every test with the SHA-256 of its input and of its (normalized) output, and whether the files
are shipped in the zip or rebuilt by gen.py on the student's computer. The judge refuses a test that is not in it.

  python3 tools/update_problem_manifest.py Mock_1/1          one problem
  python3 tools/update_problem_manifest.py --all             every problem
  python3 tools/update_problem_manifest.py --check --all     exit 1 if any manifest is stale (used by CI)

New NN.in / NN.out files are added as shipped tests (in_file / out_file true). Existing entries keep their flags:
a test that gen.py rebuilds stays unshipped, only its hashes are refreshed when the files are present.
"""
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = os.path.join(REPO, "problems", "batch")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "core"))
import judge  # noqa: E402  (normalize: the output hash ignores trailing spaces, like the judge)


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def out_hash(path):
    with open(path, "rb") as f:
        return judge.output_hash(f.read())


def test_names(folder):
    return sorted(f[:-3] for f in os.listdir(folder) if f.endswith(".in") and f[:-3].isdecimal())


def updated(folder):
    """The manifest folder/manifest.json should have, given the files in folder. Raises ValueError for a test
    whose shipped files are missing."""
    path = os.path.join(folder, "manifest.json")
    man = {"version": 1, "tests": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            man = json.load(f)
    entries = {t["name"]: dict(t) for t in man["tests"]}
    for name in test_names(folder):
        e = entries.setdefault(name, {"name": name, "in": "", "out": "", "in_file": True, "out_file": True})
        e["in"] = sha_file(os.path.join(folder, name + ".in"))
        if os.path.exists(os.path.join(folder, name + ".out")):
            e["out"] = out_hash(os.path.join(folder, name + ".out"))
        elif e["out_file"]:
            raise ValueError(f"{name}.out is missing (add it, or delete test {name} from manifest.json)")
    for name, e in entries.items():
        if e["in_file"] and not os.path.exists(os.path.join(folder, name + ".in")):
            raise ValueError(f"{name}.in is listed as shipped but missing (restore it, or delete the entry)")
    man["tests"] = [entries[k] for k in sorted(entries, key=lambda n: (len(n), n))]
    return man


def dumps(man):
    return json.dumps(man, indent=1) + "\n"


def problems(args):
    if "--all" in args:
        return sorted(os.path.join(BATCH, k, n) for k in os.listdir(BATCH) if k.startswith("Mock_")
                      for n in os.listdir(os.path.join(BATCH, k)) if n.isdecimal())
    return [os.path.join(BATCH, *a.split("/")) for a in args if not a.startswith("--")]


def main():
    args = sys.argv[1:]
    folders = problems(args)
    if not folders:
        print(__doc__)
        return 2
    stale = []
    for folder in folders:
        rel = os.path.relpath(folder, BATCH).replace(os.sep, "/")
        if not os.path.isdir(folder):
            print(f"{rel}: no such problem folder")
            return 2
        try:
            man = updated(folder)
        except ValueError as ex:
            print(f"{rel}: {ex}")
            return 1
        path = os.path.join(folder, "manifest.json")
        current = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                current = json.load(f)
        if current == man:              # same content (the file's own formatting does not matter)
            continue
        stale.append(rel)
        if "--check" not in args:
            with open(path, "w", encoding="utf-8") as f:
                f.write(dumps(man))
            print(f"{rel}: manifest.json updated ({len(test_names(folder))} inputs on disk)")
    if "--check" in args and stale:
        print("stale problem manifest(s): " + ", ".join(stale)
              + "\nrun  python3 tools/update_problem_manifest.py --all  and commit.")
        return 1
    if "--check" in args:
        print(f"{len(folders)} problem manifest(s) up to date.")
    elif not stale:
        print("nothing to change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
