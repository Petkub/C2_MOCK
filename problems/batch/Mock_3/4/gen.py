import random, os
from operator import ne, itemgetter
g0, g1 = itemgetter(0), itemgetter(1)
random.seed(2614)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([3, 2, 4, 1, 2], [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]))
cases.append(([5, 5, 5], []))
cases.append(([1, 1, 1], [(1, 2), (2, 3), (3, 1)]))
cases.append(([2, 3, 3], [(1, 3), (2, 3)]))
cases.append(([4, 1, 1, 1, 6], [(1, 5), (2, 3), (3, 4), (4, 5), (2, 4)]))
def dag(n, m, tmax, cyc=False, layered=None):
    perm = list(range(1, n + 1)); random.shuffle(perm); E = []
    while len(E) < m - cyc:
        if layered:
            i = random.randrange(n - layered); j = random.randint(i + 1, min(n - 1, i + layered))
        else:
            i, j = sorted(random.sample(range(n), 2))
        E.append((perm[i], perm[j]))
    if cyc:
        a, b = random.choice(E) if E else (perm[0], perm[1]); E.append((b, a))   # reverse an existing edge: cycle
    random.shuffle(E)
    return ([random.randint(1, tmax) for _ in range(n)], E)
for _ in range(6):
    n = random.randint(1, 8)
    cases.append(dag(n, random.randint(0, 10) if n > 1 else 0, 5, cyc=(n > 2 and random.random() < 0.3)))
N, M, B = 50000, 50000, 10**9
cases.append(dag(3000, 6000, 1000))
cases.append(dag(N, M, B))
cases.append(dag(N, M, 10, layered=5))                    # deep: long chains, many ties
cases.append(dag(N, M, 1, layered=3))                     # all equal durations: many critical courses
cases.append(dag(N, M, B, cyc=True, layered=50))          # one cycle hidden in a large graph
cases.append(([B] * N, [(i, i + 1) for i in range(1, N)]))  # one long chain: 2*10^14
cases.append(([random.randint(1, B) for _ in range(N)], []))
cases.append(([1] * N, [(1, i) for i in range(2, N + 1)]))   # star: every course critical
E = [(i, i + 1) for i in range(1, N)] + [(N, 1)]            # big cycle
cases.append(([1] * N, E))
# two parallel chains of equal length -> both critical; plus a short branch
h = N // 2
E = [(i, i + 1) for i in range(1, h)] + [(i, i + 1) for i in range(h + 1, N)]
cases.append(([2] * N, E))
cases.append(dag(N, M, 1000, layered=1000))
for n, m, tmax, lay in ((30000, 60000, 10**9, None), (40000, 40000, 5, 4), (50000, 80000, 100, 20), (30000, 90000, 1, 2)):
    cases.append(dag(n, m, tmax, layered=lay))
cases.append(dag(100000, 100000, B))
cases.append(([10**9] * 100000, [(i, i + 1) for i in range(1, 100000)]))
cases.append(([10**9] * 5000, [(i, i + 1) for i in range(1, 5000)] + [(1, 5000)]))
cases.append(dag(20000, 40000, 10**9, layered=3))
# ---- legacy strengthening (2026-10): the big tests were mostly N = 5 * 10^4 and shallow, so repeated relaxation
# over the edge list (Bellman-Ford style) and "count the courses on one longest path" scored 83%. The new big tests
# use M = 10^5 with deep DAGs in shuffled edge order (thousands of relaxation rounds) and many tied longest paths.
# The stars, cycles, the sorted chain and the all-equal shallow DAG keep their N = 5 * 10^4 tests (size does not
# matter there).
# The cases above are still generated so the unchanged tests keep their bytes; `override` replaces some of them,
# `extra` adds tests at the end. All new data comes from R, not from `random`.
R = random.Random(26142)
rr = R.random
def ri(a, b): return a + int(rr() * (b - a + 1))
def shuffle(L):
    """Fisher-Yates driven by rr() (faster than R.shuffle)"""
    for i in range(len(L) - 1, 0, -1):
        j = int(rr() * (i + 1)); L[i], L[j] = L[j], L[i]
def dag2(n, m, tmax, cyc=False, layered=None, shuffled=True):
    """like dag() above (random 1-D DAGs are shallow: every few hundred courses no edge crosses a gap)"""
    perm = list(range(1, n + 1))
    if shuffled: shuffle(perm)
    k = m - cyc
    if layered:
        E = [(perm[i], perm[i + 1 + int(rr() * min(layered, n - 1 - i))]) for i in [int(rr() * (n - layered)) for _ in range(k)]]
    else:
        E = []
        while len(E) < k:
            E += [(perm[min(i, j)], perm[max(i, j)]) for i, j in [(int(rr() * n), int(rr() * n)) for _ in range(k - len(E))] if i != j]
    if cyc:
        a, b = E[int(rr() * len(E))]; E.append((b, a))
    if shuffled: shuffle(E)
    return ([ri(1, tmax) for _ in range(n)], E)
def relabel(t, E):
    """random course numbers and edge order for a graph built on 1..n"""
    n = len(t); perm = list(range(1, n + 1)); shuffle(perm)
    t2 = [0] * n
    for i in range(n): t2[perm[i] - 1] = t[i]
    E2 = [(perm[a - 1], perm[b - 1]) for a, b in E]; shuffle(E2)
    return (t2, E2)
def diamonds(k, w):
    """(build on 1..n, then relabel) k diamonds in a row (a -> b, a -> c, b -> d, c -> d), all durations w: both sides of each diamond are critical"""
    t = [w] * (3 * k + 1); E = []
    for d in range(k):
        a = 3 * d + 1
        E += [(a, a + 1), (a, a + 2), (a + 1, a + 3), (a + 2, a + 3)]
    return (t, E)
def grid(layers, width, m, tmax):
    """(build on 1..n, then relabel) deep DAG: layers of `width` courses, edges only between consecutive layers, every course has an edge in and
    out (so with equal durations every course is critical, and longest paths end at many different courses)"""
    n = layers * width; E = []
    for L in range(layers - 1):
        for x in range(width):
            E.append((L * width + x + 1, (L + 1) * width + ri(0, width - 1) + 1))
            E.append((L * width + ri(0, width - 1) + 1, (L + 1) * width + x + 1))
    while len(E) < m:
        L = ri(0, layers - 2); E.append((L * width + ri(1, width), (L + 1) * width + ri(1, width)))
    assert len(E) == m
    return ([ri(1, tmax) for _ in range(n)], E)
def twin(g):
    """two disjoint copies of the same graph: the longest paths (and the courses finishing at T) come in pairs"""
    t, E = g; n = len(t)
    return relabel(t + t, E + [(a + n, b + n) for a, b in E])
M = 100000
h = M // 2
override = {
    13: twin(dag2(h, h, B, shuffled=False)),
    14: twin(grid(6250, 4, h, 10)),                            # deep instead of the shallow random layered DAGs
    18: ([ri(1, 1000) for _ in range(M)], []),               # no conditions: every longest course is critical
    21: relabel([2] * M, [(i, i + 1) for i in range(1, h)] + [(i, i + 1) for i in range(h + 1, M)]),
    22: relabel(*grid(5000, 10, M, 1000)),
    23: twin(dag2(h, h, B, shuffled=False)),
    24: twin(grid(12500, 2, h, 5)),
    25: twin(grid(3125, 8, h, 100)),
    26: relabel(*grid(25000, 2, M, 1)),
    30: twin(grid(5000, 5, h, B)),
}
extra = [
    relabel(*diamonds(25000, 1)),
    twin(diamonds(12500, 10**9)),                              # 2.5 * 10^13, twice
    twin(grid(5000, 5, h, 2)),
    # long chain with a back edge from its end to its middle: a cycle hidden deep
    relabel([ri(1, B) for _ in range(M)], [(i, i + 1) for i in range(1, M)] + [(M, M // 2)]),
    # many chains of the same total length: every chain is critical, they end at different courses
    relabel([1] * M, [(i, i + 1) for i in range(1, M) if i % 5000]),
    # duplicated conditions along two deep chains of nearly equal length
    relabel([3] * h, ([(i, i + 1) for i in range(1, h // 2)] + [(i, i + 1) for i in range(h // 2 + 1, h)]) * 2),
]
for i, (t, E) in enumerate(cases + extra, 1):
    if i in override:
        t, E = override[i]
    n = len(t)
    assert 1 <= n <= 100000 and len(E) <= 100000 and 1 <= min(t) and max(t) <= B
    if E:
        As, Bs = list(map(g0, E)), list(map(g1, E))
        assert 1 <= min(As) and max(As) <= n and 1 <= min(Bs) and max(Bs) <= n and all(map(ne, As, Bs))
    open(f"tests/{i:02d}.in", "w").write(f"{n} {len(E)}\n" + " ".join(map(str, t)) + "\n" + "".join(f"{a} {b}\n" for a, b in E))
assert len(cases) + len(extra) <= 40
print(len(cases) + len(extra), "tests")
