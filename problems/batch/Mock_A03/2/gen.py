# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A test is (m, s, q, d): shops (minimum quality, price) and pieces (quality, cost).
import os, random

random.seed(1202024)
rnd = random.random
MAXN, MAXV = 100000, 10 ** 6
V5 = 10 ** 5 - 1
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(m, s, q, d):
    c, p = len(m), len(q)
    assert 1 <= c <= MAXN and 1 <= p <= MAXN and len(s) == c and len(d) == p
    assert all(0 <= x <= MAXV for x in m + s + q + d)
    lines = [f"{c} {p}"] + [" ".join(map(str, a)) for a in (m, s, q, d)]
    tests.append("\n".join(lines) + "\n")


def vals(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def rising(m, lo, hi, noise, top=MAXV):
    """price grows with the minimum quality (better shops pay more), plus noise; top = the largest quality"""
    return [min(MAXV, max(0, lo + (hi - lo) * x // top + ri(-noise, noise))) for x in m]


def falling(m, lo, hi, noise):
    return [min(MAXV, max(0, hi - (hi - lo) * x // MAXV + ri(-noise, noise))) for x in m]


def small(cmax, pmax, vmax):
    c, p = ri(1, cmax), ri(1, pmax)
    add(vals(c, 0, vmax), vals(c, 0, vmax), vals(p, 0, vmax), vals(p, 0, vmax))


# samples
add([2, 5, 8], [4, 9, 7], [6, 3, 9, 1], [3, 5, 2, 2])
add([4, 7], [3, 5], [2, 8, 5], [1, 6, 4])
add([5, 0, 3, 7], [6, 2, 5, 11], [3, 8, 5, 1, 7], [1, 4, 2, 0, 9])
add([10, 20, 15, 30, 25], [100, 120, 90, 200, 150], [12, 31, 18, 26, 9, 22], [30, 150, 95, 60, 20, 40])
add([300, 120, 450, 80, 600, 250], [40, 55, 70, 35, 95, 60], [500, 100, 260, 700, 90, 330, 50],
    [30, 50, 20, 100, 10, 65, 5])
# hidden: tiny and small (brute checks these)
add([0], [0], [0], [0])                                              # 0 1
add([MAXV], [MAXV], [MAXV - 1], [0])                                # no shop accepts
add([3, 3, 3], [7, 2, 5], [3, 2, 9], [7, 0, 6])
small(8, 8, 10)
small(30, 30, 20)
small(300, 300, 50)
small(2000, 2000, 1000)
m = vals(3000, 500, 5000)
add(m, rising(m, 0, 10 ** 5, 3000), vals(3000, 0, 6000), vals(3000, 0, 40000))
m = vals(5000, 0, 200)
add(m, vals(5000, 0, 100), vals(5000, 0, 250), vals(5000, 0, 100))  # many equal minima, many zero profits

# hidden: big (C = P = 100000)
# uniform, independent
add(vals(N, 0, MAXV), vals(N, 0, MAXV), vals(N, 0, MAXV), vals(N, 0, MAXV))
# better shops pay more, pieces of every quality
m = vals(N, 0, V5)
add(m, rising(m, 0, V5, 2000, V5), vals(N, 0, V5), vals(N, 0, V5 // 2))
m = vals(N, 0, MAXV)
add(m, rising(m, 2 * 10 ** 5, MAXV, 5000), vals(N, 0, MAXV), vals(N, 0, 3 * 10 ** 5))
# better shops pay more, pieces mostly poor (the strict shops are useless to most pieces)
m = vals(N, 1000, MAXV)
q = [ri(0, 10 ** 5) if rnd() < 0.9 else ri(0, MAXV) for _ in range(N)]
add(m, rising(m, 0, MAXV, 1000), q, vals(N, 0, 2000))
# every piece is excellent: every shop accepts it
# (shops with distinct minima and a strictly higher price for a higher minimum: no shop is ever useless)
m = [9 * i + ri(0, 8) for i in range(N)]
for i in range(N - 1, 0, -1):
    j = ri(0, i)
    m[i], m[j] = m[j], m[i]
add(m, m[:], [MAXV - ri(0, 10) for _ in range(N)], vals(N, 0, MAXV))
add(vals(N, 0, 9 * 10 ** 5), [MAXV - ri(0, 10 ** 4) for _ in range(N)], vals(N, 9 * 10 ** 5, MAXV), vals(N, 0, 1000))
# large total
add([0] * N, [MAXV] * N, [MAXV] * N, [0] * N)
# the least demanding shops pay the most
m = vals(N, 0, MAXV)
add(m, falling(m, 0, MAXV, 50000), vals(N, 0, MAXV), vals(N, 0, MAXV))
# no shop accepts most pieces; many pieces cost nothing
m = vals(N, 5 * 10 ** 5, MAXV)
q = [ri(0, 5 * 10 ** 5 - 1) if rnd() < 0.8 else ri(5 * 10 ** 5, MAXV) for _ in range(N)]
add(m, rising(m, 0, MAXV, 10000), q, [0 if rnd() < 0.5 else ri(0, MAXV) for _ in range(N)])
m = vals(N, 1, 1000)
add(m, vals(N, 0, 1000), [0 if rnd() < 0.3 else ri(0, 1000) for _ in range(N)], [0 if rnd() < 0.4 else ri(0, 1000) for _ in range(N)])
# many equal minimum qualities with different prices; pieces with exactly the minimum quality
m = [ri(0, 999) * 1000 for _ in range(N)]
q = [ri(0, 999) * 1000 + (0 if rnd() < 0.7 else ri(1, 999)) for _ in range(N)]
add(m, vals(N, 0, MAXV), q, vals(N, 0, MAXV))
m = [ri(0, 300) for _ in range(N)]
add(m, vals(N, 0, 300), vals(N, 0, 310), vals(N, 0, 300))
m = vals(N, 0, V5)
add(m, rising(m, 0, V5, 3000, V5), [m[ri(0, N - 1)] for _ in range(N)], vals(N, 0, V5 // 3))
# many pieces with zero profit
m = vals(N, 0, 1000)
s = rising([x * 1000 for x in m], 0, 1000, 20)
add(m, s, vals(N, 0, 1000), vals(N, 0, 1000))
m = vals(N, 0, 100)
add(m, vals(N, 0, 50), vals(N, 0, 100), vals(N, 40, 50))
# few shops / few pieces
add(vals(1, 0, MAXV), vals(1, 0, MAXV), vals(N // 2, 0, MAXV), vals(N // 2, 0, MAXV))
add(vals(N // 2, 0, MAXV), vals(N // 2, 0, MAXV), vals(1, MAXV, MAXV), vals(1, 0, 0))
# (distinct minima, price rising strictly with the minimum; every piece is poor)
m = list(range(N))
add(m, rising(m, 0, MAXV, 0, V5), sorted(vals(N, 0, 2000), reverse=True), vals(N, 0, 2 * 10 ** 4))
# no shop accepts many pieces, small numbers
m = vals(N, 20, 100)
q = [ri(0, 19) if rnd() < 0.4 else ri(20, 100) for _ in range(N)]
add(m, rising(m, 0, 100, 10, 100), q, [0 if rnd() < 0.5 else ri(0, 100) for _ in range(N)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
