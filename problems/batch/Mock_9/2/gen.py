# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import heapq, os, random

random.seed(540504)
MAXN, MAXM, MAXW = 400, 20_000, 10**9
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


def pad(es, m, extra=(0, 10)):
    """add heavier parallel copies of random roads until there are m roads"""
    es = list(es)
    k = len(es)
    while len(es) < m:
        u, v, w = es[int(_rnd() * k)]
        es.append((u, v, min(MAXW, w + ri(*extra))))
    return es


def shortcuts(n, terms, es):
    """for every two friends / concert junctions p, q: a direct road slightly cheaper than their shortest path
    (when it fits the limits), so every shortest path between two of them is that road; this beats the greedy
    ways that join the four junctions one by one along shortest paths (their tree has no other branching point)"""
    adj = [[] for _ in range(n)]
    for u, v, w in es:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = []
    for s0 in terms:
        d = [None] * n
        d[s0] = 0
        pq = [(0, s0)]
        while pq:
            dv, v = heapq.heappop(pq)
            if dv > d[v]:
                continue
            for u, w in adj[v]:
                if d[u] is None or dv + w < d[u]:
                    d[u] = dv + w
                    heapq.heappush(pq, (dv + w, u))
        dist.append(d)
    es = list(es)
    for i in range(4):
        for j in range(i + 1, 4):
            d = dist[i][terms[j]]
            if d is None or d < 2:
                continue
            w = d - 1 - ri(0, d // 200)
            if w <= MAXW:
                es.append((terms[i], terms[j], w))
    assert len(es) <= MAXM
    return es


def hshape(n, m, legs, bridge, legw, noisew, order):
    """an H: junction 0 with legs to two friends / the concert, junction 1 with legs to the other two, a path of
    `bridge` roads between the junctions; legs[k] roads per leg, light roads legw; the other vertices and roads are
    heavy noise (noisew) that no cheapest set uses; returns (terms, edges) with vertices 0..n-1"""
    es, nxt = [], [2]

    def path(u, k):
        for _ in range(k):
            es.append((u, nxt[0], legw()))
            u = nxt[0]
            nxt[0] += 1
        return u

    ends = [path(0, legs[0]), path(0, legs[1]), path(1, legs[2]), path(1, legs[3])]
    u = 0
    for i in range(bridge - 1):
        es.append((u, nxt[0], legw()))
        u = nxt[0]
        nxt[0] += 1
    es.append((u, 1, legw()))
    used = nxt[0]
    assert used <= n
    for v in range(used, n):
        es.append((ri(0, v - 1), v, noisew()))
    while len(es) < m - 6:
        u, v = ri(0, n - 1), ri(0, n - 1)
        if u != v:
            es.append((u, v, noisew()))
    terms = tuple(ends[i] for i in order)
    return terms, shortcuts(n, terms, es)


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
for n, extra, wmax, sc in ((8, 6, 9, False), (12, 10, 20, True), (60, 40, 10**6, True)):
    es = rand_connected(n, extra, unif(1, wmax))
    pts = tuple(random.sample(range(n), 4))
    relabel(n, pts, shortcuts(n, pts, es) if sc else es)
pts = corners(6, 8, (1, 2), PAIR_AC)
relabel(48, pts, shortcuts(48, pts, grid(6, 8, unif(1, 9), 0.2)))
base, es = clusters((40, 40), ((0, 1, 2),), unif(1, 50), unif(200, 400))
pts = pick(base, (0, 1, 1, 0))
relabel(80, pts, shortcuts(80, pts, es))
pts, es = hshape(150, 400, (12, 15, 10, 14), 8, unif(1, 100), unif(10**4, 10**5), PAIR_AC)
relabel(150, pts, es)
# hidden: maximum size (N = 400)
# grids with the four friends near the corners: the left pair and the right pair belong together
for (h, w), pairing, inset, wf, drop, m in (
        ((10, 40), PAIR_AC, (1, 8), unif(1, 10**6), 0.0, MAXM),
        ((10, 40), PAIR_AT, (2, 10), unif(1, 30), 0.0, 0),
        ((8, 50), PAIR_AB, (0, 0), unif(1, 1000), 0.1, MAXM),
        ((20, 20), PAIR_AT, (4, 4), unif(1, 1000), 0.0, 5000),
        ((16, 25), PAIR_AC, (3, 5), unif(1, 1000), 0.1, MAXM),
        ((4, 100), PAIR_AT, (0, 20), unif(MAXW - 10**6, MAXW), 0.0, MAXM),
        ((5, 80), PAIR_AC, (1, 15), unif(1, 10**6), 0.0, 12_000),
        ((8, 50), PAIR_AT, (2, 10), unif(1, 100), 0.05, MAXM),
        ((20, 20), PAIR_AC, (6, 6), unif(1, 10**6), 0.0, MAXM)):
    es = grid(h, w, wf, drop)
    pts = corners(h, w, inset, pairing)
    relabel(h * w, pts, shortcuts(h * w, pts, pad(es, m - 6, (0, 1000)) if m else es))
# two dense clusters joined by a few expensive roads
for pairing in (PAIR_AT, PAIR_AB, PAIR_AC):
    base, es = clusters((200, 200), ((0, 1, 5),), unif(1, 1000), unif(10**4, 10**5))
    for _ in range(MAXM - 6 - len(es)):             # more roads inside the clusters
        c = ri(0, 1)
        u, v = ri(base[c], base[c + 1] - 1), ri(base[c], base[c + 1] - 1)
        if u != v:
            es.append((u, v, ri(500, 5000)))
    pts = pick(base, (0, 0, 1, 1))
    pts = tuple(pts[i] for i in pairing)
    relabel(MAXN, pts, shortcuts(MAXN, pts, es))
# three clusters in a row: two friends in the first, the others in the second and the third
base, es = clusters((160, 80, 160), ((0, 1, 4), (1, 2, 4)), unif(1, 1000), unif(10**5, 10**6))
pts = pick(base, (0, 0, 1, 2))
pts = (pts[0], pts[2], pts[3], pts[1])
relabel(MAXN, pts, shortcuts(MAXN, pts, pad(es, MAXM - 6, (0, 10**6))))
# a sparse H: long legs, a long bridge
pts, es = hshape(MAXN, 700, (30, 35, 25, 40), 100, unif(1, 10**6), unif(10**8, MAXW), PAIR_AC)
relabel(MAXN, pts, es)
# a long path, all roads at the maximum (the largest answer)
pos = random.sample(range(MAXN), 4)
relabel(MAXN, tuple(pos), pad([(i, i + 1, MAXW) for i in range(MAXN - 1)], MAXM))
# a deep tree (every road is needed)
es = [(ri(max(0, i - 3), i - 1), i, ri(1, 10**6)) for i in range(1, MAXN)]
relabel(MAXN, tuple(random.sample(range(MAXN), 4)), es)
# random dense graphs
es = rand_connected(MAXN, MAXM - MAXN + 1 - 6, unif(1, 10**6))
pts = tuple(random.sample(range(MAXN), 4))
relabel(MAXN, pts, shortcuts(MAXN, pts, es))
# H shapes hidden among heavy roads
pts, es = hshape(MAXN, MAXM, (40, 45, 50, 42), 60, unif(1, 2 * 10**5), unif(10**8, MAXW), PAIR_AT)
relabel(MAXN, pts, es)
pts, es = hshape(MAXN, MAXM, (70, 60, 65, 75), 5, unif(1, 1000), unif(10**6, 10**7), PAIR_AB)
relabel(MAXN, pts, es)
# a spider: four long legs from a hub to the four friends, plus direct roads between the friends that are
# slightly cheaper than going through the hub
legs, es, ends, lens = [99, 100, 100, 100], [], [], []
v = 1
for k in legs:
    prev, tot = 0, 0
    for _ in range(k):
        w = ri(1, 10**6)
        es.append((prev, v, w))
        prev, tot = v, tot + w
        v += 1
    ends.append(prev)
    lens.append(tot)
for i in range(4):
    for j in range(i + 1, 4):
        es.append((ends[i], ends[j], lens[i] + lens[j] - ri(1, 1000)))
relabel(v, (ends[1], ends[2], ends[3], ends[0]), pad(es, MAXM, (10**6, 10**7)))
# two components: c cannot reach the concert
base, es = clusters((MAXN // 2, MAXN // 2), (), unif(1, 10**6), None)
pts = pick(base, (0, 0, 1, 0))
relabel(MAXN, pts, pad(es, MAXM))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
