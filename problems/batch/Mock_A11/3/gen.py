# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1402)
MAXQ, MAXT, MAXS, MAXTSUM = 100000, 10, 5000, 400000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only rnd(), so every Python version gives the same tests)"""
    return a + int(rnd() * (b - a + 1))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def add(qs):
    assert 1 <= len(qs) <= MAXQ
    assert sum(len(s) for _, _, s in qs) <= MAXTSUM
    lines = [str(len(qs))]
    seen = {}
    for L, R, s in qs:
        key = id(s)
        if key not in seen:          # queries repeated by many() share their size list
            assert 1 <= len(s) <= MAXT and min(s) >= 1 and sum(s) <= MAXS
            seen[key] = f"{len(s)} " + " ".join(map(str, s))
        assert 1 <= L <= R <= MAXS
        lines.append(f"{L} {R} {seen[key]}")
    tests.append("\n".join(lines) + "\n")


def split(total, t):
    """t random positive sizes with the given sum"""
    cuts = set()
    while len(cuts) < t - 1:
        cuts.add(ri(1, total - 1))
    b = [0] + sorted(cuts) + [total]
    return [b[i + 1] - b[i] for i in range(t)]


def lopsided(total, t):
    """one big department and t - 1 small ones"""
    small = [ri(1, 3) for _ in range(t - 1)]
    if sum(small) >= total:
        small = [1] * (t - 1)
    return [total - sum(small)] + small


def query(maxs, tmin=1, tmax=MAXT, shape=None, rng="any"):
    total = ri(max(tmin, maxs * 9 // 10), maxs) if rng != "small" else ri(tmin, maxs)
    t = ri(tmin, min(tmax, total))
    s = (shape or split)(total, t) if t > 1 else [total]
    for i in range(len(s) - 1, 0, -1):
        j = ri(0, i)
        s[i], s[j] = s[j], s[i]
    kind = rnd()
    if kind < 0.3:
        L, R = 1, pick([total, MAXS, ri(total, MAXS)])
    elif kind < 0.5:
        L = ri(1, total)
        R = ri(L, min(MAXS, total + 50))
    elif kind < 0.65:
        L = R = ri(1, total)
    elif kind < 0.8:                                    # a window around the sizes of the departments
        L = ri(1, max(s) + 1)
        R = ri(L, min(MAXS, max(s) + 5))
    else:
        L = ri(1, MAXS)
        R = ri(L, MAXS)
    return (L, R, s)


def many(make, n):
    """n queries: n // 3 fresh ones, then the same ones again in a shifted order (keeps gen.py fast)"""
    base = [make() for _ in range(n // 3)]
    out = base[:]
    while len(out) < n:
        k = ri(0, len(base) - 1)
        out += base[k:] + base[:k]
    return out[:n]


# samples
add([(2, 3, [2, 2]), (3, 3, [2, 2])])
add([(2, 2, [1, 1, 2]), (1, 5, [4])])
add([(1, 10, [2, 3, 4]), (4, 4, [3, 5]), (1, 1, [5, 5]), (2, 7, [1, 6])])
add([(1, 30, [15, 15]), (10, 20, [7, 9, 4])])
add([(2, 10, [1] * 10), (5, 5, [1] * 10), (3, 4, [2, 1])])
# hidden: small (brute checks these)
add([(1, 1, [1])])
add([(L, R, [a, b]) for a in range(1, 6) for b in range(1, 6) for L in range(1, 8) for R in range(L, 8)])
add([(1, 2, [1, 1]), (2, 2, [1, 1]), (1, 1, [1, 1]), (3, 5, [1, 1])])
for maxs, q in [(12, 300), (40, 300), (120, 200), (300, 100)]:
    add([query(maxs, rng="small") for _ in range(q)])
add([query(60, shape=lopsided, rng="small") for _ in range(200)])
# hidden: big. Every one is heavy: L near 1, R near S = 5000 and Q = min(10^5, 4 * 10^5 / t), so a loop over
# k = L..R for each query (sum of (t + 1)(R - L + 1) steps, up to 2.5 * 10^9) cannot finish in time.


def heavy(t, total=MAXS, shape=None, lmax=1, rlow=MAXS):
    """one heavy query: t departments with the given total, L in [1, lmax], R in [rlow, MAXS]"""
    s = (shape or split)(total, t) if t > 1 else [total]
    for i in range(len(s) - 1, 0, -1):
        j = ri(0, i)
        s[i], s[j] = s[j], s[i]
    return (ri(1, lmax), ri(rlow, MAXS), s)


def qfor(t):
    return min(MAXQ, MAXTSUM // t)


def equal(total, t):
    return [total // t + (1 if i < total % t else 0) for i in range(t)]


BIG = [
    (14100, lambda: many(lambda: heavy(ri(2, 4), MAXS - ri(0, 100)), MAXQ)),
    (14101, lambda: many(lambda: heavy(4), MAXQ)),
    (14102, lambda: many(lambda: heavy(3), qfor(3))),
    (14103, lambda: many(lambda: heavy(10), qfor(10))),
    (14104, lambda: many(lambda: heavy(8, shape=lopsided), qfor(8))),
    (14105, lambda: many(lambda: heavy(5, shape=equal, lmax=3), qfor(5))),
    (14106, lambda: many(lambda: heavy(3, MAXS - ri(0, 30), lmax=10, rlow=4990), qfor(3))),
    (14107, lambda: many(lambda: heavy(6, lmax=3), qfor(6))),
    (14108, lambda: many(lambda: heavy(7, MAXS - ri(0, 50)), qfor(7))),
    (14109, lambda: many(lambda: heavy(10, shape=lopsided, lmax=2), qfor(10))),
    (14110, lambda: many(lambda: heavy(2), MAXQ)),
    (14111, lambda: [(1, MAXS, [MAXS // 2, MAXS - MAXS // 2])] + many(lambda: heavy(4, lmax=50), MAXQ - 1)),
    (14112, lambda: many(lambda: heavy(3, shape=lopsided, lmax=5), qfor(3))),
    (14113, lambda: many(lambda: heavy(9, MAXS - ri(0, 10), rlow=4900), qfor(9))),
    (14114, lambda: many(lambda: heavy(ri(3, 10), MAXS - ri(0, 5)), 2 * MAXTSUM // 13)),
    (14115, lambda: many(lambda: heavy(4, shape=equal), MAXQ)),
    (14116, lambda: many(lambda: heavy(5, MAXS - ri(0, 100), lmax=20, rlow=4950), qfor(5))),
]
for seed, make in BIG:
    random.seed(seed)
    qs = make()
    used, keep = 0, 0
    while keep < len(qs) and used + len(qs[keep][2]) <= MAXTSUM:
        used += len(qs[keep][2])
        keep += 1
    add(qs[:keep])

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
