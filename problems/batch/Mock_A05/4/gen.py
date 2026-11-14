# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A route is (u, v, c); routes with v < u cannot be used (some tests have many of them).
import os, random

random.seed(52018)
rnd = random.random
MAXN, MAXR, MAXM = 500, 20000, 1000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, m, e):
    assert 2 <= n <= MAXN and 1 <= len(e) <= MAXR and 1 <= m <= MAXM
    for u, v, c in e:
        assert 1 <= u <= n and 1 <= v <= n and u != v and 0 <= c <= m
    tests.append("%d %d %d\n" % (n, len(e), m) + "".join(["%d %d %d\n" % x for x in e]))


def mixed(n, r, m, cfun, back=0.0, lo_span=1, hi_span=None):
    """random routes u -> v; v - u in [lo_span, hi_span] clipped at n, or v uniform in u+1..n without hi_span;
    a fraction `back` of them reversed"""
    e = []
    w = (hi_span or 0) - lo_span + 1
    for _ in range(r):
        u = 1 + int(rnd() * (n - 1))
        if hi_span:
            v = min(n, u + lo_span + int(rnd() * w))
        else:
            v = u + 1 + int(rnd() * (n - u))
        if back and rnd() < back:
            u, v = v, u
        e.append((u, v, cfun()))
    return e


N, R, M = MAXN, MAXR, MAXM
# samples
add(4, 4, [(1, 2, 1), (1, 4, 0), (2, 4, 1), (2, 3, 0), (3, 4, 2)])
add(3, 3, [(1, 3, 2), (1, 2, 1), (2, 3, 0)])
add(4, 5, [(1, 2, 0), (2, 3, 1), (2, 3, 2), (3, 4, 0), (1, 3, 3)])
add(5, 6, [(1, 2, 2), (2, 5, 3), (1, 3, 1), (3, 4, 4)])
add(5, 7, [(1, 2, 1), (1, 3, 0), (2, 4, 2), (4, 5, 0), (4, 2, 0), (3, 5, 3)])

# hidden: small and medium (brute checks these)
add(2, 1, [(1, 2, 1)])
add(2, 1000, [(2, 1, 0), (1, 2, 1000)])
add(8, 12, mixed(8, 20, 12, lambda: ri(0, 3), back=0.3))
add(30, 60, mixed(30, 400, 60, lambda: ri(0, 2), back=0.2))
add(6, 9, [(1, 2, 0), (2, 3, 1), (1, 4, 2), (4, 3, 0), (3, 5, 0), (6, 2, 0), (6, 5, 1), (2, 4, 3)])  # 6 unreachable
add(50, 400, [(i, i + 1, 0) for i in range(1, 50)])                                                 # one path
add(300, 300, mixed(300, 5000, 300, lambda: ri(0, 300)))
add(500, 200, mixed(500, 10000, 200, lambda: ri(0, 6), back=0.3, hi_span=40))

# hidden: big
add(N, M, mixed(N, R, M, lambda: ri(0, 2)))                                           # all large
add(N, M, mixed(N, R, M, lambda: ri(0, M)))
add(N, M, mixed(N, R, M, lambda: ri(0, M), back=0.3))
add(N, M, mixed(N, R, M, lambda: ri(0, 3), back=0.3))
add(N, M, mixed(N, R, M, lambda: ri(4, 9), hi_span=8))                                # long plans
add(N, M, mixed(N, R, M, lambda: ri(1, 4), hi_span=12))                               # long plans
add(N, M, mixed(N, R, M, lambda: ri(100, 400)))                                       # few rides per plan
add(N, M, mixed(N, R, M, lambda: ri(230, 500), back=0.2))
# a few distinct pairs, many copies of each
pairs = [(u, min(N, u + ri(1, 30)), ri(0, 20)) for u in range(1, N)] + mixed(N, 501, M, lambda: ri(0, 20))
add(N, M, [(u, v, ri(0, 20) if rnd() < 0.5 else c) for _ in range(R // len(pairs)) for u, v, c in pairs])
# star: 1 -> every city -> N, values stay below the limit
e = [(1, v, ri(0, M)) for v in range(2, N)] + [(v, N, ri(0, M)) for v in range(2, N)]
e += [(N, ri(1, N - 1), ri(0, M)) for _ in range(R - len(e))]
add(N, M, e)
# no route into city N can be used
e = mixed(N - 1, R - 2000, M, lambda: ri(0, 5)) + [(N, ri(1, N - 1), ri(0, 5)) for _ in range(2000)]
add(N, M, e)
# one chain with heavy stays (only the last nights have plans) + many rides that need too many nights
e = [(i, i + 1, 2) for i in range(1, N)]
for i in random.sample(range(N - 1), 8):
    e[i] = (e[i][0], e[i][1], 1)
e += mixed(N, R - len(e), M, lambda: ri(400, M))
add(N, M, e)
# layers: 1 -> layer A -> layer B -> N with big stays, values cross the limit in the middle
A, B = list(range(2, 251)), list(range(251, N))
e = [(1, a, ri(0, 250)) for a in A] + [(b, N, ri(0, 250)) for b in B]
e += [(A[ri(0, len(A) - 1)], B[ri(0, len(B) - 1)], ri(0, 400)) for _ in range(R - len(e))]
add(N, M, e)
# short jumps, mostly c = 0, some backward
add(N, M, mixed(N, R, M, lambda: 0 if rnd() < 0.7 else ri(1, 10), back=0.15, hi_span=6))
# medium jumps, stays 0..50
add(N, M, mixed(N, R, M, lambda: ri(0, 50), lo_span=10, hi_span=100))
# the second half of the cities only reached late
e = mixed(250, R // 2, M, lambda: ri(0, 3))
e += [(u + 250, v + 250, c) for u, v, c in mixed(250, R // 2 - 50, M, lambda: ri(0, 3))]
e += [(ri(1, 250), ri(251, N), ri(600, 800)) for _ in range(50)]
add(N, M, e)
# many routes from city 1 and into city N
e = [(1, ri(2, N), ri(0, M)) for _ in range(6000)] + [(ri(1, N - 1), N, ri(0, M)) for _ in range(6000)]
e += mixed(N, R - len(e), M, lambda: ri(0, M))
add(N, M, e)
add(N, M, mixed(N, R, M, lambda: ri(0, 8), back=0.5, hi_span=25))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
