import random, os
random.seed(2610)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([3, 1, 4, 1, 5], [(1, 2, 2), (1, 3, 1), (3, 4, 3), (3, 5, 2)]))
cases.append(([1, 1, 1, 1], [(1, 2, 1), (2, 3, 1), (3, 4, 1)]))
cases.append(([9], []))
cases.append(([0, 5, 0], [(1, 2, 7), (1, 3, 1)]))
cases.append(([2, 2], [(1, 2, 1000)]))
def tree(n, cmax, wmax, shape="random"):
    E = []
    for v in range(2, n + 1):
        if shape == "path": u = v - 1
        elif shape == "star": u = 1
        elif shape == "caterpillar": u = v - 1 if v % 2 == 0 else max(1, v - 2)
        elif shape == "deep": u = random.randint(max(1, v - 3), v - 1)
        else: u = random.randint(1, v - 1)
        E.append((u, v, random.randint(1, wmax)))
    perm = list(range(1, n + 1)); random.shuffle(perm)       # relabel so node 1 is not special
    E = [(perm[u - 1], perm[v - 1], w) for u, v, w in E]; random.shuffle(E)
    return ([random.randint(0, cmax) for _ in range(n)], E)
for _ in range(6):
    cases.append(tree(random.randint(2, 9), 5, 5))
# ---- stronger tests (2026-10-20): every big test at N = 100000 (O(N^2) is too slow), and exact ties ----
# Tie gadget: two parts A and B with exactly the same total population, joined by a chain of empty villages.
# The best villages are then exactly a, the chain, and b; the smallest number is put in the middle of the
# chain and village 1 outside, so "first best village met from village 1" and "last best village" both fail.
# (a separate random stream; tests 1-12 keep their bytes)
cases.append(tree(3000, 1000, 1000))                   # test 12 as before
def emit(case):
    """check one test and write it at once"""
    c, E = case
    n = len(c)
    if E and isinstance(E[0], tuple):                  # roads as (u, v, w) (tests 1-12 and one path)
        assert all(1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= 1000 for u, v, w in E)
        E = ["%d %d %d" % e for e in E]
    i = emit.count = getattr(emit, "count", 0) + 1
    assert i <= 40 and 1 <= n <= 100000 and len(E) == n - 1 and 0 <= min(c) and max(c) <= 1000
    open(f"tests/{i:02d}.in", "w").write(f"{n}\n" + " ".join(map(str, c)) + "\n" + "\n".join(E) + ("\n" if E else ""))
for case in cases:                                     # tests 1-12
    emit(case)
rng = random.Random(261050)
N = 100000
rr = rng.random
def ri(lo, hi): return lo + int(rr() * (hi - lo + 1))
def parents(n, shape, base=0):
    """parent (in base + 1 .. base + n) of every vertex base + 2 .. base + n"""
    P = []
    for v in range(2, n + 1):
        if shape == "path": u = v - 1
        elif shape == "star": u = 1
        elif shape == "caterpillar": u = v - 1 if v % 2 == 0 else max(1, v - 2)
        elif shape == "deep": u = v - 1 - int(rr() * min(3, v - 1))
        elif shape == "binary": u = v // 2
        else: u = 1 + int(rr() * (v - 1))
        P.append((base + u, base + v))
    return P
def finish(n, c, P, wmax, wmin=1, perm=None):
    """random numbers (perm[v - 1] = number of vertex v), road lengths and road order; roads as text lines"""
    if perm is None:
        perm = list(range(1, n + 1)); rng.shuffle(perm)
    k = wmax - wmin + 1
    U = [perm[u - 1] for u, _ in P]
    V = [perm[v - 1] for _, v in P]
    Wt = [wmin + int(rr() * k) for _ in P]
    assert len(P) == n - 1 and 1 <= min(Wt) and max(Wt) <= 1000 and all(map(int.__ne__, U, V))
    assert 1 <= min(U) and max(U) <= n and 1 <= min(V) and max(V) <= n
    L = list(map("%d %d %d".__mod__, zip(U, V, Wt)))
    rng.shuffle(L)
    q = [0] * n
    for i in range(n): q[perm[i] - 1] = c[i]
    return (q, L)
def tree2(n, cmax, wmax, shape="random"):
    return finish(n, [int(rr() * (cmax + 1)) for _ in range(n)], parents(n, shape), wmax)
def tie(nA, nB, t, shapes, clo, chi, wmax, wmin=1):
    """vertices 1..nA = A, nA+1..nA+nB = B, then the chain of t empty villages"""
    n = nA + nB + t
    P = parents(nA, shapes[0]) + parents(nB, shapes[1], nA)
    a, b = ri(1, nA), ri(nA + 1, nA + nB)
    chain = list(range(nA + nB + 1, n + 1))
    path = [a] + chain + [b]
    P += [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    c = [clo + int(rr() * (chi - clo + 1)) for _ in range(nA + nB)] + [0] * t
    c[a - 1] = max(c[a - 1], 1); c[b - 1] = max(c[b - 1], 1)
    d = sum(c[:nA]) - sum(c[nA:nA + nB])
    A, Bp = (1, nA), (nA + 1, nA + nB)
    while d != 0:                                      # make both parts weigh the same
        heavy, light = (A, Bp) if d > 0 else (Bp, A)
        if rr() < 0.5:                                 # lower a village of the heavier part
            v = ri(*heavy); x = min(abs(d), c[v - 1] - (1 if v in (a, b) else 0)); c[v - 1] -= x
        else:                                          # or raise one of the lighter part
            v = ri(*light); x = min(abs(d), max(chi, 1) - c[v - 1]); c[v - 1] += max(x, 0); x = max(x, 0)
        d += -x if d > 0 else x
    assert sum(c[:nA]) == sum(c[nA:nA + nB])
    perm = list(range(1, n + 1)); rng.shuffle(perm)    # perm[v - 1] = number of vertex v
    best = set(path)
    if perm.index(1) + 1 in best:                      # village 1 outside the best set
        out = ri(1, nA)
        while out in best: out = ri(1, nA)
        i1, i2 = perm.index(1), out - 1
        perm[i1], perm[i2] = perm[i2], perm[i1]
    lo = min(path, key=lambda v: perm[v - 1])          # smallest number into the middle of the chain
    mid = chain[len(chain) // 2]
    perm[lo - 1], perm[mid - 1] = perm[mid - 1], perm[lo - 1]
    return finish(n, c, P, wmax, wmin, perm)
emit(tree2(N, 1000, 1000))
# max answer, needs 64-bit; N even: the two middle villages tie, the one nearer village 1 gets the larger number
P = parents(N, "path")
perm = list(range(1, N + 1)); rng.shuffle(perm)
mids = (N // 2, N // 2 + 1)
if perm.index(1) + 1 in mids:
    j = ri(1, N // 4) - 1
    i1 = perm.index(1); perm[i1], perm[j] = perm[j], perm[i1]
near, far = mids if perm.index(1) + 1 < N // 2 else mids[::-1]
if perm[near - 1] < perm[far - 1]: perm[near - 1], perm[far - 1] = perm[far - 1], perm[near - 1]
emit(finish(N, [1000] * N, P, 1000, perm=perm))
emit(([0] * N, tree2(N, 0, 1000)[1]))             # nobody lives anywhere: answer 0 at node 1
c = [0] * N; c[N // 3] = 1000; c[2 * N // 3] = 1000         # two heavy villages: a tie along a path
emit((c, [(i, i + 1, 1) for i in range(1, N)]))
emit(tie(50000, 49999, 1, ("random", "random"), 0, 1, 1))   # populations 0/1, all roads 1
for shapes, t, clo, chi, wmax in ((("deep", "caterpillar"), 9, 0, 1000, 1000),
                                  (("path", "path"), 5, 1, 1000, 1000),
                                  (("star", "random"), 2, 0, 1000, 1000),
                                  (("binary", "random"), 20, 0, 1000, 1000),
                                  (("caterpillar", "caterpillar"), 1, 0, 1, 1000),
                                  (("random", "random"), 7, 0, 10, 1),
                                  (("deep", "deep"), 40, 900, 1000, 1000),
                                  (("random", "path"), 2, 0, 1000, 1)):
    nA = ri(30000, 50000) - t // 2
    emit(tie(nA, N - t - nA, t, shapes, clo, chi, wmax))
emit(tie(25000, 25000, 50000, ("random", "random"), 0, 1000, 1000))   # half the villages empty in a chain
emit(tie(49999, 49999, 2, ("path", "path"), 1000, 1000, 1000, 1000))  # all at the maximum
emit(tie(20000, 79990, 10, ("random", "deep"), 0, 1000, 1000))        # small A, many villages in B
emit(tie(49000, 49000, 2000, ("star", "star"), 0, 1000, 1000))
emit(tie(45000, 45000, 10000, ("random", "caterpillar"), 0, 3, 1000))
print(emit.count, "tests")
