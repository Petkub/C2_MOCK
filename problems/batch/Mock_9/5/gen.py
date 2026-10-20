# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(950521)
MAXN, MAXSUM, MAXW = 100000, 200000, 10000
tests = []
rand = random.random


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(rand() * (hi - lo + 1))


def add(n, par, w, queries, order=None):
    """par[i], w[i] for towns i = 2..n (index 0, 1 unused); queries: lists of towns;
    order (optional): the towns with every p_i before i, starting with town 1 (checked)"""
    assert 2 <= n <= MAXN and len(par) == n + 1 and len(w) == n + 1
    assert 1 <= len(queries) and sum(map(len, queries)) <= MAXSUM
    # the roads form a tree: every town is reached from town 1 going down the p_i links
    assert 1 <= min(par[2:]) and max(par[2:]) <= n and 1 <= min(w[2:]) and max(w[2:]) <= MAXW
    assert all(map(int.__ne__, par[2:], range(2, n + 1)))
    if order is None:
        kids = [[] for _ in range(n + 1)]
        for i in range(2, n + 1):
            kids[par[i]].append(i)
        order = [1]
        for u in order:
            order.extend(kids[u])
    assert len(order) == n and order[0] == 1 and min(order) == 1 and max(order) == n
    pos = dict(zip(order, range(n)))
    assert len(pos) == n                    # order lists every town once
    get = pos.__getitem__
    assert all(map(int.__lt__, map(get, par[2:]), map(get, range(2, n + 1))))
    assert all(len(set(q)) == len(q) for q in queries)
    assert 1 <= min(map(min, queries)) and max(map(max, queries)) <= n
    lines = [str(n), " ".join(map(str, par[2:])), " ".join(map(str, w[2:])), str(len(queries))]
    lines += [" ".join(map(str, [len(q)] + q)) for q in queries]
    tests.append("\n".join(lines) + "\n")


# ---- trees: base shape with nodes 0..n-1, parent bp[i] < i for i >= 1 (node 0 is the base root)
def shape(kind, n, a=0):
    if kind == "path":
        return [-1] + list(range(n - 1))
    if kind == "random":
        return [-1] + [ri(0, i - 1) for i in range(1, n)]
    if kind == "deep":                  # parent among the a previous nodes
        return [-1] + [ri(max(0, i - a), i - 1) for i in range(1, n)]
    if kind == "cater":                 # spine 0..a-1, every other node hangs on a random spine node
        return [-1] + [i - 1 if i < a else ri(0, a - 1) for i in range(1, n)]
    if kind == "broom":                 # path 0..a-1, the rest hang on its end
        return [-1] + [i - 1 if i < a else a - 1 for i in range(1, n)]
    if kind == "star":
        return [-1] + [0] * (n - 1)
    if kind == "binary":
        return [-1] + [(i - 1) // 2 for i in range(1, n)]
    if kind == "spider":                # legs of a nodes from node 0
        return [-1] + [0 if (i - 1) % a == 0 else i - 1 for i in range(1, n)]
    if kind == "comb":                  # spine 0..a-1, teeth: paths hanging from the spine nodes in turn
        bp = [-1] + list(range(a - 1))
        tooth = 0
        while len(bp) < n:
            ln = min(n - len(bp), ri(1, 2 * (n - a) // a + 1))
            bp.append(tooth % a)
            for _ in range(ln - 1):
                bp.append(len(bp) - 1)
            tooth += 1
        return bp
    raise ValueError(kind)


_perm = {}


def labels(n):
    """a random labelling of the base nodes 0..n-1 by 1..n; all trees of one size share it (fast)"""
    if n not in _perm:
        p = list(range(1, n + 1))
        random.shuffle(p)
        _perm[n] = p
    return _perm[n]


class Tree:
    """a base shape with random labels, rooted at town 1 (a random base node) for the input"""

    def __init__(self, bp, wlo=1, whi=MAXW, root=None):
        n = self.n = len(bp)
        lab = list(labels(n))
        r = ri(0, n - 1) if root is None else root
        j = lab.index(1)
        lab[j], lab[r] = lab[r], lab[j]          # node r gets label 1
        self.lab = lab
        # re-root the base tree at r: only the links on the path from r up to node 0 turn around
        bpar = list(bp)
        x, prev = r, -1
        while x != -1:
            nxt = bp[x]
            bpar[x] = prev
            prev, x = x, nxt
        par = [0] * (n + 1)
        for v in range(n):
            if bpar[v] != -1:
                par[lab[v]] = lab[bpar[v]]
        # parents before children: the path from r up to node 0, then the other nodes by index
        onpath = [False] * n
        path, x = [], r
        while x != -1:
            onpath[x] = True
            path.append(x)
            x = bp[x]
        self.order = [lab[v] for v in path] + [lab[v] for v in range(n) if not onpath[v]]
        w = [0] * (n + 1)
        span = whi - wlo + 1
        w[2:] = [wlo + int(rand() * span) for _ in range(n - 1)]
        self.par, self.w = par, w
        deg = [0] * n
        for v in range(1, n):
            deg[v] += 1
            deg[bp[v]] += 1
        self.leaves = [lab[v] for v in range(n) if deg[v] == 1] or [lab[0]]

    def pick(self, k, pool=None):
        """k distinct towns, from pool (labels) if given"""
        src = pool if pool is not None else self.lab
        size = len(src)
        k = min(k, size)
        if k * k > size:          # many towns: sample; few: draw until all differ
            return [src[i] for i in random.sample(range(size), k)]
        while True:
            q = [src[int(rand() * size)] for _ in range(k)]
            if len(set(q)) == k:
                return q


def emit(t, queries):
    """the queries in order, as many as fit into the limit on the sum of k"""
    s, keep = 0, []
    for q in queries:
        if s + len(q) > MAXSUM:
            break
        keep.append(q)
        s += len(q)
    add(t.n, t.par, t.w, keep, t.order)


def many(t, q, klo, khi, pool=None, total=None):
    qs, s = [], 0
    for _ in range(q):
        k = ri(klo, khi)
        if total is not None and s + k > total:
            break
        qs.append(t.pick(k, pool))
        s += len(qs[-1])
    return qs


# samples
add(7, [0, 0, 1, 1, 2, 2, 3, 3], [0, 0, 3, 2, 4, 1, 5, 2], [[4, 5, 7], [6], [7, 6, 4, 1]])
add(6, [0, 0, 3, 5, 3, 6, 1], [0, 0, 2, 4, 1, 3, 6], [[2, 5], [4, 6, 2], [3]])
add(5, [0, 0, 1, 1, 1, 1], [0, 0, 7, 3, 9, 1], [[2, 3, 4, 5], [1, 5], [3, 4]])
add(2, [0, 0, 1], [0, 0, 5], [[2], [1, 2]])
add(9, [0, 0, 1, 2, 2, 4, 1, 6, 6, 8], [0, 0, 4, 2, 6, 1, 3, 5, 2, 7], [[3, 5, 9], [2, 7], [5, 3, 1, 8, 9]])
# hidden: small (brute checks these)
t = Tree(shape("random", 12), 1, 10)
emit(t, many(t, 60, 1, 6))
t = Tree(shape("path", 40))
emit(t, many(t, 100, 1, 8))
t = Tree(shape("star", 30), 1, 5)
emit(t, many(t, 100, 2, 10))
t = Tree(shape("cater", 300, 60))
emit(t, many(t, 300, 1, 12) + many(t, 100, 2, 6, t.leaves))
t = Tree(shape("deep", 2000, 4))
emit(t, many(t, 600, 2, 15))
t = Tree(shape("comb", 1500, 40))
emit(t, many(t, 400, 3, 20, t.leaves) + [t.pick(40)])
# hidden: big, N = 100000
N = MAXN
t = Tree(shape("path", N))
emit(t, many(t, 30000, 2, 5))
t = Tree(shape("path", N), MAXW, MAXW)
emit(t, many(t, 20000, 3, 6) + [[t.lab[0], t.lab[N - 1]]])               # all roads, every length maximal
t = Tree(shape("deep", N, 8))
emit(t, many(t, 30000, 2, 5))
t = Tree(shape("deep", N, 3))
emit(t, many(t, 25000, 2, 6, t.leaves))
t = Tree(shape("deep", N, 2), 1, 100)
emit(t, many(t, 30000, 2, 3))
t = Tree(shape("cater", N, N // 2))
emit(t, many(t, 25000, 3, 7, t.leaves))
t = Tree(shape("cater", N, N // 4))
emit(t, many(t, 30000, 2, 5))
t = Tree(shape("broom", N, N // 2))
emit(t, many(t, 25000, 2, 6) + many(t, 500, 20, 60, t.leaves))
t = Tree(shape("broom", N, 3 * N // 4))
emit(t, many(t, 30000, 3, 4, t.leaves[:10] + t.pick(3000)))
t = Tree(shape("spider", N, N // 2))                                       # two long arms
emit(t, many(t, 30000, 2, 5))
t = Tree(shape("spider", N, 10000))                                        # ten long legs
emit(t, many(t, 25000, 3, 6))
t = Tree(shape("comb", N, 300))
emit(t, many(t, 25000, 3, 6, t.leaves))
t = Tree(shape("comb", N, 10000), 1, 100)
emit(t, [t.pick(N // 2, t.leaves), t.pick(30000)] + many(t, 20000, 1, 3))
t = Tree(shape("star", N))
emit(t, many(t, 30000, 3, 6))
t = Tree(shape("random", N))
emit(t, many(t, 35000, 2, 4))
t = Tree(shape("binary", N))
emit(t, many(t, 4000, 10, 40, t.leaves))
t = Tree(shape("deep", N, 20))
emit(t, [list(t.lab)] + many(t, 20000, 1, 1) + many(t, 15000, 2, 3))          # all towns at once, k = 1
t = Tree(shape("deep", N, 5), 1, 9)
emit(t, many(t, 800, 50, 150))

for x in tests:
    assert x.endswith("\n") and "  " not in x and " \n" not in x
os.makedirs("tests", exist_ok=True)
for i, x in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(x)
