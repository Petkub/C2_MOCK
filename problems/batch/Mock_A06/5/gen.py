# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(7065)
rnd = random.random
MAXN, MAXV, MAXC, MAXT, MAXSUM = 100000, 10 ** 6, 10 ** 6, 10 ** 9, 2 * 10 ** 6
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(K, st):
    n = len(st)
    assert 1 <= n <= MAXN
    assert 1 <= K <= MAXV
    tot = 0
    for a, b, c, t in st:
        assert 1 <= a <= b <= MAXV
        assert -MAXC <= c <= MAXC
        assert 1 <= t <= MAXT
        tot += b - a + 1
    assert tot <= MAXSUM
    lines = ["%d %d" % (n, K)] + ["%d %d %d %d" % s for s in st]
    tests.append("\n".join(lines) + "\n")


def small_random(nmax, H, cmax, tmax):
    n = ri(1, nmax)
    K = ri(1, H)
    st = []
    for i in range(n):
        w = [0, 1, 3, H // 3, H][ri(0, 4)]
        a = ri(1, H)
        b = min(H, a + ri(0, w))
        c = ri(-cmax, cmax)
        if i == 0 and rnd() < 0.7:                     # usually something accepts K
            a = max(1, K - ri(0, 3))
            b = min(H, K + ri(0, 3))
        st.append((a, b, c, ri(1, tmax)))
    a = ri(1, H)
    b = min(H, a + ri(0, H // 4))
    if rnd() < 0.5:                                    # low entries to the boss stage kill
        c = ri(a, b)
    else:
        c = ri(-cmax, cmax)
    st[-1] = (a, b, c, ri(1, tmax))
    return K, st


def tiles(L, step, cpick, tpick, lo=1, hi=MAXV):
    """stages [s, s + L - 1] for s = lo, lo + step, ..."""
    out = []
    s = lo
    while s <= hi:
        out.append((s, min(hi, s + L - 1), cpick(), tpick()))
        s += step
    return out


def points(cnt, cpick, tpick, lo=1, hi=MAXV):
    return [(h, h, cpick(), tpick()) for h in (ri(lo, hi) for _ in range(cnt))]


def killers(cnt, lo=1, hi=MAXV, tmax=MAXT):
    """single-health stages that always end the game (C = h)"""
    out = []
    for _ in range(cnt):
        h = ri(lo, hi)
        out.append((h, h, h, ri(1, tmax)))
    return out


def shuffled(st):
    random.shuffle(st)
    return st


def big(K, body, boss):
    st = shuffled(body)
    st.append(boss)
    add(K, st)


# samples
add(10, [(5, 20, 3, 2), (1, 6, -8, 5), (12, 15, 10, 7)])
add(3, [(1, 5, 1, 4), (2, 2, -1, 6), (5, 9, 2, 1)])
add(4, [(2, 6, 2, 3), (1, 3, -5, 4), (7, 9, 1, 2), (6, 8, -3, 10), (8, 12, 6, 5)])
add(5, [(1, 10, -3, 9)])
add(7, [(1, 5, -2, 1), (8, 9, 1, 1), (3, 6, 2, 1)])

# hidden: small (brute checks these)
add(1, [(1, 10, -5, 100), (1, 10, -1, 1), (6, 6, 1, 1)])     # fewest plays is not fastest
add(2, [(1, 10, -1, 1), (5, 10, 8, 1)])                        # low entries to the boss kill
add(4, [(4, 4, 4, 7)])                                         # only the boss, and it kills
add(9, [(1, 8, 1, 1), (2, 5, -3, 4)])                          # nothing accepts K
add(1, [(1, 1, 0, 5), (1, 1, -1, 3), (2, 2, 1, 1), (2, 2, 0, 2)])
for (nmax, H, cmax, tmax) in [(6, 15, 6, 10), (8, 30, 10, 1000), (40, 300, 40, MAXT),
                              (60, 2000, 300, 10 ** 6), (80, 5000, 500, MAXT)]:
    while True:
        K, st = small_random(nmax, H, cmax, tmax)
        if len(st) >= nmax // 2:
            break
    add(K, st)


def cr(a, b):
    return lambda: ri(a, b)


def up(t, lo=1, hi=MAXV - 1):
    """one wide stage that heals 1 (makes every health from K upwards reachable)"""
    return (lo, hi, -1, t)


def down(t, lo=2, hi=MAXV):
    return (lo, hi, 1, t)


# hidden: big
# 1-2: climb from low health to a boss near the top; the low part of the boss range kills
for bc in (992000, 994000):
    body = [up(ri(10 ** 8, MAXT))] + tiles(9, 12, cr(-60, 40), cr(1, MAXT))
    big(ri(1, 100), body, (990000, 995000, bc, ri(1, MAXT)))
# 3: descend from the top to a boss near the bottom that heals
body = [down(ri(10 ** 8, MAXT))] + tiles(9, 12, cr(-30, 60), cr(1, MAXT))
big(MAXV, body, (100, 300, -5, ri(1, MAXT)))
# 4-5: the boss always kills: -1 after exploring everything
for bc in (600000, 500100):
    body = [up(ri(1, MAXT))] + tiles(9, 12, cr(-50, 50), cr(1, MAXT))
    big(ri(1, 1000), body, (500000, 500100, bc, ri(1, MAXT)))
# 6: big expensive heals versus slow cheap heals
body = [(1, 950000, -997, MAXT), (1, 950000, -1, 1)] + killers(69997, 1, 950000)
big(1, body, (900000, 900000, 1, 1))
# 7: the same with random times
body = [(1, 900000, -ri(500, 1500), ri(10 ** 8, MAXT)), (1, 800000, -1, ri(1, 1000)),
        (1, 100000, -3, ri(1, 3000))] + points(79996, cr(-2000, 2000), cr(1, 10 ** 6), 1, 950000)
big(1, body, (895000, 915000, 900000, 1))
# 8: one long walk down, answer near 10^15
body = [down(MAXT)] + killers(59998)
big(MAXV, body, (1, 1, 0, MAXT))
# 9: one long walk up with all times at the maximum
body = [up(MAXT)] + killers(59998, 1, MAXV - 1)
big(1, body, (MAXV, MAXV, MAXV - 1, MAXT))
# 10-11: two wide stages plus many single-health jumps
for _ in range(2):
    body = [(1, MAXV, -1, ri(10 ** 6, 10 ** 7)), (1, 800000, 7, ri(1, 10 ** 5))] + \
           points(79997, cr(-MAXC, MAXC), cr(1, MAXT))
    lo = ri(600000, 800000)
    big(ri(1, 1000), body, (lo, lo + 30000, lo + 10000, ri(1, MAXT)))
# 12-13: short ranges, mostly small steps, some huge jumps
for _ in range(2):
    pick = lambda: ri(-100, 100) if rnd() < 0.97 else ri(-MAXC, MAXC)
    body = [down(ri(10 ** 8, MAXT))] + tiles(9, 12, pick, cr(1, MAXT))
    lo = ri(1, 3000)
    big(ri(900000, MAXV), body, (lo, lo + 2000, lo + 1000, ri(1, MAXT)))
# 14: steps -1, 0, +1 only, boss at the far end
body = [up(ri(10 ** 6, 10 ** 7))] + tiles(9, 12, cr(-1, 1), cr(1, 10 ** 6))
big(1, body, (999000, MAXV, 999500, 1))
# 15: equal times (the fewest plays is also the fastest), climb with steps up to 5
body = [up(1000)] + tiles(9, 12, cr(-5, 3), lambda: 1000)
big(ri(1, 10), body, (980000, 999999, 985000, 1000))
# 16: one stage for every health 1..79 998, nothing else accepts more
body = [up(MAXT, 1, 79998)] + [(h, h, ri(-40, 30), ri(1, MAXT)) for h in range(1, 79999)]
big(ri(1, 1000), body, (79000, 80500, 79500, ri(1, MAXT)))
# 17-18: random ranges of random lengths
for _ in range(2):
    body = [up(ri(10 ** 7, MAXT))]
    room = MAXSUM - MAXV - 50001
    while len(body) < 75000:
        L = ri(1, 20)
        a = ri(1, MAXV - L + 1)
        body.append((a, a + L - 1, ri(-300, 200), ri(1, MAXT)))
        room -= L
    assert room >= 0
    lo = ri(500000, 900000)
    big(ri(1, 1000), body, (lo, lo + 50000, lo + ri(0, 25000), ri(1, MAXT)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
