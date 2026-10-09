import random, os
random.seed(2607)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append(["S.a#....", "###...#.", "....#a#G"])
cases.append(["S#G", ".#.", "..."])
cases.append(["Sa#bG", "##b##", "a...."])
cases.append(["S#", "#G"])
cases.append(["Sab", "#ba", "G#a"])
def rnd(R, C, pw, letters, pl):
    g = [["#" if random.random() < pw else (random.choice(letters) if random.random() < pl else ".") for _ in range(C)] for _ in range(R)]
    s, t = random.sample([(i, j) for i in range(R) for j in range(C)], 2)
    g[s[0]][s[1]] = "S"; g[t[0]][t[1]] = "G"
    if R * C > 100:                      # big grids: do not wall in S or G by accident
        for (i, j) in (s, t):
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < R and 0 <= b < C and g[a][b] == "#": g[a][b] = "."
    return ["".join(r) for r in g]
for _ in range(6):
    cases.append(rnd(random.randint(2, 8), random.randint(2, 8), 0.3, "abc", 0.2))
cases.append(rnd(1000, 1000, 0.3, "abcdefghijklmnopqrstuvwxyz", 0.01))
cases.append(rnd(1000, 1000, 0.42, "ab", 0.05))
g = [["a"] * 1000 for _ in range(1000)]; g[0][0] = "S"; g[999][999] = "G"   # one letter everywhere
cases.append(["".join(r) for r in g])
g = [["a" if (i + j) % 2 else "b" for j in range(1000)] for i in range(1000)]; g[0][0] = "S"; g[999][998] = "G"
cases.append(["".join(r) for r in g])
# walls split the grid; only portals connect the halves
g = [["." for _ in range(1000)] for _ in range(1000)]
for i in range(1000): g[i][500] = "#"
for _ in range(2000): g[random.randrange(1000)][random.randrange(500)] = "q"
g[random.randrange(1000)][random.randrange(501, 1000)] = "q"
g[0][0] = "S"; g[999][999] = "G"
cases.append(["".join(r) for r in g])
g[0][0] = "S"
for i in range(1000):
    for j in range(501, 1000):
        if g[i][j] == "q": g[i][j] = "."
cases.append(["".join(r) for r in g])                                        # same but no way across: -1
# serpentine corridor with a few long-range portals
n = 999
g = [["." for _ in range(n)] for _ in range(n)]
for r in range(1, n, 2):
    for c in range(n): g[r][c] = "#"
    g[r][n - 1 if (r // 2) % 2 == 0 else 0] = "."
for k in range(5):
    ch = "vwxyz"[k]
    for _ in range(2): g[random.randrange(0, n, 2)][random.randrange(n)] = ch
g[0][0] = "S"; g[n - 1][n - 1 if ((n - 1) // 2) % 2 == 0 else 0] = "G"
cases.append(["".join(r) for r in g])
cases.append(["S" + "a" * 998 + "G"])
cases.append(rnd(1000, 1000, 0.0, "abcdefghijklmnopqrstuvwxyz", 0.5))
cases.append(rnd(30, 40, 0.4, "abcde", 0.1))
# dense portals of a single letter: scanning the letter list on every visit is far too slow
for pw, pl in ((0.2, 0.6), (0.1, 0.8), (0.3, 0.5), (0.0, 0.95)):
    cases.append(rnd(1000, 1000, pw, "a", pl))
cases.append(rnd(1000, 1000, 0.25, "ab", 0.7))
for pl in (0.8, 0.9, 0.7):
    cases.append(rnd(500, 500, 0.1, "z", pl))
cases.append(["SaG"])
cases.append(["S.b.a....G", "#########.", "a........#"])   # must walk across portal a; warping leads to a dead end
for i, g in enumerate(cases, 1):
    R, C = len(g), len(g[0]); f = "".join(g)
    assert 1 <= R <= 1000 and 1 <= C <= 1000 and all(len(r) == C for r in g)
    assert f.count("S") == 1 and f.count("G") == 1 and set(f) <= set(".#SG" + "abcdefghijklmnopqrstuvwxyz")
    open(f"tests/{i:02d}.in", "w").write(f"{R} {C}\n" + "\n".join(g) + "\n")
print(len(cases), "tests")
