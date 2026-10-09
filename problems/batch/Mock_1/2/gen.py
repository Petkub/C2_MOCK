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
# (small trap tests chosen with sol/naive are shipped as files)
for i, (H, g) in enumerate(cases, 1):
    R, C = len(g), len(g[0])
    flat = "".join(g)
    assert 1 <= R <= 500 and 1 <= C <= 500 and 0 <= H <= 10
    assert all(len(x) == C and set(x) <= set("ST.#") for x in g) and flat.count("S") == 1 and flat.count("T") == 1
    open(f"tests/{i:02d}.in", "w").write(f"{R} {C} {H}\n" + "\n".join(g) + "\n")
print(len(cases), "tests")
