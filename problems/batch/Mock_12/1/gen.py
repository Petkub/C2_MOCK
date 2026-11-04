# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(60401)
MAXN = MAXM = 100_000
MAXK = 20
MAXC = 10**9
tests = []


def ri(lo, hi):
    return lo + int(random.random() * (hi - lo + 1))


def add(n, k, col, roads, relabel=True):
    m = len(roads)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM and 1 <= k <= min(n, MAXK) and len(col) == n
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


def grow(n):
    """road j joins the district of houses 1..j with the lone house j + 1 through a random house of 1..j"""
    r = random.random
    return [orient(j + 1, 1 + int(r() * j), "r") for j in range(1, n)]


def beside(c, chain_roads, n, other_roads):
    """houses 1..c: chain_roads; houses c + 1..n: other_roads (numbered 1..n - c); the two lists interleaved at
    random (each keeps its order); one big district absorbs lone houses while the other part does its own thing"""
    other = [(u + c, v + c) for u, v in other_roads]
    out, i, j, r = [], 0, 0, random.random
    while i < len(chain_roads) or j < len(other):
        if j == len(other) or (i < len(chain_roads) and r() * (len(chain_roads) - i + len(other) - j) < len(chain_roads) - i):
            out.append(chain_roads[i])
            i += 1
        else:
            out.append(other[j])
            j += 1
    return out


def pad(roads, n, m):
    """fill up to m roads with roads inside existing districts or repeated roads"""
    roads = roads[:]
    while len(roads) < m:
        u, v = random.choice(roads)
        roads.insert(ri(len(roads) // 2, len(roads)), (v, u) if random.random() < 0.5 else (u, v))
    return roads[:m]


def skewed(n, p):
    """colour 1 for most houses, the other colours 2..p are rare (colour c has weight 1 / c^2)"""
    w = [1.0 / (c * c) for c in range(1, p + 1)]
    return random.choices(range(1, p + 1), weights=w, k=n)


def mixed(n, p, q, base=None):
    """each house: a colour of 1..p with probability q (from base if given), otherwise a colour no other house has"""
    d = distinct_colours(n, MAXC - 100)
    r = random.random
    return [(base[i] if base else ri(1, p)) if r() < q else d[i] + 100 for i in range(n)]


def clustered(n, m, glo, ghi, cross):
    """houses in groups of glo..ghi consecutive numbers, roads mostly inside a group; groups get joined slowly"""
    bounds, x = [], 1
    while x <= n:
        y = min(n, x + ri(glo, ghi) - 1)
        bounds.append((x, y))
        x = y + 1
    roads = []
    while len(roads) < m:
        if random.random() < cross:
            u, v = ri(1, n), ri(1, n)
        else:
            lo, hi = random.choice(bounds)
            if lo == hi:
                continue
            u, v = ri(lo, hi), ri(lo, hi)
        if u != v:
            roads.append((u, v))
    return roads


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
add(1000, 15, rnd_colours(1000, 18), clustered(1000, 1500, 5, 30, 0.02))
add(2000, 10, skewed(2000, 12), star(2000, "r"))
add(1500, 20, rnd_colours(1500, 22), balanced(1500))
add(3000, 20, rnd_colours(3000, 24), clustered(3000, 3000, 10, 40, 0.01))

# hidden: large
N = MAXN
add(N, 20, distinct_colours(N, 10**6), pad(chain(N, "r"), N, N))
add(N, 17, distinct_colours(N, 10**6), pad(chain(N, "r"), N, N))
add(N, 20, distinct_colours(N), pad(grow(N), N, N))
add(N, 19, rnd_colours(N, N), pad(star(N, "r"), N, N))
C = 3 * N // 5                                                  # a big district grows beside the other shapes
add(N, 20, distinct_colours(C, 10**6) + rnd_colours(N - C, 25), pad(beside(C, chain(C, "r"), N, balanced(N - C)), N, N))
add(N, 20, rnd_colours(N, N), rnd_roads(N, N))
roads = []                                                      # ten chains grow together, then join
for j in range(1, N // 10):
    for t in range(10):
        roads.append(orient(t * (N // 10) + j + 1, t * (N // 10) + ri(1, j), "r"))
for t in range(1, 10):
    roads.append(orient(ri(1, t * (N // 10)), t * (N // 10) + ri(1, N // 10), "r"))
add(N, 20, mixed(N, 20, 0.5), pad(roads, N, N))
add(N, 1, rnd_colours(N, MAXC), pad(chain(N, "r"), N, N))
add(N, 20, [i % 20 + 1 for i in range(N)], pad(chain(N, "u"), N, N))   # exactly 20 colours in all
add(N, 20, [i % 19 + 1 for i in range(N)], pad(chain(N, "s"), N, N))   # never colourful
add(N, 20, mixed(N, 25, 0.6), pad(chain(N, "r"), N, N))
half = N // 2                                                   # a chain over half the houses, every other
roads = []                                                      # road inside a district or repeated
for r in chain(half, "r"):
    roads.append(r)
    roads.append(random.choice(roads))
add(N, 20, distinct_colours(N, 10**6), roads[:N])
add(N, 20, distinct_colours(N), pad(two_fronts(N, "r"), N, N))
add(N, 20, mixed(N, 21, 0.4), pad(two_fronts(N, "r"), N, N))
add(N, 2, distinct_colours(N, 10**6), rnd_roads(N, N))
add(N, 10, mixed(N, 10, 0.5, skewed(N, 10)), pad(chain(N, "r"), N, N))
roads = []                                                      # ten districts grow side by side and each
for j in range(1, N // 10):                                     # reaches K colours only near its end
    for t in range(10):
        roads.append(orient(t * (N // 10) + j + 1, t * (N // 10) + ri(max(1, j - 20), j), "r"))
for t in range(1, 10):
    roads.append(orient(ri(1, t * (N // 10)), t * (N // 10) + ri(1, N // 10), "r"))
add(N, 18, mixed(N, 18, 0.7, skewed(N, 18)), pad(roads, N, N))
add(N, 20, [ri(1, 20) if random.random() < 0.5 else ri(1, 10**6) for _ in range(N)], pad(star(N, "r"), N, N))
add(N, 20, distinct_colours(C, 10**6) + rnd_colours(N - C, 22),
    beside(C, grow(C), N, clustered(N - C, N - C + 1, 5, 40, 0.005)))
add(N, 12, distinct_colours(C) + rnd_colours(N - C, 14), beside(C, chain(C, "r"), N, clustered(N - C, N - C + 1, 3, 25, 0.02)))
add(N, 20, rnd_colours(C, 10**6) + mixed(N - C, 30, 0.9, skewed(N - C, 30)),
    beside(C, chain(C, "r"), N, clustered(N - C, N - C + 1, 20, 200, 0.001)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
