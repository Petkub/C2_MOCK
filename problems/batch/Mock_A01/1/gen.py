# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(5120241)
rnd = random.random
MAXN, MAXA = 200000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a):
    n = len(a)
    assert 1 <= n <= MAXN
    assert all(-MAXA <= x <= MAXA for x in a)
    tests.append(f"{n}\n" + " ".join(map(str, a)) + "\n")


def rand(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


N = MAXN
# samples
add([4, -2, 7, 3, -5, 6])
add([-3, 6, 2, -1, 5])
add([10, 1, 1, 10, 1, 1, 10, 1])
add([7])
add([2, 9, 4, -6, 5, 5, 1])
# hidden: small (brute tries every plan)
add([-5])
add([0])
add([0] * 9)
add(rand(12, -2, 2))
add(rand(24, -MAXA, -1))                                    # every day loses money
add(rand(40, -3, 3))
add(rand(8, -MAXA, -1) + rand(27, -MAXA, MAXA))             # starts with losing days
add([3, 0, 3, 0, 0, 3, 0, 4, 1, 3, 0, 0, 2, 0])
# hidden: medium
add(rand(20000, -2, 2))
add(rand(3000, -MAXA, MAXA))
# hidden: big (N = 200000)
add(rand(N, -MAXA, MAXA))
add(rand(N, -MAXA, MAXA))
add(rand(N, 1, MAXA))
add([MAXA] * N)
add([-MAXA] * N)
add([0] * N)
add(rand(N, -2, 2))
add(rand(N, 0, 1))
add(rand(N, -1, 1))
a = []
while len(a) + 4 <= N:                                      # blocks x y x with x < y < 2x, then a losing day
    x = ri(MAXA // 4, MAXA // 2)
    a += [x, ri(x + 1, 2 * x - 1), x, -ri(1, MAXA)]
a += [-1] * (N - len(a))
add(a)
a = rand(N, -MAXA, -1)
for _ in range(1000):
    a[ri(0, N - 1)] = ri(1, MAXA)
add(a)                                                      # few paying days
add(rand(N // 4, -MAXA, -1) + rand(N - N // 4, -MAXA, MAXA))  # a long losing start
add([0 if rnd() < 0.2 else ri(-MAXA, MAXA) for _ in range(N)])
add(rand(N, -3, 5))
add([[-MAXA, 0, MAXA][ri(0, 2)] for _ in range(N)])
add([7] * N)
add(rand(N, -MAXA, -1))
a = []
while len(a) < N:                                           # runs of equal values
    a += [ri(-5, 9)] * ri(1, 6)
add(a[:N])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
