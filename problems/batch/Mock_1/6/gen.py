# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1204)
MAXN, MAXV = 100000, 1000000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(ds):
    assert 1 <= len(ds) <= MAXN
    for a, b in ds:
        assert 1 <= a <= MAXV and 1 <= b <= MAXV
    tests.append(str(len(ds)) + "\n" + "".join(f"{a} {b}\n" for a, b in ds))


def flip(ds):
    """turn a random half of the dominoes around"""
    return [(b, a) if rnd() < 0.5 else (a, b) for a, b in ds]


def shuffled(ds):
    ds = list(ds)
    random.shuffle(ds)
    return ds


def relabel(ds, lo=1, hi=MAXV):
    """map the values used to distinct random values in [lo, hi]"""
    vals = sorted({v for d in ds for v in d})
    new = random.sample(range(lo, hi + 1), len(vals))
    m = dict(zip(vals, new))
    return [(m[a], m[b]) for a, b in ds]


def rand_edges(n, vmax, loops=0.0):
    out = []
    for _ in range(n):
        a = ri(1, vmax)
        out.append((a, a) if rnd() < loops else (a, ri(1, vmax)))
    return out


def cycles(n, lmin, lmax, start=1):
    """disjoint cycles (every vertex even) with about n edges in total"""
    out, v = [], start
    while len(out) < n:
        ln = min(ri(lmin, lmax), n - len(out))
        if ln == 1:
            out.append((v, v))
        else:
            for i in range(ln):
                out.append((v + i, v + (i + 1) % ln))
        v += ln
    return out


def paths(n, lmin, lmax, start=1):
    """disjoint paths (two odd ends each) with about n edges in total"""
    out, v = [], start
    while len(out) < n:
        ln = min(ri(lmin, lmax), n - len(out))
        for i in range(ln):
            out.append((v + i, v + i + 1))
        v += ln + 1
    return out


# samples
add([(1, 2), (3, 4), (2, 3), (2, 5), (5, 5), (6, 6)])
add([(7, 7), (7, 7), (1, 1), (1, 7)])
add([(1, 2), (1, 3), (1, 4), (1, 5)])
add([(5, 9)])
add([(4, 8), (8, 4), (2, 6), (6, 6), (6, 4), (3, 3), (2, 3)])
# hidden: small (brute checks these)
add([(1000000, 1000000)])
add([(3, 3)] * 5 + [(1, 2)] + [(2, 2)] * 3)
add(flip(rand_edges(30, 8, 0.2)))
add(flip(rand_edges(200, 60, 0.1)))
add(flip(shuffled(cycles(150, 1, 6) + paths(150, 1, 5, 1000))))
add(relabel(flip(rand_edges(400, 300, 0.3))))
add(flip(rand_edges(600, 25)))
add(relabel(flip(shuffled(paths(500, 1, 3) + [(v, v) for v in range(2000, 2100)]))))
# hidden: big
BIG = [
    (12040, lambda: flip(rand_edges(MAXN, MAXV))),
    (12041, lambda: flip(rand_edges(MAXN, 1000))),
    (12042, lambda: flip(rand_edges(MAXN, 115000))),
    (12043, lambda: flip(rand_edges(MAXN, 100000, 0.5))),
    (12044, lambda: relabel([(v, v) for v in range(1, MAXN + 1)])),
    (12045, lambda: relabel(flip(shuffled(paths(MAXN, MAXN, MAXN))))),
    (12046, lambda: relabel(flip(shuffled(cycles(MAXN, 2, 40))))),
    (12047, lambda: relabel(flip(shuffled([(h, 1000 + 100 * h + j) for h in range(1, 1001) for j in range(100)])))),
    (12048, lambda: relabel(flip(shuffled(rand_edges(MAXN // 2, 60000) * 2)))),
    (12049, lambda: relabel(flip(shuffled(paths(MAXN, 1, 4))))),
    (12050, lambda: relabel(flip(shuffled(cycles(MAXN - 15000, 3, 30) + paths(15000, 1, 2, 500000))))),
    (12051, lambda: relabel(flip(shuffled(cycles(MAXN // 2, 1, 3) + rand_edges(MAXN // 2, 50000, 0.0))))),
    (12052, lambda: [(MAXV - ri(0, 99), MAXV - ri(0, 99)) for _ in range(MAXN)]),
    (12053, lambda: relabel(flip(shuffled(cycles(MAXN, MAXN, MAXN))))),
    (12054, lambda: relabel(flip(shuffled(paths(MAXN // 2, 50, 300) + cycles(MAXN // 2, 2, 2, 600000))))),
    (12055, lambda: flip(rand_edges(MAXN, 200000, 0.25))),
    (12056, lambda: relabel(flip(shuffled(cycles(MAXN, 1000, 20000))))),
    (12057, lambda: relabel(flip(shuffled([(1, 2)] * (MAXN // 2) + paths(MAXN // 2, 1, 1, 3))))),
]
for seed, make in BIG:
    random.seed(seed)
    add(make())

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
