# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(960622)
rnd = random.random
MAXN, MAXV = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(r, ts):
    n = len(ts)
    assert 1 <= n <= MAXN and 0 <= r <= MAXV
    assert all(1 <= a <= MAXV and 1 <= b <= MAXV for a, b in ts)
    tests.append(f"{n} {r}\n" + "".join(f"{a} {b}\n" for a, b in ts))


def shuffled(ts):
    ts = list(ts)
    random.shuffle(ts)
    return ts


def uniform(n, amax, bmax, amin=1, bmin=1):
    return [(ri(amin, amax), ri(bmin, bmax)) for _ in range(n)]


def correlated(n, amax, ratio, noise):
    """a high cap usually comes with many points: b about a * ratio, times a random factor in [1 - noise, 1 + noise]"""
    ts = []
    for _ in range(n):
        a = ri(1, amax)
        b = int(a * ratio * (1 - noise + 2 * noise * rnd()))
        ts.append((a, min(MAXV, max(1, b))))
    return ts


def anti(n, amax, bmax, noise):
    """a low cap usually comes with many points"""
    ts = []
    for _ in range(n):
        u = rnd()
        a = ri(1, max(1, int(amax * u)))
        b = int(bmax * (1 - u) * (1 - noise + 2 * noise * rnd()))
        ts.append((a, min(MAXV, max(1, b))))
    return ts


def levels(n, caps, bmax):
    """only a few different caps"""
    return [(caps[int(rnd() * len(caps))], ri(1, bmax)) for _ in range(n)]


def same_sum(n, d, bmax):
    """every tournament has the same a + b"""
    ts = []
    for _ in range(n):
        b = ri(1, min(bmax, d - 1))
        ts.append((d - b, b))
    return ts


def mixed(n, parts):
    """parts: list of (share, generator of one pair)"""
    ts = []
    for share, f in parts:
        ts += [f() for _ in range(int(n * share))]
    while len(ts) < n:
        ts.append(parts[0][1]())
    return shuffled(ts[:n])


def heavy(n, p, frac, bmax):
    """most tournaments give at most bmax points; a share p of them gives up to frac * a"""
    ts = []
    for _ in range(n):
        a = ri(1, MAXV)
        ts.append((a, max(1, int(a * frac * rnd())) if rnd() < p else ri(1, bmax)))
    return ts


def logv(hi):
    """a value whose number of digits is spread evenly up to hi"""
    return min(MAXV, max(1, int(hi ** rnd())))


def logu(n, amax, bmax, below=False):
    """caps and points of every size; below: points at most the cap"""
    ts = []
    for _ in range(n):
        a = logv(amax)
        ts.append((a, logv(min(bmax, a)) if below else logv(bmax)))
    return ts


def all_fit(n, r, bmax):
    """every tournament can be joined: caps follow a staircase that exactly allows one order"""
    order, cur = [], r
    for _ in range(n):
        b = ri(1, bmax)
        order.append((cur + ri(0, bmax // 3), b))
        cur += b
    return shuffled(order)


# samples
add(0, [(6, 8), (11, 2), (10, 1), (15, 8), (5, 4)])
add(3, [(15, 8), (8, 1), (14, 1), (7, 4), (10, 5)])
add(3, [(9, 2), (12, 5), (6, 4), (9, 5), (1, 2), (10, 2), (7, 2)])
add(3, [(10, 4), (15, 6), (11, 1), (14, 5), (10, 3), (12, 6), (9, 2)])
add(5, [(1, 1), (6, 6), (7, 7), (8, 2), (4, 8), (7, 3)])
# hidden: small (the subset brute force checks these)
add(0, [(13, 1), (8, 3), (4, 7), (1, 2), (10, 2), (11, 7), (3, 1)])  # sorting by a or by b alone fails here
add(7, [(6, 3)])                                                   # cap below the start: 0
add(MAXV, [(MAXV, MAXV)] * 3)                                      # only the first one fits
add(2, uniform(16, 60, 15))
add(0, correlated(18, 200, 0.4, 0.5))
add(0, anti(20, 300, 120, 0.3))
add(MAXV // 2, [(ri(MAXV // 2, MAXV), ri(MAXV // 10, MAXV)) for _ in range(20)])
# hidden: medium (O(N^2) brute)
add(0, logu(3000, 10 ** 7, 10 ** 7))
add(37, heavy(3000, 0.3, 0.05, 2000))
add(100, mixed(3000, [(0.5, lambda: (ri(1, 40000), ri(1, 300))), (0.5, lambda: (ri(40000, 10 ** 6), ri(500, 3000)))]))
# hidden: big (N = 100000)
N = MAXN
add(0, uniform(N, MAXV, 30000))
add(ri(1, 10 ** 6), uniform(N, MAXV, 100000))
add(0, heavy(N, 0.2, 0.1, 10000))
add(ri(1, 10 ** 5), heavy(N, 0.5, 0.01, 10000))
add(0, heavy(N, 0.05, 0.3, 30000))
add(0, logu(N, MAXV, 10 ** 5))
add(0, logu(N, MAXV, MAXV))
add(ri(1, 1000), logu(N, MAXV, MAXV, True))
add(ri(10 ** 6, 10 ** 7), logu(N, MAXV, 10 ** 6))
add(0, logu(N, MAXV, MAXV // 10))
add(0, correlated(N, MAXV, 0.0001, 0.99))
add(0, correlated(N, MAXV, 0.01, 0.9))
add(0, anti(N, MAXV, 200000, 0.5))
add(0, levels(N, [ri(1, MAXV) for _ in range(5)], 60000))
add(0, same_sum(N, MAXV, 50000))
add(0, mixed(N, [(0.6, lambda: (ri(1, 2 * 10 ** 8), ri(1, 20000))),
                 (0.4, lambda: (logv(MAXV), logv(10 ** 6)))]))
add(0, all_fit(N, 0, 9000))                                        # every tournament fits
add(ri(1, MAXV), uniform(N, MAXV, MAXV))                           # big values, a small answer
add(0, [(ri(MAXV - 1000, MAXV), ri(MAXV - 1000, MAXV)) for _ in range(N)])
add(5 * 10 ** 8, [(7 * 10 ** 8, 4000)] * N)                        # all the same
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
