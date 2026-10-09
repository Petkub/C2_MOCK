import random, os
random.seed(2620)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((10, [2, 4, 7]))
cases.append((100, [25, 50, 75]))
cases.append((5, []))
cases.append((7, [1, 2, 3, 4, 5, 6]))
cases.append((20, [17, 3, 9, 4]))
cases.append((8, [7, 1, 4, 3, 5]))
cases.append((7, [4, 1, 3, 5, 2]))
for _ in range(6):
    L = random.randint(2, 40); cases.append((L, random.sample(range(1, L), random.randint(0, min(7, L - 1)))))
B = 10**9
cases.append((5000, random.sample(range(1, 5000), 60)))
cases.append((B, random.sample(range(1, B), 500)))
cases.append((501, list(range(1, 501))))                        # every unit point
cases.append((B, sorted(random.sample(range(1, 1000), 250)) + sorted(random.sample(range(B - 1000, B), 250))))
cases.append((B, [2 ** k for k in range(1, 30)]))               # geometric positions
cases.append((B, random.sample(range(1, B), 300)))
cases.append((B, [B // 501 * k for k in range(1, 501)]))        # evenly spaced
cases.append((10**6, random.sample(range(1, 10**6), 500)))
cases.append((B, [B - k for k in range(1, 501)]))               # all near one end
cases.append((B, random.sample(range(1, B), 400)))
cases.append((997, random.sample(range(1, 997), 499)))
cases.append((B, [1, B - 1]))
# clustered cuts: cutting at the middle of the piece is far from optimal
for _ in range(5):
    centers = random.sample(range(1, 10**9), random.randint(2, 6)); c = set()
    while len(c) < random.randint(150, 500):
        x = random.choice(centers) + random.randint(-10**6, 10**6)
        if 0 < x < 10**9: c.add(x)
    cases.append((10**9, sorted(c)))
for m in (100, 200, 350, 420, 480, 150, 260):                                   # large answers
    cases.append((10**9, random.sample(range(1, 10**9), m)))
for i, (L, c) in enumerate(cases, 1):
    assert 2 <= L <= B and len(c) <= 500 and len(set(c)) == len(c) and all(0 < x < L for x in c)
    random.shuffle(c)
    open(f"tests/{i:02d}.in", "w").write(f"{L} {len(c)}\n" + " ".join(map(str, c)) + "\n")
print(len(cases), "tests")
