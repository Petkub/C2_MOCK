# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(750613)
MAXN, MAXW = 100000, 10 ** 9
tests = []
rnd = random.random


def add(k, w, par):
    """par[i] for towns i = 2..n (par[0], par[1] unused)"""
    n = len(w)
    assert 2 <= n <= MAXN and 0 <= k <= n - 1 and len(par) == n + 1
    assert 1 <= min(w) and max(w) <= MAXW
    # the roads (i, par[i]) form a tree: following parents from any town reaches town 1 without repeats
    depth = [0] * (n + 1)
    state = [0] * (n + 1)
    state[1] = 2
    for s in range(2, n + 1):
        path, v = [], s
        while state[v] == 0:
            state[v] = 1
            path.append(v)
            v = par[v]
            assert 1 <= v <= n
        assert state[v] == 2
        for u in path:
            state[u] = 2
    tests.append(f"{n} {k}\n" + " ".join(map(str, w)) + "\n" + " ".join(map(str, par[2:])) + "\n")


def build(n, shape, *a):
    """construction tree on nodes 0..n-1 with up[i] < i (root 0)"""
    up = [-1] * n
    if shape == "random":
        for i in range(1, n):
            up[i] = int(rnd() * i)
    elif shape == "deep":                      # parent among the last a[0] nodes
        d = a[0]
        for i in range(1, n):
            up[i] = i - 1 - int(rnd() * min(i, d))
    elif shape == "path":
        for i in range(1, n):
            up[i] = i - 1
    elif shape == "star":
        for i in range(1, n):
            up[i] = 0
    elif shape == "capital":                   # random tree, but a share a[0] of the towns hang on node 0
        for i in range(1, n):
            up[i] = 0 if rnd() < a[0] else int(rnd() * i)
    elif shape == "binary":
        for i in range(1, n):
            up[i] = (i - 1) // 2
    elif shape == "hubs":                      # a[0] hubs in a random tree, the others are leaves of hubs
        h = a[0]
        for i in range(1, n):
            up[i] = int(rnd() * i) if i < h else int(rnd() * h)
    elif shape == "caterpillar":               # a spine of a[0] nodes, the others hang on random spine nodes
        s = a[0]
        for i in range(1, n):
            up[i] = i - 1 if i < s else int(rnd() * s)
    elif shape == "spider":                    # legs of length about a[0] from node 0
        L = a[0]
        for i in range(1, n):
            up[i] = 0 if i % L == 1 or L == 1 else i - 1
    elif shape == "broom":                     # a path of a[0] nodes, then a star at its end
        s = a[0]
        for i in range(1, n):
            up[i] = i - 1 if i < s else s - 1
    return up


def label(up, keep_root=False):
    """random town numbers; the tree is given as parents towards town 1"""
    n = len(up)
    perm = list(range(1, n + 1))
    random.shuffle(perm)
    if keep_root:                              # construction root becomes town 1
        j = perm.index(1)
        perm[0], perm[j] = perm[j], perm[0]
    c = perm.index(1)                          # construction node that becomes town 1: re-root there
    up = up[:]
    prev, v = -1, c
    while v != -1:
        nxt = up[v]
        up[v] = prev
        prev, v = v, nxt
    par = [0] * (n + 1)
    for v in range(n):
        if up[v] != -1:
            par[perm[v]] = perm[up[v]]
    return par


def weights(n, kind):
    if kind == "big":
        return [MAXW - int(rnd() * 1000) for _ in range(n)]
    if kind == "max":
        return [MAXW] * n
    if kind == "small":
        return [1 + int(rnd() * 10) for _ in range(n)]
    if kind == "mix":                          # mostly small, some huge
        return [1 + int(rnd() * 1000) if rnd() < 0.97 else 1 + int(rnd() * MAXW) for _ in range(n)]
    return [1 + int(rnd() * MAXW) for _ in range(n)]


def tree(n, k, wk, shape, *a, keep_root=False):
    add(k, weights(n, wk), label(build(n, shape, *a), keep_root))


# samples
add(2, [4, 2, 7, 3, 5, 1, 6], [0, 0, 1, 1, 2, 2, 3, 3])
add(0, [5, 8], [0, 0, 1])
add(4, [3, 1, 4, 1, 5], [0, 0, 1, 1, 1, 1])
add(3, [2, 9, 4, 6, 1, 8, 3], [0, 0, 3, 5, 1, 7, 1, 4])
add(2, [7, 3, 3, 3, 3, 3, 3, 3], [0, 0, 1, 1, 1, 2, 3, 4, 4])
# hidden: small (brute checks these)
add(1, [10 ** 9, 10 ** 9], [0, 0, 1])
tree(12, 11, "rand", "random")
tree(15, 4, "small", "random")
tree(18, 6, "rand", "star")
tree(17, 3, "mix", "caterpillar", 5)
tree(16, 7, "small", "path")
tree(300, 40, "rand", "random")
tree(800, 300, "small", "hubs", 6)
tree(1500, 30, "mix", "deep", 5)
tree(2000, 900, "rand", "caterpillar", 40)
# hidden: big (N = 100000)
N = MAXN
tree(N, 50000, "rand", "star")
tree(N, 20000, "small", "star", keep_root=True)
tree(N, 70000, "big", "hubs", 3)
tree(N, 35000, "rand", "hubs", 20)
tree(N, 60000, "mix", "hubs", 10)
tree(N, 45000, "rand", "caterpillar", 4)
tree(N, 30000, "small", "caterpillar", 8)
tree(N, 80000, "rand", "broom", 30000)
tree(N, 40000, "rand", "spider", 3)
tree(N, 25000, "big", "spider", 2)
tree(N, 20000, "rand", "capital", 0.3)
tree(N, 50000, "rand", "random")
tree(N, 10, "rand", "deep", 3)
tree(N, 30000, "mix", "path")
tree(N, 5000, "rand", "binary")
tree(N, 0, "max", "random")
tree(N, N - 1, "rand", "hubs", 50)
tree(N, 99000, "max", "star")
tree(N, 3, "rand", "hubs", 4)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
