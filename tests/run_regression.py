#!/usr/bin/env python3
"""
Regression tests for the POSN Camp 2 Practice Judge.

  python3 tests/run_regression.py          run everything (exit code 0 = all passed)

Everything runs inside a student package built with tools/build_dist.py in a temporary folder, so the big tests
that gen.py rebuilds and progress.json are never written into the repo.
1. The package ships no rebuilt tests and no progress.json; Mock_K/1.cpp ... 6.cpp are untouched starters.
2. Every sample in samples/expected.json is judged and must get its verdict (and score, when given; that run
   also rebuilds the problem's big tests with gen.py and checks them).
   Verdict = CE if it does not compile, else the first non-AC verdict, else AC.
3. The judge's command line is run like a student would (inside a Mock_K folder, --ascii, --list, --progress).
4. Self-update: a local HTTP server serves a modified copy of the repo as v9.9; a package must update itself
   (hashes, backups, restart, create-only set files), and must refuse bad hashes, bad paths and no network.
5. manifest.json is up to date.
"""
import re
import contextlib
import functools
import http.server
import socket
import threading
import time
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO, "samples")
NAME = "C2_Mock_Test"
FAILED = []
os.environ["JUDGE_NO_UPDATE"] = "1"       # the judge never contacts GitHub during the tests
judge = None        # the package's judge.py, imported by main()
# the towers_*.cpp samples solve Signal Towers (id 14): judged by its id; TOWERS_SET/TOWERS_CPP (its student file) come
# from problems.json, so the tests follow the problem when the sets are reorganised
TOWERS_ID = "14"
with open(os.path.join(REPO, "problems", "batch", "problems.json"), encoding="utf-8") as _f:
    TOWERS_SET, _n = json.load(_f)[TOWERS_ID]["dir"].split("/")
TOWERS_CPP = _n + ".cpp"
_k = TOWERS_SET[len("Mock_"):]
TOWERS = (f"{_k[0]}{int(_k[1:])}-{_n}" if _k[:1] in "AB" else f"{_k}-{_n}")    # e.g. A6-3


def check(ok, name, detail=""):
    detail = detail.encode("ascii", "backslashreplace").decode("ascii")    # Windows consoles: cp1252
    print(("  ok    " if ok else "  FAIL  ") + name + ("" if ok else "   " + detail))
    if not ok:
        FAILED.append(name)


def build_package(out):
    p = subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_dist.py"), "--out", out, "--no-zip"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    check(p.returncode == 0, "build_dist.py", p.stdout.decode("utf-8", "replace"))
    return os.path.join(out, NAME) if p.returncode == 0 else None


# ----------------------------------------------------------------------------- 1. package contents
def test_package(root):
    print("Package")
    judge_dir = os.path.join(root, "Judge")
    extra = []
    for m in glob.glob(os.path.join(judge_dir, "problems", "batch", "Mock_*", "*", "manifest.json")):
        with open(m, encoding="utf-8") as f:
            for t in json.load(f)["tests"]:
                for ext, key in ((".in", "in_file"), (".out", "out_file")):
                    if os.path.exists(os.path.join(os.path.dirname(m), t["name"] + ext)) != t[key]:
                        extra.append(os.path.relpath(os.path.join(os.path.dirname(m), t["name"] + ext), root))
    check(not extra, "test files match manifest.json (big tests not shipped)", ", ".join(extra[:5]))
    check(not os.path.exists(os.path.join(judge_dir, "progress.json")), "no progress.json shipped")
    starters = glob.glob(os.path.join(root, "Mock_*", "[0-9].cpp"))
    with open(os.path.join(REPO, "problems", "batch", "sets.json"), encoding="utf-8") as f:
        expected = sum(len(s["problems"]) for s in json.load(f))
    check(len(starters) == expected and all(judge.is_untouched_starter(s) for s in starters),
          "Mock_K/1.cpp ... 6.cpp are untouched starters", f"{len(starters)} files")
    check(all(os.path.getsize(s) == 0 for s in starters), "Mock_K/1.cpp ... 6.cpp are empty files")
    if shutil.which("make"):      # `make 6` once fell back to make's built-in rule (compiled 6.cpp, no judging)
        bad = []
        for d in sorted(glob.glob(os.path.join(root, "Mock_*"))):
            p = subprocess.run(["make", "-n", "6"], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if p.returncode != 0 or "judge.py 6.cpp" not in p.stdout.decode("utf-8", "replace"):
                bad.append(os.path.basename(d))
        check(not bad, "make -n 6 calls judge.py 6.cpp in every Mock folder", ", ".join(bad))
    old = os.path.join(root, "old_template.cpp")          # the starter of versions before 6.0.2
    with open(old, "w") as f:
        f.write("#include <bits/stdc++.h>\nusing namespace std;\n\nint32_t main() {\n"
                "    cin.tie(0); ios::sync_with_stdio(0);\n\n    return 0;\n}\n")
    check(judge.is_template(old) and judge.is_untouched_starter(old), "the old main() starter still counts as untouched")
    os.remove(old)


def test_tracks(root):
    """v7: sets named by track (Mock_A01 ...), --set A3, progress counted per track."""
    print("Tracks")
    with open(os.path.join(REPO, "problems", "batch", "sets.json"), encoding="utf-8") as f:
        sets = json.load(f)
    names = [str(s["set"]) for s in sets]
    check(all(n[:1] in "AB" for n in names) and all(len(s["problems"]) == 6 for s in sets),
          "every set is a Track A/B set of 6 problems", ", ".join(names))
    first = sets[2]
    label = first["set"][0] + str(int(first["set"][1:]))
    folder = os.path.join(root, f"Mock_{first['set']}")
    check(os.path.isdir(folder), f"folder Mock_{first['set']} exists")
    for token in (label, label.lower(), first["set"]):
        code, out, _ = run_judge(["--set", token, "--no-color"], folder)
        check(code == 0 and "Problem 6" in out and "600 points" in out, f"--set {token} lists set {label}",
              f"exit {code}\n{out[-800:]}")
    code, out, _ = run_judge(["--set", "Z9", "--no-color"], folder)
    check(code != 0, "--set Z9 is rejected")
    code, out, _ = run_judge(["--progress", "--no-color", "--ascii"], folder)
    total_a = sum(len(s["problems"]) for s in sets if str(s["set"]).startswith("A"))
    check(code == 0 and "Track A" in out and f"/ {total_a}" in out, f"--progress shows Track A x / {total_a}", out[:800])
    total_b = sum(len(s["problems"]) for s in sets if str(s["set"]).startswith("B"))
    if total_b:         # v7 Track B: counted apart from Track A
        check("Track B" in out and f"/ {total_b}" in out, f"--progress shows Track B x / {total_b}", out[:1500])
        last_b = [s for s in sets if str(s["set"]).startswith("B")][-1]
        lb = last_b["set"][0] + str(int(last_b["set"][1:]))
        code, out, _ = run_judge(["--set", lb, "--no-color"], os.path.join(root, f"Mock_{last_b['set']}"))
        check(code == 0 and "Problem 6" in out, f"--set {lb} lists set {lb}", f"exit {code}\n{out[-800:]}")


def test_bootstrap_view():
    """Updaters before 7.0 reject Mock_A01 paths: they read "full", which must only hold entries they accept."""
    print("Bootstrap view")
    import re as _re
    old_set = _re.compile(r"^Mock_[0-9]+/[0-9]+\.cpp$")
    old_managed = _re.compile(r"^(Mock_[0-9]+/(Makefile|judge\.bat|Mock_[0-9]+\.pdf)|Guide\.pdf|README\.txt"
                              r"|Progress\.md|\.vscode/(tasks|settings)\.json)$")
    with open(os.path.join(REPO, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    full, v7 = m.get("full", {}), m.get("full_v7", {})
    check(bool(v7) and full.get("bootstrap") is True, "manifest has full_v7 and a bootstrap \"full\"")
    check(all(old_managed.match(k) for k in full.get("managed", {})) and
          all(old_set.match(k) for k in full.get("create_only", {})), "the bootstrap view only holds old-style paths")
    check(full.get("files") == v7.get("files"), "the bootstrap view installs every Judge/ file (incl. the new updater)")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None



def test_moves_70(root, tmp):
    """7.0 -> now (V7_TRACKA_SWAP): a written file of a replaced Track A problem goes to Mock_Axx/old/<n>_<Title>.cpp
    and its slot gets an empty starter for the new problem; untouched starters and every other file stay; the set
    folders are current, so nothing is removed and no README_MOVED.txt is written; it happens once."""
    print("Moves (7.0 -> now)")
    base = os.path.join(tmp, "moves_pkg_70")
    shutil.copytree(root, base)
    jd = os.path.join(base, "Judge")
    with open(os.path.join(jd, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    for rel in manifest.get("create_only", {}):
        write(os.path.join(base, *rel.split("/")), "")
    old = os.path.join(REPO, "tools", "moves", "problems_7.0.json")
    pairs = manifest.get("moves", {}).get(sha(old))
    slots = {s for s, _ in pairs}
    check(bool(pairs) and any("/old/" in d for _, d in pairs)
          and all("/old/" in d or (re.fullmatch(r"Mock_A\d\d/\d+\.cpp", d) and d.split("/")[0] == s.split("/")[0])
                  for s, d in pairs),
          "the manifest sends each replaced problem's file to old/ and a re-ordered problem's file to its new slot",
          str(pairs)[:300])
    if not pairs:
        return
    os.makedirs(os.path.join(jd, ".backup", "problems", "batch"), exist_ok=True)
    shutil.copy(old, os.path.join(jd, ".backup", "problems", "batch", "problems.json"))
    filled = {d for _, d in pairs}                               # slots that receive another problem's file
    lone = [(s, d) for s, d in pairs if "/old/" in d and s not in filled]
    untouched = lone[0][0]                                       # an empty starter is not moved
    written = {src: f"// 7.0 code for {src}\nint main(){{}}\n" for src, _ in pairs if src != untouched}
    for src, text in written.items():
        write(os.path.join(base, *src.split("/")), text)
    keep = "Mock_A01/1.cpp" if all(s != "Mock_A01/1.cpp" for s, _ in pairs) else None
    if keep:
        write(os.path.join(base, *keep.split("/")), "// kept\n")
    track_b = os.path.join(base, "Mock_B01", "1.cpp")
    write(track_b, "// track B code\n")
    run_dir = os.path.join(base, "Mock_A01")
    code, out, _ = run_judge(["--list", "--no-color"], run_dir)
    check(code == 0 and "moved with their problems" in out, "the judge says the files moved", out[:600])
    bad = [f"{s} -> {d}" for s, d in pairs if s in written and read(os.path.join(base, *d.split("/"))) != written[s]]
    check(not bad, "every written file is at its destination (old/ or the problem's new slot)", ", ".join(bad[:5]))
    check(all(read(os.path.join(base, *s.split("/"))) == "" for s in slots - filled),
          "each replaced slot holds an empty starter for its new problem")
    check(not os.path.exists(os.path.join(base, *lone[0][1].split("/"))), "an untouched starter is not moved")
    check((not keep or read(os.path.join(base, *keep.split("/"))) == "// kept\n") and read(track_b) == "// track B code\n",
          "files of problems that stay (Track A and Track B) are not touched")
    check(not glob.glob(os.path.join(base, "Mock_*", "README_MOVED.txt")), "no current set folder gets README_MOVED.txt")
    snapshot = {q: read(q) for q in glob.glob(os.path.join(base, "Mock_*", "**", "*.cpp"), recursive=True)}
    code, out, _ = run_judge(["--list", "--no-color"], run_dir)
    again = {q: read(q) for q in glob.glob(os.path.join(base, "Mock_*", "**", "*.cpp"), recursive=True)}
    check("moved" not in out and again == snapshot, "the moves happen once")

def test_moves(root, tmp, release="6.0.2"):
    """After an update from an older release (6.0, 6.0.2, 6.1) the student's files follow their problems to the v7
    folders, once, never over written code; an old folder with nothing of the student's left is removed, one with
    something left gets README_MOVED.txt."""
    print(f"Moves ({release} -> now)")
    base = os.path.join(tmp, "moves_pkg_" + release)
    shutil.copytree(root, base)
    jd = os.path.join(base, "Judge")
    with open(os.path.join(jd, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    for rel in manifest.get("create_only", {}):                  # a fresh install: every starter empty
        write(os.path.join(base, *rel.split("/")), "")
    old = os.path.join(REPO, "tools", "moves", f"problems_{release}.json")
    pairs = manifest.get("moves", {}).get(sha(old))
    check(bool(pairs), f"the manifest lists moves for a {release} install", str(list(manifest.get("moves", {}))))
    if not pairs:
        return
    os.makedirs(os.path.join(jd, ".backup", "problems", "batch"), exist_ok=True)     # what the old updater kept
    shutil.copy(old, os.path.join(jd, ".backup", "problems", "batch", "problems.json"))
    written = {src: f"// student code for {src}\nint main(){{}}\n" for src, _ in pairs}
    first = pairs[0][0]
    for src, text in written.items():
        if src != first:
            write(os.path.join(base, *src.split("/")), text)
    write(os.path.join(base, *first.split("/")), "")             # an untouched (empty) starter is not moved
    keep_dir = pairs[-1][0].split("/")[0]                        # a folder that keeps something of the student's
    write(os.path.join(base, keep_dir, "notes.txt"), "// stays\n")
    gone_dir = first.split("/")[0]                               # holds only starters / managed files after the moves
    for name in ("Makefile", "judge.bat"):
        write(os.path.join(base, gone_dir, name), "managed\n")
    run_dir = os.path.join(base, os.path.dirname(next(iter(manifest["create_only"]))))   # a v7 set folder
    sources = {src for src, _ in pairs}
    clash = next((dst for src, dst in pairs[1:] if dst.split("/")[1] != "old" and dst not in sources), None)
    if clash:                                                    # written code already at a destination
        write(os.path.join(base, *clash.split("/")), "// written before the update\n")
    probe = next(((s, d) for s, d in reversed(pairs) if d != clash and s.split("/")[0] == keep_dir), None)
    if probe:                                                    # judging a file that moves in this very run
        code, out, _ = run_judge([probe[0].split("/")[1], "--no-color"], os.path.join(base, keep_dir))
        check(code == 1 and "moved with their problems" in out and f"moved with its problem to {probe[1]}" in out,
              "the judge says the files moved, and where the file it was asked to judge went", out[:800])
    else:
        code, out, _ = run_judge(["--list", "--no-color"], run_dir)
        check(code == 0 and "moved with their problems" in out, "the judge says the files moved", out[:800])
    bad = []
    for src, dst in pairs[1:]:
        if dst == clash:
            continue
        if read(os.path.join(base, *dst.split("/"))) != written[src]:
            bad.append(f"{src} -> {dst}")
    check(not bad, "every written file is at its problem's new place (or in Mock_K/old/)", ", ".join(bad[:5]))
    if clash:
        src = next(s for s, d in pairs if d == clash)
        kept = read(os.path.join(base, *clash.split("/"))) == "// written before the update\n"
        parked = glob.glob(os.path.join(base, clash.split("/")[0], "old", "*_moved*.cpp"))
        check(kept and any(read(p) == written[src] for p in parked), "a clash never overwrites: the moved file goes to old/",
              f"{clash}: kept={kept}, parked={parked}")
    vacated = [src for src, _ in pairs[1:] if not any(d == src for _, d in pairs)]
    check(all(read(os.path.join(base, *v.split("/"))) in (None, "") for v in vacated), "no written file is left behind")
    check(not glob.glob(os.path.join(base, first.split("/")[0], first.split("/")[1])) or
          read(os.path.join(base, *first.split("/"))) == "", "an untouched starter is not moved")
    check(read(os.path.join(base, keep_dir, "notes.txt")) == "// stays\n" and
          os.path.exists(os.path.join(base, keep_dir, "README_MOVED.txt")),
          "an old folder with something of the student's stays, with README_MOVED.txt")
    gone_left = os.listdir(os.path.join(base, gone_dir)) if os.path.isdir(os.path.join(base, gone_dir)) else []
    check(not os.path.isdir(os.path.join(base, gone_dir)) or "README_MOVED.txt" in gone_left,
          f"an old folder with only starters / managed files is removed ({gone_dir})", str(gone_left))
    snapshot = {p: read(p) for p in glob.glob(os.path.join(base, "Mock_*", "**", "*.cpp"), recursive=True)}
    code, out, _ = run_judge(["--list", "--no-color"], run_dir)
    again = {p: read(p) for p in glob.glob(os.path.join(base, "Mock_*", "**", "*.cpp"), recursive=True)}
    check("moved" not in out and again == snapshot, "the moves happen once")
    if release != "6.0.2":
        return
    other = os.path.join(tmp, "moves_32")
    shutil.copytree(root, other)
    for rel in manifest.get("create_only", {}):
        write(os.path.join(other, *rel.split("/")), "")
    os.makedirs(os.path.join(other, "Judge", ".backup", "problems", "batch"))
    write(os.path.join(other, "Judge", ".backup", "problems", "batch", "problems.json"), '{"1": {"en": "Signal Towers", "dir": "Mock_1/1"}}')
    template = "#include <bits/stdc++.h>\nusing namespace std;\n\nint32_t main() {\n    cin.tie(0); ios::sync_with_stdio(0);\n\n    return 0;\n}\n"
    for k in (1, 2, 3):                                          # a 3.2 package: Mock_1 ... with starters and set files
        for name in ("Makefile", "judge.bat", f"Mock_{k}.pdf"):
            write(os.path.join(other, f"Mock_{k}", name), "managed\n")
        for n in range(1, 6):
            write(os.path.join(other, f"Mock_{k}", f"{n}.cpp"), template if n % 2 else "")
    write(os.path.join(other, "Mock_1", "6.cpp"), "// 3.2 code\n")     # written code
    write(os.path.join(other, "Mock_3", "a.exe"), "binary")              # something of the student's (not code)
    v7_dir = os.path.join(other, os.path.dirname(next(iter(manifest["create_only"]))))
    before = {p: read(p) for p in glob.glob(os.path.join(other, "Mock_A*", "*.cpp"))}
    code, out, _ = run_judge(["--list", "--no-color"], v7_dir)
    check("moved with their problems" not in out and read(os.path.join(other, "Mock_1", "6.cpp")) == "// 3.2 code\n",
          "an unknown older release (e.g. 3.2) gets no moves", out[:600])
    m1 = sorted(os.listdir(os.path.join(other, "Mock_1"))) if os.path.isdir(os.path.join(other, "Mock_1")) else []
    check(m1 == sorted(["1.cpp", "2.cpp", "3.cpp", "4.cpp", "5.cpp", "6.cpp", "Makefile", "judge.bat", "Mock_1.pdf",
                        "README_MOVED.txt"]) and "Nothing here was moved or deleted" in
          (read(os.path.join(other, "Mock_1", "README_MOVED.txt")) or ""),
          "3.2: a folder with written code keeps every file and gets README_MOVED.txt", str(m1))
    check(not os.path.exists(os.path.join(other, "Mock_2")), "3.2: a folder with only starters and set files is removed")
    check(read(os.path.join(other, "Mock_3", "a.exe")) == "binary" and
          os.path.exists(os.path.join(other, "Mock_3", "README_MOVED.txt")),
          "3.2: a folder with any other file of the student's stays (README_MOVED.txt)")
    check("Mock_2" in out and "removed" in out and before == {p: read(p) for p in glob.glob(os.path.join(other, "Mock_A*", "*.cpp"))},
          "3.2: the judge lists what it tidied; the new set folders are untouched", out[:600])
    code, out, _ = run_judge(["--list", "--no-color"], v7_dir)
    check("reorganised" not in out and os.path.isdir(os.path.join(other, "Mock_1")), "3.2: the tidy happens once")
    code, out, _ = run_judge(["6.cpp", "--no-color"], os.path.join(other, "Mock_1"))
    check(code == 1 and "is an old set folder" in out and "Rename the folder" not in out,
          "3.2: judging inside a kept old folder explains it is no longer a set", out[:400])


def test_crlf_generator():
    """On Windows gen.py (text mode) writes CRLF; the sha256 in manifest.json is of the LF file."""
    tmp = tempfile.mkdtemp(prefix="judge_gen_test_")
    try:
        data = b"3 1 0 10\n2 1\n7 2\n12 1\n"
        with open(os.path.join(tmp, "gen.py"), "w") as f:
            f.write("import os\nos.makedirs('tests', exist_ok=True)\n"
                    f"open('tests/01.in', 'w', newline='\\r\\n').write({data.decode()!r})\n")
        test = {"name": "01", "in": hashlib.sha256(data).hexdigest(), "out": "", "in_file": False, "out_file": True}
        with open(os.path.join(tmp, "manifest.json"), "w") as f:
            json.dump({"version": 1, "tests": [test]}, f)
        with contextlib.redirect_stdout(io.StringIO()):
            ok = judge.ensure_tests(tmp, judge.Style(color=False, ascii_only=True, tty=False))
        got = b""
        if os.path.isfile(os.path.join(tmp, "01.in")):
            with open(os.path.join(tmp, "01.in"), "rb") as f:
                got = f.read()
        check(ok and got == data, "gen.py writing CRLF (Windows) is accepted and stored with LF", repr(got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_scoring():
    """C2_MOCK problems score 100 or 0 ("scoring": "all", like the real exam); without the field a problem scores
    the share of tests passed. The result line still shows how many tests passed."""
    meta = judge.load_meta()
    _, num = judge.find_problem(TOWERS, meta)
    results = [("01", "AC"), ("02", "AC"), ("03", "WA"), ("04", "AC")]
    judge.set_sample_count(meta, num)
    check(meta[num].get("scoring") == "all" and judge.compute_score(results, 4)[0] == 0
          and judge.compute_score(results[:2], 2)[0] == 100, "C2_MOCK problems score 100 or 0 (scoring: all)")
    judge.set_sample_count({"x": {"samples": 5}}, "x")
    check(judge.compute_score(results, 4)[0] == 75, "a problem without the field scores the share of tests passed")
    judge.set_sample_count(meta, num)


def test_stale_tests():
    """An update that changes a problem's tests leaves the old files of its big tests behind (the updater never
    deletes): a big input whose sha256 differs is rebuilt, and an old .out of a hash-only test is ignored."""
    pdir, _ = judge.find_problem(TOWERS, judge.load_meta())
    td = judge.tests_dir(pdir)
    mpath = os.path.join(td, "manifest.json")
    with open(mpath, encoding="utf-8") as f:
        original = f.read()
    man = json.loads(original)
    t_in, t_out = [t for t in man["tests"] if not t["in_file"]][:2]
    fin, fout = os.path.join(td, t_in["name"] + ".in"), os.path.join(td, t_out["name"] + ".out")
    with open(fout, "rb") as f:
        shipped_out = f.read()
    try:
        t_out["out_file"] = False
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(man, f)
        with open(fin, "wb") as f:
            f.write(b"1 1 0 1\n1 1\n")
        with open(fout, "wb") as f:
            f.write(b"0\n")
        verdict, score = judge_sample(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), TOWERS, True)
        check(verdict == "AC" and score == 100 and sha(fin) == t_in["in"],
              "old test files left by an update: big input rebuilt, old .out ignored", f"{verdict} {score}")
    finally:
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(original)
        with open(fout, "wb") as f:
            f.write(shipped_out)


# ----------------------------------------------------------------------------- 2. verdicts
def judge_sample(src, problem, full):
    """(verdict, score) of src on problem K-P; full = run every test (needed for the score)."""
    meta = judge.load_meta()
    pdir, num = judge.find_problem(problem, meta)
    if not pdir:
        return "no such problem " + problem, 0
    judge.set_sample_count(meta, num)
    st = judge.Style(color=False, ascii_only=True, tty=False)
    tmp = tempfile.mkdtemp(prefix="judge_")
    try:
        exe, _, _, _ = judge.compile_source(src, tmp)
        if not exe:
            return "CE", 0
        with contextlib.redirect_stdout(io.StringIO()):
            if not judge.ensure_tests(pdir, st):
                return "could not rebuild the big tests", 0
            results, _, total = judge.run_tests(exe, pdir, st, 1.0, 0, not full, quiet=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [r[1] for r in results if r[1] != "AC"]
    peaks = [r[3] for r in results if r[3] is not None]
    PEAK[0] = max(peaks) / (1024 * 1024) if peaks else None
    return (bad[0] if bad else "AC"), judge.compute_score(results, total)[0]


PEAK = [None]      # peak memory (MB) seen by the last judge_sample call


def test_samples():
    print("Samples")
    with open(os.path.join(SAMPLES, "expected.json"), encoding="utf-8") as f:
        expected = json.load(f)
    for name, want in expected.items():
        full = "score" in want
        verdict, score = judge_sample(os.path.join(SAMPLES, name), want["problem"], full)
        ok = verdict == want["verdict"] and (not full or score == want["score"])
        got = verdict + (f" {score}" if full else "")
        check(ok, f"{name:<28} {want['verdict']}", f"got {got}")
        if name.endswith("_ok.cpp"):      # a small program must be measured as small (not the judge's own image)
            check(PEAK[0] is not None and 0.1 < PEAK[0] < 16, f"peak memory of a small program is measured: {PEAK[0]} MB")


def test_exited_peak():
    """A program that exits before the first memory reading must not get the judge's own size (wait4's ru_maxrss)."""
    if os.name == "nt":
        return
    import resource
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == "darwin" else 1024
    check(judge.exited_peak(own) is None, "a fast small program's peak is unknown, not the judge's own size",
          f"got {judge.exited_peak(own)}")
    check(judge.exited_peak(3 * own) == 3 * own * scale, "a fast big program's ru_maxrss is still used",
          f"got {judge.exited_peak(3 * own)}")

def test_missed_last_reading():
    """A program that grows after the last memory reading (it exits before the next one) is still MLE: wait4's
    ru_maxrss is used too. On macOS this happened when the exiting program was reaped before its final reading."""
    if os.name == "nt":
        return
    name = "linux_peak_memory" if sys.platform.startswith("linux") else "mac_peak_memory"
    real = getattr(judge, name)
    seen = set()

    def first_only(pid):           # one reading right after each start (the program is still tiny), then none
        if pid in seen:
            return None
        seen.add(pid)
        return 1024 * 1024
    setattr(judge, name, first_only)
    try:
        verdict, _ = judge_sample(os.path.join(SAMPLES, "batch", "towers_mle.cpp"), TOWERS, False)
    finally:
        setattr(judge, name, real)
    check(verdict == "MLE", "the MLE sample is MLE even when the readings miss its growth", f"got {verdict}")

# ----------------------------------------------------------------------------- 3. command line
def run_judge(args, cwd):
    """Run ../Judge/judge.py like a student inside a Mock_K folder. Returns (exit code, output, output is ASCII)."""
    p = subprocess.run([sys.executable, os.path.join(os.pardir, "Judge", "judge.py")] + args, cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stdout.isascii()


def test_cli(root):
    print("Command line")
    set1 = os.path.join(root, TOWERS_SET)
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), os.path.join(set1, TOWERS_CPP))
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_smallhi.cpp"), os.path.join(set1, "wrong.cpp"))
    code, out, _ = run_judge([TOWERS_CPP, "--no-color"], set1)
    check(code == 0 and "ACCEPTED" in out, f"inside {TOWERS_SET}: judge.py {TOWERS_CPP}", f"exit {code}\n{out}")
    progress = os.path.join(root, "Judge", "progress.json")
    try:
        with open(progress, encoding="utf-8") as f:
            best = json.load(f)["problems"][TOWERS_ID]["best"]
    except (OSError, ValueError, KeyError):
        best = None
    check(best == 100, f"progress.json records best 100 for problem {TOWERS_ID}", f"best = {best}")
    for name in ("towers_throw.cpp", "towers_warn.cpp"):
        shutil.copy(os.path.join(SAMPLES, "batch", name), os.path.join(set1, name))
    code, out, _ = run_judge(["towers_throw.cpp", TOWERS, "--no-color", "--stop"], set1)
    check("out_of_range" in out and "stderr" in out, "RE shows the program's stderr (out_of_range)", out)
    code, out, _ = run_judge(["towers_warn.cpp", TOWERS, "--no-color", "--stop"], set1)
    check("g++ warning" in out and "unused" in out, "warnings are shown after Compiled", out)
    code, out, _ = run_judge([TOWERS_CPP, "--no-color", "--stop"], set1)
    check("warning" not in out and "Memory  peak" in out and "256 MB per test" in out,
          "clean program: no warnings, memory line, limit in header", out)
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_mle.cpp"), os.path.join(set1, "towers_mle.cpp"))
    code, out, _ = run_judge(["towers_mle.cpp", TOWERS, "--no-color", "--stop", "--ml", "200"], set1)    # 400 MB
    check("Memory Limit Exceeded" in out and "limit is 200 MB" in out, "--ml 200: a 400 MB program is MLE", out)
    code, out, _ = run_judge(["towers_mle.cpp", TOWERS, "--no-color", "--stop", "--ml", "1024"], set1)
    check(code == 0 and "ACCEPTED" in out, "--ml 1024: the same program is accepted", f"exit {code}\n{out}")
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_deep.cpp"), os.path.join(set1, "towers_deep.cpp"))
    code, out, _ = run_judge(["towers_deep.cpp", TOWERS, "--no-color", "--stop"], set1)
    check(code == 0 and "ACCEPTED" in out, "a recursive DFS of depth 10^6 runs (256 MB stack)", f"exit {code}\n{out}")
    code, out, _ = run_judge(["1.cpp", "--no-color"], set1)              # the empty starter
    check(code == 0 and "1.cpp is empty" in out and "Compil" not in out, "an empty .cpp: plain message, no compile",
          f"exit {code}\n{out}")
    code, out, _ = run_judge(["--ml", "0"], set1)
    check(code == 2 and "--ml must be" in out, "judge.py --ml 0 is rejected", f"exit {code}\n{out}")
    code, out, plain = run_judge(["wrong.cpp", TOWERS, "--ascii", "--no-color"], set1)
    check(code == 0 and "First failure" in out and plain, "judge.py --ascii shows the failure, ASCII only",
          f"exit {code}, ascii={plain}\n{out}")
    code, out, _ = run_judge(["--no-color"], set1)
    check(code == 0 and "Total" in out and "Problem 6" in out and "still empty - skipped" in out, f"inside {TOWERS_SET}: judge.py (whole set)",
          f"exit {code}\n{out}")
    code, out, plain = run_judge(["--progress", "--ascii"], set1)
    check(code == 0 and plain, "judge.py --progress --ascii", f"exit {code}, ascii={plain}\n{out}")
    code, out, plain = run_judge(["--list", "--ascii"], set1)
    check(code == 0 and "Set A4" in out and plain, "judge.py --list --ascii", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--tl", "abc"], set1)
    check(code == 2 and "--tl must be" in out, "judge.py --tl abc is rejected", f"exit {code}\n{out}")


# ----------------------------------------------------------------------------- 4. self-update
def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def serve(folder, log=None):
    """Serve folder over HTTP on a free port of this computer (stands in for raw.githubusercontent.com).
    log: a list that gets the path of every request."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if log is not None:
                log.append(self.path.split("?")[0])
            super().do_GET()

    handler = functools.partial(Handler, directory=folder)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def make_repo2(tmp, version, marker):
    """A copy of the repo with a new VERSION, a marker line in judge.py and a changed README, manifest rebuilt."""
    repo2 = os.path.join(tmp, "repo2")
    if os.path.exists(repo2):
        shutil.rmtree(repo2)
    shutil.copytree(REPO, repo2, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
    with open(os.path.join(repo2, "VERSION"), "w") as f:
        f.write(version + "\n")
    with open(os.path.join(repo2, "core", "judge.py"), "a") as f:
        f.write(f"\n# {marker}\n")
    with open(os.path.join(repo2, "core", "README.txt"), "a") as f:
        f.write(f"{marker}\n")
    for name in (("student", "README.txt"), ("student", "set_files", "Makefile")):     # managed package files
        with open(os.path.join(repo2, *name), "a", encoding="utf-8") as f:
            f.write(f"\n# {marker}\n")
    rebuild_manifest(repo2)
    return repo2


def rebuild_manifest(repo2):
    subprocess.run([sys.executable, os.path.join(repo2, "tools", "build_manifest.py")], check=True,
                   stdout=subprocess.DEVNULL)


def edit_manifest(repo2, fn):
    """fn changes the parts of manifest.json that updaters install ("full_v7" and the bootstrap "full", format 2)."""
    p = os.path.join(repo2, "manifest.json")
    with open(p, encoding="utf-8") as f:
        m = json.load(f)
    parts = [m[k] for k in ("full_v7", "full") if isinstance(m.get(k), dict)] or [m]
    for part in parts:
        fn(part)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(m, f)


def run_student(args, cwd, url):
    env = dict(os.environ, JUDGE_UPDATE_URL=url)
    env.pop("JUDGE_NO_UPDATE", None)
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join(os.pardir, "Judge", "judge.py")] + args, cwd=cwd, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    return p.returncode, p.stdout.decode("utf-8", "replace"), time.time() - t0


def test_updater():
    print("Self-update")
    tmp = tempfile.mkdtemp(prefix="judge_upd_")
    try:
        subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_dist.py"), "--out", tmp, "--no-zip"],
                       check=True, stdout=subprocess.DEVNULL)
        root = os.path.join(tmp, NAME)
        judge_dir, set1 = os.path.join(root, "Judge"), os.path.join(root, TOWERS_SET)
        other = "1.cpp" if TOWERS_CPP != "1.cpp" else "2.cpp"      # a starter the student has not touched
        shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), os.path.join(set1, TOWERS_CPP))
        student_hash, old_judge = sha(os.path.join(set1, TOWERS_CPP)), sha(os.path.join(judge_dir, "judge.py"))
        template = sha(os.path.join(set1, other))

        # a) automatic update during a normal run: new files, backup, restart with the new judge
        repo2 = make_repo2(tmp, "9.9", "marker-v9.9")
        edit_manifest(repo2, lambda m: m["create_only"].update(
            {TOWERS_SET + "/7.cpp": [sha(os.path.join(REPO, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]}))
        srv, url = serve(repo2)
        code, out, _ = run_student([TOWERS_CPP, "--no-color"], set1, url)
        check(code == 0 and "restarting" in out and "ACCEPTED" in out and "Judge v9.9" in out,
              "normal run updates to v9.9, restarts, judges", f"exit {code}\n{out}")
        with open(os.path.join(judge_dir, "judge.py"), encoding="utf-8") as f:
            new_judge = f.read()
        check("marker-v9.9" in new_judge and sha(os.path.join(judge_dir, ".backup", "judge.py")) == old_judge,
              "judge.py replaced, old one kept in Judge/.backup/")
        with open(os.path.join(root, "README.txt"), encoding="utf-8") as f:
            readme = f.read()
        with open(os.path.join(set1, "Makefile"), encoding="utf-8") as f:
            makefile = f.read()
        check("marker-v9.9" in readme and "marker-v9.9" in makefile
              and os.path.exists(os.path.join(judge_dir, ".backup", "_package", TOWERS_SET, "Makefile")),
              f"managed files README.txt and {TOWERS_SET}/Makefile replaced, old copies in Judge/.backup/_package/")
        check(sha(os.path.join(set1, TOWERS_CPP)) == student_hash and sha(os.path.join(set1, other)) == template,
              "student files untouched")
        check(os.path.exists(os.path.join(set1, "7.cpp")) and sha(os.path.join(set1, "7.cpp")) == template,
              f"create-only {TOWERS_SET}/7.cpp added")
        check(not os.path.exists(os.path.join(judge_dir, ".update_tmp")), "no temp folder left behind")
        progress = os.path.join(judge_dir, "progress.json")
        with open(progress, encoding="utf-8") as f:
            best = json.load(f)["problems"].get(TOWERS_ID, {}).get("best")
        check(best == 100 and not os.path.exists(os.path.join(judge_dir, ".backup", "progress.json")),
              "progress.json kept (best 100) and not backed up", f"best = {best}")
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 0 and "up to date" in out, "--update: up to date", f"exit {code}\n{out}")

        # b) a newer version appears: normal runs wait 10 minutes, --update takes it now
        repo2 = make_repo2(tmp, "9.11", "marker-v9.11")
        code, out, _ = run_student([TOWERS_CPP, "--no-color"], set1, url)
        check(code == 0 and "Judge v9.9" in out and "restarting" not in out, "checked recently: no update yet")
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 0 and "updated to v9.11" in out, "--update: updated to v9.11", f"exit {code}\n{out}")

        # c) served file does not match its hash: nothing changes
        edit_manifest(repo2, lambda m: m["files"].update({"README.txt": "1" * 64}) or m.update(version="9.12"))
        before = sha(os.path.join(judge_dir, "README.txt"))
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 1 and "hash mismatch" in out and sha(os.path.join(judge_dir, "README.txt")) == before
              and "9.11" in open(os.path.join(judge_dir, "manifest.json"), encoding="utf-8").read(),
              "bad hash: update refused, files unchanged", f"exit {code}\n{out}")

        # d) manifest with a path outside Judge/: refused
        rebuild_manifest(repo2)
        edit_manifest(repo2, lambda m: m["files"].update({"../evil.txt": "0" * 64}) or m.update(version="9.13"))
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 1 and "bad path" in out and not os.path.exists(os.path.join(root, "evil.txt")),
              "path outside Judge/: refused", f"exit {code}\n{out}")
        rebuild_manifest(repo2)
        edit_manifest(repo2, lambda m: m["managed"].update(
            {TOWERS_SET + "/" + TOWERS_CPP: [sha(os.path.join(repo2, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]})
            or m.update(version="9.14"))
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 1 and "bad managed entry" in out and sha(os.path.join(set1, TOWERS_CPP)) == student_hash,
              "a .cpp listed as managed: refused, student file untouched", f"exit {code}\n{out}")

        # e) recovery: a damaged file is re-downloaded by python Judge/updater.py
        rebuild_manifest(repo2)
        os.remove(os.path.join(judge_dir, "README.txt"))
        shutil.rmtree(os.path.join(root, ".vscode"))     # lost when the package was copied (hidden folder)
        env = dict(os.environ, JUDGE_UPDATE_URL=url)
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], env=env, cwd=set1,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        check(p.returncode == 0 and os.path.exists(os.path.join(judge_dir, "README.txt")),
              "python Judge/updater.py restores a missing file", f"exit {p.returncode}\n{out}")
        check(os.path.exists(os.path.join(root, ".vscode", "tasks.json")),
              "a missing .vscode/ (Ctrl+Shift+B task) is restored too", f"exit {p.returncode}\n{out}")
        srv.shutdown()

        # f) no network: the judge works as usual, quickly
        os.remove(os.path.join(judge_dir, ".update_check"))
        code, out, dt = run_student([TOWERS_CPP, "--no-color"], set1, f"http://127.0.0.1:{free_port()}/")
        check(code == 0 and "ACCEPTED" in out and "restarting" not in out and dt < 30,
              f"offline: judge works ({dt:.1f} s)", f"exit {code}\n{out}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_data():
    """Every problem's own manifest.json lists the tests on disk with the right hashes."""
    print("Test data")
    p = subprocess.run([sys.executable, os.path.join(REPO, "tools", "update_problem_manifest.py"), "--check", "--all"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    check(p.returncode == 0, "problem manifests match the test files", p.stdout.decode("utf-8", "replace"))


def test_manifest():
    print("Manifest")
    p = subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_manifest.py"), "--check"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    check(p.returncode == 0, "manifest.json is up to date", p.stdout.decode("utf-8", "replace"))


def test_fast_update():
    """A judge from before 2.3 (one download per file) takes only the new judge.py / updater.py; the new updater
    then gets a whole new set in a few requests (a bundle for the test data, one template for all N.cpp)."""
    print("Fast update")
    tmp = tempfile.mkdtemp(prefix="judge_fast_")
    try:
        subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_dist.py"), "--out", tmp, "--no-zip"],
                       check=True, stdout=subprocess.DEVNULL)
        root = os.path.join(tmp, os.listdir(tmp)[0])
        judge_dir = os.path.join(root, "Judge")
        last = sorted(d for d in os.listdir(root) if d.startswith("Mock_"))[-1]      # e.g. Mock_A12
        # an old package: the updater and manifest of the last format-1 release
        shutil.copy(os.path.join(REPO, "tests", "fixtures", "updater_v2.py"), os.path.join(judge_dir, "updater.py"))
        shutil.copy(os.path.join(REPO, "tools", "legacy_manifest.json"), os.path.join(judge_dir, "manifest.json"))
        log = []
        srv, url = serve(REPO, log)
        env = dict(os.environ, JUDGE_UPDATE_URL=url)
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], env=env, cwd=root,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        got = sorted(set(log) - {"/manifest.json"})
        check(p.returncode == 0 and got and set(got) <= {"/core/judge.py", "/core/updater.py"}
              and sha(os.path.join(judge_dir, "updater.py")) == sha(os.path.join(REPO, "core", "updater.py")),
              f"old updater takes only the new updater ({len(log)} requests)", f"{got}\n{out}")
        # the new updater, and a set whose folder is not there yet
        shutil.rmtree(os.path.join(judge_dir, "problems", "batch", last))
        shutil.rmtree(os.path.join(root, last))
        del log[:]
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], env=env, cwd=root,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        data = os.path.join(judge_dir, "problems", "batch", last)
        files = [f for _, _, fs in os.walk(data) for f in fs]
        check(p.returncode == 0 and len(files) > 5 and os.path.exists(os.path.join(root, last, "1.cpp"))
              and os.path.exists(os.path.join(root, last, last + ".pdf")) and len(log) <= 12,
              f"new updater installs {last} ({len(files)} files) in {len(log)} requests", f"{log}\n{out}")
        with open(os.path.join(judge_dir, "manifest.json"), encoding="utf-8") as f:
            installed = json.load(f)
        check("full" not in installed and "full_v7" not in installed and not installed.get("bootstrap")
              and installed.get("version") == build_version(),
              "the installed manifest is the full version")
        srv.shutdown()

        # a bundle that does not match its hash: refused, nothing installed
        repo2 = make_repo2(tmp, "9.9", "marker-bundle")
        edit_manifest(repo2, lambda m: m["bundles"]["bundles/%s.zip" % last].update(sha256="0" * 64))
        shutil.rmtree(data)
        srv, url = serve(repo2)
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")],
                           env=dict(os.environ, JUDGE_UPDATE_URL=url), cwd=root,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        check(p.returncode == 1 and "hash mismatch" in out and not os.path.exists(data)
              and "marker-bundle" not in open(os.path.join(judge_dir, "judge.py"), encoding="utf-8").read(),
              "bad bundle: update refused, nothing installed", out)
        srv.shutdown()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_version():
    with open(os.path.join(REPO, "VERSION"), encoding="utf-8") as f:
        return f.read().strip()



def main():
    global judge
    if not shutil.which("g++"):
        print("g++ not found: the regression tests need a C++ compiler in PATH.")
        return 1
    tmp = tempfile.mkdtemp(prefix="judge_dist_")
    try:
        root = build_package(tmp)
        if root:
            sys.path.insert(0, os.path.join(root, "Judge"))
            sys.dont_write_bytecode = True
            import judge as package_judge
            judge = package_judge
            test_package(root)
            test_crlf_generator()
            test_samples()
            test_stale_tests()
            test_scoring()
            test_exited_peak()
            test_missed_last_reading()
            test_cli(root)
            test_tracks(root)
            test_bootstrap_view()
            test_moves(root, tmp)
            test_moves(root, tmp, "6.0")
            test_moves(root, tmp, "6.1")
            test_moves_70(root, tmp)
            test_updater()
            test_fast_update()
            test_data()
            test_manifest()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print()
    if FAILED:
        print(f"{len(FAILED)} FAILED: " + ", ".join(FAILED))
        return 1
    print("All regression tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
