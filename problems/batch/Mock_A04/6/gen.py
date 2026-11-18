# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(70406)
rnd = random.random
MAXN, MAXC = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(xs, hs, k, shuffle=True):
    xs, hs = list(xs), list(hs)
    if shuffle:
        random.shuffle(xs)
        random.shuffle(hs)
    n, m = len(xs), len(hs)
    assert 1 <= n <= MAXN and 1 <= m <= MAXN
    assert 1 <= k <= min(n, m)
    assert all(1 <= v <= MAXC for v in xs)
    assert all(1 <= a <= b <= MAXC for a, b in hs)
    lines = ["%d %d %d" % (n, m, k), " ".join(map(str, xs))]
    lines += ["%d %d" % h for h in hs]
    tests.append("\n".join(lines) + "\n")


def route(C, maxlen):
    a = ri(1, C)
    return (a, min(C, a + ri(0, maxlen)))


def rand_test(n, m, k, C, maxlen):
    add([ri(1, C) for _ in range(n)], [route(C, maxlen) for _ in range(m)], k)


def fifo_trap(n, m, k, C, noise=0.1, D=0):
    """pairs: a long route starting just left of a short one; the visitor at the short one must not take the long one"""
    xs, hs = [], []
    while len(xs) + 2 <= n and len(hs) + 2 <= m:
        c = ri(1, C - D - 3)
        w = ri(D + 2, max(D + 2, min(C - c, ri(1, 3) * 10 ** ri(1, 8))))
        hs.append((c, c + w))
        s = ri(c + 1, c + 1 + min(w - 1, 5))
        hs.append((s, s))
        xs.append(min(C, s + ri(0, D)))
        xs.append(min(C, ri(s + D + 1, c + w + D)))
    while len(xs) < n:
        xs.append(ri(1, C))
    while len(hs) < m:
        hs.append(route(C, int(C * noise)) if rnd() < 0.5 else route(C, 10))
    add(xs, hs, k)


def crowd_trap(n, m, k, C, group):
    """crowds of visitors around few routes: many visitors reach a route, but each route seats one"""
    xs, hs = [], []
    while len(hs) < m:
        hs.append(route(C, ri(0, 50)))
    centres = random.sample(hs, max(1, min(m, n // group)))
    while len(xs) < n:
        a, b = centres[ri(0, len(centres) - 1)]
        xs.append(max(1, min(C, ri(a - 20, b + 20))))
    add(xs, hs, k)


# samples
add([2, 6, 7, 15], [(4, 8), (10, 12), (1, 1)], 3, False)
add([5, 5, 5], [(5, 5), (5, 9), (1, 1), (20, 30)], 3, False)
add([10, 20, 30], [(1, 3), (14, 16), (24, 25), (40, 45), (100, 200)], 2, False)
add([3, 8, 8, 8, 12, 30], [(9, 11), (1, 4), (25, 27), (13, 13)], 4, False)
add([1000000000, 1, 500000000], [(400000000, 450000000), (999999990, 999999999)], 2, False)

# hidden: small (the brute force checks these)
add([7], [(7, 7)], 1)
add([1], [(1000000000, 1000000000)], 1)
add([1000000000, 1000000000], [(1, 1), (1, 1), (2, 3)], 2)
add([4, 50], [(1, 100), (4, 4)], 2)
add([5, 9, 30, 31], [(1, 40), (5, 5), (9, 9), (12, 31)], 4)
add([10, 10, 10, 10, 10], [(3, 4), (10, 10), (11, 13), (30, 30), (1, 1)], 4)
rand_test(8, 9, 1, 60, 20)
crowd_trap(300, 250, 160, 10 ** 6, 8)
fifo_trap(400, 300, 250, 10 ** 5, 0.1, 30)
fifo_trap(200, 380, 200, MAXC)

# hidden: big
N = MAXN
rand_test(N, N, N, MAXC, 1000)                       # every visitor must ride
rand_test(N, N, N // 2, 10 ** 8, 1000)
rand_test(N, N, N // 10, MAXC, 0)                    # one-point routes, a tenth must ride
fifo_trap(N, N, N, MAXC, 0.1, 1000)
fifo_trap(N, N, N * 9 // 10, MAXC, 0.3, 50)
fifo_trap(N, N, N // 2, 10 ** 8, 0.1, 7)
fifo_trap(N, N // 2 + 10, N // 2, MAXC, 0.1, 100000)
crowd_trap(N, N, N, MAXC, 4)
crowd_trap(N, N, N * 3 // 4, 10 ** 8, 20)
crowd_trap(N, N // 2, N // 2, MAXC, 2)
add([MAXC] * N, [(1, ri(1, 1000)) for _ in range(N)], N)                 # everyone walks almost 10^9
add([ri(1, 10 ** 8) for _ in range(N)], [(1, 10 ** 8)] * N, N)                 # every route covers the road
add([50000000] * N, [route(10 ** 8, 100) for _ in range(N)], N)            # all visitors at one spot
add([ri(1, MAXC) for _ in range(N)], [(v, v) for v in (ri(1, 10 ** 8) for _ in range(N))], N)   # one-point routes
add(range(1, N + 1), [(MAXC - N + 1, MAXC)] + [(j, j) for j in range(2, N + 1)], N)   # sorted, one far route
rand_test(N, N, N, 10 ** 6, 5)

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
