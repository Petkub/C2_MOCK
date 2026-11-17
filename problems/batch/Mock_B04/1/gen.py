# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(611606)
rnd = random.random
MAXR = MAXC = 300
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(g):
    R, C = len(g), len(g[0])
    assert 1 <= R <= MAXR and 1 <= C <= MAXC and R * C >= 2
    assert all(len(row) == C and set(row) <= set(".#GST") for row in g)
    assert sum(row.count("S") for row in g) == 1 and sum(row.count("T") for row in g) == 1
    tests.append(f"{R} {C}\n" + "\n".join(g) + "\n")


def field(R, C, hole, glass):
    """random rows: '#' with probability hole, 'G' with probability glass (in 1/256 steps), else '.'"""
    h, gl = int(hole * 256), int(glass * 256)
    table = bytes((35 if b < h else 71 if b < h + gl else 46) for b in range(256))
    return [bytearray(random.getrandbits(8 * C).to_bytes(C, "little").translate(table)) for _ in range(R)]


def maze(R, C, w, wall, glass=0.0, extra=0.0):
    """corridors w cells wide between walls `wall` cells thick (a random spanning tree of the rooms,
    plus a fraction `extra` of further openings); glass sprinkled on the floor"""
    p = w + wall
    nr, nc = (R - wall) // p, (C - wall) // p
    g = [bytearray(b"#" * C) for _ in range(R)]

    def room(i, j):
        for r in range(wall + i * p, wall + i * p + w):
            g[r][wall + j * p: wall + j * p + w] = b"." * w

    def link(i, j, k, l):
        r0, c0 = wall + min(i, k) * p, wall + min(j, l) * p
        if i != k:
            for r in range(r0 + w, r0 + p):
                g[r][c0: c0 + w] = b"." * w
        else:
            for r in range(r0, r0 + w):
                g[r][c0 + w: c0 + p] = b"." * wall

    for i in range(nr):
        for j in range(nc):
            room(i, j)
    seen = [[False] * nc for _ in range(nr)]
    stack = [(0, 0)]
    seen[0][0] = True
    while stack:
        i, j = stack[-1]
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= i + di < nr and 0 <= j + dj < nc and not seen[i + di][j + dj]]
        if not nb:
            stack.pop()
            continue
        k, l = nb[int(rnd() * len(nb))]
        seen[k][l] = True
        link(i, j, k, l)
        stack.append((k, l))
    for _ in range(int(extra * nr * nc)):
        i, j = ri(0, nr - 1), ri(0, nc - 1)
        if rnd() < 0.5 and i + 1 < nr:
            link(i, j, i + 1, j)
        elif j + 1 < nc:
            link(i, j, i, j + 1)
    if glass > 0:
        for row in g:
            for c in range(C):
                if row[c] == 46 and rnd() < glass:
                    row[c] = 71
    return g


def comb(R, C, k, gw, hole, glass):
    """a random field split by walls of holes on every k-th row, each with a gap of width gw,
    at the right and left end in turn (a long snake path)"""
    g = field(R, C, hole, glass)
    side = 0
    for r in range(k - 1, R - 1, k):
        g[r] = bytearray(b"#" * C)
        lo = C - gw if side == 0 else 0
        for rr in range(max(0, r - 2), min(R, r + 3)):
            if rr != r - 1 + k and rr != r + 1 - k:
                g[rr][lo: lo + gw] = b"." * gw
        side ^= 1
    return g


def place(g, s, t):
    (sr, sc), (tr, tc) = s, t
    g[sr][sc] = ord("S")
    g[tr][tc] = ord("T")
    return [row.decode() for row in g]


def floor_near(g, r, c):
    """the floor cell ('.') nearest to (r, c) by scanning outwards"""
    R, C = len(g), len(g[0])
    for d in range(max(R, C)):
        for rr in range(max(0, r - d), min(R, r + d + 1)):
            for cc in (c - d, c + d) if d else (c,):
                if 0 <= cc < C and g[rr][cc] == 46:
                    return rr, cc
        for cc in range(max(0, c - d), min(C, c + d + 1)):
            for rr in (r - d, r + d):
                if 0 <= rr < R and g[rr][cc] == 46:
                    return rr, cc
    raise ValueError("no floor")


def clear(g, r, c, k):
    """a (2k+1) x (2k+1) patch of plain floor around (r, c)"""
    for rr in range(max(0, r - k), min(len(g), r + k + 1)):
        for cc in range(max(0, c - k), min(len(g[0]), c + k + 1)):
            g[rr][cc] = 46


def corners(g, far=True, k=2):
    """S near the top-left corner, T near the bottom-right one (far) or at a random place;
    k > 0: plain floor around both"""
    R, C = len(g), len(g[0])
    s = (ri(0, min(R - 1, 3)), ri(0, min(C - 1, 3)))
    t = (ri(max(0, R - 4), R - 1), ri(max(0, C - 4), C - 1)) if far else (ri(0, R - 1), ri(0, C - 1))
    if k:
        clear(g, *s, k)
        clear(g, *t, k)
    s, t = floor_near(g, *s), floor_near(g, *t)
    if s == t:
        t = floor_near(g, R - 1 - s[0], C - 1 - s[1])
    assert s != t
    return place(g, s, t)


def maze_ends(g, w, wall):
    """S in the first room, T in the last room of a maze (both on plain floor)"""
    R, C = len(g), len(g[0])
    p = w + wall
    nr, nc = (R - wall) // p, (C - wall) // p
    s = (wall + ri(0, w - 1), wall + ri(0, w - 1))
    t = (wall + (nr - 1) * p + ri(0, w - 1), wall + (nc - 1) * p + ri(0, w - 1))
    return place(g, s, t)


def lock_target(g, t):
    """make T impossible to stand on: the cells two steps away in every direction are holes"""
    tr, tc = t
    for dr, dc in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        r, c = tr + dr, tc + dc
        if 0 <= r < len(g) and 0 <= c < len(g[0]):
            g[r][c] = 35


# samples
add(["S....#", "..G...", "......", ".#..G.", "....T."])
add(["S..G..T"])
add(["S.G..", ".....", ".....", "..T..", "....."])
add(["..#.....", ".S#..G..", "..#.....", "........", ".....#T."])
add(["S..G...", "G.G..T.", "......."])
# hidden: small (brute checks these)
add(["ST"])
add(["S", ".", ".", "T"])
add(corners(field(12, 15, 0.15, 0.2)))
add(corners(field(30, 30, 0.2, 0.25), False))
add(maze_ends(maze(41, 62, 1, 2, 0.02, 0.2), 1, 2))
add(maze_ends(maze(70, 70, 2, 1, 0.05, 0.1), 2, 1))
add(corners(field(60, 80, 0.1, 0.35)))
# hidden: big
add(corners(field(300, 300, 0.0, 0.0)))                        # empty floor
add(corners(field(300, 300, 0.15, 0.2)))
add(corners(field(300, 300, 0.2, 0.1)))
add(corners(field(300, 300, 0.05, 0.4)))
add(corners(field(300, 300, 0.12, 0.3), False))
add(corners(field(300, 300, 0.18, 0.18)))
add(maze_ends(maze(300, 300, 1, 2, 0.0, 0.3), 1, 2))                   # rails: rooms one cell wide, links two long
add(maze_ends(maze(300, 300, 1, 2, 0.0, 0.0), 1, 2))                    # a tree of rails
add(maze_ends(maze(300, 300, 2, 1, 0.05, 0.05), 2, 1))
add(maze_ends(maze(299, 300, 3, 1, 0.3, 0.02), 3, 1))
add(maze_ends(maze(300, 297, 2, 2, 0.1, 0.2), 2, 2))
g = field(300, 300, 0.1, 0.2)
clear(g, 0, 0, 2)
clear(g, 295, 295, 4)
lock_target(g, (295, 295))
add(place(g, (0, 0), (295, 295)))                                # T cannot be stood on: -1
add(corners(field(300, 300, 0.2, 0.0)))
add(["S" + "".join("G" if i % 3 and rnd() < 0.3 else "." for i in range(1, 297)) + "T.."])
add(list("S" + "." * 298 + "T"))                              # 299 is not a multiple of 3: -1
add(corners(field(2, 300, 0.0, 0.3)))
add(corners(field(150, 300, 0.15, 0.3), False))
add(corners(field(300, 300, 0.0, 0.5)))
add(corners(comb(300, 300, 5, 3, 0.0, 0.15)))                  # a snake path through gaps
add(corners(comb(300, 300, 8, 4, 0.01, 0.2), False))
g = field(300, 300, 0.1, 0.25)
for r in range(180, 240):                                       # T inside a closed room
    g[r][180] = g[r][240] = 35
g[180][180:241] = g[240][180:241] = b"#" * 61
clear(g, 0, 0, 2)
clear(g, 210, 210, 3)
add(place(g, (0, 0), (210, 210)))
add(maze_ends(maze(300, 300, 2, 1, 0.03, 0.4), 2, 1))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
