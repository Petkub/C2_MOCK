# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Format: "N K", then the N times, then the N colours.
import os, random

random.seed(52024)
rnd = random.random
MAXN, MAXT = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffle(x):
    for i in range(len(x) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        x[i], x[j] = x[j], x[i]


def add(t, c, k):
    n = len(t)
    assert 1 <= k <= n <= MAXN and len(c) == n
    assert all(1 <= x <= MAXT for x in t)
    assert all(1 <= x <= k for x in c)
    seen = [False] * (k + 1)
    for x in c:
        seen[x] = True
    assert all(seen[1:])
    tests.append(f"{n} {k}\n" + " ".join(map(str, t)) + "\n" + " ".join(map(str, c)) + "\n")


def colours(n, k):
    """every colour at least once, the rest random"""
    c = list(range(1, k + 1)) + [ri(1, k) for _ in range(n - k)]
    shuffle(c)
    return c


def rand_test(n, k, lo=1, hi=MAXT):
    add([ri(lo, hi) for _ in range(n)], colours(n, k), k)


def pairs_test(pairs, k):
    """pairs = list of (time, colour); shuffled before writing"""
    shuffle(pairs)
    add([p[0] for p in pairs], [p[1] for p in pairs], k)


def rare(n, k, rare_times, lo, hi):
    """colour k only at rare_times, the other colours anywhere in [lo, hi]"""
    pairs = [(x, k) for x in rare_times]
    m = n - len(pairs)
    cs = colours(m, k - 1)
    pairs += [(ri(lo, hi), cs[i]) for i in range(m)]
    pairs_test(pairs, k)


def blocks(n, k, width, gap):
    """colour c only in [base_c, base_c + width), blocks in a random order of colours"""
    order = list(range(1, k + 1))
    shuffle(order)
    cs = colours(n, k)
    base = {col: 1 + i * (width + gap) for i, col in enumerate(order)}
    pairs_test([(base[col] + ri(0, width - 1), col) for col in cs], k)


def all_at_one(n, k, v, lo, hi):
    """every colour once at time v, the rest random"""
    pairs = [(v, col) for col in range(1, k + 1)]
    cs = colours(n - k, k)
    pairs += [(ri(lo, hi), cs[i]) for i in range(n - k)]
    pairs_test(pairs, k)


N = MAXN
# samples
add([12, 30, 19, 25, 41, 28, 8], [1, 2, 3, 1, 3, 2, 2], 3)
add([15, 3, 22, 9], [2, 4, 1, 3], 4)
add([50, 47, 61, 35, 58, 44, 70, 39, 52, 66], [1, 3, 2, 2, 1, 1, 3, 3, 2, 1], 3)
add([100, 230, 180, 140, 260, 85, 205, 120], [2, 1, 2, 1, 2, 1, 1, 2], 2)
add([31, 16, 27, 8, 44, 19, 36, 23, 12, 40, 5, 29], [4, 1, 3, 2, 4, 2, 1, 4, 3, 2, 3, 1], 4)
# hidden: small and medium (brute checks these)
add([777], [1], 1)
add([5, 9, 2, 9, 7], [1, 1, 1, 1, 1], 1)
add([40, 15, 40, 22, 15, 31, 8, 40], [1, 2, 2, 1, 1, 2, 1, 1], 2)        # equal times across colours
rand_test(300, 7)
rand_test(2000, 40, 1, 5000)
rand_test(2000, 2000)
rare(1500, 3, [ri(1, 10)], 10 ** 8, 2 * 10 ** 8)
blocks(2000, 100, 10 ** 6, 3 * 10 ** 6)
rand_test(1000, 500, 1, 300)
# hidden: big (N = 100000)
rand_test(N, 2)
rand_test(N, 10)
rand_test(N, 300)
rand_test(N, 100)
rand_test(N, 30000)
rand_test(N, N)
rand_test(N, 50000)
rare(N, 30, [MAXT], 1, 10 ** 6)                                      # one athlete far away
rare(N, 1000, [1, MAXT], 4 * 10 ** 8, 6 * 10 ** 8)                   # rare colour at both ends
rand_test(N, 200, 1, 1000)                                           # many equal times
rand_test(N, 20000, 1, 100)                                          # many equal times, many colours
all_at_one(N, 20000, ri(1, 10 ** 8), 1, MAXT)                        # answer 0
blocks(N, 1000, 5 * 10 ** 5, 4 * 10 ** 5)                            # colours in separate blocks
rare(N, 2, [MAXT - ri(0, 10 ** 6)], 1, 9 * 10 ** 8)                 # colour 2 has one athlete
all_at_one(N, 20000, MAXT, MAXT - 1, MAXT)                           # times near the maximum
rand_test(N, 70000)
step = ri(3, 9)
pairs_test([(1 + i * step, i % 30000 + 1) for i in range(N)], 30000)  # colours in turn, evenly spaced
rare(N, 1000, [1, MAXT], 10 ** 8, 3 * 10 ** 8)                   # rare colour at both ends, other place
cs = colours(N - 30000, 30000)
pairs_test([(ri(MAXT - 5 * 10 ** 5, MAXT), col) for col in range(1, 30001)]
           + [(ri(1, 10 ** 6), col) for col in cs], 30000)           # every colour once near the top

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
