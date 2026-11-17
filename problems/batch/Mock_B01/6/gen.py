# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Input: N, then row i (i = 1..N-1) holds a[i][i+1..N]; a > 0: no passage, build cost a;
# a < 0: passage exists, closing cost -a.
# Most big tests plant a valid passage set for a start room s != 1 (a random tree whose subtrees are
# cyclic intervals, plus free passages from rooms to their descendants), then flip a few pairs.
# This makes the best start unique and far from room 1 (kills the fixed-start method), keeps many
# passages from a room into its later child subtrees (kills closing them), and makes the
# "walk around the circle" chain expensive.
import os, random

random.seed(20250125)
rnd = random.random
MAXN, MAXA = 500, 10000
tests = []


def ri(lo, hi):
    return lo + int(rnd() * (hi - lo + 1))


def add(a):
    n = len(a)
    assert 2 <= n <= MAXN
    rows = []
    for i in range(n - 1):
        row = a[i][i + 1:]
        assert all(v != 0 and -MAXA <= v <= MAXA for v in row)
        rows.append(" ".join(map(str, row)))
    tests.append("%d\n" % n + "".join(r + "\n" for r in rows))


def text(s):
    t = list(map(int, s.split()))
    n = t[0]
    a = [[0] * n for _ in range(n)]
    p = 1
    for i in range(n):
        for j in range(i + 1, n):
            a[i][j] = a[j][i] = t[p]
            p += 1
    assert p == len(t)
    add(a)


def build(n, present, cost):
    """present(i, j) -> bool (passage exists now), cost(i, j) -> 1..MAXA"""
    a = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            c = cost(i, j)
            a[i][j] = a[j][i] = -c if present(i, j) else c
    return a


def rand_test(n, pneg, lo=1, hi=MAXA):
    add(build(n, lambda i, j: rnd() < pneg, lambda i, j: ri(lo, hi)))


def tree(n, shape):
    """parent of each position 1..n-1 in visiting order; subtrees are intervals of positions.
    shape: 'rand' (uniform on the stack), 'deep' (near the top), 'wide' (near the root),
    'star', 'path', 'bin' (each room at most two children)"""
    par = [-1] * n
    kids = [0] * n
    st = [0]
    for t in range(1, n):
        if shape == "star":
            d = 0
        elif shape == "path":
            d = len(st) - 1
        elif shape == "deep":
            d = max(0, len(st) - 1 - int(rnd() * 3))
        elif shape == "wide":
            d = min(len(st) - 1, int(rnd() * 3))
        elif shape == "bin":
            d = len(st) - 1
            while kids[st[d]] >= 2 or (d > 0 and rnd() < 0.3):
                d -= 1
            assert d >= 0
        else:
            d = int(rnd() * len(st))
        del st[d + 1:]
        par[t] = st[d]
        kids[st[d]] += 1
        st.append(t)
    return par


def planted(n, s, shape, noise, back, lo=1, hi=MAXA, tree_cost=None):
    """a valid passage set for start room s (0-based) with tree `shape`; each pair is flipped with
    probability noise; a passage from a room to a non-child descendant exists with probability back"""
    par = tree(n, shape)
    size = [1] * n
    for t in range(n - 1, 0, -1):
        size[par[t]] += size[t]
    pos = [(v - s) % n for v in range(n)]  # room -> position in the visiting order

    def present(i, j):
        x, y = sorted((pos[i], pos[j]))
        if par[y] == x:
            ok = True
        elif y < x + size[x]:
            ok = rnd() < back
        else:
            ok = False
        return ok != (rnd() < noise)

    def cost(i, j):
        if tree_cost is not None:
            x, y = sorted((pos[i], pos[j]))
            if par[y] == x:
                return tree_cost
        return ri(lo, hi)

    return build(n, present, cost)


# samples
text("4 -3 -7 6 8 -5 -4")
text("5 -1 -6 3 -2 7 4 9 2 4 7")
text("6 -12 28 11 41 25 33 -25 -2 -30 20 1 9 48 45 39")
text("6 3 11 17 8 3 27 18 1 19 10 17 14 14 8 27")
text("6 -3 -9 5 27 -27 3 21 17 2 -12 -29 14 27 23 23")
# hidden: small and medium (brute checks these)
text("2 7")
text("2 -10000")
text("3 5 -4 6")
add(planted(6, 4, "rand", 0.15, 0.5, 1, 20))
add(planted(9, 5, "rand", 0.1, 0.5, 1, 50))
add(planted(12, 7, "bin", 0.1, 0.6, 1, 100))
rand_test(10, 0.5, 1, 30)
add(planted(14, 3, "wide", 0.08, 0.7))
# hidden: big (N = 500)
N = MAXN
add(planted(N, ri(100, 400), "rand", 0.001, 0.5))
add(planted(N, ri(100, 400), "deep", 0.001, 0.5))
add(planted(N, ri(100, 400), "wide", 0.002, 0.7))
add(planted(N, ri(100, 400), "bin", 0.003, 0.5))
add(planted(N, ri(100, 400), "star", 0.001, 0.5))
add(planted(N, ri(100, 400), "path", 0.005, 0.5))
add(planted(N, ri(1, N - 1), "rand", 0.002, 0.9, 1, MAXA, MAXA))
add(planted(N, ri(1, N - 1), "wide", 0.0005, 0.95, 5000, MAXA))
add(planted(N, ri(1, N - 1), "deep", 0.01, 0.3))
add(planted(N, ri(1, N - 1), "rand", 0.03, 0.5))
add(planted(N, 0, "rand", 0.001, 0.5))
add(planted(N, N - 1, "wide", 0.001, 0.8))
rand_test(N, 0.5)
rand_test(N, 0.9)
rand_test(N, 0.1)
add(build(N, lambda i, j: True, lambda i, j: ri(1, MAXA)))                     # every passage exists
add(build(N, lambda i, j: False, lambda i, j: ri(1, MAXA)))                    # no passage at all
add(build(N, lambda i, j: (j - i) % N not in (1, N - 1), lambda i, j: MAXA))   # all but the circle
add(build(N, lambda i, j: (i + j) % 2 == 1, lambda i, j: ri(9000, MAXA)))      # bipartite by parity

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
