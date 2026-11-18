# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(130317)
rnd = random.random
MAXCELLS, MAXA = 300000, 10 ** 6
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(K, g):
    R, C = len(g), len(g[0])
    assert R >= 1 and C >= 1 and R * C <= MAXCELLS
    assert all(len(row) == C for row in g)
    assert 1 <= K <= C
    assert all(-MAXA <= x <= MAXA for row in g for x in row)
    lines = [f"{R} {C} {K}"] + [" ".join(map(str, row)) for row in g]
    tests.append("\n".join(lines) + "\n")


def rand_grid(R, C, lo, hi):
    return [[ri(lo, hi) for _ in range(C)] for _ in range(R)]


def mixed(R, C, M, pos=0.5, neg=0):
    """values in [-M, M]; each is positive with probability pos, a negative one is at most -neg"""
    return [[ri(1, M) if rnd() < pos else -ri(neg, M) for _ in range(C)] for _ in range(R)]


def trap_row(C, K, M):
    """values for one row against a scan that drops a negative start: short rich blocks (shorter than K), each
    preceded by a mildly negative stretch and followed by a very negative one, so the best tunnel keeps the stretch"""
    row = []
    while len(row) < C:
        blk = ri(max(1, K // 4), max(1, K // 2))
        row += [-ri(M // 50, M // 10) for _ in range(ri(K, 2 * K))]
        row += [ri(M // 2, M) for _ in range(blk)]
        row += [-ri(M // 2, M) for _ in range(ri(K, 2 * K))]
    return row[:C]


def shafts(g, i):
    """best shaft sums above and below every plot of row i"""
    R, C = len(g), len(g[0])
    up, dn = [0] * C, [0] * C
    for j in range(C):
        s = 0
        for t in range(i - 1, -1, -1):
            s += g[t][j]
            up[j] = max(up[j], s)
        s = 0
        for t in range(i + 1, R):
            s += g[t][j]
            dn[j] = max(dn[j], s)
    return up, dn


def embed(R, C, i, target, M, pos):
    """a grid whose row i is worth `target` per plot once its best shafts are added; other rows poor"""
    g = mixed(R, C, M, pos, M // 2)
    up, dn = shafts(g, i)
    for j in range(C):
        while not -M <= target[j] - up[j] - dn[j] <= M:     # a shaft too rich: block it next to the tunnel row
            for t in list(range(i - 1, -1, -1)) + list(range(i + 1, R)):
                if g[t][j] != -M:
                    g[t][j] = -M
                    break
            col = [[g[t][j]] for t in range(R)]
            u, d = shafts(col, i)
            up[j], dn[j] = u[0], d[0]
        g[i][j] = target[j] - up[j] - dn[j]
    return g


def wide_traps(R, C, K, M, pos=0.1):
    """one trap row (its value per plot counts the shafts) in a random grid"""
    return embed(R, C, ri(0, R - 1), trap_row(C, K, M // 2), M, pos)


def tall(R, C, M, pos):
    """long columns: rich and poor runs, so the best shafts stop at different depths"""
    g = [[0] * C for _ in range(R)]
    for j in range(C):
        i = 0
        while i < R:
            ln = ri(1, 4000)
            p = pos if rnd() < 0.5 else 1 - pos
            for t in range(i, min(R, i + ln)):
                g[t][j] = ri(1, M) if rnd() < p else -ri(0, M)
            i += ln
    return g


# samples
add(2, [[-5, -3, 4, -6, 1], [-5, -2, 3, -6, -1], [6, -6, -5, -5, -6], [3, -2, -1, -2, -5]])
add(3, [[-1, 2, -3, -10, -4, -1], [-2, -3, -6, 9, -3, -2], [-4, 1, -2, -12, -1, -3]])
add(1, [[-7, -3, -9], [-4, -8, -2]])
add(1, [[2], [-3], [4], [-1], [3]])
add(3, [[3, -1, -4, 2, 0, -2, 5], [-6, 4, 1, -3, 7, -5, -1], [2, -7, -2, 6, -4, 3, -3],
        [-1, 5, -6, -2, 1, -8, 4], [4, -3, 2, -5, -1, 6, -2]])

# hidden: small (the brute force tries everything on these)
add(1, [[5]])
add(1, [[-5]])
add(4, [[1, -2, 3, -4]])
add(2, [[-1000000, 1000000], [1000000, -1000000]])
add(3, rand_grid(4, 5, -3, 3))
add(3, wide_traps(3, 9, 3, 100))
add(5, mixed(6, 8, 10, 0.45))
add(7, mixed(30, 40, MAXA, 0.4))
add(12, wide_traps(8, 120, 12, MAXA))
add(1, tall(150, 6, MAXA, 0.4))

# hidden: big (R * C = 300 000, very wide or very tall)
add(1, [[ri(-MAXA, MAXA) for _ in range(MAXCELLS)]])
add(2000, [trap_row(MAXCELLS, 2000, MAXA)])
add(MAXCELLS // 2, [[ri(MAXA - 1000, MAXA) for _ in range(MAXCELLS)]])     # the whole row, near 3 * 10^11
add(500, wide_traps(2, 150000, 500, MAXA))
add(3000, wide_traps(3, 100000, 3000, MAXA))
add(40, mixed(3, 100000, MAXA, 0.5))
add(30000, mixed(4, 75000, MAXA, 0.6))
add(100, wide_traps(4, 75000, 100, MAXA))
add(1, rand_grid(4, 75000, -MAXA, -1))                                     # every plot loses
add(30000, rand_grid(4, 75000, -MAXA, -MAXA + 10))                        # a long tunnel that loses a lot
add(1, tall(MAXCELLS, 1, MAXA, 0.3))
add(1, [[ri(0, MAXA)] for _ in range(MAXCELLS)])                           # one column, near 3 * 10^11
add(2, tall(150000, 2, MAXA, 0.35))
add(3, [[ri(-MAXA, MAXA // 3) for _ in range(3)] for _ in range(100000)])
add(2, tall(100000, 3, MAXA, 0.4))
add(4, tall(75000, 4, MAXA, 0.6))
add(3, [[ri(MAXA // 2, MAXA) for _ in range(4)] for _ in range(75000)])    # everything is worth digging

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
