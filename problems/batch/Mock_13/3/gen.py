# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1005)
MAXN, MAXW, MAXS = 100000, 10**9, 10**14
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(crates):
    assert 1 <= len(crates) <= MAXN
    for w, s in crates:
        assert 1 <= w <= MAXW and 0 <= s <= MAXS
    tests.append(f"{len(crates)}\n" + "".join(f"{w} {s}\n" for w, s in crates))


def deadline(n, wlo, whi, frac, noise):
    """crate i gets a random weight and w + s close to (a random rank) * (average weight) * frac,
    so about a share frac of the crates fit and many must be dropped on the way"""
    avg = (wlo + whi) / 2
    out = []
    for _ in range(n):
        w = ri(wlo, whi)
        d = int(ri(0, n - 1) * avg * frac) + ri(-noise, noise)
        out.append((w, min(MAXS, max(0, d - w))))
    return out


def heavy_bait(n, frac, k=1):
    """light crates as in deadline(), plus heavy crates with small w + s that take the early places"""
    out = deadline(n - n // 10, k, 2000 * k, frac, 3000 * k)
    for _ in range(n // 10):
        w = ri(20000 * k, 60000 * k)
        out.append((w, ri(0, 400000 * k)))
    random.shuffle(out)
    return out


def strong_heavy(n, frac, k=1):
    """weights spread widely, s anti-correlated with w: ordering by s alone or by w alone goes wrong"""
    out = []
    for _ in range(n):
        w = ri(1, 9000 * k) if rnd() < 0.7 else ri(9000 * k, 20000 * k)
        d = int(ri(0, n - 1) * 3000 * k * frac)
        out.append((w, min(MAXS, max(0, d - w + ri(0, 5000 * k)))))
    return out


def mixed(n, frac, heavy, k):
    """w + s near (a random rank) * frac * k, but a share `heavy` of the crates take a large part of it
    as weight: their s is small although w + s is large, so the order by s alone differs a lot"""
    out = []
    for _ in range(n):
        d = int(ri(1, n) * frac * k)
        if rnd() < heavy:
            w = max(1, min(MAXW, int(d * (0.2 + 0.7 * rnd()))))
        else:
            w = ri(1, k)
        out.append((w, max(0, d - w)))
    return out


def logspread(n, frac, spread, k):
    """w + s near (a random rank) * frac * k, weights spread over `spread` powers of ten around k"""
    out = []
    for _ in range(n):
        d = int(ri(1, n) * frac * k)
        w = max(1, min(MAXW, int(k * 10 ** (rnd() * spread - spread / 2))))
        out.append((w, max(0, d - w)))
    return out


def equal_sum(n, c):
    out = []
    for _ in range(n):
        w = ri(1, min(c, MAXW))
        out.append((w, c - w))
    return out


# samples
add([(3, 4), (5, 2), (2, 9), (4, 6), (6, 1)])
add([(5, 0), (1, 0), (2, 3)])
add([(7, 0)])
add([(10, 25), (8, 3), (1, 1), (6, 20), (9, 12), (3, 2)])
add([(4, 10), (4, 10), (4, 10), (4, 10), (2, 3), (7, 30), (1, 0), (5, 5)])
# hidden: small (brute tries every set of crates on n <= 18)
for n, m in [(12, 30), (15, 100), (18, 1000)]:
    add([(ri(1, m), ri(0, 2 * m)) for _ in range(n)])
add(deadline(17, 1, 10, 0.5, 5))
add([(MAXW, 10**9) for _ in range(3)] + [(MAXW - 1, 0)])
# hidden: medium (brute runs its O(n^2) DP)
add(heavy_bait(3000, 0.6))
# hidden: big
G = 10**9
BIG = [
    (2001, lambda: logspread(MAXN, 0.5, 3, 10**6)),
    (2002, lambda: logspread(MAXN, 0.9, 3, 10**5)),
    (2003, lambda: deadline(MAXN, 1, G, 0.7, 5 * G)),
    (2004, lambda: deadline(MAXN, 1, 10000, 0.9, 10000)),
    (2005, lambda: logspread(MAXN, 0.3, 2, 10**7)),
    (2006, lambda: deadline(MAXN, 1, 100, 0.45, 50)),
    (2007, lambda: heavy_bait(MAXN, 0.5)),
    (2008, lambda: heavy_bait(MAXN, 0.8, 10**4)),
    (2009, lambda: strong_heavy(MAXN, 0.4)),
    (2010, lambda: strong_heavy(MAXN, 0.7, 10**4)),
    (2011, lambda: equal_sum(MAXN, 2 * 10**13)),
    (2012, lambda: mixed(MAXN, 0.5, 0.5, 10**8)),
    (2013, lambda: [(ri(1, MAXW), MAXS) for _ in range(MAXN)]),
    (2014, lambda: [(ri(MAXW // 2, MAXW), ri(0, 10**10)) for _ in range(MAXN)]),
    (2015, lambda: [(ri(1, MAXW), 0) for _ in range(MAXN)]),
    (2016, lambda: sorted(logspread(MAXN, 0.6, 2, 10**6), key=lambda c: c[0] + c[1])),
    (2017, lambda: sorted(mixed(MAXN, 0.4, 0.4, 10**7), key=lambda c: -c[0] - c[1])),
    (2018, lambda: deadline(MAXN - 1, 1, 10000, 0.55, 0) + [(MAXW, MAXS)]),
    (2019, lambda: deadline(MAXN, 1, G, 0.55, 3 * G)),
]
for seed, make in BIG:
    random.seed(seed)
    add(make()[:MAXN])

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
