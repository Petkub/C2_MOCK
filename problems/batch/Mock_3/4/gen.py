# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer depends only on the order of the readings (with ties), so a test = a sequence of ranks 0..K-1
# + a pool of K distinct readings in increasing order.
import os, random

random.seed(304113)
rnd = random.random
MAXN, MAXV = 200000, 10 ** 18
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def big(a, b):
    """uniform-ish integer in a..b with full precision (two random() calls)"""
    span = b - a + 1
    if span < 2 ** 50:
        return a + int(rnd() * span)
    return a + (int(rnd() * 10 ** 9) * 10 ** 9 + int(rnd() * 10 ** 9)) % span


def add(b):
    n = len(b)
    assert 3 <= n <= MAXN
    assert 0 <= min(b) and max(b) <= MAXV
    tests.append(f"{n}\n" + " ".join(map(str, b)) + "\n")


# ---- pools: k distinct readings in increasing order ----
def pool_range(k, lo, hi):
    """k distinct readings in lo..hi; the largest is hi"""
    if k > 5000:                                     # random gaps, about 98% of the range
        g = (hi - lo) * 196 // (100 * k)
        out, v = [], lo + ri(0, 9)
        for _ in range(k - 1):
            out.append(v)
            v += 1 + int(rnd() * g)
        assert v < hi
        return out + [hi]
    s = {hi}
    while len(s) < k:
        s.add(big(lo, hi))
    return sorted(s)


def pool_mixed(k, lo, hi, top):
    """k - top distinct readings in lo..hi and `top` more in 10^17 .. 10^18 (the largest is 10^18)"""
    return pool_range(k - top, lo, hi) + pool_range(top, 10 ** 17, MAXV)


def pool_top(k):
    """k distinct readings close to 10^18 (the top one is 10^18)"""
    return [MAXV - (k - 1 - r) * ri(1, 7) - (k - 1 - r) ** 2 for r in range(k)]


def pool_dense(k):
    """k distinct small readings (a random subset of 0..3k)"""
    out, v = [], ri(0, 2)
    for _ in range(k):
        out.append(v)
        v += 1 + int(rnd() * 3)
    return out


# ---- sequences of ranks ----
def rand_ranks(n, k):
    return [int(rnd() * k) for _ in range(n)]


def perm(n):
    a = list(range(n))
    key = [rnd() for _ in a]
    return [a[i] for i in sorted(range(n), key=key.__getitem__)]


def noise(a, k):
    """k random swaps"""
    a = list(a)
    n = len(a)
    for _ in range(k):
        i, j = int(rnd() * n), int(rnd() * n)
        a[i], a[j] = a[j], a[i]
    return a


def mountain(n):
    """ranks rising to the peak and falling again (both sides interleave the ranks)"""
    p = perm(n)
    m = ri(n // 3, 2 * n // 3)
    left = sorted(p[:m])
    right = sorted(p[m:], reverse=True)
    return left + right


def valley(n):
    p = perm(n)
    m = ri(n // 3, 2 * n // 3)
    return sorted(p[:m], reverse=True) + sorted(p[m:])


def plateaus(n, peaks, levels):
    """`peaks` hills made of runs of equal ranks"""
    out = []
    cuts = sorted(ri(1, n - 1) for _ in range(peaks - 1))
    lens = [b - a for a, b in zip([0] + cuts, cuts + [n])]
    for ln in lens:
        top = ri(levels // 2, levels - 1)
        up = []
        while len(up) < ln:
            run = ri(1, 60)
            lv = int(rnd() * (top + 1))
            up += [lv] * run
        up = up[:ln]
        half = ri(0, ln)
        out += sorted(up[:half]) + sorted(up[half:], reverse=True)
    return out


def runs(n, k, maxrun):
    out = []
    while len(out) < n:
        out += [int(rnd() * k)] * ri(1, maxrun)
    return out[:n]


def make(ranks, pool):
    assert max(ranks) < len(pool)
    return list(map(pool.__getitem__, ranks))


# samples
add([6, 11, 4, 9, 3])
add([50, 80, 50, 20, 80, 35])
add([10, 4, 10])
add([3000000000, 125, 70000000000, 999999999999, 4000000000, 125, 61, 800000000000])
add([0, 4, 9, 4, 0, 11, 7, 7, 18, 2, 9, 1])
# hidden: small and medium (brute checks these)
add([0, MAXV, 0])
add([MAXV, MAXV, MAXV, 7, MAXV])
add(make(rand_ranks(8, 4), pool_range(4, 0, 30)))
add(make(rand_ranks(300, 20), pool_range(20, 0, MAXV)))
add(make(mountain(400), pool_range(400, 10 ** 17, MAXV)))
add(make(rand_ranks(2000, 2000), pool_range(2000, 0, MAXV)))
add(make(rand_ranks(10000, 30), pool_top(30)))
add(make(plateaus(12000, 3, 200), pool_range(200, 10 ** 12, 10 ** 15)))
add(rand_ranks(15000, 2))
add(make(rand_ranks(50000, 40), pool_top(40)))
# hidden: big (n = 200000; readings mostly below 10^14 to keep each input within ~3 MB)
N = MAXN
G, T, E, W = 10 ** 9, 10 ** 10, 10 ** 12, 5 * 10 ** 13
add(make(perm(N), pool_range(N, 0, W)))                          # all different, random order
add(make(rand_ranks(N, 1000), pool_range(1000, 0, E)))
add(make(rand_ranks(N, 3), pool_range(3, G, T)))                   # three different readings
add(rand_ranks(N, 2))                                               # readings 0 and 1 only
add([7] * N)                                                        # all equal
add(make(noise(mountain(N), 300), pool_range(N, G, W)))
add(make(plateaus(N, 1, 3000), pool_mixed(3000, G, T, 30)))
add(make(noise(valley(N), 20000), pool_range(N, 0, W)))
add(make(noise(list(range(N))[::-1], 2000), pool_mixed(N, G, W, 500)))
add(make(noise(list(range(N)), 2000), pool_range(N, T, W)))
add(make(rand_ranks(N, N // 3), pool_range(N // 3, E, 10 * E)))
r = rand_ranks(N, N - 1)
for i in range(N):
    if rnd() < 0.5:
        r[i] = N - 1                                                # half of the readings are the largest
add(make(r, pool_range(N, G, 10 * E)))
add(make(rand_ranks(N, N), pool_dense(N)))                         # small readings
add(make(runs(N, 5000, 50), pool_range(5000, G, T)))
add(make(plateaus(N, 20, 100000), pool_range(100000, G, E)))
add(make(rand_ranks(N, 2), pool_range(2, G, T)))                   # two different readings
flare = perm(N)                                                    # 97% of the readings are 0
add([0 if rnd() < 0.97 else v for v in make(flare, pool_range(N, 1, W))])
base = ri(1000, 9999)                                              # about 95% equal to one middle reading, in runs
lvl = make(perm(N), pool_range(N, 0, W))
seq, i = [], 0
while len(seq) < N:
    if rnd() < 0.87:
        seq += [base] * ri(1, 60)
    else:
        ln = ri(1, 20)
        seq += lvl[i:i + ln]
        i += ln
add(seq[:N])
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
