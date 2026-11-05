# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1403)
MAXRC, MAXK, MAXA = 500, 20, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only random.random(), so every Python version gives the same tests)"""
    return a + int(rnd() * (b - a + 1))


def add(K, g):
    R, C = len(g), len(g[0])
    assert 1 <= R <= MAXRC and 1 <= C <= MAXRC and 1 <= K <= MAXK
    for row in g:
        assert len(row) == C and -MAXA <= min(row) and max(row) <= MAXA
    tests.append(f"{R} {C} {K}\n" + "".join(" ".join(map(str, row)) + "\n" for row in g))


def uniform(R, C, lo, hi):
    return [[ri(lo, hi) for _ in range(C)] for _ in range(R)]


def staircase(R, C, steps, good, bad, noise=0):
    """bad everywhere except a monotone staircase (from (1, 1) to (R, C)) with about `steps` turns, worth `good`"""
    g = [[ri(bad[0], bad[1]) for _ in range(C)] for _ in range(R)]
    r = c = 0
    moves = ["R"] * (C - 1) + ["D"] * (R - 1)
    # group the moves into `steps` + 1 alternating runs
    runs = max(1, min(steps + 1, len(moves)))
    seq, nr, nd = [], C - 1, R - 1
    for i in range(runs):
        left = runs - i
        if i % 2 == 0:
            k = nr if left <= 2 else ri(0, max(0, 2 * nr // left))
            seq += ["R"] * k
            nr -= k
        else:
            k = nd if left <= 2 else ri(0, max(0, 2 * nd // left))
            seq += ["D"] * k
            nd -= k
    seq += ["R"] * nr + ["D"] * nd
    g[0][0] = ri(good[0], good[1])
    for m in seq:
        if m == "R":
            c += 1
        else:
            r += 1
        g[r][c] = ri(good[0], good[1])
        if noise and 0 <= r + 1 < R:
            g[r + 1][c] = ri(good[0], good[1]) // noise
    return g


def transpose(g):
    return [list(col) for col in zip(*g)]


def bands(R, C, width, hi, lo):
    """diagonal bands: good cells where (r + c) // width is even, so a straight line crosses many bad bands"""
    return [[ri(hi // 2, hi) if ((r + c) // width) % 2 == 0 else ri(lo, lo // 2) for c in range(C)] for r in range(R)]


def checker(R, C, a, b):
    return [[(a if (r + c) % 2 == 0 else b) + ri(-3, 3) for c in range(C)] for r in range(R)]


# samples
add(2, [[2, -3, 4, 1], [1, 5, -2, 3], [-4, 2, 6, 1]])
add(1, [[1, 8, -9, 0], [-2, 3, 7, -1], [5, -6, 4, 2], [0, 1, -3, 6]])
add(3, [[4, -1, -2, 7, 3]])
add(1, [[-5]])
add(3, [[3, -2, 0, 1, 5], [1, 4, -3, 2, -1], [-6, 2, 8, -4, 0], [2, 0, 1, 3, 2], [-1, 5, -2, 6, 4]])
# hidden: small (brute checks these)
add(1, [[7], [-2], [3]])
add(20, [[MAXA] * 3] * 2)
add(1, uniform(2, 2, -MAXA, MAXA))
for R, C, K, lo, hi in [(9, 8, 2, -10, 10), (20, 25, 5, -10 ** 6, 10 ** 6),
                        (40, 40, 20, -50, 80), (50, 60, 4, -MAXA, MAXA)]:
    add(K, uniform(R, C, lo, hi))
add(6, staircase(45, 50, 9, (10 ** 8, MAXA), (-MAXA, -10 ** 8)))
add(3, bands(60, 60, 5, 10 ** 6, -10 ** 6))
# hidden: big
M = MAXRC
BIG = [
    (14300, lambda: (20, uniform(M, M, -MAXA, MAXA))),
    (14301, lambda: (1, uniform(M, M, -MAXA, MAXA // 2))),
    (14302, lambda: (12, transpose(staircase(M, M, 12, (-3 * 10 ** 8, -10 ** 8), (-MAXA, -6 * 10 ** 8))))),
    (14303, lambda: (20, [[MAXA] * M for _ in range(M)])),
    (14304, lambda: (20, [[-MAXA] * M for _ in range(M)])),
    (14305, lambda: (10, staircase(M, M, 30, (10 ** 8, MAXA), (-MAXA, -10 ** 8)))),
    (14306, lambda: (20, staircase(M, M, 20, (5 * 10 ** 8, MAXA), (-MAXA, 0), noise=3))),
    (14307, lambda: (18, staircase(M, M, 18, (MAXA, MAXA), (-10, 10)))),
    (14308, lambda: (13, bands(M, M, 7, MAXA, -MAXA))),
    (14309, lambda: (12, bands(M, M, 40, MAXA, -MAXA))),
    (14310, lambda: (20, checker(M, M, MAXA - 3, -MAXA + 3))),
    (14311, lambda: (16, checker(M, M, -10 ** 8, 10 ** 7))),
    (14312, lambda: (20, uniform(1, M, -MAXA, 0))),
    (14314, lambda: (15, uniform(M, 2, -MAXA, MAXA))),
    (14318, lambda: (2, uniform(M, M, -10 ** 4, 10 ** 4))),
    (14315, lambda: (11, uniform(M, M, -2 * 10 ** 8, 10 ** 7))),
    (14316, lambda: (14, staircase(M, M, 60, (-10 ** 7, 0), (-10 ** 8, -10 ** 7)))),
    (14317, lambda: (19, uniform(M, M, -10, 10))),
    (14319, lambda: (4, transpose(staircase(M, M, 4, (-10 ** 7, 0), (-5 * 10 ** 7, -10 ** 7))))),
]
for seed, make in BIG:
    random.seed(seed)
    add(*make())

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
