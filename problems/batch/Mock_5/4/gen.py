# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(540504)
MAXN, MAXM, MAXW = 50_000, 100_000, 10**9
tests = []
_rnd = random.random


def ri(lo, hi):
    return lo + int(_rnd() * (hi - lo + 1))


def shuf(x):
    for i in range(len(x) - 1, 0, -1):
        j = int(_rnd() * (i + 1))
        x[i], x[j] = x[j], x[i]


def add(n, terms, edges):
    """terms = (a, b, c, t); edges = [(u, v, w)], written as given"""
    m = len(edges)
    assert 4 <= n <= MAXN and 3 <= m <= MAXM
    assert len(terms) == 4 and len(set(terms)) == 4 and all(1 <= x <= n for x in terms)
    for u, v, w in edges:
        assert 1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= MAXW
    t = (f"{n} {m}\n" + " ".join(map(str, terms)) + "\n"
         + "".join(f"{u} {v} {w}\n" for u, v, w in edges))
    assert len(t) <= 3_000_000
    tests.append(t)


def relabel(n, terms, edges):
    """random vertex numbers, random edge order and direction; vertices are 0..n-1 here"""
    lab = list(range(1, n + 1))
    shuf(lab)
    es = [(lab[u], lab[v], w) if _rnd() < 0.5 else (lab[v], lab[u], w) for u, v, w in edges]
    shuf(es)
    add(n, tuple(lab[x] for x in terms), es)


def grid(h, w, wfun, drop=0.0):
    """h x w grid, vertex r * w + c; each edge is removed with probability drop (the spine stays)"""
    es = []
    for r in range(h):
        for c in range(w):
            v = r * w + c
            if c + 1 < w and (r == 0 or _rnd() >= drop):
                es.append((v, v + 1, wfun()))
            if r + 1 < h and (c == 0 or _rnd() >= drop):
                es.append((v, v + w, wfun()))
    return es


def corners(h, w, inset, order):
    """four vertices near the corners (top-left, bottom-left, top-right, bottom-right), each moved inwards by up to
    inset rows / columns; order says which of a, b, c, t gets which corner"""
    pts = []
    for (r0, c0) in ((0, 0), (h - 1, 0), (0, w - 1), (h - 1, w - 1)):
        dr, dc = ri(0, inset[0]), ri(0, inset[1])
        r = r0 + dr if r0 == 0 else r0 - dr
        c = c0 + dc if c0 == 0 else c0 - dc
        pts.append(r * w + c)
    return tuple(pts[i] for i in order)


def rand_connected(n, extra, wfun, base=0):
    """random tree on base..base+n-1 plus extra random edges"""
    es = []
    for i in range(1, n):
        es.append((base + int(_rnd() * i), base + i, wfun()))
    for _ in range(extra):
        u, v = ri(0, n - 1), ri(0, n - 1)
        if u != v:
            es.append((base + u, base + v, wfun()))
    return es


def unif(lo, hi):
    return lambda: ri(lo, hi)


# order of the corners (TL, BL, TR, BR) -> (a, b, c, t): the left pair and the right pair belong together
PAIR_AB = (0, 1, 2, 3)      # {a, b} left, {c, t} right
PAIR_AC = (0, 2, 1, 3)      # {a, c} left, {b, t} right
PAIR_AT = (0, 2, 3, 1)      # {a, t} left, {b, c} right

def clusters(sizes, links, wf, lw):
    """random connected clusters of the given sizes; links: (i, j, k) = k roads between clusters i and j"""
    es, base = [], [0]
    for sz in sizes:
        es += rand_connected(sz, sz // 2, wf, base=base[-1])
        base.append(base[-1] + sz)
    for i, j, k in links:
        for _ in range(k):
            es.append((ri(base[i], base[i + 1] - 1), ri(base[j], base[j + 1] - 1), lw()))
    return base, es


def pick(base, cl):
    """distinct random vertices, the k-th one inside cluster cl[k]"""
    while True:
        pts = tuple(ri(base[c], base[c + 1] - 1) for c in cl)
        if len(set(pts)) == len(pts):
            return pts


# samples
add(6, (1, 2, 3, 4), [(1, 5, 3), (2, 5, 2), (3, 5, 4), (5, 4, 5), (3, 6, 1), (6, 4, 5)])
add(5, (1, 2, 5, 3), [(1, 2, 4), (2, 3, 1), (3, 1, 2), (4, 5, 3)])
add(4, (1, 2, 3, 4), [(1, 4, 5), (2, 4, 3), (1, 4, 2), (3, 4, 1)])
add(5, (1, 2, 3, 4), [(1, 5, MAXW), (2, 5, MAXW), (5, 3, MAXW), (4, 5, MAXW)])
add(5, (3, 4, 5, 2), [(1, 2, 6), (1, 3, 6), (1, 4, 7), (2, 5, 9), (1, 5, 6), (3, 1, 2)])
# hidden: small
add(4, (4, 3, 2, 1), [(1, 2, 5), (2, 3, 5), (3, 4, 5)])
add(6, (1, 2, 3, 4), [(1, 5, 1), (5, 2, 1), (3, 6, 1), (6, 4, 1), (1, 2, 1), (3, 4, 1)])         # two parts: -1
for n, extra, wmax in ((8, 6, 9), (12, 10, 20), (150, 100, 10**6)):
    es = rand_connected(n, extra, unif(1, wmax))
    relabel(n, tuple(random.sample(range(n), 4)), es)
relabel(48, corners(6, 8, (1, 2), PAIR_AC), grid(6, 8, unif(1, 9), 0.2))
base, es = clusters((40, 40), ((0, 1, 2),), unif(1, 50), unif(200, 400))
pts = pick(base, (0, 1, 1, 0))
relabel(80, pts, es)
relabel(300, corners(10, 30, (2, 4), PAIR_AT), grid(10, 30, unif(1, 50)))
relabel(250, (0, 249, 120, 60), [(i, i + 1, ri(1, MAXW)) for i in range(249)])
# hidden: maximum size
# long grids with the four friends near the corners: the left pair and the right pair belong together
for (h, w), pairing, inset, wf, drop in (
        ((50, 1000), PAIR_AC, (5, 30), unif(1, 10**6), 0.0),
        ((50, 1000), PAIR_AT, (10, 100), unif(1, 30), 0.0),
        ((50, 1000), PAIR_AB, (0, 0), unif(1, 1000), 0.1),
        ((100, 500), PAIR_AT, (20, 60), unif(1, 1000), 0.0),
        ((100, 500), PAIR_AC, (10, 40), unif(1, 1000), 0.1),
        ((20, 2500), PAIR_AT, (3, 200), unif(MAXW - 10**6, MAXW), 0.0),
        ((25, 2000), PAIR_AC, (4, 300), unif(1, 10**6), 0.0),
        ((40, 1250), PAIR_AT, (8, 150), unif(1, 100), 0.05),
        ((223, 224), PAIR_AC, (40, 40), unif(1, 10**6), 0.0)):
    relabel(h * w, corners(h, w, inset, pairing), grid(h, w, wf, drop))


# two clusters joined by a few expensive roads
for pairing in (PAIR_AT, PAIR_AB, PAIR_AC):
    h = MAXN // 2
    base, es = clusters((h, h), ((0, 1, 5),), unif(1, 1000), unif(10**5, 10**6))
    pts = pick(base, (0, 0, 1, 1))
    relabel(2 * h, tuple(pts[i] for i in pairing), es)
# three clusters in a row: two friends in the first, the others in the second and the third
base, es = clusters((20_000, 10_000, 20_000), ((0, 1, 4), (1, 2, 4)), unif(1, 1000), unif(10**5, 10**6))
pts = pick(base, (0, 0, 1, 2))
relabel(MAXN, (pts[0], pts[2], pts[3], pts[1]), es)
# a very long grid of 5 rows: a and t near one column, b and c near another
h, w = 5, MAXN // 5
p0, p1 = ri(0, w // 3), ri(2 * w // 3, w - 1)
relabel(h * w, (p0, 4 * w + p1 - ri(0, 9), p1, 4 * w + p0 + ri(0, 9)), grid(h, w, unif(1, 10**6)))
# a long path, all roads at the maximum
pos = random.sample(range(MAXN), 4)
relabel(MAXN, tuple(pos), [(i, i + 1, MAXW) for i in range(MAXN - 1)])
# a deep tree (every road is needed)
es = [(ri(max(0, i - 3), i - 1), i, ri(1, 10**6)) for i in range(1, MAXN)]
relabel(MAXN, tuple(random.sample(range(MAXN), 4)), es)
# random sparse graphs
es = rand_connected(MAXN, MAXN, unif(1, 10**6))
relabel(MAXN, tuple(random.sample(range(MAXN), 4)), es)
# a square grid, the friends anywhere
h, w = 223, 224
relabel(h * w, tuple(random.sample(range(h * w), 4)), grid(h, w, unif(1, 1000), 0.2))
# two components: c cannot reach the concert
base, es = clusters((MAXN // 2, MAXN // 2), (), unif(1, 10**6), None)
pts = pick(base, (0, 0, 1, 0))
relabel(MAXN, pts, es)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
