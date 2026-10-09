import random, os
random.seed(2612)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(([(0, 0), (3, 4), (-2, 1)], [(2, 1, 1), (2, -5, 0), (1, 10, -10), (2, 1, 1)]))
cases.append(([(5, 5)], [(2, 5, 5), (2, 0, 0)]))
cases.append(([(1, 1), (1, 1)], [(1, -1, -1), (2, 0, 0), (2, 1, -1)]))
cases.append(([(4, -2), (-1, 3)], [(2, 1, 1), (1, 0, -5), (2, 1, 1), (2, -3, 4)]))
cases.append(([(2, 3), (-4, 1), (0, -6)], [(2, 0, 0), (2, -4, 1), (1, 7, 7), (2, -4, 1)]))
def rnd(n, q, c, padd=0.5):
    P = [(random.randint(-c, c), random.randint(-c, c)) for _ in range(n)]
    Q = [(1 if random.random() < padd else 2, random.randint(-c, c), random.randint(-c, c)) for _ in range(q)]
    if all(t == 1 for t, _, _ in Q): Q[-1] = (2, 0, 0)
    return (P, Q)
for _ in range(6):
    cases.append(rnd(random.randint(1, 6), random.randint(1, 8), 10))
N, Q, B = 50000, 50000, 10**9
cases.append(rnd(2000, 2000, B))
cases.append(rnd(N, Q, B, 0.0))
cases.append(rnd(1, Q, B, 0.5))                        # start with one point, grow online
cases.append(rnd(N, Q, B, 0.9))
cases.append(rnd(N, Q, 1000))
cases.append(([(B, B)] * 10, [(2, -B, -B)] * Q))      # 4 * 10^9: needs 64-bit
cases.append(([(random.choice([-B, B]), random.choice([-B, B])) for _ in range(N)], [(2, random.randint(-B, B), random.randint(-B, B)) for _ in range(Q)]))
cases.append(([(0, 0)], [(1, i, -i) if i % 2 else (2, -i, i) for i in range(1, Q + 1)]))
cases.append(rnd(N, Q, 5))
for c, padd in ((B, 0.3), (10**6, 0.6), (B, 0.05), (100, 0.5)):
    cases.append(rnd(random.randint(20000, 40000), random.randint(20000, 40000), c, padd))
cases.append(rnd(100000, 100000, B, 0.3))
cases.append(rnd(1, 100000, B, 0.5))
cases.append(([(-10**9, 10**9)], [(2, 10**9, -10**9)]))
for i, (P, Qs) in enumerate(cases, 1):
    assert 1 <= len(P) <= 100000 and 1 <= len(Qs) <= 100000 and any(t == 2 for t, _, _ in Qs)
    assert all(abs(x) <= B and abs(y) <= B for x, y in P) and all(abs(a) <= B and abs(b) <= B for _, a, b in Qs)
    open(f"tests/{i:02d}.in", "w").write(f"{len(P)} {len(Qs)}\n" + "".join(f"{x} {y}\n" for x, y in P) + "".join(f"{t} {a} {b}\n" for t, a, b in Qs))
print(len(cases), "tests")
