# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# One robot can do task j then task i iff u_j <= u_i and w_j <= w_i with u = T - P*A, w = T + Q*A; the answer is
# the longest chain with u strictly increasing and w strictly decreasing (Dilworth). The big tests stress:
# full-speed moves (equal u or equal w: the tie order), identical tasks, keys far above 2^31, the natural greedy
# (give a task to any robot that reaches it), the symmetric P = Q = 1 keys, answers from 1 to M.
import os, random

random.seed(2020)
rnd = random.random
MAXM, MAXV = 100000, 10 ** 9
M = MAXM
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, p, q, ts, a_s, mix=True):
    m = len(ts)
    assert 1 <= m <= MAXM and len(a_s) == m
    assert 1 <= n <= MAXV and 1 <= p <= MAXV and 1 <= q <= MAXV
    assert all(1 <= t <= MAXV for t in ts) and all(1 <= a <= n for a in a_s)
    if mix:
        order = list(range(m))
        random.shuffle(order)
        ts = [ts[i] for i in order]
        a_s = [a_s[i] for i in order]
    tests.append("%d %d %d %d\n%s\n%s\n" % (n, m, p, q, " ".join(map(str, ts)), " ".join(map(str, a_s))))


def rand_test(n, m, p, q, tmax, alo=1, ahi=None):
    ahi = n if ahi is None else ahi
    add(n, p, q, [ri(1, tmax) for _ in range(m)], [ri(alo, ahi) for _ in range(m)])


def routes(n, m, p, q, k, dmax, full=0.0, tstart=1, alo=1, ahi=None):
    """k robots move along the rail legally; the tasks are points of their routes (answer <= k).
    full: chance that a step is a full-speed move (equal u or equal w with the previous task)."""
    ahi = n if ahi is None else ahi
    ts, a_s = [], []
    per = [m // k + (1 if i < m % k else 0) for i in range(k)]
    for c in per:
        t, a = ri(tstart, tstart + dmax), ri(alo, ahi)
        for _ in range(c):
            ts.append(t)
            a_s.append(a)
            dt = ri(0, dmax)
            if rnd() < full:
                if rnd() < 0.5:
                    step = min(dt // p, ahi - a)
                    a += step
                    dt = step * p
                else:
                    step = min(dt // q, a - alo)
                    a -= step
                    dt = step * q
            else:
                lo, hi = max(alo, a - dt // q), min(ahi, a + dt // p)
                a = ri(lo, hi)
            t = min(MAXV, t + dt)
    add(n, p, q, ts, a_s)


def lines(n, m, p, q, tmax, alo=1, ahi=None):
    """tasks on full-speed lines: many equal u = T - P*A or equal w = T + Q*A"""
    ahi = n if ahi is None else ahi
    ts, a_s = [], []
    while len(ts) < m:
        a = ri(alo, ahi)
        t = ri(1, tmax)
        for _ in range(min(ri(2, 6), m - len(ts))):
            ts.append(t)
            a_s.append(a)
            if rnd() < 0.5:
                if a + 1 > ahi or t + p > MAXV:
                    break
                a, t = a + 1, t + p
            else:
                if a - 1 < alo or t + q > MAXV:
                    break
                a, t = a - 1, t + q
    add(n, p, q, ts[:m], a_s[:m])


# samples
add(6, 1, 2, [1, 2, 4, 5], [2, 5, 3, 4], False)
add(10, 2, 1, [3, 3, 5, 1, 9, 9], [4, 4, 7, 6, 2, 8], False)
add(20, 1, 2, [24, 11, 28, 3, 4, 19, 15, 27, 3], [18, 4, 9, 15, 18, 4, 12, 17, 2], False)
add(30, 2, 5, [16, 13, 24, 5, 25, 26, 13, 1], [2, 2, 16, 21, 2, 24, 12, 25], False)
add(MAXV, MAXV, MAXV, [MAXV], [MAXV], False)
# hidden: small and medium (brute checks these)
add(5, 1, 1, [7, 7], [2, 3])
rand_test(8, 12, 2, 3, 15)
rand_test(15, 60, 1, 2, 30)
lines(30, 300, 3, 2, 200)
routes(1000, 1500, 4, 7, 30, 60, 0.3)
rand_test(100, 2000, 2, 1, 1000)
routes(MAXV, 2000, ri(10 ** 7, 10 ** 8), ri(10 ** 7, 10 ** 8), 40, 10 ** 8, 0.3, 1, MAXV - 50, MAXV)
# hidden: big (M = 100000)
add(MAXV, ri(1, MAXV), ri(1, MAXV), [ri(1, MAXV)] * M, [ri(1, MAXV)] * M)          # one task repeated
add(MAXV, ri(1, 100), ri(1, 100), [777] * M, [ri(1, MAXV) for _ in range(M)])     # all at one time
add(MAXV, ri(1, 100), ri(1, 100), [ri(1, MAXV) for _ in range(M)], [ri(1, MAXV)] * M)  # all on one stop
rand_test(MAXV, M, ri(1, MAXV), ri(1, MAXV), MAXV)                                  # nearly all incomparable
rand_test(10 ** 6, M, 1, 1, 10 ** 6)                                                # the symmetric case
rand_test(10 ** 5, M, 1, 10 ** 6, 10 ** 9)                                          # going down is very slow
rand_test(10 ** 5, M, 10 ** 6, 1, 10 ** 9)                                          # going up is very slow
rand_test(1000, M, 3, 7, 50000)
rand_test(200, M, 5, 2, 10 ** 6)
routes(MAXV, M, ri(10 ** 7, MAXV), ri(10 ** 7, MAXV), 300, 10 ** 9 // 400, 0.4, 1, MAXV - 100, MAXV)  # keys > 2^31
routes(MAXV, M, ri(2 * 10 ** 6, 10 ** 7), ri(2 * 10 ** 6, 10 ** 7), 50, 10 ** 9 // 2500, 0.5, 1, MAXV - 1000, MAXV)
lines(MAXV, M, 3, 5, 10 ** 6, 1, 3000)                                              # many full-speed pairs
lines(500, M, 1, 1, 50000)
routes(10 ** 6, M, 2, 3, 1, 10000, 0.7)                                             # one robot is enough
routes(10 ** 6, M, 5, 1, 20, 50000, 0.5)
routes(10 ** 5, M, 1, 4, 2000, 1500, 0.4)
routes(10 ** 6, M, 7, 3, 20000, 10000, 0.3)
add(MAXV, 1, 1, [ri(1, 10 ** 6) for _ in range(M)], [ri(1, 10 ** 5) for _ in range(M)])
rand_test(MAXV, M, ri(10 ** 8, MAXV), ri(10 ** 8, MAXV), MAXV, MAXV - 20, MAXV)    # keys near -10^18 and 10^18

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
