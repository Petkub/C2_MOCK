import random, os
random.seed(2618)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((10, 1, [(8, 5), (6, 4), (5, 3)]))
cases.append((10, 0, [(8, 5), (6, 4), (5, 3)]))
cases.append((3, 2, [(1, 7), (1, 7), (6, 10)]))
cases.append((0, 5, [(4, 1), (5, 2)]))
cases.append((20, 3, [(15, 9), (9, 8), (7, 7), (11, 9), (3, 1)]))
for _ in range(7):
    n = random.randint(1, 7)
    cases.append((random.randint(0, 40), random.randint(0, 3), [(random.randint(1, 20), random.randint(1, 30)) for _ in range(n)]))
V = 10**9
def rnd(n, Bm, C, pmax, vmax): return (Bm, C, [(random.randint(1, pmax), random.randint(1, vmax)) for _ in range(n)])
cases.append(rnd(100, 50000, 10, 50000, V))
cases.append(rnd(100, 50000, 10, 2000, V))                    # most items affordable: values sum near 10^11
cases.append(rnd(100, 50000, 0, 5000, V))
cases.append(rnd(100, 1, 10, 3, V))                           # only coupon items (price 1 -> 0) fit
cases.append(rnd(100, 50000, 10, 50000, 1))                   # maximise count
cases.append((50000, 10, [(random.choice([2, 3]) * 10000 + 1, V) for _ in range(100)]))
cases.append(rnd(100, 37777, 5, 1500, V))
cases.append(rnd(60, 50000, 10, 50000, V))
cases.append(rnd(100, 49999, 7, 49999, V))
cases.append(rnd(100, 50000, 3, 999, V))
cases.append((50000, 1, [(50000, V)] + [(1, 1)] * 99))
cases.append(rnd(100, 25000, 10, 10000, V))
cases.append(rnd(80, 50000, 2, 50000, V))
cases.append((50000, 10, [(random.randint(40000, 50000), V - random.randint(0, 1000)) for _ in range(100)]))
for Bm in (777, 3001, 12345, 49999, 101, 2023, 555, 8191):                       # odd prices and tight budgets: rounding matters
    cases.append((Bm, 10, [(2 * random.randint(0, 2000) + 1, random.randint(V // 2, V)) for _ in range(100)]))
for i, (Bm, C, it) in enumerate(cases, 1):
    n = len(it)
    assert 1 <= n <= 100 and 0 <= Bm <= 50000 and 0 <= C <= 10 and all(1 <= p <= 50000 and 1 <= v <= V for p, v in it)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {Bm} {C}\n" + "".join(f"{p} {v}\n" for p, v in it))
print(len(cases), "tests")
