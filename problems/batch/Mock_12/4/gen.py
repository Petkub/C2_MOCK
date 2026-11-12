# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1204180)
rnd = random.random
MAXN, MAXK, MAXS = 250000, 250000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(k, s):
    n = len(s)
    assert 1 <= n <= MAXN and 2 <= k <= MAXK
    assert all(1 <= x <= MAXS for x in s)
    tests.append(f"{n} {k}\n" + " ".join(map(str, s)) + "\n")


def uni(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def logu(n, hi_exp):
    """lengths spread over many orders of magnitude"""
    return [min(MAXS, max(1, int(10 ** (rnd() * hi_exp)))) for _ in range(n)]


def small_big(n, frac):
    """mostly short files and a fraction of very long ones"""
    return [ri(MAXS // 2, MAXS) if rnd() < frac else ri(1, 1000) for _ in range(n)]


def need_pad(n, k):
    return n > 1 and (n - 1) % (k - 1) != 0


# samples
add(3, [4, 1, 3, 2, 5])
add(4, [7, 2, 5])
add(2, [6, 6, 2, 9, 3, 1])
add(3, [10, 3, 8, 1, 6, 2])
add(5, [12, 3, 7, 3, 20, 1, 9, 15, 4])
# hidden: small (brute checks these)
add(2, [ri(1, MAXS)])                                   # one file: nothing to merge
add(3, [5, 5])
add(9, uni(9, 1, 100))                                  # K >= N
for n, k in ((7, 3), (9, 4), (8, 5), (9, 6), (9, 2)):
    add(k, uni(n, 1, 50) if rnd() < 0.5 else logu(n, 4))
add(3, [MAXS] * 9)
# hidden: big
N = MAXN
for k in (3, 4, 5, 7, 64, 1000, 31623):
    n = N - ri(0, 5)
    while not need_pad(n, k):
        n -= 1
    add(k, uni(n, 1, MAXS) if k < 7 or k % 2 else logu(n, 9))
add(2, small_big(N, 0.5))                              # plain pairs
add(2, logu(N, 9))
add(2, logu(N, 7))
add(2, uni(N, MAXS // 2, MAXS))                         # pairs, all within a factor 2: every new file is the longest
add(6, small_big(N, 0.3))
add(2, [1] * N)                                         # all equal (pairs)
add(5, sorted(uni(N, 1, 10 ** 6)))
add(8, sorted(uni(N, 1, MAXS), reverse=True))
add(MAXK, uni(N, 1, 10 ** 6))                           # K = N: one merge
add(N - 1, uni(N, 1, 10 ** 6))
add(N // 2 + 3, logu(N, 9))
add(3, uni(N - 1, MAXS, MAXS))                          # no padding needed, largest answer
add(11, logu(N - 7, 6))
add(MAXK, [ri(1, 10)])                                  # one file, large K

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
