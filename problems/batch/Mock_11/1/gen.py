# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(710701)
MAXN, MAXQ, MAXK = 10**9, 100000, 10**18
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(N, qs):
    assert 1 <= N <= MAXN and 1 <= len(qs) <= MAXQ
    for t, x, k in qs:
        assert t in (1, 2) and 1 <= x <= 2 * N and 0 <= k <= MAXK
    lines = [f"{N} {len(qs)}"] + [f"{t} {x} {k}" for t, x, k in qs]
    tests.append("\n".join(lines) + "\n")


def rk():
    """mostly huge k, sometimes small, sometimes the extremes"""
    r = rnd()
    if r < 0.70:
        return ri(10**12, MAXK)
    if r < 0.85:
        return ri(0, 60)
    if r < 0.95:
        return ri(61, 10**9)
    return MAXK if r < 0.98 else 0


def queries(N, q, divs=()):
    """random cards / positions, the ends of both halves, and multiples of divisors of 2N + 1"""
    D = 2 * N
    special = [1, D, N, N + 1]
    qs = []
    for _ in range(q):
        r = rnd()
        if r < 0.05:
            x = special[int(rnd() * 4)]
        elif r < 0.10 and divs and divs[0] <= D:
            d = divs[int(rnd() * len(divs))]
            x = d * ri(1, max(1, D // d)) if d <= D else d % D + 1
        else:
            x = ri(1, D)
        qs.append((1 if rnd() < 0.5 else 2, x, rk()))
    return qs


# samples
add(4, [(1, 1, 2), (2, 1, 2), (1, 8, 3), (2, 5, 1)])
add(1, [(1, 1, 0), (2, 1, 3), (1, 2, 4)])
add(5, [(1, 7, 2), (2, 10, 5), (1, 4, 13), (2, 2, 100)])
add(12, [(1, 1, 1), (2, 1, 1), (1, 23, 37), (2, 9, 50)])
add(7, [(2, 14, 1), (1, 3, 4), (2, 8, 1000000000000)])
add(MAXN, [(1, 1, 1), (2, 1, 1), (1, 1999999999, 10**18), (2, 123456789, 987654321987654321)])   # maximum N and k (was sample 4)
# hidden: small (brute builds the whole permutation)
for N, q in [(2, 40), (3, 50), (10, 300), (100, 1000), (1000, 3000), (50000, 5000), (1000000, 5000),
             (2000000, 5000)]:
    add(N, queries(N, q, (3, 5, 7)))
# hidden: big; the comment is the factorisation of M = 2N + 1 and the order of 2 modulo M
BIG = [
    (1000000000, (3,)),                   # 3 * 666666667, order 24 691 358
    (999999986, ()),                      # prime, order M - 1
    (999999930, ()),                      # prime, order M - 1
    (999999926, ()),                      # prime, order M - 1
    (850056851, (37, 45949019)),          # order 827 082 324
    (704417849, (1087, 1296077)),         # order 703 769 268
    (791929389, (25373, 62423)),          # order 791 885 492
    (616355924, (19, 64879571)),          # order 583 916 130
    (574500189, (293, 3921503)),          # order 572 539 292
    (500952870, (1367, 732923)),          # order 500 585 726
    (605698631, (59, 20532157)),          # order 595 432 524
    (758098104, (11, 137836019)),         # order 689 180 090
    (692008694, (10891, 127079)),         # order 691 939 710
    (879974823, (347, 5071901)),          # order 877 438 700
    (581130733, (3, 9, 27, 3**10)),       # M = 3^19, order 2 * 3^18
    (597130409, (53, 22533223)),          # order 585 863 772
    (536870912, (5, 25, 41, 13)),         # M = 2^30 + 1, order 60
]
for i, (N, divs) in enumerate(BIG):
    random.seed(711000 + i)
    add(N, queries(N, MAXQ if i < 4 else 60000, divs))   # keeps the tests under 40 MB in total

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
