#!/usr/bin/env python3
"""
Regression tests for the POSN Camp 2 Practice Judge.

  python3 tests/run_regression.py          run everything (exit code 0 = all passed)

Everything runs inside a student package built with tools/build_dist.py in a temporary folder, so the big tests
that gen.py rebuilds and progress.json are never written into the repo.
1. Package: no rebuilt tests and no progress.json are shipped.
2. Student package (one folder per problem): the layout of every set and problem folder (tools/layout.py and
   judge.py agree), judging from the problem folder, from the set folder, by file name and by folder, the tracker
   (scores by problem id), make / judge.bat in the set folder / the VS Code tasks, nothing left behind (Judge/.build/ is empty).
3. Every sample in samples/expected.json is judged and must get its verdict (and score, when given; that run
   also rebuilds the problem's big tests with gen.py and checks them).
   Verdict = CE if it does not compile, else the first non-AC verdict, else AC.
4. The judge's command line is run like a student would (--ascii, --list, --progress, --set).
5. Self-update: a local HTTP server serves a modified copy of the repo as v9.9; a package must update itself
   (hashes, backups, restart, create-only code files), and must refuse bad hashes, bad paths and no network.
   Fast update: a whole new set arrives in a few requests.
6. A later release (a fake next version over local HTTP): re-titled, replaced and moved problems, a clash, files the updater
   did not ship, tracker scores kept, a quiet second run.
7. Reports to the teacher (tests/report_tests.py, the same file in C2_PRACTICE): login, outbox, pull,
   backup / restore, speed, against tools/fake_report_server.py on this computer.
8. The problem manifests and manifest.json are up to date.
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
sys.path.insert(0, os.path.join(REPO, "tools"))
import layout  # noqa: E402      (the names of the student package)

SAMPLES = os.path.join(REPO, "samples")
NAME = "C2_Mock_Test"
FAILED = []
os.environ["JUDGE_NO_UPDATE"] = "1"       # the judge never contacts GitHub during the tests
os.environ["JUDGE_REPORT_URL"] = "off"    # ... nor the teacher's report server (report_tests uses a fake one)
os.environ["STUPIDGRADER_HOME"] = tempfile.mkdtemp(prefix="judge_login_")   # never the real login file
judge = None        # the package's judge.py, imported by main()
# the towers_*.cpp samples solve Signal Towers (id 14): judged by its id; its set folder (TOWERS_SET), problem folder
# (TOWERS_N) and code file (TOWERS_CPP) come from problems.json, so the tests follow the problem when it moves
TOWERS_ID = "14"
with open(os.path.join(REPO, "problems", "batch", "problems.json"), encoding="utf-8") as _f:
    _e = json.load(_f)[TOWERS_ID]
TOWERS_TITLE = _e["en"]
TOWERS_SET, TOWERS_N = _e["dir"].split("/")                 # Mock_A07, 3
TOWERS_KEY = TOWERS_SET[len("Mock_"):]                      # A07
TOWERS_CPP = os.path.basename(layout.entry_code_path(_e))   # A07-3.cpp
TOWERS = f"{TOWERS_KEY[0]}{int(TOWERS_KEY[1:])}-{TOWERS_N}"  # A7-3
OTHER_N = "1" if TOWERS_N != "1" else "2"                   # a problem of the same set the tests leave empty
OTHER_CPP = f"{TOWERS_KEY}-{OTHER_N}.cpp"


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


# ----------------------------------------------------------------------------- reports to the teacher
def test_reports():
    import report_tests
    tmp = tempfile.mkdtemp(prefix="judge_report_")
    try:
        root = build_package(tmp)
        if root:
            report_tests.run(check, root, f"{TOWERS_SET}/{TOWERS_N}", TOWERS_CPP, int(TOWERS_ID),
                             os.path.join(SAMPLES, "batch", "towers_ok.cpp"), "mock",
                             sibling=os.path.join(os.path.dirname(REPO), "C2_PRACTICE"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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



def problems_json():
    with open(os.path.join(REPO, "problems", "batch", "problems.json"), encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------------- 2. one folder per problem
def test_layout(root):
    """The package is laid out as tools/layout.py says, and judge.py names the files the same way."""
    print("Student package (one folder per problem)")
    sets, meta = judge.load_sets(), problems_json()
    bad, agree, count = [], True, 0
    for s in sets:
        d0 = layout.set_dir(s)
        top = os.path.join(root, d0)
        want_top = {"Makefile", "judge.bat", f"{d0}.pdf"} | {layout.slot(s, i) for i in range(1, len(s["problems"]) + 1)}
        if set(os.listdir(top)) != want_top:
            bad.append(f"{d0}: {sorted(set(os.listdir(top)) ^ want_top)}")
        agree = agree and judge.set_folder(s) == d0
        for i, pid in enumerate(s["problems"], 1):
            count += 1
            agree = agree and judge.code_name(s, i) == layout.code_name(s, i) and judge.slot_name(s, i) == layout.slot(s, i)
            agree = agree and meta[str(pid)]["dir"] == f"{d0}/{i}" and layout.entry_code_path(meta[str(pid)]) == layout.code_path(s, i)
            d = os.path.join(top, layout.slot(s, i))
            want = {layout.code_name(s, i), layout.pdf_name(s, i, layout.file_title(meta[str(pid)]))}
            got = set(os.listdir(d)) if os.path.isdir(d) else set()
            if got != want:
                bad.append(f"{d0}/{layout.slot(s, i)}: {sorted(got ^ want)}")
            elif os.path.getsize(os.path.join(d, layout.code_name(s, i))) != 0:
                bad.append(f"{d0}/{layout.slot(s, i)}: the code file is not empty")
            else:
                with open(os.path.join(d, layout.pdf_name(s, i, layout.file_title(meta[str(pid)]))), "rb") as f:
                    if f.read(5) != b"%PDF-":
                        bad.append(f"{d0}/{layout.slot(s, i)}: not a PDF")
    check(not bad and count == 120, f"every problem folder ({count}) holds exactly its empty code file and its PDF "
          "(no Makefile / judge.bat); every set folder its PDF, Makefile, judge.bat and the problem folders 1 ... 6", "\n".join(bad[:8]))
    check(agree, "judge.py and tools/layout.py name the set folders, problem folders and code files the same way")
    with open(os.path.join(root, "Judge", "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    import importlib.util
    spec = importlib.util.spec_from_file_location("package_updater", os.path.join(root, "Judge", "updater.py"))
    upd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upd)
    check(all(upd.set_path(rel) for rel in man["create_only"]) and all(upd.managed_path(rel) for rel in man["managed"])
          and sum(1 for rel in man["managed"] if upd.problem_pdf(rel)) == count,
          "updater.py accepts every package path of the manifest (its path rules agree with tools/layout.py)")
    names = [n for _, _, fs in os.walk(root) for n in fs] + [n for _, ds, _ in os.walk(root) for n in ds]
    check(all(n.isascii() and " " not in n for n in names), "every file and folder name is ASCII without spaces")
    pdfs = [layout.pdf_name(s, i, layout.file_title(meta[str(pid)])) for s in sets for i, pid in enumerate(s["problems"], 1)]
    check(all(re.fullmatch(r"[1-9]_[A-Za-z0-9_]{1,60}\.pdf", n) for n in pdfs),
          "problem PDF names: <n>_<EnglishTitle>.pdf, letters, digits and _ only, title at most 60 characters")
    long_en = "Reincarnated as a Dark Lord Before Taking Over the World with Power 999999999"
    override = [(s, i, meta[str(pid)]) for s in sets for i, pid in enumerate(s["problems"], 1)
                if meta[str(pid)].get("file_title")]
    check(layout.pdf_name({"set": "A01"}, 1, layout.file_title({"en": long_en, "file_title": "Dark_Lord_Power_999999999"}))
          == "1_Dark_Lord_Power_999999999.pdf"
          and layout.file_title({"en": long_en}) == long_en and len(layout.title_slug(long_en)) == 60
          and override and all(os.path.isfile(os.path.join(root, *layout.pdf_path(s, i, e["file_title"]).split("/")))
                               and not os.path.exists(os.path.join(root, *layout.pdf_path(s, i, e["en"]).split("/")))
                               for s, i, e in override),
          "file-name override: a problems.json \"file_title\" names the problem's PDF instead of its English title "
          "(Mock_A01/1 -> 1_Dark_Lord_Power_999999999.pdf, not the 60-character cut of the long title)",
          str([(layout.set_dir(s), i, e.get("file_title")) for s, i, e in override]))
    check(layout.title_slug("Mo's  Algo-rithm: 2 (hard)") == "Mos_Algorithm_2_hard" and len(layout.title_slug("x" * 80)) == 60,
          "title -> file name: spaces become _, other characters are dropped, at most 60 characters")
    stray = [os.path.join(dp, n) for dp, _, fs in os.walk(root) for n in fs
             if "Judge" not in os.path.relpath(dp, root).split(os.sep)
             and (n.endswith((".in", ".out", ".exe", ".o")) or n == "a.out")]
    check(not stray, "no sample files or binaries in the set and problem folders", str(stray[:5]))
    starters = glob.glob(os.path.join(root, "Mock_*", "*", "*.cpp"))
    check(len(starters) == count and all(judge.is_untouched_starter(q) for q in starters),
          "the code files are untouched starters (a run on one is not recorded)", f"{len(starters)} files")


def progress_best(root):
    try:
        with open(os.path.join(root, "Judge", "progress.json"), encoding="utf-8") as f:
            return json.load(f)["problems"][TOWERS_ID]["best"]
    except (OSError, ValueError, KeyError):
        return None


def towers_solved(out, slot=TOWERS_N):
    """True when the --progress view shows Signal Towers as solved, as problem `slot` of its set."""
    return any(ln.split()[:1] == [str(slot)] and TOWERS_TITLE[:12] in ln and "solved" in ln for ln in out.splitlines())


def test_judging(root, tmp):
    """Judging from the problem folder, from the set folder, by file name and by folder; the tracker records the
    score under the problem's id; nothing is left in the folders, and Judge/.build/ is empty afterwards."""
    set1 = os.path.join(root, TOWERS_SET)
    prob = os.path.join(set1, TOWERS_N)
    mine = os.path.join(TOWERS_N, TOWERS_CPP)
    ok_cpp = os.path.join(SAMPLES, "batch", "towers_ok.cpp")
    code, out, _ = run_judge(["--no-color"], prob)
    check(code == 0 and f"{TOWERS_CPP} is empty" in out and "Compil" not in out,
          "an empty code file: plain message, no compile", f"exit {code}\n{out}")
    check(progress_best(root) is None, "a run on an untouched starter is not recorded")
    shutil.copy(ok_cpp, os.path.join(prob, TOWERS_CPP))
    before = {dp: sorted(fs) for dp, _, fs in os.walk(set1)}
    code, out, _ = run_judge(["--no-color"], prob)
    check(code == 0 and "ACCEPTED" in out and TOWERS_CPP in out and "../../Judge/judge.py --progress" in out.replace("\\", "/"),
          "inside the problem folder: judge.py (no arguments)", f"exit {code}\n{out}")
    check(progress_best(root) == 100, f"progress.json records best 100 under the problem's id ({TOWERS_ID})",
          f"best = {progress_best(root)}")
    for cwd, what in ((prob, "the problem folder"), (set1, "the set folder"), (root, "the package folder")):
        code, out, plain = run_judge(["--progress", TOWERS_KEY, "--no-color", "--ascii"], cwd)
        check(code == 0 and plain and towers_solved(out), f"--progress shows the 100 (run in {what})", f"exit {code}\n{out}")
    code, out, _ = run_judge([TOWERS_CPP, "--no-color"], prob)
    check(code == 0 and "ACCEPTED" in out, f"inside the problem folder: judge.py {TOWERS_CPP}", f"exit {code}\n{out}")
    for arg in (TOWERS_N, mine):
        code, out, _ = run_judge([arg, "--no-color"], set1)
        check(code == 0 and "ACCEPTED" in out, f"inside the set folder: judge.py {arg}", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--no-color"], set1)
    check(code == 0 and "Total" in out and f"{OTHER_N}/{OTHER_CPP} is still empty - skipped" in out and "Problem 6" in out
          and " 100 / 600" in out, "inside the set folder: judge.py (whole set)", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--set", TOWERS_KEY, set1, "--no-color"], tmp)
    check(code == 0 and " 100 / 600" in out, f"anywhere: judge.py --set {TOWERS_KEY} FOLDER", f"exit {code}\n{out}")
    code, out, _ = run_judge([os.path.join(root, TOWERS_SET, TOWERS_N), "--no-color"], tmp)
    check(code == 0 and "ACCEPTED" in out, f"anywhere: judge.py <path>/{TOWERS_SET}/{TOWERS_N}", f"exit {code}\n{out}")
    code, out, _ = run_judge([os.path.join(set1, mine), "--no-color"], tmp)
    check(code == 0 and "ACCEPTED" in out, f"anywhere: judge.py <path>/{TOWERS_CPP} (the VS Code task)", f"exit {code}\n{out}")
    code, out, _ = run_judge([os.path.join(root, "Progress.md"), "--no-color"], prob)
    check(code == 0 and "Progress" in out and "Track A" in out and "ACCEPTED" not in out,
          "Ctrl+Shift+B on a file that is not a .cpp shows the progress dashboard", f"exit {code}\n{out[:600]}")
    away = os.path.join(tmp, "elsewhere")
    os.makedirs(away)
    for name in (TOWERS_CPP, TOWERS_CPP.lower(), f"{TOWERS_KEY[0].lower()}{int(TOWERS_KEY[1:])}-{TOWERS_N}.cpp"):
        shutil.copy(ok_cpp, os.path.join(away, name))
        code, out, _ = run_judge([os.path.join(away, name), "--no-color"], away)
        check(code == 0 and "ACCEPTED" in out, f"by file name alone: {name} in another folder", f"exit {code}\n{out}")
    shutil.copy(ok_cpp, os.path.join(prob, "second_try.cpp"))
    code, out, _ = run_judge(["second_try.cpp", "--no-color"], prob)
    check(code == 0 and "ACCEPTED" in out, "by folder alone: another .cpp inside the problem folder", f"exit {code}\n{out}")
    os.remove(os.path.join(prob, "second_try.cpp"))
    code, out, _ = run_judge([os.path.join(away, TOWERS_CPP), f"{TOWERS_KEY}-{OTHER_N}", "--no-color", "--stop"], away)
    check(code == 0 and "ACCEPTED" not in out and "Problem not found" not in out and "Result" in out,
          "an explicit K-P wins over the file name", f"exit {code}\n{out}")
    shutil.copy(ok_cpp, os.path.join(away, "mine.cpp"))
    code, out, _ = run_judge([os.path.join(away, "mine.cpp"), "--no-color"], away)
    check(code == 1 and "Cannot tell which problem" in out and "Mock_A03/5/A03-5.cpp" in out and "do not rename" in out,
          "a .cpp with no problem in its name or folders: a clear message", f"exit {code}\n{out}")
    shutil.copy(ok_cpp, os.path.join(set1, "3.cpp"))             # the flat name of the old layout means nothing now
    code, out, _ = run_judge(["3.cpp", "--no-color"], set1)
    check(code == 1 and "Cannot tell which problem" in out, "a flat N.cpp in the set folder is not a problem's file",
          f"exit {code}\n{out}")
    os.remove(os.path.join(set1, "3.cpp"))
    code, out, _ = run_judge(["9", "--no-color"], set1)
    check(code != 0 and "Traceback" not in out, "inside the set folder: judge.py 9 is refused", f"exit {code}\n{out}")
    code, out, _ = run_judge([TOWERS_CPP + ".txt", "--no-color"], prob)
    check(code == 1 and "Source file not found" in out and "Mock_<set>/<problem>/<set>-<problem>.cpp" in out,
          "a missing file: the message says where code files live", f"exit {code}\n{out}")
    if os.name != "nt" and shutil.which("make"):
        env = dict(os.environ, PYTHON=sys.executable, NO_COLOR="1")
        for cwd, args, want, what in ((set1, [TOWERS_N], "ACCEPTED", f"make {TOWERS_N} in the set folder"),
                                      (set1, [], " 100 / 600", "make in the set folder (whole set)"),
                                      (set1, ["progress"], "Track A", "make progress in the set folder")):
            r = subprocess.run(["make"] + args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = r.stdout.decode("utf-8", "replace")
            check(r.returncode == 0 and want in out, what, out[-600:])
        bad = []            # `make 6` once fell back to make's built-in rule (compiled 6.cpp, no judging)
        for d in sorted(glob.glob(os.path.join(root, "Mock_*"))):
            r = subprocess.run(["make", "-n", "6"], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if r.returncode != 0 or not r.stdout.decode("utf-8", "replace").rstrip().endswith("judge.py 6"):
                bad.append(os.path.basename(d))
        check(not bad, "make -n 6 calls judge.py 6 in every set folder", ", ".join(bad))
    with open(os.path.join(set1, "judge.bat"), "rb") as f:
        set_bat = f.read()
    check(b'"..\\Judge\\judge.py" %1' in set_bat and b'cd /d "%~dp0"' in set_bat
          and set_bat.count(b"\r\n") == set_bat.count(b"\n") > 5 and b'if "%~1"=="" pause' in set_bat,
          "judge.bat (set folder): quoted paths, runs from its own folder, passes %1, CRLF")
    check(not glob.glob(os.path.join(root, "Mock_*", "*", "Makefile")) and not glob.glob(os.path.join(root, "Mock_*", "*", "judge.bat")),
          "no Makefile or judge.bat in any problem folder (they are in the set folders only)")
    with open(os.path.join(root, ".vscode", "tasks.json"), encoding="utf-8") as f:
        tasks = json.load(f)["tasks"]
    check(tasks[0]["args"][-1] == "${file}" and tasks[0]["group"].get("isDefault") and "/.." in tasks[1]["options"]["cwd"]
          and any("--progress" in t["args"] for t in tasks),
          "VS Code: Ctrl+Shift+B judges the open file, the second task the whole set, a task shows the progress")
    after = {dp: sorted(fs) for dp, _, fs in os.walk(set1)}
    check(after == before, "judging leaves no binary or temporary file in the set or problem folders",
          str([(k, v) for k, v in after.items() if before.get(k) != v][:3]))
    build = os.path.join(root, "Judge", ".build")
    check(os.path.isdir(build) and os.listdir(build) == [], "programs are compiled in Judge/.build/, which is empty afterwards",
          str(os.listdir(build)) if os.path.isdir(build) else "no Judge/.build")
    os.chmod(build, 0o500)
    try:
        if os.name != "nt" and not os.access(build, os.W_OK):       # (root can always write: skipped then)
            code, out, _ = run_judge(["--no-color"], prob)
            check(code == 0 and "ACCEPTED" in out and os.listdir(build) == [],
                  "Judge/.build/ not writable: the judge compiles in the system temp folder instead", f"exit {code}\n{out}")
    finally:
        os.chmod(build, 0o700)
    code, out, _ = run_judge(["--list", "--no-color"], root)
    check(code == 0 and f"{TOWERS_CPP[:-4]} " in out and f"{TOWERS_SET}/1 ... 6" in out and "Mock_B08/1 ... 6" in out,
          "judge.py --list shows the folders and code names", f"exit {code}\n{out[:900]}")
    code, out, _ = run_judge(["--set", TOWERS_KEY, "--no-color"], set1)
    check(code == 0 and f"{TOWERS_SET}/1/{TOWERS_KEY}-1.cpp" in out, "judge.py --set K says where the code files are",
          f"exit {code}\n{out}")


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
def judge_from(cwd):
    """judge.py of the package that holds cwd, as a student types it there (../Judge/judge.py, ../../Judge/judge.py);
    its full path when cwd is not inside the package."""
    full = os.path.join(PACKAGE[0], "Judge", "judge.py")
    d = os.path.abspath(cwd)
    for up in ("", os.pardir, os.path.join(os.pardir, os.pardir)):
        if os.path.isfile(os.path.join(d, up, "Judge", "judge.py")):
            return os.path.join(up, "Judge", "judge.py")
    return full


PACKAGE = [None]    # the package built by main()


def run_judge(args, cwd):
    """Run judge.py like a student in the folder cwd. Returns (exit code, output, output is ASCII)."""
    p = subprocess.run([sys.executable, judge_from(cwd)] + args, cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stdout.isascii()


def test_cli(root, tmp):
    print("Command line")
    set1 = os.path.join(root, TOWERS_SET)
    work = os.path.join(tmp, "work")            # other programs for the same problem, judged with an explicit K-P
    os.makedirs(work)
    for name in ("towers_ok.cpp", "towers_smallhi.cpp", "towers_throw.cpp", "towers_warn.cpp", "towers_mle.cpp", "towers_deep.cpp"):
        shutil.copy(os.path.join(SAMPLES, "batch", name), os.path.join(work, name))
    code, out, _ = run_judge(["towers_throw.cpp", TOWERS, "--no-color", "--stop"], work)
    check("out_of_range" in out and "stderr" in out, "RE shows the program's stderr (out_of_range)", out)
    code, out, _ = run_judge(["towers_warn.cpp", TOWERS, "--no-color", "--stop"], work)
    check("g++ warning" in out and "unused" in out, "warnings are shown after Compiled", out)
    code, out, _ = run_judge(["towers_ok.cpp", TOWERS, "--no-color", "--stop"], work)
    check("warning" not in out and "Memory  peak" in out and "256 MB per test" in out,
          "clean program: no warnings, memory line, limit in header", out)
    code, out, _ = run_judge(["towers_mle.cpp", TOWERS, "--no-color", "--stop", "--ml", "200"], work)    # 400 MB
    check("Memory Limit Exceeded" in out and "limit is 200 MB" in out, "--ml 200: a 400 MB program is MLE", out)
    code, out, _ = run_judge(["towers_mle.cpp", TOWERS, "--no-color", "--stop", "--ml", "1024"], work)
    check(code == 0 and "ACCEPTED" in out, "--ml 1024: the same program is accepted", f"exit {code}\n{out}")
    code, out, _ = run_judge(["towers_deep.cpp", TOWERS, "--no-color", "--stop"], work)
    check(code == 0 and "ACCEPTED" in out, "a recursive DFS of depth 10^6 runs (256 MB stack)", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--ml", "0"], set1)
    check(code == 2 and "--ml must be" in out, "judge.py --ml 0 is rejected", f"exit {code}\n{out}")
    code, out, plain = run_judge(["towers_smallhi.cpp", TOWERS, "--ascii", "--no-color"], work)
    check(code == 0 and "First failure" in out and plain, "judge.py --ascii shows the failure, ASCII only",
          f"exit {code}, ascii={plain}\n{out}")
    code, out, plain = run_judge(["--progress", "--ascii"], set1)
    check(code == 0 and plain, "judge.py --progress --ascii", f"exit {code}, ascii={plain}\n{out}")
    code, out, plain = run_judge(["--list", "--ascii"], set1)
    check(code == 0 and "Set A4" in out and plain, "judge.py --list --ascii", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--tl", "abc"], set1)
    check(code == 2 and "--tl must be" in out, "judge.py --tl abc is rejected", f"exit {code}\n{out}")
    build = os.path.join(root, "Judge", ".build")
    check(os.listdir(build) == [], "Judge/.build/ is empty after judging", str(os.listdir(build)))


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
    """fn changes manifest.json as updaters read it."""
    p = os.path.join(repo2, "manifest.json")
    with open(p, encoding="utf-8") as f:
        m = json.load(f)
    fn(m)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(m, f)


def run_student(args, cwd, url):
    env = dict(os.environ, JUDGE_UPDATE_URL=url)
    env.pop("JUDGE_NO_UPDATE", None)
    t0 = time.time()
    p = subprocess.run([sys.executable, judge_from(cwd)] + args, cwd=cwd, env=env,
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
        one = os.path.join(TOWERS_N, TOWERS_CPP)
        other = os.path.join(OTHER_N, OTHER_CPP)                  # a starter the student has not touched
        new = os.path.join("7", f"{TOWERS_KEY}-7.cpp")
        shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), os.path.join(set1, one))
        student_hash, old_judge = sha(os.path.join(set1, one)), sha(os.path.join(judge_dir, "judge.py"))
        template = sha(os.path.join(set1, other))

        # a) automatic update during a normal run: new files, backup, restart with the new judge
        repo2 = make_repo2(tmp, "9.9", "marker-v9.9")
        edit_manifest(repo2, lambda m: m["create_only"].update(
            {f"{TOWERS_SET}/7/{TOWERS_KEY}-7.cpp": [sha(os.path.join(REPO, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]}))
        srv, url = serve(repo2)
        code, out, _ = run_student([one, "--no-color"], set1, url)
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
        check(sha(os.path.join(set1, one)) == student_hash and sha(os.path.join(set1, other)) == template,
              "student files untouched")
        check(os.path.exists(os.path.join(set1, new)) and sha(os.path.join(set1, new)) == template,
              f"a create-only code file ({TOWERS_SET}/7/{TOWERS_KEY}-7.cpp) is added")
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
        code, out, _ = run_student([one, "--no-color"], set1, url)
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
            {f"{TOWERS_SET}/{TOWERS_N}/{TOWERS_CPP}": [sha(os.path.join(repo2, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]})
            or m.update(version="9.14"))
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 1 and "bad managed entry" in out and sha(os.path.join(set1, one)) == student_hash,
              "a .cpp listed as managed: refused, student file untouched", f"exit {code}\n{out}")
        wrong = (f"{TOWERS_SET}/1.cpp", f"{TOWERS_SET}/1/1.cpp", f"{TOWERS_SET}/1/B99-1.cpp", f"{TOWERS_SET}/1/{TOWERS_KEY}-2.cpp",
                 f"{TOWERS_SET}/0/{TOWERS_KEY}-0.cpp", f"{TOWERS_SET}/10/{TOWERS_KEY}-10.cpp", "Mock_C01/1/C01-1.cpp",
                 "Mock_1/1/1-1.cpp", "Mock_A1/1/A1-1.cpp", f"{TOWERS_SET}/old/1_X.cpp", f"{TOWERS_SET}/1/sub/{TOWERS_KEY}-1.cpp",
                 "Judge/x.cpp")
        for n, rel in enumerate(wrong):
            rebuild_manifest(repo2)
            edit_manifest(repo2, lambda m: m["create_only"].update(
                {rel: [sha(os.path.join(repo2, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]})
                or m.update(version=f"9.2{n}"))
            code, out, _ = run_student(["--update", "--no-color"], set1, url)
            check(code == 1 and "bad create-only entry" in out and not os.path.exists(os.path.join(root, *rel.split("/"))),
                  f"a create-only path that is not Mock_<set>/<n>/<set>-<n>.cpp is refused ({rel})", f"exit {code}\n{out}")
        for n, rel in enumerate((f"{TOWERS_SET}/notes.pdf", f"{TOWERS_SET}/Mock_B01.pdf", f"{TOWERS_SET}/1/2_Title.pdf",
                                 f"{TOWERS_SET}/1/1_Bad-Title.pdf", f"{TOWERS_SET}/old/Makefile", "Mock_7/Makefile",
                                 "Mock_A01/3/Makefile", "Mock_A01/3/judge.bat")):
            rebuild_manifest(repo2)
            edit_manifest(repo2, lambda m: m["managed"].update(
                {rel: [sha(os.path.join(repo2, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]})
                or m.update(version=f"9.4{n}"))
            code, out, _ = run_student(["--update", "--no-color"], set1, url)
            check(code == 1 and "bad managed entry" in out and not os.path.exists(os.path.join(root, *rel.split("/"))),
                  f"a managed path outside the layout is refused ({rel})", f"exit {code}\n{out}")

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
        code, out, dt = run_student([one, "--no-color"], set1, f"http://127.0.0.1:{free_port()}/")
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


def test_versions():
    """The updater only moves to a strictly newer version. The release served here (9.9) is older-looking content:
    no report.py / config.json, another judge.py and a re-titled problem PDF (what made a newer build go back to 4.0.0,
    retiring its PDFs). Installed newer (9.10) or the same (9.9): nothing changes, even with --update. Older (9.8):
    the normal update."""
    print("Update only to a newer version")
    tmp = tempfile.mkdtemp(prefix="judge_ver_")
    try:
        root = build_package(tmp)
        judge_dir, set1 = os.path.join(root, "Judge"), os.path.join(root, TOWERS_SET)
        repo2 = make_repo2(tmp, "9.9", "marker-v9.9")
        for name in ("report.py", "config.json"):            # files of a newer build (grader-discord)
            if os.path.exists(os.path.join(repo2, "core", name)):
                os.remove(os.path.join(repo2, "core", name))
        rebuild_manifest(repo2)
        pdf = next(k for k in sorted(json.load(open(os.path.join(repo2, "manifest.json"), encoding="utf-8"))["managed"])
                   if re.fullmatch(r".+/[0-9]+/[0-9]+_[A-Za-z0-9_]+\.pdf", k))
        retitled = pdf.rsplit("/", 1)[0] + "/" + pdf.rsplit("/", 1)[1].split("_")[0] + "_Retitled_Problem.pdf"
        edit_manifest(repo2, lambda m: m["managed"].update({retitled: m["managed"].pop(pdf)}))
        srv, url = serve(repo2)

        def mark(version):
            p = os.path.join(judge_dir, "manifest.json")
            with open(p, encoding="utf-8") as f:
                m = json.load(f)
            m["version"] = version
            with open(p, "w", encoding="utf-8") as f:
                json.dump(m, f)

        def snapshot():
            out = {}
            for dp, ds, fs in os.walk(root):
                for f in fs:
                    rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
                    if rel not in ("Judge/.update_check", "Judge/manifest.json"):
                        out[rel] = sha(os.path.join(dp, f))
            return out

        def runs():
            outs = []
            for args in (["--list"], ["--update"]):
                if os.path.exists(os.path.join(judge_dir, ".update_check")):
                    os.remove(os.path.join(judge_dir, ".update_check"))
                outs.append(run_student(args + ["--no-color"], set1, url)[1])
            return outs

        before = snapshot()
        for version, word in (("9.10", "newer than the published v9.9"), ("9.9.0", "up to date")):
            mark(version)
            auto, forced = runs()
            check(snapshot() == before and "restarting" not in auto and word in forced
                  and not os.path.exists(os.path.join(judge_dir, ".backup")),
                  f"installed {version}, release 9.9: nothing changes (no file, no PDF retired), also with --update",
                  forced[-500:])
        header = os.path.join("include", "bits", "stdc++.h")         # the same bytes in the release: put back
        os.remove(os.path.join(judge_dir, header))
        os.remove(os.path.join(judge_dir, "README.txt"))              # other bytes in the release: not touched
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], cwd=set1, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=dict(os.environ, JUDGE_UPDATE_URL=url))
        after = snapshot()
        check("repaired 1 files" in p.stdout.decode() and after.get("Judge/include/bits/stdc++.h") == before["Judge/include/bits/stdc++.h"]
              and after.get("Judge/README.txt") is None and after.get("Judge/report.py") == before.get("Judge/report.py"),
              "same version, forced: only a file the release has exactly as installed is put back (README.txt differs: not)",
              p.stdout.decode()[-300:])
        shutil.copy(os.path.join(REPO, "core", "README.txt"), os.path.join(judge_dir, "README.txt"))
        mark("9.8")
        auto, _ = runs()
        check("restarting" in auto and "marker-v9.9" in open(os.path.join(judge_dir, "judge.py"), encoding="utf-8").read()
              and os.path.exists(os.path.join(root, *retitled.split("/"))),
              "installed 9.8, release 9.9: the normal update", auto[-500:])
        srv.shutdown()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_fast_update():
    """A package from a release before the newest set gets that whole set in a few requests (a bundle for the test
    data, one template for all the code files, the set folder's Makefile and judge.bat, one PDF per problem; a
    problem folder gets its code file and its PDF, nothing else)."""
    print("Fast update")
    tmp = tempfile.mkdtemp(prefix="judge_fast_")
    try:
        subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_dist.py"), "--out", tmp, "--no-zip"],
                       check=True, stdout=subprocess.DEVNULL)
        root = os.path.join(tmp, NAME)
        judge_dir = os.path.join(root, "Judge")
        last = sorted(d for d in os.listdir(root) if d.startswith("Mock_"))[-1]      # e.g. Mock_B08
        last_set = next(s for s in judge.load_sets() if layout.set_dir(s) == last)
        last_n = len(last_set["problems"])
        # an older package: its manifest does not know the last set, whose folders are not there yet
        with open(os.path.join(judge_dir, "manifest.json"), encoding="utf-8") as f:
            old = json.load(f)
        old["version"] = "0.9"
        old["files"] = {k: v for k, v in old["files"].items() if not k.startswith("problems/batch/%s/" % last)}
        for key in ("managed", "create_only"):
            old[key] = {k: v for k, v in old.get(key, {}).items() if not k.startswith(last + "/")}
        old.pop("bundles", None)
        with open(os.path.join(judge_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(old, f)
        shutil.rmtree(os.path.join(judge_dir, "problems", "batch", last))
        shutil.rmtree(os.path.join(root, last))
        log = []
        srv, url = serve(REPO, log)
        env = dict(os.environ, JUDGE_UPDATE_URL=url)
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], env=env, cwd=root,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        data = os.path.join(judge_dir, "problems", "batch", last)
        files = [f for _, _, fs in os.walk(data) for f in fs]
        check(p.returncode == 0 and len(files) > 5
              and os.path.exists(os.path.join(root, *layout.code_path(last_set, last_n).split("/")))
              and os.path.exists(os.path.join(root, last, last + ".pdf"))
              and len(glob.glob(os.path.join(root, last, "*", "*.pdf"))) == last_n
              and all(len(os.listdir(d)) == 2 for d in glob.glob(os.path.join(root, last, "[1-9]")))
              and os.path.isfile(os.path.join(root, last, "Makefile")) and len(log) <= 10 + last_n,
              f"updater installs {last} ({len(files)} files) in {len(log)} requests", f"{log}\n{out}")
        with open(os.path.join(judge_dir, "manifest.json"), encoding="utf-8") as f:
            installed = json.load(f)
        check(installed.get("version") == build_version() and len(installed.get("create_only", {})) == 120,
              "the installed manifest is the new version")
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



def outside_judge(root):
    """{path: bytes} of every file of a package outside Judge/."""
    out = {}
    for dp, ds, fs in os.walk(root):
        if dp == root and "Judge" in ds:
            ds.remove("Judge")
        for n in fs:
            with open(os.path.join(dp, n), "rb") as f:
                out[os.path.relpath(os.path.join(dp, n), root).replace(os.sep, "/")] = f.read()
    return out


def next_release_plan():
    """What the fake later release changes. X = the set of Signal Towers (problem T), Y and Z = two other sets.
    In X: T and U swap places, R2 and R9 are re-titled, P3 and P8 are replaced by new problems.
    Y/1 and Z/1 swap places (a move across sets); the old Y/2 moves to a new slot Y/7 and Y/2 gets a new problem."""
    sets = judge.load_sets()
    sx = next(s for s in sets if layout.set_dir(s) == TOWERS_SET)
    sy, sz = [s for s in sets if s is not sx][:2]
    T = int(TOWERS_N)
    U, R2, R9, P3, P8 = [i for i in range(1, 7) if i != T]
    return sx, sy, sz, T, U, R2, R9, P3, P8


def next_version(v):
    """The version after v (4.1.0 -> 4.1.1, 7.3 -> 7.4): the updater only installs a strictly newer release."""
    parts = v.split(".")
    return ".".join(parts[:-1] + [str(int(parts[-1]) + 1)])


def make_next_release(tmp, version=None):
    """A copy of the repo as that later release (see next_release_plan). Returns (repo2, the old English titles
    {(set, slot): title})."""
    version = version or next_version(build_version())
    repo2 = make_repo2(tmp, version, "marker-" + version)
    batch = os.path.join(repo2, "problems", "batch")
    os.makedirs(os.path.join(repo2, "tools", "moves"), exist_ok=True)       # what the teacher saves at release time
    shutil.copy(os.path.join(REPO, "problems", "batch", "problems.json"),
                os.path.join(repo2, "tools", "moves", f"problems_{build_version()}.json"))
    with open(os.path.join(batch, "problems.json"), encoding="utf-8") as f:
        P = json.load(f)
    with open(os.path.join(batch, "sets.json"), encoding="utf-8") as f:
        S = json.load(f)
    x, y, z, T, U, R2, R9, P3, P8 = next_release_plan()
    sx, sy, sz = (next(s for s in S if s["set"] == q["set"]) for q in (x, y, z))

    def pid(s, i):
        return str(s["problems"][i - 1])

    old = {(s["set"], i): P[pid(s, i)]["en"] for s in (sx, sy, sz) for i in range(1, 7)}

    def swap(sa, i, sb, j):                 # two problems change places: problems.json "dir", sets.json, test data
        a, b = pid(sa, i), pid(sb, j)
        da, db = (os.path.join(batch, *P[q]["dir"].split("/")) for q in (a, b))
        os.rename(da, da + "_x"), os.rename(db, da), os.rename(da + "_x", db)
        P[a]["dir"], P[b]["dir"] = P[b]["dir"], P[a]["dir"]
        sa["problems"][i - 1], sb["problems"][j - 1] = int(b), int(a)

    renamed = {old[sx["set"], R2]: "Renamed Problem Two", old[sx["set"], R9]: "Renamed Problem Nine"}
    for i in (R2, R9):
        P[pid(sx, i)]["en"] = renamed[old[sx["set"], i]]
        P[pid(sx, i)].pop("file_title", None)                              # a re-title drops the file-name override
    for i, title in ((P3, "Brand New Three"), (P8, "Brand New Eight")):
        P[pid(sx, i)]["en"] = title
        P[pid(sx, i)].pop("file_title", None)
    swap(sx, T, sx, U)
    swap(sy, 1, sz, 1)
    ydir = layout.set_dir(sy)
    P["9001"] = dict(P[pid(sy, 2)], dir=f"{ydir}/7")                       # the old Y/2 -> a new slot 7
    shutil.copytree(os.path.join(batch, ydir, "2"), os.path.join(batch, ydir, "7"))
    P[pid(sy, 2)]["en"] = "Brand New Clash"
    P[pid(sy, 2)].pop("file_title", None)
    sy["problems"].append(9001)
    with open(os.path.join(batch, "problems.json"), "w", encoding="utf-8") as f:
        json.dump(P, f, ensure_ascii=False, indent=1)
    with open(os.path.join(batch, "sets.json"), "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=1)
    bm = os.path.join(repo2, "tools", "build_manifest.py")
    with open(bm, encoding="utf-8") as f:
        text = f.read()
    assert text.count("RENAMED = {") == 1, "tools/build_manifest.py: RENAMED = {...} not found once"
    with open(bm, "w", encoding="utf-8") as f:      # this release's renames go in front of the ones already listed
        f.write(text.replace("RENAMED = {", "RENAMED = {" + "".join(f"{k!r}: {v!r}, " for k, v in renamed.items()), 1))
    files = os.path.join(repo2, "student", "set_files")
    shutil.copy(os.path.join(files, "Makefile"), os.path.join(files, "Makefile_7"))
    for s in (sx, sy, sz):                                                 # the PDFs follow the titles
        for i in range(1, len(s["problems"]) + 1):
            d = os.path.join(repo2, "student", layout.set_dir(s), layout.slot(s, i))
            os.makedirs(d, exist_ok=True)
            want = os.path.join(d, layout.pdf_name(s, i, layout.file_title(P[pid(s, i)])))
            if not os.path.exists(want):
                have = glob.glob(os.path.join(d, "*.pdf"))
                if have:
                    os.rename(have[0], want)
                else:
                    shutil.copy(glob.glob(os.path.join(repo2, "student", layout.set_dir(s), "1", "*.pdf"))[0], want)
    rebuild_manifest(repo2)
    return repo2, old


def test_future_update(root=None):
    """From 7.2 on, releases replace, re-title and move problems. A package gets a fake next version over local HTTP: the
    student's written files follow their problems (inside a set and across sets), nothing is overwritten or
    deleted, old PDFs are retired only when their bytes are the shipped ones, the tracker's scores stay with their
    problems (progress.json is not touched), and the second run is quiet."""
    print("A later release (a fake next version over local HTTP)")
    tmp = tempfile.mkdtemp(prefix="judge_next_")
    try:
        if root is None:                 # else: a package given by the caller (the unpacked release zip)
            subprocess.run([sys.executable, os.path.join(REPO, "tools", "build_dist.py"), "--out", tmp, "--no-zip"],
                           check=True, stdout=subprocess.DEVNULL)
            root = os.path.join(tmp, NAME)
        judge_dir = os.path.join(root, "Judge")
        x, y, z, T, U, R2, R9, P3, P8 = next_release_plan()
        X, Y, Z = (layout.set_dir(s) for s in (x, y, z))
        repo2, old = make_next_release(tmp)
        with open(os.path.join(REPO, "problems", "batch", "problems.json"), encoding="utf-8") as f:
            old_file = {e["dir"]: layout.file_title(e) for e in json.load(f).values()}   # PDF titles before

        def code(s, i):
            return os.path.join(root, *layout.code_path(s, i).split("/"))

        def old_pdf(i):
            return os.path.join(root, *layout.pdf_path(x, i, old_file[f"{X}/{i}"]).split("/"))

        # the student's work before the update: Signal Towers solved (100 in the tracker), other files written
        shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), code(x, T))
        towers_text = read(code(x, T))
        run_code, out, _ = run_judge(["--no-color"], os.path.dirname(code(x, T)))
        check(run_code == 0 and "ACCEPTED" in out and progress_best(root) == 100,
              "before the update: Signal Towers is solved, 100 in the tracker", f"exit {run_code}\n{out}")
        written = {(s["set"], i): f"// my code for {s['set']} problem {i}: {old[s['set'], i]}\nint main() {{ return 0; }}\n"
                   for s, i in ((x, U), (x, R2), (x, P3), (y, 1), (y, 2))}
        for s, i in ((x, U), (x, R2), (x, P3), (y, 1), (y, 2)):
            write(code(s, i), written[s["set"], i])
        own = {os.path.join(root, X, str(T), "notes.txt"): "my notes\n", os.path.join(root, X, "mysol.cpp"): "// scratch\n",
               os.path.join(root, X, str(R2), "backup.cpp"): "// an older try\n",
               os.path.join(root, Y, "old", "keep.cpp"): "// already in old/\n",
               code(y, 7): "// I made this file myself\nint main() {}\n"}
        for path, text in own.items():
            write(path, text)
        shipped2 = sha(old_pdf(R2))
        with open(old_pdf(R9), "ab") as f:
            f.write(b"\n% a note the student saved into this PDF\n")
        changed9 = sha(old_pdf(R9))
        progress = os.path.join(judge_dir, "progress.json")
        progress_before = sha(progress)

        srv, url = serve(repo2)
        towers_dir = os.path.dirname(code(x, T))
        moved_towers = layout.code_path(x, U)
        run_code, out, _ = run_student([TOWERS_CPP, "--no-color", "--stop"], towers_dir, url)
        check(run_code == 0 and "restarting" in out and f"just moved with its problem to {moved_towers}" in out
              and "Result" in out and "ACCEPTED" not in out,
              f"a normal run finds {next_version(build_version())}, installs it, restarts, and says where the code of the file it judges went",
              f"exit {run_code}\n{out}")
        with open(os.path.join(judge_dir, "manifest.json"), encoding="utf-8") as f:
            check(json.load(f).get("version") == next_version(build_version()), "the installed version is the next one")
        with open(os.path.join(judge_dir, "problems", "batch", "problems.json"), encoding="utf-8") as f:
            titles = {e["dir"]: layout.file_title(e) for e in json.load(f).values()}   # the PDF titles after the update

        def new_pdf(s, i):
            return os.path.join(root, *layout.pdf_path(s, i, titles[f"{layout.set_dir(s)}/{i}"]).split("/"))

        # tracker: progress.json is not touched, the 100 stays with Signal Towers (now problem U of its set)
        check(sha(progress) == progress_before, "progress.json is not touched by the update or the moves")
        run_code, out_p, _ = run_judge(["--progress", x["set"], "--no-color", "--ascii"], os.path.join(root, X))
        check(run_code == 0 and towers_solved(out_p, U) and not towers_solved(out_p, T),
              f"the tracker still shows the 100 for the moved problem (now problem {U})", out_p)
        # a re-titled problem: the code stays, the old PDF is retired, the new one appears
        bak2 = os.path.join(judge_dir, ".backup", "_package", *layout.pdf_path(x, R2, old_file[f"{X}/{R2}"]).split("/"))
        check(read(code(x, R2)) == written[x["set"], R2] and not glob.glob(os.path.join(root, X, "old", f"{R2}_*")),
              "re-titled problem: the written file stays in its folder")
        check(os.path.isfile(new_pdf(x, R2)) and "Renamed_Problem_Two" in new_pdf(x, R2) and not os.path.exists(old_pdf(R2))
              and os.path.isfile(bak2) and sha(bak2) == shipped2,
              "re-titled problem: the new PDF appears, the old one is retired to Judge/.backup/_package/")
        check(os.path.isfile(new_pdf(x, R9)) and os.path.isfile(old_pdf(R9)) and sha(old_pdf(R9)) == changed9,
              "an old PDF whose bytes are not the shipped ones stays where it is")
        # a replaced problem: the written file goes to Mock_<set>/old/, the slot gets an empty starter
        parked3 = os.path.join(root, X, "old", layout.old_name(P3, old[x["set"], P3]))
        check(read(parked3) == written[x["set"], P3] and read(code(x, P3)) == "",
              f"replaced problem: the written file goes to {X}/old/{layout.old_name(P3, old[x['set'], P3])}, the slot is empty again",
              f"{os.listdir(os.path.join(root, X, 'old')) if os.path.isdir(os.path.join(root, X, 'old')) else None}")
        check(read(code(x, P8)) == "" and not glob.glob(os.path.join(root, X, "old", f"{P8}_*")),
              "replaced problem with an untouched empty starter: nothing is moved")
        folder8 = sorted(os.listdir(os.path.join(root, X, str(P8))))
        check(folder8 == sorted([layout.code_name(x, P8), f"{P8}_Brand_New_Eight.pdf"]),
              "a replaced problem's folder holds the new PDF only (the old shipped one is retired)", str(folder8))
        # moved problems follow their titles
        check(read(code(x, T)) == written[x["set"], U] and read(code(x, U)) == towers_text,
              f"problems swapped inside a set ({T} <-> {U}): each written file follows its problem")
        check(read(code(z, 1)) == written[y["set"], 1] and read(code(y, 1)) == "",
              f"a problem moved to another set ({Y}/1 -> {Z}/1): the written file follows, the old slot is empty again")
        # a clash: the destination already holds written code
        parked = os.path.join(root, Y, "old", f"{y['set']}-2_moved.cpp")
        check(read(code(y, 7)) == own[code(y, 7)] and read(parked) == written[y["set"], 2] and read(code(y, 2)) == ""
              and "already held your code" in out,
              f"clash ({Y}/2 -> {Y}/7, where the student has code): nothing overwritten, the incoming file goes to old/, reported",
              out)
        check(all(read(path) == text for path, text in own.items()),
              "files the updater did not ship (notes, extra .cpp files, a file already in old/) are untouched")
        lines = [ln for ln in out.splitlines() if " -> " in ln]
        check(len(lines) == 5 and "moved with their problems" in out, "every move is printed once", "\n".join(lines))
        folder7 = sorted(os.listdir(os.path.join(root, Y, "7")))
        check(folder7 == sorted([layout.code_name(dict(y, problems=[0] * 7), 7), os.path.basename(new_pdf(dict(y, problems=[0] * 7), 7))]),
              "a new problem folder (7) holds exactly its code file and its PDF", str(folder7))
        # the second run is quiet and changes nothing
        snap = outside_judge(root)
        run_code, out2, _ = run_student(["--no-color"], os.path.dirname(code(x, U)), url)
        check(run_code == 0 and "ACCEPTED" in out2 and "moved" not in out2 and "restarting" not in out2
              and outside_judge(root) == snap, "the second run is quiet, changes nothing, and judges the moved file", out2)
        run_code, out3, _ = run_student(["--update", "--no-color"], os.path.join(root, X), url)
        check(run_code == 0 and "up to date" in out3 and outside_judge(root) == snap, "--update afterwards: up to date",
              out3)
        srv.shutdown()
        with open(os.path.join(REPO, "manifest.json"), encoding="utf-8") as f:
            real = json.load(f)
        check(set(real) == {"version", "sources", "files", "managed", "create_only", "bundles", "moves"},
              "the manifest is one plain view (no legacy or bootstrap view)", str(sorted(real)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    global judge
    if not shutil.which("g++"):
        print("g++ not found: the regression tests need a C++ compiler in PATH.")
        return 1
    tmp = tempfile.mkdtemp(prefix="judge_dist_")
    try:
        root = build_package(tmp)
        if root:
            PACKAGE[0] = root
            sys.path.insert(0, os.path.join(root, "Judge"))
            sys.dont_write_bytecode = True
            import judge as package_judge
            judge = package_judge
            test_package(root)
            test_layout(root)
            test_judging(root, tmp)
            test_crlf_generator()
            test_samples()
            test_stale_tests()
            test_scoring()
            test_exited_peak()
            test_missed_last_reading()
            test_cli(root, tmp)
            test_tracks(root)
            test_reports()
            test_updater()
            test_versions()
            test_fast_update()
            test_future_update()
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
