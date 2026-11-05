# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(510501)
MAXN = 120000
DAY = 86400
rnd = random.random
tests = []


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


CLOCK = ["%02d:%02d:%02d" % (c // 3600, c // 60 % 60, c % 60) for c in range(DAY)]


def clock(t):
    return CLOCK[t % DAY]


def add_lines(lines):
    """lines: list of (absolute second, name, kind) in log order"""
    n = len(lines)
    assert 1 <= n <= MAXN
    out = [str(n)]
    prev = None
    for t, nm, k in lines:
        assert 1 <= len(nm) <= 10 and nm.isalpha() and nm.islower() and k in ("IN", "OUT")
        if prev is not None:
            assert 0 <= t - prev < DAY          # the day rule recovers the true times
        prev = t
        out.append("%s %s %s" % (clock(t), nm, k))
    tests.append("\n".join(out) + "\n")


def add_raw(rows):
    """samples: rows of 'HH:MM:SS name KIND'"""
    tests.append("\n".join([str(len(rows))] + rows) + "\n")


POOL = "".join(chr(97 + int(rnd() * 26)) for _ in range(300000))      # names are slices of this string


def names(u, lmin=1, lmax=10):
    """u distinct names; some are prefixes of others"""
    out, seen = [], set()
    while len(out) < u:
        if out and rnd() < 0.08:
            base = out[int(rnd() * len(out))]
            nm = base[:ri(1, len(base))] if rnd() < 0.5 else (base + chr(97 + ri(0, 25)))[:10]
        else:
            L = ri(lmin, lmax) if rnd() < 0.3 else ri(lmin, min(lmax, max(lmin, 5)))
            p = int(rnd() * (len(POOL) - 10))
            nm = POOL[p:p + L]
        if nm not in seen:
            seen.add(nm)
            out.append(nm)
    return out


def planned(n, u, horizon, grid=1, dmax=20000, ties=0.3, dup=0.15, stray=0.15, opn=0.3, heavy=0, seed=None):
    """users with planned stays (some repeated lengths, extra INs, stray OUTs, stays left open);
    events merged in time order, filler lines added so that consecutive lines are < 1 day apart, cut to n lines"""
    if seed is not None:
        random.seed(seed)
    nms = names(u + 1)
    filler = nms.pop()                 # this user only has OUT lines (never printed)
    ev = []
    per = max(2, n // u)
    for idx, nm in enumerate(nms):
        cnt = per * 30 if idx < heavy else ri(1, 2 * per)        # wanted number of lines
        cur = ri(0, horizon)
        if idx < heavy:
            cur = ri(0, horizon // 50)
        span = max(1, (horizon - cur) // max(1, cnt))
        fixed = [ri(0, dmax) for _ in range(3)] if rnd() < ties else None
        made = 0
        while made < cnt:
            t = cur + ri(0, 2 * span)
            d = fixed[int(rnd() * 3)] if fixed else ri(0, dmax) if rnd() < 0.9 else ri(0, 3 * span)
            t -= t % grid
            d -= d % grid
            ev.append((t, rnd(), nm, "IN"))
            made += 1
            if rnd() < dup:
                x = t + ri(0, d)
                ev.append((x - x % grid, rnd(), nm, "IN"))
                made += 1
            if made >= cnt and rnd() < opn:
                break
            ev.append((t + d, rnd(), nm, "OUT"))
            made += 1
            cur = t + d
            if rnd() < stray:
                x = cur + ri(0, span)
                ev.append((x - x % grid, rnd(), nm, "OUT"))
                made += 1
        if rnd() < stray:
            x = ri(0, horizon)
            ev.append((x - x % grid, rnd(), nm, "OUT"))
    ev.sort()
    lines, prev = [], None
    for t, _, nm, k in ev:
        while prev is not None and t - prev >= DAY:
            prev += ri(DAY // 2, DAY - 1)
            lines.append((prev, filler, "OUT"))
        lines.append((t, nm, k))
        prev = t
        if len(lines) >= n:
            break
    add_lines(lines[:n])


def stream(n, u, gaps, pin=0.55, seed=None):
    """random IN / OUT lines of u users; gaps is a list of (weight, lo, hi)"""
    if seed is not None:
        random.seed(seed)
    nms = names(u)
    tot = sum(w for w, _, _ in gaps)
    t = ri(0, DAY - 1)
    lines = []
    for _ in range(n):
        x = rnd() * tot
        for w, lo, hi in gaps:
            x -= w
            if x < 0:
                break
        t += ri(lo, hi)
        lines.append((t, nms[int(rnd() * u)], "IN" if rnd() < pin else "OUT"))
    add_lines(lines)


# samples
add_raw(["09:00:00 b IN", "09:05:30 a IN", "09:12:00 b OUT", "09:20:00 a OUT"])
add_raw(["23:55:00 n IN", "23:58:00 t IN", "00:05:00 n OUT", "00:10:00 t OUT"])
add_raw(["08:30:00 m IN", "08:32:10 p IN", "08:40:00 m OUT", "08:41:00 m IN", "08:44:30 p OUT", "08:46:00 m OUT"])
add_raw(["17:50:00 t IN", "17:52:00 a IN", "17:58:00 a OUT", "18:02:00 t OUT", "09:05:00 a IN", "09:12:00 a OUT"])
add_raw(["23:55:00 k IN", "23:56:00 b IN", "23:59:00 k OUT", "00:04:00 b OUT", "23:58:00 k IN", "00:03:00 k OUT"])

# hidden: small (brute checks these)
add_raw(["10:00:00 a IN", "10:05:00 a IN", "10:10:00 a OUT", "10:12:00 a IN", "10:15:00 b OUT"])  # repeated IN, stray OUT, unfinished stay
add_raw(["09:00:00 k IN", "09:05:00 k OUT", "08:00:00 k IN", "08:05:00 k OUT"])                    # equal longest stays
add_raw(["00:00:00 a IN"])
add_raw(["23:59:59 zz OUT", "00:00:00 zz OUT", "00:00:00 z OUT"])
planned(40, 5, 5 * DAY, grid=600, dmax=7200)
planned(300, 30, 40 * DAY, grid=60, dmax=30000)
stream(2000, 20, [(3, 0, 0), (5, 1, 3600), (2, 40000, DAY - 1)])
planned(5000, 400, 3000 * DAY, grid=1, dmax=80000, heavy=3)
stream(8000, 3, [(1, 0, 0), (1, DAY - 1, DAY - 1), (2, 1, 600)], pin=0.5)
planned(10000, 2000, 400 * DAY, grid=3600, dmax=4 * 3600)

# hidden: big
BIG = [
    (520001, lambda: planned(MAXN, 40000, 60000 * DAY, grid=1, dmax=40000, heavy=2)),
    (520002, lambda: planned(MAXN, 56000, 30000 * DAY, grid=60, dmax=DAY, heavy=1)),
    (520003, lambda: planned(MAXN, 20000, 40000 * DAY, grid=3600, dmax=10 * 3600, heavy=3)),
    (520004, lambda: planned(MAXN, 30000, 50000 * DAY, grid=1, dmax=3 * DAY, ties=0.8, heavy=2)),
    (520005, lambda: planned(MAXN, 40000, 28000 * DAY, grid=10, dmax=5000, dup=0.4, stray=0.4, heavy=1)),
    (520006, lambda: planned(MAXN, 60000, 70000 * DAY, grid=1, dmax=60000, opn=0.8, heavy=2)),
    (520007, lambda: planned(MAXN, 10000, 45000 * DAY, grid=900, dmax=20 * 3600, heavy=5)),
    (520009, lambda: stream(MAXN, 30000, [(4, 0, 0), (3, 1, 5000), (3, 50000, DAY - 1)])),
    (520010, lambda: stream(MAXN, 50000, [(1, DAY - 1, DAY - 1), (1, 0, 0), (1, DAY - 2, DAY - 1)])),
    (520011, lambda: stream(MAXN, 20000, [(9, 0, 0), (1, 1, DAY - 1)], pin=0.6)),
    (520012, lambda: stream(MAXN, 40000, [(1, 1, DAY - 1)], pin=0.5)),
    (520013, lambda: stream(MAXN, 5, [(2, 0, 0), (1, 1, 3600), (2, 60000, DAY - 1)], pin=0.5)),
    (520014, lambda: planned(MAXN, 60000, 35000 * DAY, grid=1, dmax=DAY - 1, ties=0.5, opn=0.5)),
    (520015, lambda: planned(MAXN, 25000, 60000 * DAY, grid=7200, dmax=DAY, heavy=4)),
    (520016, lambda: planned(MAXN, 45000, 40000 * DAY, grid=1, dmax=1000, dup=0.3, heavy=2)),
    (520017, lambda: stream(MAXN, 60000, [(1, 0, 0), (1, 1, 2), (1, 80000, DAY - 1)])),
]
for seed, make in BIG:
    random.seed(seed)
    make()

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
