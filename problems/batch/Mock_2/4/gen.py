import random, os
random.seed(2609)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([5, 1, 4, 2, 3], [(1, 2), (2, 3), (3, 4), (4, 5)], [2, 4, 1, 3]))
cases.append(([10, 20, 30], [(1, 2), (2, 3), (1, 3)], [1, 2, 3]))
cases.append(([3, 3], [(1, 2), (1, 2)], [2, 1]))
cases.append(([7, 1, 1, 1], [(2, 3), (3, 4)], [1, 2]))
cases.append(([0, 0, 5, 0], [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)], [5, 3, 1, 4, 2]))
def rnd(n, m, pmax, conn=False):
    E = []
    if conn:
        for v in range(2, n + 1): E.append((random.randint(1, v - 1), v))
    while len(E) < m:
        u, v = random.sample(range(1, n + 1), 2); E.append((u, v))
    random.shuffle(E)
    o = list(range(1, m + 1)); random.shuffle(o)
    return ([random.randint(0, pmax) for _ in range(n)], E, o)
for _ in range(6):
    n = random.randint(2, 9); cases.append(rnd(n, random.randint(1, 12), 10))
N, M, B = 50000, 50000, 10**9
cases.append(rnd(3000, 6000, 1000))
cases.append(rnd(N, M, B, True))
cases.append(rnd(N, N - 1, B, True))                  # a tree: every closure splits a group
cases.append(rnd(N, M, 1))
cases.append(rnd(N, 60000, B))                         # sparse: many small groups
# path 1-2-...-N closed from the middle outwards
E = [(i, i + 1) for i in range(1, N)]
o = sorted(range(1, N), key=lambda i: abs(i - N // 2))
cases.append(([B] * N, E, o))
# star: centre has huge population
E = [(1, i) for i in range(2, N + 1)]; o = list(range(1, N)); random.shuffle(o)
cases.append(([B] + [random.randint(0, 10) for _ in range(N - 1)], E, o))
# two dense blobs joined by one bridge closed first
half = N // 2
E = [(random.randint(1, half), random.randint(1, half)) for _ in range(M // 2 - 1)]
E += [(random.randint(half + 1, N), random.randint(half + 1, N)) for _ in range(M // 2 - 1)]
E = [(u, v) for u, v in E if u != v]
E.append((1, N))
o = [len(E)] + random.sample(range(1, len(E)), len(E) - 1)
cases.append(([random.randint(0, B) for _ in range(N)], E, o))
cases.append(rnd(N, M, 0))                             # all zero populations
cases.append(rnd(2, 1, B))
for n, m, conn in ((30000, 30000, True), (40000, 20000, False), (20000, 50000, True), (50000, 49999, True)):
    cases.append(rnd(n, m, B, conn))
cases.append(rnd(100000, 100000, B, True))
cases.append(rnd(100000, 99999, B, True))
for i, (p, E, o) in enumerate(cases, 1):
    n, m = len(p), len(E)
    assert 1 <= n <= 100000 and 1 <= m <= 100000 and sorted(o) == list(range(1, m + 1))
    assert all(1 <= u <= n and 1 <= v <= n and u != v for u, v in E) and all(0 <= x <= B for x in p)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {m}\n" + " ".join(map(str, p)) + "\n" + "".join(f"{u} {v}\n" for u, v in E) + " ".join(map(str, o)) + "\n")
print(len(cases), "tests")
