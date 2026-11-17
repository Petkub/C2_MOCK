# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Stations form a tree (p_i < i). The answer is the greedy over group tops (deepest first). Every big tree is deep
# (paths, near-paths, long branches, long spines) and about half of the group members are spread over the whole
# tree, so that climbing parent by parent is too slow. The other groups are local with 3+ stations on different
# branches, so that splitting a group into pairs or taking the top of only its first and last station gives a
# different answer, and the answer stays large.
import os, random

random.seed(20231)
rnd = random.random
MAXN, MAXM, MAXS = 200000, 100000, 200000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(par, groups):
    """par[i] for i = 2..n (par[0], par[1] unused); groups: list of lists of stations"""
    n = len(par) - 1
    m = len(groups)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM
    assert all(1 <= p < i for i, p in enumerate(par[2:], 2))
    assert sum(len(g) for g in groups) <= MAXS
    assert min(len(g) for g in groups) >= 1
    flat = [c for g in groups for c in g]
    assert 1 <= min(flat) and max(flat) <= n
    lines = ["%d %d" % (n, m), " ".join(map(str, par[2:]))]
    lines += ["%d %s" % (len(g), " ".join(map(str, g))) for g in groups]
    tests.append("\n".join(lines) + "\n")


# ---------------------------------------------------------------- trees (par[i] < i)
def tree(n, kind, w=4):
    if kind == "path":
        body = [i - 1 for i in range(2, n + 1)]
    elif kind == "win":                           # narrow random tree, depth about 2n / (w + 1)
        body = [i - 1 - int(rnd() * min(w, i - 1)) for i in range(2, n + 1)]
    elif kind == "cat":                           # spine 1..w, the rest hang from spine stations
        body = [i - 1 if i <= w else 1 + int(rnd() * w) for i in range(2, n + 1)]
    elif kind == "broom":                         # path 1..w, then a star around w
        body = [i - 1 if i <= w else w for i in range(2, n + 1)]
    elif kind == "two":                           # two long branches from station 1
        body = [1 if i <= 3 else i - 2 for i in range(2, n + 1)]
    elif kind == "branches":                      # w long branches from station 1
        body = [1 if i <= w + 1 else i - w for i in range(2, n + 1)]
    elif kind == "bumpy":                         # a path with rare short side steps
        body = [i - 1 if i <= 2 or rnd() < 0.97 else i - 1 - ri(1, min(30, i - 2)) for i in range(2, n + 1)]
    elif kind == "comb":                          # spine 1..w, then chains of 50 stations hanging from the spine
        body = [i - 1 if i <= w or (i - w - 1) % 50 else 1 + int(rnd() * w) for i in range(2, n + 1)]
    elif kind == "fork":                          # path 1..w, then two long branches from station w
        body = [i - 1 if i <= w else (w if i <= w + 2 else i - 2) for i in range(2, n + 1)]
    elif kind == "rand":
        body = [1 + int(rnd() * (i - 1)) for i in range(2, n + 1)]
    else:                                         # "bin": complete binary tree
        body = [i // 2 for i in range(2, n + 1)]
    return [0, 0] + body


def children(par):
    ch = [[] for _ in par]
    for i in range(2, len(par)):
        ch[par[i]].append(i)
    return ch


def walk_down(ch, v, steps):
    for _ in range(steps):
        c = ch[v]
        if not c:
            break
        v = c[int(rnd() * len(c))]
    return v


# ---------------------------------------------------------------- groups
def g_random(n, m, kmin, kmax):
    return [[1 + int(rnd() * n) for _ in range(ri(kmin, kmax))] for _ in range(m)]


def g_local(par, ch, m, kmax, reach, hi=0):
    """members near a random station (one of 1..hi if hi is given): walk up a bit, then down a bit"""
    n = len(par) - 1
    out = []
    for _ in range(m):
        v = ri(1, hi or n)
        for _ in range(ri(0, reach)):
            if v > 1:
                v = par[v]
        out.append([walk_down(ch, v, ri(0, 2 * reach)) for _ in range(ri(1, kmax))])
    return out


def g_spread(par, ch, m, k, reach):
    """first and last members close together (same small subtree), middle ones far away:
    the top of only the first and last member is too deep, pairs (c1, ci) differ from the group"""
    n = len(par) - 1
    out = []
    for _ in range(m):
        v = ri(1, n)
        a = walk_down(ch, v, ri(0, reach))
        b = walk_down(ch, v, ri(0, reach))
        mid = []
        for _ in range(k - 2):
            u = v
            for _ in range(ri(1, 3 * reach)):
                if u > 1:
                    u = par[u]
            mid.append(walk_down(ch, u, ri(0, 3 * reach)))
        out.append([a] + mid + [b])
    return out


def g_star_groups(par, ch, m, k, reach):
    """a station s and k - 1 members in different child subtrees of s: the whole group is cut by s alone"""
    n = len(par) - 1
    cand = [v for v in range(1, n + 1) if len(ch[v]) >= 2]
    out = []
    for _ in range(m):
        s = cand[int(rnd() * len(cand))]
        g = [walk_down(ch, ch[s][int(rnd() * len(ch[s]))], ri(0, reach)) for _ in range(k)]
        out.append(g)
    return out


def g_cross(n, m):
    """for the "two" tree: one member deep in the even branch, one deep in the odd branch (the top is station 1)"""
    return [[2 * ri(n // 4, n // 2), 2 * ri(n // 4, n // 2) - 1] for _ in range(m)]


def mix(*lists):
    g = [x for l in lists for x in l]
    random.shuffle(g)
    return g


def fit(groups):
    """drop groups until the size limits hold"""
    total = sum(len(g) for g in groups)
    while len(groups) > MAXM or total > MAXS:
        total -= len(groups.pop())
    return groups


def big(par, parts):
    add(par, fit(mix(*parts)))


# ---------------------------------------------------------------- samples
add([0, 0, 1, 1, 2, 2, 3, 3, 5, 6], [[4, 8], [9], [7, 6, 3], [4, 5, 9]])
add([0, 0, 1, 2, 3, 2, 5], [[3, 5], [4, 6], [1, 2]])
add([0, 0, 1, 2, 3, 4, 5, 6], [[4, 4, 4], [2, 6], [7, 1], [3, 6, 5]])
add([0, 0, 1, 1, 1, 2, 2, 4, 4, 8, 8, 8], [[9, 10, 11], [5], [6, 7, 3], [11, 6], [2, 4, 8]])
add([0, 0, 1, 1, 2, 3, 3, 3, 7], [[8, 4], [2, 3], [5, 6], [6, 8, 7], [4, 4]])

# ---------------------------------------------------------------- small hidden (brute checks these)
add([0, 0, 1], [[1, 2]])
add([0, 0, 1], [[2], [2, 2], [1]])
for s in range(4):
    n = ri(6, 16)
    par = tree(n, ["rand", "win", "cat", "bin"][s], 3)
    ch = children(par)
    if s % 2:
        add(par, mix(g_random(n, ri(2, 5), 1, 4), g_spread(par, ch, 2, 3, 1)))
    else:
        add(par, mix(g_random(n, ri(3, 7), 1, 5)))

# ---------------------------------------------------------------- medium, shallow trees (not max size)
par = tree(40000, "rand")
ch = children(par)
add(par, fit(mix(g_random(40000, 14000, 2, 3), g_spread(par, ch, 7000, 4, 2))))
par = tree(40000, "bin")
ch = children(par)
add(par, fit(mix(g_local(par, ch, 17000, 4, 3), g_star_groups(par, ch, 3500, 3, 4))))

# ---------------------------------------------------------------- big (N = 200 000), deep trees
N = MAXN
BIG = [
    ("path", 0, lambda par, ch: [g_random(N, 100000, 2, 2)]),                 # pairs on a path
    ("path", 0, lambda par, ch: [g_random(N, 50000, 2, 2), g_spread(par, ch, 33000, 3, 1)]),
    ("bumpy", 0, lambda par, ch: [g_random(N, 40000, 2, 3), g_spread(par, ch, 15000, 4, 4),
                                  g_star_groups(par, ch, 10000, 3, 3)]),
    ("bumpy", 0, lambda par, ch: [g_random(N, 55000, 2, 2), g_local(par, ch, 45000, 2, 3)]),
    ("win", 2, lambda par, ch: [g_random(N, 60000, 2, 2), g_local(par, ch, 40000, 3, 4)]),
    ("win", 2, lambda par, ch: [g_random(N, 15000, 6, 6), g_spread(par, ch, 25000, 3, 6),
                                [[ri(1, N)] for _ in range(20000)]]),
    ("two", 0, lambda par, ch: [g_random(N, 60000, 2, 2), g_spread(par, ch, 25000, 3, 4)]),
    # the long climbs from deep stations meet no closed station before the shallow part
    ("two", 0, lambda par, ch: [g_cross(N, 70000), g_local(par, ch, 30000, 3, 8, N // 10)]),
    ("fork", N // 2, lambda par, ch: [g_random(N, 30000, 2, 4), g_spread(par, ch, 20000, 3, 5),
                                      g_local(par, ch, 20000, 3, 3)]),
    ("branches", 3, lambda par, ch: [g_random(N, 65000, 2, 2), g_spread(par, ch, 23000, 3, 5)]),
    ("cat", N * 7 // 10, lambda par, ch: [g_random(N, 60000, 2, 2), g_star_groups(par, ch, 25000, 3, 1)]),
    ("cat", N * 8 // 10, lambda par, ch: [g_random(N, 50000, 2, 2), g_spread(par, ch, 30000, 3, 2)]),
    ("broom", N * 3 // 4, lambda par, ch: [g_random(N, 60000, 2, 2), g_star_groups(par, ch, 15000, 3, 0),
                                           [[ri(1, N)] for _ in range(20000)]]),
    ("comb", N * 7 // 10, lambda par, ch: [g_random(N, 60000, 2, 2), g_spread(par, ch, 15000, 4, 4),
                                           g_local(par, ch, 10000, 3, 6)]),
]
for kind, w, parts in BIG:
    par = tree(N, kind, w)
    ch = children(par)
    big(par, parts(par, ch))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
