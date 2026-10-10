#!/usr/bin/env python3
"""
Regression tests for the POSN Camp 2 Practice Judge.

  python3 tests/run_regression.py          run everything (exit code 0 = all passed)

Everything runs inside a student package built with tools/build_dist.py in a temporary folder, so the big tests
that gen.py rebuilds and progress.json are never written into the repo.
1. The package ships no rebuilt tests and no progress.json; Mock_K/1.cpp ... 5.cpp are untouched starters.
2. Every sample in samples/expected.json is judged and must get its verdict (and score, when given; that run
   also rebuilds the problem's big tests with gen.py and checks them).
   Verdict = CE if it does not compile, else the first non-AC verdict, else AC.
3. The judge's command line is run like a student would (inside Mock_1, --ascii, --list, --progress).
4. Self-update: a local HTTP server serves a modified copy of the repo as v9.9; a package must update itself
   (hashes, backups, restart, create-only set files), and must refuse bad hashes, bad paths and no network.
5. manifest.json is up to date.
"""
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
    check(len(starters) == 20 and all(judge.is_untouched_starter(s) for s in starters),
          "Mock_K/1.cpp ... 5.cpp are untouched starters", f"{len(starters)} files")


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


# ----------------------------------------------------------------------------- 3. command line
def run_judge(args, cwd):
    """Run ../Judge/judge.py like a student inside a Mock_K folder. Returns (exit code, output, output is ASCII)."""
    p = subprocess.run([sys.executable, os.path.join(os.pardir, "Judge", "judge.py")] + args, cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stdout.isascii()


def test_cli(root):
    print("Command line")
    set1 = os.path.join(root, "Mock_1")
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), os.path.join(set1, "1.cpp"))
    shutil.copy(os.path.join(SAMPLES, "batch", "towers_smallhi.cpp"), os.path.join(set1, "wrong.cpp"))
    code, out, _ = run_judge(["1.cpp", "--no-color"], set1)
    check(code == 0 and "ACCEPTED" in out, "inside Mock_1: judge.py 1.cpp", f"exit {code}\n{out}")
    progress = os.path.join(root, "Judge", "progress.json")
    try:
        with open(progress, encoding="utf-8") as f:
            best = json.load(f)["problems"]["1"]["best"]
    except (OSError, ValueError, KeyError):
        best = None
    check(best == 100, "progress.json records best 100 for problem 1", f"best = {best}")
    for name in ("towers_throw.cpp", "towers_warn.cpp"):
        shutil.copy(os.path.join(SAMPLES, "batch", name), os.path.join(set1, name))
    code, out, _ = run_judge(["towers_throw.cpp", "1-1", "--no-color", "--stop"], set1)
    check("out_of_range" in out and "stderr" in out, "RE shows the program's stderr (out_of_range)", out)
    code, out, _ = run_judge(["towers_warn.cpp", "1-1", "--no-color", "--stop"], set1)
    check("g++ warning" in out and "unused" in out, "warnings are shown after Compiled", out)
    code, out, _ = run_judge(["1.cpp", "--no-color", "--stop"], set1)
    check("warning" not in out and "Memory  peak" in out and "256 MB per test" in out,
          "clean program: no warnings, memory line, limit in header", out)
    code, out, _ = run_judge(["1.cpp", "--no-color", "--stop", "--ml", "1"], set1)
    check("Memory Limit Exceeded" in out and "limit is 1 MB" in out, "--ml 1 makes a small program MLE", out)
    code, out, _ = run_judge(["--ml", "0"], set1)
    check(code == 2 and "--ml must be" in out, "judge.py --ml 0 is rejected", f"exit {code}\n{out}")
    code, out, plain = run_judge(["wrong.cpp", "1-1", "--ascii", "--no-color"], set1)
    check(code == 0 and "First failure" in out and plain, "judge.py --ascii shows the failure, ASCII only",
          f"exit {code}, ascii={plain}\n{out}")
    code, out, _ = run_judge(["--no-color"], set1)
    check(code == 0 and "Total" in out and "Problem 5" in out, "inside Mock_1: judge.py (whole set)",
          f"exit {code}\n{out}")
    code, out, plain = run_judge(["--progress", "--ascii"], set1)
    check(code == 0 and plain, "judge.py --progress --ascii", f"exit {code}, ascii={plain}\n{out}")
    code, out, plain = run_judge(["--list", "--ascii"], set1)
    check(code == 0 and "Set 4" in out and plain, "judge.py --list --ascii", f"exit {code}\n{out}")
    code, out, _ = run_judge(["--tl", "abc"], set1)
    check(code == 2 and "--tl must be" in out, "judge.py --tl abc is rejected", f"exit {code}\n{out}")


# ----------------------------------------------------------------------------- 4. self-update
def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def serve(folder):
    """Serve folder over HTTP on a free port of this computer (stands in for raw.githubusercontent.com)."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=folder)
    handler.log_message = lambda *a: None
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
        judge_dir, set1 = os.path.join(root, "Judge"), os.path.join(root, "Mock_1")
        shutil.copy(os.path.join(SAMPLES, "batch", "towers_ok.cpp"), os.path.join(set1, "1.cpp"))
        student_hash, old_judge = sha(os.path.join(set1, "1.cpp")), sha(os.path.join(judge_dir, "judge.py"))
        template = sha(os.path.join(set1, "2.cpp"))

        # a) automatic update during a normal run: new files, backup, restart with the new judge
        repo2 = make_repo2(tmp, "9.9", "marker-v9.9")
        edit_manifest(repo2, lambda m: m["create_only"].update(
            {"Mock_1/6.cpp": [sha(os.path.join(REPO, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]}))
        srv, url = serve(repo2)
        code, out, _ = run_student(["1.cpp", "--no-color"], set1, url)
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
              and os.path.exists(os.path.join(judge_dir, ".backup", "_package", "Mock_1", "Makefile")),
              "managed files README.txt and Mock_1/Makefile replaced, old copies in Judge/.backup/_package/")
        check(sha(os.path.join(set1, "1.cpp")) == student_hash and sha(os.path.join(set1, "2.cpp")) == template,
              "student files untouched")
        check(os.path.exists(os.path.join(set1, "6.cpp")) and sha(os.path.join(set1, "6.cpp")) == template,
              "create-only Mock_1/6.cpp added")
        check(not os.path.exists(os.path.join(judge_dir, ".update_tmp")), "no temp folder left behind")
        progress = os.path.join(judge_dir, "progress.json")
        with open(progress, encoding="utf-8") as f:
            best = json.load(f)["problems"].get("1", {}).get("best")
        check(best == 100 and not os.path.exists(os.path.join(judge_dir, ".backup", "progress.json")),
              "progress.json kept (best 100) and not backed up", f"best = {best}")
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 0 and "up to date" in out, "--update: up to date", f"exit {code}\n{out}")

        # b) a newer version appears: normal runs wait 10 minutes, --update takes it now
        repo2 = make_repo2(tmp, "9.11", "marker-v9.11")
        code, out, _ = run_student(["1.cpp", "--no-color"], set1, url)
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
            {"Mock_1/1.cpp": [sha(os.path.join(repo2, "student", "set_files", "template.cpp")), "student/set_files/template.cpp"]})
            or m.update(version="9.14"))
        code, out, _ = run_student(["--update", "--no-color"], set1, url)
        check(code == 1 and "bad managed entry" in out and sha(os.path.join(set1, "1.cpp")) == student_hash,
              "a .cpp listed as managed: refused, student file untouched", f"exit {code}\n{out}")

        # e) recovery: a damaged file is re-downloaded by python Judge/updater.py
        rebuild_manifest(repo2)
        os.remove(os.path.join(judge_dir, "README.txt"))
        env = dict(os.environ, JUDGE_UPDATE_URL=url)
        p = subprocess.run([sys.executable, os.path.join(judge_dir, "updater.py")], env=env, cwd=set1,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        check(p.returncode == 0 and os.path.exists(os.path.join(judge_dir, "README.txt")),
              "python Judge/updater.py restores a missing file", f"exit {p.returncode}\n{out}")
        srv.shutdown()

        # f) no network: the judge works as usual, quickly
        os.remove(os.path.join(judge_dir, ".update_check"))
        code, out, dt = run_student(["1.cpp", "--no-color"], set1, f"http://127.0.0.1:{free_port()}/")
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
            test_cli(root)
            test_updater()
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
