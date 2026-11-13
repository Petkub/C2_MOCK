# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Most big tests are built from the levels Q_1..Q_N of one day measured from its start without the floor
# (p_i = Q_i - Q_(i-1)); Q_N is the net change of a day.
import os, random

random.seed(802018)
rnd = random.random
MAXN, MAXH, MAXP = 10000, 10 ** 12, 10 ** 12
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(h, p):
    n = len(p)
    assert 1 <= n <= MAXN and 1 <= h <= MAXH
    assert all(-MAXP <= x <= MAXP for x in p)
    tests.append(f"{n} {h}\n" + " ".join(map(str, p)) + "\n")


def from_levels(q):
    p, prev = [], 0
    for x in q:
        p.append(x - prev)
        prev = x
    return p


def band(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def walk(n, lo, hi, step, start=0):
    out, x = [], start
    for _ in range(n):
        x += ri(-step, step)
        if x < lo:
            x = 2 * lo - x
        if x > hi:
            x = 2 * hi - x
        out.append(x)
    return out


def peaks(p):
    """the highest level on day 1 and on day 2"""
    w, best = 0, []
    for _ in range(2):
        m = 0
        for x in p:
            w = max(0, w + x)
            m = max(m, w)
        best.append(m)
    return best


def big_h():
    return MAXH - ri(0, 10 ** 9)


N = MAXN
# samples
add(12, [6, -3, 2])
add(5, [3, -4])
add(7, [2])
add(25, [3, 4, -6, 2])
add(1020, [120, -50, 80, -100, 90, -30])
# hidden: small and medium (brute checks these)
add(5, [-3])
add(11, [8, -12, 9, -6])                                            # day 2, net change < 0
add(9, [5, -2, 6, -20])                                             # day 1, net change < 0
add(1, [0, 0, 1])
add(ri(200, 400), [ri(-30, 30) for _ in range(ri(5, 12))] + [40])  # small, many days
q = walk(2000, -5000, 5000, 400)
q[-1] = 37
add(ri(5 * 10 ** 6, 10 ** 7), from_levels(q))                       # medium, the floor on day 1
q = walk(1500, -3000, 3000, 300) + [-1]
add(max(peaks(from_levels(q))) + 1, from_levels(q))                 # net change < 0, never
q = [ri(1, 9000) for _ in range(1200)] + [-ri(1, 50)]
add(max(q) + ri(1, 40), from_levels(q))                             # net change < 0, never (only by a little)
q = [-ri(0, 10 ** 6)] + walk(800, -10 ** 6, 10 ** 6, 10 ** 5)
q[-1] = 0
add(ri(10 ** 6, 3 * 10 ** 6), from_levels(q))                       # net change 0
# hidden: H up to 10^12 with tiny N
add(MAXH, [1])
add(MAXH - 1, [MAXP, -MAXP, 3])
add(MAXH, [-MAXP, MAXP - 1])                                       # never
# hidden: big (N = 10000)
add(big_h(), from_levels(band(N - 1, 0, 5 * 10 ** 11) + [1]))
add(big_h(), from_levels(band(N - 1, -4 * 10 ** 11, 4 * 10 ** 11) + [7]))
add(big_h(), from_levels(walk(N - 1, -3 * 10 ** 11, 3 * 10 ** 11, 10 ** 9) + [3]))
q = [-6 * 10 ** 11] + band(N - 2, -6 * 10 ** 11, 3 * 10 ** 11) + [5]
add(big_h(), from_levels(q))                                        # deep dip in step 1
q = walk(N - 1, -10 ** 5, 10 ** 5, 1000) + [2]
add(big_h(), from_levels(q))                                        # small moves, about 5 * 10^11 days
q = [0] * (N - 1) + [1]
for _ in range(30):
    q[ri(0, N - 2)] = ri(-10 ** 11, 10 ** 11)
add(big_h(), from_levels(q))                                        # mostly zeros
q = band(N - 1, -4 * 10 ** 11, 0) + [9]
add(big_h(), from_levels(q))                                        # highest level at the end of the day
q = band(N - 1, -10 ** 11, 10 ** 11)
q[0] = 2 * 10 ** 11
q.append(ri(10 ** 9, 10 ** 10))
add(big_h(), from_levels(q))                                        # a few hundred days
q = band(N - 1, -5 * 10 ** 11, 5 * 10 ** 11) + [ri(10 ** 11, 3 * 10 ** 11)]
add(big_h(), from_levels(q))                                        # a few days, net change large
q = walk(N - 1, -2 * 10 ** 11, 2 * 10 ** 11, 5 * 10 ** 10) + [ri(10 ** 7, 10 ** 8)]
add(big_h(), from_levels(q))                                        # thousands of days
q = band(N - 1, -10 ** 8, 10 ** 8) + [ri(10 ** 5, 10 ** 6)]
add(big_h(), from_levels(q))                                        # about 10^6 days
q = band(N - 1, -10 ** 11, 4 * 10 ** 11) + [ri(1000, 10000)]
add(big_h(), from_levels(q))                                        # about 10^8 days
# net change <= 0
a, h = N // 3, big_h()
q = band(a - 1, 0, 5 * 10 ** 11) + [6 * 10 ** 11]                  # day 1 reaches 6 * 10^11
q += band(a, -4 * 10 ** 11, 0) + [-6 * 10 ** 11]                    # empties the tank
q += band(N - 2 * a - 2, -6 * 10 ** 11, -2 * 10 ** 11) + [-ri(1, 10 ** 9)]
add(h, from_levels(q))                                              # day 2
q = walk(N - 101, 0, 3 * 10 ** 11, 2 * 10 ** 8) + band(99, -5 * 10 ** 11, -10 ** 11) + [-5 * 10 ** 11, -10 ** 11]
a, b = peaks(from_levels(q))
assert a < b
add(ri(a + 1, b), from_levels(q))                                   # day 2
q = band(N - 1, 10 ** 11, 9 * 10 ** 11) + [-ri(1, 10 ** 11)]
q[ri(1000, 8000)] = MAXH
add(big_h(), from_levels(q))                                        # day 1
q = walk(N - 1, -4 * 10 ** 11, 4 * 10 ** 11, 2 * 10 ** 11) + [0]
add(max(peaks(from_levels(q))) + ri(1, 10), from_levels(q))         # net change 0, never
q = band(N - 1, -3 * 10 ** 11, 4 * 10 ** 11) + [-ri(1, 10 ** 11)]
add(max(peaks(from_levels(q))) + 1, from_levels(q))                # never
q = walk(N - 2001, 0, 4 * 10 ** 11, 10 ** 9) + band(1999, -3 * 10 ** 11, 0) + [-4 * 10 ** 11, 0]
a, b = peaks(from_levels(q))
assert a < b
add(ri(a + 1, b), from_levels(q))                                   # net change 0, day 2

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
