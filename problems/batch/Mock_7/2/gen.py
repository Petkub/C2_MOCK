# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(730202)
MAXN, MAXM, MAXH, MAXW = 60000, 60000, 10 ** 9, 10 ** 6
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(n, h, edges):
    m = len(edges)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM and len(h) == n
    assert all(0 <= x <= MAXH for x in h)
    if edges:
        us, vs, ws = zip(*edges)
        assert 1 <= min(us) and max(us) <= n and 1 <= min(vs) and max(vs) <= n
        assert 1 <= min(ws) and max(ws) <= MAXW and all(map(int.__ne__, us, vs))
    lines = [f"{n} {m}", " ".join(map(str, h))] + [f"{u} {v} {w}" for u, v, w in edges]
    tests.append("\n".join(lines) + "\n")


class Graph:
    """towns 0..n-1 while building; emit() relabels them (start -> 1, goal -> N, the rest shuffled)"""

    def __init__(self):
        self.h = []
        self.e = []

    def node(self, alt):
        self.h.append(alt)
        return len(self.h) - 1

    def edge(self, u, v, w):
        assert u != v
        self.e.append((u, v, w))

    def room(self):
        return min(MAXN - len(self.h), MAXM - len(self.e))

    def emit(self, start, goal):
        n = len(self.h)
        rest = [v for v in range(n) if v != start and v != goal]
        random.shuffle(rest)
        lab = [0] * n
        lab[start] = 1
        if goal != start:
            lab[goal] = n
        for i, v in enumerate(rest):
            lab[v] = i + 2
        h = [0] * n
        for v in range(n):
            h[lab[v] - 1] = self.h[v]
        # roads in the order of their (random) first label: the build order would show the structure
        out = sorted((lab[u], lab[v], w) if rnd() < 0.5 else (lab[v], lab[u], w) for u, v, w in self.e)
        add(n, h, out)


def gadgets(g, a, k, low, mid):
    """k gadgets in a row from hub a: a - x - b with x low but long, a - y - b with y higher but short;
    returns the list of towns used and the last hub"""
    used = [a]
    for _ in range(k):
        x = g.node(ri(*low))
        y = g.node(ri(*mid))
        b = g.node(ri(*low))
        s = ri(1, MAXW // 3)
        lng = ri(s + 1, MAXW)
        g.edge(a, x, ri(1, lng))
        g.edge(x, b, lng)
        g.edge(a, y, ri(1, s))
        g.edge(y, b, s)
        used += [x, y, b]
        a = b
    return used, a


def bumps(g, pool, cnt, hr, bridge, wr=(1, MAXW)):
    """cnt towns with altitudes in hr: a dead end off a town of pool, or (bridge) a short link between two"""
    for _ in range(cnt):
        if g.room() < 2:
            break
        v = g.node(ri(*hr))
        a = pool[int(rnd() * len(pool))]
        g.edge(a, v, ri(*wr))
        if bridge:
            b = pool[int(rnd() * len(pool))]
            if b != a:
                g.edge(v, b, ri(*wr))


def chain_test(k, nb, bridge=False, peak_at_goal=False, hmax=MAXH, decoy=True):
    """gadget chain, bumps between the low and the peak altitude, then the mandatory peak next to the goal"""
    g = Graph()
    H = ri(hmax * 3 // 4, hmax)
    L1 = ri(H // 4, H // 2)
    s = g.node(ri(0, L1))
    used, end = gadgets(g, s, k, (0, L1), (L1 + 1, H))
    if peak_at_goal:
        t = g.node(H)
        g.edge(end, t, ri(1, MAXW))
    else:
        p = g.node(H)
        t = g.node(ri(0, L1))
        g.edge(end, p, ri(1, MAXW))
        g.edge(p, t, ri(1, MAXW))
    if decoy and H < MAXH:      # short routes over towns higher than the peak
        for _ in range(3):
            d = g.node(ri(H + 1, MAXH))
            g.edge(s, d, 1)
            g.edge(d, t, 1)
    # bridges must not skip the peak: they only join towns of the chain
    bumps(g, used, nb, (L1 + 1, H), bridge, (MAXW // 2, MAXW))
    g.emit(s, t)


def basin_test(nbasin, mbasin, nb, npass, low=None, hmax=MAXH, wmax=MAXW, bridge=True):
    """a random low basin around town 1; bumps (bridges/dead ends) above the basin; the goal is reached only
    over a few passes higher than everything in the basin"""
    g = Graph()
    if low is None:
        low = hmax // 3
    H = ri(low + 1, hmax - 1)
    base = [g.node(ri(0, low)) for _ in range(nbasin)]

    def road(u, v):
        # the lower a road's towns, the longer it tends to be
        top = max(g.h[u], g.h[v])
        g.edge(u, v, min(wmax, max(1, int(wmax * rnd() * (1.05 - top / (low + 1))))))

    for v in range(1, nbasin):
        road(base[int(rnd() * v)], base[v])
    for _ in range(mbasin - (nbasin - 1)):
        u, v = base[int(rnd() * nbasin)], base[int(rnd() * nbasin)]
        if u != v:
            road(u, v)
    t = g.node(ri(0, low))
    for i in range(npass):
        p = g.node(H if i == 0 else ri(H, hmax))
        g.edge(base[int(rnd() * nbasin)], p, ri(1, wmax))
        g.edge(p, t, ri(1, wmax))
    for _ in range(2):          # short routes over towns higher than every pass
        d = g.node(ri(H + 1, hmax) if npass == 1 else hmax)
        g.edge(base[0], d, 1)
        g.edge(d, t, 1)
    bumps(g, base, nb, (low + 1, H), bridge, (1, max(1, wmax // 20)))
    g.emit(base[0], t)


def mountain(rows, cols, k_extra, slope, hills=12):
    """a grid of valleys and ridges rising towards the goal corner, plus a few random long roads"""
    g = Graph()
    top = MAXH // 2
    hl = [(ri(0, rows - 1), ri(0, cols - 1), ri(1, top // hills)) for _ in range(hills)]
    ids = []
    for r in range(rows):
        row = []
        for c in range(cols):
            val = ri(0, MAXH // 50) + slope * (r + c) // (rows + cols)
            for hr, hc, hv in hl:
                val += hv * 30 // (30 + abs(hr - r) + abs(hc - c))
            row.append(g.node(min(MAXH, val)))
        ids.append(row)
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                g.edge(ids[r][c], ids[r][c + 1], ri(1, 100) if rnd() < 0.5 else ri(1, MAXW))
            if r + 1 < rows:
                g.edge(ids[r][c], ids[r + 1][c], ri(1, 100) if rnd() < 0.5 else ri(1, MAXW))
    n = len(g.h)
    for _ in range(k_extra):
        u, v = int(rnd() * n), int(rnd() * n)
        if u != v:
            g.edge(u, v, ri(1, MAXW))
    # the two corners lie in low valleys
    g.h[ids[0][0]] = ri(0, MAXH // 50)
    g.h[ids[rows - 1][cols - 1]] = ri(0, MAXH // 50)
    g.emit(ids[0][0], ids[rows - 1][cols - 1])


def split_test(n, m, hmax=MAXH, alone=False):
    """1 and N in different parts (alone: N has no road at all)"""
    g = Graph()
    for _ in range(n):
        g.node(ri(0, hmax))
    g.h[0] = g.h[n - 1] = 0
    half = n - 1 if alone else n // 2
    while len(g.e) < m:
        u = int(rnd() * n)
        v = int(rnd() * half) if u < half else half + int(rnd() * (n - half))
        if u != v:
            g.edge(u, v, ri(1, MAXW))
    g.emit(0, n - 1)


# samples
add(5, [3, 5, 2, 7, 1], [(1, 2, 2), (2, 5, 2), (1, 4, 1), (4, 5, 1), (1, 3, 4), (3, 5, 9), (1, 5, 15)])
add(4, [1, 1, 1, 1], [(1, 2, 5), (3, 4, 5), (2, 1, 3)])
add(1, [7], [])
add(4, [4, 2, 6, 9], [(1, 2, 3), (2, 4, 4), (1, 3, 1), (3, 4, 1), (2, 4, 2)])
add(5, [5, 0, 8, 2, 4], [(1, 2, 4), (2, 4, 2), (4, 5, 3), (1, 3, 1), (3, 5, 1)])
# hidden: small (brute checks these)
add(1, [MAXH], [])
add(5, [0, 1, 5, 2, 9], [(1, 2, 10), (2, 4, 10), (1, 3, 1), (3, 4, 1), (4, 5, 1)])
chain_test(10, 20, bridge=True, peak_at_goal=True)
basin_test(150, 300, 100, 4, hmax=1000)
mountain(12, 15, 30, MAXH // 3)
# hidden: big
chain_test(10000, 20000)
chain_test(10000, 10000, bridge=True)
chain_test(8000, 26000, bridge=True, peak_at_goal=True)
chain_test(14990, 0, hmax=10 ** 6)
chain_test(12000, 12000, bridge=True)
chain_test(6000, 40000)
chain_test(9000, 25000, bridge=True, decoy=False)
basin_test(20000, 30000, 15000, 5)
basin_test(12000, 26000, 15000, 2, wmax=1000)
basin_test(25000, 35000, 12000, 3, bridge=False)
basin_test(20000, 30000, 15000, 5, hmax=40, low=10)
basin_test(20000, 25000, 17000, 2, hmax=MAXH, low=MAXH - 30000)
basin_test(30000, 45000, 7000, 1)
mountain(200, 150, 0, MAXH // 2)
mountain(150, 150, 10000, MAXH * 2 // 3, hills=6)
mountain(240, 120, 2000, MAXH // 2, hills=20)
split_test(MAXN, MAXM)
split_test(MAXN // 2, MAXM, alone=True)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
