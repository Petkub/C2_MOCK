# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Most tests come from hidden strengths Y (c = min(Y_a, Y_b), always consistent); a "bad" record
# (c smaller than both final lower bounds) is inserted before the first record of one of its ropes,
# so checking each record right after reading it does not see the contradiction.
import os, random

random.seed(1219019)
rnd = random.random
MAXN, MAXM, MAXC = 10 ** 5, 10 ** 5, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, recs):
    m = len(recs)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM
    for a, b, c in recs:
        assert 1 <= a <= n and 1 <= b <= n and a != b and 1 <= c <= MAXC
    tests.append(f"{n} {m}\n" + "".join(f"{a} {b} {c}\n" for a, b, c in recs))


def pair(n):
    a = ri(1, n)
    b = ri(1, n - 1)
    return a, (b if b < a else b + 1)


def from_y(y, pairs):
    """records consistent with strengths y[1..n]"""
    return [(a, b, min(y[a], y[b])) for a, b in pairs]


def rand_pairs(n, m, lo=1, hi=None):
    """m random pairs among ropes lo..hi"""
    hi = n if hi is None else hi
    k = hi - lo + 1
    out = []
    for _ in range(m):
        a, b = pair(k)
        out.append((a + lo - 1, b + lo - 1))
    return out


def low(n, recs):
    x = [1] * (n + 1)
    for a, b, c in recs:
        x[a] = max(x[a], c)
        x[b] = max(x[b], c)
    return x


def bad(n, recs, hidden=True):
    """insert one contradicting record; hidden: placed before the first record of one of its ropes"""
    x = low(n, recs)
    while True:
        u, v = pair(n)
        if min(x[u], x[v]) >= 2:
            break
    c = ri(1, min(x[u], x[v]) - 1)
    if hidden:
        first = next((j for j, r in enumerate(recs) if r[0] == u or r[1] == u), len(recs))
        pos = ri(0, first)
    else:
        pos = len(recs)
    return recs[:pos] + [(u, v, c) if rnd() < 0.5 else (v, u, c)] + recs[pos:]


def ys(n, lo, hi):
    return [0] + [ri(lo, hi) for _ in range(n)]


N, M = MAXN, MAXM
# samples
add(4, [(1, 2, 3), (1, 3, 7), (3, 4, 5), (2, 4, 3)])
add(3, [(1, 2, 5), (1, 3, 5), (2, 3, 3)])
add(5, [(1, 2, 4), (2, 4, 8), (3, 5, 2), (4, 5, 6), (1, 5, 4), (2, 3, 2)])
add(4, [(1, 2, 6), (3, 4, 2), (2, 3, 6), (1, 4, 2), (1, 3, 4)])
add(5, [(1, 2, 10), (2, 3, 10), (3, 4, 7), (4, 5, 7), (2, 1, 10)])
# hidden: small (brute checks these)
add(2, [(2, 1, MAXC)])
add(2, [(1, 2, 7), (2, 1, 7), (1, 2, 7)])
add(2, [(1, 2, 7), (2, 1, 9)])                                       # -1, the same pair twice
add(7, from_y(ys(7, 1, 20), rand_pairs(7, 5, 1, 5)))                 # ropes 6, 7 untested
add(6, bad(6, from_y(ys(6, 1, 30), rand_pairs(6, 6))))              # -1, hidden
add(8, from_y(ys(8, 1, 4), rand_pairs(8, 7)))                       # ties
# hidden: medium
add(1000, from_y(ys(1000, 1, 10), rand_pairs(1000, 2000)))
add(3000, bad(3000, from_y(ys(3000, 1, MAXC), rand_pairs(3000, 4000))))
add(N, [(ri(1, N // 2), ri(N // 2 + 1, N), ri(MAXC - 10 ** 6, MAXC))])  # one record
# hidden: big
add(N, from_y(ys(N, 1, MAXC), rand_pairs(N, M)))                    # some ropes untested
y = ys(N, 1, MAXC)
add(N, from_y(y, [(i, i + 1) if rnd() < 0.5 else (i + 1, i) for i in range(1, N)] + rand_pairs(N, 1)))
y = ys(N, 1, MAXC)
y[1] = MAXC
add(N, from_y(y, [(1, i) if rnd() < 0.5 else (i, 1) for i in range(2, N + 1)] + rand_pairs(N, 1)))  # star
add(N, from_y(ys(N, 1, MAXC), rand_pairs(N, M, 1, N // 2)))         # half of the ropes untested
add(N, from_y(ys(N, 1, 10), rand_pairs(N, M)))                      # small values, many ties
add(300, from_y(ys(300, 1, MAXC), rand_pairs(300, M)))              # many repeated pairs
add(N, [p + (MAXC,) for p in rand_pairs(N, M)])                     # all c equal
add(N, [p + (1,) for p in rand_pairs(N, M)])
y = [0] + [MAXC - ri(0, 3) for _ in range(N)]
add(N, from_y(y, rand_pairs(N, M)))                                 # values almost equal
# -1, the contradiction appears only after later records
add(N, bad(N, from_y(ys(N, 1, MAXC), rand_pairs(N, M - 1))))
add(N, bad(N, from_y(ys(N, 1, 100), rand_pairs(N, M - 1))))
y = ys(N, 1, MAXC)
add(N, bad(N, from_y(y, [(i, i + 1) for i in range(1, N)])))       # a path
add(200, bad(200, from_y(ys(200, 1, MAXC), rand_pairs(200, M - 1))))
add(N, bad(N, [p + (MAXC,) for p in rand_pairs(N, M - 1)]))
# -1, seen as soon as the bad record is read
add(N, bad(N, from_y(ys(N, 1, MAXC), rand_pairs(N, M - 1)), hidden=False))
recs = from_y(ys(N, 1, MAXC), rand_pairs(N, M - 1, 1, 60000))      # many ropes untested
add(N, bad(N, recs))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
