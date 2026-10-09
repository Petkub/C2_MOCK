import random, os
random.seed(2601)
os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples (01-05) ----
cases.append((1, 0, 10, [(2, 1), (7, 2), (12, 1)]))
cases.append((2, 0, 10, [(2, 1), (7, 2), (12, 1)]))
cases.append((2, 3, 5, [(4, 3), (0, 1), (10, 2), (4, 1)]))
cases.append((3, 5, 5, [(5, 7), (5, 1), (5, 100), (6, 1)]))
cases.append((2, -10**9, 10**9, [(10**9, 1), (-10**9, 10**9)]))
# ---- small random (brute-checkable) ----
for _ in range(6):
    n = random.randint(1, 8)
    k = random.randint(1, n)
    A = random.randint(-30, 30); B = A + random.randint(0, 30)
    cases.append((k, A, B, [(random.randint(-40, 40), random.randint(1, 5)) for _ in range(n)]))
# ---- large ----
def big(n, k, A, B, xr, sr):
    return (k, A, B, [(random.randint(*xr), random.randint(*sr)) for _ in range(n)])
N = 100000
cases.append(big(N, 1, -10**9, 10**9, (-10**9, 10**9), (1, 1000)))
cases.append(big(N, N, -10**9, 10**9, (-10**9, 10**9), (1, 10**9)))
cases.append(big(N, 50000, -10**9, 10**9, (-10**9, 10**9), (1, 1000)))
cases.append(big(50000, 777, 0, 10**6, (0, 10**6), (1, 3)))
cases.append(big(N, 30000, -5 * 10**8, 5 * 10**8, (-10**9, 10**9), (1, 1)))
cases.append(big(50000, 1000, 123456, 123456, (-10**9, 10**9), (1, 1000)))     # A = B
# towers all outside [A, B]
cases.append((5000, -1000, 1000, [(random.choice([-1, 1]) * random.randint(10**8, 10**9), random.randint(1, 100)) for _ in range(N)]))
# overflow trap: huge s, answer near 2e9
t = [(10**9, 1)] + [(random.randint(-10**9, 10**9), 10**9) for _ in range(N - 1)]
cases.append((N, -10**9, 10**9, t))
# dense equal positions, answer 0
cases.append((N, 42, 42, [(42, random.randint(1, 10**9)) for _ in range(N)]))
# evenly spaced, small s: answer depends on gaps
cases.append((3, 0, 999999, [(i * 10, 1 + (i % 3)) for i in range(N)]))
# intervals touch exactly (r + 1 = l') at the answer P = 5
cases.append((1, 0, 11 * (N - 1), [(11 * i, 1) for i in range(N)]))
cases.append((2, 0, 11 * 300, [(11 * i, 1) for i in range(301)] + [(11 * i + 5, 1) for i in range(301)]))
# binding gap at the left end A: every tower is far to the right of A
cases.append(big(N, 3, -10**6, 10**9, (0, 10**9), (1, 1000)))
cases.append(big(N, 20, -10**9, -10**9 + 10**6, (-10**9 + 10**6, 10**9), (1, 10**4)))
# more large random
cases.append(big(50000, 49999, 0, 10**9, (0, 10**9), (1, 10**9)))
for i, (k, A, B, t) in enumerate(cases, 1):
    n = len(t)
    assert 1 <= k <= n <= 100000 and -10**9 <= A <= B <= 10**9
    assert all(-10**9 <= x <= 10**9 and 1 <= s <= 10**9 for x, s in t)
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(f"{n} {k} {A} {B}\n" + "".join(f"{x} {s}\n" for x, s in t))
print(len(cases), "tests")
