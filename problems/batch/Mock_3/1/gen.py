import random, os
from operator import lt, itemgetter
g0, g1 = itemgetter(0), itemgetter(1)
random.seed(2611)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append([(1, 5), (3, 8), (4, 6)])
cases.append([(0, 10), (0, 10)])
cases.append([(1, 2), (2, 3), (5, 9)])
cases.append([(0, 1000000000)])
cases.append([(2, 7), (1, 9), (3, 4), (3, 4)])
for _ in range(6):
    n = random.randint(1, 8); I = []
    for _ in range(n):
        l = random.randint(0, 30); I.append((l, l + random.randint(1, 15)))
    cases.append(I)
N, B = 50000, 10**9
def rnd(n, span, lmax):
    I = []
    for _ in range(n):
        l = random.randint(0, span - 1); I.append((l, min(span, l + random.randint(1, lmax))))
    return I
cases.append(rnd(3000, 5000, 100))
cases.append(rnd(N, B, B))
cases.append(rnd(N, B, 10**4))
cases.append(rnd(N, 1000, 1000))                       # heavy overlap on small coordinates
cases.append([(0, B)] * N)                             # everything at depth N
cases.append([(i, B - i) for i in range(N)])           # nested
cases.append([(i * 5000, i * 5000 + 5000) for i in range(N)])   # touching, never overlapping
cases.append([tuple(x * 10**8 for x in sorted(random.sample(range(11), 2))) for _ in range(N)])   # many equal endpoints
cases.append(rnd(N, 10**6, 10))
cases.append([(i, i + 1) for i in range(N // 2)] + [(i, i + 2) for i in range(N // 2)])
for span, lmax in ((10**9, 10**9), (10**5, 50), (10**9, 10**6), (5000, 5000)):
    cases.append(rnd(random.randint(30000, 50000), span, lmax))
cases.append(rnd(100000, B, B))
cases.append(rnd(100000, 10**6, 100))
for idx in range(11, len(cases)):
    mx = max(r for _, r in cases[idx])
    if mx <= 10**6 and idx % 2 == 0:
        f = 10**9 // mx
        cases[idx] = [(l * f, r * f) for l, r in cases[idx]]
# ---- legacy strengthening (2026-10): the big tests were mostly N = 5 * 10^4, where O(N^2) programs still run in
# about a second. The same families are rebuilt at N = 10^5, and new tests where most people are present most of
# the time (filling every compressed piece of every interval costs ~10^10 steps there).
# Families with few distinct times (where N hardly matters) keep their N = 5 * 10^4 tests.
# The cases above are still generated and shuffled so the unchanged tests keep their bytes; `override` replaces
# some of them, `extra` adds tests at the end. All new data comes from R, not from `random`.
R = random.Random(26112)
rr = R.random
M = 100000
def ri(a, b): return a + int(rr() * (b - a + 1))
def rnd2(n, span, lmax, f=1):
    I = []
    for _ in range(n):
        l = int(rr() * span); I.append((l * f, min(span, l + 1 + int(rr() * lmax)) * f))
    return I
def shuf(I):
    R.shuffle(I)
    return I
def sorted_points(n, lo, hi):
    """n distinct sorted times in [lo, hi)"""
    return sorted(R.sample(range(lo, hi), n))
override = {
    13: rnd2(M, B, B),
    14: rnd2(M, B, 10**4),
    17: shuf([(i, B - i) for i in range(M)]),            # nested
    18: shuf([(i * 10000, i * 10000 + 10000) for i in range(M)]),   # touching, never overlapping
    20: rnd2(M, 10**6, 10),
    21: shuf([(i, i + 1) for i in range(M // 2)] + [(i, i + 2) for i in range(M // 2)]),
    22: rnd2(M, 10**9, 10**9),
    23: rnd2(M, 10**5, 50, 10**4),
    24: rnd2(M, 10**9, 10**6),
    25: rnd2(M, 5000, 5000, 2 * 10**5),
}
extra = []
L, Rt = sorted_points(M, 0, B // 2), sorted_points(M, B // 2 + 1, B + 1)
extra.append(shuf(list(zip(L, Rt[::-1]))))                       # random nested, all endpoints distinct
L, Rt = sorted_points(M, 0, 10**8), sorted_points(M, 9 * 10**8, B + 1)
R.shuffle(Rt); extra.append(list(zip(L, Rt)))                    # all long, crossing
L = sorted_points(M, 0, B // 2)
extra.append(shuf([(l, l + B // 2) for l in L]))                 # sliding: every interval half the day
extra.append(shuf([(l, B) for l in sorted_points(M, 0, B)]))     # all stay until the end
extra.append([(ri(0, B // 3), ri(2 * B // 3, B)) for _ in range(M)])
extra.append(shuf([(ri(0, 10**6), B - ri(0, 10**6)) for _ in range(M // 2)] + rnd2(M // 2, B, B)))
extra.append([(lambda l: (l, l + ri(B // 4, B - l)))(ri(0, 3 * B // 4 - 1)) for _ in range(M)])
for i, I in enumerate(cases + extra, 1):
    if i <= len(cases):
        random.shuffle(I) if i > 5 else None
    if i in override:
        I = override[i]
    Ls, Rs = list(map(g0, I)), list(map(g1, I))
    assert 1 <= len(I) <= 100000 and min(Ls) >= 0 and max(Rs) <= B and all(map(lt, Ls, Rs))
    open(f"tests/{i:02d}.in", "w").write(f"{len(I)}\n" + "".join(f"{l} {r}\n" for l, r in I))
assert len(cases) + len(extra) <= 40
print(len(cases) + len(extra), "tests")
