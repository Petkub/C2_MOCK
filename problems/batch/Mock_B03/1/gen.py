# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer depends only on the order of the codes, so a test = an order of ranks 0..n-1 + a pool of codes.
import os, random
from itertools import accumulate

random.seed(1005207)
rnd = random.random
MAXN, MAXV = 300000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(p):
    n = len(p)
    assert 1 <= n <= MAXN
    assert 1 <= min(p) and max(p) <= MAXV
    assert len(set(p)) == n
    tests.append(f"{n}\n" + " ".join(map(str, p)) + "\n")


# ---- pools: n distinct codes in increasing order ----
def pool_curve(n, e):
    """codes r + 1 + floor(K (r / n)^e): small codes first, the largest close to 10^9"""
    k = MAXV - n - ri(0, 1000)
    return [r + 1 + int(k * (r / n) ** e) for r in range(n)]


def pool_dense(n, big):
    """codes from a random subset of 1..3n, then the top `big` codes moved up to 10^8 .. 10^9"""
    out = list(accumulate(1 + int(rnd() * 3) for _ in range(n)))
    hi = sorted(ri(10 ** 8, MAXV) for _ in range(big))
    for j in range(big):
        out[n - big + j] = max(hi[j], out[n - big + j - 1] + 1)
    return out


def pool_uniform(n):
    """n distinct codes uniform in 1 .. 10^9"""
    s = set()
    while len(s) < n:
        s.add(ri(1, MAXV))
    return sorted(s)


def pool_spread(n):
    """n codes spread over 1 .. 10^9 (random gaps)"""
    g = 2 * (MAXV // n) - 100
    out = list(accumulate(1 + int(rnd() * g) for _ in range(n)))
    assert out[-1] <= MAXV
    return out


def pool_perm(n):
    return list(range(1, n + 1))


# ---- orders of ranks ----
def shuffled(a):
    a = list(a)
    key = [rnd() for _ in a]
    return [a[i] for i in sorted(range(len(a)), key=key.__getitem__)]


def swaps(a, k):
    a = list(a)
    n = len(a)
    for _ in range(k):
        i, j = int(rnd() * n), int(rnd() * n)
        a[i], a[j] = a[j], a[i]
    return a


def blocks(n, b):
    """b blocks of consecutive ranks in random block order, each block increasing or decreasing"""
    cuts = sorted(set([0, n] + [ri(1, n - 1) for _ in range(b - 1)]))
    parts = [list(range(cuts[i], cuts[i + 1])) for i in range(len(cuts) - 1)]
    out = []
    for part in shuffled(parts):
        out += part if rnd() < 0.5 else part[::-1]
    return out


def zigzag(n):
    out, lo, hi = [], 0, n - 1
    while lo <= hi:
        out.append(lo); lo += 1
        if lo <= hi:
            out.append(hi); hi -= 1
    return out


def lead(n, k):
    """rank k first, then the others increasing"""
    return [k] + [r for r in range(n) if r != k]


def make(order, pool):
    return list(map(pool.__getitem__, order))


# samples
add([310, 7, 25])
add([8, 3, 20, 15])
add([42])
add([44, 9, 61, 2, 37, 50])
add([70, 12, 95, 33, 8, 81, 46, 59, 21, 64, 17, 88, 5])
# hidden: small and medium (brute checks these)
add([4, 999999999])
add([600000000, 3])
add(make(shuffled(range(8)), pool_uniform(8)))
add(make(list(range(7))[::-1], pool_curve(7, 3)))
add(make(shuffled(range(20)), pool_uniform(20)))
add(make(swaps(range(1000), 30), pool_curve(1000, 4)))
add(make(shuffled(range(25000)), pool_uniform(25000)))
add(make(list(range(25000))[::-1], pool_dense(25000, 500)))
add(make(blocks(30000, 40), pool_perm(30000)))
# hidden: big (n = 300000)
N = MAXN
add(make(shuffled(range(N)), pool_spread(N)))
add(make(shuffled(range(N)), pool_spread(N)))
add(make(shuffled(range(N)), pool_spread(N)))
add(make(shuffled(range(N)), pool_perm(N)))
add(make(list(range(N)), pool_curve(N, 10)))                       # the first arrangement
add(make(list(range(N))[::-1], pool_dense(N, 100)))                # the last arrangement
add(make(lead(N, ri(N // 3, 2 * N // 3)), pool_curve(N, 9)))
add(make(lead(N, N - 1), pool_dense(N, 1)))
add(make(swaps(range(N), 40), pool_curve(N, 11)))
add(make(swaps(list(range(N))[::-1], 40), pool_dense(N, 20000)))
add(make(blocks(N, 300), pool_spread(N)))
add(make(blocks(N, 8), pool_dense(N, 50000)))
add(make(zigzag(N), pool_spread(N)))
o = list(range(N // 2)) + shuffled(range(N // 2, N))
add(make(o, pool_dense(N, 10)))                                    # increasing prefix, random suffix
o = shuffled(range(N // 2, N)) + list(range(N // 2))
add(make(o, pool_curve(N, 10)))                                    # the larger half first, in random order
o = [N - 1] + shuffled(range(N - 1))
add(make(o, pool_perm(N - 1) + [MAXV]))                            # codes <= n except the largest
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
