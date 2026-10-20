# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A test is kept as two lists (prices, ratings) so that the big tests are built quickly.
import os, random

random.seed(740218)
MAXN, MAXV = 150000, 10 ** 9
tests = []
rnd = random.random


def add(h):
    ps, rs = h
    n = len(ps)
    assert 1 <= n <= MAXN and len(rs) == n
    assert 1 <= min(ps) and max(ps) <= MAXV and 1 <= min(rs) and max(rs) <= MAXV
    flat = [0] * (2 * n)
    flat[0::2] = ps
    flat[1::2] = rs
    tests.append(f"{n}\n" + "%d %d\n" * n % tuple(flat))


def pairs(lst):
    return [p for p, r in lst], [r for p, r in lst]


def band(n, width, slope, wp, wr):
    """points along a falling line: x in [0, width), price x + noise, rating (width - x) * slope + noise"""
    xs = [int(rnd() * width) for _ in range(n)]
    ps = [x + 1 + int(rnd() * (wp + 1)) for x in xs]
    rs = [(width - x) * slope + 1 + int(rnd() * (wr + 1)) for x in xs]
    return ps, rs


def layers(n, count, size, step):
    """`count` copies of one random antichain (price and rating both increasing), each copy moved by
    (+step, -step): a hotel of a copy is beaten by the same hotel of the copies before"""
    bp, br, p, r = [], [], 1, 1
    for _ in range(size):
        p += random.randint(0, 3)
        r += random.randint(0, 3)
        bp.append(p)
        br.append(r)
    top = count * step
    ks = [int(rnd() * count) * step for _ in range(n)]
    js = [int(rnd() * size) for _ in range(n)]
    return [bp[j] + k for j, k in zip(js, ks)], [br[j] + top - k for j, k in zip(js, ks)]


def blocks(n, cnt, side, grid):
    """`cnt` squares on a falling diagonal, random points inside each, coordinates divided by `grid`"""
    ks = [int(rnd() * cnt) for _ in range(n)]
    ps = [(k * side + int(rnd() * side)) // grid + 1 for k in ks]
    rs = [((cnt - k) * side + int(rnd() * side)) // grid + 1 for k in ks]
    return ps, rs


def dup(h, share):
    """replace a share of the hotels by copies of other hotels"""
    ps, rs = h[0][:], h[1][:]
    n = len(ps)
    for _ in range(int(n * share)):
        i, j = int(rnd() * n), int(rnd() * n)
        ps[i], rs[i] = ps[j], rs[j]
    return ps, rs


def spread(h):
    """map prices and ratings to random large values in the same order (the rounds do not change)"""
    out = []
    for col in h:
        vals = sorted(set(col))
        m = dict(zip(vals, sorted(random.sample(range(1, MAXV + 1), len(vals)))))
        out.append([m[v] for v in col])
    return tuple(out)


_perm = []


def mixed(h):
    """h in a random order; every big test has MAXN hotels, so one shuffled order is reused (fast)"""
    n = len(h[0])
    if n < MAXN:
        idx = list(range(n))
        random.shuffle(idx)
    else:
        if not _perm:
            _perm.extend(range(MAXN))
            random.shuffle(_perm)
        idx = _perm
    return [h[0][i] for i in idx], [h[1][i] for i in idx]


# samples
add(pairs([(300, 4), (200, 5), (300, 4), (100, 3), (200, 2), (400, 5), (500, 1)]))
add(pairs([(5, 1), (5, 2), (5, 3), (5, 3)]))
add(pairs([(7, 7)]))
add(pairs([(3, 3), (5, 1), (1, 5), (4, 2), (2, 4)]))
add(pairs([(4, 6), (2, 2), (6, 5), (3, 6), (2, 7), (5, 3), (4, 6), (1, 1)]))
# hidden: small (brute checks these)
add(pairs([(1, 1), (1, 1)]))
add(pairs([(10 ** 9, 1), (1, 10 ** 9), (10 ** 9, 10 ** 9), (1, 1)]))
add(mixed(dup(band(40, 10, 1, 2, 2), 0.2)))
add(mixed(dup(blocks(300, 30, 4, 2), 0.1)))
add(([random.randint(1, 4) for _ in range(500)], [random.randint(1, 4) for _ in range(500)]))
add(mixed(dup(layers(2000, 200, 50, 3), 0.05)))
add(mixed(band(3000, 1500, 2, 3, 3)))
add(mixed(dup(band(8000, 4000, 1, 5, 5), 0.1)))
add(spread(mixed(dup(blocks(10000, 2000, 3, 1), 0.05))))
# hidden: big (N = 150000)
N = MAXN
add(mixed(dup(band(N, 60000, 1, 3, 3), 0.05)))
add(mixed(dup(band(N, 40000, 2, 8, 2), 0.1)))
add(mixed(dup(band(N, 100000, 1, 1, 1), 0.02)))
add(mixed(dup(band(N, 25000, 1, 10, 40), 0.05)))
add(mixed(band(N, 30000, 3, 0, 5)))                         # many equal prices
add(mixed(band(N, 30000, 1, 6, 0)))                         # many equal ratings
add(mixed(dup(layers(N, 60000, 20, 6), 0.03)))
add(mixed(dup(layers(N, 70000, 60, 2), 0.05)))
add(mixed(layers(N, 50000, 40, 8)))
add(mixed(dup(blocks(N, 25000, 6, 2), 0.05)))
add(mixed(dup(blocks(N, 50000, 3, 1), 0.1)))
add(mixed(blocks(N, 40000, 8, 3)))
add(spread(mixed(dup(band(N, 70000, 1, 2, 2), 0.05))))
add(spread(mixed(dup(layers(N, 80000, 10, 2), 0.05))))
x = range(1, N + 1)
add(mixed(([i for i in x], [N + 1 - i for i in x])))                         # one chain: rounds 1..N
add(mixed(([(i + 1) // 2 for i in x], [(N + 2 - i) // 2 for i in x])))      # a chain through equal values
add(mixed(dup(([i // 3 + 1 for i in x], [(N - i) // 3 + 1 for i in x]), 0.3)))
add(([int(rnd() * MAXV) + 1 for _ in x], [int(rnd() * MAXV) + 1 for _ in x]))
add(([5] * N, [5] * N))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
