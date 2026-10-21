# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1002417)
MAXR = MAXC = 1000
MAXK = 5
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add_rows(rows, k):
    r, c = len(rows), len(rows[0])
    assert 1 <= r <= MAXR and 1 <= c <= MAXC and 0 <= k <= MAXK
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
for (r, c, p, k) in ((8, 8, 0.2, 0), (10, 12, 0.1, 2), (30, 40, 0.08, 3)):
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
g.emit(g.random_ice(), g.random_ice(), 4, seal=True)
g = Rink(200, 200)
g.sprinkle(0.03)
g.emit(g.random_ice(), g.free_mid(), 3)
g = Rink(300, 300)
last = bands(g, 0, 300, 3, 0.3, 2)
g.emit(band_cell(g, (0, 3)), band_cell(g, last), 4)
g = Rink(1, 1000)
for j in (3, 500, 501, 997):
    g.wall(0, j)
g.emit((0, 4), (0, 300), 0)

# ---------------------------------------------------------------- big hidden
R, C = MAXR, MAXC
# sealed goal in a large hall: everything else has to be explored
for p, k in ((0.01, 5),):
    g = Rink(R, C)
    g.sprinkle(p)
    g.emit(g.random_ice(), g.free_mid(), k, seal=True)

# open hall on top (wall density p), long serpentine below it, the goal in its last band
for hall, h, extra, stub, k, p in ((400, 2, 0.1, 1, 5, 0.006), (300, 3, 0.3, 2, 4, 0.006), (500, 2, 0.05, 0, 5, 0.006),
                                   (200, 2, 0.2, 1, 5, 0.006), (900, 3, 0.5, 1, 2, 0.003), (700, 2, 0.15, 1, 5, 0.006),
                                   (800, 2, 0.1, 1, 5, 0.006), (900, 2, 0.2, 1, 4, 0.006), (850, 3, 0.3, 1, 3, 0.006),
                                   (960, 2, 0.3, 1, 5, 0.004), (940, 2, 0.1, 1, 5, 0.005)):
    g = Rink(R, C)
    g.sprinkle(p, 0, hall)
    for j in range(C):
        g.wall(hall, j)
    for _ in range(3):
        g.ice(hall, ri(0, C - 1))
    last = bands(g, hall + 1, R, h, extra, stub)
    g.emit(g.random_ice(0, hall), band_cell(g, last), k)

# serpentine over the whole rink (rows or, transposed, columns)
for h, extra, stub, k, tr in ((2, 0.1, 1, 5, False), (3, 0.2, 2, 4, True), (2, 0.0, 0, 4, False),
                              (2, 0.4, 3, 5, True), (2, 0.1, 1, 0, False), (4, 0.3, 1, 5, False),
                              (2, 0.2, 2, 3, True)):
    g = Rink(R, C)
    last = bands(g, 0, R, h, extra, stub)
    s, t = band_cell(g, (0, h)), band_cell(g, last)
    if k == 0:      # no brakes: the goal is a place where the skater can stop
        t = (last[1] - 1, C - 1 if g.is_ice(last[1] - 1, C - 1) else 0)
    if tr:
        rows = [x.decode() for x in g.g]
        g.g = [bytearray("".join(rows[i][j] for i in range(R)).encode()) for j in range(C)]
        s, t = (s[1], s[0]), (t[1], t[0])
    g.emit(s, t, k)

# random rinks of different densities, the goal away from every wall
for p, k in ((0.008, 3),):
    g = Rink(R, C)
    g.sprinkle(p)
    g.emit(g.random_ice(0, 100, 0, 100), g.free_mid(900, 1000, 900, 1000), k)

# pillars on a lattice
g = Rink(R, C)
for i in range(3, R, 7):
    for j in range(ri(0, 10), C, 11):
        g.wall(i, j)
g.emit(g.random_ice(0, 50), g.free_mid(950, 1000), 5)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
