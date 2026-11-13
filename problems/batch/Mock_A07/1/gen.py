# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# c = a // L is the number of pieces of a pipe; a pipe is "exact" when a % L == 0.
# Queries mix: sums of the smallest exact c's (hit exactly, or just above), random K in [1, P],
# large K above the sum of every exact c, and K > P (answer -1).
import os, random

random.seed(4010)
rnd = random.random
MAXN, MAXQ, MAXL, MAXA, MAXK = 100000, 100000, 10 ** 9, 10 ** 9, 10 ** 15
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(L, a, ks):
    n, q = len(a), len(ks)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ and 1 <= L <= MAXL
    assert all(1 <= x <= MAXA for x in a)
    assert all(1 <= k <= MAXK for k in ks)
    tests.append(f"{n} {q} {L}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, ks)) + "\n")


def pipes(n, L, p_exact, cmin, cmax):
    """n pipes; with probability p_exact a multiple of L with c in [cmin, cmax], else a non-multiple"""
    a = []
    hi_c = min(cmax, MAXA // L)
    for _ in range(n):
        if rnd() < p_exact:
            a.append(L * ri(cmin, hi_c))
        else:
            while True:
                x = ri(1, MAXA) if rnd() < 0.5 or L * (hi_c + 1) > MAXA else ri(1, L * (hi_c + 1))
                if x % L:
                    break
            a.append(x)
    return a


def queries(a, L, q, w_hit=2, w_near=1, w_rand=1, w_top=6, w_over=0.3):
    exact = sorted(x // L for x in a if x % L == 0)
    P = sum(x // L for x in a)
    pre = [0]
    for c in exact:
        pre.append(pre[-1] + c)
    ws = [w_hit, w_near, w_rand, w_top, w_over]
    tot = sum(ws)
    ks = []
    for _ in range(q):
        r = rnd() * tot
        if r < ws[0] and len(pre) > 1:
            k = pre[ri(1, len(pre) - 1)]
        elif r < ws[0] + ws[1] and len(pre) > 1:
            m = ri(1, len(pre) - 1)
            nxt = exact[m] if m < len(exact) else 1
            k = pre[m] + ri(1, max(1, nxt - 1))
        elif r < ws[0] + ws[1] + ws[2]:
            k = ri(1, max(1, P))
        elif r < ws[0] + ws[1] + ws[2] + ws[3]:
            k = ri(max(1, pre[-1]), max(1, P))
        else:
            k = ri(P + 1, min(MAXK, 2 * P + 10))
        ks.append(max(1, min(k, MAXK)))
    return ks


# samples
add(3, [7, 6, 9, 4], [3, 5, 9])
add(5, [5, 5, 12], [2, 3, 4])
add(4, [8, 13, 4, 20, 2, 16], [1, 6, 10, 11, 12])
add(10, [35, 40, 100, 9, 60, 30], [2, 24, 26])
add(2, [10, 3, 4, 7, 6, 12, 1], [4, 9, 16, 21])

# hidden: small (brute checks these)
add(1, [1], [1, 2])
add(7, [6, 13, 20], [1, 2, 3, 4])                                    # no pipe is exact
add(4, [4, 4, 4, 4, 4], [1, 3, 5, 6])                                # every pipe is exactly L
add(1000, [999, 1000, 2000, 3500, 1], [1, 2, 3, 4, 5, 6, 7])
for L, n, cmax in ((3, 12, 6), (5, 30, 9), (2, 60, 12)):
    a = pipes(n, L, 0.6, 1, cmax)
    a = [x if x <= 40 * L else ri(1, 40 * L) for x in a]
    P = sum(x // L for x in a)
    add(L, a, list(range(1, P + 3)))                                 # every K
a = pipes(1000, 10 ** 8, 0.5, 1, 9)
add(10 ** 8, a, queries(a, 10 ** 8, 1000))                           # medium

# hidden: big (N = Q = 100000)
N, Q = MAXN, MAXQ
for L, p, cmin, cmax in ((1, 1.0, 1, MAXA), (3, 0.9, 1, 4 * 10 ** 6), (17, 0.85, 1, 6 * 10 ** 7),
                         (1000, 0.9, 1, 10 ** 6), (12345, 0.8, 1, 81000), (2, 0.95, 10 ** 6, 5 * 10 ** 8)):
    a = pipes(N, L, p, cmin, cmax)
    add(L, a, queries(a, L, Q))
# large K: almost every query needs every exact pipe
for L, p in ((5, 0.97), (999, 0.95), (40000, 0.97)):
    a = pipes(N, L, p, 1, MAXA // L)
    add(L, a, queries(a, L, Q, 1, 0, 1, 16, 1))
# few pieces per pipe, many short pipes
for L, p in ((10 ** 8, 0.9), (3 * 10 ** 8, 0.85), (10 ** 9, 0.9)):
    a = pipes(N, L, p, 1, 10)
    add(L, a, queries(a, L, Q))
# every exact c equal, and exact c with a few huge values
a = [7 * 123456 if rnd() < 0.9 else ri(1, MAXA) for _ in range(N)]
add(7, a, queries(a, 7, Q))
a = pipes(N, 50, 0.9, 1, 20)
for i in range(300):
    a[ri(0, N - 1)] = 50 * ri(10 ** 7, MAXA // 50)
add(50, a, queries(a, 50, Q, 2, 1, 1, 6, 0))
# exact pipes sorted from the largest c (input order = worst order), and K right at the sums
a = sorted(pipes(N, 9, 0.85, 1, 10 ** 8), key=lambda x: (x % 9 != 0, -x))
add(9, a, queries(a, 9, Q, 4, 1, 1, 4, 0))
# half the queries above P
a = pipes(N, 31, 0.6, 1, 3 * 10 ** 7)
add(31, a, queries(a, 31, Q, 1, 1, 2, 1, 5))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
