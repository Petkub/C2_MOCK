import random, os
random.seed(2608)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append([(5, 4), (6, 7), (6, 4), (2, 3)])
cases.append([(3, 3), (3, 4), (3, 5)])
cases.append([(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
cases.append([(7, 7)])
cases.append([(1, 1), (2, 2), (2, 3), (3, 2), (3, 3), (4, 4)])
cases.append([(1, 10), (2, 2), (3, 3), (4, 4), (5, 11)])
for _ in range(6):
    n = random.randint(1, 12); cases.append([(random.randint(1, 6), random.randint(1, 6)) for _ in range(n)])
N, B = 50000, 10**9
def rnd(n, wr, hr): return [(random.randint(1, wr), random.randint(1, hr)) for _ in range(n)]
cases.append(rnd(5000, 100, 100))
cases.append(rnd(N, B, B))
cases.append(rnd(N, 1000, 1000))                       # many equal widths/heights
cases.append(rnd(N, 10, B))                            # few widths: tie handling matters
cases.append([(i, i) for i in range(1, N + 1)])        # answer N
cases.append([(i, N + 1 - i) for i in range(1, N + 1)])  # answer 1
cases.append([(i // 2 + 1, i // 2 + 1) for i in range(N)])  # pairs of equal dolls
cases.append([(random.randint(1, B), 7) for _ in range(N)])   # all same height: 1
cases.append([(x, x + random.randint(-50, 50)) for x in sorted(random.sample(range(100, B), N))])
cases.append([(i // 1000 + 1, random.randint(1, 1000)) for i in range(N)])
for wr, hr in ((10**9, 10**9), (300, 300), (50, 10**9), (10**9, 50)):
    cases.append(rnd(random.randint(30000, 50000), wr, hr))
cases.append(rnd(100000, B, B))
cases.append(rnd(100000, 3000, 3000))
# ---- stronger tests (2026-10-20): every big test at N = 100000, so O(N^2) is too slow, and ties that break
# a wrong sort order (equal widths chained) or a non-strict LIS (equal heights chained) ----
# (a separate random stream replaces tests 14+; tests 1-13 keep their bytes)
del cases[13:]                                         # the old big tests are replaced below
for i, p in enumerate(cases, 1):
    assert 1 <= len(p) <= 100000 and all(1 <= w <= B and 1 <= h <= B for w, h in p)
    random.shuffle(p) if i > 5 else None
    open(f"tests/{i:02d}.in", "w").write(f"{len(p)}\n" + "".join(f"{w} {h}\n" for w, h in p))
rng = random.Random(260830)
N = 100000
def ri(lo, hi): return lo + int(rng.random() * (hi - lo + 1))     # faster than randint (gen.py must be quick)
def rnd2(n, wr, hr): return [(ri(1, wr), ri(1, hr)) for _ in range(n)]
def emit(p):
    """check one big test, shuffle it and write it at once"""
    i = emit.count = getattr(emit, "count", 13) + 1
    assert i <= 40 and 1 <= len(p) <= 100000
    W = [w for w, _ in p]; H = [h for _, h in p]
    assert 1 <= min(W) and max(W) <= B and 1 <= min(H) and max(H) <= B
    L = list(map("%d %d".__mod__, p))
    rng.shuffle(L)
    open(f"tests/{i:02d}.in", "w").write(f"{len(p)}\n" + "\n".join(L) + "\n")
emit(rnd2(N, B, B))
emit(rnd2(N, 1000, 1000))                       # many equal widths/heights
emit(rnd2(N, 10, B))                            # few widths: tie handling matters
emit([(i, i) for i in range(1, N + 1)])         # answer N
emit([(i, N + 1 - i) for i in range(1, N + 1)])  # answer 1
emit([(i // 2 + 1, i // 2 + 1) for i in range(N)])  # pairs of equal dolls
emit([(ri(1, B), 7) for _ in range(N)])   # all same height: 1
emit([(x, x + ri(-50, 50)) for x in (ri(100, 60000) for _ in range(N))])   # near the diagonal, widths repeat
emit([(i // 1000 + 1, ri(1, 1000)) for i in range(N)])
for wr, hr in ((10**9, 10**9), (300, 300), (50, 10**9), (10**9, 50), (3000, 3000)):
    emit(rnd2(N, wr, hr))
# groups of equal width whose heights also rise from group to group: one doll per group
G, S = 500, 200
emit([(g * 7 + 3, g * S + j + 1) for g in range(G) for j in range(S)])
# runs of equal height along increasing widths: one doll per run
emit([(i + 1, i // 50 + 1) for i in range(N)])
# 1000 columns of equal width, column w holds 100 heights spread over [50 w, 50 w + 5000]
emit([(w, 50 * w + ri(0, 5000)) for w in range(1, 1001) for _ in range(100)])
# copies of the same doll along a diagonal
emit([(x // 5 + 1, x // 5 + 1) for x in range(N)])
emit([(B, B)] * N)                               # all identical: 1
emit([(ri(B - 300, B), ri(B - 100000, B)) for _ in range(N)])
# a long staircase hidden in noise: answer about 20000, with ties on both coordinates
st = [(3 * i + ri(0, 3), 3 * i + ri(0, 3)) for i in range(1, 25001)]
emit(st + rnd2(N - len(st), 75000, 75000))
# chains of equal width blocks: width w has heights w .. w + 30 (equal widths would chain 31 at a time)
emit([(w, w + j) for w in range(1, N // 31 + 1) for j in range(31)][:N])
# heights repeat across a band of widths
emit([(ri(1, B), ri(1, 2000) * 1000) for _ in range(N)])
emit([(ri(1, 2000), ri(1, 2000)) for _ in range(N)])
emit([(ri(1, 100000), ri(1, 100)) for _ in range(N)])
emit([(ri(1, 100), ri(1, 100000)) for _ in range(N)])
emit([(i // 2 + 1, i + 1) for i in range(N)])   # each width twice, heights rising: answer N / 2
print(emit.count, "tests")
