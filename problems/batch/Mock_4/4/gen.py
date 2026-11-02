# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(840413)
MAXN, MAXA, MAXW = 200000, 10 ** 6, 10 ** 5
tests = []


def add(a, w):
    n = len(a)
    assert 1 <= n <= MAXN and len(w) == n
    assert all(1 <= x <= MAXA for x in a) and all(1 <= x <= MAXW for x in w)
    tests.append(f"{n}\n{' '.join(map(str, a))}\n{' '.join(map(str, w))}\n")


def rlist(n, lo, hi):
    rnd = random.random
    span = hi - lo + 1
    return [lo + int(rnd() * span) for _ in range(n)]


def zigzag(n, lo, hi, run_lo, run_hi):
    """monotone runs of random lengths going up and down alternately, values kept in [lo, hi]"""
    a, x, up = [], (lo + hi) // 2, True
    rnd = random.random
    while len(a) < n:
        ln = run_lo + int(rnd() * (run_hi - run_lo + 1))
        for _ in range(ln):
            step = 1 + int(rnd() * max(1, (hi - lo) // (2 * run_hi)))
            x = x + step if up else x - step
            x = min(hi, max(lo, x))
            a.append(x)
        up = not up
    return a[:n]


def heavy_inside(a, lo_w, hi_w, light):
    """light weights on the turning points of a, heavy ones elsewhere (inside the monotone runs)"""
    n = len(a)
    w = rlist(n, lo_w, hi_w)
    for i in range(n):
        if (i == 0 or i == n - 1 or (a[i] - a[i - 1]) * (a[i + 1] - a[i]) <= 0):
            w[i] = 1 + int(random.random() * light)
    return w


def far_apart(n, blk_lo, blk_hi, kind):
    """heavy trees far apart, separated by blocks of light trees that cannot zigzag on their own (all equal, strictly
    increasing or strictly decreasing), so the best chain jumps over whole blocks"""
    a, w, rnd, hi = [], [], random.random, True
    while len(a) < n:
        if kind == "dec":                                   # all heavy trees short
            a.append(1 + int(rnd() * 100000))
        elif kind == "alt":                                 # heavy trees alternately tall and short
            a.append(MAXA - int(rnd() * 1000) if hi else 1 + int(rnd() * 1000))
            hi = not hi
        else:                                               # all heavy trees tall
            a.append(MAXA - int(rnd() * 100000))
        w.append(MAXW - int(rnd() * 1000))
        ln = blk_lo + int(rnd() * (blk_hi - blk_lo + 1))
        if kind == "alt":
            x = 2000 + int(rnd() * 100000)
            a += list(range(x, x + ln))
        elif kind == "dec":
            x = 500000 + int(rnd() * 100000)
            a += list(range(x, x - ln, -1))
        else:
            a += [400000 + int(rnd() * 100000)] * ln
        w += [1 + int(rnd() * 50) for _ in range(ln)]
    return a[:n], w[:n]


def wall(a, w, ln):
    """a block of ln light trees of one height in the middle of a and w (lengths kept): the best chain has to
    jump over it"""
    n, rnd = len(a), random.random
    p = n // 3 + int(rnd() * (n // 3))
    h = 1 + int(rnd() * MAXA)
    a = a[:p] + [h] * ln + a[p:]
    w = w[:p] + [1 + int(rnd() * 50) for _ in range(ln)] + w[p:]
    return a[:n], w[:n]


# samples
add([4, 9, 2, 8, 7, 5, 1], [9, 7, 5, 5, 9, 4, 8])
add([3, 5, 5, 2], [1, 4, 6, 2])
add([1, 2, 3, 4, 5], [5, 1, 1, 1, 6])
add([1000000], [100000])
add([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], [8, 2, 7, 1, 8, 2, 8, 1, 8, 2])
# hidden: small (brute checks these)
add([2, 1], [1, 1])
add([7, 7, 3, 3, 9, 9, 1, 1], [5, 9, 2, 8, 4, 6, 1, 7])
add(rlist(10, 1, 3), rlist(10, 1, 10))
add(rlist(200, 1, 5), rlist(200, 1, 100))
a = zigzag(1000, 1, 1000, 2, 8)
add(a, heavy_inside(a, 500, 1000, 100))
add(rlist(2000, 1, 50), rlist(2000, 1, MAXW))
add(sorted(rlist(3000, 1, 2000), reverse=True), rlist(3000, 1, MAXW))
a = [1 + (i % 2) for i in range(5000)]                                  # 1 2 1 2 ...
add(a, rlist(5000, 1, MAXW))
add(rlist(15000, 1, MAXA), rlist(15000, 1, MAXW))
# hidden: big
N = MAXN
add(*wall(rlist(N, 1, MAXA), rlist(N, 1, MAXW), 30000))
add(*far_apart(N, 8000, 30000, "dec"))
add(*wall(rlist(N, 1, 10), rlist(N, 1, MAXW), 30000))
add(*wall(rlist(N, 1, 2), rlist(N, 1, MAXW), 25000))
add([MAXA - (i % 2) for i in range(N)], [MAXW] * N)                    # perfect zigzag, all heavy
add([1 + (i // 2) % 2 for i in range(N)], [MAXW - (i % 7) for i in range(N)])   # pairs of equal values
a = zigzag(N, 1, MAXA, 3, 30)
add(*wall(a, heavy_inside(a, MAXW // 2, MAXW, 1000), 35000))
a = zigzag(N, 1, 1000, 2, 6)
add(*wall(a, heavy_inside(a, 1000, MAXW, 50), 40000))
a = zigzag(N, 1, MAXA, 100, 2000)
add(*wall(a, rlist(N, 1, MAXW), 30000))
add(list(range(1, N + 1)), rlist(N, 1, MAXW))                          # increasing: at most 2 items
add([7] * N, rlist(N, 1, MAXW))                                         # all equal: one item
a = []
for i in range(N // 2):                                                 # converging zigzag
    a += [1 + i % 1000 * 7, MAXA - i % 1000 * 7]
add(*wall(a, rlist(N, 1, MAXW), 28000))
a = [x for x in rlist(N // 50, 1, MAXA) for _ in range(50)]            # blocks of equal values
add(a, rlist(N, 1, MAXW))
add(*far_apart(N, 500, 4000, "const"))
a = zigzag(N, 1, 20, 1, 4)
add(*wall(a, rlist(N, MAXW - 100, MAXW), 30000))
add(*far_apart(N, 15000, 40000, "const"))
add(*far_apart(N, 1500, 20000, "alt"))
add(*far_apart(N, 20000, 50000, "alt"))
add(*far_apart(N, 12000, 40000, "const"))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
