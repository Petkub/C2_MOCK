"""
Regression cases of the reports to the teacher (core/report.py, plans/GRADER_DESIGN.md section 8), run by
tests/run_regression.py. The same file is in C2_PRACTICE and C2_MOCK; each passes its own package and sample problem.
Everything runs against tools/fake_report_server.py on this computer (it answers through a 302 like Apps Script):
never Google, never the student's real login file (STUPIDGRADER_HOME points into the test folder).
"""
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
from fake_report_server import FakeServer  # noqa: E402

GOOD = "petkub-AB2C"
OTHER = "mona-XY23"
SHARED = ("core/report.py", "tools/fake_report_server.py", "tests/report_tests.py")


def closed_url():
    """A local address where nothing listens (no internet / Web App switched off)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}/exec"


class Case:
    def __init__(self, check, root, problem_dir, code_name, pid, ok_src, pkg):
        self.check, self.root, self.pkg, self.pid = check, root, pkg, pid
        self.pdir = os.path.join(root, *problem_dir.split("/"))
        self.code = os.path.join(self.pdir, code_name)
        self.rel = problem_dir + "/" + code_name
        self.ok_src = ok_src
        self.home = os.path.join(os.path.dirname(root), "home")
        self.judge_dir = os.path.join(root, "Judge")
        self.srv = FakeServer({GOOD: {"name": "Petkub"}, OTHER: {"name": "Mona"}})
        self.outputs = []           # everything the judge printed in these cases (English only)
        self.url = self.srv.start()

    def judge(self, args=(), url=None, inp=None, interactive=False, cwd=None, root=None):
        """Run the package's judge in the problem folder. Returns (exit code, output, seconds)."""
        env = dict(os.environ, JUDGE_NO_UPDATE="1", STUPIDGRADER_HOME=self.home,
                   JUDGE_REPORT_URL=url or self.url)
        env.pop("JUDGE_REPORT_INTERACTIVE", None)
        if interactive:
            env["JUDGE_REPORT_INTERACTIVE"] = "1"
        judge = os.path.join(root or self.root, "Judge", "judge.py")
        t0 = time.time()
        p = subprocess.run([sys.executable, judge] + list(args) + ["--no-color"], cwd=cwd or self.pdir, env=env,
                           input=(inp or "").encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=300)
        out = p.stdout.decode("utf-8", "replace")
        self.outputs.append(out)
        return p.returncode, out, time.time() - t0

    def login_file(self):
        try:
            with open(os.path.join(self.home, "student.json"), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def outbox(self, judge_dir=None):
        p = os.path.join(judge_dir or self.judge_dir, ".outbox.jsonl")
        if not os.path.exists(p):
            return []
        with open(p, encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]

    def write(self, path, text):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def read(self, path):
        with open(path, encoding="utf-8", newline="") as f:
            return f.read()

    def reset_login(self):
        p = os.path.join(self.home, "student.json")
        if os.path.exists(p):
            os.remove(p)


def run(check, root, problem_dir, code_name, pid, ok_src, pkg, sibling=None):
    """root: a built package only these tests use; problem_dir/code_name: the code file of problem pid in it, which
    ok_src solves; sibling: the other package's repo (the shared files must be the same)."""
    print("Reports to the teacher (report.py, fake Apps Script on this computer)")
    c = Case(check, root, problem_dir, code_name, pid, ok_src, pkg)
    try:
        shutil.copy(ok_src, c.code)
        same_in_both(c, sibling)
        first_login(c)
        shared_login(c)
        switches(c)
        outbox(c)
        pull(c)
        backup_restore(c)
        speed(c)
        never_breaks(c)
        english(c)
    finally:
        c.srv.stop()


def same_in_both(c, sibling):
    if not sibling or not os.path.isdir(sibling):
        return
    for rel in SHARED:
        a, b = os.path.join(REPO, rel), os.path.join(sibling, rel)
        if os.path.exists(b):
            with open(a, "rb") as fa, open(b, "rb") as fb:
                c.check(fa.read() == fb.read(), f"{rel} is the same file in both packages ({os.path.basename(sibling)})")


def first_login(c):
    code, out, _ = c.judge()
    c.check(code == 0 and "ACCEPTED" in out and "Not logged in" in out and c.login_file() is None and not c.srv.requests,
            "first run in a terminal that cannot type: judged, a one-line hint, nothing asked, nothing sent", out[-600:])
    code, out, _ = c.judge(interactive=True, inp="\n")
    c.check(code == 0 and "ACCEPTED" in out and "Skipped" in out and (c.login_file() or {}).get("skipped") is True,
            "first run, Enter: skipped and judged", out[:900])
    code, out, _ = c.judge(interactive=True)
    c.check("Student code from your teacher" not in out and "Not logged in" in out,
            "after a skip the judge does not ask again (one-line hint)", out[:600])
    c.reset_login()
    code, out, _ = c.judge(interactive=True, inp="petkub-ZZZZ\nnot a code\npetkub-QQQQ\n")
    c.check(code == 0 and "ACCEPTED" in out and out.count("not valid") == 2 and "looks like" in out
            and (c.login_file() or {}).get("code") == "" and (c.login_file() or {}).get("skipped") is True,
            "three wrong codes: skipped for now with the --login hint, then judged", out[:1200])
    c.reset_login()
    code, out, _ = c.judge(interactive=True, inp=f"{OTHER[:-4]}WXYZ\ny\ny\n", url=closed_url())
    lf = c.login_file() or {}
    c.check(code == 0 and "No connection" in out and lf.get("code") == f"{OTHER[:-4]}WXYZ" and not lf.get("verified_at")
            and len(c.outbox()) == 1, "no internet at login: the code is kept unchecked, the result waits in the outbox",
            out[:1200])
    code, out, _ = c.judge()
    lf = c.login_file() or {}
    c.check("not accepted any more" in out and lf.get("code") == "" and lf.get("skipped") is False,
            "an unchecked code the server refuses is cleared (asked again next time)", out[-600:])
    c.write(os.path.join(c.judge_dir, ".outbox.jsonl"), "")
    n = len(c.srv.raw)
    code, out, _ = c.judge(interactive=True, inp=f"{GOOD}\ny\ny\n")
    lf = c.login_file() or {}
    c.check(code == 0 and "Hello Petkub" in out and "ACCEPTED" in out and lf.get("code") == GOOD and lf.get("verified_at")
            and lf.get("report") is True and lf.get("sync") is True, "right code + two yes: logged in, checked", out[:1200])
    ev = c.srv.raw[-1] if len(c.srv.raw) > n else {}
    c.check(ev.get("student") == GOOD and ev.get("pkg") == c.pkg and ev.get("slot_path") == c.rel and ev.get("score") == 100
            and set(ev.get("verdicts", "")) == {"A"} and ev.get("attempt", 0) >= 1 and not c.outbox(),
            "the event reaches the server through the 302 (problem, slot_path, score, verdicts, attempt)", str(ev))
    with open(c.code, "rb") as f:
        mine = f.read()
    kept = c.srv.drive.get(GOOD, {}).get(c.pkg, {})
    c.check(any(v["versions"][0].get("code", "").encode("utf-8") == mine for v in kept.values()),
            "sync on: the code is attached and kept")
    p = os.path.join(c.home, "student.json")
    c.check(os.name == "nt" or (os.stat(p).st_mode & 0o077) == 0, "the login file can be read by its owner only")


def shared_login(c):
    other = os.path.join(os.path.dirname(c.root), "second", os.path.basename(c.root))
    shutil.copytree(c.root, other, ignore=shutil.ignore_patterns(".outbox.jsonl", "*.zip"))
    n = len(c.srv.raw)
    code, out, _ = c.judge(interactive=True, cwd=c.pdir.replace(c.root, other), root=other)
    c.check(code == 0 and "Student code" not in out and len(c.srv.raw) == n + 1 and c.srv.raw[-1]["student"] == GOOD,
            "another package on the same computer uses the shared login (no question)", out[-400:])
    c.write(os.path.join(other, "Judge", ".student"), OTHER + "\n")
    code, out, _ = c.judge(cwd=c.pdir.replace(c.root, other), root=other)
    c.check(c.srv.raw[-1]["student"] == OTHER, "Judge/.student overrides the shared login (this package only)",
            str(c.srv.raw[-1].get("student")))
    code, out, _ = c.judge(["--report", "status"], cwd=c.pdir.replace(c.root, other), root=other)
    c.check(code == 0 and ".student" in out and OTHER in out, "--report status names the login file in use", out)
    code, out, _ = c.judge(["--report", "status"])
    c.check(code == 0 and GOOD in out and "student.json" in out and "Waiting   0" in out,
            "--report status: student, login file, server, waiting results", out)
    shutil.rmtree(os.path.dirname(other), ignore_errors=True)


def switches(c):
    code, out, _ = c.judge(["--sync", "off"])
    n, req = len(c.srv.raw), len(c.srv.requests)
    c.judge()
    ev = c.srv.raw[-1]
    c.check(code == 0 and len(c.srv.raw) == n + 1 and "code" not in ev and (c.login_file() or {}).get("sync") is False,
            "--sync off: the score is sent without the code")
    sent = [r for r in c.srv.requests[req:] if r[0] == "event"]
    c.check(sent == [("event", 1)], "one POST per judged solution", str(sent))
    c.judge(["--report", "off"])
    req = len(c.srv.requests)
    code, out, _ = c.judge()
    c.check(code == 0 and "ACCEPTED" in out and len(c.srv.requests) == req and not c.outbox() and "Not logged in" not in out,
            "--report off: nothing is sent or queued, no hint", out[-300:])
    c.judge(["--report", "on"])
    c.judge(["--sync", "on"])
    req = len(c.srv.requests)
    c.judge(["--stop"])
    c.check(len(c.srv.requests) == req, "--stop (tests skipped): not reported")
    c.check((c.login_file() or {}).get("sync") is True and (c.login_file() or {}).get("report") is True, "--report on, --sync on")
    req = len(c.srv.requests)
    code, out, _ = c.judge(cwd=os.path.dirname(c.pdir))       # the whole set / topic
    ev = [r for r in c.srv.requests[req:] if r[0] == "event"]
    c.check(code == 0 and "Total" in out and len(ev) == 1, "judging a whole set: its events go in one POST", str(ev))


def outbox(c):
    down = closed_url()
    code, out, _ = c.judge(url=down)
    code2, out2, _ = c.judge(url=down)
    c.check(code == code2 == 0 and "ACCEPTED" in out2 and "2 results waiting" in out2 and len(c.outbox()) == 2,
            "no internet: judged as usual, '2 results waiting' and both kept in the outbox", out2[-400:])
    saved = c.read(os.path.join(c.judge_dir, ".outbox.jsonl"))
    n = len(c.srv.raw)
    code, out, _ = c.judge()
    c.check(len(c.srv.raw) == n + 3 and not c.outbox() and "waiting" not in out,
            "back online: every waiting event is sent (not only the last), the outbox is emptied", out[-300:])
    c.write(os.path.join(c.judge_dir, ".outbox.jsonl"), saved)       # an answer that was lost on the way back
    code, out, _ = c.judge()
    c.check(len(c.srv.raw) == n + 4 and not c.outbox(), "events sent twice are stored once (event_id)")
    c.check(not c.srv.direct and c.srv.requests and not c.srv.answers,
            "every answer was read after following the 302 redirect (like script.googleusercontent.com)")


def pull(c):
    data = "// the copy kept by the teacher\nint main() { return 0; }\n"
    c.srv.drive[GOOD] = {c.pkg: {"X": {"pid": c.pid, "slot_path": "old/place.cpp",
                                       "versions": [{"sha": "x", "time": "2099-01-01T00:00:00+07:00", "score": 100,
                                                     "code": data}]}}}
    mine = c.read(c.code)
    c.write(c.code, "")
    code, out, _ = c.judge(["--pull"])
    c.check(code == 0 and c.read(c.code) == data and "wrote 1" in out,
            "--pull: an empty code file gets the teacher's copy (at this version's place, by pid)", out)
    code, out, _ = c.judge(["--pull"])
    c.check("already the same 1" in out and c.read(c.code) == data, "--pull again: the same code is skipped", out)
    c.write(c.code, mine)
    code, out, _ = c.judge(["--pull"])
    old = os.path.join(os.path.dirname(c.pdir), "old")
    kept = os.listdir(old) if os.path.isdir(old) else []
    c.check(c.read(c.code) == mine and len(kept) == 1 and "_cloud_" in kept[0] and c.read(os.path.join(old, kept[0])) == data,
            "--pull over written code: never overwritten, the teacher's copy goes to old/<slot>_cloud_<date>.cpp", out)
    code, out, _ = c.judge(["--pull"])
    c.check(len(os.listdir(old)) == 1 and "already the same 1" in out, "--pull again: the copy in old/ is not repeated")
    shutil.rmtree(old)
    c.srv.drive.pop(GOOD, None)


def backup_restore(c):
    mine = c.read(c.code)
    code, out, _ = c.judge(["--backup"])
    zips = [f for f in os.listdir(c.root) if f.endswith(".zip")]
    names = zipfile.ZipFile(os.path.join(c.root, zips[0])).namelist() if zips else []
    c.check(code == 0 and len(zips) == 1 and c.rel in names and "backup.json" in names and "Judge/progress.json" in names,
            "--backup: a zip next to Judge/ with the code files and progress.json", out + str(names))
    c.write(c.code, "")
    code, out, _ = c.judge(["--restore", os.path.join(c.root, zips[0])])
    c.check(code == 0 and c.read(c.code) == mine and "wrote 1" in out, "--restore: an empty code file gets its code back", out)
    c.write(c.code, mine + "// changed after the backup\n")
    code, out, _ = c.judge(["--restore", os.path.join(c.root, zips[0])])
    old = os.path.join(os.path.dirname(c.pdir), "old")
    kept = os.listdir(old) if os.path.isdir(old) else []
    c.check(c.read(c.code).endswith("// changed after the backup\n") and len(kept) == 1 and "_backup_" in kept[0],
            "--restore over newer code: never overwritten, the backup's copy goes to old/", out)
    shutil.rmtree(old, ignore_errors=True)
    c.write(c.code, mine)
    os.remove(os.path.join(c.root, zips[0]))


def speed(c):
    def best_of(url, n=2):
        return min(c.judge(url=url)[2] for _ in range(n))
    base = best_of("off")
    down = best_of(closed_url())
    c.srv.delay = 30                         # Google never answers
    hang = best_of(c.url, 1)
    c.srv.delay = 0
    # Windows waits about 2 s before it reports a refused connection to a closed local port (no internet at all
    # fails at once): still within the 3 s the judge waits after the result
    c.check(down - base < (1.0 if os.name != "nt" else 3.5),
            f"no internet: judging is not slower ({base:.2f} s -> {down:.2f} s)")
    c.check(hang - base < 3.0 + 1.0, f"a server that never answers: at most 3 s more, after the result ({base:.2f} s -> {hang:.2f} s)")
    c.judge()                                # send what the slow runs left


def never_breaks(c):
    p = os.path.join(c.home, "student.json")
    good = c.read(p)
    c.write(p, "{ not json")
    code, out, _ = c.judge()
    c.check(code == 0 and "ACCEPTED" in out and "Traceback" not in out, "a broken login file never breaks judging", out[-300:])
    c.write(p, good)
    src = os.path.join(c.judge_dir, "report.py")
    os.rename(src, src + ".off")
    try:
        code, out, _ = c.judge()
        c.check(code == 0 and "ACCEPTED" in out and "Traceback" not in out, "without report.py the judge works as before")
        code, out, _ = c.judge(["--report", "status"])
        c.check(code == 1 and "report.py is missing" in out, "--report without report.py: a clear message", out)
    finally:
        os.rename(src + ".off", src)
    spec = importlib.util.spec_from_file_location("repo_judge", os.path.join(REPO, "core", "judge.py"))
    repo_judge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(repo_judge)
    c.check(not repo_judge.report_ready() and not os.path.exists(os.path.join(REPO, "core", "manifest.json")),
            "the repo's core/judge.py (not an installed package: no Judge/manifest.json) never reports")


THAI = re.compile("[\u0e00-\u0e7f]")
SAMPLE_NAMES = re.compile(r"mona|k7q3", re.IGNORECASE)


def english(c):
    """Everything a student reads about reports is English, and help text shows <name>-XXXX, never a sample name."""
    thai = [o for o in c.outputs if THAI.search(o)]
    c.check(not thai, f"every line the judge printed in these {len(c.outputs)} runs is English (no Thai)",
            thai[0][:300] if thai else "")
    code, out, _ = c.judge(["--help"])
    c.check("--login [CODE]" in out and "<name>-XXXX" in out and not SAMPLE_NAMES.search(out) and not THAI.search(out),
            "--help: English, the placeholder <name>-XXXX, no sample name", out)
    c.reset_login()
    code, out, _ = c.judge(interactive=True, inp="\n")
    c.check("<name>-XXXX" in out and not SAMPLE_NAMES.search(out), "the first-run prompt shows <name>-XXXX", out[:600])
    code, out, _ = c.judge(["--login"])
    c.check(code == 2 and "--login <name>-XXXX" in out, "--login without a code (no terminal): the placeholder", out)
    code, out, _ = c.judge(["--login", GOOD.lower()], interactive=True, inp="y\ny\n")
    n = len(c.srv.raw)
    c.judge()
    c.check(code == 0 and len(c.srv.raw) == n + 1 and c.srv.raw[-1]["student"] == GOOD,
            "a code typed in other letter case works (codes ignore case)", out[:400])
    with open(os.path.join(c.root, "README.txt"), encoding="utf-8") as f:
        readme = f.read()
    start = readme.find("Reports to your teacher (Discord) and code copies")
    end = readme.find("\n\n", start)
    section = readme[start:end] if start >= 0 else ""
    c.check(section and not THAI.search(section) and "--login <name>-XXXX" in section and not SAMPLE_NAMES.search(readme),
            "README.txt: the report section is English with <name>-XXXX; no sample name anywhere",
            section[:300] or "section not found")
    with open(os.path.join(c.judge_dir, "report.py"), encoding="utf-8") as f:
        c.check(not SAMPLE_NAMES.search(f.read()), "report.py has no sample student name")
