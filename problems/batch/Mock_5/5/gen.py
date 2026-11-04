# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1405001)
MAXN, MAXA = 200000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(a):
    assert 1 <= len(a) <= MAXN
    assert all(1 <= x <= MAXA for x in a)
    tests.append(f"{len(a)}\n" + " ".join(map(str, a)) + "\n")


def logu(n, hi=MAXA):
    """values spread over all magnitudes (random exponent, then random mantissa)"""
    out = []
    for _ in range(n):
        top = 2 ** ri(0, 29)
        out.append(min(hi, ri(top, 2 * top - 1)))
    return out


def geo_blocks(n, up=True, ratio=2, start=1):
    """blocks start, start * ratio, ... (each value is at least the sum of the earlier ones in its block)"""
    out = []
    while len(out) < n:
        x, blk = start, []
        while x <= MAXA:
            blk.append(x)
            x *= ratio
        out += blk if up else blk[::-1]
    return out[:n]


def fib_blocks(n, x=1, y=1):
    """Fibonacci blocks: three neighbours have max equal to the sum of the other two"""
    out = []
    while len(out) < n:
        a, b = x, y
        while a <= MAXA:
            out.append(a)
            a, b = b, a + b
    return out[:n]


def spikes(n, low, high, every, scale):
    """small values with a spike every ~`every` villages; a spike is about `scale` times the sum since the last one"""
    out, since = [], 0
    for i in range(n):
        if i and ri(1, every) == 1:
            v = max(1, min(MAXA, int(since * scale * (0.6 + 0.8 * rnd()))))
            since = 0
        else:
            v = ri(low, high)
        out.append(v)
        since += v
    return out


def doubling(n, lo, hi):
    """each village about as big as all the previous ones of its run together (sum doubles), runs restart"""
    out = []
    while len(out) < n:
        s = ri(1, 3)
        out.append(s)
        tot = s
        while len(out) < n:
            v = tot + ri(lo, hi)
            if v < 1 or v > MAXA:
                break
            out.append(v)
            tot += v
    return out[:n]


def plant(a, k):
    """k long stretches of tiny values next to one huge village (long districts that are not balanced)"""
    a = list(a)
    n = len(a)
    for _ in range(k):
        ln = ri(4000, 40000)
        st = ri(1, n - ln - 1)
        for i in range(st, st + ln):
            a[i] = ri(1, 3)
        a[st - 1 if ri(0, 1) else st + ln] = MAXA
    return a


# samples
add([4, 2, 3, 6, 2])
add([5, 5, 5, 5])
add([3, 1, 2, 2, 5, 1])
add([4, 1, 1, 6, 2, 3, 9])
add([10, 1, 2, 3, 8, 20])
# hidden: small (brute checks these)
add([MAXA])
add([7, 7])
add([ri(1, 10) for _ in range(300)])
add(logu(2000))
add(fib_blocks(1500, 1, 2))
add(spikes(3000, 1, 9, 6, 1.0))
add([MAXA if ri(1, 300) == 1 else ri(1, 3) for _ in range(3000)])
add(doubling(3000, -2, 2))
add([MAXA] * 5000)
# hidden: big (each with its own seed)
N = MAXN
BIG = [
    (1406000, lambda: [MAXA] * N),
    (1406001, lambda: plant([ri(1, MAXA) for _ in range(N)], 3)),
    (1406002, lambda: plant(logu(N), 3)),
    (1406003, lambda: plant(geo_blocks(N, True), 3)),
    (1406004, lambda: plant(geo_blocks(N, False), 3)),
    (1406005, lambda: plant(fib_blocks(N), 3)),
    (1406006, lambda: plant(spikes(N, 1, 9, 30, 1.0), 3)),
    (1406007, lambda: spikes(N, 1, 100, 1000, 1.0)),
    (1406008, lambda: spikes(N, 1, 3, 3, 1.0)),
    (1406009, lambda: plant(doubling(N, -1, 1), 3)),
    (1406010, lambda: plant(sorted(ri(1, MAXA) for _ in range(N)), 3)),
    (1406011, lambda: plant(sorted((ri(1, 10 ** 6) for _ in range(N)), reverse=True), 3)),
    (1406018, lambda: [MAXA if ri(1, 20000) == 1 else ri(1, 1000) for _ in range(N)]),
    (1406012, lambda: plant([ri(1, 5) if i % 2 else 2 ** ri(0, 29) for i in range(N)], 3)),
    (1406013, lambda: [x for i in range(N // 2) for x in (1, 1)][:N - 1] + [MAXA]),
    (1406014, lambda: plant(geo_blocks(N // 2, True, 3) + geo_blocks(N - N // 2, False, 3), 3)),
    (1406015, lambda: spikes(N, 1, 1000, 15000, 1.0)),
    (1406016, lambda: [MAXA if ri(1, 4000) == 1 else ri(1, 3) for _ in range(N)]),
    (1406017, lambda: [ri(10 ** 5, MAXA) if ri(1, 500) == 1 else ri(1, 50) for _ in range(N)]),
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
