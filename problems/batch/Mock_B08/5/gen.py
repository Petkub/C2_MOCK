# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The water that starts in bucket i holds max(0, min(b_i..b_q) - K q) liters when it is in bucket q,
# where b_j = a_j + K j. The big tests make the water live long (so simulating minute by minute is slow),
# make long decreasing runs of b (so walking each source's chain is slow), make many equal b values
# (windows with several minima), and make K * N far above 2^31.
import os, random

random.seed(20240202)
rnd = random.random
MAXN, MAXK, MAXA = 200000, 10 ** 9, 10 ** 9
N = MAXN
tests = []


def ri(lo, hi):
    return lo + int(rnd() * (hi - lo + 1))


def add(k, a):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= k <= MAXK
    assert all(isinstance(x, int) and 1 <= x <= MAXA for x in a)
    tests.append(f"{n} {k}\n" + " ".join(map(str, a)) + "\n")


def clip(a):
    return [min(MAXA, max(1, x)) for x in a]


def rand_a(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def flat_b(n, k, c, noise=0):
    """b_j = a_j + k j close to the constant c (equal minima everywhere when noise = 0)"""
    return clip([c - k * j + (ri(0, noise) if noise else 0) for j in range(1, n + 1)])


def falling_b(n, k, top, step):
    """b strictly decreasing: a_j falls faster than k per bucket (long chains of smaller values)"""
    return clip([top - (step + k) * j + ri(0, step - 1) for j in range(1, n + 1)])


# samples
add(1, [6, 9, 3, 8, 5, 7])
add(3, [10, 10, 10, 10])
add(2, [5, 8, 8, 3, 9, 9, 2])
add(1, [1000000000] * 5)
add(4, [3])
# hidden: small and medium (brute checks these)
add(1, [1, 1])
add(2, rand_a(10, 1, 12))
add(1, rand_a(30, 1, 40))
add(3, flat_b(40, 3, 200))                                            # every b equal
add(5, flat_b(300, 5, 3000, 4))                                       # many equal b
add(7, rand_a(2000, 1, 20000))
add(1, falling_b(2000, 1, 10 ** 6, 300))
add(ri(1, 50), rand_a(1500, 1, 30000))
# hidden: big (N = 200000)
add(12000, rand_a(N, 9 * 10 ** 8, MAXA))                              # water lives long, K * N above 2^31
add(1, falling_b(N, 1, MAXA, 4000))                                   # b falls everywhere: chains of length N
add(2, falling_b(N, 2, MAXA, 1500) )
add(1000, flat_b(N, 1000, MAXA))                                      # all b equal
add(4000, flat_b(N, 4000, MAXA, 3000))                                # b nearly equal, many ties
add(11000, rand_a(N, 95 * 10 ** 7, MAXA))                            # K * N far above 2^31
add(ri(11000, 13000), [MAXA] * N)
add(MAXK, rand_a(1000, 1, MAXA))                                      # all water gone after one minute
add(11000, rand_a(N, 7 * 10 ** 8, MAXA))
add(1, rand_a(N, 100000, 400000))                                     # water dies part way along
add(20000, [ri(1, 600000) if j < N // 2 and rnd() < 0.002 else ri(5 * 10 ** 8, MAXA) for j in range(N)])
saw = []
while len(saw) < N:                                                   # sawtooth: falling runs of b
    run = ri(1, 3000)
    top = ri(6 * 10 ** 8, MAXA)
    saw += [top - 7 * j for j in range(run)]
add(5, clip(saw[:N]))
add(15000, sorted(rand_a(N, 1, MAXA)))                                # a increasing
add(1, sorted(rand_a(N, 1, MAXA), reverse=True))                      # a decreasing
blk = []
while len(blk) < N:                                                   # blocks of equal b, deep dips in the first half
    c = ri(5 * 10 ** 8, MAXA)
    j0 = len(blk) + 1
    blk += [c - 50 * (j0 + j) for j in range(ri(1, 500))]
    if len(blk) < N // 2:
        blk.append(ri(1, 10 ** 6))
add(50, clip(blk[:N]))
add(200, falling_b(N, 200, 9 * 10 ** 8, 1000)[::-1])                  # b rising then the last ones high
add(ri(2, 9), [ri(5 * 10 ** 8, MAXA) if j % 1000 or j > N // 2 else 1 for j in range(N)])  # walls of 1 in the first half
add(30000, [MAXA - 30000 * (j % 30000) for j in range(N)])            # equal b inside each period

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
