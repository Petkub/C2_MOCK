import random, os
random.seed(2614)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([3, 2, 4, 1, 2], [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]))
cases.append(([5, 5, 5], []))
cases.append(([1, 1, 1], [(1, 2), (2, 3), (3, 1)]))
cases.append(([2, 3, 3], [(1, 3), (2, 3)]))
cases.append(([4, 1, 1, 1, 6], [(1, 5), (2, 3), (3, 4), (4, 5), (2, 4)]))
def dag(n, m, tmax, cyc=False, layered=None):
    perm = list(range(1, n + 1)); random.shuffle(perm); E = []
    while len(E) < m - cyc:
        if layered:
            i = random.randrange(n - layered); j = random.randint(i + 1, min(n - 1, i + layered))
        else:
            i, j = sorted(random.sample(range(n), 2))
        E.append((perm[i], perm[j]))
    if cyc:
        a, b = random.choice(E) if E else (perm[0], perm[1]); E.append((b, a))   # reverse an existing edge: cycle
    random.shuffle(E)
    return ([random.randint(1, tmax) for _ in range(n)], E)
for _ in range(6):
    n = random.randint(1, 8)
    cases.append(dag(n, random.randint(0, 10) if n > 1 else 0, 5, cyc=(n > 2 and random.random() < 0.3)))
N, M, B = 50000, 50000, 10**9
cases.append(dag(3000, 6000, 1000))
cases.append(dag(N, M, B))
cases.append(dag(N, M, 10, layered=5))                    # deep: long chains, many ties
cases.append(dag(N, M, 1, layered=3))                     # all equal durations: many critical courses
cases.append(dag(N, M, B, cyc=True, layered=50))          # one cycle hidden in a large graph
cases.append(([B] * N, [(i, i + 1) for i in range(1, N)]))  # one long chain: 2*10^14
cases.append(([random.randint(1, B) for _ in range(N)], []))
cases.append(([1] * N, [(1, i) for i in range(2, N + 1)]))   # star: every course critical
E = [(i, i + 1) for i in range(1, N)] + [(N, 1)]            # big cycle
cases.append(([1] * N, E))
# two parallel chains of equal length -> both critical; plus a short branch
h = N // 2
E = [(i, i + 1) for i in range(1, h)] + [(i, i + 1) for i in range(h + 1, N)]
cases.append(([2] * N, E))
cases.append(dag(N, M, 1000, layered=1000))
for n, m, tmax, lay in ((30000, 60000, 10**9, None), (40000, 40000, 5, 4), (50000, 80000, 100, 20), (30000, 90000, 1, 2)):
    cases.append(dag(n, m, tmax, layered=lay))
cases.append(dag(100000, 100000, B))
cases.append(([10**9] * 100000, [(i, i + 1) for i in range(1, 100000)]))
cases.append(([10**9] * 5000, [(i, i + 1) for i in range(1, 5000)] + [(1, 5000)]))
cases.append(dag(20000, 40000, 10**9, layered=3))
for i, (t, E) in enumerate(cases, 1):
    n = len(t)
    assert 1 <= n <= 100000 and len(E) <= 100000 and all(1 <= x <= B for x in t) and all(1 <= a <= n and 1 <= b <= n and a != b for a, b in E)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {len(E)}\n" + " ".join(map(str, t)) + "\n" + "".join(f"{a} {b}\n" for a, b in E))
print(len(cases), "tests")
