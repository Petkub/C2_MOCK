import random, os
random.seed(2602)
os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples ----
cases.append((1, ["S..#.", "##.#.", "...#.", ".###.", "....T"]))
cases.append((0, ["S#T", ".#.", "..."]))
cases.append((1, ["S##T"]))
cases.append((2, ["S##T"]))
cases.append((1, ["S.#.", ".###", "..#T"]))
# ---- small random ----
def rnd(R, C, H, p, place="random"):
    g = [["#" if random.random() < p else "." for _ in range(C)] for _ in range(R)]
    if place == "corner":
        s, t = (0, 0), (R - 1, C - 1)
    else:
        s, t = random.sample([(i, j) for i in range(R) for j in range(C)], 2)
    g[s[0]][s[1]] = "S"; g[t[0]][t[1]] = "T"
    return (H, ["".join(r) for r in g])
for _ in range(5):
    cases.append(rnd(random.randint(2, 6), random.randint(2, 6), random.randint(0, 3), 0.5))
# ---- large ----
def near(R, C, H, p, dist):
    g = [["#" if random.random() < p else "." for _ in range(C)] for _ in range(R)]
    sr, sc = random.randrange(R), random.randrange(C)
    while True:
        tr, tc = sr + random.randint(-dist, dist), sc + random.randint(-dist, dist)
        if 0 <= tr < R and 0 <= tc < C and (tr, tc) != (sr, sc): break
    g[sr][sc] = "S"; g[tr][tc] = "T"
    return (H, ["".join(r) for r in g])
cases.append(rnd(500, 500, 10, 0.3, "corner"))
cases.append(rnd(500, 500, 10, 0.4, "corner"))
cases.append(rnd(500, 500, 0, 0.25, "corner"))
cases.append(near(500, 500, 6, 0.5, 40))
cases.append(near(500, 500, 10, 0.55, 30))
g = [["#"] * 500 for _ in range(500)]
g[250][250] = "S"; g[250][261] = "T"
cases.append((10, ["".join(x) for x in g]))                     # all walls, exactly 10 between
row = ["."] * 500
for c in random.sample(range(1, 499), 10): row[c] = "#"
row[0] = "S"; row[499] = "T"
cases.append((10, ["".join(row)]))
col = ["."] * 500
for c in random.sample(range(1, 499), 6): col[c] = "#"
col[0] = "T"; col[499] = "S"
cases.append((5, col))
# serpentine maze: thin walls, hammer shortcuts through them
def snake(n, H, gaps=1):
    g = [["."] * n for _ in range(n)]
    for r in range(1, n, 2):
        for c in range(n):
            g[r][c] = "#"
        hole = n - 1 if (r // 2) % 2 == 0 else 0
        g[r][hole] = "."
    g[0][0] = "S"; g[n - 1][n - 1] = "T"
    return (H, ["".join(x) for x in g])
cases.append(snake(499, 0))
cases.append(snake(499, 10))
cases.append(snake(499, 7))
# thick walls: walls 2 cells thick need 2 hammers each
def thick(n, H):
    g = [["."] * n for _ in range(n)]
    for r in range(2, n - 1, 4):
        for c in range(n):
            g[r][c] = "#"; g[r + 1][c] = "#"
        hole = n - 1 if (r // 4) % 2 == 0 else 0
        g[r][hole] = "."; g[r + 1][hole] = "."
    g[0][n // 2] = "S"; g[n - 1][n // 2] = "T"
    return (H, ["".join(x) for x in g])
cases.append(thick(500, 10))
cases.append(thick(500, 3))
# T sealed in a box thicker than H
g = [["."] * 500 for _ in range(500)]
for r in range(240, 261):
    for c in range(240, 261):
        g[r][c] = "#"
g[250][250] = "T"; g[0][0] = "S"
cases.append((9, ["".join(x) for x in g]))
cases.append((10, ["".join(x) for x in g]))
# small trap tests chosen with sol/naive (tests 26-28, kept byte-identical)
TRAPS = [
    (3, [
        '##.#..####.##.##...#..',
        '#.....###..######..##.',
        '##.##..##.#..##...##.#',
        '........####...#...#..',
        '.#.#...##.#####.#...##',
        '#..###....############',
        '##..###..#.#.##.##..##',
        '.##..#...#.#.#.#...#..',
        '#..#####..##.#.#....##',
        '#......#.###....#.#...',
        '#..#...##..##.#....###',
        '.###....#..#S.####.#..',
        '#.#.....#.#......#.##.',
        '.##.##....##.######..#',
        '.#......##.#......#..#',
        '..#.....###.........##',
        '#..##.#.#.#..#.#..#.##',
        '.#...#...#.#..##..###.',
        '#...###...#.#.....##.#',
        '.#....#......###.###.#',
        '####.##...##..###...##',
        '..#.#....#.#.##..#.###',
        '#.#.##....#.#..#.#...#',
        '...#.#.#.#..####..##..',
        '.###.....##..##.#...##',
        '#.##...........##.#.##',
        '#..###..#.###...#.#.#.',
        '#.#.#.#..####...###..#',
        '..##.#...#.#..#..#.##.',
        '#.##.######...#..#.#.#',
        '#.###..#.##..###.#.##.',
        '..#..##.#..###...#..##',
        '#...##....#.##.##..##.',
        '....#....#.###..#..##.',
        '..#.....#.##.#.###.#..',
        '#.#.##..#.###..#...###',
        '#..##.....#.####.#....',
        '#..#.#..##.##.##..####',
        '.#....#.....#..#...#..',
        '#..#.#...###.#...##...',
        '.##.#....##..#.#.#####',
        '##.##..###.....#..##.#',
        '#.#....#..#.###....##.',
        '#.#......####...#####.',
        '#.#..#..#..#..#.#.#...',
        '#....######..##.#....#',
        '##..#.#.......#.####.T',
        '..#.#.##..####..#.....',
        '###.#.#.#.#.##..#.##..',
        '###.##.#.###..###.#...',
        '...#.#..#..#...#..#...',
        '##.###.##...#.#....#..',
        '#..#.####.....#..#....',
        '.....#..#.##..##..#..#',
        '.###..####.####.#...#.',
        '.#.#.##..##.####......',
        '.#.#..#...###.##..#.##',
        '.##.##.##.....#....##.',
        '..#......####.#..#..#.',
    ]),
    (3, [
        '##..###.#.....###....#..#..#..#.##......#..####...#......',
        '.##.#.#..##....##S.#......#.###..#...###...##.#.#.....##.',
        '..#....#.#....#....#....##.#.##.##.##..####.##.#.#...#.##',
        '..##..#...#.##.#..#.#.#..#....#.#...#..#.#.......#..#....',
        '#..##...#......#.#....####....#..#.#####.......####...#.#',
        '..#.##.#....#####.#.##.#..#.##..##.##.#.#.#...###..#..##.',
        '.#.###..#..###..###.###...#.#.######.#.#...#...##.....#..',
        '##...##.######...###...........##..#.#####....#...##.####',
        '..#.....#.#.#.#.####.#.###.#.#.##.#.#...##......##...#..#',
        '..##.#..#.#.#.##.#..#.#.###..#.........##.##..#.#####.##.',
        '######..#...#.#.#..##.###.#..##.#.#..#......#.###.###....',
        '#...#.......####.###.#####.#####.#..#.##########...#.#...',
        '..##.#.......#..#.#.#...##.....###.##.##.....########..#.',
        '..##......#..#.....#..#.##...##.##....##.#.....#..##.#..#',
        '..#..###...#...##.#.....##..#...##.#...##.#..#.###.#.....',
        '#.....###...#.#.#.#...#...#...#......#.##....#.#.##..####',
        '....##......###.#.#..###.#..##........##..####....#...##.',
        '#.###.#..#...##.####.#.##T.##..#..##.##....#...##...####.',
        '..###...###..#.##......#.....##..#.#####..######.##.....#',
        '.#.##....#..#..###.#...#..........##...###....#..##.#...#',
        '...#.#...#..#.#...###.#.#.##..#.....##..#...#...#.##..#..',
        '#######..##..#......##...##.####.##.#..#...#..##.##.#####',
        '#...#.#.#....##.#.#.#.###...#.#.#.#.#......#####.#...##..',
        '####.#.##...##.#...###..#...####.##...####.#.##...#.##..#',
    ]),
    (3, [
        '#...#..#..#T.###.##...#.#..###.##.##..##.##.###',
        '#.#.#####.#....##......#...#.#......#..#.#...#.',
        '#.##......###....##.#.......##.#.#.....#.##.#..',
        '#....###.#..#.##.#..##.##....#.#.##...##.######',
        '......#..#..##..#.##........#..#####..###....##',
        '##.#......#.....#..####.........#..#.#..#.#...#',
        '....###...#..#.#.####....###...##.#...#.##.#.#.',
        '...##...#.##.#..##.#...#.#.....#...#...####.##.',
        '.##.....#.....#.#.###...#....###..#.#S..##..#..',
        '.#...#...###...##...#.#...#.......##..#......#.',
        '#.......#.#.#.....#..#....##..#...#.....#......',
        '##..#...####..#..##.......######.#.#.#...#.#..#',
        '..#.##...####.#.....##.#...#..#..#.###..##.###.',
        '.#..###..##.#...#.#.##...##...#.###.#...##..##.',
        '.#.#..#.##.#.#...#..#.#....####....##...#....##',
        '.#.##.###.####.#...###....#####.....#.........#',
        '##.#...##.....#.#.#..#..#.#.######..#.......###',
        '..##.####.#..#.....#..#.#..#....###..#..#.#.#..',
        '.#....###..#####..#....##.#.##.#..#.#...####...',
        '....##...#..#.#.##.#.#.###.#.#...##....##......',
        '.##.##..##########..#.#.#......#.....#...#....#',
        '#.##.#..#..#.#..#........#....##..#..#...#.#.#.',
        '.#....#....#..####.#..##...#.##.#..#.##......#.',
        '#.#...###..#..##...#..#..#....#..#....##..#...#',
        '#.....#.##..#.#.#....##....##....#.##..#.#...##',
    ]),
]
cases += TRAPS

# ---- stronger tests (2026-10-20): hammer-dominance traps ----
# A cell is first reached by a path that breaks walls, but T sits in a vault of walls of thickness th, so the
# right path must reach that area again later with fewer hammers used. "One visit per cell" BFS (and its variant
# keeping the most hammers among same-distance arrivals) fails; "fewest hammers first" gives a too long path.
rng = random.Random(260220)
def vault(g, tr, tc, th, ent=None):
    R, C = len(g), len(g[0])
    for r in range(tr - th, tr + th + 1):
        for c in range(tc - th, tc + th + 1):
            if 0 <= r < R and 0 <= c < C:
                assert g[r][c] != "S"
                g[r][c] = "#"
    if ent is not None:                     # a free tunnel out of the vault on one side
        dr, dc = [(1, 0), (-1, 0), (0, 1), (0, -1)][ent]
        for k in range(1, th + 1):
            r, c = tr + dr * k, tc + dc * k
            if 0 <= r < R and 0 <= c < C: g[r][c] = "."
    g[tr][tc] = "T"
def grid_of(case):
    H, rows = case
    g = [list(x) for x in rows]
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c] == "T": g[r][c] = "."; t = (r, c)
    return H, g, t
def pack(H, g): return (H, ["".join(x) for x in g])
# enlarge the traps of some existing big tests
for idx, th in ((10, 9), (19, 6), (20, 4), (22, 2)):        # tests 11, 20, 21, 23: T now in a vault
    H, g, (tr, tc) = grid_of(cases[idx])
    vault(g, tr, tc, th)
    cases[idx] = pack(H, g)
H, g, (tr, tc) = grid_of(cases[24])                          # test 25: the box of thickness H in random terrain
for r in range(500):
    for c in range(500):
        if not (240 <= r <= 260 and 240 <= c <= 260) and g[r][c] == "." and rng.random() < 0.3: g[r][c] = "#"
g[tr][tc] = "T"
cases[24] = pack(H, g)
N = 500
def snake_vault(H, th, wt, ch, holes, ent, transpose=False):
    g = [["."] * N for _ in range(N)]
    r, k = ch, 0
    while r + wt <= N - 1:                  # wall bands of thickness wt, corridors of height ch
        hole = N - 1 if k % 2 == 0 else 0
        for rr in range(r, r + wt):
            for c in range(N): g[rr][c] = "." if c == hole or rng.random() < holes else "#"
        r += wt + ch; k += 1
    tr, tc = rng.randint(N - 120, N - 1 - th), rng.randint(th, N - 1 - th)
    vault(g, tr, tc, th, ent)
    g[0][rng.randrange(N)] = "S"
    if transpose: g = [list(x) for x in zip(*g)]
    return pack(H, g)
def terrain_vault(H, th, p, ent):
    g = [["#" if rng.random() < p else "." for _ in range(N)] for _ in range(N)]
    tr, tc = rng.randint(th, N - 1 - th), rng.randint(th, N - 1 - th)
    vault(g, tr, tc, th, ent)
    while True:
        sr, sc = rng.randrange(N), rng.randrange(N)
        if abs(sr - tr) + abs(sc - tc) > 200: break
    g[sr][sc] = "S"
    return pack(H, g)
def spiral_vault(H, th, wt, ent):
    g = [["."] * N for _ in range(N)]
    k, lo = 0, 1
    while lo + wt < N // 2 - th - 2:        # nested square rings, one gap each, gaps on rotating sides
        hi = N - 1 - lo
        for t in range(wt):
            a, b = lo + t, hi - t
            for c in range(a, b + 1): g[a][c] = g[b][c] = "#"
            for r in range(a, b + 1): g[r][a] = g[r][b] = "#"
        mid, side = rng.randint(lo + wt + 1, N - 2 - lo - wt), k % 4
        for t in range(wt):
            a, b = lo + t, hi - t
            if side == 0: g[a][mid] = "."
            elif side == 1: g[mid][b] = "."
            elif side == 2: g[b][mid] = "."
            else: g[mid][a] = "."
        lo += wt + 1 + rng.randint(0, 2); k += 1
    vault(g, N // 2, N // 2, th, ent)
    g[0][0] = "S"
    return pack(H, g)
cases.append(snake_vault(10, 6, 1, 1, 0.002, None))
cases.append(snake_vault(10, 7, 1, 1, 0.002, 3))
cases.append(snake_vault(9, 4, 2, 1, 0.001, 1))
cases.append(snake_vault(10, 5, 1, 2, 0.01, 2, transpose=True))
cases.append(snake_vault(3, 1, 1, 3, 0.003, None))
cases.append(terrain_vault(10, 6, 0.35, None))
cases.append(terrain_vault(10, 7, 0.38, 3))
cases.append(terrain_vault(8, 5, 0.36, 1))
cases.append(terrain_vault(10, 3, 0.4, None))
cases.append(spiral_vault(10, 6, 1, None))
cases.append(spiral_vault(9, 4, 2, None))
cases.append(spiral_vault(10, 8, 1, 1))
assert len(cases) <= 40
for i, (H, g) in enumerate(cases, 1):
    R, C = len(g), len(g[0])
    flat = "".join(g)
    assert 1 <= R <= 500 and 1 <= C <= 500 and 0 <= H <= 10
    assert all(len(x) == C and set(x) <= set("ST.#") for x in g) and flat.count("S") == 1 and flat.count("T") == 1
    open(f"tests/{i:02d}.in", "w").write(f"{R} {C} {H}\n" + "\n".join(g) + "\n")
print(len(cases), "tests")
