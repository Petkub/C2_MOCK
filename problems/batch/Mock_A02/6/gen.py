# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1902)
MAXQ, MAXV = 100000, 4000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only rnd(), so every Python version gives the same tests)"""
    return a + int(rnd() * (b - a + 1))


def add(qs):
    assert 1 <= len(qs) <= MAXQ
    for w, b, k in qs:
        assert 0 <= w <= MAXV and 0 <= b <= MAXV and w + b >= 1 and 0 <= k <= MAXV
    tests.append(f"{len(qs)}\n" + "".join(f"{w} {b} {k}\n" for w, b, k in qs))


def peak(w, b):
    """a k where the count is far from zero (about the usual number of white-black places)"""
    if w == 0 or b == 0:
        return 0
    m = w * b // (w + b)
    return max(1, min(w, b, m + ri(-40, 40)))


def query(maxv, kind):
    w, b = ri(0, maxv), ri(0, maxv)
    if kind == "big":
        w, b = ri(maxv * 4 // 5, maxv), ri(maxv * 4 // 5, maxv)
    if w + b == 0:
        w = 1
    r = rnd()
    if r < 0.7:
        k = peak(w, b)
    elif r < 0.8:
        k = min(w, b)
    elif r < 0.85:
        k = min(MAXV, min(w, b) + ri(1, 3))
    elif r < 0.9:
        k = ri(0, 2)
    else:
        k = ri(0, max(1, min(w, b)))
    return (w, b, k)


def edge():
    """one colour (any k), both colours with k = 0, or k larger than min(W, B)"""
    r = rnd()
    if r < 0.4:
        c, k = ri(1, MAXV), (0 if rnd() < 0.5 else ri(1, 3))
        return (c, 0, k) if rnd() < 0.5 else (0, c, k)
    if r < 0.7:
        return (ri(1, MAXV), ri(1, MAXV), 0)
    w, b = ri(1, MAXV - 1), ri(1, MAXV - 1)
    return (w, b, min(MAXV, min(w, b) + ri(1, 50)))


# samples (true answers below the modulus)
add([(2, 2, 1), (2, 2, 2)])
add([(3, 1, 1), (3, 1, 2), (1, 3, 1)])
add([(1, 1, 1), (3, 3, 2), (4, 2, 2), (5, 5, 3), (6, 4, 1)])
add([(10, 10, 5), (7, 3, 3), (8, 8, 8), (12, 5, 4)])
add([(20, 15, 7), (16, 18, 6), (25, 25, 1)])
# hidden: small (brute checks these)
add([(w, b, k) for w in range(9) for b in range(9) if w + b > 0 for k in range(10)])
add([(1, 0, 0), (0, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 0), (1, 1, 1), (1, 1, 2)])
add([query(30, "any") for _ in range(1500)])
add([query(60, "big") for _ in range(800)])
add([(ri(40, 60), ri(40, 60), ri(0, 60)) for _ in range(800)])
add([edge() for _ in range(3000)])
# hidden: big
BIG = [
    lambda: query(MAXV, "big"),
    lambda: query(MAXV, "any"),
    lambda: (MAXV, MAXV, peak(MAXV, MAXV)),
    lambda: (ri(1, MAXV), ri(1, MAXV), ri(0, MAXV)),
    lambda: (ri(MAXV - 100, MAXV), ri(1, 50), ri(1, 50)),
    lambda: (MAXV, MAXV, ri(1, MAXV)),
]
for seed, kinds in [(1, [0]), (2, [0]), (3, [1]), (4, [2]), (5, [0, 1]), (6, [3]), (7, [4]), (8, [0, 4]),
                    (9, [5]), (10, [0]), (11, [0, 2]), (12, [1, 3]), (13, [0]), (14, [2, 5]), (15, [0]),
                    (16, [0, 1, 2, 3, 4, 5]), (17, [0])]:
    random.seed(19020 + seed)
    pe = 0.003 if seed % 3 else 0.0     # most big tests also hold a few edge queries
    add([edge() if rnd() < pe else BIG[kinds[i % len(kinds)]]() for i in range(MAXQ)])

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
