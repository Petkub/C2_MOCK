# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# "blocks" tests: the necklace is made of runs of nearly equal pearls whose lengths are in [L, R]; the run that
# holds pearl 1 is cut so that the best cutting starts its line at pearl p + 1 (p chosen per test, often p >= L).
import os, random

random.seed(110526)
rnd = random.random
MAXN, MAXA = 50000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(L, R, a):
    n = len(a)
    assert 2 <= n <= MAXN and 2 <= L <= R <= 10
    assert all(1 <= x <= MAXA for x in a)
    tests.append(f"{n} {L} {R}\n" + " ".join(map(str, a)) + "\n")


def rand_vals(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def blocks(n, L, R, p, spread, noise, lens=None):
    """runs of lengths in [L, R] (or from lens) with values far apart, rotated so that a run starts at pearl p + 1"""
    a = []
    while len(a) < n:
        left = n - len(a)
        if lens:
            k = lens[len(a) % len(lens)] if left >= lens[0] else left
        else:
            k = ri(L, R)
        if left - k < L and left - k != 0:
            k = left if left <= R else left - L     # finish with runs that still fit in [L, R]
        base = ri(noise + 1, spread - noise)
        a += [base + ri(-noise, noise) for _ in range(k)]
    a = a[:n]
    return a[n - p:] + a[:n - p]


def climb(n, step):
    """slowly rising sizes around the necklace: the only big jump is between pearl n and pearl 1"""
    a, x = [], 1
    for _ in range(n):
        x += ri(0, step)
        a.append(x)
    return a


N = MAXN
# samples
add(2, 3, [3, 7, 8, 2, 2, 5, 6, 4])
add(3, 4, [6, 4, 3, 3, 7, 2, 3])
add(2, 4, [12, 4, 9, 10, 3, 3, 15, 11, 6, 13])
add(3, 3, [4, 8, 1, 7, 7, 2, 5])
add(3, 5, [20, 18, 3, 6, 14, 2, 9, 11, 16, 1, 5, 19])
# hidden: small (brute checks these)
add(2, 2, [5, 9])
add(2, 10, [3, 3, 8])
add(4, 5, rand_vals(11, 1, 50))                         # 11 pearls cannot be cut into pieces of 4 or 5
add(2, 3, blocks(15, 2, 3, 2, 1000, 3))
add(3, 6, blocks(16, 3, 6, 5, 1000, 0))
add(2, 10, rand_vals(17, 1, MAXA))
add(4, 4, blocks(16, 4, 4, 3, 100, 1))
add(3, 5, rand_vals(18, 1, 9))
# hidden: medium
add(2, 7, blocks(3000, 2, 7, 6, MAXA, 1000))
add(5, 5, rand_vals(4999, 1, MAXA))                     # 4999 is not a multiple of 5
# hidden: big (N = 50000 or close)
add(2, 10, rand_vals(N, 1, MAXA))
add(3, 10, rand_vals(N, 1, MAXA))
add(2, 3, rand_vals(N, 1, 1000))
add(6, 9, rand_vals(N, 1, MAXA))
add(2, 10, blocks(N, 2, 10, 9, MAXA, 10 ** 6))
add(3, 9, blocks(N, 3, 9, 7, MAXA, 0))
add(5, 8, blocks(N, 5, 8, 7, MAXA, 10 ** 7, lens=[8]))       # only a cut before pearl 8 is good
add(6, 10, blocks(N, 6, 10, 9, MAXA, 5 * 10 ** 6, lens=[10]))  # only a cut before pearl 10 is good
add(2, 6, blocks(N, 2, 6, 5, 10 ** 6, 2000))
add(10, 10, blocks(N, 10, 10, 9, MAXA, 10 ** 5))
add(7, 7, blocks(N - 3, 7, 7, 3, MAXA, 10))            # 49997 = 7 * 7142 + 3: impossible
add(2, 2, [1 if i % 2 == 0 else MAXA for i in range(N)])
add(2, 4, [ri(1, 3) if i % 2 == 0 else MAXA - ri(0, 2) for i in range(N)])
add(3, 7, climb(N, 10000))
add(2, 9, [MAXA] * N)
add(4, 10, [ri(1, 3) * 3 * 10 ** 8 + ri(0, 10) for _ in range(N)])
add(8, 9, blocks(N - 1, 8, 9, 8, MAXA, 10 ** 8))
add(3, 4, blocks(N, 3, 4, 3, 10 ** 4, 0, lens=[4, 3]))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
