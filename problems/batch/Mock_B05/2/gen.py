# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A line is kept as a tuple: (1, l, r, c) for a claim, (2, l, r) for a question.
import bisect, os, random
from itertools import accumulate

random.seed(940417)
MAXN, MAXM, MAXC = 200000, 100000, 10 ** 9
tests = []
rand = random.random


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(rand() * (hi - lo + 1))


def add(n, lines):
    m = len(lines)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    for s in lines:
        assert s[0] in (1, 2) and len(s) == 5 - s[0] and 1 <= s[1] <= s[2] <= n
        assert s[0] == 2 or -MAXC <= s[3] <= MAXC
    tests.append(f"{n} {m}\n" + "".join(f"1 {s[1]} {s[2]} {s[3]}\n" if s[0] == 1 else f"2 {s[1]} {s[2]}\n"
                                          for s in lines))


def hidden(n, lo=-1000, hi=1000):
    """a hidden array of day amounts, returned as its prefix sums P[0..n]"""
    w = hi - lo + 1
    return [0] + list(accumulate([lo + int(rand() * w) for _ in range(n)]))


def claim(P, l, r, wrong=False):
    """the true total of days l..r (or a wrong one); totals are clipped to the allowed range"""
    c = P[r] - P[l - 1]
    if wrong:
        c += random.choice((-1, 1)) * ri(1, 1000)
    return (1, l, r, max(-MAXC, min(MAXC, c)))


def mix(claims, queries, tail=0.0):
    """claims keep their order; queries are spread at random positions among them
    (a share `tail` of them after the last claim)"""
    pos = sorted(len(claims) if rand() < tail else ri(0, len(claims)) for _ in range(len(queries)))
    out, j = [], 0
    for i, c in enumerate(claims):
        while j < len(pos) and pos[j] == i:
            out.append(queries[j])
            j += 1
        out.append(c)
    out += queries[j:]
    return out


def chain(n, k, way, P, qn, wrong=0.0):
    """claims [i, i] for i = 1..k in order (way "L"), k..1 (way "R"), or two chains at once: 1..k/2 upwards
    and k..k/2+1 downwards, taking turns (way "B"); after each claim some questions inside a part claimed
    so far (known totals) and a few reaching outside it (UNKNOWN); some claims repeat a claimed range with a
    wrong total"""
    if way == "L":
        order = list(range(1, k + 1))
    elif way == "R":
        order = list(range(k, 0, -1))
    else:
        h = k // 2
        order = [x for pair in zip(range(1, h + 1), range(k, h, -1)) for x in pair]
    lines, parts = [], {}       # parts: side -> [lo, hi] claimed so far
    per, acc, qleft = qn / k, 0.0, qn
    for i in order:
        side = 0 if way != "B" or i <= k // 2 else 1
        if side in parts and rand() < wrong:
            lo, hi = parts[side]
            j = ri(lo, hi)
            lines.append(claim(P, j, min(hi, j + ri(0, 50)), True))
        lo, hi = parts.get(side, (i, i))
        parts[side] = (min(lo, i), max(hi, i))
        lines.append(claim(P, i, i))
        acc += per
        while acc >= 1 and qleft > 0:
            acc -= 1
            qleft -= 1
            if rand() < 0.1:
                l = ri(1, n)
                lines.append((2, l, ri(l, n)))
            else:
                lo, hi = parts[random.choice(sorted(parts))]
                l, r = ri(lo, hi), ri(lo, hi)
                lines.append((2, min(l, r), max(l, r)))
    return lines[:MAXM]


def grow(n, k, P, qn, bmax=1, wrong=0.0, tail=0.0):
    """the known part grows from the middle, each claim adds a block of 1..bmax days on a random side"""
    lo = hi = n // 2           # prefix points lo..hi are tied together
    cl = []
    for _ in range(k):
        if lo == 0 and hi == n:
            break
        if (rand() < 0.5 and lo > 0) or hi == n:
            b = min(lo, ri(1, bmax))
            cl.append(claim(P, lo - b + 1, lo))
            lo -= b
        else:
            b = min(n - hi, ri(1, bmax))
            cl.append(claim(P, hi + 1, hi + b))
            hi += b
    # each question is drawn among the points tied together at its position in the list
    out = mix(cl, [None] * qn, tail)
    lo = hi = n // 2
    left, right = [], []        # tied points below lo..., above hi... (besides n // 2)
    res = []

    def point(i):
        return n // 2 if i == 0 else (left[i - 1] if i <= len(left) else right[i - 1 - len(left)])

    for s in out:
        if s is None:
            k = len(left) + len(right) + 1
            if rand() < 0.08 or k == 1:
                l = ri(1, n)
                res.append((2, l, ri(l, n)))
            else:
                a, b = point(ri(0, k - 1)), point(ri(0, k - 1))
                while a == b:
                    a, b = point(ri(0, k - 1)), point(ri(0, k - 1))
                res.append((2, min(a, b) + 1, max(a, b)))
                if rand() < wrong:
                    res.append(claim(P, min(a, b) + 1, max(a, b), True))
        else:
            res.append(s)
            if s[1] - 1 < lo:
                lo = s[1] - 1
                left.append(lo)
            if s[2] > hi:
                hi = s[2]
                right.append(hi)
    return res[:MAXM]


def scatter(n, k, P, qn, wrong=0.0, tail=0.0, near=False, path=0):
    """k + 1 prefix points in random order; each claim ties the next point to a point tied before:
    a random one, one of the `path` latest ones, or (near) its nearest neighbour among the tied points,
    the points then lying close together (2k + 2 consecutive prefix points); questions between tied points"""
    if near:
        off = ri(0, n - 2 * k - 1)
        pts = random.sample(range(off, off + 2 * k + 2), k + 1)
        srt = [pts[0]]
    else:
        pts = random.sample(range(0, n + 1), k + 1)
    cl = []
    for t in range(1, k + 1):
        a = pts[t]
        if near:
            i = bisect.bisect(srt, a)
            if i == 0 or (i < len(srt) and srt[i] - a < a - srt[i - 1]):
                b = srt[i]
            else:
                b = srt[i - 1]
            srt.insert(i, a)
        elif path:
            b = pts[t - 1 - ri(0, min(t - 1, path - 1))]
        else:
            b = pts[ri(0, t - 1)]
        cl.append(claim(P, min(a, b) + 1, max(a, b)))
    out = mix(cl, [None] * qn, tail)
    res, t = [], 1          # pts[0..t-1] are tied together
    for s in out:
        if s is None:
            if rand() < 0.05 or t == 1:
                l = ri(1, n)
                res.append((2, l, ri(l, n)))
            else:
                a, b = pts[ri(0, t - 1)], pts[ri(0, t - 1)]
                while a == b:
                    a, b = pts[ri(0, t - 1)], pts[ri(0, t - 1)]
                res.append((2, min(a, b) + 1, max(a, b)))
                if rand() < wrong:
                    res.append(claim(P, min(a, b) + 1, max(a, b), True))
        else:
            res.append(s)
            t += 1
    return res[:MAXM]


def blocks(n, k, P, qn, shuffle, wrong=0.0, tail=0.0):
    """breakpoints 0 = x_0 < x_1 < ... < x_k <= n, claims [x_j + 1, x_(j+1)], questions between breakpoints"""
    xs = [0] + sorted(random.sample(range(1, n + 1), k))
    cl = [claim(P, xs[j] + 1, xs[j + 1]) for j in range(k)]
    if shuffle:
        random.shuffle(cl)
    qs = []
    for _ in range(qn):
        if rand() < 0.85:
            a, b = ri(0, k), ri(0, k)
            while a == b:
                b = ri(0, k)
            qs.append((2, xs[min(a, b)] + 1, xs[max(a, b)]))
        else:
            l = ri(1, n)
            qs.append((2, l, ri(l, min(n, l + 1000))))
    for _ in range(int(qn * wrong)):
        a, b = ri(0, k), ri(0, k)
        while a == b:
            b = ri(0, k)
        qs.append(claim(P, xs[min(a, b)] + 1, xs[max(a, b)], True))
    random.shuffle(qs)
    return mix(cl, qs, tail)[:MAXM]


def points(n, k, P, m, pclaim, wrong=0.0, maxlen=None):
    """random lines whose ends are in a fixed set of k cut points (the claims tie them together quickly)"""
    cut = sorted(random.sample(range(0, n + 1), k))
    lines = []
    for _ in range(m):
        a = ri(0, k - 1)
        b = min(k - 1, a + ri(1, maxlen)) if maxlen else ri(0, k - 1)
        while b == a:
            b = ri(0, k - 1)
        a, b = min(a, b), max(a, b)
        l, r = cut[a] + 1, cut[b]
        lines.append(claim(P, l, r, rand() < wrong) if rand() < pclaim else (2, l, r))
    return lines


def star(n, k, P, qn):
    """claims [1, r] for k random r, questions between those r"""
    rs = random.sample(range(1, n + 1), k)
    cl = [claim(P, 1, r) for r in rs]
    qs = []
    for _ in range(qn):
        a, b = rs[ri(0, k - 1)], rs[ri(0, k - 1)]
        while a == b:
            b = rs[ri(0, k - 1)]
        a, b = min(a, b), max(a, b)
        qs.append((2, a + 1, b) if rand() < 0.8 else (2, 1, b))
    return mix(cl, qs, 0.3)


def small(n, m, pclaim, lo, hi, wrong):
    P = hidden(n, lo, hi)
    lines = []
    for _ in range(m):
        l = ri(1, n)
        r = ri(l, n)
        lines.append(claim(P, l, r, rand() < wrong) if rand() < pclaim else (2, l, r))
    return lines


def parse(text):
    return [tuple(map(int, s.split())) for s in text]


# samples
add(5, parse(["1 1 3 10", "1 4 5 -2", "2 1 5", "1 2 3 4", "2 1 1", "1 1 1 5", "2 2 4"]))
add(3, parse(["2 1 3", "1 1 3 0", "1 1 3 0", "1 1 3 1", "2 1 3"]))
add(4, parse(["1 1 2 -7", "2 2 3", "1 3 4 4", "1 2 3 1", "2 1 4"]))
add(1, parse(["2 1 1", "1 1 1 -1000000000", "2 1 1", "1 1 1 7"]))
add(8, parse(["1 1 4 3", "1 5 8 3", "1 3 6 0", "1 1 8 5", "2 3 8"]))
# hidden: small (brute checks these)
add(10, small(10, 40, 0.6, -5, 5, 0.3))
add(50, small(50, 500, 0.7, -3, 3, 0.4))
add(200, chain(200, 200, "B", hidden(200, MAXC, MAXC), 300, 0.1))     # totals beyond 2^31
add(300, grow(300, 250, hidden(300), 400, 2, 0.1))
add(2000, scatter(2000, 900, hidden(2000, -10 ** 6, 10 ** 6), 6000, 0.2, 0.0, True))
add(5000, blocks(5000, 2000, hidden(5000), 6000, True, 0.1, 0.5))
# hidden: big, N = 200000, M <= 100000
N = MAXN
add(N, scatter(N, 40000, hidden(N, -10 ** 8, 10 ** 8), 40000, 0.05, 0.2, True))
add(N, chain(N, 60000, "L", hidden(N, MAXC - 10, MAXC), 40000))          # totals up to 6 * 10^13
add(N, chain(N, 60000, "R", hidden(N, -MAXC, -MAXC + 10), 40000))        # totals down to -6 * 10^13
add(N, grow(N, 55000, hidden(N, -MAXC, MAXC), 45000, 1, 0.02))
add(N, scatter(N, 40000, hidden(N, -10 ** 5, 10 ** 5), 40000))
add(N, scatter(N, 40000, hidden(N, -10 ** 5, 10 ** 5), 40000, 0.1, 0.3))
add(N, scatter(N, 35000, hidden(N, -10 ** 5, 10 ** 5), 35000, 0.3))
add(N, scatter(N, 40000, hidden(N, -10 ** 5, 10 ** 5), 40000, 0.0, 0.0, False, 3))
add(N, scatter(N, 40000, hidden(N, -5 * 10 ** 7, 5 * 10 ** 7), 40000, 0.0, 0.0, True))
add(N, scatter(N, 40000, hidden(N, -2 * 10 ** 8, 2 * 10 ** 8), 40000, 0.1, 0.0, True))
add(N, scatter(N, 45000, hidden(N, -10 ** 8, 10 ** 8), 35000, 0.0, 0.5, True))
add(N, points(N, 20000, hidden(N), MAXM, 0.5, 0.1))
add(N, star(N, 40000, hidden(N), 40000))
add(N, blocks(N, 45000, hidden(N, -2 * 10 ** 7, 2 * 10 ** 7), 35000, True, 0.0, 0.7))
# claims [i, i + 9] sliding: ten interleaved chains; questions whose length is a multiple of 10 are known
P = hidden(N, -10 ** 8, 10 ** 8)
cl = [claim(P, i, i + 9) for i in range(1, 50001)]
qs = []
for _ in range(30000):
    l = ri(1, 40000)
    qs.append((2, l, l + 10 * ri(1, 999) - 1) if rand() < 0.8 else (2, l, l + ri(0, 9999)))
add(N, mix(cl, qs, 0.3))
# one long chain of single days claimed in random order, then questions over it
P = hidden(N, -MAXC, MAXC)
add(N, [claim(P, i, i) for i in random.sample(range(1, 50001), 50000)]
    + [(2, ri(1, 25000), ri(25000, 50000)) for _ in range(30000)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
