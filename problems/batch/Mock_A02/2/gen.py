# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
import os, random

random.seed(70202)
rnd = random.random
MAXN, MAXD = 200000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def clamp(v):
    return min(MAXD, max(1, v))


def add(d):
    n = len(d)
    assert 1 <= n <= MAXN
    assert all(isinstance(x, int) and 1 <= x <= MAXD for x in d)
    tests.append(f"{n}\n{' '.join(map(str, d))}\n")


def uniform(n, lo=1, hi=MAXD):
    return [ri(lo, hi) for _ in range(n)]


def rising(n, step, noise, start=1):
    """about `step` more per plane, plus or minus `noise`: drops between planes far apart"""
    return [clamp(start + k * step + ri(-noise, noise)) for k in range(n)]


def plateaus(n, maxlen, gap):
    """runs of equal times (each run needs spreading), the runs `gap` apart"""
    d, v = [], ri(1, 1000)
    while len(d) < n:
        d += [clamp(v)] * min(ri(1, maxlen), n - len(d))
        v += ri(0, gap)
    return d


def sawtooth(n, period, height, climb):
    """teeth going up by `height` then falling back, the whole saw climbing slowly"""
    return [clamp(1 + (k % period) * height + (k // period) * climb) for k in range(n)]


def late_drops(n, count):
    """increasing times with a few dips of growing size, so the answer keeps changing"""
    d = [MAXD // 2 + k for k in range(n)]
    for j in sorted(random.sample(range(1, n), count)):
        d[j] = clamp(d[j] - ri(1, j * 2000))
    return d


# samples
add([4, 4, 7, 2, 9])
add([10, 20, 30, 30, 30])
add([12, 10, 13, 1, 19, 1, 12, 13])
add([MAXD, 1, MAXD])

# hidden: small
add([7])
add([5, 5])
add([3, 2])
add([1, 1, 1, 1, 1, 1])                        # the first times go below 1
add(uniform(10, 1, 12))
add(plateaus(12, 4, 3))
add(rising(40, 2, 6))
add(sawtooth(30, 5, 4, 3))
add(uniform(2000))
add(rising(2000, 3, 40))

# hidden: big
add(uniform(MAXN))
add(uniform(MAXN, MAXD - 1000, MAXD))
add([MAXD] * MAXN)                             # all at the same minute
add([1] * MAXN)
add(list(range(MAXD, MAXD - MAXN, -1)))         # going down by 1
add(list(range(1, MAXN + 1)))                  # already fine: all 0
add([MAXD - MAXN + 1 + k // 2 for k in range(MAXN)])   # pairs at the same minute
add(rising(MAXN, 1, 3))
add(rising(MAXN, 2, 1000))
add(rising(MAXN, 4000, 2000000, 10 ** 6))
add(plateaus(MAXN, 50, 60))
add(plateaus(MAXN, 3, 2))
add(sawtooth(MAXN, 1000, 3, 2000))
add(sawtooth(MAXN, 7, 1, 7))
add(late_drops(MAXN, 40))
add([clamp(MAXD - 3 * k + (k % 3) * 7) for k in range(MAXN)])  # down with small bumps
add([1 + k if k < MAXN - 1 else 1 for k in range(MAXN)])      # one drop at the very end
add([MAXD] + rising(MAXN - 1, 1, 2))                           # the first plane is far too late

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
