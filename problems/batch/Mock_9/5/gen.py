# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(5101)
MAXN = 200000
MAXV = 10 ** 9
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def add(m, k, a):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= m and 1 <= k and m * k <= n
    assert all(1 <= x <= MAXV for x in a)
    tests.append(f"{n} {m} {k}\n" + " ".join(map(str, a)) + "\n")


def planted(n, k, extra, x, order, hi_top=MAXV, lo_bot=1, rp=0.0):
    """boxes of odd length between k and k + extra while they fit in n fruits; returns (number of boxes, row).
    In a box of length L exactly (L + 1) / 2 fruits are >= x (about half of them equal to x), the others < x.
    rp > 0: the first rp share of the boxes get one more fruit >= x and the last rp share one fewer
    (the total stays the same, but the surplus is far from where it is needed).
    order: 'front' = big fruits first, 'back' = last, 'mix' = shuffled, 'wave' = alternate boxes front/back"""
    lens = []
    used = 0
    while True:
        L = k + ri(0, extra)
        if L % 2 == 0:
            L += 1
        if used + L > n:
            break
        lens.append(L)
        used += L
    nb = len(lens)
    R = int(nb * rp)
    a = []
    for b, L in enumerate(lens):
        h = (L + 1) // 2
        if b < R and h < L:
            h += 1
        elif b >= nb - R:
            h -= 1
        hi = [x if random.random() < 0.5 else ri(x + 1, hi_top) for _ in range(h)]
        lo = [ri(lo_bot, x - 1) for _ in range(L - h)]
        o = order if order != "wave" else ("front" if b % 2 == 0 else "back")
        if o == "front":
            part = hi + lo
        elif o == "back":
            part = lo + hi
        else:
            part = hi + lo
            random.shuffle(part)
        a += part
    return nb, a


def clustered(n, lo_len, hi_len, p_hi, mix):
    """runs of random length: a run is 'high' with probability p_hi; a value in a high run is >= 600 000 000
    with probability mix (in a low run with probability 1 - mix): the big values come in clumps"""
    a = []
    while len(a) < n:
        high = random.random() < p_hi
        for _ in range(ri(lo_len, hi_len)):
            big = (random.random() < mix) == high
            a.append(ri(600000000, MAXV) if big else ri(1, 599999999))
    return a[:n]


def addp(res, k, slack=0):
    add(res[0] - slack, k, res[1])


def rnd(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


# samples
add(3, 2, [7, 8, 5, 2, 8, 7, 8, 3, 7])
add(2, 2, [1, 10, 10, 2, 10, 3])
add(1, 3, [4, 9, 2, 6])
add(3, 2, [5, 1, 4, 4, 2, 8])
add(2, 1, [10 ** 9, 1, 10 ** 9 - 1, 10 ** 9])
# hidden: small (checked by the direct DP)
add(1, 1, [5])
add(2, 1, [3, 3])
add(4, 1, [2, 9, 1, 7, 7, 3, 8])
add(3, 3, rnd(12, 1, 3))
addp(planted(14, 2, 2, 50, "front", 100), 2)
addp(planted(25, 3, 3, 500, "mix", 1000), 3)
add(7, 1, rnd(40, 1, 6))
addp(planted(60, 4, 6, 10 ** 8, "wave"), 4)
addp(planted(140, 5, 4, 7, "front", 9), 5)
add(30, 2, rnd(150, 1, 1000))
# hidden: special shapes (medium size)
add(100, 10, [123456789] * 1000)                                 # all equal
add(1000, 2, [MAXV - (i % 3 == 0) for i in range(3000)])         # two values, period 3
# hidden: large (planted rows defeat a greedy cut; moving the surplus to the front and clumping the big values
# defeat "enough fruits >= x in total")
N = MAXN
add(1, 1, rnd(N, 1, MAXV))                                       # one box: the median of everything
add(N, 1, rnd(N, 1, MAXV))                                       # every fruit alone: the smallest value
add(N // 50, 50, rnd(N, 1, 3))                                   # every box exactly 50 fruits
addp(planted(N, 3, 4, 500000000, "front", rp=0.1), 3)
addp(planted(N, 4, 6, 400000000, "mix", rp=0.05), 4)
addp(planted(N, 30, 40, 700000000, "front", rp=0.2), 30)
addp(planted(N, 8, 15, 600000000, "wave", rp=0.1), 8)
addp(planted(N, 6, 8, 2, "front", 3, 1), 6)                      # values 1..3 only
add(700, 200, clustered(N, 300, 900, 0.5, 1.0))                  # long clumps of big and small values
addp(planted(N, 2, 10, 5, "front", 9, 1, rp=0.1), 2)            # values 1..9 only
add(20000, 7, rnd(N, 1, 10))
add(3000, 60, sorted(rnd(N, 1, MAXV)))                           # increasing row
add(3000, 60, sorted(rnd(N, 1, MAXV), reverse=True))             # decreasing row
addp(planted(N, 50, 20, 900000000, "front", rp=0.3), 50)
addp(planted(N, 10, 10, 250000000, "mix", rp=0.05), 10)
addp(planted(N, 5, 6, 800000000, "front", rp=0.1), 5, 3)        # three boxes of slack
add(900, 120, clustered(N, 50, 400, 0.45, 0.8))                  # shorter, noisy clumps
add(500, 300, [ri(500000000, MAXV) for _ in range(N // 4)] + [ri(1, 500000000) for _ in range(N // 2)]
    + [ri(500000000, MAXV) for _ in range(N // 4)])               # big values at both ends only

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
