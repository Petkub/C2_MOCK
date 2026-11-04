# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

MAXN, MAXT = 100000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(rows):
    n = len(rows)
    assert 1 <= n <= MAXN
    for d, s, e in rows:
        assert 1 <= d <= n and 0 <= s < e <= MAXT
    tests.append(f"{n}\n" + "".join(f"{d} {s} {e}\n" for d, s, e in rows))


def iv(lo, hi):
    """a random interval inside [lo, hi]"""
    a, b = ri(lo, hi), ri(lo, hi)
    if a == b:
        return (a, a + 1) if a < hi else (a - 1, a)
    return (min(a, b), max(a, b))


def rand_rows(n, k, lo=0, hi=MAXT):
    """n people, departments 1..k, intervals inside [lo, hi]"""
    out = []
    for _ in range(n):
        s, e = iv(lo, hi)
        out.append((ri(1, k), s, e))
    return out


def shuffled(rows):
    random.shuffle(rows)
    return rows


random.seed(150201)
# samples
add([(1, 1, 4), (1, 3, 8), (2, 2, 6), (3, 5, 9)])
add([(1, 0, 10), (2, 0, 4), (3, 6, 10)])
add([(2, 0, 7), (2, 3, 9)])
add([(1, 0, 3), (2, 3, 6), (3, 6, 9), (1, 1, 2), (2, 1, 8)])
add([(4, 10, 20), (1, 15, 25), (2, 12, 18), (4, 11, 30), (3, 19, 21), (1, 5, 40)])
# hidden: small (brute checks these)
add([(1, 5, 6)])
for seed, n, k, hi in [(1, 8, 3, 20), (2, 30, 4, 50), (3, 100, 10, 200), (4, 300, 5, 1000),
                       (5, 300, 300, MAXT), (6, 300, 2, 30)]:
    random.seed(150210 + seed)
    add(rand_rows(n, k, 0, hi))
random.seed(150220)
add([(1 + i % 3, 2 * i, 2 * i + 2) for i in range(200)])                 # only touching intervals
random.seed(150221)
add(shuffled([(1 + (i % 2), i, 1000 - i) for i in range(300)]))          # nested
# hidden: big, each with its own seed
M = MAXN


def overlap_mid(n, k):
    """every interval contains the middle time"""
    return [(ri(1, k), ri(0, MAXT // 2 - 1), ri(MAXT // 2 + 1, MAXT)) for _ in range(n)]


def chains(n, k, step):
    """people of different departments handing over at the same moments"""
    out = []
    for i in range(n):
        s = (i // k) * step
        out.append((1 + i % k, s, s + step))
    return out


def handover(n, k, lo, hi, side):
    """a crowd present around time T = (lo + hi) / 2; `side` people leave at T and as many from the same
    departments arrive at T, so the largest P(t) holds just before T and again from T on"""
    t = (lo + hi) // 2
    out = []
    for _ in range(side):
        d = ri(1, k)
        out.append((d, ri(lo, t - 1), t))
        out.append((d, t, ri(t + 1, hi)))
    for _ in range(n - 2 * side):
        out.append((ri(1, k), ri(lo, (lo + t) // 2), ri((t + hi) // 2, hi)))
    return shuffled(out)


def twice(rows, shift):
    """the same day pattern repeated later, so the maximum is reached again"""
    return rows + [(d, s + shift, e + shift) for d, s, e in rows]


BIG = [
    (150301, lambda: twice(rand_rows(M // 2, M // 2, 0, MAXT // 2 - 1), MAXT // 2 + 1)),
    (150302, lambda: rand_rows(M, 2)),
    (150303, lambda: twice(rand_rows(M // 2, 5, 0, 1000), 5000)),
    (150304, lambda: overlap_mid(M, M)),
    (150305, lambda: overlap_mid(M, 3)),
    (150306, lambda: [(i + 1, 0, MAXT) for i in range(M)]),                  # the largest answers
    (150307, lambda: [(1 + i % 2, 0, MAXT) for i in range(M)]),
    (150308, lambda: [(1, 0, MAXT)] * (M - 3) + [(2, 0, 1), (3, MAXT - 1, MAXT), (2, 7, 9)]),
    (150309, lambda: shuffled([(ri(1, M), i, MAXT - i) for i in range(M)])),  # nested
    (150310, lambda: shuffled(chains(M, 7, 3))),
    (150311, lambda: shuffled(chains(M, 1000, 10 ** 4))),
    (150312, lambda: twice(rand_rows(M // 2, 50, 0, 200), 200)),
    (150313, lambda: rand_rows(M, M, 0, 10)),
    (150314, lambda: [(ri(1, M), 3 * i, 3 * i + ri(1, 3)) for i in range(M)]),   # nearly disjoint
    (150315, lambda: [(1, 2 * i + 1, 2 * i + 2) for i in range(M)]),         # nobody meets anybody
    (150316, lambda: rand_rows(M // 2, 2) + rand_rows(M // 2, M, MAXT // 3, MAXT // 3 * 2)),
    (150317, lambda: shuffled([(1 + i % 4, ri(0, 10 ** 6), MAXT - ri(0, 10 ** 6)) for i in range(M)])),
    (150318, lambda: [(1 + (i * 7919) % 10, ri(0, 1000) * 1000, ri(1001, 2000) * 1000) for i in range(M)]),
    (150319, lambda: handover(M, M, 0, MAXT, 5000)),
    (150320, lambda: handover(M, 2, 10 ** 6, 2 * 10 ** 6, 20000)),
    (150321, lambda: twice(handover(M // 2, 10, 0, MAXT // 2 - 1, 1500), MAXT // 2 + 1)),
    (150322, lambda: handover(M, 3, 0, 1000, 2000)),
]
for seed, make in BIG:
    random.seed(seed)
    add(make())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
