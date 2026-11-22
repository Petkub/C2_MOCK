#!/usr/bin/env python3
"""
Write manifest.json: the version (file VERSION) and the SHA-256 of every file the student package gets inside
Judge/, the managed package files outside Judge/ (the PDFs, Makefile, judge.bat, README.txt, Guide.pdf,
Progress.md, .vscode/: replaced on the students' computers when they change) and the create-only files (the empty
code file of every problem: added only when missing, never replaced).
Judge/updater.py on the students' computers compares this file with what they have.

  python3 tools/build_manifest.py            write manifest.json (run after changing core/, problems/, student/)
  python3 tools/build_manifest.py --check    exit 1 if manifest.json or a bundle is stale (used by CI)

It also writes bundles/<folder>.zip: every shipped file of one set (problems/batch/<folder>/), so the updater
fetches a new set of problems in a few requests. A bundle is rewritten only when its content changes.

The package layout (one folder per problem) is in tools/layout.py.

Format:
  {"version": "7.2",
   "sources": {"problems/": "problems/", "": "core/"},        Judge/ path prefix -> repo folder
   "files": {"judge.py": "<sha256>", "problems/batch/Mock_A01/1/01.in": "<sha256>", ...},
   "managed": {"Mock_A01/Mock_A01.pdf": ["<sha256>", "student/Mock_A01/Mock_A01.pdf"],
               "Mock_A01/3/3_<Title>.pdf": ["<sha256>", "student/Mock_A01/3/3_<Title>.pdf"],
               "Mock_A01/Makefile": ["<sha256>", "student/set_files/Makefile"], ...},
   "create_only": {"Mock_A01/3/A01-3.cpp": ["<sha256>", "student/set_files/template.cpp"], ...},
   "bundles": {"bundles/Mock_A01.zip": {"sha256": "<sha256>", "prefix": "problems/batch/Mock_A01/"}, ...},
   "moves": {"<sha256 of an earlier release's problems.json>": [["Mock_A01/3/A01-3.cpp", "Mock_A02/5/A02-5.cpp"], ...]}}

"moves" (for releases after 7.2, the first one students get): tools/moves/problems_<v>.json is the problems.json of
release <v> (exact bytes; save it there when a later release moves, replaces or re-titles problems). A problem is
the same problem when its English title is the same (RENAMED maps an old title to a new one), so its code file goes
to the problem's new folder; a problem that is no longer in the sets (replaced by a new problem) goes to
<its old set folder>/old/<n>_<Title>.cpp. Judge/updater.py follow_moves() applies them once.
A re-titled problem's old PDF needs no list: the updater retires a managed PDF that the new manifest dropped when
its bytes are still the installed ones.
"""
import hashlib
import json
import re
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "manifest.json")
SOURCES = {"problems/": "problems/", "": "core/"}
SKIP_NAMES = {"__pycache__", ".DS_Store", "progress.json", "progress.json.tmp", ".update_check"}
SKIP_SUFFIXES = (".pyc",)
BUNDLES = "bundles"
STALE = []                                  # bundles that --check found out of date


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def version():
    with open(os.path.join(REPO, "VERSION"), encoding="utf-8") as f:
        return f.read().strip()


def shipped(dirpath, names):
    """Names in dirpath that go into the package: not the big tests gen.py rebuilds on the student's computer
    (manifest.json of the problem: in_file / out_file false), which judging in the repo may have created."""
    skip = set()
    p = os.path.join(dirpath, "manifest.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for t in json.load(f)["tests"]:
                if not t["in_file"]:
                    skip.add(t["name"] + ".in")
                if not t["out_file"]:
                    skip.add(t["name"] + ".out")
    return [n for n in names if n not in SKIP_NAMES and n not in skip and not n.endswith(SKIP_SUFFIXES)
            and not n.startswith(".")]


def judge_files():
    """Every file of Judge/ as (Judge-relative path, repo-relative path), both with '/' separators."""
    out = []
    for prefix, repo_dir in SOURCES.items():
        top = os.path.join(REPO, repo_dir)
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = sorted(shipped(dirpath, dirnames))
            for name in sorted(shipped(dirpath, filenames)):
                rel = os.path.relpath(os.path.join(dirpath, name), top).replace(os.sep, "/")
                out.append((prefix + rel, repo_dir + rel))
    return sorted(out)


def load_sets():
    with open(os.path.join(REPO, "problems", "batch", "sets.json"), encoding="utf-8") as f:
        return json.load(f)


def load_problems():
    with open(os.path.join(REPO, "problems", "batch", "problems.json"), encoding="utf-8") as f:
        return json.load(f)


def set_files():
    """Create-only files (the empty code file of every problem) as (package path, repo-relative source path)."""
    return [(layout.code_path(s, i), "student/set_files/template.cpp")
            for s in load_sets() for i in range(1, len(s["problems"]) + 1)]


def problem_pdfs():
    """Every problem's own PDF as (package path, repo-relative source path); it must exist in student/."""
    meta = load_problems()
    out = []
    for s in load_sets():
        for i, pid in enumerate(s["problems"], 1):
            rel = layout.pdf_path(s, i, layout.file_title(meta[str(pid)]))
            if not os.path.exists(os.path.join(REPO, "student", *rel.split("/"))):
                raise SystemExit(f"missing student/{rel}: run C2_MOCK_SRC build.py all (it writes the problem PDFs)")
            out.append((rel, "student/" + rel))
    return out


def managed_files():
    """Managed package files outside Judge/ as (package path, repo-relative source path). A problem folder holds
    exactly its code file and its PDF: Makefile and judge.bat are in the set folders only."""
    out = []
    for name in ("README.txt", "Guide.pdf", "Progress.md", ".vscode/tasks.json", ".vscode/settings.json"):
        if os.path.exists(os.path.join(REPO, "student", *name.split("/"))):
            out.append((name, "student/" + name))
    for s in load_sets():
        d = layout.set_dir(s)
        n = len(s["problems"])
        out.append((f"{d}/Makefile", "student/set_files/Makefile" + ("" if n == 6 else f"_{n}")))
        out.append((f"{d}/judge.bat", "student/set_files/judge.bat"))
        if os.path.exists(os.path.join(REPO, "student", d, f"{d}.pdf")):
            out.append((f"{d}/{d}.pdf", f"student/{d}/{d}.pdf"))
    return out + problem_pdfs()


def with_hashes(pairs):
    return {rel: [sha256_file(os.path.join(REPO, src)), src] for rel, src in pairs}


def zip_members(path):
    """{member name: sha256} of a zip, or None when it is missing or broken."""
    try:
        with zipfile.ZipFile(path) as z:
            return {i.filename: hashlib.sha256(z.read(i)).hexdigest() for i in z.infolist()}
    except (OSError, zipfile.BadZipFile):
        return None


def write_zip(path, members):
    """Deterministic zip of (Judge/ path, repo path) pairs: fixed dates and modes, sorted names."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, src in sorted(members):
            info = zipfile.ZipInfo(rel, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(os.path.join(REPO, src), "rb") as f:
                z.writestr(info, f.read())
    os.replace(tmp, path)


def bundles(pairs, files, write):
    """One bundle per problem folder problems/batch/<folder>/, rewritten only when its content changed."""
    groups = {}
    for rel, src in pairs:
        parts = rel.split("/")
        if len(parts) >= 4 and parts[0] == "problems" and parts[1] == "batch":
            groups.setdefault(parts[2], []).append((rel, src))
    out = {}
    for folder, members in sorted(groups.items()):
        name = f"{BUNDLES}/{folder}.zip"
        path = os.path.join(REPO, BUNDLES, folder + ".zip")
        if zip_members(path) != {rel: files[rel] for rel, _ in members}:
            if not write:
                STALE.append(name)
                continue
            write_zip(path, members)
        out[name] = {"sha256": sha256_file(path), "prefix": f"problems/batch/{folder}/"}
    return out


MOVES = os.path.join(REPO, "tools", "moves")
RENAMED = {                         # old English title -> new title, if a problem is renamed between releases
    # 7.3 story pass (C2_MOCK_SRC plans/STORY_ALL.md): technique words out of titles, chuuni titles in Track B
    "Two Stacks of Boxes": "Two Piles by the Conveyor",                         # A2/4
    "Every Window Has Variety": "Variety in Every Snack Pack",                  # A6/3
    "One Card to Fix": "Sealed Combo of the Handmade Deck",                     # B2/5
    "Ice Rink With Brakes": "Queen of the Rink, Brakes Sold Separately",        # B3/2
    "Fireballs and Demons": "Fireball Sage of Nine Thousand Deaths",            # B4/6
    "Nonogram Count": "The AI Swore There Was Only One Answer",                 # B5/1
    "Vanishing Card Pairs": "Seal of the Twin Cards",                           # B6/5
    "Camp Tents": "The Unchosen of the Campsite",                               # B7/5
    "Zone Passes": "The Cursed Tickets of the Theme Park",                      # B8/4
}


def moves(now=None, folder=MOVES):
    """{sha256 of an earlier problems.json: [[from, to], ...]} for every file in tools/moves/ (code file paths)."""
    if now is None:
        now = load_problems()
    here = {e["en"]: layout.entry_code_path(e) for e in now.values()}
    out = {}
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        pairs = []
        for e in sorted(old.values(), key=lambda e: e["dir"]):
            src, title = layout.entry_code_path(e), RENAMED.get(e["en"], e["en"])
            n = int(e["dir"].split("/")[1])
            if title in here:
                if here[title] != src:
                    pairs.append([src, here[title]])
            else:                                   # replaced by a new problem: park it in its set's old/
                pairs.append([src, f"{e['dir'].split('/')[0]}/old/{layout.old_name(n, e['en'])}"])
        out[sha256_file(path)] = pairs
    return out


def build(write=True):
    pairs = judge_files()
    files = {rel: sha256_file(os.path.join(REPO, src)) for rel, src in pairs}
    return {"version": version(), "sources": SOURCES, "files": files, "managed": with_hashes(managed_files()),
            "create_only": with_hashes(set_files()), "bundles": bundles(pairs, files, write), "moves": moves()}


def installed(manifest):
    """The part of a manifest that the updater installs (and writes as Judge/manifest.json): all of it."""
    return manifest


def dumps(manifest):
    return json.dumps(manifest, indent=0, sort_keys=True) + "\n"


def main():
    check = "--check" in sys.argv[1:]
    manifest = build(write=not check)
    text = dumps(manifest)
    if check:
        if STALE:
            print("bundles are stale (" + ", ".join(STALE[:3]) + "): run  python3 tools/build_manifest.py  and commit.")
            return 1
        try:
            with open(MANIFEST, encoding="utf-8") as f:
                current = f.read()
        except OSError:
            current = ""
        if current != text:
            print("manifest.json is stale: run  python3 tools/build_manifest.py  and commit it.")
            return 1
        full = installed(manifest)
        print(f"manifest.json is up to date (v{full['version']}, {len(full['files'])} files).")
        return 0
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(text)
    full = installed(manifest)
    print(f"Wrote manifest.json: v{full['version']}, {len(full['files'])} files in Judge/, "
          f"{len(full['managed'])} managed and {len(full['create_only'])} create-only package files, "
          f"{len(full['bundles'])} bundles, moves from {len(full['moves'])} earlier releases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
