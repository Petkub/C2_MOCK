# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(910101)
rnd = random.random
MAXRC = 1000
tests = []
TR = str.maketrans("01", ".#")


def add(rows):
    r, c = len(rows), len(rows[0])
    assert 1 <= r <= MAXRC and 1 <= c <= MAXRC
    for row in rows:
        assert len(row) == c and set(row) <= set("#.")
    tests.append(f"{r} {c}\n" + "\n".join(rows) + "\n")


def bits(c):
    return random.getrandbits(c)


def row_of(x, c):
    return format(x, "0%db" % c).translate(TR)


def rand_grid(r, c, kind):
    """random land with density 1/2, 9/16, 5/8, 7/16, 3/8 or 3/4 (bit tricks, fast)"""
    rows = []
    for _ in range(r):
        if kind == "1/2":
            x = bits(c)
        elif kind == "9/16":
            x = (bits(c) | bits(c)) & (bits(c) | bits(c))
        elif kind == "5/8":
            x = bits(c) | (bits(c) & bits(c))
        elif kind == "7/16":
            x = (bits(c) & bits(c)) | (bits(c) & bits(c))
        elif kind == "3/8":
            x = bits(c) & (bits(c) | bits(c))
        else:  # 3/4
            x = bits(c) | bits(c)
        rows.append(row_of(x, c))
    return rows


def small_rand(r, c, p):
    return ["".join("#" if rnd() < p else "." for _ in range(c)) for _ in range(r)]


def comb(r, c, gap=1):
    """full land rows, gap water rows between them, all teeth joined by column 0"""
    rows = []
    for i in range(r):
        rows.append("#" * c if i % (gap + 1) == 0 else "#" + "." * (c - 1))
    return rows


def transpose(rows):
    return ["".join(col) for col in zip(*rows)]


def snake(r, c):
    """one land path of width 1: full rows joined alternately at the right and the left end"""
    rows = []
    for i in range(r):
        if i % 2 == 0:
            rows.append("#" * c)
        elif i % 4 == 1:
            rows.append("." * (c - 1) + "#")
        else:
            rows.append("#" + "." * (c - 1))
    return rows


def spiral(n):
    """a land spiral of width 1 with water between the turns"""
    g = [["."] * n for _ in range(n)]
    r, c, d = 0, 0, 0
    dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
    g[0][0] = "#"
    turns = 0
    while True:
        moved = False
        while True:
            nr, nc = r + dr[d], c + dc[d]
            ar, ac = nr + dr[d], nc + dc[d]
            if not (0 <= nr < n and 0 <= nc < n) or g[nr][nc] == "#":
                break
            if 0 <= ar < n and 0 <= ac < n and g[ar][ac] == "#":
                break
            r, c = nr, nc
            g[r][c] = "#"
            moved = True
        if not moved:
            turns += 1
            if turns > 2:
                break
        else:
            turns = 0
        d = (d + 1) % 4
    return ["".join(x) for x in g]


def blocks(r, c, h, w):
    """land rectangles h x w separated by water lines of width 1"""
    rows = []
    for i in range(r):
        if i % (h + 1) == h:
            rows.append("." * c)
        else:
            rows.append("".join("." if j % (w + 1) == w else "#" for j in range(c)))
    return rows


def holes(r, c, p):
    """land with random water holes (density p)"""
    return ["".join("." if rnd() < p else "#" for _ in range(c)) for _ in range(r)]


def rings(n):
    """concentric square rings of land, water rings between them"""
    rows = []
    for i in range(n):
        rows.append("".join("#" if min(i, j, n - 1 - i, n - 1 - j) % 2 == 0 else "." for j in range(n)))
    return rows


def checker(r, c):
    return ["".join("#" if (i + j) % 2 == 0 else "." for j in range(c)) for i in range(r)]


def stripes(r, c, w):
    """vertical land stripes of width w with one water column between them; random gaps in the water"""
    rows = []
    for i in range(r):
        rows.append("".join("." if j % (w + 1) == w else "#" for j in range(c)))
    return rows


# samples
add(["##..#.",
     "#..##.",
     "..#...",
     "##..##",
     "#..#.#"])
add(["#.#.#",
     ".#.#.",
     "#.#.#"])
add(["###..###",
     "..#..#..",
     "..#.##.#",
     "###....."])
add(["..#..##",
     "#.#....",
     "#...###",
     ".##.#..",
     "....#.#",
     "###...#"])
add([".#..#..#.",
     "##.##.###",
     "...#.....",
     "#..#.###.",
     "##...#.##"])
# hidden: small (brute checks these)
add(["#"])
add(["."])
add(["###", "###", "###", "###"])                  # no water: nothing to fill
add(["....", "....", "....", "...."])              # no land
add(["#.##.###.####.#####"])
add(transpose(["##.#.###..#.##.#"]))
add(["##.##", "#####", "##.##"])                    # water cells inside one island
add(small_rand(20, 20, 0.6))
add(comb(9, 11))
add(blocks(17, 23, 3, 4))
# hidden: big (1000 x 1000)
N = MAXRC
add(rand_grid(N, N, "1/2"))
add(rand_grid(N, N, "9/16"))
add(rand_grid(N, N, "5/8"))
add(rand_grid(N, N, "7/16"))
add(rand_grid(N, N, "3/4"))
add(comb(N, N))                                     # one comb island, every water cell touches it twice
add(transpose(comb(N, N, 2)))
add(snake(N, N))                                    # one path of length about N * N / 2
add(spiral(N))
add(holes(N, N, 0.12))                              # one island with many lakes
add(holes(N, N, 0.3))
add(checker(N, N))
add(blocks(N, N, 9, 9))
add(stripes(N, N, 2))
add(rings(N))
add(["#" * N] * N)                                  # no water
g = ["#" * N] * N
g[N // 3] = "#" * 700 + "." + "#" * (N - 701)
add(g)                                              # one water cell
add(["." * N] * N)                                  # no land
add(rand_grid(N, 777, "9/16"))

for t in tests:
    assert t.endswith("\n") and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
