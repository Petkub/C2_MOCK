import random, os
random.seed(2609)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([5, 1, 4, 2, 3], [(1, 2), (2, 3), (3, 4), (4, 5)], [2, 4, 1, 3]))
cases.append(([10, 20, 30], [(1, 2), (2, 3), (1, 3)], [1, 2, 3]))
cases.append(([3, 3], [(1, 2), (1, 2)], [2, 1]))
cases.append(([7, 1, 1, 1], [(2, 3), (3, 4)], [1, 2]))
cases.append(([0, 0, 5, 0], [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)], [5, 3, 1, 4, 2]))
def rnd(n, m, pmax, conn=False):
    E = []
    if conn:
        for v in range(2, n + 1): E.append((random.randint(1, v - 1), v))
    while len(E) < m:
        u, v = random.sample(range(1, n + 1), 2); E.append((u, v))
    random.shuffle(E)
    o = list(range(1, m + 1)); random.shuffle(o)
    return ([random.randint(0, pmax) for _ in range(n)], E, o)
for _ in range(6):
    n = random.randint(2, 9); cases.append(rnd(n, random.randint(1, 12), 10))
N, M, B = 50000, 50000, 10**9
cases.append(rnd(3000, 6000, 1000))
# ---- stronger tests (2026-10-20): every big test at the full size (N, M up to 100000) ----
# Besides random graphs, bridges on cycles through big hubs: closing one does not split a group, but a search
# from its two ends must scan a whole hub before the ends meet again (one search per day is too slow).
# A separate random stream; test 21 (tiny) is kept as it was.
def emit(case):
    """check one test and write it at once"""
    p, E, o = case
    i = emit.count = getattr(emit, "count", 0) + 1
    n, m = len(p), len(E)
    assert i <= 40 and 1 <= n <= 100000 and 1 <= m <= 100000 and sorted(o) == list(range(1, m + 1))
    assert all(1 <= u <= n and 1 <= v <= n and u != v for u, v in E) and 0 <= min(p) and max(p) <= B
    open(f"tests/{i:02d}.in", "w").write(f"{n} {m}\n" + " ".join(map(str, p)) + "\n" + "".join(map("%d %d\n".__mod__, E)) + " ".join(map(str, o)) + "\n")
for case in cases:                                     # tests 1-12
    emit(case)
rng = random.Random(260940)
N = M = 100000
def ri(lo, hi): return lo + int(rng.random() * (hi - lo + 1))
def pops(n, pmax):
    rr = rng.random
    return [int(rr() * (pmax + 1)) for _ in range(n)]
def rnd2(n, m, pmax, conn=False, hub=0.0):
    """random graph (conn: a random tree first); with probability hub a bridge goes to the hub island h"""
    h, rr = ri(1, 50), rng.random
    E = []
    if conn:
        for v in range(2, n + 1):
            E.append((h if v > h and rr() < hub else ri(1, v - 1), v))
    while len(E) < m:
        u, v = ri(1, n), ri(1, n)
        if rr() < hub: u = h
        if u != v: E.append((u, v))
    o = list(range(1, m + 1)); rng.shuffle(o)
    return (pops(n, pmax), E, o)
def relabel(n, p, E, first, shuffled=False):
    """random island names, bridge numbers and directions; the bridges E[i], i in first, close first (in order)"""
    perm = list(range(1, n + 1)); rng.shuffle(perm)
    m, rr = len(E), rng.random
    num = list(range(m)); rng.shuffle(num)             # E[i] becomes bridge num[i] + 1
    E2 = [None] * m
    for i, (u, v) in enumerate(E):
        E2[num[i]] = (perm[u - 1], perm[v - 1]) if rr() < 0.5 else (perm[v - 1], perm[u - 1])
    isfirst = bytearray(m)
    for i in first: isfirst[num[i]] = 1
    o = [num[i] + 1 for i in first] + [j + 1 for j in range(m) if not isfirst[j]]   # the others by number
    if shuffled: rng.shuffle(o)
    q = [0] * n
    for i in range(n): q[perm[i] - 1] = p[i]
    return (q, E2, o)
def hubs(h, k, pmax, shuffled=False):
    """h hub islands, each joined to every one of k other islands; the bridges of hub 1 close first"""
    E = [(a, h + 1 + i) for a in range(1, h + 1) for i in range(k)]
    first = list(range(k)); rng.shuffle(first)
    return relabel(h + k, pops(h + k, pmax), E, first, shuffled)
def theta(k, L, pmax, shuffled=False):
    """k paths of L bridges each between islands 1 and 2; the middle bridge of every path closes first"""
    E, n = [], 2
    for _ in range(k):
        prev = 1
        for j in range(L - 1):
            n += 1; E.append((prev, n)); prev = n
        E.append((prev, 2))
    first = [i * L + L // 2 for i in range(k)]; rng.shuffle(first)
    return relabel(n, pops(n, pmax), E, first, shuffled)
emit(rnd2(N, M, B, True, 0.5))
emit(rnd2(N, N - 1, B, True, 0.5))             # a tree: every closure splits a group
emit(rnd2(N, M, 1, True, 0.4))
emit(rnd2(N, 70000, 10**6, False, 0.5))        # sparse: many small groups
# path 1-2-...-N closed from the middle outwards
E = [(i, i + 1) for i in range(1, N)]
emit(([B] * N, E, sorted(range(1, N), key=lambda i: abs(i - N // 2))))
# star: centre has huge population
E = [(1, i) for i in range(2, N + 1)]; o = list(range(1, N)); rng.shuffle(o)
emit(([B] + [ri(0, 10) for _ in range(N - 1)], E, o))
# two blobs, each around a hub island, joined by one bridge closed first
half = N // 2
E = [(1, ri(2, half)) if rng.random() < 0.5 else (ri(1, half), ri(1, half)) for _ in range(M // 2 - 1)]
E += [(N, ri(half + 1, N - 1)) if rng.random() < 0.5 else (ri(half + 1, N), ri(half + 1, N)) for _ in range(M // 2 - 1)]
E = [(u, v) for u, v in E if u != v]
E.append((1, N))
emit((pops(N, B), E, [len(E)] + rng.sample(range(1, len(E)), len(E) - 1)))
emit(rnd2(N, M, 0))                            # all zero populations
emit(([211854912, 34535427], [(2, 1)], [1]))   # test 21 as before
emit(hubs(2, 49999, B))
emit(hubs(3, 33333, 10**6))
emit(hubs(4, 25000, B))
emit(theta(10000, 10, B))
emit(theta(33333, 3, B))
emit(hubs(2, 49999, B, True))                  # the same shapes closed in random order
emit(theta(10000, 10, 10**6, True))
emit(rnd2(40000, M, B, True, 0.5))
print(emit.count, "tests")
