# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1005220)
rnd = random.random
MAXN, MAXQ, MAXA = 200000, 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a, qs):
    n, q = len(a), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(1 <= x <= MAXA for x in a)
    assert all(1 <= l <= r <= n for l, r in qs)
    tests.append(f"{n} {q}\n" + " ".join(map(str, a)) + "\n" + "".join(f"{l} {r}\n" for l, r in qs))


def shuffled(a):
    a = a[:]
    for i in range(len(a) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        a[i], a[j] = a[j], a[i]
    return a


def stairs(n, lo=1, extra=(0, 0), big=0.0):
    """values lo, lo+1, ... each occurring about x times (x + a delta from extra), shuffled;
    a fraction `big` of the positions gets a value > n (up to 10^9)"""
    a, x = [], lo
    while len(a) < n:
        a += [x] * max(1, x + ri(*extra))
        x += 1
    a = a[:n]
    for i in range(n):
        if rnd() < big:
            a[i] = ri(n + 1, MAXA)
    return shuffled(a)


def blocks(n, maxv, big=0.0):
    """runs: a value x repeated about x times, then another run (equal values close together)"""
    a = []
    while len(a) < n:
        x = ri(1, maxv)
        a += [x] * max(1, x + ri(-2, 2))
        if rnd() < big:
            a += [ri(n + 1, MAXA)] * ri(1, 5)
    return a[:n]


def uniform(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def q_random(n, q):
    out = []
    for _ in range(q):
        l, r = ri(1, n), ri(1, n)
        out.append((min(l, r), max(l, r)))
    return out


def q_short(n, q, maxlen):
    out = []
    for _ in range(q):
        ln = ri(1, min(n, maxlen))
        l = ri(1, n - ln + 1)
        out.append((l, l + ln - 1))
    return out


def q_long(n, q):
    out = []
    for _ in range(q):
        l = ri(1, max(1, n // 20))
        r = ri(n - n // 20, n)
        out.append((min(l, r), max(l, r)))
    return out


def q_mix(n, q):
    return shuffled(q_random(n, q // 3) + q_short(n, q // 3, 2000) + q_long(n, q - 2 * (q // 3)))


# samples
add([2, 1, 2, 3, 3, 5, 3, 1], [(1, 8), (1, 3), (3, 7)])
add([4, 100, 4, 4, 1, 4], [(1, 6), (2, 6), (5, 5)])
add([1, 1, 1, 1], [(1, 1), (1, 2), (2, 4)])
add([3, 2, 1, 2, 3, 3, 1, 2, 2, 6], [(1, 10), (2, 4), (1, 6), (4, 9)])
add([7, 2, 2, 7, 1, 9, 2], [(1, 7), (2, 3), (1, 1)])
# hidden: small (brute checks these)
add([1], [(1, 1)])
add([5], [(1, 1)])
add(stairs(60, extra=(-1, 1)), q_random(60, 300))
add(blocks(300, 12, big=0.2), q_mix(300, 600))
add(uniform(500, 1, 6), q_short(500, 800, 40))
add(stairs(2000, lo=2, extra=(-1, 2), big=0.1), q_random(2000, 1500))
add(uniform(3000, 1, 3000) + [MAXA] * 1000, q_mix(4000, 2000))
# hidden: big (N = 200000, Q = 100000)
N, Q = MAXN, MAXQ
add(stairs(N), q_random(N, Q))
add(stairs(N, extra=(-1, 1)), q_long(N, Q))
add(stairs(N, lo=2, extra=(-2, 2), big=0.15), q_random(N, Q))
add(blocks(N, 60), q_short(N, Q, 300))
add(blocks(N, 600, big=0.1), q_mix(N, Q))
add(blocks(N, 3000), q_random(N, Q))
add(uniform(N, 1, 20), q_short(N, Q, 100))
add(uniform(N, 1, 400), q_mix(N, Q))
add([ri(N - 2000, N) if rnd() < 0.85 else ri(N + 1, MAXA) for _ in range(N)], q_random(N, Q))   # almost no value can count
add([1] * N, q_short(N, Q, 3))
add([2, 1] * (N // 2), q_short(N, Q, 6))
add([ri(1, 3) if i % 2 else MAXA - ri(0, 9) for i in range(N)], q_short(N, Q, 12))
add(shuffled([3] * 3 + [10] * 10 + [100] * 100 + [1000] * 1000 + [10000] * 10000 + [100000] * 100000
             + uniform(N - 111113, N + 1, 2 * N)), q_long(N, Q))
add(stairs(N, extra=(0, 0)), q_long(N, Q))
add(stairs(N, extra=(-1, 0), big=0.02), q_mix(N, Q))
add(stairs(N, lo=3, extra=(0, 1)), q_random(N, Q))
add([N] * N, [(1, N)] * (Q // 2) + q_long(N, Q - Q // 2))           # one value occurring N times
a = stairs(N // 2, extra=(0, 1))
add(a + a[::-1], q_random(N, Q))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
