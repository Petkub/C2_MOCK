import random, os
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
for i, J in enumerate(cases, 1):
    assert 1 <= len(J) <= 100000 and all(1 <= t <= B and 1 <= d <= B for t, d in J)
    random.shuffle(J) if i > 5 else None
    open(f"tests/{i:02d}.in", "w").write(f"{len(J)}\n" + "".join(f"{t} {d}\n" for t, d in J))
print(len(cases), "tests")
