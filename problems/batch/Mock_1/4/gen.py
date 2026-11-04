# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1205)
MAXN, MAXH, MAXC, MAXK = 100000, 10 ** 9, 1000, 10 ** 18
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(K, h, c):
    n = len(h)
    assert 1 <= n <= MAXN and len(c) == n and 0 <= K <= MAXK
    assert all(1 <= x <= MAXH for x in h) and all(1 <= x <= MAXC for x in c)
    tests.append(f"{n} {K}\n{' '.join(map(str, h))}\n{' '.join(map(str, c))}\n")


def cost(h, c, D):
    """the smallest cost for roughness D (to place K exactly at a chosen answer)"""
    g = list(h)
    for i in range(1, len(g)):
        if g[i - 1] + D < g[i]:
            g[i] = g[i - 1] + D
    for i in range(len(g) - 2, -1, -1):
        if g[i + 1] + D < g[i]:
            g[i] = g[i + 1] + D
    return sum(ci * (hi - gi) for hi, ci, gi in zip(h, c, g))


def maxdiff(h):
    return max([abs(a - b) for a, b in zip(h, h[1:])] + [0])


def at(h, c, frac_lo, frac_hi, minus=0):
    """K = cost of a roughness between frac_lo and frac_hi of the no-cut roughness (minus a little)"""
    D = int(maxdiff(h) * (frac_lo + (frac_hi - frac_lo) * rnd()))
    return max(0, cost(h, c, D) - minus)


def pits(n, k, side):
    """a high plateau with k deep pits: side 1 = pits in the right fifth, -1 = left fifth, 0 = both ends"""
    h = [ri(MAXH - 1000, MAXH) for _ in range(n)]
    for j in range(k):
        s = side if side else (1 if j % 2 else -1)
        p = ri(n - n // 5, n - 1) if s == 1 else ri(0, n // 5)
        h[p] = ri(1, 1000)
    return h


def pitted(h, k, side):
    """put k deep pits into h: side 1 = right fifth, 0 = both ends, 2 = anywhere (always one at the right end)"""
    n = len(h)
    for j in range(k):
        if side == 2:
            p = n - 1 if j == 0 else ri(0, n - 1)
        elif side == 1 or j % 2:
            p = ri(n - n // 5, n - 1)
        else:
            p = ri(0, n // 5)
        h[p] = ri(1, 1000)
    return h


def at_d(h, c, dlo, dhi):
    """K = cost of a roughness in [dlo, dhi]"""
    return cost(h, c, ri(dlo, dhi))


def cs(n, lo=1, hi=MAXC):
    return [ri(lo, hi) for _ in range(n)]


def rand_h(n, lo=1, hi=MAXH):
    return [ri(lo, hi) for _ in range(n)]


def zigzag(n, hi=MAXH):
    return [ri(hi - hi // 10, hi) if i % 2 else ri(1, hi // 10) for i in range(n)]


def spikes(n, k, base_hi=1000):
    h = [ri(1, base_hi) for _ in range(n)]
    for _ in range(k):
        h[ri(0, n - 1)] = ri(MAXH // 2, MAXH)
    return h


def walk(n, step, lo=1, hi=MAXH):
    """a random walk with steps up to `step`, kept inside [lo, hi]"""
    h, v = [], ri(lo, hi)
    for _ in range(n):
        v = min(hi, max(lo, v + ri(-step, step)))
        h.append(v)
    return h


def cliffs(n, rising):
    """slow slopes ended by sudden cliffs; rising=False mirrors it (cliffs on the other side)"""
    h, v = [], ri(1, 1000)
    for _ in range(n):
        if rnd() < 0.002:
            v = ri(1, 1000)
        else:
            v = min(MAXH, v + ri(0, 40000))
        h.append(v)
    return h if rising else h[::-1]


# samples
add(7, [3, 9, 4, 8, 2], [1, 1, 2, 1, 1])
add(10, [1, 10, 1], [1, 3, 1])
add(0, [7], [4])
add(100, [6, 2, 9, 5], [2, 1, 3, 1])
add(25, [12, 4, 15, 15, 3, 9, 20, 1], [2, 1, 3, 1, 2, 1, 1, 4])
# hidden: small (brute checks these)
for n, H, cmax in [(2, 30, 5), (6, 20, 3), (10, 40, 10), (15, 30, 1), (25, 40, 1000), (30, 25, 7)]:
    h, c = rand_h(n, 1, H), cs(n, 1, cmax)
    add(at(h, c, 0.1, 0.7, ri(0, 1)), h, c)
add(0, [60, 1], [MAXC, MAXC])
add(MAXK, [60, 1, 60], [MAXC, 1, MAXC])
h = rand_h(40, 1, 60); c = cs(40)
add(at(h, c, 0.1, 0.5), h, c)
# hidden: big
N = MAXN
BIG = [
    (12050, lambda: (lambda h, c: (at(h, c, 0.05, 0.9), h, c))(rand_h(N), cs(N))),
    (12053, lambda: (lambda h, c: (0, h, c))(rand_h(N), cs(N))),
    (12054, lambda: (lambda h, c: (MAXK, h, c))(rand_h(N), [MAXC] * N)),
    (12055, lambda: (lambda h, c: (at(h, c, 0.1, 0.5), h, c))(zigzag(N), cs(N))),
    (12056, lambda: (lambda h, c: (at_d(h, c, 2 * 10 ** 4, 8 * 10 ** 4), h, c))(pitted(walk(N, 10000, MAXH // 2), 5, 1), cs(N))),
    (12058, lambda: (lambda h, c: (at(h, c, 0.0002, 0.001), h, c))(cliffs(N, True), cs(N))),
    (12059, lambda: (lambda h, c: (at(h, c, 0.0002, 0.001), h, c))(cliffs(N, False), cs(N))),
    (12060, lambda: (lambda h, c: (at_d(h, c, 4 * 10 ** 4, 15 * 10 ** 4), h, c))(pitted(walk(N, 40000, MAXH // 2), 15, 1), [MAXC] * N)),
    (12061, lambda: (lambda h, c: (at_d(h, c, 3 * 10 ** 4, 10 ** 5), h, c))(pitted(walk(N, 30000, MAXH // 3), 50, 0), cs(N, 1, 1))),
    (12062, lambda: (lambda h, c: (at_d(h, c, 10 ** 4, 3 * 10 ** 4), h, c))(pits(N, 3, 1), cs(N))),
    (12069, lambda: (lambda h, c: (at_d(h, c, 2 * 10 ** 4, 10 ** 5), h, c))(pits(N, 20, 1), cs(N))),
    (12070, lambda: (lambda h, c: (at_d(h, c, 10 ** 4, 5 * 10 ** 4), h, c))(pits(N, 4, -1), cs(N))),
    (12071, lambda: (lambda h, c: (at_d(h, c, 10 ** 4, 4 * 10 ** 4), h, c))(pits(N, 6, 0), cs(N))),
    (12064, lambda: (lambda h, c: (at(h, c, 0.2, 0.8), h, c))(rand_h(N, 1, 100), cs(N))),
    (12065, lambda: (lambda h, c: (at(h, c, 0.5, 0.9, 1), h, c))(zigzag(N), cs(N, 900, MAXC))),
    (12066, lambda: (lambda h, c: (0, h, c))([7] * N, cs(N))),
    (12072, lambda: (lambda h, c: (at_d(h, c, 3 * 10 ** 4, 12 * 10 ** 4), h, c))(pitted(walk(N, 20000, MAXH // 2), 10, 1), cs(N))),
    (12073, lambda: (lambda h, c: (at_d(h, c, 5 * 10 ** 4, 2 * 10 ** 5), h, c))(pitted(walk(N, 50000, MAXH // 2), 30, 0), [MAXC] * N)),
    (12074, lambda: (lambda h, c: (at_d(h, c, 10 ** 4, 6 * 10 ** 4), h, c))(pits(N, 100, 1), cs(N, 1, 1))),
    (12075, lambda: (lambda h, c: (at_d(h, c, 10 ** 4, 3 * 10 ** 4), h, c))(pitted(walk(N, 5000, MAXH // 2), 8, 2), cs(N))),
    (12068, lambda: (lambda h, c: (at(h, c, 0.1, 0.4, 1), h, c))(spikes(N, 3000, 10 ** 6), cs(N))),
]
for seed, make in BIG:
    random.seed(seed)
    add(*make())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
