# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A row is (s, a, b): s parts in stock, a parts per robot of model 1, b parts per robot of model 2.
# Most big tests are a few "core" rows that decide the answer plus many "filler" rows; many tests have
# totals where t * a or t * b no longer fits in 64 bits, and close_costs() keeps only cores where the usual
# ternary searches over the number of model-1 robots give a wrong total.
import os, random

random.seed(2023416)
rnd = random.random
MAXN, MAXS, MAXA = 50000, 10 ** 18, 10 ** 9
tests = []


def ri(lo, hi):
    return lo + int(rnd() * (hi - lo + 1))


def add(rows, shuffle=True):
    rows = list(rows)
    if shuffle:
        n = len(rows)
        # small tests: a full shuffle; big tests: only the first rows (the core rows) go to random places
        for i in range(n - 1 if n <= 2000 else 64):
            j = i + int(rnd() * (n - i))
            rows[i], rows[j] = rows[j], rows[i]
    assert 1 <= len(rows) <= MAXN
    for s, a, b in rows:
        assert 1 <= s <= MAXS and 1 <= a <= MAXA and 1 <= b <= MAXA
    tests.append("%d\n" % len(rows) + "".join("%d %d %d\n" % r for r in rows))


def through(p, q, a, b, slack):
    """a row that allows p robots of model 1 with q of model 2 and a little more (slack)"""
    return (min(MAXS, p * a + q * b + slack), a, b)


def near_point(n, p, q, amax, slackmax):
    """n rows that all pass close to the point (p, q)"""
    return [through(p, q, ri(1, amax), ri(1, amax), ri(0, slackmax)) for _ in range(n)]


def filler(n, amax, smin):
    """rows that only matter for very large totals: small a, b and a big stock"""
    return [(ri(smin, MAXS), ri(1, amax), ri(1, amax)) for _ in range(n)]


def crossing(p, q, big, slack):
    """two steep rows through (p, q): one cheap for model 1, one cheap for model 2"""
    return [through(p, q, ri(1, 3), ri(big // 2, big), ri(0, slack)),
            through(p, q, ri(big // 2, big), ri(1, 3), ri(0, slack))]


def only_cheap(n, ans, bmax):
    """every row has a <= b, so model 1 alone is best; one row allows exactly ans robots and only just"""
    a0 = ri(1, 1000)
    rows = [((ans + 1) * a0 - ri(1, a0), a0, ri(a0 + 2, bmax))]
    for _ in range(n - 1):
        a = ri(1, bmax)
        rows.append(((ans + 1) * a + ri(0, a), a, min(MAXA, a + ri(0, bmax))))
    return rows


def ternary_fails(rows):
    """True if each of three common ternary searches over the number of model-1 robots miss the best total"""
    def f(p):
        return p + min((s - p * a) // b for s, a, b in rows)

    def search(rule):
        lo, hi = 0, min(s // a for s, a, b in rows)
        while hi - lo > 2:
            m1, m2 = lo + (hi - lo) // 3, hi - (hi - lo) // 3
            lo, hi = rule(lo, hi, m1, m2, f(m1), f(m2))
        return max(f(p) for p in range(lo, hi + 1))

    rules = [lambda lo, hi, m1, m2, f1, f2: (m1 + 1, hi) if f1 < f2 else (lo, m2),
             lambda lo, hi, m1, m2, f1, f2: (m1, hi) if f1 <= f2 else (lo, m2),
             lambda lo, hi, m1, m2, f1, f2: (m1 + 1, hi) if f1 < f2 else (lo, m2 - 1)]
    got = [search(r) for r in rules]
    # the true best total: the largest t for which some p works, found from the rows directly
    lo, hi = 0, min(s // min(a, b) for s, a, b in rows)
    while lo < hi:
        t = (lo + hi + 1) // 2
        kl, kh = 0, t
        for s, a, b in rows:
            if a >= b:
                kh = min(kh, (s - t * b) // (a - b)) if a > b else (kh if t * b <= s else -1)
            else:
                kl = max(kl, -((s - t * a) // (b - a)) + t)
        if kl <= kh:
            lo = t
        else:
            hi = t - 1
    return all(g != lo for g in got)


def close_costs(n, amax, mult, d):
    """a few rows where the two models cost almost the same decide the answer; the rest are filler"""
    while True:
        p, q = ri(mult // 10, mult), ri(mult // 10, mult)
        core = []
        for _ in range(6):
            b = ri(amax // 2, amax - d)
            a = b - ri(1, d) if rnd() < 0.5 else b + ri(1, d)
            core.append((min(MAXS, p * a + q * b + ri(0, b)), a, b))
        if ternary_fails(core):
            return core + filler(n - len(core), 3, MAXS // 2)


aux = random.Random(68)   # the filler of precision_trap() has its own stream


def precision_trap(t, big, q):
    """at t robots the smallest number of model-1 robots is (t * big - s) / (big - 1) = t - q + 1 / (big - 1), just
    above t - q, while the other core row allows at most t - q of them: t is impossible, t - 1 is the answer.
    In 64-bit floating point the ratio rounds to t - q, so t looks possible."""
    core = [(q * (big - 1) + t - 1, 1, big), (2 * t - q, 2, 1)]
    return core + [(97 * 10 ** 16 + int(aux.random() * 3 * 10 ** 16), 1 + int(aux.random() * 2), 1 + int(aux.random() * 2))
                   for _ in range(N - 2)]


N = MAXN
# samples
add([(24, 5, 2), (33, 2, 4), (30, 4, 1)], False)
add([(30, 4, 3), (20, 2, 3)], False)
add([(120, 2, 8), (182, 7, 1), (68, 2, 4), (132, 3, 2)], False)
add([(5, 2, 7), (100, 1, 1), (3, 4, 4)], False)
add([(262803281, 988, 635), (518691364, 859, 115), (820922582, 895, 165), (271154377, 876, 705),
     (145944372, 408, 898)], False)
# hidden: small (brute checks these)
add([(11, 5, 2)])                                                   # one row, only model 2
add([(ri(1, 300), ri(1, 12), ri(1, 12)) for _ in range(8)])
add([(ri(100, 2000), ri(1, 30), ri(1, 30)) for _ in range(30)])
add(near_point(40, 37, 52, 20, 3))
add(near_point(2000, 600, 250, 50, 10) + filler(200, 50, 10 ** 5))
add([(ri(10 ** 4, 10 ** 5), ri(1, 50), ri(1, 50)) for _ in range(2000)] + [(ri(1, 6), 7, 9)])   # answer 0
# hidden: big values, few rows
add([(MAXS, 1, 1)])
add(crossing(ri(10 ** 8, 5 * 10 ** 8), ri(10 ** 8, 5 * 10 ** 8), MAXA, 10 ** 9))
add([(MAXS - ri(0, 10 ** 6), MAXA, ri(1, 5)), (MAXS - ri(0, 10 ** 6), ri(1, 5), MAXA), (MAXS, 2, 3)])
add([(MAXS - 1, 1, 1), (MAXS, 2, 1)])
# hidden: big (N = 50000)
add(near_point(N, ri(10 ** 8, 4 * 10 ** 8), ri(10 ** 8, 4 * 10 ** 8), MAXA, MAXA))
add([(ri(5 * 10 ** 17, MAXS), ri(1, 10), ri(MAXA // 10, MAXA)) for _ in range(N)])   # model 1 uses few parts
add(near_point(N, ri(10 ** 16, 10 ** 17), ri(10 ** 16, 10 ** 17), 4, 3))
add([(ri(9 * 10 ** 17, MAXS), ri(1, 3), ri(MAXA // 2, MAXA)) for _ in range(N)])   # model 1 uses few parts
add(crossing(ri(10 ** 8, 4 * 10 ** 8), ri(10 ** 8, 4 * 10 ** 8), MAXA, 10 ** 8) + filler(N - 2, 9, 9 * 10 ** 17))
add(crossing(ri(10 ** 6, 10 ** 7), ri(10 ** 8, 10 ** 9), MAXA, 10 ** 6) + filler(N - 2, 9, 5 * 10 ** 17))
add(crossing(ri(10 ** 2, 10 ** 3), ri(10 ** 2, 10 ** 3), MAXA, 10 ** 9) + filler(N - 2, 1000, 10 ** 17))
add([(ri(MAXS // 2, MAXS), ri(1, MAXA), ri(1, MAXA)) for _ in range(N)])
# (test 24 used to be the line below; its rows are still drawn so the later tests keep the same random stream)
_ = [(ri(MAXS // 2, MAXS), ri(1, 10), ri(1, 10)) for _ in range(N)]
add(precision_trap(326397517784163999, 911391326, 293841254))     # k from a ratio just above an integer
p, q = ri(10 ** 17, 2 * 10 ** 17), ri(10 ** 17, 2 * 10 ** 17)
add([through(p, q, 2, 1, ri(0, 1)), through(p, q, 1, 2, ri(0, 1))] + filler(N - 2, 1, 6 * 10 ** 17))
x = ri(10 ** 5, 10 ** 6)
add([(ri(10 ** 12, MAXS), x, x) for _ in range(N)])                 # both models need the same parts
add(only_cheap(N, ri(10 ** 11, 10 ** 12), 10 ** 6))                # model 1 is never worse, one row decides
add([(s, b, a) for s, a, b in only_cheap(N, ri(10 ** 8, 10 ** 9), 10 ** 4)])   # model 2 is never worse
add([(ri(1, MAXA - 1), MAXA, MAXA)] + near_point(N - 1, 3 * 10 ** 8, 2 * 10 ** 8, MAXA, 10 ** 8))   # answer 0
for amax, mult, d in [(MAXA, 10 ** 9, 1000), (MAXA, 10 ** 9, 30), (10 ** 7, 10 ** 11, 100), (10 ** 9, 10 ** 9, 10 ** 4),
                      (10 ** 6, 10 ** 12, 10)]:
    add(close_costs(N, amax, mult, d))                              # the two models cost almost the same
add([(s, b, a) for s, a, b in precision_trap(465392386453165566, 910813867, 360400983)])   # the same trap for the number of model-2 robots

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
