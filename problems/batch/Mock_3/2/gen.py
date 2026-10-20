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
# ---- legacy strengthening (2026-10): the O(stores x questions) brute force scored 74% because many big tests had
# few stores or few questions. The new big tests have >= 6 * 10^4 stores and mostly questions (brute: >= 4 * 10^9
# distance computations). Small coordinates keep the files small where the size of the values does not matter.
# The cases above are still generated so the unchanged tests keep their bytes; `override` replaces some of them,
# `extra` adds tests at the end. All new data comes from R, not from `random`.
R = random.Random(26122)
rr = R.random
def ri(a, b): return a + int(rr() * (b - a + 1))
def rnd2(n, q, c, padd):
    P = [(ri(-c, c), ri(-c, c)) for _ in range(n)]
    Q = [(1 if rr() < padd else 2, ri(-c, c), ri(-c, c)) for _ in range(q)]
    return (P, Q)
def square(n, q, c, padd):
    """stores on the boundary of a square: the farthest store is a corner, not just any store with extreme x or y"""
    def pt():
        v = ri(-c, c); k = ri(0, 3)
        return [(c, v), (-c, v), (v, c), (v, -c)][k]
    P = [pt() for _ in range(n)]
    Q = [(1,) + pt() if rr() < padd else (2, ri(-c, c), ri(-c, c)) for _ in range(q)]
    return (P, Q)
def cluster(n, q, cx, cy, r, c, padd):
    """stores packed near (cx, cy), questions from anywhere: all stores almost tie"""
    P = [(cx + ri(-r, r), cy + ri(-r, r)) for _ in range(n)]
    Q = [(1, cx + ri(-r, r), cy + ri(-r, r)) if rr() < padd else (2, ri(-c, c), ri(-c, c)) for _ in range(q)]
    return (P, Q)
override = {
    13: rnd2(65000, 65000, B, 0.0),
    16: rnd2(70000, 70000, 1000, 0.1),
    18: ([(R.choice([-B, B]), R.choice([-B, B])) for _ in range(65000)], [(2, ri(-B, B), ri(-B, B)) for _ in range(65000)]),
    20: rnd2(70000, 70000, 5, 0.1),
    21: rnd2(65000, 65000, B, 0.3),
    22: rnd2(70000, 70000, 10**6, 0.2),
    23: rnd2(65000, 65000, B, 0.05),
    24: rnd2(70000, 70000, 100, 0.15),
}
extra = [
    square(70000, 70000, 10**4, 0.1),
    square(65000, 65000, B, 0.2),
    cluster(65000, 65000, 5 * 10**8, -5 * 10**8, 1000, B, 0.1),
    cluster(70000, 70000, 0, 0, 3, 10**4, 0.2),
    # stores spread outward over time: each new store is the farthest so far
    ([(ri(-1000, 1000), ri(-1000, 1000)) for _ in range(65000)],
     [(1, 1000 + 7 * i, -1000 - 3 * i) if i % 10 == 0 else (2, ri(-1000, 1000), ri(-1000, 1000)) for i in range(70000)]),
    # the same question again and again
    rnd2(70000, 0, 10**5, 0)[:1] + ([(1, ri(-10**5, 10**5), ri(-10**5, 10**5)) if i % 8 == 0 else (2, 12345, -6789) for i in range(70000)],),
    rnd2(70000, 70000, 10**4, 0.0),
    rnd2(65000, 65000, 10**5, 0.1),
    # diamond |x| + |y| = c: many stores at the same largest distance
    ([(lambda x: (x, R.choice([-1, 1]) * (10**5 - abs(x))))(ri(-10**5, 10**5)) for _ in range(70000)],
     [(2, ri(-10**5, 10**5), ri(-10**5, 10**5)) for _ in range(70000)]),
    rnd2(70000, 70000, 50, 0.25),
]
for i, (P, Qs) in enumerate(cases + extra, 1):
    if i in override:
        P, Qs = override[i]
    assert 1 <= len(P) <= 100000 and 1 <= len(Qs) <= 100000 and any(t == 2 for t, _, _ in Qs)
    assert all(abs(x) <= B and abs(y) <= B for x, y in P) and all(abs(a) <= B and abs(b) <= B for _, a, b in Qs)
    open(f"tests/{i:02d}.in", "w").write(f"{len(P)} {len(Qs)}\n" + "".join(f"{x} {y}\n" for x, y in P) + "".join(f"{t} {a} {b}\n" for t, a, b in Qs))
assert len(cases) + len(extra) <= 40
print(len(cases) + len(extra), "tests")
