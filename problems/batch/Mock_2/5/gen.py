import random, os
random.seed(2610)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([3, 1, 4, 1, 5], [(1, 2, 2), (1, 3, 1), (3, 4, 3), (3, 5, 2)]))
cases.append(([1, 1, 1, 1], [(1, 2, 1), (2, 3, 1), (3, 4, 1)]))
cases.append(([9], []))
cases.append(([0, 5, 0], [(1, 2, 7), (1, 3, 1)]))
cases.append(([2, 2], [(1, 2, 1000)]))
def tree(n, cmax, wmax, shape="random"):
    E = []
    for v in range(2, n + 1):
        if shape == "path": u = v - 1
        elif shape == "star": u = 1
        elif shape == "caterpillar": u = v - 1 if v % 2 == 0 else max(1, v - 2)
        elif shape == "deep": u = random.randint(max(1, v - 3), v - 1)
        else: u = random.randint(1, v - 1)
        E.append((u, v, random.randint(1, wmax)))
    perm = list(range(1, n + 1)); random.shuffle(perm)       # relabel so node 1 is not special
    E = [(perm[u - 1], perm[v - 1], w) for u, v, w in E]; random.shuffle(E)
    return ([random.randint(0, cmax) for _ in range(n)], E)
for _ in range(6):
    cases.append(tree(random.randint(2, 9), 5, 5))
N = 50000
cases.append(tree(3000, 1000, 1000))
cases.append(tree(N, 1000, 1000))
cases.append(tree(N, 1000, 1000, "path"))
cases.append(tree(N, 1000, 1000, "star"))
cases.append(tree(N, 1000, 1000, "deep"))
cases.append(tree(N, 1000, 1000, "caterpillar"))
cases.append(([1000] * N, tree(N, 0, 1000, "path")[1]))   # max answer, needs 64-bit
cases.append(([0] * N, tree(N, 0, 1000)[1]))              # nobody lives anywhere: answer 0 at node 1
c = [0] * N; c[N // 3] = 1000; c[2 * N // 3] = 1000         # two heavy villages: a tie along a path
cases.append((c, [(i, i + 1, 1) for i in range(1, N)]))
cases.append(tree(N, 1, 1))
for shape in ("random", "path", "deep", "caterpillar"):
    cases.append(tree(random.randint(30000, 50000), 1000, 1000, shape))
cases.append(tree(100000, 1000, 1000))
cases.append(([1000] * 100000, tree(100000, 0, 1000, "path")[1]))
for i, (c, E) in enumerate(cases, 1):
    n = len(c)
    assert 1 <= n <= 100000 and len(E) == n - 1 and all(0 <= x <= 1000 for x in c) and all(1 <= w <= 1000 for _, _, w in E)
    open(f"tests/{i:02d}.in", "w").write(f"{n}\n" + " ".join(map(str, c)) + "\n" + "".join(f"{u} {v} {w}\n" for u, v, w in E))
print(len(cases), "tests")
