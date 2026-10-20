# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(530503)
MAXN, MAXA, MAXW = 10_000, 10**9, 10**9
tests = []
_rnd = random.random


def ri(lo, hi):
    return lo + int(_rnd() * (hi - lo + 1))


def shuf(x):
    for i in range(len(x) - 1, 0, -1):
        j = int(_rnd() * (i + 1))
        x[i], x[j] = x[j], x[i]


def add(a, edges):
    n = len(a)
    assert 1 <= n <= MAXN and len(edges) == n - 1
    assert all(-MAXA <= x <= MAXA for x in a)
    assert all(1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= MAXW for u, v, w in edges)
    # n - 1 edges that connect everything form a tree
    adj = [[] for _ in range(n + 1)]
    for u, v, _ in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * (n + 1)
    seen[1] = True
    order = [1]
    for x in order:
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                order.append(y)
    assert len(order) == n
    t = f"{n}\n" + " ".join(map(str, a)) + "\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)
    assert len(t) <= 3_000_000
    tests.append(t)


def shape(n, kind):
    """par[i] for i = 1..n-1 is a node in 0..i-1 (node 0 is the top)"""
    par = [-1] * n
    h = n // 2
    for i in range(1, n):
        if kind == "random":
            par[i] = int(_rnd() * i)
        elif kind == "path":
            par[i] = i - 1
        elif kind == "star":
            par[i] = 0
        elif kind == "deep":                    # depth about n / 2
            par[i] = ri(max(0, i - 3), i - 1)
        elif kind == "binary":
            par[i] = (i - 1) // 2
        elif kind == "broom":                   # a path of n / 2 nodes, then a star at its end
            par[i] = i - 1 if i <= h else h
        elif kind == "broom2":                  # a star at the top, then a long path below one leaf
            par[i] = 0 if i <= h else (1 if i == h + 1 else i - 1)
        elif kind == "cater":                   # a path with leaves hanging anywhere on it
            par[i] = i - 1 if i < h else ri(0, h - 1)
        elif kind == "comb":                    # every path node has one leaf
            par[i] = i - 2 if i % 2 == 0 else max(0, i - 2)
        elif kind == "bushes":                  # a path of n / 2 nodes, then groups of 50 leaves at random path nodes
            if i < h:
                par[i] = i - 1
            elif (i - h) % 50 == 0:
                par[i] = ri(0, h - 1)
            else:
                par[i] = par[i - 1]
        elif kind == "chains":                  # about sqrt(n) chains below the top
            k = max(1, int(n ** 0.5))
            par[i] = 0 if i <= k else i - k
        elif kind == "twobrooms":               # two long paths from the top, each ending in a star
            q = n // 4
            if i <= 2:
                par[i] = 0
            elif i < 2 * q:
                par[i] = i - 2
            else:
                par[i] = 2 * q - 2 + (i % 2)
        else:
            raise ValueError(kind)
    return par


def tree(n, kind, afun, wfun, first=None):
    """a tree of the given shape with random labels; first: the label 1 goes to that shape node"""
    par = shape(n, kind)
    lab = list(range(1, n + 1))
    shuf(lab)
    if first is not None:
        j = lab.index(1)
        lab[first], lab[j] = lab[j], lab[first]
    a = [0] * n
    for i in range(n):
        a[lab[i] - 1] = afun()
    edges = []
    for i in range(1, n):
        u, v = lab[par[i]], lab[i]
        edges.append((u, v, wfun()) if ri(0, 1) else (v, u, wfun()))
    shuf(edges)
    add(a, edges)
    return a, edges


def unif(lo, hi):
    return lambda: ri(lo, hi)


# samples
add([3, -4, 2, 6, 5, 7, -1], [(1, 2, 2), (1, 3, 1), (2, 4, 1), (2, 5, 1), (3, 6, 4), (3, 7, 2)])
add([5, -2, -2, 5], [(1, 2, 1), (2, 3, 1), (3, 4, 1)])
add([-7], [])
add([-5, 8, 8, 8], [(2, 1, 10), (1, 3, 1), (4, 1, 3)])
add([4, -3, 9, -8, 6], [(3, 2, 2), (1, 2, 5), (5, 4, 1), (4, 2, 3)])
# hidden: small (every set is tried by brute.cpp)
add([MAXA, -MAXA], [(2, 1, MAXW)])
add([1, 1, 1], [(1, 2, 1), (3, 1, 1)])
tree(10, "random", unif(-20, 20), unif(1, 10))
tree(12, "path", unif(-5, 30), unif(1, 15))
tree(14, "star", unif(-MAXA, MAXA), unif(1, MAXW))
tree(16, "deep", unif(-50, 50), unif(1, 30))
# hidden: medium
tree(60, "path", unif(-100, 100), unif(1, 60))
tree(150, "random", unif(-MAXA, MAXA), unif(1, MAXW))
tree(300, "broom", unif(-1000, 3000), unif(1, 1000))
tree(400, "cater", unif(0, 100), unif(1, 100))
# hidden: maximum size
N = MAXN
tree(N, "path", unif(-MAXA, MAXA), unif(1, MAXW))
tree(N, "path", lambda: MAXA, lambda: 1)                                  # the largest possible answers
tree(N, "broom", unif(-MAXA, MAXA), unif(1, 100))
tree(N, "broom", unif(0, MAXA), unif(1, MAXW))
tree(N, "broom2", unif(-1000, 1000), unif(1, 1000))
tree(N, "star", unif(-MAXA, MAXA), unif(1, MAXW))
tree(N, "cater", unif(-100, 300), unif(1, 300))
tree(N, "binary", unif(-MAXA, MAXA), unif(1, MAXW))
tree(N, "random", unif(-1000, 1000), unif(1, 1000))
tree(N, "deep", unif(-MAXA, MAXA), unif(1, MAXW // 4))
tree(N, "twobrooms", unif(-10**6, 10**6), unif(1, 10**6))
tree(N, "bushes", unif(-500, 1000), unif(1, 700))
tree(N, "chains", unif(-MAXA, MAXA), unif(1, MAXA))
tree(N, "broom", lambda: -MAXA, lambda: MAXW)                             # the smallest possible answers
tree(N, "comb", unif(0, 100), unif(1, 100))
tree(N, "broom", unif(0, 10**6), unif(1, 10**6), first=N - 1)            # village 1 is a leaf of the star
tree(N, "cater", unif(0, 100), unif(50, 150), first=N - 1)                # village 1 is a leaf
tree(N, "bushes", unif(-MAXA, MAXA), unif(1, MAXW), first=0)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
