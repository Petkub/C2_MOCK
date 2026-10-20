# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(60502)
MAXN, MAXM, MAXW, MAXK = 10_000, 50_000, 10**6, 11
tests = []


def ri(lo, hi):
    return lo + int(random.random() * (hi - lo + 1))


def add(n, roads, s, cap, orders, relabel=True):
    m, k = len(roads), len(orders)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM and 1 <= k <= MAXK and 1 <= cap <= k and 1 <= s <= n
    assert all(1 <= a <= n and 1 <= b <= n and a != b and 1 <= w <= MAXW for a, b, w in roads)
    assert all(1 <= p <= n and 1 <= q <= n for p, q in orders)
    if relabel:                                  # random vertex numbers and road order
        r = random.random
        lab = [0] + sorted(range(1, n + 1), key=lambda _: r())
        roads = sorted(((lab[a], lab[b], w) if r() < 0.5 else (lab[b], lab[a], w) for a, b, w in roads),
                       key=lambda _: r())
        s = lab[s]
        orders = [(lab[p], lab[q]) for p, q in orders]
    tests.append(f"{n} {m}\n" + "".join(f"{a} {b} {w}\n" for a, b, w in roads)
                 + f"{s} {k} {cap}\n" + "".join(f"{p} {q}\n" for p, q in orders))


def w_rand(lo=1, hi=MAXW):
    return ri(lo, hi)


def connected(n, m, lo=1, hi=MAXW, extra_from=None):
    """random tree (attach to a recent vertex: long thin shape) plus random extra roads"""
    roads = [(v, ri(max(1, v - 30), v - 1), w_rand(lo, hi)) for v in range(2, n + 1)]
    while len(roads) < m:
        a, b = ri(1, n), ri(1, n)
        if a != b:
            roads.append((a, b, w_rand(lo, hi)))
    return roads


def grid(r, c, lo, hi, m):
    idx = lambda i, j: i * c + j + 1
    roads = []
    for i in range(r):
        for j in range(c):
            if j + 1 < c:
                roads.append((idx(i, j), idx(i, j + 1), w_rand(lo, hi)))
            if i + 1 < r:
                roads.append((idx(i, j), idx(i + 1, j), w_rand(lo, hi)))
    while len(roads) < m:                        # a few diagonals
        i, j = ri(0, r - 2), ri(0, c - 2)
        roads.append((idx(i, j), idx(i + 1, j + 1), w_rand(lo, hi)))
    return roads


def two_towns(n, m, bridge_len, bridge_w):
    """two random towns of equal size joined by a long road of bridge_len hops; returns roads, town A, town B"""
    t = (n - bridge_len + 1) // 2
    A = list(range(1, t + 1))
    B = list(range(t + 1, 2 * t + 1))
    roads = []
    for town in (A, B):
        for i in range(1, len(town)):
            roads.append((town[i], town[ri(max(0, i - 20), i - 1)], w_rand(1, 1000)))
    chain = [A[-1]] + list(range(2 * t + 1, n + 1)) + [B[0]]
    for i in range(len(chain) - 1):
        roads.append((chain[i], chain[i + 1], bridge_w))
    while len(roads) < m:
        town = A if random.random() < 0.5 else B
        a, b = random.choice(town), random.choice(town)
        if a != b:
            roads.append((a, b, w_rand(1, 1000)))
    return roads, A, B


def cycle(n, m, lo, hi):
    roads = [(i, i % n + 1, w_rand(lo, hi)) for i in range(1, n + 1)]
    while len(roads) < m:                        # parallel or longer copies: never shortcuts
        i = ri(1, n)
        roads.append((i, i % n + 1, MAXW))
    return roads


def pts(n, k, pool=None):
    pool = pool or list(range(1, n + 1))
    return [(random.choice(pool), random.choice(pool)) for _ in range(k)]


# samples
add(5, [(1, 2, 2), (2, 3, 1), (3, 4, 5), (4, 5, 1)], 1, 1, [(2, 4), (3, 5)],
    relabel=False)
add(4, [(1, 2, 3), (2, 3, 2), (3, 4, 2)], 1, 3, [(2, 4), (2, 2), (4, 1)], relabel=False)
add(4, [(1, 2, 4), (3, 4, 1)], 2, 1, [(1, 4)], relabel=False)
add(3, [(1, 2, 1), (2, 3, 1)], 1, 1, [(1, 3), (2, 2)], relabel=False)
add(3, [(1, 2, 5), (2, 3, 7)], 2, 2, [(1, 3), (3, 1), (2, 2)], relabel=False)

# hidden: small (checked by trying every order, or by Dijkstra over (vertex, parcels))
add(2, [(1, 2, 1000000)], 2, 1, [(2, 2)])
add(2, [(1, 2, 7), (2, 1, 3)], 1, 1, [(2, 1), (1, 2), (2, 1)])
r_, A, B = two_towns(40, 90, 5, 1000)
add(40, r_, A[0], 1, [(random.choice(A), random.choice(B)) for _ in range(5)])
add(100, connected(100, 300, 1, MAXW), 50, 3, pts(100, 5))
add(12, connected(12, 20, 1, 9), 1, 2, pts(12, 8, [1, 2, 3, 4]))
r_, A, B = two_towns(30, 60, 3, 500)
add(30, r_, B[0], 2, [(random.choice(A), random.choice(B)) for _ in range(7)])
add(20, cycle(20, 30, 1, 50), 1, 3, pts(20, 9))
add(500, connected(500, 2000, 1, MAXW), 7, 1, pts(500, 6))
r_ = connected(60, 100, 1, 100)
r_ = [(a, b, w) for a, b, w in r_ if a != 60 and b != 60] + [(1, 2, 5)]
add(60, r_, 1, 2, pts(59, 6) + [(60, 3)])        # one pickup cannot be reached

# hidden: large
N, M = MAXN, MAXM
add(N, connected(N, M), 1, 3, pts(N, 11))
add(N, connected(N, M), 1, 1, pts(N, 11))
add(N, connected(N, M, 1, 1000), ri(1, N), 2, pts(N, 11))
add(N, grid(100, 100, 1, MAXW, M), 5050, 4, pts(N, 11))
add(N, grid(100, 100, 1, 1000, 25_000), 1, 2, [(ri(1, 50), ri(9950, N)) for _ in range(11)])
for cap, bridge in ((1, 3000), (2, 6000), (3, 100), (5, 8000), (11, 2000)):
    r_, A, B = two_towns(N, M, bridge, MAXW)
    add(N, r_, random.choice(A), cap, [(random.choice(A), random.choice(B)) for _ in range(11)])
r_, A, B = two_towns(N, M, 9000, MAXW)                 # back and forth: some parcels go the other way
add(N, r_, random.choice(B), 2, [(random.choice(A), random.choice(B)) if i % 3 else
                                 (random.choice(B), random.choice(A)) for i in range(11)])
add(N, cycle(N, M, 1, MAXW), 1, 1, [(i * 900 + 1, (i * 900 + 4500) % N + 1) for i in range(11)])
add(N, cycle(N, M, MAXW - 10, MAXW), 1, 2, [((i * 2311) % N + 1, (i * 2311 + N // 2) % N + 1) for i in range(11)])
star = []                                          # long arms from the centre 1
arm = (N - 1) // 11
for a in range(11):
    prev = 1
    for t in range(arm):
        v = 2 + a * arm + t
        star.append((prev, v, w_rand(MAXW // 2, MAXW)))
        prev = v
ends = [1 + (a + 1) * arm for a in range(11)]
while len(star) < M:
    v = ri(2, 1 + 11 * arm)
    star.append((v, v - 1 if v > 2 else 1, MAXW))   # extra copies of arm roads
add(1 + 11 * arm, star, 1, 3, [(ends[i], ends[(i + 4) % 11]) for i in range(11)])
add(N, connected(N, M), 9, 10, pts(N, 11, list(range(1, 40))))   # shared and equal points
same = [ri(1, N) for _ in range(4)]
add(N, connected(N, M, 1, 5000), same[0], 2, [(same[i % 4], same[(i * 3 + 1) % 4]) for i in range(10)]
    + [(same[2], same[2])])                       # four places only, one parcel stays put
add(N, connected(N, M), 1, 6, pts(N, 11))
add(N, connected(N, M, 1, 300), 1, 1, pts(N, 11))
add(N, connected(N, M, 1000, 2000), 1, 2, pts(N, 11))
r_ = connected(N - 5, M - 6)                     # one drop on an island of five houses
r_ += [(a + N - 5, b + N - 5, w) for a, b, w in connected(5, 6)]
add(N, r_, 1, 3, pts(N - 5, 10) + [(ri(1, N - 5), N - 2)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
