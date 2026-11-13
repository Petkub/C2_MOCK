# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A test is c_0..c_4 and the wheels [a_i, b_i]. The number of outcomes (product of the widths) times max(c) is kept
# <= 4 * 10^18, which bounds the answer. Big tests: N = 50 000, most wheels fixed (a_i = b_i), a few wide ones at random
# positions; wheels of width up to 2 * 10^9 + 1 make a loop over every value of every wheel too slow.
import os, random

random.seed(2012005)
rnd = random.random
MAXN, MAXV, MAXC, MAXANS = 50000, 10 ** 9, 10 ** 9, 4 * 10 ** 18
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(c, wheels):
    n = len(wheels)
    assert 1 <= n <= MAXN and len(c) == 5 and all(1 <= x <= MAXC for x in c)
    prod = 1
    for a, b in wheels:
        assert -MAXV <= a <= b <= MAXV
        prod *= b - a + 1
    assert prod * max(c) <= MAXANS
    tests.append(f"{n}\n" + " ".join(map(str, c)) + "\n" + "".join(f"{a} {b}\n" for a, b in wheels))


def wheel(w, lo=-MAXV, hi=MAXV):
    """a wheel of width w with both ends in [lo, hi]"""
    a = ri(lo, hi - w + 1)
    return (a, a + w - 1)


def fixed(lo=-MAXV, hi=MAXV):
    x = ri(lo, hi)
    return (x, x)


def big(widths, c, lo=-MAXV, hi=MAXV, n=MAXN):
    """n wheels: the given widths at random positions, the rest fixed"""
    ws = [wheel(w, lo, hi) for w in widths]
    ws += [fixed(lo, hi) for _ in range(n - len(ws))]
    random.shuffle(ws)
    add(c, ws)


def nz(w):
    """a width that is not a multiple of 5 (one such wheel would make every remainder equally likely)"""
    return w if w % 5 else w - 1


def fill(budget, wmin, wmax):
    """random widths in [wmin, wmax] (log-uniform, no multiple of 5) while their product stays <= budget"""
    out, prod = [], 1
    while True:
        w = nz(int(wmin * (wmax / wmin) ** rnd()))
        if prod * w > budget:
            w = nz(budget // prod)
            if w >= 2:
                out.append(w)
            return out
        out.append(w)
        prod *= w


def cs(hi):
    return [ri(1, hi) for _ in range(5)]


# samples
add([1, 2, 3, 4, 5], [(1, 3), (2, 4)])
add([7, 1, 2, 9, 3], [(-4, 0), (6, 6)])
add([3, 1, 4, 1, 5], [(-7, 7)])
add([10, 20, 30, 40, 50], [(-12, -9), (100, 101), (-3, 5), (8, 8)])
add([5, 8, 2, 6, 4], [(-100, 100), (37, 61), (-25, -1), (12, 12), (-9, 9)])
# hidden: small (brute checks these)
add(cs(10 ** 9), [(-999999998, -999999998)])
add(cs(100), [wheel(ri(1, 7), -30, 30) for _ in range(6)])
add(cs(1000), [wheel(ri(1, 4), -40, -1) for _ in range(10)])
add(cs(10 ** 6), [wheel(ri(1, 3), MAXV - 50, MAXV) if rnd() < 0.5 else wheel(ri(1, 3), -MAXV, -MAXV + 50)
                  for _ in range(14)])
add(cs(10 ** 9), [wheel(ri(150, 200), -500, 500) for _ in range(3)])
# medium
add(cs(4 * 10 ** 8), [(-MAXV, MAXV)])
big(fill(10 ** 15, 2, 40), cs(1000), n=1000)
# big: one wheel over (almost) the whole range plus another wide one; up to about 4 * 10^9 values in all, so a loop
# over every value of every wheel is far too slow
w = 2 * MAXV + 1 - ri(0, 1000)
big([w, nz(min(2 * MAXV + 1, MAXANS // w) - ri(0, 10 ** 5))], [1] * 5)
big([2 * MAXV - 2, nz(MAXANS // 2 // (2 * MAXV - 2) - ri(0, 10 ** 5))], cs(2))
big([MAXV - 1, MAXV - 2, 4], [1, 1, 1, 1, 1], -MAXV, -1)              # answer just below 4 * 10^18
big([nz(2 * MAXV - ri(0, 10 ** 6)), nz(ri(10 ** 6, 3 * 10 ** 6))] + [3, 2, 4], cs(5))
w = nz(2 * MAXV + 1 - ri(0, 10 ** 6))
big([w, nz(ri(19 * 10 ** 8, min(2 * MAXV + 1, MAXANS // w))), 1], cs(1))
big([nz(ri(155 * 10 ** 7, 16 * 10 ** 8)), nz(ri(15 * 10 ** 8, 16 * 10 ** 8))], cs(1), -MAXV, 6 * 10 ** 8)  # mostly negative
# big: many small widths
big([5] * 25, cs(3))                                                 # every remainder equally likely
big([2] * 56, cs(10))
big([3] * 28 + [4] * 5, cs(30), -MAXV, -1)
big(fill(10 ** 12, 2, 9), [10 ** 6 - ri(0, 100) for _ in range(5)])
big(fill(10 ** 16, 2, 1000), cs(100))
big(fill(10 ** 17, 6, 10 ** 6), cs(10), -MAXV, MAXV // 10)
big(fill(10 ** 13, 7, 5 * 10 ** 4), cs(10 ** 5), -MAXV, -1)
big(fill(10 ** 18 // 50, 1000, 10 ** 8), cs(50))
big(fill(10 ** 14, 2, 20), cs(10 ** 4), -1000, 1000)
big(fill(10 ** 17, 2, 2 * MAXV), cs(8))
# big: every wheel fixed
big([], cs(MAXC))
big([], cs(MAXC), -MAXV, -1)
# big: two wheels over almost the whole range (about 4 * 10^9 values in all)
for _ in range(3):
    w1 = nz(2 * MAXV + 1 - ri(0, 100))
    big([w1, nz(min(2 * MAXV + 1, MAXANS // w1))], [1] * 5)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
