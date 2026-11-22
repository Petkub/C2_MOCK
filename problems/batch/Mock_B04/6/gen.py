# Writes tests/NN.in for this problem. Samples first (01..06), then hidden tests.
# Answer = min over the spelled monster k of best(prefix before k) + best(suffix after k), where best() is the
# capped left-to-right greedy. The big tests make the cap matter (big / small alternations, small HP next to big HP),
# put the best k away from the largest HP, add dead monsters (HP 0) as walls and push the answer above 2^31.
import os, random

random.seed(2602)
rnd = random.random
MAXN, MAXH = 200000, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(h):
    n = len(h)
    assert 1 <= n <= MAXN and all(0 <= x <= MAXH for x in h)
    tests.append(f"{n}\n" + " ".join(map(str, h)) + "\n")


def rand_h(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def alternate(n, big, small):
    """big / small HP in turn: aiming at the small monsters hits two big ones, but only a few times"""
    return [ri(*big) if i % 2 == 0 else ri(*small) for i in range(n)]


def with_zeros(h, p):
    return [0 if rnd() < p else x for x in h]


def blocks(n, maker):
    """runs of random length, each made by maker(len), joined"""
    h = []
    while len(h) < n:
        h += maker(min(n - len(h), ri(1, 60)))
    return h


# samples
add([1, 1, 4, 1, 5])
add([6, 1, 9, 2, 0])
add([9, 2, 2, 4, 3, 2, 9, 8])
add([7, 0, 9, 0, 0, 5, 4])
add([1000000000])
add([5, 1, 5, 1, 5])          # the target must be alive: 9 (a covering model that ignores it says 6)
# hidden: tiny (the brute force plays the game itself on these)
add([0])
add([3, 3])
add([2, 1, 2, 1, 2])
add([4, 1, 3, 1, 4, 2])
add([1, 3, 1, 1, 3, 1, 2])
add([2, 0, 3, 1, 0, 2, 1, 1])
add([1, 2, 1, 2, 1, 2, 1, 2])
# hidden: medium
add(rand_h(50000, 0, MAXH))
add(alternate(50000, (10 ** 8, MAXH), (0, 5)))
# hidden: big (N = 200000)
add(rand_h(N, 0, MAXH))
add(rand_h(N, 1, 10))
add(rand_h(N, 0, 2))
add([MAXH] * N)
add([1] * N)
add(alternate(N, (9 * 10 ** 8, MAXH), (0, 3)))
add(alternate(N, (1, 20), (0, 2)))
add(alternate(N, (MAXH, MAXH), (1, 1)))
add(with_zeros(rand_h(N, 1, MAXH), 0.1))
add(blocks(N, lambda m: alternate(m, (ri(1, MAXH), MAXH), (0, ri(0, 1000)))))
add(blocks(N, lambda m: rand_h(m, 0, 50) if rnd() < 0.5 else rand_h(m, 10 ** 8, MAXH)))
add(sorted(rand_h(N, 0, MAXH)))
add(sorted(rand_h(N, 0, MAXH), reverse=True))
add([ri(0, 3) if i % 3 == 1 else ri(5 * 10 ** 8, MAXH) for i in range(N)])
add([abs(i - N // 3) * 7000 + ri(0, 1000) for i in range(N)])
h = alternate(N, (8 * 10 ** 8, MAXH), (0, 2))
h[0] = MAXH                                                            # largest HP at the left end
add(h)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
