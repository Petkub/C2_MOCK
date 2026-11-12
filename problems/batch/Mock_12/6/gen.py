# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1260521)
rnd = random.random
MAXN = MAXQ = 100000
MAXV = 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a, ops):
    n, q = len(a), len(ops)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(-MAXV <= x <= MAXV for x in a)
    assert any(o[0] == 2 for o in ops)
    for t, u, v in ops:
        if t == 1:
            assert 1 <= u <= n and -MAXV <= v <= MAXV
        else:
            assert t == 2 and 1 <= u <= v <= n
    lines = [f"{n} {q}", " ".join(map(str, a))]
    lines += [f"{t} {u} {v}" for t, u, v in ops]
    tests.append("\n".join(lines) + "\n")


def vals(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def mixed(n, big):
    """mostly positive, some negative: big = values up to 10^9"""
    hi = MAXV if big else 1000
    return [ri(-hi, hi) if rnd() < 0.3 else ri(0, hi) for _ in range(n)]


def wavy(n, big):
    """runs where taking every second stall is not best: a big value next to two medium ones"""
    hi = MAXV if big else 1000
    a = []
    while len(a) < n:
        k = ri(1, 4)
        m = ri(hi // 3, hi // 2)
        a += [m, ri(hi // 2 + 1, hi)] * k + [m]
        a += [ri(-hi, 0) for _ in range(ri(0, 2))]
    return a[:n]


def queries(n, q, upd, lo_len, vgen):
    """q operations, a fraction upd of updates (new value from vgen()); ranges at least lo_len long"""
    ops = []
    for _ in range(q):
        if rnd() < upd:
            ops.append((1, ri(1, n), vgen()))
        else:
            ln = ri(lo_len, n)
            l = ri(1, n - ln + 1)
            ops.append((2, l, l + ln - 1))
    if all(o[0] == 1 for o in ops):
        ops[-1] = (2, 1, n)
    return ops


def longq(n, q, upd, vgen):
    """every range starts in the first tenth and ends in the last tenth"""
    ops = []
    for _ in range(q):
        if rnd() < upd:
            ops.append((1, ri(1, n), vgen()))
        else:
            ops.append((2, ri(1, max(1, n // 10)), ri(n - n // 10, n)))
    if all(o[0] == 1 for o in ops):
        ops[-1] = (2, 1, n)
    return ops


# samples
add([3, -1, 4, 1, 5, 9], [(2, 1, 6), (1, 4, 10), (2, 2, 5), (2, 1, 6)])
add([-5, 2, -3, 4, -1], [(2, 1, 5), (1, 3, 7), (2, 1, 5), (2, 4, 5)])
add([6, 8, 2, 7, 3, 5, 9, 4], [(2, 1, 8), (1, 2, -4), (2, 1, 3), (2, 5, 8)])
add([5, 1, 1, 5, 2, 8, 3, 3, 7], [(2, 1, 9), (1, 6, 2), (2, 4, 9), (2, 1, 4)])
add([4, -2, 6, 6, -3, 8, 1], [(2, 2, 6), (1, 5, 5), (2, 3, 7)])

# hidden: small (brute checks these)
add([-7], [(2, 1, 1)])
add([0, 0, 0], [(2, 1, 3), (1, 2, 5), (2, 1, 3), (2, 1, 1)])
add(vals(12, -20, -1), queries(12, 30, 0.2, 1, lambda: ri(-20, -1)))             # all negative: 0
add(vals(300, -50, 50), queries(300, 600, 0.3, 1, lambda: ri(-50, 50)))
add(mixed(2000, True), queries(2000, 3000, 0.4, 1, lambda: ri(-MAXV, MAXV)))
add(wavy(3000, False), queries(3000, 3000, 0.2, 1, lambda: ri(0, 1000)))
add(vals(1500, -MAXV, -1) , queries(1500, 2000, 0.3, 1, lambda: ri(-MAXV, MAXV // 50)))  # mostly negative
add(vals(5000, MAXV - 1000, MAXV), queries(5000, 5000, 0.1, 2000, lambda: MAXV))   # large values

# hidden: big (N = Q = 100000)
N, Q = MAXN, MAXQ
big = lambda: ri(-MAXV, MAXV)
pos = lambda: ri(0, MAXV)
small = lambda: ri(-1000, 1000)
add(mixed(N, True), queries(N, Q, 0.3, 1, big))
add(mixed(N, True), longq(N, Q, 0.2, pos))
add(vals(N, MAXV - 10 ** 6, MAXV), longq(N, Q, 0.0, pos))                          # only questions
add(vals(N, MAXV, MAXV), longq(N, Q, 0.05, lambda: MAXV))
add(wavy(N, True), queries(N, Q, 0.25, N // 2, lambda: ri(MAXV // 3, MAXV)))
add(wavy(N, False), longq(N, Q, 0.25, lambda: ri(0, 1000)))
add(vals(N, -MAXV, -1), longq(N, Q, 0.3, lambda: ri(-MAXV, -1)))                   # always 0
a = vals(N, -MAXV, -1)
for i in range(0, N, 997):
    a[i] = ri(1, MAXV)
add(a, longq(N, Q, 0.3, lambda: ri(-MAXV, MAXV // 1000)))                          # mostly negative
add(vals(N, -1000, 1000), queries(N, Q, 0.3, N // 3, small))
add(vals(N, -1000, 1000), longq(N, Q, 0.5, small))
add(vals(N, 0, 1000), longq(N, Q, 0.1, lambda: ri(0, 1000)))
add(vals(N, 0, 0), longq(N, Q, 0.5, lambda: ri(0, 1)))
add([ri(1, 9) * (i % 2 * 2 - 1) for i in range(N)], longq(N, Q, 0.2, lambda: ri(-9, 9)))  # + - + - ...
add(mixed(N, False), [(2, 1, N)] * (Q // 2) + [(2, 2, N)] * (Q - Q // 2))         # whole range again and again
a = mixed(N, True)
ops = []
for k in range(Q):
    i = ri(1, N)
    ops.append((1, i, big()) if k % 2 == 0 else (2, max(1, i - N // 2), min(N, i + N // 2)))
add(a, ops)
add(vals(N, 1, 3), longq(N, Q, 0.3, lambda: ri(1, 3)))
add(vals(N, -5, 10), queries(N, Q, 0.3, 1, lambda: ri(-5, 10)))                    # random lengths

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
