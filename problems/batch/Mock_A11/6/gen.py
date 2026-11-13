# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A grid is a list of strings of '0' (mango) and '1' (mangosteen); n * m <= 300 000.
# Most big tests plant one or more denser blocks of '1' on a sparser background, so the best plot is not trivial.
import os, random

random.seed(62014)
rnd = random.random
LIM = 300000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(g):
    n, m = len(g), len(g[0])
    assert 1 <= n and 1 <= m and n * m <= LIM
    assert all(len(r) == m and set(r) <= set("01") for r in g)
    tests.append("%d %d\n" % (n, m) + "\n".join(g) + "\n")


def rand_grid(n, m, p):
    return ["".join("1" if rnd() < p else "0" for _ in range(m)) for _ in range(n)]


def planted(n, m, p0, blocks):
    """background density p0; blocks = list of (r1, r2, c1, c2, p) (0-based, inclusive)"""
    g = [[1 if rnd() < p0 else 0 for _ in range(m)] for _ in range(n)]
    for r1, r2, c1, c2, p in blocks:
        for i in range(r1, r2 + 1):
            row = g[i]
            for j in range(c1, c2 + 1):
                row[j] = 1 if rnd() < p else 0
    return ["".join("1" if x else "0" for x in row) for row in g]


def rand_block(n, m, p, minfrac=0.2, maxfrac=0.8):
    h = max(1, int(n * (minfrac + (maxfrac - minfrac) * rnd())))
    w = max(1, int(m * (minfrac + (maxfrac - minfrac) * rnd())))
    r1, c1 = ri(0, n - h), ri(0, m - w)
    return (r1, r1 + h - 1, c1, c1 + w - 1, p)


def blocky(n, m, p0=None, k=None):
    if p0 is None:
        p0 = 0.15 + 0.3 * rnd()
    if k is None:
        k = ri(1, 3)
    return planted(n, m, p0, [rand_block(n, m, 0.6 + 0.35 * rnd()) for _ in range(k)])


# ---- samples (01..05) ----
add(["100101", "111001", "110000", "101110"])
add(["00000", "10100", "00001", "11100", "01001", "11100"])
add(["10110011"])
add(["001",
     "110",
     "111",
     "011",
     "101",
     "000"])
add(["01101",
     "10011",
     "01110",
     "11010",
     "00100"])

# ---- small hidden tests (brute checks these) ----
add(["0"])
add(["1"])
add(["0000", "0000", "0000"])
add(["1111", "1111"])
add(["0", "1", "1", "0", "1", "0", "0", "1"])
add(["0001000"])
for n, m, p in ((7, 9, 0.5), (12, 5, 0.35), (4, 15, 0.6), (11, 11, 0.45)):
    add(rand_grid(n, m, p))
add(blocky(14, 18, 0.25, 2))
add(blocky(20, 9, 0.3, 2))

# ---- max size: square and near-square ----
add(blocky(547, 548, 0.3, 1))
add(rand_grid(548, 547, 0.5))
add(blocky(400, 750, 0.35, 3))
add(blocky(750, 400, 0.35, 3))
add(["".join("1" if (i + j) % 2 else "0" for j in range(548)) for i in range(547)])   # checkerboard
add(["0" * 548 for _ in range(547)])                                                       # no mangosteen
add(["1" * 600 for _ in range(500)])                                                       # no mango
g = ["0" * 547 for _ in range(548)]
for _ in range(40):
    i, j = ri(0, 547), ri(0, 546)
    g[i] = g[i][:j] + "1" + g[i][j + 1:]
add(g)                                                                                     # a few mangosteen trees

# ---- max size: tall boards (more rows than columns) ----
add(blocky(150000, 2, 0.3, 2))
add(blocky(60000, 5, 0.25, 2))
add(blocky(30000, 10, 0.3, 3))
add(rand_grid(15000, 20, 0.5))
add(["0"] * LIM)
add(blocky(LIM, 1, 0.4, 2))

# ---- max size: wide boards (more columns than rows) ----
add(blocky(2, 150000, 0.3, 2))
add(blocky(5, 60000, 0.25, 2))
add(blocky(10, 30000, 0.3, 3))
add(blocky(1, LIM, 0.35, 2))

os.makedirs("tests", exist_ok=True)
for f in os.listdir("tests"):
    if f.endswith(".in"):
        os.remove(os.path.join("tests", f))
for k, t in enumerate(tests, 1):
    with open(os.path.join("tests", "%02d.in" % k), "w") as f:
        f.write(t)
