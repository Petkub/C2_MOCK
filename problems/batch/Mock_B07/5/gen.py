# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Big tests (N = 5000) mix: wide random sizes, many equal sizes (student and tent of the same size), every student
# able to get a tent (the arrangement with all students inside competes with arrangements that leave some outside),
# chains where each student is just above or just below a tent, all sizes equal (N! ways), and nobody fits (0 pairs).
# Every big test has DP values that overflow a 32-bit product.
import os, random

random.seed(20201213)
rnd = random.random
MAXN, MAXV = 5000, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffled(xs):
    keys = [rnd() for _ in xs]
    return [xs[i] for i in sorted(range(len(xs)), key=lambda i: keys[i])]


def add(h, l, mix=True):
    n = len(h)
    assert 1 <= n <= MAXN and len(l) == n
    assert 1 <= min(h) and max(h) <= MAXV and 1 <= min(l) and max(l) <= MAXV
    if mix:
        h, l = shuffled(h), shuffled(l)
    tests.append(f"{n}\n" + " ".join(map(str, h)) + "\n" + " ".join(map(str, l)) + "\n")


def rand_vals(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


# samples (fixed order, no shuffle)
add([5, 4, 5, 6], [2, 3, 3, 5], False)
add([3, 6, 3, 5], [3, 2, 6, 6], False)
add([3, 5, 7, 4, 6, 8], [3, 9, 5, 2, 3, 9], False)
add([5, 6, 7], [2, 3, 4], False)
add([4, 4, 4, 4], [4, 4, 4, 4], False)

# small tests for brute.cpp
for n, v in ((1, 2), (2, 3), (6, 4), (7, 10), (8, 6), (8, 1000), (7, 3)):
    add(rand_vals(n, 1, v), rand_vals(n, 1, v))
h = rand_vals(8, 1, 20)
add(h, [x + ri(0, 3) for x in h])                                 # every student can get a tent

# mid sizes
add(rand_vals(300, 1, 50), rand_vals(300, 1, 50))
h = rand_vals(1000, 1, 10 ** 6)
add(h, [x + ri(0, 10 ** 4) for x in h])

# max size
add(rand_vals(N, 1, MAXV), rand_vals(N, 1, MAXV))                 # wide random
add(rand_vals(N, 1, 10), rand_vals(N, 1, 10))                     # many equal sizes
add(rand_vals(N, 1, 100), rand_vals(N, 1, 100))
add(rand_vals(N, 1, N), rand_vals(N, 1, N))
h = rand_vals(N, 1, MAXV - 10 ** 6)
add(h, [x + ri(0, 10 ** 6) for x in h])                           # every student can get a tent
h = rand_vals(N, 1, 1000)
add(h, [x + ri(0, 5) for x in h])
h = rand_vals(N, 1, 30)
add(h, [x + ri(0, 1) for x in h])
add([2 * i for i in range(1, N + 1)], [2 * i + 1 for i in range(1, N + 1)])   # each tent just above a student
add([2 * i + 1 for i in range(1, N + 1)], [2 * i for i in range(1, N + 1)])   # each tent just below a student
add([2 * i for i in range(1, N + 1)], [2 * i for i in range(1, N + 1)])       # equal pairs
add([7] * N, [7] * N)                                             # all equal: N! ways
add(rand_vals(N, 1, 10 ** 6), rand_vals(N, 10 ** 6, MAXV))        # every student fits every tent
add(rand_vals(N, 5 * 10 ** 8 + 1, MAXV), rand_vals(N, 1, 5 * 10 ** 8))   # nobody fits
add(rand_vals(N // 2, 1, 1000) + rand_vals(N // 2, MAXV - 1000, MAXV),
    rand_vals(N // 2, 1, 1000) + rand_vals(N // 2, MAXV - 1000, MAXV))
add(rand_vals(N, 1, MAXV // 2), rand_vals(N, MAXV // 4, MAXV))    # tents mostly larger
add(rand_vals(N, MAXV // 4, MAXV), rand_vals(N, 1, MAXV // 2))    # tents mostly smaller
add(rand_vals(N, MAXV - 3000, MAXV), rand_vals(N, MAXV - 3000, MAXV))
h = rand_vals(N, 1, 2000)
add(h[:N - 50] + rand_vals(50, 2001, 3000), [x + ri(0, 2) for x in h[:N - 50]] + rand_vals(50, 1, 2000))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
print(len(tests))
