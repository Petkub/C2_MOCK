# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A tree of N towns; for each start town: the longest simple trip, ties broken by the lexicographically smallest
# label sequence. Every longest trip passes through a centre of the tree, so the big tests stress: many branches of
# the centre that tie in height, label sequences that agree on a long prefix (equal labels everywhere or labels in
# {1, 2}), both the one-centre and the two-centre case, deep paths (sums near 10^14) and town numbers shuffled so a
# "smaller town number" tie-break is wrong half of the time.
import os, random

random.seed(20231202)
rnd = random.random
MAXN, MAXL = 100000, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, edges, shuffle=True):
    """edges: list of (a, b, l) on towns 0..n-1 (or 1..n when shuffle is False)"""
    assert 2 <= n <= MAXN and len(edges) == n - 1
    if shuffle:
        perm = list(range(1, n + 1))
        random.shuffle(perm)
        edges = [(perm[a], perm[b], l) if rnd() < 0.5 else (perm[b], perm[a], l) for a, b, l in edges]
        random.shuffle(edges)
    # check: a tree on 1..n, labels in range
    par = list(range(n + 1))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b, l in edges:
        assert 1 <= a <= n and 1 <= b <= n and a != b and 1 <= l <= MAXL
        ra, rb = find(a), find(b)
        assert ra != rb
        par[ra] = rb
    tests.append(f"{n}\n" + "".join(f"{a} {b} {l}\n" for a, b, l in edges))


HI = False      # when set, labels are the L largest values (near 10^9): same ties, sums past the int range


def lab(L):
    return MAXL - L + ri(1, L) if HI else ri(1, L)


def random_tree(n, L, window=None):
    """town i joins a random earlier town (within the last `window` towns if given)"""
    e = []
    for i in range(1, n):
        lo = 0 if window is None else max(0, i - window)
        e.append((i, ri(lo, i - 1), lab(L)))
    return e


def spider(n, legs, L, centre_label=None):
    """a centre with `legs` legs of (almost) equal length"""
    e, nxt = [], 1
    per = (n - 1) // legs
    extra = (n - 1) - per * legs
    for k in range(legs):
        prev = 0
        for j in range(per + (1 if k < extra else 0)):
            l = centre_label if (j == 0 and centre_label is not None) else lab(L)
            e.append((nxt, prev, l))
            prev = nxt
            nxt += 1
    return e


def same_prefix_legs(n, legs, L, depth_diff):
    """legs whose label sequences agree except near the end (the decision comes late)"""
    per = (n - 1) // legs
    base = [lab(L) for _ in range(per)]
    e, nxt = [], 1
    for k in range(legs):
        seq = base[:]
        for _ in range(depth_diff):
            p = per - 1 - int(rnd() * min(per, 30))
            seq[p] = lab(L)
        prev = 0
        for j in range(per):
            e.append((nxt, prev, seq[j]))
            prev = nxt
            nxt += 1
    while nxt < n:                       # leftovers hang off the centre as short legs
        e.append((nxt, 0, lab(L)))
        nxt += 1
    return e


def binary_like(n, L):
    return [(i, (i - 1) // 2, lab(L)) for i in range(1, n)]


def caterpillar(n, spine, L):
    e = [(i, i - 1, lab(L)) for i in range(1, spine)]
    for i in range(spine, n):
        e.append((i, ri(0, spine - 1), lab(L)))
    return e


def doubled_legs(n, legs, L):
    """from the centre, legs that split into identical twins: many equal sequences"""
    e, nxt = [], 1
    depth = max(2, (n - 1) // (legs * 3))
    while True:
        need = 1 + 2 * depth
        if nxt + need > n:
            break
        trunk = nxt
        e.append((trunk, 0, lab(L)))
        nxt += 1
        seq = [lab(L) for _ in range(depth)]
        for _ in range(2):
            prev = trunk
            for j in range(depth):
                e.append((nxt, prev, seq[j]))
                prev = nxt
                nxt += 1
    while nxt < n:
        e.append((nxt, ri(0, nxt - 1), lab(L)))
        nxt += 1
    return e


def two_centres(n, L):
    """two adjacent centres a = 0 and b = 1, each with several legs of the same length"""
    e = [(1, 0, lab(L))]
    nxt = 2
    legs = 6
    per = (n - 2) // (2 * legs)
    for root in (0, 1):
        for k in range(legs):
            prev = root
            for j in range(per):
                e.append((nxt, prev, lab(L)))
                prev = nxt
                nxt += 1
    while nxt < n:
        e.append((nxt, ri(2, nxt - 1), lab(L)))   # short twigs, never longer than the legs on average
        nxt += 1
    return e


# samples (town numbers as written)
add(7, [(1, 2, 5), (1, 3, 2), (2, 4, 1), (3, 5, 3), (1, 6, 2), (6, 7, 7)], False)
add(5, [(1, 2, 4), (2, 3, 4), (3, 4, 4), (4, 5, 4)], False)
add(2, [(2, 1, 1000000000)], False)
add(8, [(4, 1, 3), (4, 2, 3), (4, 3, 2), (1, 5, 1), (2, 6, 1), (3, 7, 9), (5, 8, 2)], False)
add(9, [(5, 1, 2), (5, 2, 2), (5, 3, 2), (1, 4, 6), (2, 6, 1), (3, 7, 1), (6, 8, 4), (7, 9, 4)], False)
# hidden: small and medium (brute checks these)
add(3, [(0, 1, 7), (1, 2, 7)])
add(12, random_tree(12, 2))
add(40, random_tree(40, 3, 4))
add(200, spider(200, 7, 2))
add(500, same_prefix_legs(500, 6, 2, 1))
add(800, two_centres(800, 2))
add(1500, random_tree(1500, 2, 30))
add(2000, doubled_legs(2000, 20, 3))
# hidden: big (N = 100000)
add(N, [(i, i - 1, MAXL) for i in range(1, N)])                        # a path, all labels 10^9
add(N, [(i, 0, 1) for i in range(1, N)])                               # a star, equal labels
add(N, random_tree(N, MAXL))
add(N, random_tree(N, 2))
HI = True
add(N, random_tree(N, 2, 3))                                           # deep random
HI = False
add(N, spider(N, 300, 2))
HI = True
add(N, spider(N, 3, 1))                                                # three equal legs, equal labels
HI = False
add(N, spider(N, 50, MAXL, 7))
add(N, same_prefix_legs(N, 40, 3, 1))
HI = True
add(N, same_prefix_legs(N, 4, 2, 2))
HI = False
add(N, same_prefix_legs(N, 1000, 2, 1))
add(N, binary_like(N, 2))
add(N, caterpillar(N, 50000, 2))
HI = True
add(N, doubled_legs(N, 100, 2))
HI = False
add(N, doubled_legs(N, 5, 1000))
HI = True
add(N, two_centres(N, 2))
HI = False
add(N, two_centres(N, MAXL))
add(N, random_tree(N, 3, 50))
add(N, [(i, i - 1, ri(MAXL - 3, MAXL)) for i in range(1, N)])         # a path, labels near 10^9

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
    assert len(t) <= 3_000_000
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
