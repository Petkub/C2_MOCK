import random, os
random.seed(2608)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append([(5, 4), (6, 7), (6, 4), (2, 3)])
cases.append([(3, 3), (3, 4), (3, 5)])
cases.append([(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
cases.append([(7, 7)])
cases.append([(1, 1), (2, 2), (2, 3), (3, 2), (3, 3), (4, 4)])
cases.append([(1, 10), (2, 2), (3, 3), (4, 4), (5, 11)])
for _ in range(6):
    n = random.randint(1, 12); cases.append([(random.randint(1, 6), random.randint(1, 6)) for _ in range(n)])
N, B = 50000, 10**9
def rnd(n, wr, hr): return [(random.randint(1, wr), random.randint(1, hr)) for _ in range(n)]
cases.append(rnd(5000, 100, 100))
cases.append(rnd(N, B, B))
cases.append(rnd(N, 1000, 1000))                       # many equal widths/heights
cases.append(rnd(N, 10, B))                            # few widths: tie handling matters
cases.append([(i, i) for i in range(1, N + 1)])        # answer N
cases.append([(i, N + 1 - i) for i in range(1, N + 1)])  # answer 1
cases.append([(i // 2 + 1, i // 2 + 1) for i in range(N)])  # pairs of equal dolls
cases.append([(random.randint(1, B), 7) for _ in range(N)])   # all same height: 1
cases.append([(x, x + random.randint(-50, 50)) for x in sorted(random.sample(range(100, B), N))])
cases.append([(i // 1000 + 1, random.randint(1, 1000)) for i in range(N)])
for wr, hr in ((10**9, 10**9), (300, 300), (50, 10**9), (10**9, 50)):
    cases.append(rnd(random.randint(30000, 50000), wr, hr))
cases.append(rnd(100000, B, B))
cases.append(rnd(100000, 3000, 3000))
for i, p in enumerate(cases, 1):
    assert 1 <= len(p) <= 100000 and all(1 <= w <= B and 1 <= h <= B for w, h in p)
    random.shuffle(p) if i > 5 else None
    open(f"tests/{i:02d}.in", "w").write(f"{len(p)}\n" + "".join(f"{w} {h}\n" for w, h in p))
print(len(cases), "tests")
