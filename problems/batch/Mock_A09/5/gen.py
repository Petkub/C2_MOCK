# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
# Integers only (no floating point): big tests are rebuilt on the students' machines and checked by SHA-256.
import heapq, os, random

random.seed(95017)
_bits = random.getrandbits


def ri(a, b):
    """an integer in [a, b] (b - a < 2^40); the tiny modulo bias does not matter for tests"""
    return a + _bits(48) % (b - a + 1)


MAXN, MAXM, MAXQ, MAXW, MAXX = 50000, 100000, 50000, 10 ** 6, 10 ** 12
tests = []


def stair(n, edges):
    """f[k] = least rain with an umbrella of strength k, k = 0 .. d1(N) (0-indexed vertices, home n-1)"""
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))
    d1 = [-1] * n
    d1[0] = 0
    order = [0]
    for x in order:
        for y, _ in g[x]:
            if d1[y] < 0:
                d1[y] = d1[x] + 1
                order.append(y)
    assert min(d1) >= 0                                  # connected
    INF = 1 << 62
    dn = [INF] * n
    dn[n - 1] = 0
    pq = [(0, n - 1)]
    while pq:
        d, x = heapq.heappop(pq)
        if d != dn[x]:
            continue
        for y, w in g[x]:
            if d + w < dn[y]:
                dn[y] = d + w
                heapq.heappush(pq, (d + w, y))
    D = d1[n - 1]
    f = [dn[0]] * (D + 1)
    for v in range(n):
        if d1[v] <= D:
            f[d1[v]] = min(f[d1[v]], dn[v])
    for k in range(1, D + 1):
        f[k] = min(f[k], f[k - 1])
    assert f[D] == 0
    return f


def queries(f, q, mode="mix"):
    """q tolerances aimed at the steps of f (exact values, one below, inside a gap, the extremes)"""
    D = len(f) - 1
    xs = []
    for _ in range(q):
        if mode == "top":                                # answer >= 1 but X is large
            k = ri(1, min(D, 3))
        else:
            k = ri(0, D)
        c = ri(0, 9)
        if c <= 2:
            x = f[k]
        elif c <= 4:
            x = f[k] - 1
        elif c <= 7:
            x = ri(f[k + 1] if k < D else 0, f[k])
        elif c == 8:
            x = ri(0, f[0] + 5)
        else:
            x = ri(0, 1) * MAXX if mode != "top" else f[1]
        xs.append(max(0, x))
    return xs


def add(n, edges, xs, relabel=True, checked=False):
    m = len(edges)
    assert 2 <= n <= MAXN and n - 1 <= m <= MAXM
    assert 1 <= len(xs) <= MAXQ
    us = [e[0] for e in edges]
    vs = [e[1] for e in edges]
    ws = [e[2] for e in edges]
    assert min(us) >= 0 and min(vs) >= 0 and max(us) < n and max(vs) < n
    assert all(u != v for u, v in zip(us, vs)) and 1 <= min(ws) and max(ws) <= MAXW
    assert len({u * n + v if u < v else v * n + u for u, v in zip(us, vs)}) == m      # simple graph
    assert all(0 <= x <= MAXX for x in xs)
    if not checked:
        stair(n, edges)                                  # asserts connectivity
    lab = list(range(n))
    if relabel:
        mid = lab[1:n - 1]
        random.shuffle(mid)
        lab = [0] + mid + [n - 1]
        edges = edges[:]
        random.shuffle(edges)
    lines = ["%d %d" % (n, m)]
    flip = format(random.getrandbits(m), "b").zfill(m) if relabel else "0" * m
    for (u, v, w), c in zip(edges, flip):
        if c == "1":
            u, v = v, u
        lines.append("%d %d %d" % (lab[u] + 1, lab[v] + 1, w))
    lines.append(str(len(xs)))
    lines += [str(x) for x in xs]
    tests.append("\n".join(lines) + "\n")


def add_q(n, edges, q, mode="mix", relabel=True):
    add(n, edges, queries(stair(n, edges), q, mode), relabel, True)   # stair() asserted connectivity


class G:
    def __init__(self, n):
        self.n, self.e, self.s = n, [], set()

    def edge(self, u, v, w):
        if u == v:
            return False
        key = u * self.n + v if u < v else v * self.n + u
        if key in self.s:
            return False
        self.s.add(key)
        self.e.append((u, v, w))
        return True


def chain_chords(n, K, extra, wlo, whi, factor):
    """a path 0 - 1 - ... - n-1 of light roads, plus chords (i, i+d), d <= K, that save roads but cost more rain"""
    g = G(n)
    for i in range(n - 1):
        g.edge(i, i + 1, ri(wlo, whi))
    while len(g.e) < n - 1 + extra:
        d = ri(2, min(K, n - 1))
        i = ri(0, n - 1 - d)
        g.edge(i, i + d, min(MAXW, d * ri(wlo, whi) * ri(factor[0], factor[1]) // 4 + ri(1, whi)))
    return g.e


def grid(R, C, wmax, rainy_mid):
    """an R x C grid; with rainy_mid the middle rows are much wetter than the border"""
    g = G(R * C)
    for r in range(R):
        for c in range(C):
            for r2, c2 in ((r + 1, c), (r, c + 1)):
                if r2 < R and c2 < C:
                    if rainy_mid and 0 < min(r, r2) and max(r, r2) < R - 1 and 0 < c < C - 1:
                        w = ri(wmax // 2, wmax)
                    else:
                        w = ri(1, wmax // 50 + 1)
                    g.edge(r * C + c, r2 * C + c2, w)
    return g.e


def deep_tree(n, back, extra, span, wmax):
    """vertex v hangs from one of the `back` previous vertices, plus `extra` short local edges"""
    g = G(n)
    for v in range(1, n):
        g.edge(ri(max(0, v - back), v - 1), v, ri(1, wmax))
    while len(g.e) < n - 1 + extra:
        u = ri(0, n - 2)
        g.edge(u, min(n - 1, u + ri(2, span)), ri(1, wmax))
    return g.e


def two_routes(A, B, links, extra_n, wcheap, wdear):
    """a long dry route of A roads and a short wet route of B roads from 0 to home, cross links between them,
    plus extra_n more vertices hanging off as side streets"""
    n = A + B - 1 + extra_n
    home = n - 1
    g = G(n)
    a = [0] + list(range(1, A)) + [home]                     # A roads
    b = [0] + list(range(A, A + B - 1)) + [home]             # B roads
    for i in range(A):
        g.edge(a[i], a[i + 1], ri(1, wcheap))
    for i in range(B):
        g.edge(b[i], b[i + 1], ri(wdear // 2, wdear))
    cnt = 0
    while cnt < links:
        i = ri(1, A - 1)
        j = min(B - 1, max(1, i * B // A + ri(-2, 2)))     # aligned links: no shortcut in roads
        cnt += g.edge(a[i], b[j], ri(1, wdear))
    for v in range(A + B - 1, n - 1):
        g.edge(ri(0, v - 1), v, ri(1, wdear))
    return n, g.e


def random_graph(n, m, wmax):
    g = G(n)
    for v in range(1, n):
        g.edge(ri(0, v - 1), v, ri(1, wmax))
    while len(g.e) < m:
        g.edge(ri(0, n - 1), ri(0, n - 1), ri(1, wmax))
    return g.e


def raw(n, es, xs):
    add(n, [(u - 1, v - 1, w) for u, v, w in es], xs, relabel=False)


# samples
raw(5, [(1, 2, 4), (2, 3, 1), (3, 5, 6), (2, 4, 2), (4, 5, 3)], [8, 0, 9])
raw(6, [(1, 2, 7), (2, 3, 7), (3, 6, 7), (1, 4, 1), (4, 5, 1), (5, 6, 30)], [21, 15, 7, 6])
raw(2, [(1, 2, 1000000)], [999999, 1000000, 0, 1000000000000])
raw(6, [(1, 2, 300000), (2, 3, 300000), (3, 4, 300000), (4, 5, 300000), (5, 6, 300000), (1, 6, 1000000)],
    [1000000, 999999, 600000, 0])

# hidden: small (brute.cpp checks these)
for t in range(10):
    n = ri(5, 10) if t < 7 else ri(25, 45)
    if t % 3 == 0:
        e = chain_chords(n, 3, ri(0, n - 2), 1, 9, (2, 8))
    elif t % 3 == 1:
        e = random_graph(n, ri(n - 1, min(n * (n - 1) // 2, 2 * n)), [5, 30, MAXW][t % 3])
    else:
        e = deep_tree(n, 2, ri(0, min(3, n - 3)), 3, 20)
    add_q(n, e, ri(5, 12))

# hidden: medium
add_q(3000, random_graph(3000, 6000, MAXW), 3000)
add_q(2000, chain_chords(2000, 6, 1500, 1, 1000, (3, 9)), 2000)

# hidden: big (every one has a long BFS distance from 1 to N)
add_q(MAXN, chain_chords(MAXN, 8, MAXM - MAXN + 1, 1, 30, (3, 9)), MAXQ)
add_q(MAXN, chain_chords(MAXN, 20, MAXM - MAXN + 1, 10000, 200000, (4, 6)), MAXQ, "top")
add_q(MAXN, chain_chords(MAXN, 5, MAXM - MAXN + 1, MAXW // 2, MAXW, (4, 4)), MAXQ)      # rain near 5 * 10^10
add_q(MAXN, chain_chords(MAXN, 50, 30000, 1, 100, (2, 12)), MAXQ)
add_q(MAXN, grid(100, 500, MAXW, True), MAXQ)
add_q(MAXN, grid(200, 250, MAXW, False), MAXQ, "top")
add_q(MAXN, grid(50, 1000, 1000, True), MAXQ)
add_q(MAXN, deep_tree(MAXN, 3, MAXM - MAXN + 1, 6, MAXW), MAXQ)
add_q(MAXN, deep_tree(MAXN, 10, 20000, 40, MAXW), MAXQ, "top")
add_q(MAXN, deep_tree(MAXN, 1, MAXM - MAXN + 1, 4, MAXW), MAXQ)
n, e = two_routes(30000, 1500, 2000, MAXN - 31499, 20, MAXW)
add_q(n, e, MAXQ)
n, e = two_routes(45000, 5000, 40000, MAXN - 49999, 3, 5000)
add_q(n, e, MAXQ, "top")
n, e = two_routes(20000, 20000, 50000, MAXN - 39999, MAXW, MAXW)
add_q(n, e, MAXQ)
add_q(MAXN, chain_chords(MAXN, 3, 0, MAXW, MAXW, (4, 4)), MAXQ)                         # one long wet street
add_q(MAXN, chain_chords(MAXN, 12, MAXM - MAXN + 1, 1, MAXW, (1, 3)), MAXQ, "top")
add_q(MAXN, deep_tree(MAXN, 2, 50000, 4, 1), MAXQ)                                      # every road rains 1
add_q(MAXN, grid(250, 200, 50, False), MAXQ)
add_q(MAXN, chain_chords(MAXN, 4, MAXM - MAXN + 1, 300000, 600000, (3, 5)), MAXQ)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
