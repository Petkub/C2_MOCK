# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(74104)
rnd = random.random
MAXN, MAXR, MAXT = 200000, 200000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, k, vis):
    r = len(vis)
    assert 1 <= n <= MAXN and 1 <= r <= MAXR and 1 <= k <= r
    assert all(1 <= p <= n and 1 <= t <= MAXT for p, t in vis)
    tests.append("%d %d %d\n" % (n, r, k) + "".join("%d %d\n" % v for v in vis))


def rand_vis(r, plo, phi, tlo, thi):
    return [(ri(plo, phi), ri(tlo, thi)) for _ in range(r)]


def same_key(r, n, base, spread):
    """start stall p, start minute t = p + base + (a small offset in [0, spread]): many equal t - p"""
    out = []
    for _ in range(r):
        p = ri(1, n)
        out.append((p, p + base + ri(0, spread)))
    return out


# samples
add(5, 1, [(1, 2), (3, 1), (2, 4)])
add(4, 2, [(1, 3), (2, 1), (3, 2)])
add(1, 2, [(1, 1000000000), (1, 7), (1, 7), (1, 999999999)])
add(8, 2, [(1, 5), (4, 3), (6, 4), (2, 9), (3, 8), (7, 12)])
add(6, 3, [(2, 1000000000), (6, 1), (1, 500)])

# hidden: small and medium (brute checks these)
add(1, 1, [(1, 1)])
add(3, 1, [(3, 5)])
add(10, 3, rand_vis(12, 1, 10, 1, 15))
add(12, 4, same_key(15, 12, 0, 1))                       # many arrive together
add(30, 7, rand_vis(40, 1, 30, 1, 40))
add(50, 50, rand_vis(50, 1, 50, 1, MAXT))                 # K = R: nobody misses a sample
add(300, 1, rand_vis(400, 1, 300, 1, 600))
add(2000, 300, same_key(2500, 2000, 10, 3))
add(2000, 900, [(ri(1, 2000), MAXT - ri(0, 3000)) for _ in range(2000)])

# hidden: medium-size K = 1 (one sample per stall)
add(60000, 1, rand_vis(60000, 1, 60000, 1, 120000))
add(60000, 1, same_key(60000, 60000, 0, 0))

# hidden: max size (every stall hands out many samples)
N = R = MAXN
add(N, R // 2, rand_vis(R, 1, 1000, 1, 2000))             # start order and arrival order differ
add(N, R // 2, rand_vis(R, 1, 1, 1, MAXT))               # everyone starts at stall 1
add(N, 100000, same_key(R, N // 2, 7, 0))                # everyone has the same t - p: numbers decide
add(N, 60000, same_key(R, N // 4, 0, 9))
add(N, 150000, [(ri(1, N), ri(1, 10 ** 6)) for _ in range(R)])
add(N, R // 2, [(p, 500000 + p // 2 + ri(0, 3)) for p in (ri(1, N // 2) for _ in range(R))])   # later start, earlier arrival
add(N, 40000, [(p, 300000000 + p // 3) for p in (ri(1, 20000) for _ in range(R))])
add(N, R, rand_vis(R, 1, N, 1, MAXT))                     # K = R
add(N, R - 1, same_key(R, 1000, 5, 2))
add(N, 30000, rand_vis(R, 1, 5000, 1, 10000))
add(N, 120000, same_key(R, 50000, 1000, 50))
add(N, 80000, [(ri(1, 3), ri(1, 4)) for _ in range(R)])   # three start stalls, four start minutes
add(N, 100000, [(p, MAXT - p * 4000 - ri(0, 3)) for p in (ri(1, 2000) for _ in range(R))])
add(N, 50000, [(ri(1, 30000), ri(1, 60000)) for _ in range(R)])
add(N, 90000, same_key(R, 100, 123456, 1))
add(N, 70000, [(p, p + (j % 5)) for j, p in enumerate(ri(1, 8000) for _ in range(R))])
add(N, 100000, [(1 + j % 1000, 1000000 - j // 1000) for j in range(R)])   # by number: later start minute earlier

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
