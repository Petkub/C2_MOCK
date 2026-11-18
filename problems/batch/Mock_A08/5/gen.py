# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(70805)
rnd = random.random
MAXC = 1000000          # N * M
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(g):
    g = [row.decode() if isinstance(row, bytearray) else row for row in g]
    n, m = len(g), len(g[0])
    assert 1 <= n and 1 <= m and n * m <= MAXC
    for row in g:
        assert len(row) == m and set(row) <= set(".#ABCD")
    tests.append("%d %d\n%s\n" % (n, m, "\n".join(g)))


def walls(n, m, mode):
    """n x m grid of bytearrays; mode = number of random bit masks ANDed (wall share 1/2^mode), 0 = no walls"""
    g = []
    for _ in range(n):
        if mode == 0:
            g.append(bytearray(b"." * m))
            continue
        x = random.getrandbits(m)
        for _ in range(mode - 1):
            x &= random.getrandbits(m)
        s = format(x, "0%db" % m)[-m:] if m > 0 else ""
        g.append(bytearray(s.translate(str.maketrans("01", ".#")).encode()))
    return g


def put(g, ch, cnt, r0=0, r1=None, c0=0, c1=None, over=b"."):
    """put `cnt` stations `ch` on random cells of the rectangle that hold a character in `over`"""
    n, m = len(g), len(g[0])
    r1 = n - 1 if r1 is None else r1
    c1 = m - 1 if c1 is None else c1
    tries = 0
    while cnt > 0 and tries < 50 * (cnt + 10):
        tries += 1
        r, c = ri(r0, r1), ri(c0, c1)
        if g[r][c] in over:
            g[r][c] = ord(ch)
            cnt -= 1


def box(g, r0, r1, c0, c1):
    """walls on the border of the rectangle (rows r0..r1, cols c0..c1)"""
    for c in range(c0, c1 + 1):
        g[r0][c] = g[r1][c] = ord("#")
    for r in range(r0, r1 + 1):
        g[r][c0] = g[r][c1] = ord("#")


def clear(g, r0, r1, c0, c1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            g[r][c] = ord(".")


def snake(n, m, gapw=1):
    """corridors on even rows; each odd row is a wall with one gap, alternating right and left"""
    g = walls(n, m, 0)
    for r in range(1, n, 2):
        g[r] = bytearray(b"#" * m)
        side = (r // 2) % 2
        for k in range(gapw):
            g[r][m - 1 - k if side == 0 else k] = ord(".")
    return g


def rand_small(n, m, wall, lt):
    g = []
    for _ in range(n):
        row = ""
        for _ in range(m):
            x = rnd()
            row += "#" if x < wall else ("ABCD"[int(rnd() * 4)] if x < wall + lt else ".")
        g.append(row)
    return g


# samples
add(["A..#..C", ".#B#.#.", ".#..#B.", "D...A..", "..C#..D"])
add(["A.B#C.", "...#..", "D.##.D"])
add(["BDA..CB.ADCA"])
add(["..C#A....", ".#.#.##B.", "B#D..#.#.", ".##.#C..#", "A..#..#D.", ".C...B..."])
add(["AB", "DC"])

# hidden: small (brute checks these)
add(["A"])
add(["ABCD"])
add(["D", "C", "B", "A"])
add(["A#BCD"])
add(rand_small(8, 9, 0.2, 0.3))
add(rand_small(12, 15, 0.3, 0.15))
add(rand_small(30, 30, 0.25, 0.05))
add(rand_small(1, 200, 0.0, 0.08))
add(rand_small(40, 50, 0.35, 0.03))

# hidden: big (N * M = 1 000 000)
# 1) many A in the bottom-left, a far B at the top-left that is reached first in row order, the good B near the A
g = walls(1000, 1000, 4)
clear(g, 0, 999, 0, 0)
put(g, "A", 1500, 900, 999, 0, 60)
g[0][0] = ord("B")
g[999][3] = ord("B")
put(g, "C", 5, 300, 400, 0, 3)
put(g, "D", 40, 0, 999, 900, 999)
add(g)

# 2) greedy trap: the nearest B (left of the A) is far from every C; a slightly farther B has C next to it
g = walls(1000, 1000, 4)
put(g, "A", 1000, 450, 550, 40, 60, over=b".#")
put(g, "B", 4, 480, 520, 0, 4, over=b".#")
clear(g, 495, 505, 98, 106)
g[500][100] = ord("B")
g[500][102] = ord("C")
put(g, "D", 6, 0, 999, 950, 999)
add(g)

# 3) random woods
g = walls(1000, 1000, 2)
for ch, k in (("A", 1500), ("B", 50), ("C", 50), ("D", 3)):
    put(g, ch, k)
add(g)
g = walls(1000, 1000, 3)
for ch, k in (("A", 2000), ("B", 5), ("C", 5), ("D", 5)):
    put(g, ch, k)
add(g)
g = walls(500, 2000, 3)
put(g, "A", 1500, 0, 499, 0, 300)
for ch, k in (("B", 30), ("C", 30), ("D", 2)):
    put(g, ch, k, 0, 499, 300, 1999)
add(g)
g = walls(1000, 1000, 0)
for ch, k in (("A", 2000), ("B", 3), ("C", 3), ("D", 3)):
    put(g, ch, k)
add(g)

# 4) snakes: very long walks
g = snake(1000, 1000)
for ch, k in (("A", 1500), ("B", 20), ("C", 20), ("D", 2)):
    put(g, ch, k)
add(g)
g = snake(999, 1001, 2)
put(g, "A", 1500, 0, 300)
put(g, "B", 10, 600, 998)
put(g, "C", 10, 0, 400)
put(g, "D", 1, 700, 998)
add(g)

# 5) thin grids
g = walls(1, 1000000, 0)
for ch, k in (("A", 1500), ("B", 40), ("C", 40), ("D", 4)):
    put(g, ch, k)
add(g)
g = walls(2, 500000, 3)
g[1] = bytearray(b"." * 500000)
for ch, k in (("A", 1500), ("B", 60), ("C", 60), ("D", 10)):
    put(g, ch, k)
add(g)
g = [bytearray(b".") for _ in range(1000000)]
put(g, "A", 1500, 0, 300000)
put(g, "B", 20, 0, 999999)
put(g, "C", 20, 0, 999999)
put(g, "D", 3, 0, 999999)
add(g)

# 6) no answer
g = walls(1000, 1000, 3)
for ch, k in (("A", 1500), ("B", 40), ("C", 40)):
    put(g, ch, k, 0, 899)
box(g, 950, 999, 900, 999)
put(g, "D", 20, 951, 998, 901, 998)
add(g)
g = walls(1000, 1000, 4)
for ch, k in (("A", 1500), ("B", 40), ("D", 40)):
    put(g, ch, k)
add(g)

# 7) more traps for the row-order queue and for the greedy choice
g = walls(500, 2000, 4)
for r in range(500):
    g[r][0] = ord(".")
put(g, "A", 1500, 400, 499, 0, 80)
g[0][0] = ord("B")
g[0][1] = ord("B")
g[499][2] = ord("B")
put(g, "C", 4, 150, 250, 0, 2)
put(g, "D", 10, 0, 499, 1800, 1999)
add(g)
g = walls(1, 1000000, 0)
put(g, "A", 300, 0, 0, 500000, 500600)
put(g, "B", 3, 0, 0, 499900, 499950)
g[0][500700] = ord("B")
g[0][500703] = ord("C")
put(g, "C", 3, 0, 0, 0, 1000)
put(g, "D", 2, 0, 0, 990000, 999999)
add(g)
g = walls(1000, 1000, 3)
put(g, "A", 1500)
put(g, "B", 300)
put(g, "C", 300)
put(g, "D", 300)
add(g)
g = walls(1000, 1000, 3)
for r in range(1000):
    g[r][999] = ord(".")
put(g, "A", 1500, 880, 999, 900, 999)
g[0][999] = ord("B")
g[999][990] = ord("B")
put(g, "C", 6, 250, 420, 996, 999)
put(g, "D", 5, 0, 200, 0, 100)
add(g)
g = walls(2000, 500, 0)
put(g, "A", 1500, 1700, 1999, 0, 499)
put(g, "B", 5, 0, 30, 0, 499)
put(g, "B", 5, 1650, 1700, 0, 499)
put(g, "C", 8, 700, 900, 0, 499)
put(g, "D", 4, 0, 100, 0, 499)
add(g)
# a small copy of trap 1 (brute checks it)
g = walls(60, 60, 4)
clear(g, 0, 59, 0, 0)
put(g, "A", 40, 52, 59, 0, 8)
g[0][0] = ord("B")
g[59][2] = ord("B")
put(g, "C", 2, 18, 25, 0, 1)
put(g, "D", 3, 0, 59, 50, 59)
add(g)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
