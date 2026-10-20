# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(60401)
MAXN = MAXM = 100_000
MAXC = 10**9
tests = []


def ri(lo, hi):
    return lo + int(random.random() * (hi - lo + 1))


def add(n, k, col, roads, relabel=True):
    m = len(roads)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM and 1 <= k <= n and len(col) == n
    assert 1 <= min(col) and max(col) <= MAXC
    us, vs = zip(*roads)
    assert 1 <= min(us) and max(us) <= n and 1 <= min(vs) and max(vs) <= n
    assert not any(map(int.__eq__, us, vs))
    if relabel:                                  # hide the construction order behind random house numbers
        r = random.random
        key = [0.0] + [r() for _ in range(n)]
        lab = [0] + sorted(range(1, n + 1), key=key.__getitem__)
        newcol = [0] * (n + 1)
        for i, c in zip(lab[1:], col):
            newcol[i] = c
        col = newcol[1:]
        us = [lab[u] for u in us]
        vs = [lab[v] for v in vs]
    tests.append(f"{n} {m} {k}\n" + " ".join(map(str, col)) + "\n"
                 + "".join([f"{u} {v}\n" for u, v in zip(us, vs)]))


def orient(u, v, how):
    """how: 'r' random, 'u' keep (u, v), 's' swap"""
    if how == "s" or (how == "r" and random.random() < 0.5):
        return (v, u)
    return (u, v)


def distinct_colours(n, hi=MAXC):
    seen, out, r = set(), [], random.random
    while len(out) < n:         # each draw adds at most one colour, so n - len(out) draws never overshoot
        new = [c for c in dict.fromkeys([1 + int(r() * hi) for _ in range(n - len(out))]) if c not in seen]
        seen.update(new)
        out += new
    return out


def rnd_colours(n, hi):
    return [ri(1, hi) for _ in range(n)]


def chain(n, how):
    """road j joins the district of houses 1..j with the lone house j + 1 (house j + 1 first when how = 'u')"""
    r, roads = random.random, []
    for j in range(1, n):           # = orient(j + 1, ri(1, j) if r() < 0.3 else j, how), written out (faster)
        v = 1 + int(r() * j) if r() < 0.3 else j
        roads.append((v, j + 1) if how == "s" or (how == "r" and r() < 0.5) else (j + 1, v))
    return roads


def star(n, how):
    return [orient(1, j, how) for j in range(2, n + 1)]


def balanced(n):
    """merge districts in pairs, then pairs of pairs, ... (equal sizes every time)"""
    groups = [[i] for i in range(1, n + 1)]
    roads = []
    while len(groups) > 1:
        nxt = []
        for i in range(0, len(groups) - 1, 2):
            a, b = groups[i], groups[i + 1]
            roads.append(orient(random.choice(a), random.choice(b), "r"))
            nxt.append(a + b if len(a) >= len(b) else b + a)
        if len(groups) % 2:
            nxt.append(groups[-1])
        groups = nxt
    return roads


def rnd_roads(n, m):
    roads = []
    for _ in range(m):
        u = ri(1, n)
        v = ri(1, n - 1)
        v += v >= u
        roads.append((u, v))
    return roads


def shuffled(a):
    r = random.random
    return sorted(a, key=lambda _: r())


def rnd_tree(n):
    roads = [orient(j, ri(max(1, j - 1 - ri(0, 50)), j - 1), "r") for j in range(2, n + 1)]
    return shuffled(roads)


def two_fronts(n, how):
    """two districts grow side by side (each road adds one lone house to one of them), then they meet"""
    roads = []
    for j in range(3, n + 1):
        side = 1 if random.random() < 0.5 else 2
        roads.append(orient(j, side, how))
    roads.append((1, 2))
    return roads


def pad(roads, n, m):
    """fill up to m roads with roads inside existing districts or repeated roads"""
    roads = roads[:]
    while len(roads) < m:
        u, v = random.choice(roads)
        roads.insert(ri(len(roads) // 2, len(roads)), (v, u) if random.random() < 0.5 else (u, v))
    return roads[:m]


# samples
add(6, 2, [3, 3, 5, 7, 7, 8], [(1, 2), (4, 5), (2, 3), (5, 6), (5, 4), (6, 3)], relabel=False)
add(5, 3, [1, 2, 1, 2, 3], [(1, 2), (3, 4), (2, 3), (4, 5)], relabel=False)
add(4, 1, [10, 20, 10, 30], [(1, 2), (2, 1), (3, 4)], relabel=False)
add(4, 4, [1000000000, 5, 5, 7], [(1, 2), (3, 4), (2, 3)], relabel=False)
add(6, 3, [2, 6, 2, 9, 6, 4], [(1, 3), (2, 5), (3, 5), (6, 4), (4, 1)], relabel=False)

# hidden: small (checked by recounting from scratch)
add(2, 2, [1, 2], [(2, 1)])
add(2, 2, [7, 7], [(1, 2), (2, 1), (1, 2)])
add(10, 3, rnd_colours(10, 4), rnd_roads(10, 15))
add(50, 4, rnd_colours(50, 5), rnd_roads(50, 80))
add(1000, 200, distinct_colours(1000), pad(chain(1000, "r"), 1000, 1500))
add(2000, 150, rnd_colours(2000, 300), star(2000, "r"))
add(1500, 700, distinct_colours(1500), balanced(1500))

# hidden: large
N = MAXN
add(N, 50_000, distinct_colours(N, 10**6), pad(chain(N, "r"), N, N))
add(N, 70_000, distinct_colours(N, 10**6), pad(chain(N, "u"), N, N))
add(N, 30_000, distinct_colours(N, 10**6), pad(chain(N, "s"), N, N))
add(N, 40_000, rnd_colours(N, N), pad(star(N, "r"), N, N))
add(N, N // 4, distinct_colours(N), pad(balanced(N), N, N))
add(N, 1000, rnd_colours(N, N), rnd_roads(N, N))
add(N, 50, rnd_colours(N, 50), rnd_roads(N, N))                 # few colours
roads = []                                                      # ten chains grow together, then join
for j in range(1, N // 10):
    for t in range(10):
        roads.append(orient(t * (N // 10) + j + 1, t * (N // 10) + ri(1, j), "r"))
for t in range(1, 10):
    roads.append(orient(ri(1, t * (N // 10)), t * (N // 10) + ri(1, N // 10), "r"))
add(N, 20_000, distinct_colours(N), pad(roads, N, N))
add(N, 1, rnd_colours(N, MAXC), pad(chain(N, "r"), N, N))
add(N, 30_000, [i % 30_000 + 1 for i in range(N)], pad(chain(N, "r"), N, N))   # exactly 30000 colours in all
add(N, 5_000, rnd_colours(N, 2 * N), pad(rnd_tree(N), N, N))
half = N // 2                                                   # a chain over half the houses, every other
roads = []                                                      # road inside a district or repeated
for r in chain(half, "r"):
    roads.append(r)
    roads.append(random.choice(roads))
add(N, 25_000, distinct_colours(N, 10**6), roads[:N])
add(N, 45_000, distinct_colours(N), pad(two_fronts(N, "r"), N, N))
add(N, N, distinct_colours(N), pad(chain(N, "r"), N, N))        # only the whole town reaches K
add(N, 60_000, rnd_colours(N, 10 * N), pad(two_fronts(N, "r"), N, N))
add(N, 2, distinct_colours(N, 10**6), rnd_roads(N, N))
add(N, N // 2, distinct_colours(N, 10**6), pad(chain(N, "r"), N, N))
roads = []                                                      # ten districts grow side by side and each
for j in range(1, N // 10):                                     # reaches K colours only near its end
    for t in range(10):
        roads.append(orient(t * (N // 10) + j + 1, t * (N // 10) + ri(max(1, j - 20), j), "r"))
for t in range(1, 10):
    roads.append(orient(ri(1, t * (N // 10)), t * (N // 10) + ri(1, N // 10), "r"))
add(N, 9_000, distinct_colours(N, 10**6), pad(roads, N, N))
add(N, 300, [ri(1, 2000) if random.random() < 0.5 else ri(1, 10**6) for _ in range(N)], pad(star(N, "r"), N, N))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
