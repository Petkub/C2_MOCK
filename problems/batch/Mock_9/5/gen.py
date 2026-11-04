# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(905)
MAXN, MAXW = 100000, 10 ** 6
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def shuf(a):
    """a shuffled copy of the list a (Fisher-Yates with rnd(): faster than random.shuffle)"""
    b = list(a)
    for i in range(len(b) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        b[i], b[j] = b[j], b[i]
    return b


def add(n, c, plant, edges, tree_ok=False):
    """edges = (us, vs, ws); tree_ok: emit() already proved the roads form a tree
    (par[i] < i, relabelled by a permutation)"""
    us, vs, ws = edges
    assert 1 <= n <= MAXN and len(us) == len(vs) == len(ws) == n - 1
    assert sorted(c) == list(range(1, n + 1))
    assert len(plant) == n and set(plant) <= {"0", "1"} and "1" in plant
    if n > 1:
        assert 1 <= min(us) and max(us) <= n and 1 <= min(vs) and max(vs) <= n
        assert all(map(int.__ne__, us, vs)) and 1 <= min(ws) and max(ws) <= MAXW
    if not tree_ok:             # n - 1 roads that connect all towns: a tree
        check_tree(n, us, vs)
    lines = [str(n), " ".join(map(str, c)), plant] + list(map("{} {} {}".format, us, vs, ws))
    tests.append("\n".join(lines) + "\n")


def add_list(n, c, plant, roads):
    """roads given as (u, v, w) triples (samples)"""
    add(n, c, plant, tuple(map(list, zip(*roads))) if roads else ([], [], []))


def check_tree(n, us, vs):
    adj = [[] for _ in range(n + 1)]
    for u, v in zip(us, vs):
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * (n + 1)
    seen[1] = True
    stack = [1]
    cnt = 1
    while stack:
        for u in adj[stack.pop()]:
            if not seen[u]:
                seen[u] = True
                cnt += 1
                stack.append(u)
    assert cnt == n


# ---------------------------------------------------------------- tree shapes on 0..n-1 (par[i] < i)
def shape(kind, n):
    par = [-1] * n
    if kind == "random":
        for i in range(1, n):
            par[i] = int(rnd() * i)
    elif kind == "deep":
        for i in range(1, n):
            par[i] = ri(max(0, i - 4), i - 1)
    elif kind == "path":
        for i in range(1, n):
            par[i] = i - 1
    elif kind == "caterpillar":
        spine = max(1, n // 2)
        for i in range(1, n):
            par[i] = i - 1 if i < spine else int(rnd() * spine)
    elif kind == "spurs":           # spine 0..h-1, vertex h + j hangs below spine vertex j
        h = (n + 1) // 2
        for i in range(1, n):
            par[i] = i - 1 if i < h else i - h
    elif kind == "star":
        for i in range(1, n):
            par[i] = 0
    elif kind == "broom":
        h = n // 2
        for i in range(1, n):
            par[i] = i - 1 if i <= h else h
    elif kind == "binary":
        for i in range(1, n):
            par[i] = (i - 1) // 2
    elif kind == "long-arms":       # a few long paths out of vertex 0
        arms = 5
        for i in range(1, n):
            par[i] = i - arms if i > arms else 0
    else:
        raise ValueError(kind)
    return par


def weights(kind, n, par, plants):
    w = [0] * n
    for i in range(1, n):
        if kind == "rand":
            w[i] = ri(1, MAXW)
        elif kind == "max":
            w[i] = MAXW
        elif kind == "small":
            w[i] = ri(1, 10)
        elif kind == "spur":        # roads into a plant leaf are short, the rest long
            w[i] = ri(1, 3) if i in plants else ri(30000, 99999)
        else:
            raise ValueError(kind)
    return w


def has_child(n, par):
    ch = [False] * n
    for i in range(1, n):
        ch[par[i]] = True
    return ch


def choose_plants(kind, n, par, cnt):
    ch = has_child(n, par)
    leaves = [v for v in range(n) if not ch[v]]
    if kind == "random":
        return set(random.sample(range(n), cnt))
    if kind == "leaves":
        return set(random.sample(leaves, min(cnt, len(leaves))))
    raise ValueError(kind)


def choose_order(kind, n, par, plants, start=None):
    """order of joining towns (0-based vertices); start = c_1 if given"""
    ch = has_child(n, par)
    if start is None:
        start = int(rnd() * n)
    if kind == "random":
        return [start] + shuf([v for v in range(n) if v != start])
    if kind == "leaves":            # non-plant leaves first, then the plants, then everything else
        lv = shuf([v for v in range(n) if not ch[v] and v != start and v not in plants])
        pl = shuf(sorted(v for v in plants if v != start))
        seen = set(lv) | set(pl) | {start}
        rest = shuf([v for v in range(n) if v not in seen])
        return [start] + lv + pl + rest
    if kind == "bfs":               # every new town is next to the network
        adj = [[] for _ in range(n)]
        for i in range(1, n):
            adj[i].append(par[i])
            adj[par[i]].append(i)
        seen = [False] * n
        seen[start] = True
        frontier = [start]
        out = []
        while frontier:
            j = int(rnd() * len(frontier))
            frontier[j], frontier[-1] = frontier[-1], frontier[j]
            v = frontier.pop()
            out.append(v)
            for u in adj[v]:
                if not seen[u]:
                    seen[u] = True
                    frontier.append(u)
        return out
    if kind == "zigzag":            # path 0..n-1: start in the middle, then the two ends inwards
        lo, hi = 0, n - 1
        out = [start]
        while lo <= hi:
            for v in (lo, hi):
                if v != start and v not in out[-2:]:
                    out.append(v)
            lo += 1
            hi -= 1
        assert sorted(out) == list(range(n))
        return out
    raise ValueError(kind)


def emit(n, par, w, plants, order, keep_one=None):
    """random labels; keep_one: vertex that gets label 1 (else a vertex that is not c_1)"""
    lab = shuf(list(range(1, n + 1)))
    if n > 1:
        one = keep_one
        if one is None:             # town 1 is never c_1 here (c_1 = 1 is tested on its own)
            one = order[0]
            while one == order[0]:
                one = int(rnd() * n)
        j = lab.index(1)
        lab[j], lab[one] = lab[one], lab[j]
    assert sorted(lab) == list(range(1, n + 1))
    assert n == 1 or (min(par[1:]) >= 0 and all(map(int.__lt__, par[1:], range(1, n))))
    c = [lab[v] for v in order]
    plant = ["0"] * n
    for v in plants:
        plant[lab[v] - 1] = "1"
    # roads in the order of the label of their lower end (labels are random), random direction
    idx = sorted(range(1, n), key=lab.__getitem__)
    lo = list(map(lab.__getitem__, idx))
    hi = [lab[par[i]] for i in idx]
    flip = format(random.getrandbits(n - 1), "0%db" % (n - 1)) if n > 1 else ""
    us = [b if f == "1" else a for a, b, f in zip(lo, hi, flip)]
    vs = [a if f == "1" else b for a, b, f in zip(lo, hi, flip)]
    ws = [w[i] for i in idx]
    add(n, c, "".join(plant), (us, vs, ws), tree_ok=True)


def build(n, kind, wkind="rand", pkind="random", pcnt=3, okind="random", start=None, c1_plant=False,
          one=None):
    par = shape(kind, n)
    if pkind == "spurs":            # plants = the hanging leaves of some spine vertices
        h = (n + 1) // 2
        plants = set(random.sample(range(h, n), min(pcnt, n - h))) if n > h else {0}
    else:
        plants = choose_plants(pkind, n, par, pcnt)
    if start is None:
        cand = [v for v in range(n) if v not in plants] or [0]
        start = cand[int(rnd() * len(cand))]
    if c1_plant:
        plants.add(start)
    w = weights(wkind, n, par, plants)
    order = choose_order(okind, n, par, plants, start)
    emit(n, par, w, plants, order, one)


# samples
add_list(7, [3, 6, 1, 5, 2, 7, 4], "0000101",
    [(1, 2, 4), (2, 3, 2), (2, 4, 3), (4, 5, 1), (4, 6, 5), (1, 7, 6)])
add_list(5, [3, 2, 4, 1, 5], "10001", [(1, 2, 3), (2, 3, 4), (3, 4, 1), (4, 5, 2)])
add_list(1, [1], "1", [])
add_list(4, [2, 4, 1, 3], "0100", [(1, 2, 7), (2, 3, 9), (2, 4, 1)])
add_list(5, [2, 5, 3, 1, 4], "10000", [(1, 3, 5), (3, 2, 2), (3, 4, 4), (4, 5, 1)])
# hidden: small (brute checks these)
add_list(2, [2, 1], "01", [(1, 2, MAXW)])
build(12, "random", "small", "random", 2, "leaves")
build(40, "spurs", "spur", "spurs", 3, "leaves")
build(300, "random", "rand", "random", 1, "random")
build(2000, "caterpillar", "spur", "leaves", 4, "leaves")
build(3000, "path", "small", "random", 2, "zigzag", start=1500)
build(9000, "deep", "rand", "random", 5, "random", c1_plant=True)
# hidden: big
build(MAXN, "path", "rand", "random", 2, "zigzag", start=MAXN // 2)
build(MAXN, "path", "max", "random", 1, "random")
build(MAXN, "path", "spur", "random", 30, "leaves", start=7)
build(MAXN, "spurs", "spur", "spurs", 5, "leaves")
build(MAXN, "random", "rand", "random", 3, "leaves")
build(MAXN, "random", "spur", "leaves", 20, "leaves")
build(MAXN, "deep", "spur", "leaves", 50, "leaves")
build(MAXN, "caterpillar", "rand", "leaves", 3, "leaves")
build(MAXN, "broom", "spur", "leaves", 10, "leaves", start=0)
build(MAXN, "star", "rand", "random", 1, "random")
build(MAXN, "binary", "spur", "leaves", 8, "leaves")
build(MAXN, "long-arms", "rand", "random", 2, "leaves")
build(MAXN, "random", "rand", "random", MAXN // 10, "bfs")
build(MAXN, "deep", "max", "random", 1, "random", c1_plant=True)
build(MAXN, "path", "max", "random", 1, "random", start=0, one=MAXN - 1)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
