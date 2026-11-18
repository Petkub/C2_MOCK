# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Integer-only randomness (random.Random.randint), so every platform builds the same files.
import os, random

r = random.Random(90107)
MAXN = MAXQ = 100000
MAXA, MAXB, MAXK = 10 ** 9, 10 ** 9, 10 ** 15
tests = []


def ri(a, b):
    return r.randint(a, b)


def intervals(a, b):
    out, p, s = [], 0, 0
    for x, y in zip(a, b):
        p += x
        s += y
        out.append((p - s, p + s))
    return out


def add(a, b, k):
    n, q = len(a), len(k)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ and len(b) == n
    assert all(-MAXA <= x <= MAXA for x in a)
    assert all(0 <= x <= MAXB for x in b)
    assert all(-MAXK <= x <= MAXK for x in k)
    tests.append(f"{n} {q}\n{' '.join(map(str, a))}\n{' '.join(map(str, b))}\n{' '.join(map(str, k))}\n")


def targets(a, b, q, mix):
    """q targets; mix = weights of (inside, endpoint, endpoint +- 1, gap of the union, anywhere, far away)"""
    iv = intervals(a, b)
    lo_all = min(l for l, h in iv)
    hi_all = max(h for l, h in iv)
    srt = sorted(iv)
    gaps, reach = [], srt[0][1]
    for l, h in srt[1:]:
        if l > reach + 1:
            gaps.append((reach + 1, l - 1))
        reach = max(reach, h)
    kinds = []
    for kind, w in enumerate(mix):
        kinds += [kind] * w
    out = []
    while len(out) < q:
        kind = kinds[ri(0, len(kinds) - 1)]
        l, h = iv[ri(0, len(iv) - 1)]
        if kind == 0:
            if h - l < 2:
                continue
            v = ri(l + 1, h - 1)
        elif kind == 1:
            v = l if ri(0, 1) else h
        elif kind == 2:
            v = l - 1 if ri(0, 1) else h + 1
        elif kind == 3:
            if not gaps:
                continue
            g = gaps[ri(0, len(gaps) - 1)]
            v = ri(g[0], g[1])
        elif kind == 4:
            v = ri(lo_all - 10, hi_all + 10)
        else:
            v = ri(-MAXK, lo_all - 1) if ri(0, 1) else ri(hi_all + 1, MAXK)
        if -MAXK <= v <= MAXK:
            out.append(v)
    return out


# samples (every target is outside all intervals or on an end of one)
add([4, 7, -9, 6, 3], [0, 0, 0, 0, 0], [9, -3, 11])
add([5, -8, 10], [1, 2, 0], [2, 13])
add([-3, -3, 10, 2, -20, 1], [0, 1, 0, 2, 1, 0], [-10, 25, -4, 0])
add([-10 ** 9], [5], [10 ** 15, -10 ** 15])
add([2, 2, 2, -15, 30, -1, -1, 0], [0, 1, 0, 1, 0, 2, 0, 3], [8, 30, -20, 26, 11, 0])

# hidden: small (the brute simulates every position)
add([7], [0], [7])
add([0], [3], [-5, -3, -1, 0, 2, 3, 4])
add([0, 0, 0, 0], [0, 1, 0, 2], list(range(-5, 6)))
for _ in range(5):
    n = ri(3, 8)
    a = [ri(-12, 12) for _ in range(n)]
    b = [ri(0, 2) for _ in range(n)]
    add(a, b, targets(a, b, ri(10, 30), [3, 2, 2, 3, 3, 0]))
a = [9, 8, 10, -40, 9, 12, 7, 9]
b = [1, 0, 0, 0, 1, 0, 0, 0]
add(a, b, targets(a, b, 30, [3, 1, 2, 4, 2, 0]))


# hidden: max size (N = Q = 100 000)
N, Q = MAXN, MAXQ


def walk(lo, hi, n=N):
    return [ri(lo, hi) for _ in range(n)]


a, b = walk(-MAXA, MAXA), walk(0, 99)                         # random walk, narrow intervals, huge sums
add(a, b, targets(a, b, Q, [3, 1, 2, 3, 1, 0]))
a, b = walk(-MAXA, MAXA), [0] * N                             # single points
add(a, b, targets(a, b, Q, [0, 2, 3, 4, 1, 0]))
a, b = walk(0, 60000), walk(0, 9)                             # rising, gaps between the intervals
add(a, b, targets(a, b, Q, [4, 1, 1, 4, 0, 0]))
a, b = walk(-60000, 0), walk(0, 9)                            # falling
add(a, b, targets(a, b, Q, [4, 1, 1, 4, 0, 0]))
a, b = [0] * N, walk(0, 30000)                                # nested intervals around 0
add(a, b, targets(a, b, Q, [3, 1, 1, 0, 1, 3]))
a, b = walk(-1000, 1000), walk(0, 1)                          # dense, small values
add(a, b, targets(a, b, Q, [2, 2, 2, 3, 1, 3]))
a = [(MAXA if i % 2 == 0 else -MAXA + ri(0, 3)) for i in range(N)]   # zigzag, drifting slowly
b = walk(0, 2)
add(a, b, targets(a, b, Q, [3, 1, 2, 3, 1, 0]))
a = [MAXA] * N                                                # extreme sums near 10^14
b = [MAXB if i % 50 == 0 else 0 for i in range(N)]
add(a, b, targets(a, b, Q, [3, 1, 2, 0, 1, 3]))
a, b = [-MAXA] * N, walk(0, 1000)                             # far negative, targets beyond both ends
add(a, b, targets(a, b, Q, [3, 1, 1, 3, 0, 2]))
a, b = walk(30000, 90000), walk(0, 1)                         # rising, overlapping intervals
add(a, b, targets(a, b, Q, [3, 1, 1, 4, 1, 1]))
a = walk(-50000, 50000)
b = [ri(0, 50) if ri(0, 999) else ri(10 ** 3, 10 ** 4) for _ in range(N)]   # a few wide jumps of the width
add(a, b, targets(a, b, Q, [3, 1, 1, 3, 1, 1]))
a, b = walk(-MAXA, MAXA), walk(0, 99)                         # the same target many times
k = targets(a, b, 50, [3, 1, 1, 3, 0, 0])
add(a, b, [k[ri(0, 49)] for _ in range(Q)])
a, b = walk(1, 9), [0] * N                                    # rising slowly, B = 0: every point a gap of < 10
add(a, b, targets(a, b, Q, [0, 2, 3, 4, 1, 0]))
a = [ri(-MAXA, MAXA) if i < 1000 else ri(-3, 3) for i in range(N)]   # big moves first, then small
b = walk(0, 5)
add(a, b, targets(a, b, Q, [4, 1, 1, 3, 1, 0]))
a, b = walk(-20000, 25000), walk(0, 4)                        # slow random drift
add(a, b, targets(a, b, Q, [4, 1, 2, 3, 0, 0]))
a, b = walk(-5000, 5000), walk(0, 100)                        # mostly overlapping intervals
add(a, b, targets(a, b, Q, [2, 1, 2, 4, 1, 3]))
a = walk(-MAXA, MAXA)
b = [ri(0, 10 ** 6) for _ in range(N)]                        # the widths grow fast
add(a, b, targets(a, b, Q, [2, 1, 2, 2, 1, 3]))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
