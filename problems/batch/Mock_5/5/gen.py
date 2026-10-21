# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(550521)
MAXN, MAXQ, MAXH = 100000, 100000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(h, qs):
    n, q = len(h), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert 1 <= min(h) and max(h) <= MAXH
    ls, rs = zip(*qs)
    assert min(ls) >= 1 and max(rs) <= n and all(map(int.__le__, ls, rs))
    lines = [f"{n} {q}", " ".join(map(str, h))] + [f"{l} {r}" for l, r in qs]
    tests.append("\n".join(lines) + "\n")


# ---------------------------------------------------------------- heights
def h_random(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def h_runs(n, hmax, decreasing, maxrun):
    """monotone with runs of equal heights"""
    h = []
    cur = hmax if decreasing else 1
    step = max(1, (hmax - 1) // n)
    while len(h) < n:
        h += [cur] * ri(1, maxrun)
        cur += -ri(1, step) if decreasing else ri(1, step)
        cur = max(1, min(hmax, cur))
    return h[:n]


def h_ruler(n, scale=1, noise=0):
    """h_i = (number of trailing zero digits of i in base 3) + 1: a nested pattern with many equal heights"""
    h = []
    for i in range(1, n + 1):
        t = 1
        while i % 3 == 0:
            i //= 3
            t += 1
        h.append(t * scale + (ri(0, noise) if noise else 0))
    return h


def h_walk(n, step, hmax):
    """random walk with small steps (many equal neighbours and plateaus)"""
    h = [ri(1, hmax)]
    for _ in range(n - 1):
        h.append(max(1, min(hmax, h[-1] + ri(-step, step))))
    return h


def h_mountain(n, hmax, maxrun, valley=False):
    """non-decreasing up to a peak, then non-increasing (or the other way round: a valley)"""
    a = h_runs(n // 2, hmax, False, maxrun)
    b = h_runs(n - n // 2, hmax, True, maxrun)
    if valley:
        return b + a
    return a + b


def h_walls(n, hmax):
    """equal walls of decreasing height with equal pairs inside each gap (the 9 5 5 pattern)"""
    h = []
    top = hmax
    while len(h) < n:
        h.append(top)
        v = ri(1, max(1, top - 1))
        k = ri(1, 4)
        h += [v] * k
        if rnd() < 0.3:
            h.append(ri(1, v))
        if rnd() < 0.2:
            top = max(2, top - ri(0, 3))
    return h[:n]


def h_zigzag(n, peak_levels, low):
    """peaks of a few equal heights separated by low hills"""
    h = []
    for i in range(n):
        h.append(random.choice(peak_levels) if i % 2 == 0 else ri(1, low))
    return h


# ---------------------------------------------------------------- queries
def q_long(n, q):
    a, b = max(1, n // 10), n - n // 10
    return [(1 + int(rnd() * a), b + int(rnd() * (n - b + 1))) for _ in range(q)]


def q_random(n, q):
    out = []
    for _ in range(q):
        l, r = 1 + int(rnd() * n), 1 + int(rnd() * n)
        out.append((l, r) if l <= r else (r, l))
    return out


def q_prefix_suffix(n, q):
    """long ranges with many different left ends"""
    out = []
    for _ in range(q):
        if rnd() < 0.5:
            out.append((ri(1, n // 2), ri(n // 2, n)))
        else:
            l = ri(1, n)
            out.append((l, ri(max(l, n - n // 20), n)))
    return out


def q_mixed(n, q):
    out = []
    for _ in range(q):
        t = rnd()
        if t < 0.15:
            l = ri(1, n)
            out.append((l, min(n, l + ri(0, 30))))
        elif t < 0.2:
            out.append((1, n))
        else:
            l, r = ri(1, n), ri(1, n)
            out.append((min(l, r), max(l, r)))
    return out


def q_all(n):
    return [(l, r) for l in range(1, n + 1) for r in range(l, n + 1)]


# samples
add([3, 1, 3, 2, 2, 5, 4, 4], [(1, 8), (2, 5), (3, 6), (7, 7)])
add([2, 2, 2, 2, 2], [(1, 5), (2, 4), (3, 3)])
add([7], [(1, 1)])
add([5, 1, 5, 1, 5, 6], [(1, 6), (1, 5), (2, 4), (3, 6), (5, 6)])
add([9, 5, 5, 8, 2, 3, 2, 9, 1], [(1, 9), (2, 7), (4, 8), (1, 4), (5, 9)])
# hidden: small (brute checks these)
add([1], [(1, 1)])
add(h_random(10, 1, 3), q_all(10))
add(h_random(14, 1, 2), q_all(14))
add(h_random(200, 1, 5), q_random(200, 2000))
add(h_random(300, 1, MAXH), q_mixed(300, 300))
add(h_walls(400, 30), q_all(30) + q_random(400, 600))
add(h_ruler(729), q_random(729, 800))
add(h_mountain(2000, 60, 5), q_long(2000, 60))
add(h_walk(12000, 2, 40), q_mixed(12000, 12000))
# hidden: big
N, Q = MAXN, MAXQ
add(h_random(N, 1, MAXH), q_long(N, Q))
add(h_random(N, 1, 3), q_random(N, Q))
add(h_random(N, 1, 10), q_long(N, Q))
add(h_random(N, 1, 100), q_prefix_suffix(N, Q))
add([MAXH] * N, q_mixed(N, Q))
add(list(range(1, N + 1)), q_long(N, Q))
add([MAXH - i for i in range(N)], q_prefix_suffix(N, Q))
add(h_runs(N, MAXH, True, 4), q_long(N, Q))
add(h_runs(N, 3000, True, 60), q_random(N, Q))
add(h_runs(N, MAXH, False, 3), q_prefix_suffix(N, Q))
add(h_walls(N, MAXH), q_long(N, Q))
add(h_walls(N, 20), q_mixed(N, Q))
add(h_zigzag(N, [50, 50, 50, 49], 48), q_prefix_suffix(N, Q))
add(h_ruler(N), q_long(N, Q))
add(h_ruler(N, 3, 1), q_random(N, Q))
add(h_mountain(N, 5000, 6), q_prefix_suffix(N, Q))
add(h_mountain(N, MAXH, 2, valley=True), q_long(N, Q))
add(h_walk(N, 1, 20), q_mixed(N, Q))
add(h_walk(N, 3, MAXH), [(1, N)] * Q)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
