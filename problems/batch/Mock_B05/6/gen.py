# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Every max-size test is built against the O(N * pieces) walk: almost every board is wide (it covers nearly all
# of the about 2N pieces) and the heights mostly rise, so most boards also rewrite most pieces they visit.
# The "pillar" tests put tall one-slot boards (next to each other or with a gap, at random) under wide boards
# that rise below them: a min / max segment tree that only stops at "min > h" or "max <= h", or a map of runs
# of equal height, visits every pillar on every wide board. Answers reach about 10^14.
import os, random

random.seed(1232)
rnd = random.random
MAXN, MAXX, MAXH = 100000, 10 ** 9, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(boards):
    n = len(boards)
    assert 1 <= n <= MAXN
    for l, r, h in boards:
        assert 1 <= l <= r <= MAXX and 1 <= h <= MAXH
    tests.append(f"{n}\n" + "".join(f"{l} {r} {h}\n" for l, r, h in boards))


def rand_board(c, hmax, wmin=0):
    """a random board on slots 1..c of width >= wmin + 1"""
    a, b = ri(1, c), ri(1, c)
    if a > b:
        a, b = b, a
    if b - a < wmin:
        a = ri(1, c - wmin)
        b = a + wmin + int(rnd() * (c - a - wmin + 1))
    return (a, b, ri(1, hmax))


def wide(k, hs, lo=10 ** 7, hi=MAXX - 10 ** 7, top=MAXX):
    """k wide boards: left end in [1, lo], right end in [hi, top], heights from the list hs"""
    return [(ri(1, lo), ri(hi, top), hs[i]) for i in range(k)]


def pillars(p, hfun, lo=2 * 10 ** 7, hi=MAXX - 2 * 10 ** 7, w=0):
    """p tall boards of width w + 1 inside [lo, hi]; each one touches the previous one or leaves a gap (at random),
    so the pieces under a wide board are tall / low in an unpredictable pattern"""
    gap = 2 * (hi - lo) // p - w - 1
    assert gap >= 2
    out, a = [], lo
    for i in range(p):
        out.append((a, a + w, hfun()))
        a += w + 1 + (0 if rnd() < 0.5 else ri(1, gap))
    assert out[-1][1] <= hi
    return out


def rising(k, a, b):
    return sorted(ri(a, b) for _ in range(k))


def mix(a, b):
    """insert the boards of b at random places of a, keeping both orders"""
    out, i, j = [], 0, 0
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and rnd() < len(a) / (len(a) + len(b))):
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out


# samples
add([(3, 8, 4), (1, 5, 2), (4, 10, 4)])
add([(5, 5, 10), (1, 9, 3), (1, 9, 6), (2, 7, 10)])
add([(2, 6, 5), (4, 9, 5), (1, 3, 7), (5, 5, 1), (1, 10, 6), (8, 8, 9)])
add([(1, 1000000000, 7), (300000000, 700000000, 3), (1, 999999999, 7), (500000000, 500000000, 8)])
add([(10, 20, 4), (15, 25, 2), (12, 18, 9), (5, 30, 3), (14, 16, 9), (1, 40, 9), (20, 22, 1)])
# hidden: small and medium (brute checks these)
add([(1, 1, 1)])
add([(7, 7, 3), (7, 7, 3), (7, 7, 2), (7, 7, 4)])
add([rand_board(30, 5) for _ in range(40)])
add([rand_board(200, 10 ** 9) for _ in range(300)])
add([rand_board(10 ** 9, 20) for _ in range(500)])
add(pillars(1000, lambda: ri(5000, 10000)) + wide(1000, [ri(1, 10000) for _ in range(1000)]))
add([rand_board(5000, 50, 1000) for _ in range(3000)])
add([(i, 10 ** 9 - i, 3000 - i) for i in range(1, 2001)] + [rand_board(10 ** 9, 3000) for _ in range(1000)])
add(wide(20000, [ri(1, MAXH) for _ in range(20000)]))                                         # random heights
# hidden: big, big coordinates
P, Q = N // 3, N // 2
add(pillars(P, lambda: MAXH) + wide(N - P, rising(N - P, 1, MAXH - 1)))                       # pillars, rising floods
add(pillars(Q, lambda: ri(5 * 10 ** 8, MAXH)) + wide(N - Q, rising(N - Q, 1, 5 * 10 ** 8)))
add(mix(pillars(P, lambda: ri(10 ** 8, MAXH)), wide(N - P, rising(N - P, 1, 10 ** 8))))
add(pillars(P, lambda: ri(1, 2) * 4 * 10 ** 8) + wide(N - P, [(i * 10 ** 9) // (N - P) + 1 for i in range(N - P)]))
add(pillars(P, lambda: MAXH, w=3) + wide(N - P, rising(N - P, 1, MAXH - 1)))
add([(a, a + ri(0, 5), MAXH) for a, _, _ in pillars(Q, lambda: 1, w=5)] + wide(N - Q, rising(N - Q, 1, MAXH - 1)))  # pillars of random width
add(mix(pillars(P, lambda: ri(1, MAXH), w=50), wide(N - P, rising(N - P, 1, MAXH))))
nar = []
for _ in range(P):
    a = ri(1, MAXX - 10 ** 4)
    nar.append((a, a + ri(0, 10 ** 4), ri(1, MAXH)))
add(nar + wide(N - P, rising(N - P, 1, MAXH)))                                               # narrow random boards, then rising
add(wide(N, rising(N, 1, MAXH)))                                                             # rising: every slot counts
add(wide(N, [7] * N))                                                                        # all equal, total ~10^14
# hidden: big, small coordinates (shorter lines, so more of them fit)
S = 10 ** 6
add(pillars(Q, lambda: S, 4 * 10 ** 5, 6 * 10 ** 5) + wide(N - Q, rising(N - Q, 1, S - 1), 4 * 10 ** 5, 6 * 10 ** 5, S))
add(mix(pillars(P, lambda: ri(1, N), 4 * 10 ** 5, 6 * 10 ** 5), wide(N - P, list(range(1, N - P + 1)), 4 * 10 ** 5, 6 * 10 ** 5, S)))  # ties with pillars
add([(i, 4 * 10 ** 5 - i, 1 + i // 50) for i in range(1, N + 1)])                             # nested, rising with ties
add(wide(N, rising(N, 1, 5), 4 * 10 ** 5, 6 * 10 ** 5, S))                                           # many equal heights
add([(N + 1 - i, N + i, i) for i in range(1, N + 1)])                                         # growing boards, each covers all before

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
    assert len(t) <= 3_100_000
assert len(tests) <= 35 and sum(map(len, tests)) <= 40 * 10 ** 6
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
