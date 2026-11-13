# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1302001)
MAXQ, MAXV = 50000, 10 ** 18
tests = []


def add(qs):
    assert 1 <= len(qs) <= MAXQ
    for a, b in qs:
        assert 0 <= a <= MAXV and 0 <= b <= MAXV
    tests.append("\n".join([str(len(qs))] + [f"{a} {b}" for a, b in qs]) + "\n")


def isqrt(x):
    r = int(x ** 0.5)
    while r * r > x:
        r -= 1
    while (r + 1) * (r + 1) <= x:
        r += 1
    return r


def clip(v):
    return max(0, min(MAXV, v))


def logu(hi):
    """a value spread over all orders of magnitude up to hi"""
    return min(hi, int(10 ** random.uniform(0, 18.0001)))


def square_edge(p):
    """the cans of p odd rows, give or take one"""
    return clip(p * p + random.choice((-1, -1, 0, 1)))


def even_edge(q):
    """the cans of q even rows, give or take one"""
    return clip(q * (q + 1) + random.choice((-1, -1, 0, 1)))


def edge_pair(lo, hi):
    """one colour exactly at a boundary, the other with enough cans or just one row short of it"""
    p = random.randint(lo, hi)
    kind = random.randint(0, 3)
    if kind == 0:
        a, b = square_edge(p), even_edge(p + random.randint(-1, 1))
    elif kind == 1:
        a, b = square_edge(p), even_edge(p - 1 + random.randint(0, 1))
    elif kind == 2:
        a, b = even_edge(p), square_edge(p + random.randint(-1, 1))
    else:
        a, b = square_edge(p), clip(random.randint(p * p - 2 * p, p * p + 2 * p))
    return (a, b) if random.random() < 0.5 else (b, a)


# samples
add([(5, 6), (0, 7), (10, 2)])
add([(3, 1), (2, 2)])
add([(0, 0), (1, 0), (0, 1), (6, 3), (100, 100)])
add([(7, 12), (12, 7), (16, 20), (20, 16), (1, 1000)])
add([(1000000, 1000000), (123456789, 987654321), (999999999999, 0)])
# hidden: small (brute checks these)
add([(a, b) for a in range(0, 30) for b in range(0, 30)])
add([(random.randint(0, 10 ** 4), random.randint(0, 10 ** 4)) for _ in range(2000)])
add([edge_pair(1, 3000) for _ in range(2000)])
add([(random.randint(0, 10 ** 8), random.randint(0, 10 ** 8)) for _ in range(300)])
add([edge_pair(1000, 30000) for _ in range(300)])
add([(random.randint(0, 10 ** 9), random.randint(0, 50)) for _ in range(200)]
    + [(random.randint(0, 50), random.randint(0, 10 ** 9)) for _ in range(200)])
add([(MAXV, MAXV)])
# hidden: big
add([(MAXV - random.randint(1, 10 ** 9), MAXV) if i % 2 else (MAXV, MAXV - random.randint(1, 10 ** 9))
     for i in range(MAXQ)])
add([(MAXV - i, MAXV - random.randint(0, 3)) for i in range(MAXQ)])
add([edge_pair(900000000, 1000000000) for _ in range(MAXQ)])
add([edge_pair(900000000, 1000000000) for _ in range(MAXQ)])
add([edge_pair(1, 1000000000) for _ in range(MAXQ)])
add([edge_pair(100000000, 1000000000) for _ in range(MAXQ)])
add([(logu(MAXV), logu(MAXV)) for _ in range(MAXQ)])
add([(random.randint(0, MAXV), random.randint(0, MAXV)) if i % 2 else edge_pair(1, 1000000000) for i in range(MAXQ)])
add([edge_pair(500000000, 1000000000) for _ in range(MAXQ)])
add([edge_pair(200000000, 1000000000) for _ in range(MAXQ)])
bigp = [(p * p - 1, MAXV) for p in range(10 ** 9, 10 ** 9 - MAXQ // 2, -1)]
add(bigp + [(b, a) for a, b in bigp])
bigq = [(MAXV, q * (q + 1) - 1) for q in range(999999999, 999999999 - MAXQ // 2, -1)]
add(bigq + [(b, a) for a, b in bigq])
add([(clip(p * p - 1), clip(p * p - p - 1)) for p in (random.randint(5 * 10 ** 8, 10 ** 9) for _ in range(MAXQ))])
add([(clip(x), clip(x + random.randint(-2 * 10 ** 9, 2 * 10 ** 9)))
     for x in (random.randint(10 ** 17, MAXV) for _ in range(MAXQ))])
add([edge_pair(100000000, 1000000000) if i % 10 else edge_pair(1, 1000) for i in range(MAXQ)])
add([(random.randint(0, 10 ** 12), random.randint(0, 10 ** 12)) for _ in range(MAXQ)])
add([(random.randint(0, 10 ** 14), random.randint(0, MAXV)) if i % 2 else (random.randint(0, MAXV), random.randint(0, 10 ** 14))
     for i in range(MAXQ)])
add([edge_pair(999000000, 1000000000) for _ in range(MAXQ)])

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
