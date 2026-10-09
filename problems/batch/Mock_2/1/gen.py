import random, os
random.seed(2606)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((3, 2, [1, 2, 3, 4, 5]))
cases.append((5, 1, [-5, 5, 10, -3, 3]))
cases.append((4, 3, [2, 2, 2, 2, 2, 2]))
cases.append((7, 1, [7]))
cases.append((1000000000, 1, [1000000000, -1000000000, 1000000000]))
for _ in range(6):
    n = random.randint(1, 15)
    cases.append((random.randint(1, 10), random.randint(1, n), [random.randint(-20, 20) for _ in range(n)]))
N, B = 100000, 10**9
def rnd(n, K, L, lo, hi): return (K, L, [random.randint(lo, hi) for _ in range(n)])
cases.append(rnd(3000, 7, 10, -B, B))
cases.append(rnd(N, 7, 1, -B, B))
cases.append(rnd(N, 1, 1, -B, B))                       # every subarray: answer ~2*10^10
cases.append(rnd(N, 1000, 50, -B, B))
cases.append(rnd(N, 10**9, 1, -1, 1))                   # sums are small: divisible only when 0
cases.append(rnd(N, 999999937, 1000, -B, B))
cases.append(rnd(N, 2, N - 1, -B, B))
cases.append((3, 1, [-1] * N))                          # all negative
cases.append((3, 100, [random.choice([-B, B, 0]) for _ in range(N)]))
cases.append(rnd(N, 12345, 77777, -5, 5))
for K, L in ((13, 1), (2, 5000), (100003, 3), (6, 20000), (1, 30000)):
    cases.append(rnd(random.randint(30000, 50000), K, L, -B, B))
cases.append(rnd(100000, 2, 1, -B, B))
cases.append(rnd(100000, 3, 10, -B, B))
cases.append(rnd(80000, 1, 7, -5, 5))
cases.append(rnd(100000, 2, 3, -9, 9))
cases.append(rnd(100000, 4, 100, 0, 0))
for i, (K, L, a) in enumerate(cases, 1):
    n = len(a)
    assert 1 <= n <= 100000 and 1 <= K <= 10**9 and 1 <= L <= n and all(abs(x) <= 10**9 for x in a)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {K} {L}\n" + " ".join(map(str, a)) + "\n")
print(len(cases), "tests")
