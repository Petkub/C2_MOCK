# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1302003)
rnd = random.random
MAXN, MAXQ, MAXA, MAXK = 500000, 50000, 10 ** 9, 10
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def add(a, qs):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= len(qs) <= MAXQ
    assert all(1 <= x <= MAXA for x in a)
    for l, r, k in qs:
        assert 1 <= l <= r <= n and 1 <= k <= MAXK
    lines = ["%d %d" % (n, len(qs)), " ".join(map(str, a))] + ["%d %d %d" % q for q in qs]
    tests.append("\n".join(lines) + "\n")


def arr(n, hi, lo=1):
    span = hi - lo + 1
    return [lo + int(rnd() * span) for _ in range(n)]


ALLK = tuple(range(1, MAXK + 1))


def rq(n, q, ks=ALLK):
    out = []
    for _ in range(q):
        l, r = ri(1, n), ri(1, n)
        if l > r:
            l, r = r, l
        out.append((l, r, pick(ks)))
    return out


def longq(n, q, ks=ALLK, slack=1000):
    """ranges that cover almost the whole array"""
    return [(ri(1, slack), ri(n - slack + 1, n), pick(ks)) for _ in range(q)]


def shortq(n, q, maxlen=25):
    out = []
    for _ in range(q):
        l = ri(1, n)
        out.append((l, min(n, l + ri(0, maxlen - 1)), ri(1, MAXK)))
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
# hidden: large values (sums far above 2^31)
M = 100000
add([MAXA] * M, [(1, M, pick((2, 3))) for _ in range(MAXQ)])
add(arr(M, MAXA, MAXA - 1000), longq(M, MAXQ, (2, 3, 5, 7)))
add(arr(M, MAXA), rq(M, MAXQ))
add([pick((1, MAXA)) for _ in range(M)], longq(M, MAXQ, (1, 2, 4)))
# hidden: the largest N and Q (long ranges, small k)
N, Q = MAXN, MAXQ
A9, A99, A999 = arr(N, 9), arr(N, 99), arr(N, 999)
add(A9, longq(N, Q, (2,)))
add(A99, longq(N, Q, (2, 3)))
add(A9, longq(N, Q))
add(A999[:N - 37], longq(N - 37, Q, (1, 2)))
add(A99, rq(N, Q))
add(A9, rq(N, Q, (2,)))
add(A999, longq(N, Q, (4, 5, 9, 10)))
add(arr(N, 9, 5), [(ri(1, 10), N - ri(0, 9), ri(1, 10)) for _ in range(Q)])
add(A99, longq(N, Q // 2, (2, 3)) + shortq(N, Q // 2))
add([1 + 8 * (i % 2) for i in range(N)], longq(N, Q, (2, 3, 5, 7)))
add(A9, [(ri(1, 30), N, ri(1, 10)) for _ in range(Q)])
add(A99, [(1, ri(N - 30, N), ri(2, 4)) for _ in range(Q)])
add(A999, longq(N, Q, (3, 4, 5, 6), slack=5000))
add(A9, longq(N, Q, (2, 6, 10), slack=20000))
add(arr(N, 99, 90), longq(N, Q, (2, 3, 4)))
add(A99[::-1], longq(N, Q, ALLK, slack=100))

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
