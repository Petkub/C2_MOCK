# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The friendships at the end form the "filled" graph of the leaving order; on almost every big test the fill is
# huge (10^9 .. 2 * 10^10 pairs), so any method that touches every final friendship (day-by-day simulation,
# copying friend sets without small-to-large, walking every path) runs out of time. The elimination forest is
# deep on the star and path-like tests (binary lifting / LCA depth), and vertices with many earlier friends in
# different branches break a union of paths taken in the wrong order.
import os, random

random.seed(2212)
rnd = random.random
MAXN, MAXM = 100000, 100000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def add(n, order, edges, relabel=True):
    """order: leaving order of 1..n; edges: list of (a, b); relabel: rename the people at random"""
    m = len(edges)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM
    assert sorted(order) == list(range(1, n + 1))
    if relabel:
        nm = [0] + shuffled(range(1, n + 1))
        order = [nm[v] for v in order]
        edges = [(nm[a], nm[b]) for a, b in edges]
    seen = set()
    for a, b in edges:
        assert 1 <= a <= n and 1 <= b <= n and a != b
        key = min(a, b) * (n + 1) + max(a, b)
        assert key not in seen
        seen.add(key)
    if relabel:
        edges = shuffled(edges)
        edges = [(a, b) if rnd() < 0.5 else (b, a) for a, b in edges]
    lines = ["%d %d" % (n, m), " ".join(map(str, order))]
    lines += ["%d %d" % e for e in edges]
    tests.append("\n".join(lines) + "\n")


def rand_edges(n, m, have=None):
    seen = set() if have is None else set(min(a, b) * (n + 1) + max(a, b) for a, b in have)
    out = [] if have is None else list(have)
    while len(out) < m:
        a, b = ri(1, n), ri(1, n)
        if a == b:
            continue
        key = min(a, b) * (n + 1) + max(a, b)
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b))
    return out


def rand_tree(n, spread):
    """parent of v is chosen among the last `spread` vertices before v (small spread: long paths)"""
    return [(v, ri(max(1, v - spread), v - 1)) for v in range(2, n + 1)]


def perm(n):
    return shuffled(range(1, n + 1))


def by_degree(n, edges, rev=False):
    deg = [0] * (n + 1)
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    key = [(deg[v] * (-1 if rev else 1), rnd(), v) for v in range(1, n + 1)]
    return [v for _, _, v in sorted(key)]


# samples
add(6, [2, 6, 3, 1, 4, 5], [(2, 3), (4, 5), (5, 6), (1, 3), (2, 6), (1, 4)], False)
add(7, [1, 4, 6, 5, 2, 3, 7], [(2, 3), (1, 6), (6, 7), (2, 5), (3, 7), (4, 5), (1, 5)], False)
add(2, [2, 1], [(1, 2)], False)
add(8, [4, 7, 6, 8, 5, 2, 1, 3], [(1, 2), (6, 7), (2, 6), (1, 3), (5, 8), (7, 8), (3, 5)], False)
add(8, [1, 3, 5, 6, 8, 7, 2, 4], [(2, 4), (1, 3), (7, 8), (1, 5), (2, 6), (3, 8), (5, 6), (4, 7)], False)
# hidden: small and medium (brute checks these)
for n, m in ((5, 4), (9, 12), (40, 60), (1500, 1600)):
    add(n, perm(n), rand_edges(n, m))
add(2000, [1] + list(range(2, 2001)), [(1, v) for v in range(2, 2001)])          # the centre leaves first
# hidden: big
N = MAXN
add(N, perm(N), rand_edges(N, MAXM))                                              # random graph
add(N, perm(N), rand_edges(N, 70000))                                             # sparser random graph
e = rand_edges(N, MAXM)
add(N, by_degree(N, e), e)                                                        # fewest friends leave first
e = rand_edges(N, MAXM)
add(N, by_degree(N, e, True), e)                                                  # most friends leave first
add(N, [1] + shuffled(range(2, N + 1)), [(1, v) for v in range(2, N + 1)])        # star, the centre leaves first
h = N // 2
add(N, [1, 2] + shuffled(range(3, N + 1)),
    [(1, v) for v in range(3, h + 1)] + [(2, v) for v in range(h - 1, N + 1)])    # two hubs leave first
H = N // 2
tr = rand_tree(H, 3)
add(H, perm(H), rand_edges(H, MAXM, tr))                                          # long tree plus random friendships
tr = rand_tree(H, H)
add(H, perm(H), rand_edges(H, MAXM, tr))                                          # random tree plus random friendships
line = [(v, v + 1) for v in range(1, H)]
add(H, list(range(H // 2, 0, -1)) + list(range(H // 2 + 1, H + 1)),
    rand_edges(H, MAXM, line))                                                    # line + random, from the middle
add(H, perm(H), rand_edges(H, MAXM))                                              # random graph, 4 friends on average
add(70000, perm(70000), rand_edges(70000, MAXM))
side = 223
grid = []
for r in range(side):
    for c in range(side):
        v = r * side + c + 1
        if c + 1 < side:
            grid.append((v, v + 1))
        if r + 1 < side:
            grid.append((v, v + side))
add(side * side, perm(side * side), grid)                                         # a grid, random order
hubs = 30
cnt = MAXM // hubs
add(hubs + cnt, perm(hubs + cnt), [(h, v) for h in range(1, hubs + 1) for v in range(hubs + 1, hubs + cnt + 1)])  # 30 hubs
dense = [(a, b) for a in range(1, 301) for b in range(a + 1, 301)][:MAXM // 2]
add(H, perm(H), rand_edges(H, MAXM, dense))                                       # a close group + random friendships
e = rand_edges(H, MAXM)
add(H, by_degree(H, e), e)                                                        # fewest friends leave first
add(80000, perm(80000), rand_edges(80000, MAXM))
c = shuffled(range(2, N + 1))
add(N, c[:N // 2] + [1] + c[N // 2:], [(1, v) for v in range(2, N + 1)])          # star, the centre leaves halfway
q = (MAXM - 3) // 3
add(3 * q + 3, perm(3 * q + 3), [(h, v) for h in range(1, 4) for v in range(4 + (h - 1) * q // 2, 4 + (h - 1) * q // 2 + q)])  # 3 hubs, overlapping
# hidden: few new friendships (correctness, smaller)
n = 30000
k = 300
add(k, perm(k), rand_edges(k, 40000))                                             # almost everyone is a friend
tr = rand_tree(n, 3)
add(n, perm(n), tr)                                                               # long random tree
add(n, list(range(2, n + 1)) + [1], [(1, v) for v in range(2, n + 1)])            # star, the centre leaves last
add(n, perm(n), [(v, v + 1) for v in range(1, n)])                                # a line, random order
add(n, perm(n), rand_edges(n, 12000))                                             # many small groups

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
