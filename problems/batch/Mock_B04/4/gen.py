# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer is the best "highest point": at a region v (2 * max(up[v], down[v])) or during the flight over an
# edge u -> v (up[u] + w + down[v] when |up[u] - down[v]| <= w), with up / down from two max-relaxing Dijkstras.
# Big tests: n = 80000 (an O(n^2) Dijkstra dies), edges written in random order and random orientation with
# random region labels (so checking an edge in one direction only fails), weights on the scale of the altitude
# differences (edge peaks matter), and ridges of altitude near 10^9 (answers above 2^31).
import os, random

random.seed(20231)
rnd = random.random
MAXN, MAXM, MAXA, MAXW = 80000, 100000, 10 ** 9, 10 ** 6
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add_raw(n, a, edges):
    """a: list of n altitudes (1-based regions in order), edges: list of (u, v, w), already labelled 1..n"""
    m = len(edges)
    assert 2 <= n <= MAXN and n - 1 <= m <= MAXM and len(a) == n
    assert a[0] == 0 and a[-1] == 0 and min(a) >= 0 and max(a) <= MAXA
    us, vs, ws = zip(*edges)
    assert min(us) >= 1 and min(vs) >= 1 and max(us) <= n and max(vs) <= n
    assert min(ws) >= 1 and max(ws) <= MAXW and all(map(int.__ne__, us, vs))
    assert len({u * (n + 1) + v if u < v else v * (n + 1) + u for u, v in zip(us, vs)}) == m
    adj = [[] for _ in range(n + 1)]
    for u, v in zip(us, vs):
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * (n + 1)
    seen[1] = True
    st = [1]
    while st:
        for y in adj[st.pop()]:
            if not seen[y]:
                seen[y] = True
                st.append(y)
    assert all(seen[1:])
    lines = [f"{n} {m}", " ".join(map(str, a))] + ["%d %d %d" % e for e in edges]
    tests.append("\n".join(lines) + "\n")


def add(n, a, edges):
    """internal ids 0..n-1 (0 = start, n-1 = landing region): random labels and orientation"""
    mid = list(range(2, n))
    random.shuffle(mid)
    lab = [1] + mid + [n]
    alt = [0] * n
    for i in range(n):
        alt[lab[i] - 1] = a[i]
    out = [(lab[u], lab[v], w) if rnd() < 0.5 else (lab[v], lab[u], w) for u, v, w in edges]
    add_raw(n, alt, out)


class G:
    def __init__(self, n):
        self.n, self.e, self.s = n, [], set()

    def edge(self, u, v, w):
        if u == v:
            return False
        k = u * self.n + v if u < v else v * self.n + u
        if k in self.s:
            return False
        self.s.add(k)
        self.e.append((u, v, w))
        return True


def tree_plus(n, m, wf, span):
    """random tree (parent within span ids before) plus random extra edges between ids at most span apart"""
    g = G(n)
    for i in range(1, n):
        g.edge(i, max(0, i - 1 - int(rnd() * span)), wf())
    while len(g.e) < m:
        u = int(rnd() * n)
        v = u + int(rnd() * (2 * span + 1)) - span
        if 0 <= v < n:
            g.edge(u, v, wf())
    return g.e


def grid(r, c, m, wf):
    """r x c grid (0 = a corner, n-1 = the opposite corner): a random spanning tree of the grid edges plus
    more grid edges up to m"""
    n = r * c
    cand = []
    for i in range(r):
        for j in range(c):
            if j + 1 < c:
                cand.append((i * c + j, i * c + j + 1))
            if i + 1 < r:
                cand.append((i * c + j, (i + 1) * c + j))
    random.shuffle(cand)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    g, rest = G(n), []
    for u, v in cand:
        fu, fv = find(u), find(v)
        if fu != fv:
            par[fu] = fv
            g.edge(u, v, wf())
        else:
            rest.append((u, v))
    for u, v in rest[:m - len(g.e)]:
        g.edge(u, v, wf())
    return g.e


def layers(n, m, wf):
    """layer 0 = {0}, last layer = {n-1}, the rest split into layers of random widths, edges only between
    neighbouring layers or inside a layer"""
    ids = list(range(1, n - 1))
    cuts = sorted(random.sample(range(1, n - 2), max(1, (n - 2) // 400)))
    lay = [[0]] + [ids[a:b] for a, b in zip([0] + cuts, cuts + [n - 2])] + [[n - 1]]
    g = G(n)
    for k in range(1, len(lay)):
        for v in lay[k]:
            p = lay[k - 1]
            g.edge(v, p[int(rnd() * len(p))], wf())
    while len(g.e) < m:
        k = ri(1, len(lay) - 1)
        p, q = lay[k - 1], lay[k] if rnd() < 0.8 else lay[k - 1]
        g.edge(p[int(rnd() * len(p))], q[int(rnd() * len(q))], wf())
    return g.e, lay


def unif(lo, hi):
    k = hi - lo + 1
    return lambda: lo + int(rnd() * k)


def alts_rand(n, A, zero=0.0):
    a = [0 if rnd() < zero else ri(0, A) for _ in range(n)]
    a[0] = a[-1] = 0
    return a


def alts_mountain(n, A, noise):
    """high in the middle of the id range, low at both ends"""
    a = []
    for i in range(n):
        h = A * (1 - abs(2 * i / (n - 1) - 1))
        a.append(max(0, min(MAXA, int(h) + ri(-noise, noise))))
    a[0] = a[-1] = 0
    return a


def alts_ridge(n, A, lo, hi, base):
    """ids in [lo, hi) get altitude near A, the others at most base"""
    a = [ri(A - A // 50, A) if lo <= i < hi else ri(0, base) for i in range(n)]
    a[0] = a[-1] = 0
    return a


# ---- samples
add_raw(4, [0, 3, 6, 0], [(1, 2, 2), (2, 4, 4), (1, 3, 1), (3, 4, 2)])
add_raw(5, [0, 4, 2, 7, 0], [(1, 2, 1), (2, 5, 3), (1, 3, 3), (3, 4, 1), (4, 5, 1), (2, 3, 2)])
add_raw(2, [0, 0], [(1, 2, 5)])
add_raw(6, [0, 9, 1, 4, 8, 0], [(1, 2, 3), (1, 3, 2), (3, 4, 4), (4, 6, 3), (2, 5, 1), (5, 6, 2), (3, 5, 6)])
add_raw(4, [0, 20, 5, 0], [(1, 2, 3), (2, 4, 3), (1, 3, 15), (3, 4, 24)])

# ---- hidden: small (brute checks these)
add(2, [0, 0], [(0, 1, 1)])
add(3, [0, 7, 0], [(0, 1, 2), (1, 2, 3)])
for n, m, A, W in [(6, 8, 8, 4), (8, 12, 12, 3), (9, 14, 6, 6), (12, 20, 20, 2), (10, 9, 15, 5)]:
    add(n, alts_rand(n, A, 0.2), tree_plus(n, m, unif(1, W), 3))
add(12, alts_mountain(12, 14, 2), grid(3, 4, 15, unif(1, 4)))

# ---- hidden: big (n = 80000)
N, M = MAXN, MAXM
add(N, alts_rand(N, 10 ** 6), tree_plus(N, M, unif(1, 10 ** 6), 50))
add(N, alts_rand(N, 3000, 0.3), tree_plus(N, M, unif(1, 2000), 20))
add(N, alts_mountain(N, MAXA, 10 ** 6), tree_plus(N, M, unif(1, 10 ** 6), 5))           # long, peak 10^9
add(N, alts_mountain(N, 5 * 10 ** 7, 3000), tree_plus(N, M, unif(1, 1000), 3))
add(N, alts_ridge(N, MAXA, 30000, 31000, 10 ** 6), tree_plus(N, M, unif(1, 10 ** 6), 30))   # ridge 10^9
add(N, alts_ridge(N, 10 ** 8, 40000, 40100, 1000), tree_plus(N, M, unif(1, 500), 200))
add(N, alts_mountain(N, 10 ** 6, 50), grid(200, 400, M, unif(1, 300)))
add(N, alts_rand(N, 600), grid(400, 200, M, unif(1, 1000)))
add(N, alts_ridge(N, MAXA, 40000, 40500, 10 ** 6), grid(160, 500, M, unif(1, 10 ** 6)))
e, lay = layers(N, M, unif(1, 2000))
add(N, alts_rand(N, 2000 * len(lay) // 4), e)
e, lay = layers(N, M, unif(1, 10 ** 6))
a = [ri(0, 10 ** 6) for _ in range(N)]
for v in lay[len(lay) // 2]:
    a[v] = ri(MAXA - 10 ** 6, MAXA)
a[0] = a[-1] = 0
add(N, a, e)                                                                            # every route crosses 10^9
add(N, [0] * N, tree_plus(N, M, unif(1, 10 ** 6), 1000))                                # plain shortest path
add(N, alts_rand(N, 10 ** 6, 0.5), tree_plus(N, M, unif(10 ** 6 - 10, 10 ** 6), 40))
add(N, alts_rand(N, 50, 0.0), tree_plus(N, M, unif(1, 30), 10))
add(N, alts_mountain(N, 2 * 10 ** 5, 1), tree_plus(N, N - 1, unif(1, 5), 1))            # a path
add(N, alts_mountain(N, MAXA, 0), tree_plus(N, M, unif(1, 10 ** 6), 2))
add(N, alts_rand(N, MAXA, 0.9), tree_plus(N, M, unif(1, 10 ** 6), 100))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
print([len(t) for t in tests], sum(len(t) for t in tests))
assert sum(len(t) for t in tests) <= 40 * 10 ** 6
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
