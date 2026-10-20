# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(730101)
MAXRC, MAXM, MAXQ = 3000, 20000, 100000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(R, C, s, segs, qs):
    assert 1 <= R <= MAXRC and 1 <= C <= MAXRC and 1 <= s <= C
    assert 0 <= len(segs) <= MAXM and 1 <= len(qs) <= MAXQ
    for r1, c1, r2, c2 in segs:
        assert 1 <= r1 <= r2 <= R and 1 <= c1 <= c2 <= C and (r1 == r2 or c1 == c2)
        assert not (r1 <= 1 <= r2 and c1 <= s <= c2), "the source is a rock"
    for r, c in qs:
        assert 1 <= r <= R and 1 <= c <= C
    lines = [f"{R} {C} {s} {len(segs)}"] + [f"{a} {b} {c} {d}" for a, b, c, d in segs]
    lines += [str(len(qs))] + [f"{r} {c}" for r, c in qs]
    tests.append("\n".join(lines) + "\n")


def safe(segs, s):
    """drop the segments that would cover the source (1, s)"""
    return [g for g in segs if not (g[0] <= 1 <= g[2] and g[1] <= s <= g[3])]


def queries(R, C, s, segs, q):
    """random cells, rock cells, the source, cells near the source and repeats"""
    qs = [(ri(1, R), ri(1, C)) for _ in range(q * 6 // 10)]
    for _ in range(q // 10):
        if not segs:
            break
        r1, c1, r2, c2 = segs[int(rnd() * len(segs))]
        qs.append((ri(r1, r2), ri(c1, c2)))
    qs.append((1, s))
    while len(qs) < q * 9 // 10:
        qs.append((ri(1, min(R, 40)), max(1, min(C, s + ri(-40, 40)))))
    k = len(qs)
    while len(qs) < q:          # repeats
        qs.append(qs[int(rnd() * k)])
    return qs


def shelves(R, C, k, lmin, lmax, rmin=3):
    """k horizontal rock shelves at random places; a shelf at row r is at most r // 2 long, so no single
    shelf closes the cone of cells the source reaches"""
    out = []
    for _ in range(k):
        r = ri(rmin, R)
        ln = min(ri(lmin, lmax), max(1, r // 2))
        c = ri(1, max(1, C - ln + 1))
        out.append((r, c, r, min(C, c + ln - 1)))
    return out


def walls(R, C, k, hmin, hmax, s=None, gap=0):
    """k vertical rock walls standing on random rows (none within `gap` columns of the source column s)"""
    out = []
    while len(out) < k:
        c = ri(1, C)
        if s is not None and abs(c - s) < gap:
            continue
        ln = ri(hmin, hmax)
        r = ri(2, max(2, R - ln + 1))
        out.append((r, c, min(R, r + ln - 1), c))
    return out


def stair(r, c, length, d, C):
    """a watertight diagonal wall from (r, c) going down, d = -1 (left) or +1 (right): pieces of 2 cells"""
    out = []
    for i in range(length):
        a, b = sorted((c + d * i, c + d * (i + 1)))
        a, b = max(a, 1), min(b, C)
        if a <= b:
            out.append((r + i, a, r + i, b))
    return out


def cup(r, c, half, C):
    """a V-shaped cup whose bottom is at (r + half - 1, c) and whose rim is at row r"""
    return stair(r, c - half + 1, half, 1, C) + stair(r, c + half - 1, half, -1, C)


def cups(R, C, s, k, hmin, hmax):
    out = []
    for _ in range(k):
        half = ri(hmin, hmax)
        r = ri(max(3, 3 * half), max(3, R - half))        # deep enough not to close the source's cone
        out += cup(r, ri(1, C), half, C)
    return out


def gaps(R, C, first, step):
    """nearly full-width shelves from row `first` every `step` rows, the gap alternating sides"""
    return [(r, 1, r, C - 1) if i % 2 else (r, 2, r, C) for i, r in enumerate(range(first, R + 1, step))]


def big(R, C, s, segs, q=MAXQ):
    segs = safe(segs, s)[:MAXM]
    add(R, C, s, segs, queries(R, C, s, segs, q))


# samples
add(5, 7, 4, [(3, 3, 3, 5), (4, 7, 5, 7)], [(5, 4), (1, 4), (3, 4), (4, 4)])
add(3, 3, 2, [], [(3, 1), (2, 1), (1, 2)])
add(1, 5, 3, [], [(1, 3), (1, 2)])
add(4, 3, 1, [(3, 1, 3, 2)], [(4, 1), (2, 2), (1, 1)])
add(6, 8, 5, [(4, 2, 4, 4), (5, 6, 6, 6)], [(6, 5), (5, 8)])
# hidden: small (brute checks these)
for R, C, k in [(8, 9, 4), (20, 15, 12), (40, 60, 30), (60, 40, 80), (50, 50, 0)]:
    s = ri(1, C)
    segs = safe(shelves(R, C, k // 2, 1, C // 2, 2) + walls(R, C, k - k // 2, 1, R // 2), s)
    add(R, C, s, segs, queries(R, C, s, segs, 300))
add(MAXRC, 1, 1, [(2500, 1, 2500, 1)], [(2499, 1), (2500, 1), (2501, 1), (1, 1), (MAXRC, 1)])
add(2, MAXRC, 1500, [], [(2, 1499), (2, 1500), (2, 1501), (1, 1500), (2, 1)])
add(MAXRC, MAXRC, 7, [(2, 6, 2, 8)], [(1, 7), (2, 7), (MAXRC, MAXRC)])        # the source is closed in
add(300, 300, 150, safe(shelves(300, 300, 40, 5, 60) + cups(300, 300, 150, 3, 5, 30), 150),
    [(ri(1, 300), ri(1, 300)) for _ in range(2000)])
# hidden: big
M = MAXRC
# each big test has its own seed, so changing one test does not change the others
BIG = [
    (731000, lambda: (M, M, M // 2, [])),
    (731001, lambda: (M, M, 1, [])),
    (734002, lambda: (M, M, M, walls(M, M, 30, 100, 2000))),
    (731003, lambda: (M, M, 2777, shelves(M, M, 60, 100, 900))),
    (731004, lambda: (M, M, 1500, shelves(M, M, 400, 20, 300))),
    (731005, lambda: (M, M, 1300, shelves(M, M, 3000, 3, 15) + walls(M, M, 1000, 3, 30))),
    (731006, lambda: (M, M, 1500, [(ri(2, M), ri(1, M)) * 2 for _ in range(MAXM)])),
    (731007, lambda: (M, M, 1499, walls(M, M, 300, 100, 2000, 1499, 400) + shelves(M, M, 100, 50, 300))),
    (731008, lambda: (M, M, 1500, cups(M, M, 1500, 25, 20, 300))),
    (740009, lambda: (M, M, 1200, gaps(M, M, 1700, 260) + walls(M, M, 40, 200, 1200))),
    (731010, lambda: (M, M, 1500, walls(M, M, 2000, 1, 50) + shelves(M, M, 2000, 1, 50) + cups(M, M, 1500, 10, 5, 100))),
    (742011, lambda: (M, M, 2222, cups(M, M, 2222, 40, 10, 200) + shelves(M, M, 300, 10, 300))),
    (731012, lambda: (M, 1500, 700, walls(M, 1500, 60, 50, 1000, 700, 300) + shelves(M, 1500, 100, 5, 40))),
    (740013, lambda: (1500, M, 1500, shelves(1500, M, 150, 10, 60) + walls(1500, M, 100, 5, 500, 1500, 300))),
    (731014, lambda: (M, 900, 450, walls(M, 900, 100, 50, 600))),
    (731015, lambda: (M, M, 1500, [(r, c, r, c) for r in range(2, M, 9) for c in range(1 + r % 5, M + 1, 150)][:MAXM])),
    (731016, lambda: (M, M, M, stair(2, M - 1, 1200, -1, M) + shelves(M, M, 500, 10, 200))),
]
for seed, make in BIG:
    random.seed(seed)
    big(*make())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
