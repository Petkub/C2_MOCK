# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1201350)
rnd = random.random
MAXRC, MAXA = 400, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(g):
    r, c = len(g), len(g[0])
    assert 1 <= r <= MAXRC and 1 <= c <= MAXRC
    assert all(len(row) == c and all(-MAXA <= x <= MAXA for x in row) for row in g)
    tests.append(f"{r} {c}\n" + "".join(" ".join(map(str, row)) + "\n" for row in g))


def rand_grid(r, c, lo, hi):
    return [[ri(lo, hi) for _ in range(c)] for _ in range(r)]


def mixed(r, c, big, p_neg):
    """values in [-big, big], negative with probability p_neg"""
    return [[(-1 if rnd() < p_neg else 1) * ri(0, big) for _ in range(c)] for _ in range(r)]


def bad_rows(r, c, big, rows, depth):
    """mostly positive grid; the given rows are almost all strongly negative, with a few cheap holes"""
    g = [[ri(0, big) for _ in range(c)] for _ in range(r)]
    for i in rows:
        for j in range(c):
            g[i][j] = -ri(depth // 2, depth)
        for _ in range(max(1, c // 50)):
            g[i][ri(0, c - 1)] = -ri(0, depth // 4)
    return g


# samples
add([[3, -1, 2, 5], [-4, 6, -8, -2], [-3, -9, -7, 4], [1, 3, -2, 2]])
add([[1, 4, 2], [5, 1, 1], [2, 3, 6], [4, 1, 2], [1, 7, 3]])
add([[2, -3, 4, 1, -6], [-5, 2, -1, -4, 3], [7, 1, -8, 2, 0], [-2, -6, 3, 5, -1],
     [4, -3, -9, 1, 2], [-1, 8, 2, -7, 6]])
add([[-5], [-7], [-2]])
add([[12, -30, 7, 25, -4, 9], [-18, 5, -11, -26, 14, -3], [21, -9, 16, 3, -20, 8],
     [-6, -27, 4, 19, -12, 11], [10, 2, -15, -8, 23, -5]])
# hidden: small (brute checks these)
add([[ri(-9, 9)]])
add([[-3, 4], [5, -2]])
add(rand_grid(13, 1, -20, 20))
add(mixed(13, 5, 1000, 0.6))
add(rand_grid(11, 7, 1, 30))                                  # all positive: no jump
add(bad_rows(13, 6, 40, [3, 8], 500))                         # two bad rows: one jump is not enough
add(rand_grid(12, 4, -1000, -1))                              # all negative
add([[ri(-5, 5) for _ in range(MAXRC)]])                      # one row
# hidden: big
R = C = MAXRC
add(mixed(R, C, MAXA, 0.5))
add(mixed(R, C, MAXA, 0.7))
add(mixed(R, C, MAXA, 0.3))
add(rand_grid(R, C, 0, MAXA))                                 # no jump, answer > 2^31
add(rand_grid(R, C, -MAXA, -MAXA // 2))                      # all strongly negative
add([[MAXA] * C for _ in range(R)])
add([[-MAXA] * C for _ in range(R)])
add(bad_rows(R, C, MAXA, [150], MAXA))                        # one bad row: jump over it
add(bad_rows(R, C, MAXA // 10, [40, 41, 200, 330, 331, 332], MAXA))
add(bad_rows(R, C, MAXA, list(range(5, R - 1, 7)), MAXA))     # many bad rows
add(mixed(R, C, 1000, 0.55))
add(mixed(R, C, 10 ** 6, 0.45))
add(mixed(R, C, MAXA, 0.6))
add(mixed(R, C, 10 ** 5, 0.15))                               # few negatives
add(rand_grid(R, 1, -MAXA, MAXA))                             # one column
add(rand_grid(R, 3, -MAXA, MAXA))
add(rand_grid(2, C, -MAXA, MAXA))                             # two rows: no jump possible
add(rand_grid(3, C, -MAXA, MAXA))
g = rand_grid(R, C, 0, 10 ** 6)
for j in range(C):
    g[R - 2][j] = -MAXA                                       # the jump must end on the last row
add(g)
g = rand_grid(R, C, 0, 10 ** 6)
for j in range(C):
    g[1][j] = -MAXA                                           # the jump must start on the first row
add(g)
g = rand_grid(R, C, 0, MAXA)
g[0] = [-ri(MAXA // 2, MAXA) for _ in range(C)]               # the first row is strongly negative but must be used
add(g)
g = mixed(R, C, MAXA, 0.4)
g[0] = [-ri(MAXA // 2, MAXA) for _ in range(C)]               # the same with a mixed grid
add(g)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
