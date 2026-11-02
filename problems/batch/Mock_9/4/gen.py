# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(5202)
MAXN = 100000
MAXM = 100000
MAXW = 10 ** 9
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def add(n, edges, shuffle=True):
    """edges: list of (a, b, w); home stays vertex 1, the other labels are permuted when shuffle is set"""
    m = len(edges)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM
    if shuffle:
        perm = list(range(2, n + 1))
        random.shuffle(perm)
        lab = [0, 1] + perm
        edges = [(lab[a], lab[b], w) if random.random() < 0.5 else (lab[b], lab[a], w) for a, b, w in edges]
        random.shuffle(edges)
    for a, b, w in edges:
        assert 1 <= a <= n and 1 <= b <= n and a != b and 1 <= w <= MAXW
    tests.append(f"{n} {m}\n" + "".join(f"{a} {b} {w}\n" for a, b, w in edges))


def tree_edges(lo, hi, wlo, whi, depth=None):
    """random tree on vertices lo..hi (each vertex hangs from a random earlier one, or from one of the last
    `depth` ones to make it deep)"""
    e = []
    for v in range(lo + 1, hi + 1):
        p = ri(lo, v - 1) if depth is None else ri(max(lo, v - depth), v - 1)
        e.append((p, v, ri(wlo, whi)))
    return e


def extra_edges(lo, hi, cnt, wlo, whi):
    e = []
    for _ in range(cnt):
        a = ri(lo, hi)
        b = ri(lo, hi)
        while b == a:
            b = ri(lo, hi)
        e.append((a, b, ri(wlo, whi)))
    return e


def gadget_size(trap, pair):
    """(vertices, roads) used by gadgets()"""
    return (30 if trap else 0) + (1 if pair is not None else 0), (61 if trap else 0) + (2 if pair is not None else 0)


def gadgets(nxt, W, trap, pair, inner_lo, inner_hi):
    """trap: home -> a small blob with cheap cycles (road W - D/2), the blob joined to the inner graph by one
    road of length D: no short loop goes through it, but loops inside its branch are short.
    pair: a vertex joined to home by two parallel roads of total 2W + pair (the best loop when pair is
    smaller than every inner road). Vertices nxt, nxt + 1, ... are used."""
    e = []
    if trap:
        D = W // 4
        e += tree_edges(nxt, nxt + 29, 1, 10) + extra_edges(nxt, nxt + 29, 30, 1, 10)
        e.append((1, nxt, W - D // 2))
        e.append((nxt + 29, ri(inner_lo, inner_hi), D))
        nxt += 30
    if pair is not None:
        e.append((1, nxt, W + pair // 2))
        e.append((nxt, 1, W + pair - pair // 2))
    return e


def hub(n, m, deg1, W, spread, wlo, whi, depth=None, trap=False, pair=None):
    """inner graph (a tree plus random roads, weights wlo..whi), home joined to deg1 inner vertices by roads
    of length W..W+spread, plus gadgets"""
    gv, ge = gadget_size(trap, pair)
    hi = n - gv
    e = tree_edges(2, hi, wlo, whi, depth)
    e += extra_edges(2, hi, m - deg1 - ge - len(e), wlo, whi)
    for v in random.sample(range(2, hi + 1), deg1):
        e.append((1, v, W + ri(0, spread)))
    return e + gadgets(hi + 1, W, trap, pair, 2, hi)


def dead_ends(n, m, light, heavy, wlo, whi, trap=False):
    """home has `light` cheap roads into small trees that lead nowhere else, and `heavy` expensive roads
    (nearly equal) into a connected inner graph: every loop needs two expensive roads"""
    W = 5 * 10 ** 8
    gv, ge = gadget_size(trap, None)
    e = []
    v = 2
    for _ in range(light):
        size = ri(1, 6)
        e.append((1, v, ri(1, 20)))
        e += tree_edges(v, v + size - 1, 1, 20)
        v += size
    inner_lo, hi = v, n - gv
    e += tree_edges(inner_lo, hi, wlo, whi)
    e += extra_edges(inner_lo, hi, m - heavy - ge - len(e), wlo, whi)
    for x in random.sample(range(inner_lo, hi + 1), heavy):
        e.append((1, x, W + ri(0, 1000)))
    return e + gadgets(hi + 1, W, trap, None, inner_lo, hi)


# samples
add(6, [(1, 2, 1), (2, 4, 1), (4, 5, 1), (5, 2, 1), (1, 3, 5), (3, 4, 2), (1, 6, 1)], False)
add(4, [(1, 2, 3), (2, 3, 1), (3, 4, 1), (4, 2, 1)], False)
add(3, [(1, 2, 5), (2, 3, 1), (2, 1, 7)], False)
add(5, [(2, 3, 4), (1, 2, 6), (4, 5, 1), (1, 4, 2), (3, 5, 2), (5, 2, 9)], False)
add(3, [(1, 2, MAXW), (2, 3, MAXW), (3, 1, MAXW)], False)
# hidden: small (checked by the brute force)
add(2, [(1, 2, 7)])
add(2, [(1, 2, 7), (2, 1, 3), (1, 2, 4)])                        # two parallel roads: 3 + 4
add(5, [(2, 3, 1), (3, 4, 1), (4, 2, 1), (4, 5, 2)])               # home has no road
add(7, tree_edges(1, 7, 1, 9))                                    # a tree: -1
add(8, [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 5, 1), (4, 6, 1), (5, 6, 1), (4, 5, 9), (6, 7, 1), (7, 8, 1),
        (8, 6, 1)])
add(30, hub(30, 60, 6, 1, 49, 1, 10))
add(100, hub(100, 200, 10, 1000, 20, 1, 5, trap=True))
add(80, dead_ends(80, 140, 8, 5, 1, 30))
add(200, hub(200, 400, 3, 1, 999, 1, 1000))
add(500, hub(500, 1200, 50, 1000, 30, 40, 100, trap=True, pair=35))
add(1000, hub(1000, 2500, 200, 1, MAXW, 1, MAXW))
# hidden: large (most: many roads at home of nearly equal length, a cheap inside, and the gadgets)
N, M = MAXN, MAXM
W = 10 ** 8
add(50000, hub(50000, M, 3000, W, 100, 1, 1000, trap=True))
add(50000, hub(50000, M, 3000, 10 ** 6, 0, 1, 3, trap=True))      # equal roads at home, many ties
add(70000, hub(70000, M, 10000, 10 ** 6, 50, 1, 100, trap=True))
add(80000, hub(80000, M, 2000, 5 * W, 1000, 1, 1000, depth=50, trap=True))   # long thin inner graph
add(70000, dead_ends(70000, M, 3000, 800, 1, 1000, trap=True))
add(80000, dead_ends(80000, M, 6000, 4000, 1, 10, trap=True))
add(60000, hub(60000, M, 3000, W, 100, 200, 1000, trap=True, pair=150))      # best: two parallel roads
add(N, tree_edges(1, N, 1, MAXW))                                 # a tree: -1
e = hub(69999, M - 1, 4000, 1, MAXW - 1, 1, MAXW)                 # home hangs on a single road: -1
add(70000, [(a + 1, b + 1, w) for a, b, w in e] + [(1, 2, 5)])
e = hub(N - 1, M - 1, 1, 1, 8, 1, 9)                              # same, a tree-like cheap graph
add(N, [(a + 1, b + 1, w) for a, b, w in e] + [(1, 2, 5)])
add(N, [(i, i + 1, MAXW) for i in range(1, N)] + [(N, 1, MAXW)], False)   # one huge ring: N * 10^9
e = [(1, v, W + ri(0, 100)) for v in range(2, 60001)]             # a star with cheap chords
e += gadgets(60001, W, True, None, 2, 60000)
e += extra_edges(2, 60000, M - len(e), 1, 1000)
add(60030, e)
add(60000, hub(60000, M, 25000, 3 * W, 10, 20, 1000, depth=3, trap=True, pair=15))
add(70000, hub(70000, M, 500, W, 1000, 300, 10 ** 5, trap=True, pair=250))
add(70000, dead_ends(70000, M, 2000, 3000, 1, 10 ** 6, trap=True))
add(50000, hub(50000, M, 1000, 1, 0, 1, 1))                       # all weights 1
R, C = 200, 249                                                   # a grid, home joined to many cells
e = []
for r in range(R):
    for c in range(C):
        v = 2 + r * C + c
        if c + 1 < C:
            e.append((v, v + 1, ri(1, 1000)))
        if r + 1 < R:
            e.append((v, v + C, ri(1, 1000)))
e += gadgets(R * C + 2, 10 ** 6, True, None, 2, R * C + 1)
for v in random.sample(range(2, R * C + 2), M - len(e)):
    e.append((1, v, 10 ** 6 + ri(0, 100)))
add(R * C + 31, e)
add(70000, hub(70000, M, 1500, MAXW - 1000, 400, 500, 10 ** 5, trap=True, pair=400))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
