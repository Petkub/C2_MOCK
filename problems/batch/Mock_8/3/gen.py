# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A test = an N x M board of integers, N * M <= 200 000, |a| <= 10^9.
import os, random

random.seed(803)
rnd = random.random
MAXNM, MAXV = 200000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add_rows(rows):
    n, m = len(rows), len(rows[0])
    assert n >= 1 and m >= 1 and n * m <= MAXNM
    assert all(len(r) == m for r in rows)
    assert all(-MAXV <= x <= MAXV for r in rows for x in r)
    tests.append(f"{n} {m}\n" + "".join(" ".join(map(str, r)) + "\n" for r in rows))


def add(n, m, flat):
    assert len(flat) == n * m
    add_rows([flat[i * m:(i + 1) * m] for i in range(n)])


def unif(k, lo, hi):
    """k values uniform in lo..hi"""
    w = hi - lo + 1
    return [lo + int(rnd() * w) for _ in range(k)]


def plant(n, m, flat, r, c, r2, c2, lo, hi):
    """overwrite the cells of the channel with corner (r, c) and ends r2, c2 (0-based) by values in lo..hi"""
    for i in range(min(r, r2), max(r, r2) + 1):
        flat[i * m + c] = ri(lo, hi)
    for j in range(min(c, c2), max(c, c2) + 1):
        flat[r * m + j] = ri(lo, hi)


def one_line(n, m, flat, row, lo, hi):
    """row >= 0: that row gets values in lo..hi; row < 0: column -row-1 does"""
    if row >= 0:
        for j in range(m):
            flat[row * m + j] = ri(lo, hi)
    else:
        c = -row - 1
        for i in range(n):
            flat[i * m + c] = ri(lo, hi)


# ---- samples ----
add_rows([[3, -2, 5, -1, 4], [-6, 1, -3, 2, -5], [4, -1, 7, 6, 1], [-2, 8, -4, -3, 2]])
add_rows([[5, -3, 2], [-1, 4, -2], [6, -7, 3], [2, 1, -4]])
add_rows([[-4, 9, -1, 3, -8, 6], [2, -5, 7, -2, 4, -1]])
add_rows([[-2, 9, 8, -5, 2, 6], [9, -7, -9, 6, -1, 8], [-2, -3, 6, 8, 8, 6]])
add_rows([[-58, 12, -390, -777, -805], [-540, -323, -145, 187, 271], [-631, -712, -159, -617, 22],
          [-223, 445, 600, 515, 168], [296, -613, 308, -829, -864]])

# ---- hidden: small and medium (brute checks these) ----
add_rows([[-MAXV]])
add_rows([[MAXV, MAXV]])
add(3, 3, unif(9, -50, -1))                                        # every cell negative
add(6, 7, unif(42, -20, 15))
add(1, 20, unif(20, -MAXV, MAXV))
add(20, 1, unif(20, -MAXV, MAXV))
add(15, 20, unif(300, -MAXV, MAXV))
add(120, 150, unif(18000, -MAXV // 2, MAXV))                       # long arms
add(4, 5000, unif(20000, -MAXV, MAXV))

# ---- hidden: big (N * M = 200 000) ----
N = MAXNM
add(1, N, unif(N, -MAXV, MAXV))
add(N, 1, unif(N, -MAXV // 10 * 9, MAXV))
add(2, N // 2, unif(N, -MAXV, MAXV))
add(N // 2, 2, unif(N, -10 ** 4, -1))                              # every cell negative
add(4, N // 4, unif(N, -MAXV, MAXV // 10 * 9))
add(N // 4, 4, unif(N, -10 ** 6, 10 ** 6))
add(8, N // 8, unif(N, -MAXV, MAXV))
add(N // 8, 8, unif(N, -10 ** 5, 10 ** 5 + 3000))
add(400, 500, unif(N, -MAXV // 2, MAXV))                          # whole row + whole column
add(500, 400, unif(N, -MAXV, MAXV // 2))                          # short arms
add(200, 1000, unif(N, MAXV - 10 ** 6, MAXV))                     # every cell close to 10^9
add(1000, 200, unif(N, -MAXV, -1))                                # every cell negative
f = unif(N, -10 ** 6, -1)
one_line(100, 2000, f, 37, -3 * 10 ** 5, 10 ** 6)
add(100, 2000, f)                                                 # one good row: a straight channel
f = unif(N, -10 ** 6, -1)
one_line(2000, 100, f, -64, -3 * 10 ** 5, 10 ** 6)
add(2000, 100, f)                                                 # one good column
f = unif(N, -10 ** 4, 3000)
plant(250, 800, f, 210, 640, 30, 90, 0, 10 ** 4)
add(250, 800, f)                                                  # arms up and left
f = unif(N, -10 ** 4, 3000)
plant(800, 250, f, 120, 200, 760, 15, 0, 10 ** 4)
add(800, 250, f)                                                  # arms down and left
f = unif(300 * 666, -MAXV, MAXV // 3)
plant(300, 666, f, 250, 100, 20, 600, MAXV // 2, MAXV)
add(300, 666, f)                                                  # arms up and right (N * M = 199 800)
add(10, N // 10, unif(N, -MAXV, MAXV))
add(N // 20, 20, unif(N, -100, 100))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
