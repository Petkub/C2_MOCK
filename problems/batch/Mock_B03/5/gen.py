# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer for a prefix follows the plan run by run (neighbouring stages with the same direction form one run);
# each run ends at the earliest checkpoint where a strictly monotone chain of (run length + 1) points can end.
# Big tests keep the answers large (an O(N * answer) DP must time out), split long runs into many stages,
# use many equal heights (strict steps) and shapes where a single greedy chain gets stuck.
import os, random

random.seed(7202)
rnd = random.random
MAXN, MAXM, MAXC, MAXH = 200000, 200000, 10 ** 9, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(h, plan):
    """h: heights, plan: list of (d, c)"""
    n, m = len(h), len(plan)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    assert all(1 <= x <= MAXH for x in h)
    assert all(d in (0, 1) and 1 <= c <= MAXC for d, c in plan)
    lines = ["%d %d" % (n, m), " ".join(map(str, h))] + ["%d %d" % (d, c) for d, c in plan]
    tests.append("\n".join(lines) + "\n")


def rand_h(n, hi=MAXH):
    return [ri(1, hi) for _ in range(n)]


def trend(n, slope, noise, base=1):
    """heights that rise by slope per point with random noise (slope < 0: fall), clipped to [1, MAXH]"""
    out = []
    for i in range(n):
        v = base + int(slope * i) + ri(-noise, noise)
        out.append(min(MAXH, max(1, v)))
    return out


def waves(n, period, amp, noise):
    """a zigzag: up for period points, down for period points, ..."""
    out, v, up = [], amp + 1, True
    for i in range(n):
        if i % period == 0 and i > 0:
            up = not up
        v += (1 if up else -1) * ri(1, amp)
        out.append(v)
    lo = min(out)
    return [min(MAXH, x - lo + 1 + ri(0, noise)) for x in out]


def alt_plan(m, first, lens):
    """m stages, directions alternate starting with first, lengths drawn from lens()"""
    return [((first + i) % 2, lens()) for i in range(m)]


def split_plan(runs, first, pieces):
    """runs: list of run lengths with alternating directions; each run is cut into stages of sizes from pieces()"""
    plan = []
    for i, r in enumerate(runs):
        d = (first + i) % 2
        while r > 0:
            c = min(r, pieces())
            plan.append((d, c))
            r -= c
    return plan


def rand_plan(m, cmax):
    return [(ri(0, 1), ri(1, cmax)) for _ in range(m)]


# samples
add([1, 5, 3, 4, 2, 6], [(1, 1), (0, 1), (1, 2)])
add([4, 4, 6, 2, 2, 5, 1], [(0, 1), (1, 2)])
add([3, 3, 3, 3], [(1, 1), (0, 1)])
add([2, 9, 4, 7, 7, 1, 8, 3], [(0, 1), (1, 1), (0, 1), (1, 1), (0, 3), (1, 1)])
add([10, 20, 30, 40, 50], [(1, 2), (1, 2), (0, 1000000000)])
# hidden: small (brute checks these)
add([42], [(1, 5)])
add(rand_h(12, 5), rand_plan(5, 3))
add(rand_h(60, 10), rand_plan(20, 4))
add(rand_h(150), split_plan([ri(1, 6) for _ in range(40)], 1, lambda: ri(1, 2)))
add(trend(200, 1, 20, 50), split_plan([ri(5, 30) for _ in range(20)], 0, lambda: ri(1, 3)))
add(waves(250, 7, 5, 3), alt_plan(60, 1, lambda: ri(1, 8)))
add(rand_h(300, 30), rand_plan(300, 2))
# hidden: big (N = 200000)
add(rand_h(N), alt_plan(N, 1, lambda: 1))                                  # zigzag: the answer is about 2N / 3
add(rand_h(N, 3), alt_plan(N, 0, lambda: 1))                               # zigzag on three heights
add(waves(N, 50, 1000, 0), alt_plan(N // 50, 1, lambda: ri(10, 60)))
add(waves(N, 300, 50, 20), split_plan([ri(50, 250) for _ in range(2000)], 1, lambda: ri(1, 5)))
add(trend(N, 3, 30), [(1, MAXC)])                                         # one long climb, many points out of order
add(trend(N, 3, 30), [(1, 1)] * MAXM)                                     # the same climb cut into 1-step stages
add(trend(N, -4000, 2000, MAXH - 10), split_plan([N], 0, lambda: ri(1, 3)))  # one long descent in stages
add(rand_h(N, 2), alt_plan(N, 1, lambda: 1))                               # two heights
add(trend(N, 0.5, 3), split_plan([N // 4] * 4, 1, lambda: ri(1, 1000)))   # many equal neighbours
blk = []                                                                   # rising blocks like 5 6 7 1 2 3 4
for b in range(N // 400):
    base = 1 + b * 1000
    blk += [base + 500 + i for i in range(150)] + [base + i for i in range(250)]
add(blk, [(1, 150)] * 1300)
add(waves(N, 1000, 100, 0), split_plan([ri(100, 900) for _ in range(500)], 1, lambda: ri(50, 200)))
add(rand_h(N), rand_plan(MAXM, 1))                                         # random 1-step stages
add(rand_h(N, 1000), alt_plan(N // 3, 0, lambda: ri(1, 2)))
add(trend(N, 2, 50), [(1, ri(100, 400)) if i % 2 == 0 else (0, ri(1, 3)) for i in range(1000)])  # long climbs, short descents
add(waves(N, 20, 10000, 1000), split_plan([ri(3, 18) for _ in range(20000)], 1, lambda: ri(1, 6)))
add(trend(N, 10, 30), [(1, 10000), (0, 3), (1, 10000), (0, 3)] * 5 + [(1, MAXC)])
add(waves(N, 2, 1000, 0), alt_plan(MAXM, 1, lambda: ri(1, 2)))
add(trend(N, -3, 20, 2 * 10 ** 6), [(0, MAXC), (1, MAXC)])                # the descent never finishes

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
