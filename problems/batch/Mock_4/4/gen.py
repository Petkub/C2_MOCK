import random, os
random.seed(2619)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((3, [(1, 2, 4), (2, 3, 5)], [(1, 3, 3), (1, 2, 1)]))
cases.append((4, [(1, 2, 10), (2, 3, 10), (3, 4, 10)], [(1, 4, 100), (1, 4, 5)]))
cases.append((2, [(1, 2, 7), (1, 2, 3)], [(2, 1, 5)]))
cases.append((4, [(1, 2, 1), (1, 3, 1), (1, 4, 1)], [(2, 3, 1), (3, 4, 1), (2, 4, 1)]))
cases.append((5, [(1, 2, 3), (2, 3, 3), (3, 4, 3), (4, 5, 3)], [(1, 5, 1), (2, 4, 2), (1, 3, 9)]))
W = 10**6
def graph(n, m, q, wmax, qw=None):
    E = [(random.randint(1, v - 1), v, random.randint(1, wmax)) for v in range(2, n + 1)]
    while len(E) < m: E.append((*random.sample(range(1, n + 1), 2), random.randint(1, wmax)))
    random.shuffle(E)
    E = [(v, u, w) if random.random() < 0.5 else (u, v, w) for u, v, w in E]
    qw = qw or wmax
    Q = [(*random.sample(range(1, n + 1), 2), random.randint(1, qw)) for _ in range(q)]
    perm = list(range(1, n + 1)); random.shuffle(perm)
    E = [(perm[u - 1], perm[v - 1], w) for u, v, w in E]; Q = [(perm[u - 1], perm[v - 1], w) for u, v, w in Q]
    return (n, E, Q)
for _ in range(6):
    n = random.randint(2, 8); cases.append(graph(n, random.randint(n - 1, 12), random.randint(1, 5), 20))
cases.append(graph(60, 59, 60, W))
cases.append(graph(300, 299, 300, W))                   # a tree, new roads shortcut it
cases.append(graph(300, 10000, 300, W))
cases.append(graph(300, 299, 300, W, qw=10))            # very cheap new roads
cases.append(graph(300, 2000, 300, 1000, qw=W))         # new roads mostly useless
n = 300; E = [(i, i + 1, W) for i in range(1, n)]
cases.append((n, E, [(random.randint(1, n), random.randint(1, n), random.randint(1, W)) for _ in range(300)]))
cases[-1] = (n, E, [(u, v, w) for u, v, w in cases[-1][2] if u != v][:300])
cases.append(graph(300, 10000, 300, 5))
cases.append(graph(250, 5000, 300, W))
cases.append(graph(300, 1000, 300, W, qw=W // 100))
cases.append(graph(200, 300, 300, W))
cases.append(graph(300, 400, 300, W, qw=W))
cases.append(graph(280, 3000, 300, W))
cases.append(graph(300, 300, 300, W, qw=W // 10))
for i, (n, E, Q) in enumerate(cases, 1):
    assert 2 <= n <= 300 and n - 1 <= len(E) <= 10000 and 1 <= len(Q) <= 300
    assert all(1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= W for u, v, w in E + Q)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {len(E)} {len(Q)}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in E + Q))
print(len(cases), "tests")
