# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1302003)
MAXN, MAXQ, MAXA, MAXK = 100000, 100000, 10 ** 9, 10
tests = []


def add(a, qs):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= len(qs) <= MAXQ
    assert all(1 <= x <= MAXA for x in a)
    for l, r, k in qs:
        assert 1 <= l <= r <= n and 1 <= k <= MAXK
    lines = [f"{n} {len(qs)}", " ".join(map(str, a))] + [f"{l} {r} {k}" for l, r, k in qs]
    tests.append("\n".join(lines) + "\n")


def arr(n, hi, lo=1):
    return [random.randint(lo, hi) for _ in range(n)]


def rq(n, q, ks=range(1, MAXK + 1)):
    out = []
    for _ in range(q):
        l, r = sorted((random.randint(1, n), random.randint(1, n)))
        out.append((l, r, random.choice(ks)))
    return out


def longq(n, q, ks=range(1, MAXK + 1), slack=1000):
    """ranges that cover almost the whole array"""
    return [(random.randint(1, slack), random.randint(n - slack + 1, n), random.choice(ks)) for _ in range(q)]


def shortq(n, q, maxlen=25):
    out = []
    for _ in range(q):
        l = random.randint(1, n)
        r = min(n, l + random.randint(0, maxlen - 1))
        out.append((l, r, random.randint(1, MAXK)))
    return out


# samples
add([5, 3, 8, 1, 4, 2], [(1, 6, 2), (2, 5, 3), (3, 3, 1)])
add([7, 7, 7, 7, 7], [(1, 3, 5), (1, 5, 5), (2, 5, 2)])
add([10], [(1, 1, 1), (1, 1, 2)])
add([4, 1, 6, 2, 9, 3, 5, 8], [(1, 8, 3), (2, 7, 4), (4, 8, 1), (5, 6, 7), (1, 8, 10)])
add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [(1, 12, 4), (3, 12, 5), (6, 9, 2), (10, 12, 3)])
# hidden: small (brute checks these)
add([MAXA], [(1, 1, k) for k in range(1, MAXK + 1)])
add(arr(10, 20), [(l, r, k) for l in range(1, 11) for r in range(l, 11) for k in range(1, 11)])
add(arr(50, 100), rq(50, 3000))
add(arr(300, MAXA), rq(300, 3000) + shortq(300, 1000))
add(arr(2000, 1000), rq(2000, 2000))
add(arr(5000, MAXA), longq(5000, 1000, slack=50))
# hidden: big
N, Q = MAXN, MAXQ
add([MAXA] * N, [(1, N, random.choice((2, 3))) for _ in range(Q)])
add([MAXA] * N, longq(N, Q))
add(arr(N, MAXA), longq(N, Q, (2, 3, 4)))
add(arr(N, MAXA), longq(N, Q, (1, 2)))
add(arr(N, MAXA), rq(N, Q))
add(arr(N, MAXA), rq(N, Q, (2,)))
add(arr(N, 1000), longq(N, Q))
add(arr(N, MAXA, 10 ** 8), longq(N, Q, (2, 3)))
add(arr(N, 1000), rq(N, Q))
add(arr(N, MAXA), longq(N, Q, (4, 5, 9, 10)))
add(arr(N, 100), [(random.randint(1, 10), N - random.randint(0, 9), random.randint(1, 10)) for _ in range(Q)])
add(arr(N, 100), longq(N, Q // 2, (2, 3)) + shortq(N, Q // 2))
add(arr(N, MAXA, MAXA - 1000), longq(N, Q, (2, 3, 5, 7)))
add([random.choice((1, MAXA)) for _ in range(N)], rq(N, Q))
add(arr(N, 9), [(l, N, k) for l, k in ((random.randint(1, 30), random.randint(1, 10)) for _ in range(Q))])
add(arr(N, 9), [(1, r, k) for r, k in ((random.randint(N - 30, N), random.randint(2, 4)) for _ in range(Q))])
add(arr(N, 9), longq(N, Q, (3, 4, 5, 6), slack=5000))
add(arr(N, 99), longq(N, Q, (2, 6, 10), slack=20000))

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
