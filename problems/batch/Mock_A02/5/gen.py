# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1006219)
rnd = random.random
MAXN, MAXQ, MAXV = 200000, 100000, 10 ** 6
tests = []
STR = [str(i) for i in range(MAXV + 1)]


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(d, p):
    n, q = len(d), len(p)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert 1 <= min(d) and max(d) <= MAXV
    assert 1 <= min(p) and max(p) <= MAXV
    tests.append("%d %d\n%s\n%s\n" % (n, q, " ".join([STR[x] for x in d]), " ".join([STR[x] for x in p])))


# ---- difficulties ----
def uni(n, lo, hi):
    w = hi - lo + 1
    return [lo + int(rnd() * w) for _ in range(n)]


def increasing(n):
    """strictly increasing, spread over 1 .. MAXV"""
    g = 2 * (MAXV // n) - 2
    out, x = [], 0
    for _ in range(n):
        x += 1 + int(rnd() * g)
        out.append(x)
    assert out[-1] <= MAXV
    return out


def walk(n, step):
    """random walk inside 1 .. MAXV"""
    out, x = [], ri(1, MAXV)
    for _ in range(n):
        x += int(rnd() * (2 * step + 1)) - step
        if x < 1:
            x = 2 - x
        if x > MAXV:
            x = 2 * MAXV - x
        out.append(x)
    return out


def walls(n, lo, hi, prob):
    """values in lo..hi, and now and then a stage of difficulty MAXV"""
    return [MAXV if rnd() < prob else lo + int(rnd() * (hi - lo + 1)) for _ in range(n)]


def swaps(a, k):
    a = list(a)
    n = len(a)
    for _ in range(k):
        i, j = int(rnd() * n), int(rnd() * n)
        a[i], a[j] = a[j], a[i]
    return a


def zigzag(n):
    return [ri(1, 1000) if i % 2 == 0 else ri(MAXV - 1000, MAXV) for i in range(n)]


# ---- powers ----
def mixed(q, d):
    """mostly uniform, some equal to a difficulty, some at the very top"""
    n, top = len(d), max(d)
    out = []
    for _ in range(q):
        r = rnd()
        if r < 0.7:
            out.append(1 + int(rnd() * MAXV))
        elif r < 0.9:
            out.append(d[int(rnd() * n)])
        else:
            out.append(ri(top, MAXV))
    return out


def near(q, d, lo_frac, hi_frac):
    """powers between two quantiles of the difficulties (long runs when the quantiles are high)"""
    s = sorted(d)
    n = len(s)
    a, b = s[int(lo_frac * (n - 1))], s[int(hi_frac * (n - 1))]
    return [ri(a, b) for _ in range(q)]


# samples
add([2, 7, 3, 1, 7, 4], [3, 7, 5])
add([6, 2, 2, 8], [2, 1, 9])
add([5, 1, 6], [5, 6, 2])
add([3, 3, 9, 1, 4, 3, 8, 2], [3, 8, 1, 4])
add([12, 40, 7, 7, 25, 3, 40, 18, 9, 30], [7, 25, 2, 18, 40])
# hidden: small and medium (brute checks these)
add([MAXV], [MAXV])
add([1, MAXV, 1], [1, MAXV - 1, MAXV, 999])
add(uni(8, 1, 10), uni(10, 1, 11))
add(uni(100, 1, 20), uni(100, 1, 21))
add(walk(200, 5), uni(100, 1, MAXV))
add(walk(2000, 3000), uni(2000, 1, MAXV))
d = uni(12000, 1, MAXV)
add(d, mixed(12000, d))
add([1 if rnd() < 0.99999 else 9 for _ in range(70000)], uni(30, 1, 9))
# hidden: big (n = 200000, q = 100000)
N, Q = MAXN, MAXQ
d = uni(N, 1, MAXV); add(d, mixed(Q, d))
d = uni(N, 1, 1000); add(d, mixed(Q, d))
d = increasing(N); add(d, mixed(Q, d))
d = increasing(N)[::-1]; add(d, mixed(Q, d))
d = sorted(uni(N, 1, MAXV // 4)); add(d, mixed(Q, d))
d = increasing(N // 2) + increasing(N // 2)[::-1]; add(d, mixed(Q, d))          # one hill
d = increasing(N // 2)[::-1] + increasing(N // 2); add(d, mixed(Q, d))          # one valley
d = zigzag(N); add(d, mixed(Q, d))
d = walls(N, 1, MAXV // 2, 0.00002); add(d, near(Q, d, 0.3, 1.0))
d = [MAXV // 2] * N; add(d, [MAXV // 2 + (1 if rnd() < 0.5 else -1) * ri(0, 3) for _ in range(Q)])
d = swaps(increasing(N), 100); add(d, mixed(Q, d))
d = uni(N, 1, MAXV); add(d, sorted(mixed(Q, d)))
d = uni(N, 1, MAXV); add(d, sorted(mixed(Q, d))[::-1])
d = uni(N, 1, 10); add(d, uni(Q, 1, 11))
d = walk(N, 1000); add(d, mixed(Q, d))
d = walk(N, 50000); add(d, near(Q, d, 0.5, 1.0))
d = uni(N, 1, MAXV); add(d, near(Q, d, 0.99, 1.0))
d = swaps(increasing(N)[::-1], 2000); add(d, near(Q, d, 0.0, 1.0))
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
