# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# c = the number of workers with A_i > B_i; a plan (x, y) "binds" when x > c or N - y < c.
import os, random

random.seed(1121)
rnd = random.random
MAXN, MAXQ, MAXV = 100000, 100000, 100000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a, b, qs):
    n, q = len(a), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ and len(b) == n
    assert all(0 <= v <= MAXV for v in a) and all(0 <= v <= MAXV for v in b)
    assert all(0 <= x and 0 <= y and x + y <= n for x, y in qs)
    lines = [f"{n} {q}", " ".join(map(str, a)), " ".join(map(str, b))]
    lines += [f"{x} {y}" for x, y in qs]
    tests.append("\n".join(lines) + "\n")


def positives(a, b):
    return sum(1 for u, v in zip(a, b) if u > v)


def plans(n, c, q, wide=0.8, low=0.1, narrow=0.05):
    """wide: small x and y (the best count c is allowed); low: x > c (mango needs more workers);
    the rest: N - y < c (longan needs more workers). Binding plans are mostly close to c."""
    m = max(1, n // 50)
    out = []
    for _ in range(q):
        t = rnd()
        if t < wide or (t < wide + low and c == n) or (t >= wide + low and c == 0):
            x, y = ri(0, m), ri(0, m)
        elif t < wide + low:
            x = c + 1 + int(rnd() ** 3 * (n - c - 1))
            y = ri(0, min(n - x, m))
        else:
            y = n - c + 1 + int(rnd() ** 3 * (c - 1))
            x = ri(0, min(n - y, m))
        if rnd() < narrow and x + y < n:   # a narrower window now and then
            s = ri(0, n - x - y)
            if rnd() < 0.5:
                x += s
            else:
                y += s
        out.append((x, y))
    return out


def all_plans(n):
    return [(x, y) for x in range(n + 1) for y in range(n + 1 - x)]


def uni(n, lo=0, hi=MAXV):
    return [ri(lo, hi) for _ in range(n)]


def near(base, spread):
    return [min(MAXV, max(0, v + ri(-spread, spread))) for v in base]


def big(a, b, q=MAXQ, **kw):
    add(a, b, plans(len(a), positives(a, b), q, **kw))


# samples
add([5, 3, 7, 2], [4, 6, 1, 2], [(1, 2), (0, 3), (4, 0)])
add([2, 9, 4], [6, 5, 3], [(0, 2), (3, 0), (1, 1)])
add([8], [3], [(0, 1), (1, 0)])
add([10, 0, 6, 6, 3], [1, 7, 6, 2, 9], [(0, 5), (4, 1)])
add([4, 4, 4, 4, 4, 4], [1, 2, 3, 5, 6, 7], [(1, 4), (2, 2), (0, 3), (5, 0)])
# hidden: small and medium (brute checks these)
add([0], [0], [(0, 0), (1, 0), (0, 1)])
add([MAXV, MAXV], [MAXV, 0], all_plans(2))
a = uni(8, 0, 20); b = uni(8, 0, 20); add(a, b, all_plans(8))
a = uni(12, 0, 5); add(a, a[:], all_plans(12))                            # every worker picks the same
a = uni(15, 0, 10); b = uni(15, 0, 10); add(a, b, all_plans(15))
a = uni(1000); b = uni(1000); big(a, b, 2000)
a = uni(1500, 50000); b = uni(1500, 0, 60000); big(a, b, 2000)           # most prefer mango
a = uni(1500, 0, 60000); b = uni(1500, 50000); big(a, b, 2000)           # most prefer longan
a = uni(2000, 0, 10); b = uni(2000, 0, 10); big(a, b, 2000)              # many equal pairs
# hidden: big (N = Q = 100000)
N = MAXN
big(uni(N), uni(N))
big(uni(N), uni(N), wide=0.8, low=0.1, narrow=0.0)
big(uni(N), uni(N), wide=0.2, low=0.4, narrow=0.3)
big(uni(N, 30000), uni(N, 0, 70000))
big(uni(N, 0, 70000), uni(N, 30000))
big(uni(N, 90000), uni(N, 90000))                                        # values near the top
a = uni(N); big(a, near(a, 3))                                           # nearly equal, many ties
a = uni(N); big(a, a[:])                                                 # all equal
big([MAXV] * N, uni(N))                                                  # c close to N
big(uni(N), [MAXV] * N)                                                  # c = 0
big([MAXV] * N, [MAXV] * N, wide=0.9, low=0.05)
b = uni(N); big([min(MAXV, v + ri(0, 20)) for v in b], b)               # greedy by A looks fine
a = uni(N); big(a, [min(MAXV, max(0, MAXV - v + ri(-1000, 1000))) for v in a])
a = [ri(0, 10000) for _ in range(N)]; big(a, [ri(0, 10000) for _ in range(N)])  # small values
big(uni(N), uni(N), wide=1.0, low=0.0, narrow=0.0)                                   # only wide plans
big(uni(N), uni(N), wide=0.0, low=0.5)                                   # only binding plans

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
