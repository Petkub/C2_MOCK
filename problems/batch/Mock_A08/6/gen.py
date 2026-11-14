import random, os
random.seed(2604)
_rnd = random.random


def ri(a, b):
    """random integer in [a, b] from random() only (much faster than randint, same on every Python 3)"""
    return a + int(_rnd() * (b - a + 1))


def two(lo, hi):
    """two different random integers in [lo, hi]"""
    u = ri(lo, hi)
    v = ri(lo, hi - 1)
    return u, (v + 1 if v >= u else v)


os.makedirs("tests", exist_ok=True)
cases = []
# ---- samples ----
cases.append((4, 20, [(1, 2, 0, 5, 3), (2, 4, 2, 6, 4), (1, 3, 1, 4, 2), (3, 4, 0, 10, 7), (3, 2, 0, 1, 1)]))
cases.append((3, 10, [(1, 2, 0, 3, 4), (2, 3, 1, 5, 4)]))
cases.append((2, 2, [(1, 2, 0, 7, 3)]))
cases.append((4, 30, [(1, 2, 5, 10, 2), (2, 3, 0, 4, 3), (3, 1, 0, 5, 1), (2, 4, 9, 20, 1), (3, 4, 0, 100, 1)]))
cases.append((5, 25, [(1, 2, 1, 4, 3), (2, 5, 2, 6, 5), (1, 3, 0, 5, 2), (3, 4, 4, 7, 6), (4, 5, 1, 3, 2), (2, 4, 0, 9, 1)]))
# ---- small random ----
def rnd_edges(n, m, pr, wr):
    E = []
    for _ in range(m):
        u, v = two(1, n)
        p = ri(*pr); o = ri(0, p - 1); w = ri(*wr)
        E.append((u, v, o, p, w))
    return E
def with_path(n, E, hops, pr, wr):
    mids = random.sample(range(2, n), min(hops, n - 2))
    seq = [1] + mids + [n]
    for a, b in zip(seq, seq[1:]):
        p = ri(*pr); E.append((a, b, ri(0, p - 1), p, ri(*wr)))
    random.shuffle(E)
    return E
for _ in range(6):
    n = ri(2, 6)
    cases.append((n, ri(5, 40), rnd_edges(n, ri(1, 10), (1, 10), (1, 8))))
# ---- large ----
N, M, B = 100000, 100000, 10**9
cases.append((N, B, with_path(N, rnd_edges(N, M - 30, (1, 10**7), (1, 10**4)), 29, (1, 10**7), (1, 10**4))))
cases.append((N, B, with_path(N, rnd_edges(N, M - 30, (1, 50), (1, 10**4)), 29, (1, 50), (1, 10**4))))
cases.append((N, 10**6, with_path(N, rnd_edges(N, M - 30, (1, 1000), (1, 100)), 29, (1, 1000), (1, 100))))
cases.append((N, B, with_path(N, rnd_edges(N, 40000, (10**8, 10**9), (10**7, 10**8)), 2, (10**8, 3 * 10**8), (10**7, 10**8))))   # big numbers
# long chain 1 -> 2 -> ... -> N with noise edges
E = [(i, i + 1, ri(0, 9), 10, ri(1, 1000)) for i in range(1, N)]
E += rnd_edges(N, M - len(E), (1, 10**6), (10**5, 10**6))
cases.append((N, B, E))
# chain where every hop has a single departure time (p huge): exact boundary checks
E = [(1, 2, 7, 13, 100)]
t = 7 + 13 * 380 + 100          # arrive at station 2 at this time if you catch the 381st train
for i in range(2, 1000):
    t += ri(0, 5)   # next (only) departure
    w = ri(1, 1000)
    E.append((i, i + 1, t, B, w)); t += w
cases.append((1000, t, E))
cases.append((1000, t - 1, E))
# layered DAG: many choices, depart time tradeoffs
L, W = 100, 500
def node(l, j): return l * W + j + 1
E = []
for l in range(L - 1):
    for j in range(W):
        for _ in range(2):
            p = ri(1, 100); E.append((node(l, j), node(l + 1, ri(0, W - 1)), ri(0, p - 1), p, ri(1, 50)))
n = L * W
E += [(node(L - 1, j), n, 0, 1, 1) for j in range(W - 1)]
E += [(1, node(0, j), ri(0, 9), 10, 1) for j in range(1, W)]
cases.append((n, 10**6, E[:100000]))
# N unreachable (all trains point away from N)
E = rnd_edges(20000 - 1, 50000 - 5, (1, 100), (1, 100)) + [(20000, ri(1, 19999), 0, 1, 1) for _ in range(5)]
cases.append((20000, B, E))
# T = 0: nothing can arrive in time
cases.append((N, 0, rnd_edges(N, 30000, (1, 10), (1, 10))))
# star through hub with wide period choices
E = []
for i in range(2, N):
    p = ri(1, 10**6); E.append((1, i, ri(0, p - 1), p, ri(1, 10**6)))
    p = ri(1, 10**6); E.append((i, N, ri(0, p - 1), p, ri(1, 10**6)))
cases.append((N, B, E[:M]))
# 32-bit overflow trap: departure + travel time exceeds 2^31
E = rnd_edges(N, 50000, (5 * 10**8, 10**9), (5 * 10**8, 10**9))
E += [(1, N, 5 * 10**8, 10**9, 10**9), (1, 2, 0, 1, 1), (2, 3, 0, 1, 1), (3, N, 0, 1, 1)]
random.shuffle(E)
cases.append((N, 10**9, E))
# more 32-bit traps for the forward approach: late departures with long trips everywhere
for hops in (3, 12):
    n2 = N
    E = rnd_edges(n2, 60000, (6 * 10**8, 10**9), (6 * 10**8, 10**9))     # 60 000 lines keep the file near 2.7 MB
    E += [(1, n2, 7 * 10**8, 10**9, 9 * 10**8)]
    E = with_path(n2, E, hops, (1, 1000), (1, 10**4))
    cases.append((n2, 10**9, E))
# medium random graphs
for _ in range(3):
    cases.append((N, ri(10**5, 10**9), with_path(N, rnd_edges(N, M - 16, (1, 10**5), (1, 10**4)), 15, (1, 10**5), (1, 10**4))))
# the old sample 5 (values near 10^9), moved here when the sample was replaced (2026-11-02)
cases.append((3, 10**9, [(1, 2, 999999998, 999999999, 1), (2, 3, 0, 10**9, 10**9), (1, 3, 1, 2, 10**9 - 1)]))
# rare trains: about 10^4 busy stations, many lines run only a few times (period 10^8..10^9),
# so the latest usable departure is often before the first one
for seed, rare in ((26053, 0.5), (26052, 1.0)):
    random.seed(seed)
    act = list(range(1, 7000)) + [N]
    E = []
    for _ in range(65000):          # 65 000 lines of big numbers: about 2.8 MB
        i, j = two(0, len(act) - 1)
        u, v = act[i], act[j]
        p = ri(10**8, 10**9) if _rnd() < rare else ri(1, 10**6)
        E.append((u, v, ri(0, p - 1), p, ri(10**6, 10**8)))
    cases.append((N, 10**9, E))
for i, (n, T, E) in enumerate(cases, 1):
    assert 2 <= n <= 100000 and 1 <= len(E) <= 100000 and 0 <= T <= 10**9
    assert all(1 <= u <= n and 1 <= v <= n and u != v and 0 <= o < p <= 10**9 and 1 <= w <= 10**9 for u, v, o, p, w in E)
    open(f"tests/{i:02d}.in", "w").write(f"{n} {len(E)} {T}\n" + "".join(f"{u} {v} {o} {p} {w}\n" for u, v, o, p, w in E))
print(len(cases), "tests")
