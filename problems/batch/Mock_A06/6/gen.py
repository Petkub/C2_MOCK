import random, os
random.seed(2603)
os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples ----
cases.append((2, 2, [3, -1, 4, -10, 5, -9, 2]))
cases.append((1, 1, [1, 2, 3, 4, 5]))
cases.append((2, 1, [4, 4, 4]))
cases.append((1, 6, [-3, 1, -4, 1, -5, 9]))
cases.append((3, 2, [-1, -2, 7, 8, -100, -3, -4, 6, 6]))
# ---- small random ----
def rnd(n, k, L, lo, hi):
    return (k, L, [random.randint(lo, hi) for _ in range(n)])
for _ in range(6):
    n = random.randint(3, 12); L = random.randint(1, 3)
    k = random.randint(1, max(1, (n + 1) // (L + 1)))
    cases.append(rnd(n, k, L, -20, 20))
# ---- large ----
N = 100000
B = 10**9
cases.append(rnd(N, 100, 1, -B, B))
cases.append(rnd(N, 100, 50, -B, B))
cases.append(rnd(N, 100, 990, -B, B))                 # K(L+1) = N + 1 - 1 + ... near tight
cases.append(rnd(N, 1, 1000, -B, B))
cases.append(rnd(N, 100, 1, 1, B))                    # all positive: rest days are the only loss
cases.append(rnd(N, 100, 3, -B, -1))                  # all negative
cases.append(rnd(N, 50, 1999, -B, B))                 # 50 * 2000 = 100000 <= N + 1 (tight)
cases.append((100, 999, [B if (i // 1000) % 2 == 0 else -B for i in range(N)]))
cases.append(rnd(N, 37, 7, -1000, 1000))
cases.append((100, 1, [B] * N))                        # sum fits only in 64-bit
cases.append(rnd(N, 100, 1, -B, B // 10))              # mostly negative, must still pick 100
cases.append((1, 1, [-7]))                              # N = 1
cases.append(rnd(3000, 100, 2, -B, B))                  # medium: O(N^2 K) still too slow
cases.append(rnd(5000, 20, 10, -B, B))
cases.append(rnd(N, 100, 999, -B, B))                   # tight: 100 * 1000 = N
cases.append(rnd(N, 80, 1, -5, 5))                      # many ties
cases.append(rnd(N, 2, 30000, -B, B))
cases.append(rnd(N, 100, 7, -B, B // 3))
# ---- stronger tests (2026-10-20): long runs, so the O(N K L) DP over the run length is too slow ----
# (a separate random stream, so the tests that stay as they were keep their bytes)
rng = random.Random(260320)
def big(k, L, lo, hi): return (k, L, [rng.randint(lo, hi) for _ in range(N)])
cases[14] = big(1, 40000, -B, B)                         # test 15: one long run
cases[15] = big(100, 300, 1, B)                          # test 16: all positive, rest days are the only loss
cases[16] = big(100, 600, -B, -1)                        # test 17: all negative
cases[19] = big(37, 2000, 1, 1000)                       # test 20: small positive values, every rest day costs
cases[20] = (100, 900, [B] * N)                          # test 21: sum fits only in 64-bit
cases[21] = big(100, 400, -B, B // 10)                   # test 22: mostly negative, must still pick 100
cases[26] = big(80, 250, -5, 5)                          # test 27: many ties
cases[28] = big(100, 700, -B, B // 3)                    # test 29
cases.append((100, 999, [rng.randint(1, B) for _ in range(N)]))   # K (L + 1) = N: no slack at all
# positive days with about 40 negative valleys: fewer valleys than the K - 1 rest days needed
a = [rng.randint(1, B) for _ in range(N)]
for _ in range(40):
    st = rng.randrange(N - 200)
    for j in range(st, st + rng.randint(1, 200)): a[j] = -rng.randint(1, B)
cases.append((100, 500, a))
cases.append(big(100, 800, B // 2, B))                   # all positive: where the 99 rest days go decides
cases.append(big(10, 9999, -B, B))
# long positive stretches cut by single very negative days: the best runs are much longer than L
a = []
while len(a) < N:
    a += [rng.randint(1, B) for _ in range(rng.randint(3000, 6000))] + [-B]
cases.append((35, 2500, a[:N]))
# positive blocks of length L + 1 .. 3L separated by one negative day: a rest day costs only that day
a = []
while len(a) < N:
    a += [rng.randint(B // 2, B) for _ in range(rng.randint(1000, 3000))] + [-rng.randint(1, 1000)]
cases.append((100, 300, a[:N]))
cases.append(big(99, 1000, -5, 5))
cases.append((100, 990, [-B] * N))                       # all equal negative: shortest runs everywhere
cases.append((50, 1000, [B] * N))
cases.append(big(1, 60000, -B, B))
cases.append(big(30, 3000, 1, B))
assert len(cases) <= 40
for i, (k, L, a) in enumerate(cases, 1):
    n = len(a)
    assert 1 <= n <= 100000 and 1 <= k <= 100 and 1 <= L <= n and k * (L + 1) <= n + 1
    assert all(-10**9 <= x <= 10**9 for x in a)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {k} {L}\n" + " ".join(map(str, a)) + "\n")
print(len(cases), "tests")
