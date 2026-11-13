# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random
from collections import deque

random.seed(830711)
MAXN, MAXM, MAXQ, MAXK = 1500, 8000, 100000, 10 ** 9
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def add(n, edges, queries):
    assert 1 <= n <= MAXN and 0 <= len(edges) <= MAXM and 1 <= len(queries) <= MAXQ
    for u, v in edges:
        assert 1 <= u <= n and 1 <= v <= n and u != v
    for s, t, k in queries:
        assert 1 <= s <= n and 1 <= t <= n and 0 <= k <= MAXK
    out = [f"{n} {len(edges)} {len(queries)}\n"]
    out.append("".join(f"{u} {v}\n" for u, v in edges))
    out.append("".join("%d %d %d\n" % q for q in queries))
    tests.append("".join(out))


def relabel(n, edges):
    """random town numbers and road order, random direction of each road"""
    p = list(range(1, n + 1))
    random.shuffle(p)
    e = [(p[u - 1], p[v - 1]) if random.random() < 0.5 else (p[v - 1], p[u - 1]) for u, v in edges]
    random.shuffle(e)
    return e


def pdist(n, edges, s):
    """d[2v + p]: shortest walk from s to v with parity p (-1 if none)"""
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    d = [-1] * (2 * n + 2)
    d[2 * s] = 0
    q = deque([2 * s])
    while q:
        x = q.popleft()
        u, p, nd = x >> 1, x & 1, d[x] + 1
        for w in g[u]:
            y = 2 * w + 1 - p
            if d[y] < 0:
                d[y] = nd
                q.append(y)
    return d


def queries(n, edges, count, near_src=6, span=None):
    """random queries: about 30% with k up to 10^9, a few with s = t or tiny k, the others with k up to span;
    then about a quarter of them replaced by queries exactly at / 2 below the shortest walk of each parity
    from a few sources"""
    if span is None:
        span = 2 * n
    rnd = random.random
    qs = []
    for _ in range(count):
        s, t, r = 1 + int(rnd() * n), 1 + int(rnd() * n), rnd()
        if r < 0.3:
            k = int(rnd() * (MAXK + 1))
        elif r < 0.33:
            k = 2 * int(rnd() * 11) + 1 if s == t else int(rnd() * 4)
        else:
            k = int(rnd() * (span + 1))
        qs.append((s, t, k))
    srcs = random.sample(range(1, n + 1), min(n, near_src))
    per = max(1, count // (4 * len(srcs)))
    for s in srcs:
        d = pdist(n, edges, s)
        for _ in range(per):
            t, p = 1 + int(rnd() * n), int(rnd() * 2)
            if d[2 * t + p] >= 0:
                k = d[2 * t + p] - 2 * int(rnd() * 2)       # at the shortest walk or 2 below it
                if k < 0:
                    k = d[2 * t + p]
            else:
                k = 2 * int(rnd() * (span // 2 + 1)) + p
            qs[int(rnd() * count)] = (s, t, k)
    has_road = [False] * (n + 1)
    for u, v in edges:
        has_road[u] = has_road[v] = True
    lonely = [v for v in range(1, n + 1) if not has_road[v]]
    for _ in range(min(50, 5 * len(lonely))):        # towns without roads: s = t with an even k > 0
        v = lonely[int(rnd() * len(lonely))]
        qs[int(rnd() * count)] = (v, v, 2 + 2 * int(rnd() * (MAXK // 2)))
    return qs


def connected_random(n, m):
    """random spanning tree plus random extra roads"""
    e = [(v, ri(1, v - 1)) for v in range(2, n + 1)]
    while len(e) < m:
        u, v = ri(1, n), ri(1, n)
        if u != v:
            e.append((u, v))
    return e


def bipartite_random(n, m):
    """towns 1..a on one side, a+1..n on the other: every road joins the two sides (connected)"""
    a = n // 2
    side = [list(range(1, a + 1)), list(range(a + 1, n + 1))]
    added = [[1], [a + 1]]
    e = [(1, a + 1)]
    rest = [(0, v) for v in side[0][1:]] + [(1, v) for v in side[1][1:]]
    random.shuffle(rest)
    for sd, v in rest:
        other = added[1 - sd]
        e.append((v, other[ri(0, len(other) - 1)]))
        added[sd].append(v)
    while len(e) < m:
        e.append((ri(1, a), ri(a + 1, n)))
    return e


def long_path(n, m, odd_end):
    """a path 1 - 2 - ... - n (multi-edges added along it); with odd_end a triangle closes at the far end"""
    e = [(v, v + 1) for v in range(1, n)]
    if odd_end:
        e.append((n - 2, n))
    while len(e) < m:
        v = ri(1, n - 1)
        e.append((v, v + 1))
    return e


def grid(r, c, extra_odd=0):
    """r x c grid (bipartite); extra_odd diagonal roads (each closes a triangle) near one corner"""
    idx = lambda i, j: i * c + j + 1
    e = []
    for i in range(r):
        for j in range(c):
            if j + 1 < c:
                e.append((idx(i, j), idx(i, j + 1)))
            if i + 1 < r:
                e.append((idx(i, j), idx(i + 1, j)))
    for _ in range(extra_odd):
        i, j = ri(r - 4, r - 2), ri(c - 4, c - 2)
        e.append((idx(i, j), idx(i + 1, j + 1)))
    return e


def components(sizes, kinds, m_total):
    """several components; kind 'b' bipartite (even cycle + chords across), 'o' with an odd cycle,
    'p' a path, 'i' an isolated town"""
    e, base = [], 0
    budget = m_total
    for sz, kind in zip(sizes, kinds):
        vs = list(range(base + 1, base + sz + 1))
        if kind == "i":
            assert sz == 1
        elif kind == "p":
            e += [(vs[i], vs[i + 1]) for i in range(sz - 1)]
        elif kind == "b":
            ev = [(vs[i], vs[(i + 1) % sz]) for i in range(sz)] if sz % 2 == 0 and sz >= 4 else \
                 [(vs[i], vs[i + 1]) for i in range(sz - 1)]
            for _ in range(sz):
                i, j = ri(0, sz - 1), ri(0, sz - 1)
                if (i - j) % 2 == 1:
                    ev.append((vs[i], vs[j]))
            e += ev
        else:
            e += [(vs[i], vs[i + 1]) for i in range(sz - 1)]
            i = ri(0, sz - 3)
            e.append((vs[i], vs[i + 2]))            # one triangle somewhere
            for _ in range(sz // 4):
                i, j = ri(0, sz - 1), ri(0, sz - 1)
                if i != j and (i - j) % 2 == 1:
                    e.append((vs[i], vs[j]))
        base += sz
    while len(e) < budget:                          # repeat existing roads (multi-edges)
        e.append(e[ri(0, len(e) - 1)])
    assert base <= MAXN
    return base, e[:max(budget, 0)] if len(e) > budget else e


# samples
add(5, [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)], [(1, 5, 4), (4, 4, 5), (5, 1, 2)])
add(4, [(1, 2), (2, 1), (3, 4)], [(1, 2, 2), (1, 1, 2), (1, 3, 5), (3, 3, 0)])
add(5, [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)], [(2, 4, 3), (4, 1, 1), (3, 3, 4)])
add(4, [(1, 2), (2, 3), (3, 4), (4, 1)], [(1, 3, 3), (2, 2, 4), (1, 3, 1000000000)])
add(6, [(1, 2), (2, 3), (3, 4), (2, 4), (5, 6)], [(1, 4, 3), (5, 6, 3), (1, 6, 2)])
# hidden: small (brute checks these)
add(2, [(1, 2)], [(1, 2, k) for k in range(6)] + [(1, 1, k) for k in range(6)] + [(2, 2, 999999999)])
add(3, [(1, 2), (2, 3), (3, 1)], [(s, t, k) for s in range(1, 4) for t in range(1, 4) for k in range(4)])
n = 30
e = long_path(n, 35, True)
e = relabel(n, e)
add(n, e, queries(n, e, 300, 5))
n = 40
e = connected_random(n, 60)
e = relabel(n, e)
add(n, e, queries(n, e, 300, 5))
n = 40
e = bipartite_random(n, 70)
e = relabel(n, e)
add(n, e, queries(n, e, 300, 5))
n, e = components([10, 1, 12, 1, 9, 8], "bioipo", 45)
e = relabel(n, e)
add(n, e, queries(n, e, 300, 6))
n = 50
e = grid(5, 10, 1)
e = relabel(n, e)
add(n, e, queries(n, e, 300, 5))
n = 31
e = [(i, i % n + 1) for i in range(1, n + 1)]                    # one odd cycle of 31 towns
e = relabel(n, e)
add(n, e, queries(n, e, 300, 5))
# hidden: big
N, M, Q = MAXN, MAXM, MAXQ
for odd, lone in ((True, 4), (False, 0), (True, 0)):
    e = long_path(N - lone, M, odd)
    e = relabel(N, e)                                           # towns without roads get random numbers
    add(N, e, queries(N, e, Q))
e = relabel(N, connected_random(N - 3, M))
add(N, e, queries(N, e, Q, span=40))
e = connected_random(N, N + 5)
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=200))
e = bipartite_random(N, M)
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=40))
e = relabel(N, bipartite_random(N - 2, N + 200))
add(N, e, queries(N, e, Q, span=300))
e = grid(30, 50)
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=200))
e = relabel(N, grid(30, 49, 1))                                 # 30 towns without roads
add(N, e, queries(N, e, Q, span=200))
e = grid(15, 100, 2)
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=300))
e = [(i, i % 1499 + 1) for i in range(1, 1500)] + [(1499, 1500)]  # odd cycle of 1499 towns + a tail
e += [e[ri(0, 1499)] for _ in range(M - len(e))]
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=3000))
e = [(i, i % 1500 + 1) for i in range(1, 1501)]                   # even cycle of 1500 towns
e += [e[ri(0, 1499)] for _ in range(M - len(e))]
e = relabel(N, e)
add(N, e, queries(N, e, Q, span=3000))
n, e = components([450, 1, 375, 1, 300, 225, 148], "bioipob", M)
e = relabel(n, e)
add(n, e, queries(n, e, Q, span=900))
n, e = components([750, 749, 1], "obi", M)
e = relabel(n, e)
add(n, e, queries(n, e, Q, span=1500))
n, e = components([525, 525, 450], "pob", M)
e = relabel(n, e)
add(n, e, queries(n, e, Q, span=1100))
n, e = components([1] * 750 + [750], "i" * 750 + "o", M)           # many isolated towns
e = relabel(n, e)
add(n, e, queries(n, e, Q, span=1500))
e = long_path(N, 1499 + 50, False) + [(1, 3)]                    # triangle at one end only
e = relabel(N, e)
add(N, e, queries(N, e, Q))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
