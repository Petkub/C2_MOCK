import random, os
random.seed(2611)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append([(1, 5), (3, 8), (4, 6)])
cases.append([(0, 10), (0, 10)])
cases.append([(1, 2), (2, 3), (5, 9)])
cases.append([(0, 1000000000)])
cases.append([(2, 7), (1, 9), (3, 4), (3, 4)])
for _ in range(6):
    n = random.randint(1, 8); I = []
    for _ in range(n):
        l = random.randint(0, 30); I.append((l, l + random.randint(1, 15)))
    cases.append(I)
N, B = 50000, 10**9
def rnd(n, span, lmax):
    I = []
    for _ in range(n):
        l = random.randint(0, span - 1); I.append((l, min(span, l + random.randint(1, lmax))))
    return I
cases.append(rnd(3000, 5000, 100))
cases.append(rnd(N, B, B))
cases.append(rnd(N, B, 10**4))
cases.append(rnd(N, 1000, 1000))                       # heavy overlap on small coordinates
cases.append([(0, B)] * N)                             # everything at depth N
cases.append([(i, B - i) for i in range(N)])           # nested
cases.append([(i * 5000, i * 5000 + 5000) for i in range(N)])   # touching, never overlapping
cases.append([tuple(x * 10**8 for x in sorted(random.sample(range(11), 2))) for _ in range(N)])   # many equal endpoints
cases.append(rnd(N, 10**6, 10))
cases.append([(i, i + 1) for i in range(N // 2)] + [(i, i + 2) for i in range(N // 2)])
for span, lmax in ((10**9, 10**9), (10**5, 50), (10**9, 10**6), (5000, 5000)):
    cases.append(rnd(random.randint(30000, 50000), span, lmax))
cases.append(rnd(100000, B, B))
cases.append(rnd(100000, 10**6, 100))
for idx in range(11, len(cases)):
    mx = max(r for _, r in cases[idx])
    if mx <= 10**6 and idx % 2 == 0:
        f = 10**9 // mx
        cases[idx] = [(l * f, r * f) for l, r in cases[idx]]
for i, I in enumerate(cases, 1):
    assert 1 <= len(I) <= 100000 and all(0 <= l < r <= B for l, r in I)
    random.shuffle(I) if i > 5 else None
    open(f"tests/{i:02d}.in", "w").write(f"{len(I)}\n" + "".join(f"{l} {r}\n" for l, r in I))
print(len(cases), "tests")
