# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(930503)
MAXN, MAXA, MAXB = 5000, 10 ** 9, 10 ** 6
tests = []


def add(d):
    n = len(d)
    assert 1 <= n <= MAXN
    assert all(0 <= a <= MAXA and 0 <= b <= MAXB for a, b in d)
    tests.append(f"{n}\n" + "".join(f"{a} {b}\n" for a, b in d))


def ri(lo, hi):
    return random.randint(lo, hi)


def uniform(n, alo=0, ahi=MAXA, blo=0, bhi=MAXB):
    return [(ri(alo, ahi), ri(blo, bhi)) for _ in range(n)]


def anti(n):
    """dishes with a large a also cool down fast (a and b grow together, with noise)"""
    d = []
    for _ in range(n):
        t = random.random()
        a = int(t * MAXA * random.uniform(0.6, 1.0))
        b = int(t * MAXB * random.uniform(0.2, 1.0))
        d.append((min(MAXA, a), min(MAXB, b)))
    return d


def ratio_ties(n):
    """a = q * b for a few rates q (many equal ratios a / b), plus noise dishes"""
    qs = [ri(50, 3000) for _ in range(6)]
    d = []
    for _ in range(n):
        if random.random() < 0.8:
            b = ri(1, MAXB // 3)
            q = random.choice(qs)
            d.append((min(MAXA, q * b), b))
        else:
            d.append((ri(0, MAXA), ri(0, MAXB)))
    return d


def levels(n, bs):
    """few distinct b values, random a"""
    return [(ri(0, MAXA), random.choice(bs)) for _ in range(n)]


def traps(n):
    """pairs: a fast-cooling dish with a small positive first gain and a slow dish with a large a"""
    d = []
    for _ in range(n // 2):
        b = ri(MAXB // 2, MAXB)
        d.append((b * ri(1, 4) + ri(0, b), b))
        b2 = ri(0, MAXB // 20)
        d.append((ri(MAXA // 2, MAXA), b2))
    while len(d) < n:
        d.append((ri(0, MAXA), ri(0, MAXB)))
    random.shuffle(d)
    return d


def mixed_scale(n):
    """dishes of very different sizes: some big a/big b, some small a/tiny b"""
    d = []
    for _ in range(n):
        r = random.random()
        if r < 0.3:
            d.append((ri(MAXA // 2, MAXA), ri(MAXB // 2, MAXB)))
        elif r < 0.6:
            d.append((ri(0, MAXA // 1000), ri(0, MAXB // 10000)))
        else:
            d.append((ri(0, MAXA // 10), ri(0, MAXB // 50)))
    return d


# samples
add([(10, 3), (8, 1), (9, 4), (1, 5)])
add([(2, 5), (3, 3), (0, 1)])
add([(20, 6), (9, 1), (14, 4), (3, 3), (15, 5), (6, 0)])
add([(7, 2)])
add([(12, 4), (7, 1), (9, 3), (5, 2), (11, 4), (30, 10), (4, 1), (8, 3)])
# hidden: small (the subset DP of brute.cpp checks these)
add([(0, 0)])
add([(5, 6)])
add(uniform(8, 0, 100, 0, 30))
add(uniform(12, 0, 1000, 0, 200))
add([(ri(0, 50), ri(0, 10)) for _ in range(15)])
add(levels(16, [3, 3, 7, 0]))
add(uniform(18, 0, MAXA, 0, MAXB))
add(traps(20))
# hidden: medium (the assignment method of brute.cpp checks these)
add(uniform(300))
add(anti(400))
add(ratio_ties(500))
# hidden: big, N = 5000
add(uniform(MAXN))
add(uniform(MAXN))
add(uniform(MAXN, MAXA // 2, MAXA))
add(uniform(MAXN, 0, MAXA, 0, MAXB // 10))
add(uniform(MAXN, 0, MAXA // 10, 0, MAXB // 100))
add(anti(MAXN))
add(anti(MAXN))
add(ratio_ties(MAXN))
add(levels(MAXN, [MAXB, MAXB // 2, MAXB // 5, MAXB // 20, 1000, 0]))
add(levels(MAXN, [ri(0, MAXB) for _ in range(40)]))
add(traps(MAXN))
add(traps(MAXN))
add(mixed_scale(MAXN))
add(mixed_scale(MAXN))
add(uniform(MAXN // 2) + [(ri(0, MAXA), 0) for _ in range(MAXN // 2)])
add([(ri(MAXA - MAXA // 10, MAXA), MAXB) for _ in range(MAXN)])        # equal b, all near the maximum
add([(MAXA, MAXB)] * MAXN)                                              # everything equal
add([(MAXA, 0)] * MAXN)                                                 # nothing cools down
add([(ri(0, 999), ri(1000, MAXB)) for _ in range(MAXN)])                # every dish loses
add([(ri(0, MAXA), ri(MAXB - 100, MAXB)) for _ in range(MAXN)])         # b nearly equal

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
