# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Input: K, then the fees F_1 F_2 F_3, then one line per shop: n_j followed by its n_j prices.
# Big tests use 300 000 seedlings. Most of them have about 100 000 seedlings in every shop and K between
# 120 000 and 180 000 (trying every pair of counts (x, y) is then billions of steps), with fees and prices
# chosen so that the best purchase uses one shop, two shops or all three, and so that each wrong shortcut
# (K cheapest overall, adding or dropping shops greedily, cheapest next seedling, single shop or all three,
# int totals)
# fails several tests.
import os, random

random.seed(110126)
rnd = random.random
MAXK, MAXN, MAXF, MAXP = 300000, 300000, 10 ** 9, 10 ** 6
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(k, fees, shops):
    n = sum(len(s) for s in shops)
    assert 1 <= k <= MAXK and 1 <= n <= MAXN and len(fees) == 3 and len(shops) == 3
    assert all(0 <= f <= MAXF for f in fees)
    assert all(1 <= p <= MAXP for s in shops for p in s)
    lines = [str(k), " ".join(map(str, fees))]
    for s in shops:
        lines.append(" ".join(map(str, [len(s)] + s)))
    tests.append("\n".join(lines) + "\n")


def prices(n, lo, hi):
    w = hi - lo + 1
    return [lo + int(rnd() * w) for _ in range(n)]


def mixed(n, parts):
    """n prices; parts = [(weight, lo, hi), ...]: one random number picks the range and the price in it"""
    tot = float(sum(w for w, _, _ in parts))
    if len(parts) == 1:
        return prices(n, parts[0][1], parts[0][2])
    (w1, lo1, hi1), (w2, lo2, hi2) = parts
    p = w1 / tot
    s1, s2 = (hi1 - lo1 + 1) / p, (hi2 - lo2 + 1) / (1 - p)
    out = []
    for _ in range(n):
        u = rnd()
        if u < p:
            out.append(lo1 + int(u * s1))
        else:
            out.append(lo2 + int((u - p) * s2))
    return out


# samples
add(3, [5, 2, 4], [[4, 1, 6], [3, 8], [2, 7]])
add(2, [100, 1, 50], [[1, 2, 3], [60, 70], [30]])
add(5, [7, 6, 9], [[10, 3, 12, 5], [4, 8, 6, 2], []])
add(6, [3, 4, 2], [[5, 9, 4], [7, 6, 8, 3], [2, 10]])
add(7, [30, 25, 40], [[2, 6, 3], [5, 1], [8]])

# hidden: small (brute tries every set of seedlings)
add(1, [0, 7, 3], [[], [5], []])
add(9, [10, 20, 30], [[4, 4, 9], [1, 2, 8, 3], [6, 5]])                     # K = N: buy everything
add(10, [1, 1, 1], [[2, 3], [4, 5, 6], [7, 8, 9, 1]])                        # K = N + 1: -1
add(7, [9, 4, 6], [[5] * 6, [5] * 5, [5] * 7])                              # equal prices
add(6, [50, 3, 3], [[10] * 6, [1, 1, 1, 40, 40, 40], [1, 1, 1, 40, 40]])   # best single shop is not in the best pair
add(11, [10 ** 9, 10 ** 9 - 1, 10 ** 9], [prices(7, 1, MAXP), prices(6, 1, MAXP), prices(7, 1, MAXP)])

# hidden: medium (brute tries every pair of counts)
add(2500, [3000, 5000, 4000], [prices(1500, 1, 1000), prices(1200, 1, 1000), prices(1300, 1, 1000)])
add(16000, [10 ** 8, 10 ** 8, 10 ** 8], [mixed(11000, [(97, 1, MAXP), (3, 1, 50)]),
                                          mixed(10000, [(97, 1, MAXP), (3, 1, 50)]),
                                          mixed(9000, [(50, 1, 300000), (50, 1, MAXP)])])

# hidden: big. Three shops of 100 000 seedlings each unless stated, K from 100 000 to 180 000.
B = 100000
U = [(1, 1, MAXP)]                       # uniform over the whole range


def three(parts_a, parts_b, parts_c, na=B, nb=B, nc=B):
    return [mixed(na, parts_a), mixed(nb, parts_b), mixed(nc, parts_c)]


def decoy(cheap, lo, cheap_hi=1000):
    """mostly expensive (lo .. MAXP) with a small share of very cheap seedlings"""
    return [(100 - cheap, lo, MAXP), (cheap, 1, cheap_hi)]


# all three shops are worth it (moderate fees)
add(150000, [ri(10 ** 6, 10 ** 7), ri(10 ** 6, 10 ** 7), ri(10 ** 6, 10 ** 7)], three(U, U, U))
# one shop is mostly expensive with a few very cheap seedlings: its fee is larger than what they save
add(150000, [ri(0, 1000), ri(0, 1000), MAXF], three(U, U, decoy(1, 900000)))
add(130000, [MAXF, 5 * 10 ** 8, 2 * 10 ** 8], three(decoy(0.5, 800000, 100), U, [(1, 1, 700000)]))
add(170000, [7 * 10 ** 8, MAXF, 0], three([(1, 1, 600000)], decoy(1, 950000, 10), [(1, 1, 750000)]))
add(160000, [123456789, 234567890, 999999999], three(U, [(1, 1, 900000)], decoy(0.6, 850000, 100)))
# the same shape, but the cheap seedlings are worth the fee
add(150000, [ri(0, 1000), ri(0, 1000), 10 ** 8], three(U, U, decoy(10, 900000)))
# one shop alone is best; the others are expensive apart from a few very cheap seedlings
add(120000, [MAXF, 9 * 10 ** 8, MAXF], three(decoy(0.4, 700000, 5), U, decoy(0.4, 700000, 5),
                                              na=50000, nb=200000, nc=50000))
add(100000, [8 * 10 ** 8, 9 * 10 ** 8, 10 ** 9],
    three([(1, 1, 300000)], decoy(0.5, 300000, 20), decoy(0.5, 300000, 20), na=120000, nb=90000, nc=90000))
# the best single shop is not part of the best pair: shop 1 is uniformly mid-priced, shops 2 and 3 have
# half very cheap and half very expensive seedlings
add(100000, [MAXF, ri(0, 10 ** 6), ri(0, 10 ** 6)],
    three([(1, 400000, 500000)], [(1, 1, 20), (1, 990000, MAXP)], [(1, 1, 20), (1, 990000, MAXP)]))
add(140000, [9 * 10 ** 8, 10 ** 7, 2 * 10 ** 7],
    three([(1, 300000, 400000)], [(7, 1, 1000), (3, 900000, MAXP)], [(7, 1, 1000), (3, 900000, MAXP)]))
# no single shop is enough; the largest shop is not part of the best pair
add(150000, [MAXF, 10 ** 6, 2 * 10 ** 6], three([(1, 200000, 400000)], [(1, 1, 300000)], [(1, 1, 300000)],
                                              na=110000, nb=95000, nc=95000))
# a shop with a big fee and many cheap seedlings is worth it, but not for the first seedling
add(180000, [5 * 10 ** 8, 0, 0], three([(1, 1, 1000)], [(1, 1, 900000)], [(1, 100000, MAXP)]))
# two small shops of cheap seedlings with big fees together are better than any other pair or all three,
# but one large shop alone is better still
add(150000, [MAXF, 9 * 10 ** 8, MAXF], three([(1, 1, 1000)], [(1, 1500, 2500), (1, 10000, 12666)], [(1, 1, 1000)],
                                              na=75000, nb=150000, nc=75000))
# one shop is empty
add(100000, [7 * 10 ** 8, 0, 6 * 10 ** 8], [mixed(150000, decoy(0.5, 700000)), mixed(150000, U), []])
# every price at the maximum (largest answer)
add(180000, [MAXF, MAXF, MAXF], [[MAXP] * B, [MAXP] * B, [MAXP] * B])
# K = N: everything is bought
add(MAXN, [MAXF, MAXF, MAXF], three(U, U, U))
# no fees: the K cheapest overall
add(155000, [0, 0, 0], three([(1, 1, 500000)], U, [(1, 400000, MAXP)]))
# small K with many seedlings
add(25, [500, 20, 0], three([(1, 1, 50)], [(1, 1, 200)], [(1, 100, MAXP)]))
# K larger than all seedlings: -1
add(MAXK, [1, 2, 3], three(U, U, U, na=B, nb=B, nc=B - 1))
# equal prices everywhere: only fees decide
add(160000, [10 ** 9, 999999999, 999999998], [[777777] * B, [777777] * B, [777777] * B])
# one shop alone is best; the other two shops together beat every other pair and all three, but neither of them
# alone is any good (very cheap seedlings in one half, very expensive ones in the other)
add(20000, [5500000, 6000000, 5000000], [mixed(25000, [(45, 1, 5), (55, 900000, MAXP)]),
                                         mixed(25000, [(45, 1, 5), (55, 900000, MAXP)]), prices(25000, 150, 250)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for f in os.listdir("tests"):
    if f.endswith(".in") or f.endswith(".out"):
        os.remove(os.path.join("tests", f))
for i, t in enumerate(tests, 1):
    with open("tests/{:02d}.in".format(i), "w") as f:
        f.write(t)
