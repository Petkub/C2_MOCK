# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Most tests are built from the offsets q_0 = 0, q_1, ..., q_(N-1) of every stop from the first one
# (a_i = a_1 + q_(i-1), d_i = q_i - q_(i-1)); the record has exactly one sequence iff M - 1 = max(q) - min(q).
import os, random

random.seed(2020205)
rnd = random.random
MAXN, MAXM, MAXD = 200000, 10 ** 18, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(m, d):
    n = len(d) + 1
    assert 2 <= n <= MAXN and 1 <= m <= MAXM
    assert all(-MAXD <= x <= MAXD for x in d)
    tests.append(f"{n} {m}\n" + " ".join(map(str, d)) + "\n")


def diffs(q):
    """q = offsets of stops 2..N from stop 1 (q_0 = 0 is implicit)"""
    out, prev = [], 0
    for x in q:
        out.append(x - prev)
        prev = x
    return out


def span(d):
    s = lo = hi = 0
    for x in d:
        s += x
        if s < lo:
            lo = s
        if s > hi:
            hi = s
    return hi - lo


def walk(n, step):
    return [ri(-step, step) for _ in range(n - 1)]


def from_stops(a):
    return [a[i + 1] - a[i] for i in range(len(a) - 1)]


N = MAXN
# samples
add(6, [2, -3, 4, -1])                      # 2 sequences
add(7, [3, -5, 2, 4, -1])                   # exactly one
add(5, [4, -2, -3])                         # none
add(100, [-7, 10])
add(9, [1, 4, -6, 2, 3, -1, 4])             # exactly one
# hidden: small (brute checks these)
add(1, [0])
add(2, [3])                                 # none
add(MAXM, [-MAXD])
d = [ri(1, 9) for _ in range(30)]           # every stop after the first is higher: stop 1 is the lowest
add(span(d) + 1, d)
d = [-ri(1, 9) for _ in range(40)]          # stop 1 is the highest
add(span(d) + 1, d)
d = walk(50, 6)
add(span(d) + 3, d)
d = walk(1000, 50)
add(span(d), d)                             # none, short by one
q = [ri(1, 3000) for _ in range(2999)]      # stop 1 is the only lowest one
add(span(diffs(q)) + 1, diffs(q))
a = [ri(1, 2500) for _ in range(5000)]
a[ri(0, 4999)], a[ri(0, 4999)] = 1, 2500
add(2500, from_stops(a))                    # labels 1..M, both ends used
q = [-ri(1, 10 ** 9 - 1) for _ in range(20)]
q[-1] = 1 - 10 ** 9
add(10 ** 9, diffs(q))                      # stop 1 is the only highest one, exactly one
# hidden: big (N = 200000)
d = walk(N, MAXD)
add(span(d) + 1, d)                         # exactly one, stops up to ~10^11
d = walk(N, MAXD)
add(MAXM, d)
d = walk(N, MAXD)
add(span(d) - ri(1, 10 ** 10), d)           # none
d = walk(N, MAXD)
add(span(d) + 2, d)
a = [ri(1, N) for _ in range(N)]
a[ri(0, N - 1)], a[ri(0, N - 1)] = 1, N
add(N, from_stops(a))                       # labels 1..N as in a delivery log
a = [ri(N // 2 - 100, N // 2 + 100) for _ in range(N - 2)] + [3, N - 2]
add(N, from_stops(a))                       # stays near the middle until the last two stops
a = [ri(N // 2 - 100, N // 2 + 100) for _ in range(N - 2)] + [N + 1, 1]
add(N, from_stops(a))                       # none, short by one, at the last two stops
d = [ri(1, 20000) for _ in range(N - 1)]    # stop 1 is the lowest
add(span(d) + 1, d)
d = [-ri(1, 20000) for _ in range(N - 1)]   # stop 1 is the highest
add(span(d) + ri(1, 10 ** 12), d)
add(1, [0] * (N - 1))
add(MAXM, [0] * (N - 1))
d = walk(N, 1)
add(span(d) + 1, d)
q, x = [], 0                                # stop 1 is the only lowest one, big steps
for _ in range(N - 1):
    x += ri(-MAXD, MAXD)
    if x <= 0:
        x = -x + 1
    q.append(x)
add(span(diffs(q)) + 1, diffs(q))
q, x = [], 0                                # stop 1 is the only highest one, big steps
for _ in range(N - 1):
    x += ri(-MAXD, MAXD)
    if x >= 0:
        x = -x - 1
    q.append(x)
add(MAXM - ri(0, 10 ** 15), diffs(q))
d = walk(N, 1000)
d[ri(0, N - 2)] = MAXD
add(span(d) + 1, d)                         # one huge move
d = [ri(-MAXD, MAXD // 2) for _ in range(N - 1)]
add(ri(10 ** 17, MAXM), d)                  # drifts down: lowest stop near the end
d = [ri(-MAXD // 2, MAXD) for _ in range(N - 1)]
add(span(d) + 1, d)                         # drifts up: lowest near the start, highest near the end
d = walk(N, 10 ** 6)
add(span(d) - ri(1, 10 ** 6), d)            # none
d = walk(N, 10 ** 5)
d[ri(N // 2, N - 2)] = -MAXD
add(MAXD, d)                                # none: one move as long as the rail
d = [ri(-MAXD, MAXD // 3) for _ in range(N - 1)]
add(span(d) + 1, d)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
