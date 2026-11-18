# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
import os, random

random.seed(7064)
rnd = random.random
MAXN, MAXV = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, rows, v):
    """rows[k] = (A, U, B, W) for k = 1..n (rows[0] unused)"""
    assert 1 <= n <= MAXN and len(rows) == n + 1 and 1 <= v <= n
    into = [0] * (n + 1)
    for k in range(1, n + 1):
        a, u, b, w = rows[k]
        for c, d in ((a, u), (b, w)):
            if c == 0:
                assert d == 0
            else:
                assert k < c <= n and 1 <= d <= MAXV
                into[c] += 1
    assert into[1] == 0 and all(into[c] == 1 for c in range(2, n + 1))
    lines = [str(n)] + ["%d %d %d %d" % rows[k] for k in range(1, n + 1)] + [str(v)]
    tests.append("\n".join(lines) + "\n")


def raw(text):
    tests.append(text.strip("\n") + "\n")


# ---------------------------------------------------------------- shapes: par[c], side[c] (0 left, 1 right)
def shape_random(n, near=0):
    """each new cup hangs under an earlier cup with a free slot; near > 0: under one of the last `near` cups"""
    par, side = [0] * (n + 1), [0] * (n + 1)
    slots = [[], [0, 1]] + [[0, 1] for _ in range(n - 1)]
    has_free = [1]
    for c in range(2, n + 1):
        if near:
            p = max(1, c - 1 - int(rnd() * near))
            if not slots[p]:
                p = c - 1
        else:
            i = int(rnd() * len(has_free))
            p = has_free[i]
        s = slots[p].pop(int(rnd() * len(slots[p])))
        if not near and not slots[p]:
            has_free[i] = has_free[-1]
            has_free.pop()
        par[c], side[c] = p, s
        has_free.append(c)
    return par, side


def shape_caterpillar(n, leaf=1.0):
    """a spine 1 -> ... ; every spine cup also gets a leaf (probability `leaf`) on a random side"""
    par, side = [0] * (n + 1), [0] * (n + 1)
    spine, c = 1, 2
    while c <= n:
        s = ri(0, 1)
        par[c], side[c] = spine, s
        nxt = c
        c += 1
        if c <= n and rnd() < leaf:
            par[c], side[c] = spine, 1 - s
            c += 1
        spine = nxt
    return par, side


def shape_heap(n):
    par, side = [0] * (n + 1), [0] * (n + 1)
    for c in range(2, n + 1):
        par[c], side[c] = c // 2, c % 2
    return par, side


def shape_broom(n, handle):
    """a long caterpillar handle (cups 1..handle), then a random bushy tree below its last cup"""
    par, side = shape_caterpillar(handle, 1.0)
    par += [0] * (n - handle)
    side += [0] * (n - handle)
    used = set((par[c], side[c]) for c in range(2, handle + 1))
    free = [(handle, s) for s in (0, 1) if (handle, s) not in used]
    for c in range(handle + 1, n + 1):
        i = int(rnd() * len(free))
        free[i], free[-1] = free[-1], free[i]
        p, s = free.pop()
        par[c], side[c] = p, s
        free += [(c, 0), (c, 1)]
    return par, side


# ---------------------------------------------------------------- values
def log_value():
    """spread over all magnitudes 1 .. 10^9"""
    return max(1, min(MAXV, int(10 ** (rnd() * 9.0))))


def make_rows(n, par, side, val):
    rows = [(0, 0, 0, 0)] + [[0, 0, 0, 0] for _ in range(n)]
    for c in range(2, n + 1):
        rows[par[c]][2 * side[c]] = c
        rows[par[c]][2 * side[c] + 1] = val(c)
    return rows


def tune(rows, par, side, v, slack, grow, tie=0.3, cap=MAXV - 1000, stop=1):
    """walk up from cup v to cup `stop` and set the rails on the way so that cup v is reachable:
    the rail into the path gets need + (0..slack), the other rail gets about `keep` (+ up to `grow`),
    and need (marbles that must enter the current cup) never passes `cap`. Returns need at `stop`."""
    need, c = 1, v
    while c != stop:
        p, s = par[c], side[c]
        r = rows[p]
        u = min(MAXV, need + ri(0, slack))
        if need >= cap - 5:
            u = MAXV          # leave room so that the other rail can stay at least 1
        r[2 * s + 1] = u
        t = u - need + 1
        keep = t if s == 0 else t - 1
        if r[2 * (1 - s)]:
            w = keep + (ri(-1, 1) if rnd() < tie else ri(-3, grow))
            w = max(1, min(MAXV, w, keep + cap - need))
            r[2 * (1 - s) + 1] = w
            need += max(0, w - keep)
        c = p
    return need


def finish(n, rows, v):
    add(n, [tuple(r) for r in rows], v)


def depths(par, n):
    d = [0] * (n + 1)
    for c in range(2, n + 1):
        d[c] = d[par[c]] + 1
    return d


def pick_deep(par, n, frac=0.9):
    """a cup whose depth is at least frac * the largest depth"""
    d = depths(par, n)
    m = max(d)
    cand = [c for c in range(1, n + 1) if d[c] >= frac * m]
    return cand[int(rnd() * len(cand))]


# ---------------------------------------------------------------- samples
raw("""
7
2 2 3 1
4 1 5 1
7 1 6 2
0 0 0 0
0 0 0 0
0 0 0 0
0 0 0 0
6
""")
raw("""
5
2 1 3 2
4 2 5 3
0 0 0 0
0 0 0 0
0 0 0 0
4
""")
raw("""
8
2 9 7 8
3 8 4 2
8 8 0 0
5 4 6 3
0 0 0 0
0 0 0 0
0 0 0 0
0 0 0 0
5
""")
raw("""
5
2 1000000000 3 1000000000
4 900000000 5 600000000
0 0 0 0
0 0 0 0
0 0 0 0
5
""")

# ---------------------------------------------------------------- hidden: small (brute drops marbles one by one)
raw("1\n0 0 0 0\n1\n")
raw("""
4
2 3 3 3
4 1 0 0
0 0 0 0
0 0 0 0
1
""")
for n, D, near in ((8, 3, 0), (10, 6, 3), (12, 9, 0), (15, 5, 2), (20, 12, 0), (30, 4, 4), (60, 8, 0), (200, 20, 3)):
    par, side = shape_random(n, near)
    rows = make_rows(n, par, side, lambda c: ri(1, D))
    v = pick_deep(par, n, 0.6)
    if rnd() < 0.7:
        tune(rows, par, side, v, 3, 3)
    finish(n, rows, v)

# ---------------------------------------------------------------- hidden: middle
n = 3000
par, side = shape_random(n, 5)
rows = make_rows(n, par, side, lambda c: log_value())
v = pick_deep(par, n)
tune(rows, par, side, v, 40, 3000)
finish(n, rows, v)

n = 5000
par, side = shape_caterpillar(n, 0.8)
rows = make_rows(n, par, side, lambda c: ri(1, 100000))
v = pick_deep(par, n)
tune(rows, par, side, v, 5, 2000, 0.5)
finish(n, rows, v)

# ---------------------------------------------------------------- hidden: max size
N = MAXN
# 1-3: a long caterpillar, the prize at the bottom, rails tuned tight around the tie rule
for slack, grow, tie in ((3, 15000, 0.4), (0, 18000, 0.6), (1000, 10000, 0.2)):
    par, side = shape_caterpillar(N)
    rows = make_rows(N, par, side, lambda c: log_value())
    v = pick_deep(par, N, 0.97)
    tune(rows, par, side, v, slack, grow, tie)
    finish(N, rows, v)

# 4: caterpillar, every path rail 10^9, the side rails a little above what the tie rule allows
par, side = shape_caterpillar(N)
rows = make_rows(N, par, side, lambda c: ri(1, 18000))
v = pick_deep(par, N, 0.99)
tune(rows, par, side, v, MAXV, 20000, 0.0)
finish(N, rows, v)

# 5-7: deep random trees (each cup under one of the last few cups), log-spread values, tuned path
for near, slack, grow in ((4, 50, 40000), (8, 5, 60000), (3, 2000, 30000)):
    par, side = shape_random(N, near)
    rows = make_rows(N, par, side, lambda c: log_value())
    v = pick_deep(par, N, 0.95)
    tune(rows, par, side, v, slack, grow)
    finish(N, rows, v)

# 8-9: bushy random trees, values spread, tuned path to a deep cup
for slack, grow in ((10, 6 * 10 ** 7), (100000, 10 ** 8)):
    par, side = shape_random(N, 0)
    rows = make_rows(N, par, side, lambda c: log_value())
    v = pick_deep(par, N, 0.9)
    tune(rows, par, side, v, slack, grow, 0.4)
    finish(N, rows, v)

# 10-11: complete binary tree (heap numbering), the prize at a leaf
for slack, grow in ((0, 2 * 10 ** 8), (300, 15 * 10 ** 7)):
    par, side = shape_heap(N)
    rows = make_rows(N, par, side, lambda c: log_value())
    v = ri(N // 2 + 1, N)
    tune(rows, par, side, v, slack, grow, 0.5)
    finish(N, rows, v)

# 12: broom: long handle, bushy brush, prize deep in the brush
par, side = shape_broom(N, 60000)
rows = make_rows(N, par, side, lambda c: log_value())
v = pick_deep(par, N, 0.95)
tune(rows, par, side, v, 20, 12000, 0.4)
finish(N, rows, v)

# 13: the largest answer: about 10^9 marbles must enter the cup below cup 1, and cup 1 has rails 10^9
par, side = shape_caterpillar(N)
rows = make_rows(N, par, side, lambda c: log_value())
v = pick_deep(par, N, 0.99)
c = v
while par[c] != 1:
    c = par[c]
tune(rows, par, side, v, 2, 70000, 0.3, stop=c)
rows[1][1] = MAXV
rows[1][3] = MAXV if rows[1][2] else 0
finish(N, rows, v)

# 14: answer -1 deep down (a path rail is too small), cup 1 has rails 10^9
par, side = shape_caterpillar(N)
rows = make_rows(N, par, side, lambda c: log_value())
v = pick_deep(par, N, 0.99)
tune(rows, par, side, v, 5, 15000, 0.4)
c = par[par[v]]
rows[par[c]][2 * side[c] + 1] = 1          # one marble only, but more are needed below
rows[1][1] = MAXV
if rows[1][2]:
    rows[1][3] = MAXV
finish(N, rows, v)

# 15: answer -1 in a random tree (no tuning), big rails at cup 1
par, side = shape_random(N, 6)
rows = make_rows(N, par, side, lambda c: log_value())
rows[1][1] = MAXV
rows[1][3] = MAXV if rows[1][2] else 0
finish(N, rows, pick_deep(par, N, 0.95))

# 16: a thin random tree, large rails everywhere, tuned path
par, side = shape_random(N, 2)
rows = make_rows(N, par, side, lambda c: ri(10 ** 8, MAXV))
v = pick_deep(par, N, 0.98)
tune(rows, par, side, v, 100000, 12000, 0.3)
finish(N, rows, v)

# 17-18: every rail 10^9 except a tuned path (heavy splitting everywhere)
for shape in ("cat", "rand"):
    par, side = shape_caterpillar(N) if shape == "cat" else shape_random(N, 10)
    rows = make_rows(N, par, side, lambda c: MAXV - ri(0, 3))
    v = pick_deep(par, N, 0.98)
    tune(rows, par, side, v, 2, 9000, 0.6)
    finish(N, rows, v)

# 19: a deep random tree, side rails tight around the tie rule, small spread values
par, side = shape_random(N, 3)
rows = make_rows(N, par, side, lambda c: ri(1, 30))
v = pick_deep(par, N, 0.97)
tune(rows, par, side, v, 4, 16000, 0.7)
finish(N, rows, v)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
