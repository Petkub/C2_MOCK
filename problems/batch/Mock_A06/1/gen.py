# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer is the sum of max(a_(i+1), ..., a_N) over i = 1..N-1 (or -1 when some a_i > D), so the big tests
# vary the shape of the suffix maxima: random, long non-increasing runs (many suffix-maximum records), increasing,
# mountains, valleys, plateaus, a_i = D everywhere, and the -1 cases (only a_1 too large, one cell just too large).
import os, random

random.seed(2025102)
rnd = random.random
MAXN, MAXD, MAXA = 200000, 10 ** 9, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(d, a):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= d <= MAXD
    assert all(0 <= x <= MAXA for x in a)
    tests.append(f"{n} {d}\n" + " ".join(map(str, a)) + "\n")


def band(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def falling(n, hi, lo):
    """non-increasing from about hi to about lo, random steps (some equal neighbours)"""
    out = sorted(band(n, lo, hi), reverse=True)
    return out


def stairs(n, hi, blocks, noise):
    """blocks of random values, every block a little lower than the one before"""
    out, step = [], hi // (blocks + 1)
    for b in range(blocks):
        top = hi - b * step
        out += band(n // blocks, max(0, top - noise), top)
    out += band(n - len(out), 0, max(0, hi - blocks * step))
    return out


# samples
add(4, [2, 3, 1, 4, 0])
add(3, [1, 2, 5, 0])
add(10, [7, 2, 6, 3, 3, 1])
add(6, [1, 4, 2, 6, 3, 5, 2, 2])
add(7, [3, 0, 5, 1, 7, 2, 0, 4, 1, 0])
# hidden: tiny (brute searches every placement of the robots)
add(1, [0])
add(3, [5])                                                         # N = 1, impossible
add(2, [3, 1, 1])                                                   # only a_1 is too large
add(4, [4, 4, 4, 4, 4])                                             # a_i = D everywhere
add(5, [0, 0, 0, 0, 0, 0])
add(5, [5, 1, 4, 2, 3, 1])
add(3, [0, 1, 3, 0, 2, 1])
add(6, [2, 6, 0, 0, 0, 0])
# hidden: medium
add(MAXD, band(2000, 0, MAXA))
add(10 ** 6, [x + ri(0, 50) for x in falling(25000, 10 ** 6 - 50, 0)])   # mostly falling, small dips
a = band(3000, 0, 10 ** 8)
a[0] = 10 ** 8 + 1
add(10 ** 8, a)                                                     # only a_1 is too large
# hidden: big (N = 200000)
add(MAXD, band(N, 0, MAXA))                                          # random
add(MAXD, falling(N, MAXA, 1))                                       # non-increasing
add(MAXD, [MAXA - 5000 * (i // 1000) for i in range(N)])             # long plateaus, falling
add(MAXD, sorted(band(N, 0, MAXA)))                                  # non-decreasing
add(MAXD, stairs(N, MAXA, 20000, 4 * 10 ** 4))                       # falling blocks with noise
add(MAXD, [MAXA] * N)                                                # all equal to D
a = band(N, 0, 10 ** 7)
a[0] = 10 ** 7 + 1
add(10 ** 7, a)                                                     # only a_1 is too large, -1
a = band(N, 0, 10 ** 9 - 1)
a[ri(N // 3, N - 1)] = MAXA
add(MAXA - 1, a)                                                    # one cell needs D + 1, -1
add(1000, band(N, 0, 1000))                                          # small values
m = ri(N // 3, 2 * N // 3)
add(MAXD, sorted(band(m, 0, MAXA)) + falling(N - m, MAXA, 0))        # mountain
add(MAXD, falling(m, MAXA - 10 ** 8, 0) + sorted(band(N - m, 0, MAXA)))  # valley, highest near the end
a = [0] * N
for _ in range(3000):
    a[ri(0, N // 2)] = ri(1, 10 ** 6)
add(10 ** 6, a)                                                      # sparse, zeros at the end
add(MAXD, falling(N // 2, MAXA, 5 * 10 ** 8) + band(N - N // 2, 0, 10 ** 6))
a = [MAXA - 7000 - 4000 * i + ri(0, 7000) for i in range(N)]
add(max(a), a)                                  # zigzag falling, D = max a_i
f = falling(N, 10 ** 7, 0)
add(10 ** 7, f)                                                      # non-increasing, D = a_1
add(MAXD, band(N, 5 * 10 ** 8, MAXA))
a = []
for b in range(400):
    top = MAXA - b * 2000000
    a += [ri(0, top // 2) for _ in range(N // 400 - 1)] + [top]
add(MAXD, a)                                                         # saw teeth, falling peaks
a = [0] * N
a[0] = MAXD
add(MAXD - 1, a)                                                     # only a_1 is too large, all else 0
add(1, band(N, 0, 1))                                                # D = 1

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
