# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(100324)
MAXN, MAXM, MAXW = 100000, 100000, 10 ** 6       # MAXM bounds M1 + M2
tests = []


def add(n, roads, shuttles):
    assert 1 <= n <= MAXN and len(roads) + len(shuttles) <= MAXM
    for u, v, w in roads:
        assert 1 <= u <= n and 1 <= v <= n and u != v and 1 <= w <= MAXW
    for u, l, r, c in shuttles:
        assert 1 <= u <= n and 1 <= l <= r <= n and 1 <= c <= MAXW
    lines = [f"{n} {len(roads)} {len(shuttles)}"]
    lines += ["%d %d %d" % e for e in roads]
    lines += ["%d %d %d %d" % s for s in shuttles]
    tests.append("\n".join(lines) + "\n")


def rand_roads(n, m, wlo, whi, stations=None):
    r = random.random
    st = stations if stations is not None else range(1, n + 1)
    k = len(st)
    out = []
    while len(out) < m:
        u, v = st[int(r() * k)], st[int(r() * k)]
        if u != v:
            out.append((u, v, wlo + int(r() * (whi - wlo + 1))))
    return out


def rand_shuttles(n, m, wmin, wmax, clo, chi, sources=None, lo=1, hi=None):
    """m shuttles, width (r - l + 1) in [wmin, wmax], ranges inside [lo, hi], from random sources"""
    r = random.random
    hi = n if hi is None else hi
    src = sources if sources is not None else range(1, n + 1)
    k = len(src)
    out = []
    for _ in range(m):
        wd = wmin + int(r() * (min(wmax, hi - lo + 1) - wmin + 1))
        l = lo + int(r() * (hi - lo + 2 - wd))
        out.append((src[int(r() * k)], l, l + wd - 1, clo + int(r() * (chi - clo + 1))))
    return out


# samples
add(6, [(1, 2, 4), (2, 6, 1)], [(1, 3, 5, 10), (2, 4, 6, 3)])
add(5, [(2, 3, 1)], [(1, 4, 5, 7), (2, 1, 5, 1)])
add(1, [], [])
add(4, [(1, 2, 5)], [(2, 1, 4, 9), (1, 3, 3, 2)])
add(7, [(1, 2, 3), (3, 4, 1)], [(2, 3, 7, 6), (1, 5, 6, 2), (6, 3, 3, 1)])
# hidden: small (brute checks these)
add(2, [], [(1, 2, 2, 5)])
add(3, [(2, 3, 7)], [(2, 1, 3, 1)])
add(50, rand_roads(50, 40, 1, 20), rand_shuttles(50, 30, 1, 50, 1, 50))
add(200, rand_roads(200, 300, 1, 10 ** 6), rand_shuttles(200, 100, 1, 20, 1, 10 ** 6))
add(300, rand_roads(300, 100, 1, 5), rand_shuttles(300, 300, 50, 300, 1, 5))
add(1000, [], rand_shuttles(1000, 2000, 1, 1000, 1, 100))
add(1000, rand_roads(1000, 3000, 1, 1000), [])
add(2000, rand_roads(2000, 1000, 1, 10, range(1, 1001)), rand_shuttles(2000, 2000, 1, 400, 1, 10 ** 6, hi=1500))
# hidden: big
N = MAXN


def hub(shuttles, wide=True):
    """make sure station 1 can leave: the first shuttles start at station 1"""
    for i in range(3):
        u, l, r, c = shuttles[i]
        shuttles[i] = (1, l, r, c)
    return shuttles


def falling(n, k, m, step, wlo=1, whi=1, extra=0, noise=0, by_shuttle=False):
    """chain 1 - 2 - ... - k (link costs in [wlo, whi]; roads, or one-station shuttles if by_shuttle);
    m shuttles from the chain stations to wide ranges of k+1..n, a station further along the chain has a
    cheaper shuttle (about step less per station): a new shuttle keeps improving the stations it covers.
    extra: random roads among k+1..n"""
    r = random.random
    link = [(i, i + 1, wlo + int(r() * (whi - wlo + 1))) for i in range(1, k)]
    roads = [] if by_shuttle else link
    sh = [(u, v, v, w) for u, v, w in link] if by_shuttle else []
    roads += rand_roads(n, extra, 1, MAXW, range(k + 1, n + 1)) if extra else []
    for j in range(m):
        u = 1 + j * (k - 1) // max(1, m - 1)
        wd = (n - k) // 2 + int(r() * ((n - k) // 2))
        l = k + 1 + int(r() * (n - k - wd + 1))
        sh.append((u, l, l + wd - 1, MAXW - step * u - int(r() * (noise + 1))))
    return roads, sh


add(N, rand_roads(N, 20000, 1, MAXW), hub(rand_shuttles(N, 80000, N // 2, N, 1, MAXW)))
add(N, rand_roads(N, 30000, 1, 1000), hub(rand_shuttles(N, 70000, N // 2, N, 10 ** 5, MAXW)))
add(N, rand_roads(N, 10000, 1, 10), hub(rand_shuttles(N, 90000, N - 100, N, 1, 10)))
add(N, [], hub(rand_shuttles(N, MAXM, 1, N, 1, MAXW)))
add(N, [], hub(rand_shuttles(N, MAXM, N // 3, N, 1, 1)))                 # every cost 1: many ties
add(N, [(i, i + 1, MAXW) for i in range(1, 50001)],                                           # long distances
    rand_shuttles(N, 50000, 1, 5, MAXW, MAXW, sources=range(1, 50002), lo=50002))
add(N, rand_roads(N, 50000, 1, MAXW), hub(rand_shuttles(N, 50000, 1, 50, 1, MAXW)))   # narrow shuttles
path = [(i, i + 1, 1 + int(random.random() * 10)) for i in range(1, 20001)]
add(N, path, rand_shuttles(N, 80000, N // 2, N, 1, MAXW, sources=range(1, 20002)))
add(N, *falling(N // 2, 3000, 90000, 10, 1, 2, extra=5000))      # stations above N / 2 are unreachable
add(N, rand_roads(N, 40000, 1, 100), hub(rand_shuttles(N, 60000, 10 ** 4, 3 * 10 ** 4, 100, 10 ** 4)))
add(N, rand_roads(N, 50000, 1, MAXW), hub(rand_shuttles(N, 50000, 1, N, 1, MAXW)))
add(N, *falling(N, 1000, 99000, 7))
add(N, *falling(N, 30000, 70000, 30))
add(N, *falling(N, 5000, 80000, 12, 1, 3, extra=15000, noise=20))
add(N, *falling(N, 2000, 98000, 300, 1, 100, by_shuttle=True))
add(N, *falling(N, 10000, 90000, 60, 5, 40, noise=500, by_shuttle=True))
add(N, *falling(N, 100, 59000, 9000, 1, 1000, extra=40000))
add(N, rand_roads(N, 50000, 1, MAXW), hub(rand_shuttles(N, 50000, N // 2, N, 1, 1000)))
P = 60000                                                         # a long road path, one useless shuttle
add(P, [(i, i + 1, 9 * 10 ** 5 + int(random.random() * 10 ** 5)) for i in range(1, P)], [(P, 1, P, MAXW)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
