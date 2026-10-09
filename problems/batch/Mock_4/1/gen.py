import random, os
random.seed(2616)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((7, 10, [2, 5, 3, 8, 6]))
cases.append((10, 10, [5, 5, 5, 5]))
cases.append((1, 3, [7, 9]))
cases.append((4, 4, [2]))
cases.append((3, 12, [1, 2, 3, 4, 5, 6]))
for _ in range(6):
    n = random.randint(1, 12); L = random.randint(2, 25)
    cases.append((L, L + random.randint(0, 12), [random.randint(1, 15) for _ in range(n)]))
B = 10**9
def rnd(n, L, R, hi): return (L, R, [random.randint(1, hi) for _ in range(n)])
cases.append(rnd(3000, 10**8, 9 * 10**8, B))
cases.append(rnd(100000, 2, 2 * B, B))                       # every pair: ~5*10^9
cases.append(rnd(100000, B, B + 10**6, B))
cases.append(rnd(100000, 3 * B // 2, 2 * B, B))              # sums above 2^31
cases.append((2, 2 * B, [B] * 100000))                        # all equal, sum = 2*10^9
cases.append(rnd(100000, 1, 1, B))                            # nothing fits
for L, R, hi in ((500, 1500, 1000), (10**6, 10**6, 10**6), (B, 2 * B, B), (12345678, 87654321, 10**8), (1, 2 * B, 10)):
    cases.append(rnd(random.randint(30000, 50000), L, R, hi))
cases.append(rnd(50000, 1000, 1000, 999))                     # many duplicates, exact-sum window
cases.append((2 * B - 1, 2 * B - 1, [B - 1, B, B, 1, 1]))
for R in (13 * 10**8, 16 * 10**8, 11 * 10**8):          # answers above 2^31 without taking every pair
    cases.append(rnd(100000, random.randint(0, 10**8), R, B))
for L, R in ((2 * 10**8, 15 * 10**8), (0, 12 * 10**8), (3 * 10**8, 2 * B), (5 * 10**8, 17 * 10**8)):
    cases.append(rnd(100000, L, R, B))
for L, R in ((10**9, 10**9 + 5), (5, 300), (1999999990, 2 * B)):   # large N, small answers
    cases.append(rnd(100000, L, R, B))
for i, (L, R, p) in enumerate(cases, 1):
    n = len(p)
    assert 1 <= n <= 100000 and 0 <= L <= R <= 2 * B and all(1 <= x <= B for x in p)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {L} {R}\n" + " ".join(map(str, p)) + "\n")
print(len(cases), "tests")
