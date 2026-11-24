#!/usr/bin/env python3
"""
A local stand-in for the teacher's Apps Script Web App (C2_PRACTICE_SRC/tools/apps_script/Code.gs), for the
regression tests and for trying report.py by hand. Same protocol: POST JSON {action: hello | event | pull, ...};
like Apps Script it answers a POST with a 302 redirect to a one-time URL whose GET returns the JSON answer.

  python3 tools/fake_report_server.py --student mona-K7Q3:Mona [--student ...] [--port 8765]
  then, in a built package:  JUDGE_REPORT_URL=http://127.0.0.1:8765/exec python3 ../Judge/judge.py ...

As a module: srv = FakeServer({"mona-K7Q3": {"name": "Mona"}}); url = srv.start(); ...; srv.stop()
  srv.raw        events stored (one per event_id, like the raw tab)
  srv.drive      {student: {pkg: {problem: {"pid", "slot_path", "versions": [{sha, time, score, code}, ...]}}}}
  srv.requests   [(action, number of events)] of every POST
  srv.delay      seconds to wait before answering (a slow Google); srv.direct = True answers without the 302
Python 3.7+ standard library only.
"""
import argparse
import http.server
import json
import threading
import time
import uuid

KEEP = 4                # versions kept per problem (the latest + 3)


class FakeServer:
    def __init__(self, students):
        self.students = {c: dict({"name": c.split("-")[0], "active": True, "sync_allowed": True}, **v)
                         for c, v in students.items()}
        self.raw, self.drive, self.requests = [], {}, []
        self.delay, self.direct = 0.0, False
        self.answers = {}
        self.lock = threading.Lock()
        self.srv = None

    # ------------------------------------------------------------------ protocol (as Code.gs)
    def answer(self, req):
        action = req.get("action")
        code = str(req.get("student", ""))
        self.requests.append((action, len(req.get("events", []))))
        s = self.students.get(code)
        if not s or not s.get("active"):
            return {"ok": False, "error": "bad_code"}
        if action == "hello":
            saved = {pkg: len(probs) for pkg, probs in self.drive.get(code, {}).items()}
            return {"ok": True, "name": s["name"], "sync_allowed": s["sync_allowed"], "saved": saved}
        if action == "event":
            accepted = []
            with self.lock:
                have = {e["event_id"] for e in self.raw}
                keys = {(e["student"], e["pid"], e["time"], e["code_sha256"]) for e in self.raw}
                for ev in req.get("events", []):
                    if not isinstance(ev, dict) or ev.get("student") != code or not ev.get("event_id"):
                        continue
                    accepted.append(ev["event_id"])
                    key = (ev["student"], ev.get("pid"), ev.get("time"), ev.get("code_sha256"))
                    if ev["event_id"] in have or key in keys:
                        continue                        # already stored: accepted, not stored twice
                    have.add(ev["event_id"])
                    keys.add(key)
                    self.raw.append({k: v for k, v in ev.items() if k not in ("code", "code_b64")})
                    if ("code" in ev or "code_b64" in ev) and s["sync_allowed"]:
                        self.keep_code(code, ev)
            return {"ok": True, "accepted": accepted, "name": s["name"]}
        if action == "pull":
            files = []
            for pkg, probs in self.drive.get(code, {}).items():
                if req.get("pkg") and req["pkg"] != pkg:
                    continue
                for problem, f in probs.items():
                    v = f["versions"][0]
                    item = {"pkg": pkg, "pid": f["pid"], "problem": problem, "slot_path": f["slot_path"],
                            "sha": v["sha"], "time": v["time"]}
                    item.update({k: v[k] for k in ("code", "code_b64") if k in v})
                    files.append(item)
            return {"ok": True, "files": files}
        return {"ok": False, "error": "bad_request"}

    def keep_code(self, code, ev):
        probs = self.drive.setdefault(code, {}).setdefault(ev["pkg"], {})
        f = probs.setdefault(ev["problem"], {"pid": ev["pid"], "slot_path": ev["slot_path"], "versions": []})
        if f["versions"] and f["versions"][0]["sha"] == ev["code_sha256"]:
            return
        v = {"sha": ev["code_sha256"], "time": ev["time"], "score": ev["score"]}
        v.update({k: ev[k] for k in ("code", "code_b64") if k in ev})
        f["versions"] = ([v] + f["versions"])[:KEEP]
        f["pid"], f["slot_path"] = ev["pid"], ev["slot_path"]

    # ------------------------------------------------------------------ HTTP
    def start(self, port=0):
        fake = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def send_json(self, obj):
                body = json.dumps(obj).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(n)
                if fake.delay:
                    time.sleep(fake.delay)
                try:
                    ans = fake.answer(json.loads(body.decode("utf-8")))
                except ValueError:
                    ans = {"ok": False, "error": "bad_request"}
                if fake.direct:
                    return self.send_json(ans)
                key = uuid.uuid4().hex
                fake.answers[key] = ans
                self.send_response(302)         # like script.google.com -> script.googleusercontent.com
                self.send_header("Location", f"/echo?user_content_key={key}")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):
                key = self.path.split("user_content_key=")[-1]
                ans = fake.answers.pop(key, None)
                if ans is None or not self.path.startswith("/echo"):
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self.send_json(ans)

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.srv.daemon_threads = True
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.srv.server_address[1]}/exec"

    def stop(self):
        if self.srv:
            self.srv.shutdown()
            self.srv.server_close()
            self.srv = None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--student", action="append", default=[], help="CODE[:Name], e.g. mona-K7Q3:Mona")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--delay", type=float, default=0.0, help="seconds before each answer")
    a = ap.parse_args()
    students = {}
    for s in a.student or ["mona-K7Q3:Mona"]:
        code, _, name = s.partition(":")
        students[code] = {"name": name or code.split("-")[0]}
    srv = FakeServer(students)
    srv.delay = a.delay
    url = srv.start(a.port)
    print(f"fake report server: {url}  students: {', '.join(students)}  (Ctrl-C to stop)")
    print(f"  JUDGE_REPORT_URL={url}")
    try:
        while True:
            time.sleep(5)
            print(f"  {len(srv.raw)} events stored, {sum(len(p) for d in srv.drive.values() for p in d.values())} code files")
    except KeyboardInterrupt:
        srv.stop()


if __name__ == "__main__":
    main()
