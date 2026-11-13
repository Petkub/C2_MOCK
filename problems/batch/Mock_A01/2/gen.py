# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(16101)
MAXQ, BIG = 10000, 10 ** 18
MAXR, MAXB = 10 ** 9, 10 ** 18
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only rnd(), so every Python version gives the same tests)"""
    if b - a < 2 ** 40:
        return a + int(rnd() * (b - a + 1))
    return a + (int(rnd() * 2 ** 30) * 2 ** 30 + int(rnd() * 2 ** 30)) % (b - a + 1)


def mag(lo, hi):
    """a value with a random number of digits in [lo, hi]"""
    e = ri(0, 18)
    v = ri(10 ** e, 10 ** (e + 1) - 1)
    return max(lo, min(hi, v))


def add(qs):
    assert 1 <= len(qs) <= MAXQ
    for a, r, b, C, n in qs:
        assert 1 <= a <= C <= BIG and 1 <= r <= MAXR and 0 <= b <= MAXB and 1 <= n <= BIG
    tests.append(f"{len(qs)}\n" + "".join(f"{a} {r} {b} {C} {n}\n" for a, r, b, C, n in qs))


def cap_day(a, r, b, C):
    """first day whose value is C (None if never)"""
    x, d = a, 1
    if r == 1:
        if a == C:
            return 1
        if b == 0:
            return None
        return (C - a + b - 1) // b + 1
    while x < C:
        x = min(C, r * x + b)
        d += 1
    return d


def near(a, r, b, C, n_max=BIG):
    """n next to the first capped day (or random if never capped)"""
    d = cap_day(a, r, b, C)
    if d is None:
        return mag(1, n_max)
    return max(1, min(BIG, d + ri(-2, 2)))


def q_slow_ap():
    """r = 1 with a small step: the value grows for a very long time"""
    C = ri(BIG // 10, BIG)
    a = ri(1, 1000)
    b = ri(1, 1000)
    n = ri(BIG // 2, BIG) if rnd() < 0.7 else near(a, 1, b, C)
    return (a, 1, b, C, n)


def q_ap():
    C = mag(1, BIG)
    a = ri(1, C) if rnd() < 0.5 else mag(1, C)
    b = pick([0, ri(1, 10), mag(0, MAXB), C - a, C - a + 1, ri(0, max(0, C - a))])
    n = near(a, 1, b, C) if rnd() < 0.5 else mag(1, BIG)
    return (a, 1, b, C, n)


def q_geo():
    C = ri(BIG // 100, BIG) if rnd() < 0.6 else mag(1, BIG)
    a = mag(1, C) if rnd() < 0.5 else ri(max(1, C // 3), C)
    r = pick([2, 3, ri(2, 100), mag(2, MAXR), MAXR])
    b = pick([0, ri(0, 100), mag(0, MAXB), mag(0, C)])
    n = near(a, r, b, C) if rnd() < 0.5 else mag(1, BIG)
    return (a, r, b, C, n)


def q_edge():
    k = ri(0, 5)
    if k == 0:                                        # already full
        C = mag(1, BIG)
        return (C, ri(1, MAXR), mag(0, MAXB), C, mag(1, BIG))
    if k == 1:                                        # never changes
        C = mag(2, BIG)
        return (ri(1, C - 1), 1, 0, C, mag(1, BIG))
    if k == 2:                                        # full from the second day
        C = mag(1, BIG)
        return (ri(1, C), ri(1, MAXR), ri(C, MAXB) if C < MAXB else MAXB, C, mag(1, BIG))
    if k == 3:                                        # largest values everywhere
        return (pick([1, BIG - 1, BIG]), pick([1, 2, MAXR]), pick([0, 1, MAXB]), BIG, BIG)
    if k == 4:                                        # values just below C before the cap (overflow of r x)
        C = BIG - ri(0, 10)
        return (C - ri(1, 1000), ri(2, MAXR), ri(0, 1000), C, mag(1, BIG))
    C = ri(BIG // 2, BIG)
    return (ri(1, 10), 1, ri(10 ** 9, 10 ** 12), C, BIG)


def q_below_cap(n_max=BIG):
    """r x + b lands just below a huge C (a check done in double rounds it up to C)"""
    C = ri(BIG // 2, BIG)
    r = pick([2, 3, ri(2, 100)])
    b = ri(0, 1000)
    a = (C - ri(1, 64) - b) // r
    return (a, r, b, C, ri(2, n_max))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def mix(n, w):
    kinds = [q_slow_ap, q_ap, q_geo, q_edge]
    out = []
    for _ in range(n):
        x, i = rnd() * sum(w), 0
        while x >= w[i]:
            x -= w[i]
            i += 1
        out.append(kinds[i]())
    return out


def small(n, nmax):
    """small n for the brute-force check"""
    out = []
    for _ in range(n):
        C = mag(1, BIG) if rnd() < 0.6 else ri(1, 1000)
        a = ri(1, C) if rnd() < 0.5 else ri(max(1, C - 50), C)
        r = pick([1, 1, 2, 3, ri(1, 50), mag(1, MAXR)])
        b = pick([0, ri(0, 20), mag(0, MAXB), mag(0, C)])
        out.append((a, r, b, C, ri(1, nmax)))
    return out


# samples
add([(3, 2, 1, 50, 6), (3, 2, 1, 50, 2)])
add([(10, 1, 5, 32, 7), (2, 3, 4, 1000, 5)])
add([(1, 3, 0, 1000000, 20), (6, 1, 4, 20, 5), (5, 10, 2, 6, 10)])
add([(2, 1, 3, 20, 10), (7, 2, 5, 100000, 30), (1, 1, 1, 1000, 1000)])
add([(4, 5, 1, 30, 3), (100, 1, 250, 1000, 8), (3, 1000, 7, 100000000, 4)])
# hidden: small n (checked by brute force)
add([(a, r, b, C, n) for a in (1, 2, 5) for r in (1, 2, 3) for b in (0, 1, 4) for C in (5, 6, 30)
     for n in (1, 2, 3, 7) if a <= C])
add(small(400, 30))
add(small(300, 2000))
add(small(30, 100000))
add([(x[0], x[1], x[2], x[3], ri(1, 50)) for x in [q_edge() for _ in range(300)]])
add([(ri(1, 1000), 1, ri(0, 3), ri(10 ** 5, 10 ** 6), ri(10 ** 5, 10 ** 6)) for _ in range(5)])
# hidden: big (every big test has slowly growing r = 1 queries)
add([q_slow_ap() for _ in range(MAXQ)])
add([(1, 1, 1, BIG, BIG)] * MAXQ)
add(mix(MAXQ, [1, 1, 1, 1]))
add(mix(MAXQ, [1, 3, 3, 3]))
add(mix(MAXQ, [1, 0, 5, 1]))
add(mix(MAXQ, [1, 5, 0, 1]))
add(mix(MAXQ, [1, 1, 1, 4]))
add(mix(MAXQ, [1, 2, 6, 2]))
add(mix(MAXQ, [2, 2, 2, 2]))
add([q_geo() for _ in range(MAXQ - 10)] + [q_slow_ap() for _ in range(10)])
add([q_ap() for _ in range(MAXQ - 10)] + [q_slow_ap() for _ in range(10)])
add([q_edge() for _ in range(MAXQ - 10)] + [q_slow_ap() for _ in range(10)])
add([(BIG - ri(0, 5), pick([2, MAXR]), ri(0, 5), BIG, BIG - ri(0, 5)) for _ in range(MAXQ // 2)]
    + [q_slow_ap() for _ in range(MAXQ // 2)])
add(mix(MAXQ, [1, 2, 2, 1]))
add(mix(MAXQ, [3, 1, 1, 1]))
add(mix(MAXQ, [1, 1, 3, 1]))
add(mix(MAXQ, [1, 2, 1, 3]))
add(mix(MAXQ, [1, 4, 4, 0]))
add(mix(MAXQ, [2, 1, 3, 1]))
add(mix(MAXQ, [1, 3, 1, 2]))
add(mix(MAXQ, [2, 3, 2, 3]))
add([q_slow_ap() if rnd() < 0.5 else q_geo() for _ in range(MAXQ)])
# hidden: r x + b just below C (added by the v7 solve-evaluation)
add([q_below_cap(5) for _ in range(2000)])
add([q_below_cap() if rnd() < 0.5 else q_slow_ap() for _ in range(MAXQ)])

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
