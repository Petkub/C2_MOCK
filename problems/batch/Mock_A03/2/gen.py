# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(70302)
rnd = random.random
MAXN, MAXK, MAXA = 200000, 10 ** 8, 10 ** 5
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(m, k, a):
    n = len(a)
    assert 1 <= n <= MAXN
    assert 0 <= m <= n
    assert 0 <= k <= MAXK
    assert all(1 <= v <= MAXA for v in a)
    tests.append(f"{n} {m} {k}\n{' '.join(map(str, a))}\n")


def uni(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def shuffled(a):
    random.shuffle(a)
    return a


# samples
add(2, 5, [3, 7, 4, 9])
add(3, 4, [2, 5, 3])
add(0, 100, [5, 2, 8])
add(1, 100000000, [100000])
add(4, 12, [10, 3, 25, 6, 4, 40, 7])

# hidden: small (brute.cpp checks these)
add(1, 0, [1])
add(5, 0, [4, 8, 3, 9, 6])                              # no batteries
add(3, 30, [7, 7, 7, 7, 7])                             # equal times, too few seats
add(6, 40, uni(6, 1, 10))
add(3, 25, [2, 50, 1, 60, 3, 45, 70, 4])                # the seats run out first
add(8, 150, uni(8, 1, 100000))
add(12, 120, uni(20, 1, 60))
add(25, 100, uni(40, 1, 30))

# hidden: medium
add(1000, MAXK, uni(1000, 90000, MAXA))                  # answers far above 2^31
add(0, MAXK, uni(5000, 1, MAXA))                         # nobody may be sent
add(3000, 0, uni(5000, 1, MAXA))                         # no batteries at all

# hidden: big (n = 200 000)
N = MAXN
add(N, MAXK, uni(N, 1, MAXA))                            # random, every drone may be sent
add(N, MAXK, [MAXA] * N)                                 # all equal, largest times
add(N, MAXK, [1] * N)                                    # all equal, smallest times
add(N, MAXK - 1, uni(N, 1, 100))
add(N, MAXK, sorted(uni(N, 1000, MAXA)))
add(N, MAXK, sorted(uni(N, 1, MAXA), reverse=True))
add(N, MAXK, uni(N, 99990, MAXA))                        # many ties
add(N, MAXK, shuffled([2 ** ri(0, 16) for _ in range(N)]))   # the answer is a multiple of many times
add(N, MAXK, shuffled([1] * (N // 2) + [MAXA] * (N // 2)))
add(N, 23456789, uni(N, 1, MAXA))
# the seats run out: the weakest drones are very weak, the rest are strong
add(1000, MAXK, shuffled(uni(1000, 1, 3) + uni(N - 1000, 60000, MAXA)))
add(150000, MAXK, shuffled(uni(150000, 200, 300) + uni(N - 150000, 90000, MAXA)))
add(1000, 99999000, shuffled([1] * 1000 + [MAXA] * (N - 1000)))    # exactly enough to reach the cap
add(1000, 99998999, shuffled([1] * 1000 + [MAXA] * (N - 1000)))    # one battery short
add(N - 1, MAXK, shuffled([1] * (N - 1) + [MAXA]))
add(100000, MAXK, shuffled(uni(50000, 1, 5) + uni(N - 50000, 1, MAXA)))
add(40000, MAXK, shuffled(uni(30000, 1, 20) + uni(N - 30000, 5000, MAXA)))
add(120000, 90000000, shuffled(uni(100000, 1, 10) + uni(N - 100000, 2000, MAXA)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
