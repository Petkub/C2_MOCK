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
"""
import contextlib
import glob
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
judge = None        # the package's judge.py, imported by main()


def check(ok, name, detail=""):
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
        exe, _, _ = judge.compile_source(src, tmp)
        if not exe:
            return "CE", 0
        with contextlib.redirect_stdout(io.StringIO()):
            if not judge.ensure_tests(pdir, st):
                return "could not rebuild the big tests", 0
            results, _, total = judge.run_tests(exe, pdir, st, 1.0, 0, not full, quiet=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [v for _, v, _ in results if v != "AC"]
    return (bad[0] if bad else "AC"), judge.compute_score(results, total)[0]


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
            test_samples()
            test_cli(root)
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
