import random, os
from operator import itemgetter
random.seed(2613)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append([(3, 5), (2, 4), (4, 9), (1, 3)])
cases.append([(5, 5), (1, 5), (1, 5), (1, 5), (1, 5), (1, 5)])
cases.append([(10, 4), (3, 3)])
cases.append([(2, 2)])
cases.append([(4, 4), (1, 5), (1, 6), (5, 7)])
for _ in range(6):
    n = random.randint(1, 12); cases.append([(random.randint(1, 8), random.randint(1, 25)) for _ in range(n)])
N, B = 50000, 10**9
def rnd(n, tmax, dmax): return [(random.randint(1, tmax), random.randint(1, dmax)) for _ in range(n)]
cases.append(rnd(3000, 1000, 10**5))
cases.append(rnd(N, B, B))
cases.append(rnd(N, B, 10**14 // 10**5) if False else rnd(N, 10**4, 10**8))
cases.append(rnd(N, 10**9, 10**9))
cases.append([(B, B)] * N)                               # only one fits
cases.append([(1, B)] * N)                               # all fit
cases.append([(random.randint(1, 100), random.randint(1, 10**6)) for _ in range(N)])
# long job with early deadline should be dropped for many short ones
cases.append([(B, B)] + [(1, B) for _ in range(N - 1)])
# shortest-first trap: short jobs with late deadlines vs medium jobs with early deadlines
J = [(5, 5 * (i + 1)) for i in range(N // 2)] + [(1, B) for _ in range(N // 2)]
cases.append(J)
cases.append([(random.randint(1, 10), i + random.randint(0, 5)) for i in range(1, N + 1)])
for tmax, dmax in ((10**9, 10**9), (1000, 10**6), (10**5, 10**8), (10, 10**5)):
    cases.append(rnd(random.randint(30000, 50000), tmax, dmax))
cases.append(rnd(100000, B, B))
cases.append(rnd(100000, 1000, 10**7))
cases.append([(random.randint(11, 100), random.randint(1, 10)) for _ in range(1000)])
# ---- legacy strengthening (2026-10): the O(N * answer) DP, SJF-with-feasibility-check and the exchange greedy
# with a linear max scan all pass N = 5e4; big tests below are N = 10^5 with large answers and frequent drops.
# The cases above are still generated (and shuffled) so the unchanged tests keep their bytes; `override`
# replaces some of them, `extra` adds tests at the end. All new data comes from R, not from `random`;
# i.i.d. lists are already in random order, structured ones go through shuf().
R = random.Random(26133)
rr = R.random
def ri(a, b): return a + int(rr() * (b - a + 1))     # fast randint for the big tests
def shuf(J):
    R.shuffle(J)
    return J
M = 100000
def rnd2(n, tmax, dmax): return [(1 + int(rr() * tmax), 1 + int(rr() * dmax)) for _ in range(n)]
def corr(n, dmax, a, noise, sign=1):
    """durations grow (sign 1) or shrink (sign -1) with the deadline: d * a (+ noise), so most jobs must be dropped"""
    J = []
    for _ in range(n):
        d = ri(1, dmax)
        J.append((max(1, int((d if sign > 0 else dmax - d) * a) + ri(0, noise)), d))
    return J
override = {                                             # the same families as before, at N = 10^5 with large answers
    13: rnd2(M, 20000, 7 * 10**8),
    14: rnd2(M, 10**4, 3 * 10**8),
    15: rnd2(M, 30000, B),
    17: [(1, B)] * M,                                    # all fit: answer 10^5
    18: rnd2(M, 100, 4 * 10**6),
    19: shuf([(B, B)] + [(1, B) for _ in range(M - 1)]),
    20: shuf([(5, 5 * (i + 1)) for i in range(M // 2)] + [(1, B) for _ in range(M // 2)]),
    21: shuf([(ri(1, 10), 4 * i + ri(0, 20)) for i in range(1, M + 1)]),
    23: rnd2(M, 1000, 5 * 10**7),
    24: rnd2(M, 40000, B),
    25: rnd2(M, 10, 5 * 10**5),
}
extra = []
# many cheap jobs fill the schedule, then every later job overflows it and one job must be dropped each time
A = [(ri(1, 3), ri(1, 10**5)) for _ in range(M // 2)]
A += [(ri(1, 1000), ri(10**5, 2 * 10**5)) for _ in range(M // 2)]
extra.append(shuf(A))
# one deadline for all: the answer is the most short jobs that fit
extra.append([(ri(1, 20000), 6 * 10**8) for _ in range(M)])
# few distinct deadlines, overloaded between them
extra.append([(ri(1, 10000), 10**7 * ri(1, 30)) for _ in range(M)])
# long job with an early deadline, then many short jobs: the long one must go (repeated in blocks)
A = []
for b in range(1000):
    A.append((900, 1000 * b + 1000))
    A += [(ri(5, 15), 1000 * b + ri(1, 1000)) for _ in range(99)]
extra.append(shuf(A))
# shortest-first trap at full size: medium jobs with early deadlines vs short jobs with late ones
extra.append(shuf([(4, 4 * (i + 1)) for i in range(60000)] + [(1, B) for _ in range(40000)]))
# deadlines growing with the index, durations a bit too long on average
extra.append(shuf([(ri(1, 30), 10 * i + ri(0, 50)) for i in range(1, M + 1)]))
# durations grow with the deadline (about 40% of the jobs must go), plus a few jobs that break shortest-first
extra.append(shuf(corr(M - 3000, B, 4e-5, 10) + [(1000, B)] * 3000))
extra.append(shuf(corr(M - 5000, 8 * 10**8, 5.5e-5, 20) + [(ri(1, 3000), ri(B // 2, B)) for _ in range(5000)]))
extra.append(shuf(corr(M - 2000, B, 4.5e-5, 5) + [(ri(1, 100), ri(1, B)) for _ in range(2000)]))
extra.append(shuf(corr(M, B, 3e-5, 1000, sign=-1)))     # durations shrink with the deadline
# heavy-tailed durations
extra.append([(R.choice((1, 10, 100, 1000, 10000)) * ri(1, 9), ri(1, 5 * 10**8)) for _ in range(M)])
# every job alone fits, together far too many
extra.append([(lambda d: (ri(1, min(d, 20000)), d))(ri(1, 6 * 10**8)) for _ in range(M)])

def check(J):
    ts, ds = list(map(itemgetter(0), J)), list(map(itemgetter(1), J))
    assert 1 <= len(J) <= 100000 and min(ts) >= 1 and max(ts) <= B and min(ds) >= 1 and max(ds) <= B
for i, J in enumerate(cases, 1):
    random.shuffle(J) if i > 5 else None
    if i in override:
        J = override[i]
    check(J)
    open(f"tests/{i:02d}.in", "w").write(f"{len(J)}\n" + "".join(f"{t} {d}\n" for t, d in J))
for i, J in enumerate(extra, len(cases) + 1):
    check(J)
    open(f"tests/{i:02d}.in", "w").write(f"{len(J)}\n" + "".join(f"{t} {d}\n" for t, d in J))
n_tests = len(cases) + len(extra)
assert n_tests <= 40
print(n_tests, "tests")
