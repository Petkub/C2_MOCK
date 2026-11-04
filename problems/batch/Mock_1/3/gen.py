# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1205001)
MAXRC, MAXK, MAXD = 2000, 100000, 4000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(R, C, T, sp):
    K = len(sp)
    assert 1 <= R <= MAXRC and 1 <= C <= MAXRC and 1 <= K <= MAXK and 1 <= T <= K
    for r, c, d in sp:
        assert 1 <= r <= R and 1 <= c <= C and 0 <= d <= MAXD
    tests.append("\n".join([f"{R} {C} {K} {T}"] + [f"{r} {c} {d}" for r, c, d in sp]) + "\n")


def area(R, C, r, c, d):
    """number of field cells within distance d of (r, c)"""
    s = 0
    for x in range(max(1, r - d), min(R, r + d) + 1):
        w = d - abs(x - r)
        s += min(C, c + w) - max(1, c - w) + 1
    return s


def pick_t(R, C, sp, f):
    """T near f times the average number of sprinklers on a cell (estimated from a sample)"""
    smp = [sp[ri(0, len(sp) - 1)] for _ in range(min(len(sp), 60))]
    mean = sum(area(R, C, *s) for s in smp) / len(smp) * len(sp) / (R * C)
    return max(1, min(len(sp), int(mean * f) + 1))


def rand_sp(R, C, K, dmin, dmax):
    return [(ri(1, R), ri(1, C), ri(dmin, dmax)) for _ in range(K)]


# samples
add(5, 6, 2, [(2, 2, 1), (3, 4, 2), (5, 6, 0)])
add(3, 3, 1, [(1, 1, 0), (3, 3, 1)])
add(4, 4, 3, [(2, 2, 3), (3, 3, 1), (1, 4, 2), (4, 1, 1)])
add(1, 7, 2, [(1, 4, 2), (1, 1, 10), (1, 7, 1)])
add(6, 5, 4, [(3, 3, 2), (3, 3, 2), (4, 2, 1), (1, 5, 6), (6, 1, 0)])

# hidden: small (brute checks these)
for R, C, K, dmax, f in [(1, 1, 3, 2, 1.0), (8, 8, 10, 4, 1.0), (30, 20, 60, 10, 1.0), (50, 70, 200, 30, 0.7),
                         (1, 200, 100, 50, 1.2), (200, 1, 100, 60, 0.9), (100, 100, 300, 120, 1.0),
                         (150, 120, 150, 300, 0.5)]:
    sp = rand_sp(R, C, K, 0, dmax)
    add(R, C, pick_t(R, C, sp, f), sp)
add(40, 40, 2, [(ri(1, 40), ri(1, 40), 0) for _ in range(50)] * 2)         # radius 0 only
add(60, 60, 1, [(1, 1, MAXD), (60, 60, 0)])


# hidden: big
def big(seed, make):
    random.seed(seed)
    R, C, sp, f = make()
    T = f if isinstance(f, int) else pick_t(R, C, sp, f)
    add(R, C, T, sp)


M = MAXRC
big(1206001, lambda: (M, M, rand_sp(M, M, MAXK, 800, 2000), 1.0))
big(1206002, lambda: (M, M, rand_sp(M, M, MAXK, 1000, 1500), 0.8))
big(1206003, lambda: (M, M, rand_sp(M, M, MAXK, 1500, MAXD), 0.9))
big(1206004, lambda: (M, M, rand_sp(M, M, MAXK, 0, MAXD), 1.0))
big(1206005, lambda: (M, M, rand_sp(M, M, MAXK, 900, 1100), 1.3))
big(1206006, lambda: (M, M, rand_sp(M, M, MAXK, 1200, 2000), 0.6))
big(1206007, lambda: (M, M, [(ri(1, 10), ri(1, 10), ri(1500, MAXD)) for _ in range(MAXK)], 1.0))      # near a corner
big(1206008, lambda: (M, M, [(ri(900, 1100), ri(900, 1100), ri(800, 1200)) for _ in range(MAXK)], 1.0))  # centre
big(1206009, lambda: (M, M, [(1000, 1000, 1000)] * MAXK, MAXK))                                         # one diamond K times
big(1206010, lambda: (M, M, [(ri(1, M), [1, M][ri(0, 1)], ri(1000, 3000)) for _ in range(MAXK)], 1.0))  # on the edges
big(1206011, lambda: (M, M, rand_sp(M, M, MAXK, MAXD, MAXD), MAXK))                                     # all cover everything
big(1206012, lambda: (M, M, rand_sp(M, M, MAXK, 1000, 2500), 1))
big(1206013, lambda: (M, M, rand_sp(M, M, MAXK, 0, 30), 1.0))
big(1206014, lambda: (M, 1500, rand_sp(M, 1500, MAXK, 700, 1800), 0.9))
big(1206015, lambda: (1700, M, rand_sp(1700, M, MAXK, 700, 1800), 1.2))
big(1206016, lambda: (M, M, rand_sp(M, M, MAXK, 1000, 2000), 1.15))
big(1206017, lambda: (M, M, [(ri(1, M), ri(1, M), [0, 1999][ri(0, 1)]) for _ in range(MAXK)], 1.0))
big(1206018, lambda: (M, M, rand_sp(M, M, MAXK, 1990, 2010), 0.95))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
