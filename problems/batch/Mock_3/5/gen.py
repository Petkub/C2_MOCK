import random, os
random.seed(2615)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((3, 1, [1, 0, 0]))
cases.append((5, 2, [0, 0]))
cases.append((4, 1, [1, 0, 4]))
cases.append((10, 0, [0, 0, 0]))
cases.append((6, 2, [2, 0, 0, 0, 6]))
cases.append((7, 3, [0]))
cases.append((7, 3, [4]))
for _ in range(6):
    n = random.randint(2, 7); m = random.randint(1, 5)
    cases.append((m, random.randint(0, 4), [random.choice([0, 0, random.randint(1, m)]) for _ in range(n)]))
N = 5000
def rnd(n, m, D, pf):
    return (m, D, [random.randint(1, m) if random.random() < pf else 0 for _ in range(n)])
cases.append(rnd(300, 300, 7, 0.1))
cases.append(rnd(N, N, 1, 0.0))
cases.append(rnd(N, N, N, 0.0))                       # D >= M: no restriction, M^N
cases.append(rnd(N, N, 2500, 0.01))
cases.append(rnd(N, N, 400, 0.002))
# fixed values that are far apart but reachable with the given D
a = [0] * N
for i in range(0, N, 500): a[i] = 1 if (i // 500) % 2 == 0 else 1 + 499 * 3
cases.append((N, 3, a[:]))
a[1] = 1000; cases.append((N, 3, a[:]))                  # conflicting fixed values -> 0
cases.append((1, 0, [0] * N))
cases.append((N, 0, [0] * N))                          # D = 0: all equal, M ways
cases.append((N, 4999, [random.randint(1, N) for _ in range(N)]))   # fully fixed
cases.append(rnd(N, 2000, 900, 0.0))
cases.append(rnd(N, N, 1000, 0.001))
cases.append(rnd(N, 4000, 1999, 0.0005))
for D in (300, 700, 1500, 3000):
    cases.append(rnd(N, N, D, 0.001))
for D in (500, 1200, 2500):
    cases.append(rnd(N, N, D, 0.0005))
cases.append(rnd(400, 500, 20, 0.05))
for i, (m, D, a) in enumerate(cases, 1):
    n = len(a)
    assert 1 <= n <= N and 1 <= m <= N and 0 <= D <= N and all(0 <= x <= m for x in a)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {m} {D}\n" + " ".join(map(str, a)) + "\n")
print(len(cases), "tests")
