# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os
import random

random.seed(1102)
rnd = random.random
MAXRC = 1000
MAXK = 100000
tests = []
TR = str.maketrans("01", ".#")


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(rows, halls):
    r, c = len(rows), len(rows[0])
    assert 1 <= r <= MAXRC and 1 <= c <= MAXRC
    for row in rows:
        assert len(row) == c and set(row) <= set("#.")
    k = len(halls)
    assert 1 <= k <= MAXK
    assert len(set(halls)) == k
    for (a, b) in halls:
        assert 0 <= a < r and 0 <= b < c and rows[a][b] == "."
    out = [f"{r} {c} {k}"] + rows + [f"{a + 1} {b + 1}" for (a, b) in halls]
    tests.append("\n".join(out) + "\n")


def sample(text):
    lines = text.strip().split("\n")
    r, c, k = map(int, lines[0].split())
    rows = lines[1:1 + r]
    halls = [tuple(int(x) - 1 for x in lines[1 + r + i].split()) for i in range(k)]
    add(rows, halls)


def bits(c):
    return random.getrandbits(c)


def rand_grid(r, c, kind):
    """random walls with density 0, 1/8, 1/4, 3/8 or 1/2 (bit tricks, fast)"""
    rows = []
    for _ in range(r):
        if kind == "0":
            x = 0
        elif kind == "1/8":
            x = bits(c) & bits(c) & bits(c)
        elif kind == "1/4":
            x = bits(c) & bits(c)
        elif kind == "3/8":
            x = bits(c) & (bits(c) | bits(c))
        else:
            x = bits(c)
        rows.append(format(x, "0%db" % c).translate(TR))
    return rows


def small_rand(r, c, p):
    return ["".join("#" if rnd() < p else "." for _ in range(c)) for _ in range(r)]


def pick_halls(rows, k, avoid=()):
    """k distinct random open cells (not in avoid), in random order"""
    r, c = len(rows), len(rows[0])
    seen, halls = set(avoid), []
    while len(halls) < k:
        a, b = int(rnd() * r), int(rnd() * c)
        if rows[a][b] == "." and (a, b) not in seen:
            seen.add((a, b))
            halls.append((a, b))
    return halls


def snake(r, c):
    """one path of width 1: open rows joined alternately at the right and the left end; also its cell order"""
    rows, path = [], []
    for i in range(r):
        if i % 2 == 0:
            rows.append("." * c)
            path.extend((i, j) for j in (range(c) if i % 4 == 0 else range(c - 1, -1, -1)))
        elif i % 4 == 1:
            rows.append("#" * (c - 1) + ".")
            path.append((i, c - 1))
        else:
            rows.append("." + "#" * (c - 1))
            path.append((i, 0))
    return rows, path


def spiral(n):
    """an open spiral of width 1 with walls between the turns; also its cell order from the outside in"""
    g = [["#"] * n for _ in range(n)]
    r, c, d = 0, 0, 0
    dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
    g[0][0] = "."
    path = [(0, 0)]
    turns = 0
    while True:
        moved = False
        while True:
            nr, nc = r + dr[d], c + dc[d]
            ar, ac = nr + dr[d], nc + dc[d]
            if not (0 <= nr < n and 0 <= nc < n) or g[nr][nc] == ".":
                break
            if 0 <= ar < n and 0 <= ac < n and g[ar][ac] == ".":
                break
            r, c = nr, nc
            g[r][c] = "."
            path.append((r, c))
            moved = True
        if not moved:
            turns += 1
            if turns > 2:
                break
        else:
            turns = 0
        d = (d + 1) % 4
    return ["".join(x) for x in g], path


def comb(r, c):
    """a spine in column 1 and teeth (open rows) at every even row, walls between the teeth"""
    return ["." * c if i % 2 == 0 else "." + "#" * (c - 1) for i in range(r)]


def ladder(r, c, gap):
    """open rows every gap rows, joined by open columns at both ends; random extra rungs"""
    rows = []
    for i in range(r):
        if i % gap == 0:
            rows.append("." * c)
        else:
            row = ["#"] * c
            row[0] = row[c - 1] = "."
            for _ in range(2):
                row[int(rnd() * c)] = "."
            rows.append("".join(row))
    return rows


def maze(r, c, braid):
    """binary-tree maze on the cells with even coordinates; braid = chance to open one more wall"""
    g = [bytearray(b"#" * c) for _ in range(r)]
    for i in range(0, r, 2):
        gi = g[i]
        for j in range(0, c, 2):
            gi[j] = 46
            up, left = i >= 2, j >= 2
            if up and (not left or rnd() < 0.5):
                g[i - 1][j] = 46
            elif left:
                gi[j - 1] = 46
            if braid and rnd() < braid:
                if up and left:
                    if g[i - 1][j] == 46:
                        gi[j - 1] = 46
                    else:
                        g[i - 1][j] = 46
    return [x.decode() for x in g]


def rooms(r, c, h, w):
    """rooms h x w with walls of width 1 between them and one or two random doors in every wall"""
    g = [bytearray(b"." * c) for _ in range(r)]
    for i in range(h, r, h + 1):
        g[i][:] = b"#" * c
    for j in range(w, c, w + 1):
        for i in range(r):
            g[i][j] = 35
    for i in range(h, r, h + 1):
        for j0 in range(0, c, w + 1):
            for _ in range(ri(1, 2)):
                j = min(c - 1, j0 + int(rnd() * w))
                g[i][j] = 46
    for j in range(w, c, w + 1):
        for i0 in range(0, r, h + 1):
            for _ in range(ri(1, 2)):
                i = min(r - 1, i0 + int(rnd() * h))
                g[i][j] = 46
    return [x.decode() for x in g]


def transpose(rows):
    return ["".join(col) for col in zip(*rows)]


# samples
sample("""
5 7 3
.......
.#.#...
.#.##.#
...#...
##.....
1 1
1 7
5 6
""")
sample("""
4 6 2
..#...
..#.#.
###.#.
...#..
2 1
1 5
""")
sample("""
3 9 3
.........
.###.###.
.........
2 1
1 9
3 6
""")
sample("""
3 8 3
...#....
.#...##.
...#....
1 1
2 4
3 8
""")
sample("""
3 5 3
.....
.#.#.
.....
1 1
1 5
3 3
""")

# hidden: small (brute checks these)
add(["."], [(0, 0)])
add(["." * 40], [(0, 3), (0, 9), (0, 30), (0, 31)])                 # a corridor
g = comb(21, 15)
add(g, [(i, 0) for i in range(0, 21, 4)])                          # teeth that start at a tie
g = ladder(30, 30, 3)
add(g, pick_halls(g, 12))
g = small_rand(30, 30, 0.35)
add(g, pick_halls(g, 40))
g = maze(41, 61, 0.2)
add(g, pick_halls(g, 25))
g = small_rand(120, 150, 0.3)
add(g, pick_halls(g, 60))

# hidden: big
N = MAXRC
g = rand_grid(N, N, "3/8")
add(g, pick_halls(g, 1000))
g = rand_grid(N, N, "1/2")
add(g, pick_halls(g, MAXK))
g = rand_grid(N, N, "1/4")
add(g, pick_halls(g, 3))
g = rand_grid(N, N, "0")
add(g, [(0, 0), (N - 1, N - 1)])                                    # open field, two halls in opposite corners
g = rand_grid(N, N, "1/8")
add(g, sorted(pick_halls(g, MAXK)))                                 # halls listed in reading order
g, path = snake(N, N)
add(g, [path[2 * i] for i in range(20000)])                         # halls along the path, listed from its start
add(g, [path[len(path) // 2]])
g, path = spiral(N)
add(g, [path[i] for i in range(0, 60000, 3)])
g = comb(N, N)
h = [(i, 0) for i in range(0, N, 4)]
h += pick_halls(g, 200, h)
random.shuffle(h)
add(g, h)
g = transpose(comb(N, N))
h = [(0, j) for j in range(0, N, 4)]
h += pick_halls(g, 600, h)
random.shuffle(h)
add(g, h)
g = ladder(N, N, 4)
add(g, pick_halls(g, 40))
g = maze(N, N, 0)
add(g, pick_halls(g, 600))
g = maze(N, N - 1, 0.3)
add(g, pick_halls(g, 800))
g = rooms(N, N, 9, 14)
add(g, pick_halls(g, 300))
g = rand_grid(N, N, "0")
add(g, [(0, j) for j in range(N)])                                  # the whole first row, left to right
g = rand_grid(N, N, "3/8")
add(g, pick_halls(g, 2))
g = rand_grid(N, 997, "3/8")
add(g, pick_halls(g, 20000))
g = rand_grid(N, N, "1/4")
add(g, sorted(pick_halls(g, MAXK), key=lambda p: p[0] + p[1]))     # listed from the top-left corner outwards
# a wall across the middle with one gap; most halls on a diamond around the gap, all at the same distance from it,
# so the whole lower half behind the gap is a tie (except near one hall in the lower corner); a few halls farther out
W, G = N // 2, N // 2
g = ["." * N] * W + ["#" * G + "." + "#" * (N - G - 1)] + ["." * N] * (N - W - 1)
h = []
for r in range(W):
    b = r
    for c in sorted({G - b, G + b}):
        if 0 <= c < N and rnd() < 0.9:
            h.append((r, c))
seen = set(h)
target = len(h) + 300
while len(h) < target:
    r, c = int(rnd() * W), int(rnd() * N)
    if abs(r - W) + abs(c - G) > W + 2 and (r, c) not in seen:
        seen.add((r, c))
        h.append((r, c))
h.append((N - 1, N - 1))
random.shuffle(h)
add(g, h)

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(os.path.join("tests", f"{i:02d}.in"), "w") as f:
        f.write(t)
