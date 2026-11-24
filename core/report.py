#!/usr/bin/env python3
"""
Reports to the teacher and copies of the student's code (C2_PRACTICE_SRC/plans/GRADER_DESIGN.md).
The same file ships in C2_Practice and C2_Mock (the regression tests compare the two); judge.py gives it a Package
that describes its problems. Python 3.7+ standard library only.

What it does
  - Login once per computer: the student code from the teacher (<name>-XXXX) and two separate consents (send scores;
    keep a copy of the code with the teacher). The login file is shared by both packages:
      ~/.config/stupidgrader/student.json        (Windows: %APPDATA%\\stupidgrader\\student.json)
      Judge/.student                              (optional: used instead, for this package only)
  - After every judged solution one event (problem, score, verdicts, time; the code only when sync is on, at most
    64 KB) goes to Judge/.outbox.jsonl; every waiting event is POSTed to the teacher's Apps Script Web App (it answers
    through a 302 redirect, followed here). The judge waits at most 3 s, after the result is shown; what is not sent
    stays in the outbox for the next run. The server ignores events it already has (event_id).
  - --pull copies the code kept by the teacher into this package, --backup / --restore do the same with a zip and
    no internet. Neither ever overwrites written code: a different version goes to <set folder>/old/.

Nothing here may break or slow down judging: every entry point used by judge.py catches its own errors.
Endpoint: Judge/config.json "endpoint"; JUDGE_REPORT_URL overrides it ("off" = no reports; http://127.0.0.1:PORT/
for tests). STUPIDGRADER_HOME overrides the folder of the shared login file (tests).
"""
import base64
import datetime
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.request
import uuid
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SEND_WAIT = 3.0                     # seconds the judge waits for the report after the result (then: outbox)
HELLO_WAIT = 8.0                    # checking a code at login (the student is waiting for it anyway)
PULL_WAIT = 60.0                    # --pull
MAX_CODE = 64 * 1024                # bytes of code attached to one event (bigger: the hash only)
MAX_REPLY = 32 * 1024 * 1024        # bytes read from the server
BATCH_EVENTS = 25                   # events per POST
BATCH_BYTES = 1024 * 1024           # about this many bytes per POST
OUTBOX_MAX = 1000                   # events kept while offline (the oldest are dropped)
OUTBOX_CODE = 8 * 1024 * 1024       # bytes of attached code kept in the outbox (older events keep the hash only)
LOGIN_TRIES = 3
CODE_RE = re.compile(r"^[A-Za-z0-9_.]{1,32}-[A-Za-z0-9]{4}$")       # <name>-XXXX (compared ignoring case)
PLACEHOLDER = "<name>-XXXX"
LOGIN_NAME = "student.json"
LOCAL_LOGIN = ".student"
OUTBOX = ".outbox.jsonl"
STATE = ".report_state.json"
CONFIG = "config.json"
PROGRESS = "progress.json"
VERDICT_LETTER = {"AC": "A", "WA": "W", "TLE": "T", "RE": "R", "MLE": "M"}


class Package:
    """What report.py needs to know about the package that imports it.
    name: "practice" or "mock"; problems: {pid: {"problem": "09-08", "slot_path": "09_DP_I_Foundations/08/09-08.cpp",
    "title": ..., "set": "09", "set_kind": "topic" | "mixed" | "mock", "set_pids": [...]}};
    is_starter(path): True for a code file nobody has written in yet; command: how to run the judge (for hints)."""

    def __init__(self, name, version, judge_dir, problems, is_starter, command="python3 judge.py", title=""):
        self.name = name
        self.version = version
        self.judge_dir = judge_dir
        self.root = os.path.dirname(judge_dir)
        self.problems = problems
        self.is_starter = is_starter
        self.command = command
        self.title = title or name


# ----------------------------------------------------------------------------- small helpers
def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path, limit=None):
    try:
        with open(path, "rb") as f:
            return f.read() if limit is None else f.read(limit)
    except OSError:
        return None


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_bytes(path, data):
    """Write a whole file at once (temp file + rename), creating its folder."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp" + uuid.uuid4().hex[:6]
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def write_json(path, data, private=False):
    write_bytes(path, json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8"))
    if private and os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def say(st, text, color=None):
    paint = getattr(st, color) if color else (lambda s: s)
    print("  " + paint(text), flush=True)


def note(st, text):
    say(st, text, "dim")


def same_code(a, b):
    """Student codes are compared ignoring case (petkub-ULTf = petkub-ultf)."""
    return bool(a) and bool(b) and str(a).lower() == str(b).lower()


# ----------------------------------------------------------------------------- settings
def endpoint(pkg):
    """The Web App URL, or None when reports are not set up (no endpoint yet, or JUDGE_REPORT_URL=off)."""
    url = os.environ.get("JUDGE_REPORT_URL")
    if url is None:
        cfg = load_json(os.path.join(pkg.judge_dir, CONFIG), {})
        url = cfg.get("endpoint", "") if isinstance(cfg, dict) else ""
    url = (url or "").strip()
    if url.lower() in ("", "off", "none", "0"):
        return None
    if url.startswith("https://") or url.startswith("http://127.0.0.1:") or url.startswith("http://localhost:"):
        return url
    return None


def shared_dir():
    d = os.environ.get("STUPIDGRADER_HOME")
    if d:
        return d
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "stupidgrader")


def login_path(pkg):
    """Judge/.student when it exists (this package only), else the login file shared by both packages."""
    local = os.path.join(pkg.judge_dir, LOCAL_LOGIN)
    return local if os.path.isfile(local) else os.path.join(shared_dir(), LOGIN_NAME)


def load_login(pkg):
    """{code, name, verified_at, report, sync, skipped}; Judge/.student may also hold just the code."""
    data = {"code": "", "name": "", "verified_at": "", "report": True, "sync": False, "skipped": False}
    path = login_path(pkg)
    raw = read_bytes(path, 64 * 1024)
    if raw is None:
        return data, False
    try:
        got = json.loads(raw.decode("utf-8-sig"))
    except ValueError:
        got = {"code": raw.decode("utf-8", "replace").strip().split("\n")[0].strip()}
    if isinstance(got, dict):
        for k in data:
            if k in got and isinstance(got[k], type(data[k])):
                data[k] = got[k]
    data["code"] = data["code"].strip()
    if not CODE_RE.match(data["code"]):          # a damaged file: not logged in (asked again)
        data["code"] = ""
    return data, True


def save_login(pkg, data):
    write_json(login_path(pkg), data, private=True)


def load_state(pkg):
    s = load_json(os.path.join(pkg.judge_dir, STATE), {})
    return s if isinstance(s, dict) else {}


def save_state(pkg, **kw):
    try:
        s = load_state(pkg)
        s.update(kw)
        write_json(os.path.join(pkg.judge_dir, STATE), s)
    except OSError:
        pass


# ----------------------------------------------------------------------------- network
def post(url, payload, wait):
    """POST payload as JSON and return the JSON answer (a dict), or None. Apps Script answers a POST with a 302 to
    script.googleusercontent.com, which urllib follows as a GET (the answer is there)."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8", "User-Agent": "posn-judge-report"})
    try:
        with urllib.request.urlopen(req, timeout=wait) as r:
            body = r.read(MAX_REPLY + 1)
        ans = json.loads(body.decode("utf-8"))
        return ans if isinstance(ans, dict) else None
    except Exception:
        return None


def post_within(url, payload, wait):
    """post() that returns after `wait` seconds at the latest (None then): connect, redirect and read included."""
    box = []
    t = threading.Thread(target=lambda: box.append(post(url, payload, wait)), daemon=True)
    t.start()
    t.join(wait)
    return box[0] if box else None


# ----------------------------------------------------------------------------- outbox
class OutboxLock:
    """A lock file next to the outbox, so two judges running at once do not lose events. Fails open."""

    def __init__(self, pkg):
        self.path = os.path.join(pkg.judge_dir, OUTBOX + ".lock")
        self.fd = None

    def __enter__(self):
        end = time.time() + 1.0
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > 60:      # left by a killed run
                        os.remove(self.path)
                        continue
                except OSError:
                    pass
                if time.time() > end:
                    return self
                time.sleep(0.02)
            except OSError:
                return self

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
            try:
                os.remove(self.path)
            except OSError:
                pass


def read_outbox(pkg):
    raw = read_bytes(os.path.join(pkg.judge_dir, OUTBOX))
    out = []
    for line in (raw or b"").decode("utf-8", "replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("event_id"):
            out.append(ev)
    return out


def write_outbox(pkg, events):
    path = os.path.join(pkg.judge_dir, OUTBOX)
    if not events:
        if os.path.exists(path):
            os.remove(path)
        return
    events = events[-OUTBOX_MAX:]
    size = 0
    for ev in reversed(events):                 # keep the code of the newest events only
        n = len(ev.get("code", "")) + len(ev.get("code_b64", ""))
        if size + n > OUTBOX_CODE:
            ev.pop("code", None)
            ev.pop("code_b64", None)
        else:
            size += n
    write_bytes(path, "".join(json.dumps(ev, ensure_ascii=False) + "\n" for ev in events).encode("utf-8"))


def add_event(pkg, ev):
    with OutboxLock(pkg):
        write_outbox(pkg, read_outbox(pkg) + [ev])


def drop_events(pkg, ids):
    if not ids:
        return
    with OutboxLock(pkg):
        write_outbox(pkg, [ev for ev in read_outbox(pkg) if ev["event_id"] not in ids])


def relabel(pkg, code):
    """Events waiting under an older code of the same student (the teacher made a new code) move to the new one."""
    nick = code.rsplit("-", 1)[0]
    with OutboxLock(pkg):
        events = read_outbox(pkg)
        changed = False
        for ev in events:
            old = str(ev.get("student", ""))
            if old.lower() != code.lower() and old.rsplit("-", 1)[0].lower() == nick.lower():
                ev["student"] = code
                changed = True
        if changed:
            write_outbox(pkg, events)


# ----------------------------------------------------------------------------- after a judged solution
def record(pkg, pid, score, verdicts, attempt, src):
    """Put the event of one judged solution in the outbox (when logged in and reports are on)."""
    if endpoint(pkg) is None:
        return
    login, _ = load_login(pkg)
    info = pkg.problems.get(pid)
    if not login["code"] or not login["report"] or info is None:
        return
    data = read_bytes(src) or b""
    ev = {"v": 1, "event_id": uuid.uuid4().hex, "student": login["code"], "pkg": pkg.name,
          "pkg_version": pkg.version, "pid": pid, "problem": info["problem"], "slot_path": info["slot_path"],
          "title": info.get("title", ""), "set": info.get("set", ""), "set_kind": info.get("set_kind", ""),
          "set_pids": info.get("set_pids", []), "score": int(score),
          "verdicts": "".join(VERDICT_LETTER.get(v, "-") for v in verdicts), "attempt": attempt or 0,
          "time": now_iso(), "code_sha256": sha256(data), "pdf": problem_pdf(pkg, info["slot_path"])}
    if login["sync"] and len(data) <= MAX_CODE:
        try:
            ev["code"] = data.decode("utf-8")
        except UnicodeDecodeError:              # e.g. Thai comments saved in a Windows code page
            ev["code_b64"] = base64.b64encode(data).decode("ascii")
    add_event(pkg, ev)


def problem_pdf(pkg, slot_path):
    """Package path of the problem's own PDF (<set>/<slot>/<slot>_<Title>.pdf), for the link in Discord; "" if none."""
    folder, _ = slot_path.rsplit("/", 1)
    slot = folder.rsplit("/", 1)[-1]
    try:
        names = sorted(n for n in os.listdir(os.path.join(pkg.root, *folder.split("/")))
                       if n.startswith(slot + "_") and n.endswith(".pdf"))
    except OSError:
        return ""
    return f"{folder}/{names[0]}" if names else ""


def send(pkg, login, url, deadline):
    """POST the waiting events of this login in batches until done or the deadline. Returns "bad_code", "sent",
    "partial" or "offline"."""
    result = "sent"
    while True:
        events = [ev for ev in read_outbox(pkg) if same_code(ev.get("student"), login["code"])]
        if not events:
            return result
        batch, size = [], 0
        for ev in events:
            n = len(json.dumps(ev))
            if batch and (len(batch) >= BATCH_EVENTS or size + n > BATCH_BYTES):
                break
            batch.append(ev)
            size += n
        left = deadline - time.time()
        if left <= 0.2:
            return "partial"
        ans = post_within(url, {"action": "event", "student": login["code"], "pkg": pkg.name, "events": batch}, left)
        if not ans:
            return "offline" if result == "sent" else "partial"
        if not ans.get("ok"):
            return "bad_code" if ans.get("error") == "bad_code" else "offline"
        accepted = set(str(x) for x in ans.get("accepted", []))
        drop_events(pkg, accepted)
        save_state(pkg, last_sent=now_iso())
        if ans.get("name") and not login["verified_at"]:
            login.update(name=str(ans["name"]), verified_at=now_iso())
            save_login(pkg, login)
        if not accepted.intersection(ev["event_id"] for ev in batch):
            return "partial"                    # the server took none of them: try again next time


def flush(pkg, st, wait=SEND_WAIT):
    """Send what is waiting (after the result is on the screen) and say in one line when something is wrong."""
    url = endpoint(pkg)
    if url is None:
        return False
    login, exists = load_login(pkg)
    if not login["report"]:
        return False
    if not login["code"]:
        note(st, f"Not logged in: your results are not sent to your teacher ({pkg.command} --login)")
        return True
    box = []
    t = threading.Thread(target=lambda: box.append(send(pkg, login, url, time.time() + wait)), daemon=True)
    t.start()
    t.join(wait + 0.2)
    status = box[0] if box else "partial"
    if status == "bad_code":
        login.update(code="", name="", verified_at="", skipped=False)
        save_login(pkg, login)
        say(st, f"Your student code is not accepted any more: ask your teacher for a new one ({pkg.command} --login)",
            "yellow")
        return True
    waiting = sum(1 for ev in read_outbox(pkg) if same_code(ev.get("student"), login["code"]))
    if waiting:
        note(st, f"{waiting} result{'s' if waiting != 1 else ''} waiting to be sent to your teacher (sent next time)")
        return True
    return False


# ----------------------------------------------------------------------------- login
def interactive():
    if os.environ.get("JUDGE_REPORT_INTERACTIVE") == "1":
        return True
    try:
        return sys.stdin is not None and sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def ask(question):
    """input() that returns None at end of input (no terminal)."""
    try:
        print("  " + question, end="", flush=True)
        line = sys.stdin.readline()
    except (OSError, ValueError):
        return None
    if not line:
        print()
        return None
    return line.strip()


def yes(question, st):
    ans = ask(question + " [Y/n] ")
    return ans is not None and ans.lower() in ("", "y", "yes")


def hello(pkg, url, code):
    return post_within(url, {"action": "hello", "student": code, "pkg": pkg.name}, HELLO_WAIT)


def ensure_login(pkg, st):
    """First judged run on this computer: ask for the code and the two consents (only in a terminal that can
    type; otherwise flush() prints a one-line hint after the result)."""
    url = endpoint(pkg)
    if url is None:
        return
    login, _ = load_login(pkg)
    if login["code"] or login["skipped"] or not login["report"] or not interactive():
        return
    login_flow(pkg, st, url, login)
    print()


def login_flow(pkg, st, url, login, code=None):
    """Ask (or take) the code, check it, then the consents. Returns 0 when logged in."""
    print()
    say(st, "Reports to your teacher", "bold")
    note(st, "With your student code, the judge sends each result (problem, score, time) to your teacher's")
    note(st, "sheet and to your own Discord channel. Judging works the same without it.")
    note(st, "(VS Code: click into this terminal panel first, then type)")
    tries = 0
    ans = None
    while True:
        if code is None:
            code = ask(f"Student code from your teacher ({PLACEHOLDER}), or Enter to skip: ")
            if not code:
                login.update(skipped=True)
                save_login(pkg, login)
                note(st, f"Skipped. Log in later with: {pkg.command} --login")
                return 1
        code = code.strip()
        tries += 1
        if not CODE_RE.match(code):
            say(st, f"A student code looks like {PLACEHOLDER} (your name, a dash, 4 letters or digits).", "yellow")
        else:
            ans = hello(pkg, url, code)
            if ans is None or ans.get("ok") or ans.get("error") != "bad_code":
                break
            say(st, "This code is not valid (or not active).", "yellow")
        if tries >= LOGIN_TRIES or not interactive():
            login.update(skipped=True)
            save_login(pkg, login)
            note(st, f"Skipped for now. Ask your teacher for your code, then: {pkg.command} --login")
            return 1
        code = None
    if ans is not None and ans.get("ok"):
        login.update(code=code, name=str(ans.get("name", "")), verified_at=now_iso(), skipped=False)
        say(st, f"Hello {login['name'] or code}!", "green")
    else:
        login.update(code=code, name="", verified_at="", skipped=False)
        note(st, "No connection: your code is saved and will be checked the next time you are online.")
    login["report"] = yes("Send your scores to your teacher (needed for Discord)?", st)
    sync_ok = ans is None or ans.get("sync_allowed", True) is not False
    login["sync"] = bool(login["report"] and sync_ok and
                         yes("Keep a copy of your code with your teacher, to move to another computer?", st))
    save_login(pkg, login)
    relabel(pkg, code)
    say(st, f"Logged in as {code} for C2_Practice and C2_Mock on this computer.", "green")
    note(st, f"scores {'on' if login['report'] else 'off'} · code copy {'on' if login['sync'] else 'off'} · "
             f"change with --report on|off, --sync on|off")
    saved = 0
    if ans and isinstance(ans.get("saved"), dict):
        saved = int(ans["saved"].get(pkg.name, 0) or 0)
    if saved and yes(f"Your teacher keeps copies of {saved} of your problems. Copy them here now "
                     f"(never overwrites your code)?", st):
        pull(pkg, st)
    return 0


# ----------------------------------------------------------------------------- copying code in (pull, restore)
def today():
    return datetime.date.today().strftime("%Y%m%d")


def is_code_path(rel):
    """A safe package-relative path of a .cpp file (no absolute path, no .., no backslash, not in Judge/)."""
    parts = rel.split("/")
    return (rel.endswith(".cpp") and "\\" not in rel and not rel.startswith("/") and ":" not in rel
            and all(p not in ("", ".", "..") for p in parts) and parts[0] != "Judge" and len(parts) >= 2)


def copy_in(pkg, rel, data, tag):
    """Put data at the package path rel without ever overwriting written code. Returns "wrote" (missing or untouched
    starter), "same" (already there, also as a copy in old/) or the old/ path it was kept at."""
    path = os.path.join(pkg.root, *rel.split("/"))
    if not os.path.exists(path) or pkg.is_starter(path):
        write_bytes(path, data)
        return "wrote"
    if read_bytes(path) == data:
        return "same"
    folder = os.path.dirname(os.path.dirname(path))         # the set folder: <set>/<slot>/<code>.cpp
    old = os.path.join(folder, "old")
    if os.path.isdir(old):
        for name in os.listdir(old):
            if read_bytes(os.path.join(old, name)) == data:
                return "same"
    slot = os.path.basename(os.path.dirname(path))
    base = f"{slot}_{tag}_{today()}"
    name, k = base + ".cpp", 2
    while os.path.exists(os.path.join(old, name)):
        name, k = f"{base}_{k}.cpp", k + 1
    write_bytes(os.path.join(old, name), data)
    return os.path.relpath(os.path.join(old, name), pkg.root).replace(os.sep, "/")


def tally(st, counts, kept):
    note(st, f"wrote {counts['wrote']} · already the same {counts['same']} · kept in old/ {len(kept)}"
         + (f" · not in this version {counts['missing']}" if counts.get("missing") else ""))
    for p in kept[:20]:
        note(st, "  kept " + p + "  (your file in the problem folder was not changed)")
    if len(kept) > 20:
        note(st, f"  ... {len(kept) - 20} more")


def pull(pkg, st):
    """--pull: copy the code the teacher keeps (latest version of each problem) into this package."""
    url = endpoint(pkg)
    login, _ = load_login(pkg)
    if url is None:
        say(st, "Reports are not set up in this package (no server address in Judge/config.json).", "yellow")
        return 1
    if not login["code"]:
        say(st, f"Log in first: {pkg.command} --login", "yellow")
        return 1
    note(st, "Asking your teacher's server for your code ...")
    ans = post_within(url, {"action": "pull", "student": login["code"], "pkg": pkg.name}, PULL_WAIT)
    if ans is None:
        say(st, "No answer from the server (no internet?). Nothing was changed.", "yellow")
        return 1
    if not ans.get("ok"):
        say(st, f"The server refused: {ans.get('error', 'unknown error')}. Nothing was changed.", "yellow")
        return 1
    latest = {}
    for f in ans.get("files", []):
        if isinstance(f, dict) and f.get("pkg", pkg.name) == pkg.name:
            try:
                pid = int(f.get("pid"))
            except (TypeError, ValueError):
                continue
            if pid not in latest or str(f.get("time", "")) > str(latest[pid].get("time", "")):
                latest[pid] = f
    counts, kept = {"wrote": 0, "same": 0, "missing": 0}, []
    for pid, f in sorted(latest.items()):
        info = pkg.problems.get(pid)        # the place in the installed version (problems may have moved)
        if info is None:
            counts["missing"] += 1
            continue
        if "code_b64" in f:
            data = base64.b64decode(f["code_b64"])
        else:
            data = str(f.get("code", "")).encode("utf-8")
        r = copy_in(pkg, info["slot_path"], data, "cloud")
        if r in counts:
            counts[r] += 1
        else:
            kept.append(r)
    say(st, f"Pulled {len(latest)} problem{'s' if len(latest) != 1 else ''} from your teacher's copy", "green")
    tally(st, counts, kept)
    return 0


# ----------------------------------------------------------------------------- backup / restore (no internet)
def code_files(pkg):
    """[(package path, pid or None)] of every written .cpp: the code files and other .cpp in problem folders and
    old/ folders of the sets."""
    out, seen, sets = [], set(), set()
    for pid, info in pkg.problems.items():
        rel = info["slot_path"]
        sets.add(rel.rsplit("/", 2)[0])
        path = os.path.join(pkg.root, *rel.split("/"))
        if os.path.isfile(path) and not pkg.is_starter(path):
            out.append((rel, pid))
            seen.add(rel)
    for folder in sorted(sets):
        top = os.path.join(pkg.root, *folder.split("/"))
        if not os.path.isdir(top):
            continue
        for sub in sorted(os.listdir(top)):
            d = os.path.join(top, sub)
            if not os.path.isdir(d):
                continue
            for name in sorted(os.listdir(d)):
                rel = f"{folder}/{sub}/{name}"
                if name.endswith(".cpp") and rel not in seen and os.path.isfile(os.path.join(d, name)) \
                        and not pkg.is_starter(os.path.join(d, name)):
                    out.append((rel, None))
    return out


def backup(pkg, st):
    """--backup: every written .cpp (and Judge/progress.json) into one zip next to the Judge folder."""
    files = code_files(pkg)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{os.path.basename(pkg.root) or pkg.name}_backup_{stamp}.zip"
    path = os.path.join(pkg.root, name)
    index = {"pkg": pkg.name, "version": pkg.version, "time": now_iso(),
             "files": {rel: pid for rel, pid in files if pid is not None}}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("backup.json", json.dumps(index, ensure_ascii=False, indent=1))
        for rel, _ in files:
            z.write(os.path.join(pkg.root, *rel.split("/")), rel)
        prog = os.path.join(pkg.judge_dir, PROGRESS)
        if os.path.isfile(prog):
            z.write(prog, "Judge/" + PROGRESS)
    say(st, f"Saved {len(files)} code file{'s' if len(files) != 1 else ''} in {name}", "green")
    note(st, f"Copy it to the new computer, then there: {pkg.command} --restore {name}")
    return 0


def merge_progress(mine, theirs):
    """Best scores of two progress.json files (Judge/progress.json of each package): the best of both."""
    for pid, e in theirs.get("problems", {}).items():
        if not isinstance(e, dict):
            continue
        m = mine["problems"].setdefault(pid, {"best": 0, "attempts": 0})
        if e.get("best", 0) > m.get("best", 0):
            m["best"], m["best_at"] = e.get("best", 0), e.get("best_at", "")
        if e.get("solved_at") and (not m.get("solved_at") or e["solved_at"] < m["solved_at"]):
            m["solved_at"] = e["solved_at"]
        m["attempts"] = max(m.get("attempts", 0), e.get("attempts", 0))
        hist = sorted({tuple(x) for x in m.get("history", []) + e.get("history", []) if isinstance(x, list)})
        m["history"] = [list(x) for x in hist][-30:]
        if hist:
            m["last"], m["last_score"] = hist[-1][0], hist[-1][1]
    return mine


def restore(pkg, st, zpath):
    """--restore ZIP: put back the files of a --backup zip, never over written code."""
    if not zpath or not os.path.isfile(zpath):
        say(st, f"Zip file not found: {zpath}", "red")
        return 1
    try:
        z = zipfile.ZipFile(zpath)
        index = json.loads(z.read("backup.json").decode("utf-8"))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile):
        say(st, "This is not a backup made with --backup.", "red")
        return 1
    if index.get("pkg") != pkg.name:
        say(st, f"This backup is of the other package ({index.get('pkg')}); restore it there.", "red")
        return 1
    pids = index.get("files", {})
    counts, kept = {"wrote": 0, "same": 0, "missing": 0}, []
    with z:
        for rel in z.namelist():
            if rel == "Judge/" + PROGRESS:
                theirs = json.loads(z.read(rel).decode("utf-8"))
                p = os.path.join(pkg.judge_dir, PROGRESS)
                mine = load_json(p, None) or {"version": 1, "problems": {}}
                write_json(p, merge_progress(mine, theirs))
                continue
            if not is_code_path(rel):
                continue
            target = rel
            pid = pids.get(rel)
            if pid is not None:
                info = pkg.problems.get(int(pid))
                if info is None:
                    counts["missing"] += 1
                    continue
                target = info["slot_path"]          # the problem may live elsewhere in this version
            elif not os.path.isdir(os.path.join(pkg.root, rel.split("/")[0])):
                counts["missing"] += 1
                continue
            r = copy_in(pkg, target, z.read(rel), "backup")
            if r in counts:
                counts[r] += 1
            else:
                kept.append(r)
    say(st, f"Restored from {os.path.basename(zpath)}", "green")
    tally(st, counts, kept)
    return 0


# ----------------------------------------------------------------------------- commands
def status(pkg, st):
    url = endpoint(pkg)
    login, exists = load_login(pkg)
    path = login_path(pkg)
    events = read_outbox(pkg)
    mine = sum(1 for ev in events if same_code(ev.get("student"), login["code"]))
    state = load_state(pkg)
    host = re.sub(r"^(https?://[^/]+).*$", r"\1/...", url) if url else "not set up in this package"
    who = (f"{login['code']}" + (f" ({login['name']})" if login["name"] else "")
           + ("" if login["verified_at"] else "  (not checked yet: checked when online)")) if login["code"] else "not logged in"
    print()
    say(st, "Reports to your teacher", "bold")
    print(f"  Student   {who}")
    print(f"  Scores    {'on' if login['report'] else 'off'}" + st.dim("   (--report on|off)"))
    print(f"  Code copy {'on' if login['sync'] else 'off'}" + st.dim("   (--sync on|off)"))
    print(f"  Login     {path}" + ("" if exists else st.dim("  (not created yet)")))
    if os.path.basename(path) == LOCAL_LOGIN:
        print("  " + st.dim("          Judge/.student is used instead of the shared file, for this package only"))
    print(f"  Server    {host}")
    print(f"  Last sent {state.get('last_sent', 'never').replace('T', ' ')[:16]}")
    print(f"  Waiting   {mine}" + (st.dim(f"   (+{len(events) - mine} of another code, not sent)") if len(events) > mine else ""))
    return 0


def set_switch(pkg, st, key, value):
    if value not in ("on", "off", "status"):
        say(st, f"--{'report' if key == 'report' else 'sync'} needs on, off or status", "red")
        return 2
    if value == "status":
        return status(pkg, st)
    login, _ = load_login(pkg)
    login[key] = value == "on"
    if key == "sync" and value == "on":
        login["report"] = True              # the code travels with the score
    if key == "report" and value == "off":
        login["sync"] = False
    save_login(pkg, login)
    what = "Sending scores to your teacher" if key == "report" else "Keeping a copy of your code with your teacher"
    say(st, f"{what}: {value}", "green")
    if value == "on" and not login["code"]:
        note(st, f"(you are not logged in yet: {pkg.command} --login)")
    if key == "sync" and value == "off":
        note(st, "(copies your teacher already has stay there; ask your teacher to delete them)")
    return 0


def command(pkg, st, name, value=None):
    """The report commands of judge.py: --login [CODE], --logout, --report on|off|status, --sync on|off|status,
    --pull, --backup, --restore ZIP. Returns the exit code."""
    if name == "backup":
        return backup(pkg, st)
    if name == "restore":
        return restore(pkg, st, value)
    if name == "report":
        return set_switch(pkg, st, "report", value)
    if name == "sync":
        return set_switch(pkg, st, "sync", value)
    if name == "logout":
        login, _ = load_login(pkg)
        login.update(code="", name="", verified_at="", skipped=True)
        save_login(pkg, login)
        say(st, "Logged out on this computer (your code files are not touched).", "green")
        note(st, f"Log in again: {pkg.command} --login")
        return 0
    url = endpoint(pkg)
    if url is None:
        say(st, "Reports are not set up in this package (no server address in Judge/config.json).", "yellow")
        return 1
    if name == "pull":
        return pull(pkg, st)
    if name == "login":
        login, _ = load_login(pkg)
        if value is None and not interactive():
            say(st, f"Give the code: {pkg.command} --login {PLACEHOLDER}", "yellow")
            return 2
        login.update(report=True)
        return login_flow(pkg, st, url, login, value)
    return 2
