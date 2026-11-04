# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(650521)
MAXN, MAXM, MAXK, MAXW = 3000, 10000, 100, 10 ** 6
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(n, edges, s, cap, pas):
    m, k = len(edges), len(pas)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM and 1 <= cap <= k <= MAXK and 1 <= s <= n
    for u, v, w in edges:
        assert 1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= MAXW
    for a, b in pas:
        assert 1 <= a <= n and 1 <= b <= n
    lines = [f"{n} {m} {k} {cap} {s}", " ".join(str(a) for a, b in pas), " ".join(str(b) for a, b in pas)]
    lines += [f"{u} {v} {w}" for u, v, w in edges]
    tests.append("\n".join(lines) + "\n")


def relabel(n, edges, s, pas):
    """random town numbers and road order (the build order would show the structure)"""
    perm = list(range(1, n + 1))
    random.shuffle(perm)
    lab = [0] + perm
    e = [(lab[u], lab[v], w) if rnd() < 0.5 else (lab[v], lab[u], w) for u, v, w in edges]
    random.shuffle(e)
    return e, lab[s], [(lab[a], lab[b]) for a, b in pas]


def wgt(lo=1, hi=MAXW):
    return ri(lo, hi)


def random_graph(n, m, w=(1, MAXW)):
    """connected: random tree (attach to a recent town, so it is deep) plus random extra roads"""
    e = []
    for v in range(2, n + 1):
        u = ri(max(1, v - 30), v - 1) if rnd() < 0.7 else ri(1, v - 1)
        e.append((u, v, wgt(*w)))
    while len(e) < m:
        u, v = ri(1, n), ri(1, n)
        if u != v:
            e.append((u, v, wgt(*w)))
    return e


def grid_graph(rows, cols, extra, w=(1, MAXW)):
    e = []
    idx = lambda r, c: r * cols + c + 1
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                e.append((idx(r, c), idx(r, c + 1), wgt(*w)))
            if r + 1 < rows:
                e.append((idx(r, c), idx(r + 1, c), wgt(*w)))
    n = rows * cols
    for _ in range(extra):
        u, v = ri(1, n), ri(1, n)
        if u != v:
            e.append((u, v, wgt(*w)))
    return e


def line_graph(n, extra, w=(1, MAXW), ew=None):
    e = [(v, v + 1, wgt(*w)) for v in range(1, n)]
    for _ in range(extra):
        u = ri(1, n - 1)
        v = min(n, u + ri(2, 40))
        if u != v:
            e.append((u, v, wgt(*(ew or w))))
    return e


def clusters(sizes, inner_m, bridge_w):
    """clusters of towns (random graphs with short roads) joined in a chain by long bridges;
    returns edges and the list of towns of every cluster"""
    e, groups, base = [], [], 0
    for sz, mm in zip(sizes, inner_m):
        g = random_graph(sz, mm, (1, 1000))
        e += [(u + base, v + base, w) for u, v, w in g]
        groups.append(list(range(base + 1, base + sz + 1)))
        base += sz
    for a, b in zip(groups, groups[1:]):
        for _ in range(2):
            e.append((random.choice(a), random.choice(b), ri(bridge_w // 2, bridge_w)))
    return e, groups


def pick(pool, k):
    return [random.choice(pool) for _ in range(k)]


def emit(n, e, s, cap, pas, shuffle=True):
    if shuffle:
        e, s, pas = relabel(n, e, s, pas)
    add(n, e, s, cap, pas)


# ---------------------------------------------------------------- samples
add(3, [(1, 2, 1), (2, 3, 10)], 1, 2, [(2, 3), (2, 3), (1, 3)])
add(3, [(1, 2, 1), (2, 3, 10)], 1, 2, [(1, 3), (2, 1)])
add(3, [(1, 2, 5)], 1, 1, [(2, 3)])
add(3, [(1, 2, 4), (2, 3, 3)], 2, 1, [(2, 2), (3, 1), (3, 3)])
add(4, [(1, 2, 3), (2, 3, 2), (3, 4, 4), (4, 1, 6)], 3, 2, [(2, 4), (4, 1), (1, 1), (4, 2)])

# ---------------------------------------------------------------- small hidden (brute checks these)
add(1, [], 1, 1, [(1, 1)])
n = 40
emit(n, random_graph(n, 70, (1, 50)), 1, 2, [(ri(1, n), ri(1, n)) for _ in range(10)])
n = 30
emit(n, line_graph(n, 5, (1, 100)), ri(1, n), 3, [(ri(1, n), ri(1, n)) for _ in range(11)])
e, gr = clusters([12, 12], [20, 20], 5000)
emit(24, e, gr[0][0], 2, [(random.choice(gr[0]), random.choice(gr[1])) for _ in range(11)])
n = 25
emit(n, random_graph(n, 40, (1, 9)), 5, 1, [(v, v) if rnd() < 0.5 else (v, ri(1, n)) for v in pick(range(1, n + 1), 10)])
# towns outside the shuttle's part exist, but every stop is reachable
e = random_graph(20, 35, (1, MAXW)) + [(21, 22, 7), (22, 23, 7)]
emit(23, e, 3, 4, [(ri(1, 20), ri(1, 20)) for _ in range(9)])
# the last destination cannot be reached
e = random_graph(20, 30, (1, 1000)) + [(21, 22, 1)]
pas = [(ri(1, 20), ri(1, 20)) for _ in range(8)] + [(ri(1, 20), 22)]
emit(22, e, 1, 3, pas)
n = 50
emit(n, random_graph(n, 49, (1, MAXW)), 1, 11, [(ri(1, n), ri(1, n)) for _ in range(11)])

# ---------------------------------------------------------------- big hidden
K = MAXK


def big_random(cap, w=(1, MAXW), stops=None):
    e = random_graph(MAXN, MAXM, w)
    towns = random.sample(range(1, MAXN + 1), 2 * K + 1)
    pas = [(towns[2 * j + 1], towns[2 * j + 2]) for j in range(K)] if stops is None else stops
    emit(MAXN, e, towns[0], cap, pas)


big_random(2)
big_random(3)
big_random(7)
big_random(25, (1, 1000))
big_random(K)

# grid road network
e = grid_graph(50, 60, MAXM - 5890)
towns = random.sample(range(1, MAXN + 1), 2 * K + 1)
emit(MAXN, e, towns[0], 4, [(towns[2 * j + 1], towns[2 * j + 2]) for j in range(K)])
e = grid_graph(60, 50, MAXM - 5890, (900000, MAXW))
towns = random.sample(range(1, MAXN + 1), 2 * K + 1)
emit(MAXN, e, towns[0], 2, [(towns[2 * j + 1], towns[2 * j + 2]) for j in range(K)])

# commuters: everyone waits in the first cluster and goes to the far one
for cap, sizes in ((3, [1500, 1500]), (10, [1000, 1000, 1000]), (2, [1200, 600, 1200])):
    e, gr = clusters(sizes, [s * 3 for s in sizes[:-1]] + [MAXM - 3 * sum(sizes[:-1]) - 2 * (len(sizes) - 1)], 10 ** 6)
    assert len(e) <= MAXM
    pas = [(random.choice(gr[0]), random.choice(gr[-1] if rnd() < 0.8 else random.choice(gr))) for _ in range(K)]
    emit(MAXN, e, gr[0][0], cap, pas)

# two-way traffic between two clusters
for cap in (2, 5):
    e, gr = clusters([1500, 1500], [4990, 4990], 10 ** 6)
    pas = []
    for j in range(K):
        a, b = (0, 1) if (j // ri(1, 4)) % 2 == 0 else (1, 0)
        pas.append((random.choice(gr[a]), random.choice(gr[b])))
    emit(MAXN, e, gr[0][0], cap, pas)

# a long line with heavy roads (lengths beyond 32 bits), stops jump between the two ends
e = line_graph(MAXN, 0, (MAXW, MAXW))
pas = [(ri(1, 30), ri(MAXN - 30, MAXN)) if j % 2 == 0 else (ri(MAXN - 30, MAXN), ri(1, 30)) for j in range(K)]
emit(MAXN, e, 1, 1, pas, shuffle=False)
e = line_graph(MAXN, MAXM - MAXN + 1, (1, MAXW), (MAXW, MAXW))
pas = [(ri(1, MAXN), ri(1, MAXN)) for _ in range(K)]
emit(MAXN, e, ri(1, MAXN), 3, pas)
# along a line: passengers ride forward, each a short way, waiting places interleaved
e = line_graph(MAXN, MAXM - MAXN + 1, (1, MAXW), (MAXW, MAXW))
pos = sorted(random.sample(range(1, MAXN + 1), K))
pas = [(pos[j], min(MAXN, pos[j] + ri(1, 400))) for j in range(K)]
emit(MAXN, e, 1, 2, pas)
pas = [(pos[j], max(1, pos[j] - ri(1, 400))) for j in range(K)]
emit(MAXN, e, MAXN, 4, pas)

# few stop towns used many times, some passengers going nowhere
e = random_graph(MAXN, MAXM)
hot = random.sample(range(1, MAXN + 1), 6)
pas = []
for _ in range(K):
    a = random.choice(hot)
    pas.append((a, a) if rnd() < 0.3 else (a, random.choice(hot)))
emit(MAXN, e, hot[0], 3, pas)

# star around the start
e = [(1, v, ri(1, MAXW)) for v in range(2, MAXN + 1)] + [(ri(2, MAXN), ri(2, MAXN), ri(1, MAXW)) for _ in range(MAXM - MAXN + 1)]
e = [x for x in e if x[0] != x[1]]
towns = random.sample(range(2, MAXN + 1), 2 * K)
emit(MAXN, e, 1, 6, [(towns[2 * j], towns[2 * j + 1]) for j in range(K)])

# disconnected: big second part without stops; and the -1 version
e = random_graph(2000, 7000) + [(u + 2000, v + 2000, w) for u, v, w in random_graph(1000, 3000)]
towns = random.sample(range(1, 2001), 2 * K + 1)
pas = [(towns[2 * j + 1], towns[2 * j + 2]) for j in range(K)]
emit(MAXN, e, towns[0], 5, pas)
pas[K // 2] = (pas[K // 2][0], ri(2001, MAXN))
emit(MAXN, e, towns[0], 5, pas)
# long roads along a line (totals far beyond 32 bits), stops anywhere
e = line_graph(MAXN, 3000, (MAXW // 2, MAXW), (MAXW, MAXW))
pas = [(ri(1, MAXN), ri(1, MAXN)) for _ in range(K)]
emit(MAXN, e, ri(1, MAXN), 5, pas)
# the shuttle starts in a part that holds no stop: -1
e = random_graph(1000, 3000) + [(u + 1000, v + 1000, w) for u, v, w in random_graph(MAXN - 1000, MAXM - 3000)]
towns = random.sample(range(1001, MAXN + 1), 2 * K)
emit(MAXN, e, ri(1, 1000), 3, [(towns[2 * j], towns[2 * j + 1]) for j in range(K)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
