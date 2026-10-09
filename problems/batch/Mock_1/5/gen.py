import random, os, math
random.seed(2605)
os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples ----
cases.append([[1, 5, 2], [3, 9, 4]])
cases.append([[7]])
cases.append([[0, 10, 0, 10]])
cases.append([[4, 4], [4, 4]])
cases.append([[1, 8, 2], [9, 9, 9], [3, 7, 1]])
# ---- small random ----
for _ in range(6):
    R, C = random.randint(1, 7), random.randint(1, 7)
    m = random.choice([5, 50, 10**6])
    cases.append([[random.randint(0, m) for _ in range(C)] for _ in range(R)])
# ---- large ----
B = 10**6
def rnd(R, C, m): return [[random.randint(0, m) for _ in range(C)] for _ in range(R)]
cases.append(rnd(500, 500, B))
cases.append(rnd(250, 1000, 3))
cases.append(rnd(1, 1000, B))
cases.append(rnd(1000, 1, B))
cases.append([[(i * 997 + j * 991) % (B + 1) for j in range(500)] for i in range(500)])
# smooth terrain (sum of waves) -> realistic hills, many ties
cases.append([[int(5 * 10**5 + 2 * 10**5 * math.sin(i / 37) + 2 * 10**5 * math.cos(j / 23) + random.randint(0, 50)) for j in range(500)] for i in range(500)])
# two plateaus separated by a cliff -> huge single contribution, needs 64-bit
cases.append([[0 if j < 250 else B for j in range(500)] for i in range(500)])
# all equal -> 0
cases.append([[123456] * 500 for _ in range(500)])
# checkerboard of extremes
cases.append([[B if (i + j) % 2 else 0 for j in range(500)] for i in range(500)])
# staircase: every step costs 1
cases.append([[i + j for j in range(500)] for i in range(500)])
cases.append(rnd(1000, 250, B))
# medium sizes: O(V^2) per-pair approaches should time out
cases.append(rnd(50, 60, B))
cases.append(rnd(100, 200, B))
cases.append(rnd(150, 300, 50))
cases.append(rnd(250, 200, B))
cases.append([[int(5 * 10**5 + 4 * 10**5 * math.sin((i + j) / 17)) for j in range(300)] for i in range(300)])
for i, g in enumerate(cases, 1):
    R, C = len(g), len(g[0])
    assert 1 <= R <= 1000 and 1 <= C <= 1000 and R * C <= 250000 and all(len(r) == C and all(0 <= x <= B for x in r) for r in g)
    open(f"tests/{i:02d}.in", "w").write(f"{R} {C}\n" + "\n".join(" ".join(map(str, r)) for r in g) + "\n")
print(len(cases), "tests")
