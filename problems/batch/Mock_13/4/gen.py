# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(100224)
MAXN, MAXC = 200000, 10 ** 9
tests = []
_perm = []


def add(c, k, pos, shuffle=True):
    n = len(pos)
    assert 2 <= c <= MAXC and 1 <= n <= min(c, MAXN) and 1 <= k <= n
    assert len(set(pos)) == n and 0 <= min(pos) and max(pos) < c
    pos = list(pos)
    if shuffle and not isinstance(pos, Shuffled):
        if not _perm:
            _perm.extend(range(MAXN))
            random.shuffle(_perm)
        pos = [pos[i] for i in _perm if i < n]       # one random order of 0..MAXN-1, reused (fast)
    tests.append(f"{c} {n} {k}\n" + " ".join(map(str, pos)) + "\n")


class Shuffled(list):
    """positions already in random order"""


def rnd(c, n):
    return Shuffled(random.sample(range(c), n))


def clusters(c, m, size, width, shift=None):
    """m clusters of up to `size` houses (each cluster inside `width` consecutive points), evenly spread over
    the circle and turned so that one cluster crosses the point 0 (shift: offset of the first cluster)"""
    step = c // m
    assert width < step and size <= width
    if shift is None:
        shift = c - width // 2
    r = random.random
    pos = set()
    for i in range(m):
        base = shift + i * step + (int(r() * (step - width + 1)) if i else 0)
        pos.add(base % c)                                   # every cluster has a house at both ends
        pos.add((base + width - 1) % c)
        for _ in range(size - 2):
            pos.add((base + int(r() * width)) % c)
    return sorted(pos)


def tight(k, d, smax, glo, ghi, big):
    """k clusters, each a run of houses from its first to its last house spanning exactly d, consecutive houses
    inside a cluster at most smax apart (smax < glo); gaps between clusters random in [glo, ghi]; one cluster also
    has an empty stretch of `big` points inside (big > ghi: the largest gap lies inside a cluster);
    the circle is turned so that a cluster crosses 0. Returns (c, k, positions)"""
    assert big + 4 < d and smax < glo <= ghi < big
    r = random.random
    pos, start = [], 0
    odd = int(r() * k)
    hole = 2 + int(r() * (d - big - 3))                 # in cluster `odd`: no house in hole .. hole + big - 1
    for i in range(k):
        p = 0
        while p < d:
            pos.append(start + p)
            p += 1 + int(r() * smax)
            if i == odd and hole <= p < hole + big:
                if pos[-1] != start + hole - 1:
                    pos.append(start + hole - 1)
                p = hole + big
        pos.append(start + d)
        start += d + glo + int(r() * (ghi - glo + 1))
    c = start
    turn = c - d // 3
    return c, k, [(p + turn) % c for p in pos]


def dense_sparse(m, first, gap, extra):
    """m houses on consecutive points from `first` (around the circle), then MAXN - m single houses about
    `gap` apart, each needing its own lamp; K = (number of single houses) + extra. Uses its own random
    stream so the other tests stay as they were. Returns (c, k, positions)"""
    g = random.Random(first + m)
    c = MAXC
    pos = [(first + t) % c for t in range(m)]
    p = first + m - 1
    while len(pos) < MAXN:
        p += gap + g.randint(0, gap // 10)
        pos.append(p % c)
    assert p - first < c - gap
    g.shuffle(pos)
    return c, MAXN - m + extra, Shuffled(pos)


def offset_trap(r, d, sp):
    """d houses on consecutive points, a gap of 10r, then sp (odd) houses 1.2r apart; the circle closes 0.6r after
    the last one. With radius r the dense run needs ceil(d / (2r + 1)) lamps and the sparse houses (sp + 1) / 2,
    but one lamp less works when a lamp holds the last sparse house together with the first d mod (2r + 1) dense
    houses: the only best splits start that far into the dense run, so trying just the first few hundred starts
    (in sorted order) finds a worse split. Returns (c, k, positions)"""
    assert r % 5 == 0 and sp % 2 == 1 and 0 < d % (2 * r + 1) <= 7 * r // 5 + 1
    pos = list(range(d)) + [d - 1 + 10 * r + 6 * r // 5 * t for t in range(sp)]
    return pos[-1] + 3 * r // 5, (sp + 1) // 2 + -(-d // (2 * r + 1)) - 1, pos


def multi_trap(r, m, q, seed, lone=0):
    """m segments around the circle: one house, then 0.6r later a run of q(2r + 1) + L consecutive houses
    (L = 1.4r + 1 or a few less), then a gap of over 3r. A lamp holding a segment's single house and the first L houses
    of its run saves one lamp per segment, so the best splits start only at a single house or exactly L houses into
    a run: trying a few hundred first starts or a few dozen random ones fails. `lone` far-apart single houses after
    the segments (one lamp each) make K large, so a cap like 10^8 / K on the starts tried stays below L. The circle
    is turned so that point 0 is the start of the first run. Returns (c, k, positions)"""
    g = random.Random(seed)
    w = 2 * r + 1
    pos, k, cur = [], 0, 0
    for _ in range(m):
        single = cur
        d = q * w + 7 * r // 5 + 1 - g.randint(0, 3)
        first = single + 3 * r // 5
        pos.append(single)
        pos += range(first, first + d)
        k += -(-d // w)
        cur = first + d - 1 + 3 * r + g.randint(1, r)
    for _ in range(lone):
        pos.append(cur)
        k += 1
        cur += 2 * r + 1 + g.randint(0, r)
    c = cur + r
    shift = 3 * r // 5                                     # point 0 = first house of the first run
    return c, k, Shuffled(g.sample([(x - shift) % c for x in pos], len(pos)))


# samples
add(20, 2, [1, 3, 8, 12, 17, 19], shuffle=False)
add(10, 1, [0, 5], shuffle=False)
add(1000, 4, [999, 0, 500, 7], shuffle=False)
add(100, 1, [10, 30, 45, 60, 95], shuffle=False)
add(50, 3, [2, 9, 14, 21, 25, 33, 38, 41, 47, 49], shuffle=False)
# hidden: small (brute checks these)
add(2, 2, [0, 1])
add(2, 1, [1, 0])
add(7, 1, [3])
add(100, 3, rnd(100, 30))
add(10 ** 9, 5, rnd(10 ** 9, 40))
add(60, 7, clusters(60, 7, 4, 5))
add(10 ** 9, 17, clusters(10 ** 9, 17, 3, 10 ** 7, shift=10 ** 9 - 3))
add(*tight(5, 21, 2, 3, 6, 8))
add(*tight(8, 16, 3, 4, 6, 7))
add(*tight(12, 41, 5, 10, 20, 25))
# hidden: big
N = MAXN
add(MAXC, 1, rnd(MAXC, N))
add(*offset_trap(500, 99800, 100199))
add(*offset_trap(2000, 150000, 49999))
add(*offset_trap(5000, 97000, 102999))
add(*dense_sparse(100000, MAXC - 40000, 5000, 50))   # a dense run of houses crosses point 0
add(N, 66667, list(range(N)))                       # every point holds a house
add(MAXC, 50000, clusters(MAXC, 50000, 4, 2001))
add(MAXC, 2000, clusters(MAXC, 2000, 100, 10 ** 5))
add(*tight(20000, 12, 2, 3, 5, 7))
add(*tight(20000, 19, 4, 5, 9, 12))
add(*tight(8000, 30001, 3000, 3001, 10000, 15000))
add(*tight(2, 300000001, 6000, 10 ** 6, 10 ** 8, 15 * 10 ** 7))
add(*tight(100, 2000001, 2200, 10 ** 5, 10 ** 6, 12 * 10 ** 5))
add(*multi_trap(800, 60, 1, 4, lone=9000))
add(*multi_trap(2000, 18, 2, 1, lone=4000))
add(*multi_trap(3000, 14, 1, 5, lone=3000))
add(*multi_trap(5000, 11, 1, 2, lone=2500))
add(*tight(4000, 401, 20, 25, 100, 200))
add(*dense_sparse(50000, 0, 3000, 25))
add(*multi_trap(1500, 36, 1, 3, lone=5000))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
