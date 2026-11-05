# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1504)
MAXN, MAXL = 100000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(L, sts):
    n = len(sts)
    assert 1 <= n <= MAXN and 2 <= L <= MAXL
    for p, c in sts:
        assert 0 <= p <= L - 1 and 1 <= c <= n
    tests.append(f"{n} {L}\n" + " ".join(str(p) for p, _ in sts) + "\n" + " ".join(str(c) for _, c in sts) + "\n")


def shuffled(sts):
    sts = list(sts)
    random.shuffle(sts)
    return sts


def runs(L, n, k, rmin, rmax, shift=None, pos=None, giant=0):
    """n stations at random (or given) positions; going clockwise, the companies come in runs of
    rmin..rmax stations, neighbouring runs of different companies (k >= 2 companies); the runs are
    rotated by `shift` so that one run crosses point 0; giant > 0 adds one run of `giant` stations"""
    ps = sorted(pos if pos is not None else [ri(0, L - 1) for _ in range(n)])
    cs, cur = [], ri(1, k)
    while len(cs) < n:
        cs += [cur] * ri(rmin, rmax)
        nxt = ri(1, k - 1)
        cur = nxt if nxt < cur else nxt + 1
    cs = cs[:n - giant]
    if giant:                       # make one run longer by `giant` stations
        j = ri(0, len(cs) - 1)
        cs = cs[:j] + [cs[j]] * giant + cs[j:]
    if shift is None:
        shift = ri(0, n - 1)
    cs = cs[shift:] + cs[:shift]
    return shuffled(zip(ps, cs))


# samples
add(20, [(1, 1), (3, 1), (6, 2), (10, 3), (12, 3), (15, 1), (18, 2)])
add(12, [(0, 1), (6, 2), (0, 1), (9, 2)])
add(10, [(2, 3), (7, 3), (9, 3)])
add(30, [(4, 2), (25, 1), (11, 3), (17, 2), (29, 2), (8, 1), (20, 3), (14, 1)])
add(100, [(37, 4), (90, 1), (5, 1), (62, 4), (71, 2), (13, 1), (44, 1), (98, 4), (25, 2), (56, 2)])

# hidden: small and medium (brute checks these)
add(7, [(3, 1)])
add(5, [(4, 1), (4, 2)])
add(MAXL, [(0, 1), (MAXL - 1, 2), (MAXL // 2, 1)])
for n, L, k, rmax in [(8, 9, 2, 3), (12, 30, 3, 4), (60, 50, 2, 10), (300, 1000, 4, 30), (2000, MAXL, 3, 300)]:
    add(L, runs(L, n, k, 1, rmax))
add(MAXL, [(ri(0, 10 ** 6), 1) for _ in range(1999)] + [(MAXL // 2, 2)])

# hidden: big (each with its own seed)
N = MAXN
H = MAXL // 2


def star():
    """one station of company 2, the rest of company 1 spread round the ring"""
    return shuffled([(ri(0, MAXL - 1), 1) for _ in range(N - 1)] + [(ri(0, MAXL - 1), 2)])


def halves():
    """company 1 on one half of the ring, company 2 on the other half, the halves cut at random points"""
    a = ri(0, MAXL - 1)
    return shuffled([((a + ri(0, H - 1)) % MAXL, 1) for _ in range(N // 2)] +
                    [((a + H + ri(0, H - 1)) % MAXL, 2) for _ in range(N - N // 2)])


def around_zero(k, rmin, rmax, giant):
    """all stations within 10^6 of point 0 on both sides, so going across point 0 is short"""
    pos = [ri(0, 10 ** 6) if rnd() < 0.5 else MAXL - 1 - ri(0, 10 ** 6) for _ in range(N)]
    return runs(MAXL, N, k, rmin, rmax, pos=pos, giant=giant)


def three_far():
    """company 1 near point 0 (both sides), one station of company 2 and one of company 3 far away"""
    sts = [((MAXL - ri(1, 5 * 10 ** 6)) % MAXL if rnd() < 0.5 else ri(0, 5 * 10 ** 6), 1) for _ in range(N - 2)]
    return shuffled(sts + [(H + ri(-1000, 1000), 2), (H // 2 + ri(-1000, 1000), 3)])


def clusters(m, k):
    """m clusters round the ring, all stations of a cluster of one company"""
    centres = sorted(ri(0, MAXL - 1) for _ in range(m))
    comp = [ri(1, k) for _ in range(m)]
    comp[-1] = comp[0] % k + 1 if comp[-1] == comp[0] and k > 1 else comp[-1]
    out = []
    for _ in range(N):
        j = ri(0, m - 1)
        out.append(((centres[j] + ri(-3000, 3000)) % MAXL, comp[j]))
    return shuffled(out)


BIG = [
    (150401, lambda: (MAXL, [(ri(0, MAXL - 1), ri(1, N)) for _ in range(N)])),
    (150402, lambda: (MAXL, [(ri(0, MAXL - 1), ri(1, 2)) for _ in range(N)])),
    (150403, lambda: (MAXL, star())),
    (150404, lambda: (MAXL, halves())),
    (150405, lambda: (MAXL, runs(MAXL, N, 3, 1, 3000, giant=N // 3))),
    (150406, lambda: (MAXL, runs(MAXL, N, 2, 2000, 20000))),
    (150407, lambda: (MAXL, runs(MAXL, N, 2, 40, 80, giant=N // 2))),
    (150408, lambda: (MAXL, runs(MAXL, N, 5, 1, 200, giant=N // 4))),
    (150409, lambda: (MAXL, around_zero(2, 100, 3000, N // 3))),
    (150410, lambda: (MAXL, around_zero(4, 1, 60, N // 2))),
    (150411, lambda: (MAXL, three_far())),
    (150412, lambda: (MAXL, clusters(50, 3))),
    (150413, lambda: (MAXL, clusters(500, 2))),
    (150414, lambda: (1000, runs(1000, N, 2, 1, 500, giant=N // 3))),
    (150415, lambda: (2, [(ri(0, 1), ri(1, 3)) for _ in range(N)])),
    (150416, lambda: (MAXL, [(ri(0, MAXL - 1), 7) for _ in range(N)])),
    (150417, lambda: (MAXL, runs(MAXL, N, N, 30, 300, giant=N // 3))),
    (150418, lambda: (MAXL, shuffled([(i * (MAXL // N), 1 + i % 2) for i in range(N)]))),
    (150419, lambda: (MAXL, runs(MAXL, N, 2, N // 3, N // 2, shift=N // 6))),
]
for seed, make in BIG:
    random.seed(seed)
    add(*make())

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
