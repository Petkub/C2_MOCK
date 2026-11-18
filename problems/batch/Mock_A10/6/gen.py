# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Integer-only randomness (getrandbits), so every machine builds the same files.
import os, random

random.seed(106117)
MAXN, MAXA = 200000, 10 ** 9
tests = []


def ri(a, b):
    """uniform integer in [a, b] from getrandbits only"""
    k = b - a + 1
    bits = k.bit_length()
    while True:
        r = random.getrandbits(bits)
        if r < k:
            return a + r


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = ri(0, i)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def add(a):
    n = len(a)
    assert 1 <= n <= MAXN
    assert all(isinstance(x, int) and -MAXA <= x <= MAXA for x in a)
    tests.append(f"{n}\n" + " ".join(map(str, a)) + "\n")


def rand(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def merge(x, y):
    """random interleaving of x and y (each keeps its order)"""
    out, i, j = [], 0, 0
    while i < len(x) or j < len(y):
        if j == len(y) or (i < len(x) and ri(0, len(x) + len(y) - i - j - 1) < len(x) - i):
            out.append(x[i]); i += 1
        else:
            out.append(y[j]); j += 1
    return out


def trap(D, L, big, noise=0, base=0):
    """a decreasing run of D high numbers, then L-1 low increasing numbers and `big` numbers above
    everything: a longest increasing subsequence ends high, the best walk turns at the last low number"""
    high = [base + 500000 + D - k for k in range(D)]
    low = [base + 1 + k for k in range(L - 1)]
    tops = [base + 900000 + k for k in range(big)]
    a = high + low + tops
    if noise:
        for _ in range(noise):
            p = ri(0, len(a))
            a.insert(p, ri(base - 400000, base + 1000000))
    return a


def interleaved(n, dup=False):
    """low numbers going up and high numbers going down, mixed: every card fits in one walk"""
    k = n // 2
    low = [-MAXA + (i // 2 if dup else i) for i in range(k)]
    high = [MAXA - (i // 2 if dup else i) for i in range(n - k)]
    return merge(low, high)


# samples
add([2, 9, 4, 7, 5, 1])
add([10, 8, 7, 5, 3, -2])
add([5, 1, 6, 2, 7, 3, 8, 4])
add([3, 8, 1, 5, 9, 4, 6])
add([-7])

# hidden: small and medium (brute follows every walk on these)
add([4, 4])
add(rand(10, 1, 3))
add(rand(12, -MAXA, MAXA))
add([5] * 15)
add(trap(6, 5, 2, noise=4))
add(rand(200, 1, 50))
add(interleaved(300, dup=True))
add(rand(2000, -MAXA, MAXA))
add(rand(3000, 1, 100))
add(trap(900, 700, 30, noise=300))

# hidden: big
N = MAXN
add(rand(N, -MAXA, MAXA))                                   # random, all different in practice
add(rand(N, 1, 1000))                                       # many equal numbers
add(rand(N, 1, 10))
add([-MAXA + 3 * i for i in range(N)])                      # increasing: walk right only
add([MAXA - 5 * i for i in range(N)])                       # decreasing: start at the right end, walk back
add([MAXA] * N)                                             # all equal
add([i // 2 for i in range(N)])                            # non-decreasing with pairs of equal numbers
add(interleaved(N))                                         # every card fits
add(interleaved(N, dup=True))                               # equal pairs on both sides
add(trap(100000, 100000, 1))                                # greedy LIS-first loses half
add(trap(80000, 80000, 2000, noise=30000))
add(trap(60000, 120000, 5000, noise=10000, base=-300000))
add([(i % 1000) * 1000 + i // 1000 for i in range(N)])     # many increasing blocks
add([MAXA - (i % 450) * 4000000 - i // 450 for i in range(N)])  # many decreasing blocks
add([i if i < N // 2 else N - i for i in range(N)])         # up then down
add([N // 2 - i if i < N // 2 else i - N // 2 for i in range(N)])   # down then up
add(merge(rand(N // 2, -MAXA, 0), [MAXA - i for i in range(N // 2)]))
add([ri(-MAXA, MAXA) if ri(0, 9) == 0 else -MAXA + 7 * i for i in range(N)])

os.makedirs("tests", exist_ok=True)
assert 25 <= len(tests) <= 35
for k, t in enumerate(tests, 1):
    with open(os.path.join("tests", f"{k:02d}.in"), "w", newline="\n") as f:
        f.write(t)
