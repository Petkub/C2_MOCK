import random, os
random.seed(2601)
os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples (01-05) ----
cases.append((1, 0, 10, [(2, 1), (7, 2), (12, 1)]))
cases.append((2, 0, 10, [(2, 1), (7, 2), (12, 1)]))
cases.append((2, 3, 5, [(4, 3), (0, 1), (10, 2), (4, 1)]))
cases.append((3, 5, 5, [(5, 7), (5, 1), (5, 100), (6, 1)]))
cases.append((2, -3, 8, [(0, 2), (5, 1), (-6, 3), (9, 4)]))
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
# dense equal positions far from a single point [A, B] = [10^9, 10^9]: answer = k-th smallest ceil(2e9 / s)
cases.append((N // 2, 10**9, 10**9, [(-10**9, random.randint(1, 10**5)) for _ in range(N)]))
# evenly spaced over the whole road, small s: answer depends on the gaps (about 10^4)
cases.append((3, -10**9, 10**9, [(-10**9 + i * 20000, 1 + (i % 3)) for i in range(N)]))
# intervals touch exactly (r + 1 = l') at the answer P = 9999
cases.append((1, -10**9, -10**9 + 19999 * (N - 1), [(-10**9 + 19999 * i, 1) for i in range(N)]))
cases.append((2, 0, 11 * 300, [(11 * i, 1) for i in range(301)] + [(11 * i + 5, 1) for i in range(301)]))
# binding gap at the left end A: every tower is far to the right of A
cases.append(big(N, 3, -10**9, 10**9, (0, 10**9), (1, 1000)))
cases.append(big(N, 20, -10**9, -10**9 + 10**6, (-10**9 + 10**6, 10**9), (1, 10)))
# more large random
cases.append(big(50000, 49999, 0, 10**9, (0, 10**9), (1, 10**9)))
# the old sample 5 (answer 2000000000), moved here when the sample was replaced (2026-11-02)
cases.append((2, -10**9, 10**9, [(10**9, 1), (-10**9, 10**9)]))
# dense equal positions, answer 0 (small)
cases.append((1000, 42, 42, [(42, random.randint(1, 10**9)) for _ in range(1000)]))
# ---- large answers in (10^9, 2 * 10^9] (an upper bound of 10^9 is wrong) ----
# every tower near the right end, s = 1: the point A = -10^9 is binding
cases.append(big(N, random.randint(1, N), -10**9, 10**9, (9 * 10**8, 10**9), (1, 1)))
# mirror: every tower near the left end, s = 1 (the far point B is binding)
cases.append(big(N, N // 3, -10**9, 10**9, (-10**9, -10**9 + 10**7), (1, 1)))
# two clusters at both ends, k above one cluster: each end needs the far cluster (answer near 2e9)
t = [(random.randint(-10**9, -10**9 + 1000), 1) for _ in range(N // 2)] + \
    [(random.randint(10**9 - 1000, 10**9), 1) for _ in range(N // 2)]
random.shuffle(t)
cases.append((N // 2 + 7, -10**9, 10**9, t))
# answer exactly 10^9 + 1: [A, B] = [-1, -1], every tower at 10^9 with s = 1
cases.append((N, -1, -1, [(10**9, 1)] * N))
# random positions, s = 1, k = N: every tower covers the whole road (answer about 2e9)
cases.append(big(N, N, -10**9, 10**9, (-10**9, 10**9), (1, 1)))
# answer exactly 2 * 10^9: all towers at 10^9, s = 1 except a few useless far-right ones with big s
t = [(10**9, 1)] * (N - 10) + [(10**9, random.randint(1, 10**9)) for _ in range(10)]
cases.append((N - 5, -10**9, 10**9, t))
# towers in the right quarter, s = 1, k = N / 2: answer above 10^9
cases.append(big(N, N // 2, -10**9, 10**9, (5 * 10**8, 10**9), (1, 1)))
for i, (k, A, B, t) in enumerate(cases, 1):
    n = len(t)
    assert 1 <= k <= n <= 100000 and -10**9 <= A <= B <= 10**9
    assert all(-10**9 <= x <= 10**9 and 1 <= s <= 10**9 for x, s in t)
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(f"{n} {k} {A} {B}\n" + "".join(f"{x} {s}\n" for x, s in t))
print(len(cases), "tests")
