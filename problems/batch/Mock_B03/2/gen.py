# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1002417)
MAXRC = 300000      # R * C at most this
MAXK = 2
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add_rows(rows, k):
    r, c = len(rows), len(rows[0])
    assert 1 <= r and 1 <= c and r * c <= MAXRC and 0 <= k <= MAXK
    assert all(len(x) == c and set(x) <= set(".#ST") for x in rows)
    text = "".join(rows)
    assert text.count("S") == 1 and text.count("T") == 1
    tests.append(f"{r} {c} {k}\n" + "\n".join(rows) + "\n")


class Rink:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.g = [bytearray(b"." * c) for _ in range(r)]

    def wall(self, i, j):
        self.g[i][j] = 35          # '#'

    def ice(self, i, j):
        self.g[i][j] = 46          # '.'

    def is_ice(self, i, j):
        return 0 <= i < self.r and 0 <= j < self.c and self.g[i][j] == 46

    def sprinkle(self, p, i0=0, i1=None, j0=0, j1=None):
        """about p of the cells in rows i0..i1-1, columns j0..j1-1 become walls"""
        i1 = self.r if i1 is None else i1
        j1 = self.c if j1 is None else j1
        cnt = int(p * (i1 - i0) * (j1 - j0))
        for _ in range(cnt):
            self.wall(ri(i0, i1 - 1), ri(j0, j1 - 1))

    def random_ice(self, i0=0, i1=None, j0=0, j1=None):
        i1 = self.r if i1 is None else i1
        j1 = self.c if j1 is None else j1
        while True:
            i, j = ri(i0, i1 - 1), ri(j0, j1 - 1)
            if self.g[i][j] == 46:
                return i, j

    def free_mid(self, i0=0, i1=None, j0=0, j1=None):
        """an ice cell whose four neighbours are ice too (no natural stop there)"""
        for _ in range(100000):
            i, j = self.random_ice(i0, i1, j0, j1)
            if all(self.is_ice(i + a, j + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                return i, j
        return self.random_ice(i0, i1, j0, j1)

    def emit(self, s, t, k, seal=False):
        assert s != t
        if seal:
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= t[0] + a < self.r and 0 <= t[1] + b < self.c and (t[0] + a, t[1] + b) != s:
                    self.wall(t[0] + a, t[1] + b)
        self.g[s[0]][s[1]] = 83    # 'S'
        self.g[t[0]][t[1]] = 84    # 'T'
        add_rows([x.decode() for x in self.g], k)


def bands(g, i0, i1, h, extra, top_stub):
    """rows i0..i1-1 become a serpentine: bands of h >= 2 ice rows, each followed by a wall row with one
    gap the skater can stop above without a brake (at an end, or in the middle with a single wall next to
    it in the bottom ice row) and, with probability extra, a second gap in the middle (only a brake
    stops above it); top_stub = number of single walls in the top row of every band.
    Returns the rows of the last band."""
    top = i0
    last = (i0, min(i1, i0 + h))
    while top < i1:
        bot = min(i1, top + h) - 1
        last = (top, bot + 1)
        for _ in range(top_stub):
            j = ri(1, g.c - 2)
            if bot > top and (g.is_ice(top - 1, j) is False or top == i0):
                g.wall(top, j)
        w = bot + 1
        if w >= i1:
            break
        for j in range(g.c):
            g.wall(w, j)
        if rnd() < 0.35:
            g.ice(w, 0 if rnd() < 0.5 else g.c - 1)
        else:
            j = ri(2, g.c - 3)
            g.ice(w, j)
            x = j + (1 if rnd() < 0.5 else -1)
            g.wall(bot, x)
            for y in (x - 1, x, x + 1):
                if top < bot:
                    g.ice(top, y)   # the band stays open above (and diagonally above) the single wall
        if rnd() < extra:
            g.ice(w, ri(1, g.c - 2))
        top = w + 1
    return last


def band_cell(g, rows, end_ok=False):
    i0, i1 = rows
    cells = [(i, j) for i in range(i0, i1) for j in range(g.c) if g.g[i][j] == 46 and (end_ok or 0 < j < g.c - 1)]
    return random.choice(cells)


# ---------------------------------------------------------------- samples
add_rows([".S....", "....#.", "...#..", "#..T..", "#....."], 1)
add_rows(["S..T.."], 0)
add_rows(["S..T.."], 2)
add_rows(["..#....", "S...#..", "...#...", ".....#.", "#T.....", "....#.."], 2)
add_rows(["........", ".#..#...", "....S#..", "##......", "......#.", ".T..#..."], 1)

# ---------------------------------------------------------------- small hidden (brute checks these)
add_rows(["ST"], 0)
for (r, c, p, k) in ((8, 8, 0.2, 0), (10, 12, 0.1, 2), (30, 40, 0.08, 2)):
    g = Rink(r, c)
    g.sprinkle(p)
    s = g.random_ice()
    t = g.free_mid() if rnd() < 0.7 else g.random_ice()
    if t == s:
        t = g.random_ice()
    g.emit(s, t, k)
g = Rink(31, 40)
last = bands(g, 0, 31, 2, 0.5, 1)
g.emit(band_cell(g, (0, 2)), band_cell(g, last), 2)
g = Rink(60, 50)
g.sprinkle(0.04)
g.emit(g.random_ice(), g.random_ice(), 1, seal=True)
g = Rink(200, 200)
g.sprinkle(0.03)
g.emit(g.random_ice(), g.free_mid(), 2)
g = Rink(300, 300)
last = bands(g, 0, 300, 3, 0.3, 2)
g.emit(band_cell(g, (0, 3)), band_cell(g, last), 2)
g = Rink(1, 1000)
for j in (3, 500, 501, 997):
    g.wall(0, j)
g.emit((0, 4), (0, 300), 0)

# ---------------------------------------------------------------- big hidden (R * C close to 300 000)
# Long thin rinks: slides are tens of thousands of cells long, so walking every slide again from every stop
# (O(K R C (R + C))) is far too slow. The no-brake serpentine is smaller: without brakes there are few stops.


def transpose(g, s, t):
    rows = [x.decode() for x in g.g]
    g.r, g.c = g.c, g.r
    g.g = [bytearray("".join(rows[i][j] for i in range(g.c)).encode()) for j in range(g.r)]
    return (s[1], s[0]), (t[1], t[0])


# sealed goal in an empty rink (long slides): everything else has to be explored
for (R, C) in ((3, 100000), (30, 10000), (12000, 25)):
    g = Rink(R, C)
    g.emit(g.random_ice(), g.free_mid(), 2, seal=True)

# open hall on top (wall density p), long serpentine below it, the goal in its last band
for R, C, hall, h, extra, stub, k, p, tr in ((25, 12000, 10, 2, 0.1, 1, 2, 0.0005, False),
                                             (15, 20000, 5, 2, 0.3, 0, 2, 0.002, False),
                                             (20, 15000, 6, 2, 0.05, 0, 2, 0.002, True),
                                             (12, 25000, 4, 2, 0.2, 0, 2, 0.002, False),
                                             (24, 12500, 8, 3, 0.3, 0, 2, 0.002, True),
                                             (16, 18750, 6, 2, 0.15, 0, 2, 0.001, False),
                                             (20, 15000, 8, 2, 0.1, 0, 2, 0.002, True)):
    g = Rink(R, C)
    g.sprinkle(p, 0, hall)
    for j in range(C):
        g.wall(hall, j)
    for _ in range(3):
        g.ice(hall, ri(0, C - 1))
    last = bands(g, hall + 1, R, h, extra, stub)
    s, t = g.random_ice(0, hall), band_cell(g, last)
    if tr:
        s, t = transpose(g, s, t)
    g.emit(s, t, k)

# serpentine over the whole rink (rows or, transposed, columns)
for R, C, h, extra, stub, k, tr in ((30, 10000, 2, 0.1, 1, 2, False), (15, 20000, 3, 0.2, 0, 1, True),
                                    (20, 15000, 2, 0.0, 0, 2, False), (12, 25000, 2, 0.4, 0, 2, True),
                                    (20, 1500, 2, 0.1, 1, 0, False), (24, 12500, 4, 0.3, 0, 2, False),
                                    (16, 18750, 2, 0.2, 0, 1, True)):
    g = Rink(R, C)
    last = bands(g, 0, R, h, extra, stub)
    s, t = band_cell(g, (0, h)), band_cell(g, last)
    if k == 0:      # no brakes: the goal is a place where the skater can stop
        t = (last[1] - 1, C - 1 if g.is_ice(last[1] - 1, C - 1) else 0)
    if tr:
        s, t = transpose(g, s, t)
    g.emit(s, t, k)

# nearly empty rinks, the goal away from every wall
for R, C, p in ((3, 100000, 0.00002), (10, 30000, 0.00005), (30000, 10, 0.00005)):
    g = Rink(R, C)
    g.sprinkle(p)
    g.emit(g.random_ice(0, 5, 0, 5), g.free_mid(R - 5, R, C - 5, C), 2)

# pillars on a sparse lattice (slides of about 1000 cells between them)
g = Rink(30, 10000)
for i in range(3, g.r, 7):
    for j in range(ri(0, 1000), g.c, 1000):
        g.wall(i, j)
g.emit(g.random_ice(0, 10), g.free_mid(g.r - 10, g.r), 2)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
