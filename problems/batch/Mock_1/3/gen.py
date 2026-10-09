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
for i, (k, L, a) in enumerate(cases, 1):
    n = len(a)
    assert 1 <= n <= 100000 and 1 <= k <= 100 and 1 <= L <= n and k * (L + 1) <= n + 1
    assert all(-10**9 <= x <= 10**9 for x in a)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {k} {L}\n" + " ".join(map(str, a)) + "\n")
print(len(cases), "tests")
