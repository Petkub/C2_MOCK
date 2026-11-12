# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1203061)
MAXRC, MAXM, MAXD = 1400, 10, 3000
LET = "ABCDEFGHIJ"
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(R, C, T, d, rows):
    M = len(d)
    assert 1 <= R <= MAXRC and 1 <= C <= MAXRC and 1 <= M <= MAXM and 1 <= T <= R * C
    assert all(0 <= x <= MAXD for x in d) and len(rows) == R
    ok = ("." + LET[:M]).encode()
    for s in rows:
        assert len(s) == C and s.encode().translate(None, ok) == b""
    tests.append(f"{R} {C} {M} {T}\n" + " ".join(map(str, d)) + "\n" + "\n".join(rows) + "\n")


def table(p, w):
    """byte -> character: '.' with probability about 1 - p, otherwise a model with weights w"""
    k = round(256 * p)
    tot = sum(w)
    out, acc = [], 0.0
    for j, x in enumerate(w):
        nxt = acc + k * x / tot
        out += [LET[j]] * (round(nxt) - round(acc))
        acc = nxt
    out = out[:k] + ["."] * (256 - len(out[:k]))
    return bytes("".join(out), "ascii")


def rand_rows(R, C, p, w):
    """each cell a sprinkler with probability p (model j with weight w[j]); fast: one big random number a row"""
    tb = table(p, w)
    return [random.getrandbits(8 * C).to_bytes(C, "little").translate(tb).decode() for _ in range(R)]


def area(R, C, r, c, d):
    """number of field cells within distance d of (r, c)"""
    s = 0
    for x in range(max(1, r - d), min(R, r + d) + 1):
        w = d - abs(x - r)
        s += min(C, c + w) - max(1, c - w) + 1
    return s


def pick_t(R, C, d, rows, f):
    """T near f times the average number of sprinklers on a cell (estimated from a sample of cells)"""
    cnt, tot, n = 0, 0, 0
    while n < 400 and cnt < 20000:
        cnt += 1
        r, c = ri(1, R), ri(1, C)
        ch = rows[r - 1][c - 1]
        if ch != ".":
            tot += area(R, C, r, c, d[ord(ch) - 65])
            n += 1
    if n == 0:
        return 1
    k = sum(len(s) - s.count(".") for s in rows)
    mean = tot / n * k / (R * C)
    return max(1, min(R * C, int(mean * f) + 1))


# samples
add(5, 6, 2, [1, 2, 0], ["......", ".A....", "...B..", "......", ".....C"])
add(3, 3, 1, [0, 1], ["A..", "...", "..B"])
add(4, 4, 3, [3, 1, 2], ["...C", ".A..", "..B.", "B..."])
add(1, 7, 2, [2, 10, 1], ["B..A..C"])
add(6, 5, 3, [2, 1, 6, 0], ["....C", ".....", "..A..", ".BA..", ".....", "D...."])

# hidden: small (brute checks these)
add(1, 1, 1, [5], ["."])
add(1, 1, 1, [0], ["A"])
for R, C, M, p, dmax, f in [(8, 8, 3, 0.3, 4, 1.0), (30, 20, 5, 0.2, 10, 1.0), (50, 70, MAXM, 0.1, 30, 0.7),
                            (1, 200, 4, 0.4, 50, 1.2), (200, 1, 4, 0.5, 60, 0.9), (100, 100, 8, 0.05, 120, 1.0),
                            (120, 150, MAXM, 0.6, 3000, 1.0)]:
    d = [ri(0, dmax) for _ in range(M)]
    rows = rand_rows(R, C, p, [1] * M)
    add(R, C, pick_t(R, C, d, rows, f), d, rows)
add(40, 40, 2, [0], rand_rows(40, 40, 0.5, [1]))                                   # radius 0 only
add(60, 60, 1, [MAXD, 0], ["A" + "." * 59] + ["." * 60] * 58 + ["." * 59 + "B"])
add(30, 40, 1, [7, 9], ["." * 40] * 30)                                            # no sprinkler at all


# hidden: big
def big(seed, R, C, d, p, w, f):
    random.seed(seed)
    rows = rand_rows(R, C, p, w)
    T = f if isinstance(f, int) else pick_t(R, C, d, rows, f)
    add(R, C, T, d, rows)


M = MAXRC
big(1206001, M, M, [ri(400, 1400) for _ in range(MAXM)], 0.9, [1] * MAXM, 1.0)
big(1206002, M, M, [ri(700, 1000) for _ in range(5)], 1.0, [1] * 5, 0.8)
big(1206003, M, M, [ri(1000, MAXD) for _ in range(10)], 0.7, [1] * 10, 0.9)
big(1206004, M, M, [ri(0, MAXD) for _ in range(MAXM)], 0.8, [1] * MAXM, 1.0)
big(1206005, M, M, [600, 700, 800], 0.95, [3, 2, 1], 1.3)
big(1206006, M, M, [ri(800, 1400) for _ in range(9)], 0.5, [1] * 9, 0.6)
big(1206007, M, M, [MAXD], 1.0, [1], M * M)                                         # every cell, all cover all
big(1206008, M, M, [0, 1, 2, 3, 2000], 0.85, [5, 5, 5, 5, 1], 1.0)
big(1206009, M, M, [ri(500, 900) for _ in range(MAXM)], 1.0, list(range(1, MAXM + 1)), 1.15)
big(1206010, M, M, [ri(0, 30) for _ in range(MAXM)], 0.9, [1] * MAXM, 1.0)             # small radii
big(1206011, M, M, [1399, 700, 350], 0.6, [1, 1, 1], 1)
big(1206012, M, M, [ri(500, 1200) for _ in range(8)], 0.9, [1] * 8, 0.9)
big(1206013, M, M, [ri(500, 1200) for _ in range(8)], 0.9, [1] * 8, 1.2)
big(1206014, M, M, [ri(1000, 2000) for _ in range(MAXM)], 0.3, [1] * MAXM, 0.95)
big(1206015, M, M, [2800, 1400, 0], 0.9, [1, 1, 1], 1.05)
random.seed(1206016)                                                                # sprinklers only near the border
rows = rand_rows(M, M, 0.9, [1] * 6)
rows = [s if r < 100 or r >= M - 100 else s[:100] + "." * (M - 200) + s[-100:] for r, s in enumerate(rows)]
d = [ri(1500, MAXD) for _ in range(6)]
add(M, M, pick_t(M, M, d, rows, 1.0), d, rows)
random.seed(1206017)                                                                # dense bands of rows
rows = [s if (r // 50) % 2 == 0 else "." * M for r, s in enumerate(rand_rows(M, M, 1.0, [1] * 4))]
d = [ri(600, 1200) for _ in range(4)]
add(M, M, pick_t(M, M, d, rows, 1.1), d, rows)
big(1206018, M, M, [ri(0, MAXD) for _ in range(MAXM)], 0.02, [1] * MAXM, 1.0)          # few sprinklers

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
