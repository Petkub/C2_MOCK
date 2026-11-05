# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(350501)
MAXN, MAXK, MAXS, MAXP, MAXT, MAXW = 100000, 100000, 100000, 10000, 10 ** 9, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(speeds, jobs):
    n, k = len(jobs), len(speeds)
    assert 1 <= n <= MAXN and 1 <= k <= MAXK
    assert all(1 <= s <= MAXS for s in speeds)
    for a, p, w, c in jobs:
        assert 0 <= a <= MAXT and 1 <= p <= MAXP and 1 <= w <= MAXW
        assert c == -1 or a <= c <= MAXT
    lines = [f"{n} {k}", " ".join(map(str, speeds))] + [f"{a} {p} {w} {c}" for a, p, w, c in jobs]
    tests.append("\n".join(lines) + "\n")


def make(n, k, smax, pmax, tmax, wmax, cfrac, cdelay, smin=1, pmin=1):
    """random jobs: arrivals in [0, tmax], a share cfrac of them asks to cancel at most cdelay after arriving
    (a third of those at the very moment they arrive)"""
    speeds = [ri(smin, smax) for _ in range(k)]
    jobs = []
    for _ in range(n):
        a = ri(0, tmax)
        c = -1
        if rnd() < cfrac:
            c = a if rnd() < 1 / 3 else min(MAXT, a + ri(0, cdelay))
        jobs.append((a, ri(pmin, pmax), ri(1, wmax), c))
    return speeds, jobs


def busy_low(n, k, hold, smax, pmax, tmax, wmax, cfrac, cdelay):
    """the first `hold` jobs arrive at 0 with the most pages and keep the low-numbered printers busy
    for the whole test; the rest are short jobs served by the high-numbered printers"""
    speeds = [MAXS] * hold + [ri(1, smax) for _ in range(k - hold)]
    jobs = [(0, MAXP, 1, -1) for _ in range(hold)]
    for _ in range(n - hold):
        a = ri(1, tmax)
        c = min(MAXT, a + ri(0, cdelay)) if rnd() < cfrac else -1
        jobs.append((a, ri(1, pmax), ri(1, wmax), c))
    return speeds, jobs


def two_phase(n1, n2, k, t1, burst, wmax, cfrac):
    """a quiet phase (n1 short jobs over [0, t1]: printers are often idle and free up in every order),
    then a burst of n2 long jobs arriving in [t1 + 1, t1 + burst] that queue far beyond 2^31"""
    speeds = [ri(1, MAXS) for _ in range(k)]
    jobs = []
    for _ in range(n1):
        a = ri(0, t1)
        c = min(MAXT, a + ri(0, 3 * MAXS)) if rnd() < cfrac else -1
        jobs.append((a, ri(1, 3), ri(1, wmax), c))
    for _ in range(n2):
        a = ri(t1 + 1, t1 + burst)
        c = min(MAXT, a + ri(0, 10 ** 9)) if rnd() < cfrac else -1
        jobs.append((a, ri(1, MAXP), ri(1, wmax), c))
    random.shuffle(jobs)
    return speeds, jobs


def held(h, made):
    """h extra printers numbered first, each taking at second 0 one extra job that lasts 10^9 seconds (the extra
    jobs have the smallest ids and the highest priority used), so the later jobs go to printers numbered above h"""
    speeds, jobs = made
    top = max(w for _, _, w, _ in jobs)
    return [MAXS] * h + speeds, [(0, MAXP, top, -1)] * h + jobs


# samples
add([1, 2], [(0, 3, 1, -1), (0, 2, 5, -1), (1, 1, 2, 3), (1, 2, 3, -1), (2, 1, 3, -1)])
add([3, 1, 2], [(0, 2, 2, 1), (0, 1, 2, -1), (1, 4, 7, -1), (1, 1, 1, -1)])
add([2], [(5, 1, 1, -1), (0, 2, 4, -1), (3, 1, 9, -1)])
add([5, 1, 1, 3], [(2, 3, 1, -1), (2, 2, 6, -1), (0, 1, 1, -1)])
add([2, 1], [(0, 2, 3, -1), (1, 3, 5, -1), (1, 1, 3, 2), (2, 2, 1, -1)])

# hidden: small (brute checks these); small time ranges so that many events share a moment
add([7], [(MAXT, MAXP, MAXW, MAXT)])
add([1, 1, 1], [(4, 1, 1, -1)])
for n, k, smax, pmax, tmax, wmax, cfrac, cdelay in [
        (10, 2, 3, 3, 6, 3, 0.3, 3), (40, 3, 2, 4, 15, 4, 0.3, 5), (120, 5, 3, 3, 40, 3, 0.25, 6),
        (200, 1, 2, 3, 100, 5, 0.3, 50), (250, 20, 4, 5, 30, 2, 0.4, 3), (300, 8, 1, 6, 60, 10, 0.2, 20)]:
    add(*make(n, k, smax, pmax, tmax, wmax, cfrac, cdelay))

# hidden: big (each with its own seed, so changing one test does not change the others)
N, K = MAXN, MAXK
BIG = [
    # one printer, everything waits: a long queue and finish times far beyond 2^31
    (350601, lambda: make(N, 1, MAXS, MAXP, 1000, MAXW, 0.3, 10 ** 6, smin=MAXS // 2, pmin=MAXP // 2)),
    # many printers and still more work than they can do: a long queue, long varied jobs, few priority values
    (350602, lambda: make(N, 20000, MAXS, MAXP, 1000, 5, 0.3, 10 ** 9, smin=50000, pmin=5000)),
    (350603, lambda: make(N, 12000, MAXS, MAXP, 100, 50, 0.25, 10 ** 9, smin=10000, pmin=3000)),
    (350604, lambda: make(N, 25000, MAXS, MAXP, 10 ** 5, 3, 0.35, 10 ** 9, smin=60000, pmin=5000)),
    (350605, lambda: make(N, 30000, MAXS, MAXP, 0, 3, 0.3, 10 ** 9, smin=60000, pmin=6000)),
    (350606, lambda: make(N, 25000, MAXS, MAXP, 10 ** 5, 1, 0.3, 10 ** 9, smin=40000, pmin=4000)),
    (350607, lambda: make(N, 1000, MAXS, MAXP, 3000, 1000, 0.3, 10 ** 9, smin=2000, pmin=2000)),
    (350621, lambda: make(N, 10000, MAXS, MAXP, 10 ** 4, 7, 0.3, 10 ** 9, smin=8000, pmin=8000)),
    (350608, lambda: make(N, 5000, MAXS, MAXP, 10 ** 6, 10, 0.9, 10 ** 9, smin=50000, pmin=5000)),
    (350609, lambda: make(N, 35000, MAXS, MAXP, 50, MAXW, 0.3, 10 ** 9, smin=80000, pmin=8000)),
    # short jobs arriving in a burst: many printers finish, jobs arrive and requests come at the same moments
    # (held(h, ...): printers 1..h stay busy for the whole test)
    (350610, lambda: held(50000, make(N - 50000, 10000, 2, 2, 10, 3, 0.3, 3))),
    # a quiet phase, then a burst that queues
    (350624, lambda: two_phase(20000, 80000, 400, 10 ** 8, 1000, 5, 0.3)),
    # short jobs, a few arriving every second, very many printers
    (350613, lambda: make(N, K, 3, 3, 10 ** 5, 3, 0.3, 3)),
    (350611, lambda: held(50000, make(N - 50000, 40000, 2, 4, 50000, 2, 0.4, 2))),
    # the low-numbered printers are busy all the time
    (350614, lambda: busy_low(N, K, 60000, 5, 5, 200000, 10, 0.2, 20)),
    (350615, lambda: busy_low(N, K, 90000, 3, 4, 50000, 3, 0.3, 10)),
    # light load: printers often wait, several of them free at the same moment
    (350622, lambda: held(50000, make(N - 50000, 200, 3, 3, 30000, 3, 0.3, 5))),
    (350623, lambda: held(50000, make(N - 50000, 1000, 5, 5, 20000, 2, 0.3, 10))),
    (350616, lambda: make(N, 30000, MAXS, MAXP, MAXT, 100, 0.3, 1000)),
    # a small shop with a huge queue
    (350618, lambda: make(N, 50, MAXS, MAXP, 10 ** 6, 10 ** 6, 0.3, 10 ** 9, smin=1000, pmin=1000)),
    (350625, lambda: two_phase(50000, 50000, 2000, 5 * 10 ** 8, 50, 3, 0.3)),
]
for seed, mk in BIG:
    random.seed(seed)
    add(*mk())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
