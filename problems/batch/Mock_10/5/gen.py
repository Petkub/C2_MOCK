# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1050521)
MAXL, MAXN = 10 ** 9, 20000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(L, pts, K):
    n = len(pts)
    assert 1 <= L <= MAXL and 1 <= n <= MAXN and 0 <= K <= n
    xs, ys = zip(*pts)
    assert min(xs) >= 0 and max(xs) <= L and min(ys) >= 0 and max(ys) <= L
    assert len(set(pts)) == n
    pts = list(pts)
    random.shuffle(pts)
    lines = [f"{L} {n} {K}"] + [f"{x} {y}" for x, y in pts]
    tests.append("\n".join(lines) + "\n")


def dedup(pts):
    return sorted(set(pts))


def lattice(cx, cy, dx, dy, ox, oy, L, flip=False):
    """cx * cy trees at (ox + i dx, oy + j dy); flip swaps x and y"""
    pts = [(ox + i * dx, oy + j * dy) for i in range(cx) for j in range(cy)]
    assert all(0 <= x <= L and 0 <= y <= L for x, y in pts)
    if flip:
        pts = [(y, x) for x, y in pts]
    return pts


def uniform(n, L):
    s = set()
    while len(s) < n:
        s.add((ri(0, L), ri(0, L)))
    return sorted(s)


def clusters(n, L, k, spread):
    cs = [(ri(0, L), ri(0, L)) for _ in range(k)]
    s = set()
    while len(s) < n:
        cx, cy = cs[int(rnd() * k)]
        x = int(random.gauss(cx, spread))
        y = int(random.gauss(cy, spread))
        if 0 <= x <= L and 0 <= y <= L:
            s.add((x, y))
    return sorted(s)


def full_lattice(L, holes=(), keep=lambda x, y: True):
    hs = set(holes)
    return [(x, y) for x in range(L + 1) for y in range(L + 1) if keep(x, y) and (x, y) not in hs]


def block(x1, x2, y1, y2):
    return [(x, y) for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]


def ring(n, L, g, h, fo, cx=0.5, cy=0.5, kind="uni", inside=0, edge=0.0, K=0):
    """an empty square hole of side g L centred near (cx L, cy L), a square ring of thickness h L around it holding
    most trees, a fraction fo of the trees spread over the rest of the field (a share `edge` of them on the
    four sides of the field), `inside` trees in the hole.
    kind: "uni" uniform in the ring, "lat" a jittered lattice, "clu" small clusters"""
    side, th = int(g * L), int(h * L)
    x0, y0 = int(cx * L) - side // 2, int(cy * L) - side // 2
    hx0, hx1, hy0, hy1 = x0, x0 + side, y0, y0 + side
    ox0, ox1, oy0, oy1 = max(0, hx0 - th), min(L, hx1 + th), max(0, hy0 - th), min(L, hy1 + th)

    def in_hole(x, y):
        return hx0 <= x <= hx1 and hy0 <= y <= hy1

    def in_outer(x, y):
        return ox0 <= x <= ox1 and oy0 <= y <= oy1

    s = set()
    n_out = int(n * fo)
    while len(s) < n_out:
        x, y = ri(0, L), ri(0, L)
        if rnd() < edge:
            x, y = [(x, 0), (x, L), (0, y), (L, y)][int(rnd() * 4)]
        if not in_outer(x, y):
            s.add((x, y))
    while len(s) < n_out + inside:
        s.add((ri(hx0, hx1), ri(hy0, hy1)))
    need = n - len(s)
    if kind == "lat":
        area = (ox1 - ox0) * (oy1 - oy0) - side * side
        d = max(2, int((area / need) ** 0.5 * 0.97))
        r = d // 3
        cand = set()
        for i in range((ox1 - ox0) // d + 1):
            for j in range((oy1 - oy0) // d + 1):
                x, y = ox0 + i * d + ri(-r, r), oy0 + j * d + ri(-r, r)
                if in_outer(x, y) and not in_hole(x, y):
                    cand.add((x, y))
        cand = sorted(cand - s)
        s.update(random.sample(cand, min(need, len(cand))))
    elif kind == "clu":
        cs = []
        while len(cs) < 300:
            x, y = ri(ox0, ox1), ri(oy0, oy1)
            if not in_hole(x, y):
                cs.append((x, y))
    while len(s) < n:
        if kind == "clu":
            px, py = cs[int(rnd() * len(cs))]
            x, y = int(random.gauss(px, th / 15)), int(random.gauss(py, th / 15))
        else:
            x, y = ri(ox0, ox1), ri(oy0, oy1)
        if in_outer(x, y) and not in_hole(x, y):
            s.add((x, y))
    add(L, sorted(s), K)


# samples
add(8, [(2, 2), (5, 3), (3, 6), (6, 6), (1, 4), (7, 1)], 1)
add(4, [(2, 2)], 0)
add(1, [(0, 0), (1, 1)], 1)
add(10 ** 9, [(0, 0), (3, 5)], 2)
add(12, [(3, 1), (9, 2), (6, 4), (1, 7), (10, 7), (5, 9)], 0)
# hidden: small (brute checks these)
add(1, [(0, 0)], 0)
add(190, full_lattice(190, keep=lambda x, y: x % 2 == 0), 1)
add(130, full_lattice(130, holes=block(70, 74, 40, 44)), 0)
add(20, uniform(30, 20), 2)
add(400, uniform(2000, 400), 5)
add(10 ** 9, uniform(40, 10 ** 9), 3)
add(10 ** 9, clusters(60, 10 ** 9, 3, 10 ** 7) + [(0, 0), (0, 10 ** 9), (10 ** 9, 0), (10 ** 9, 10 ** 9)], 0)
add(396, lattice(44, 44, 9, 9, 4, 5, 396), 0)
add(300, lattice(20, 25, 13, 11, 40, 2, 300) + lattice(5, 5, 3, 3, 1, 280, 300), 4)
add(1000, uniform(MAXN, 1000), 6)
# hidden: big
ring(MAXN, MAXL, 0.2, 0.15, 0.02, K=0)
ring(MAXN, MAXL, 0.2, 0.12, 0.03, K=10)
ring(MAXN, MAXL, 0.25, 0.15, 0.01, K=30)
ring(MAXN, MAXL, 0.15, 0.15, 0.02, K=0)
ring(MAXN, MAXL, 0.2, 0.2, 0.02, K=2)
ring(MAXN, 10 ** 8, 0.2, 0.15, 0.02, kind="lat", K=0)
ring(MAXN, MAXL, 0.22, 0.14, 0.02, kind="lat", K=1)
ring(MAXN, MAXL, 0.2, 0.15, 0.02, kind="clu", K=50)
ring(MAXN, MAXL, 0.2, 0.15, 0.02, cx=0.45, cy=0.56, K=3)
ring(MAXN, MAXL, 0.2, 0.15, 0.02, inside=6, K=4)
ring(MAXN, MAXL, 0.18, 0.16, 0.02, kind="lat", inside=3, K=3)
ring(MAXN, MAXL, 0.2, 0.15, 0.02, K=300)
ring(MAXN, MAXL, 0.3, 0.12, 0.01, K=5)
ring(MAXN, MAXL, 0.12, 0.15, 0.02, kind="clu", K=1)
ring(MAXN, MAXL, 0.2, 0.15, 0.04, edge=0.5, K=2)
ring(MAXN, MAXL, 0.16, 0.18, 0.03, cx=0.53, cy=0.47, kind="lat", K=7)
ring(MAXN, MAXL, 0.17, 0.13, 0.025, cy=0.52, kind="clu", K=20)
ring(MAXN, MAXL, 0.21, 0.17, 0.02, kind="lat", edge=0.3, K=0)
ring(MAXN, MAXL, 0.23, 0.13, 0.015, cx=0.48, inside=12, K=11)
add(MAXL, uniform(MAXN, MAXL), 0)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
