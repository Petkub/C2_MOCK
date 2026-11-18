# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
import os, random

random.seed(80611)
rnd = random.random
MAXN, MAXM, MAXW = 50000, 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = ri(0, i)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def add(n, s, lanes, relabel=True):
    """n points 0..n-1, start s, lanes (a, b, w) 0-based; points are renumbered and lanes shuffled"""
    m = len(lanes)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM and 0 <= s < n
    perm = shuffled(range(n)) if relabel else list(range(n))
    lines = []
    for a, b, w in lanes:
        assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= MAXW
        lines.append(f"{perm[a] + 1} {perm[b] + 1} {w}\n")
    if relabel:
        lines = shuffled(lines)
    tests.append(f"{n} {m} {perm[s] + 1}\n" + "".join(lines))


def rand_lanes(n, m, lo, hi):
    out = []
    while len(out) < m:
        a, b = ri(0, n - 1), ri(0, n - 1)
        if a != b:
            out.append((a, b, ri(lo, hi)))
    return out


def tree_plus(n, m, lo, hi, local=0):
    """lanes of a random tree directed away from point 0, plus random extra lanes (m lanes in all)"""
    out = []
    for v in range(1, n):
        u = ri(max(0, v - local), v - 1) if local else ri(0, v - 1)
        out.append((u, v, ri(lo, hi)))
    return out + rand_lanes(n, m - len(out), lo, hi)


def diamonds(hubs, k, lo, hi, extra, elo, ehi, grow=False):
    """a chain of hubs 0 -> 1 -> ...; between two hubs k two-lane branches of the SAME total length L
    (different longest lanes), plus `extra` random lanes (often long but with short single lanes)"""
    n = hubs + (hubs - 1) * k
    out = []
    nxt = hubs
    Ls = [ri(lo, hi) for _ in range(hubs - 1)]
    if grow:
        Ls.sort()
    for h in range(hubs - 1):
        L = Ls[h]
        for _ in range(k):
            x = ri(1, L - 1)
            out.append((h, nxt, x))
            out.append((nxt, h + 1, L - x))
            nxt += 1
    out += rand_lanes(n, extra, elo, ehi)
    return n, out


def layers(width, depth, extra, spread):
    """layered graph: every lane goes from layer i to layer i + 1 with length C_i + r (0 <= r <= spread),
    so all routes to a layer use the same number of lanes and equal lengths are frequent"""
    n = 1 + width * depth
    out = []
    cs = sorted(ri(spread + 1, MAXW - spread) for _ in range(depth))

    def pt(i, j):
        return 0 if i == 0 else 1 + (i - 1) * width + j
    for i in range(depth):
        cur = 1 if i == 0 else width
        for j in range(width):
            for _ in range(2):
                a = pt(i, ri(0, cur - 1)) if i else 0
                out.append((a, pt(i + 1, j), cs[i] + ri(0, spread)))
    out += rand_lanes(n, extra, 1, MAXW)
    return n, out


def traps(n, m):
    """a tree of medium lanes away from 0 plus many light lanes pointing back toward 0:
    used in the wrong direction they would lower the longest lane"""
    out = []
    par = [0] * n
    for v in range(1, n):
        par[v] = ri(max(0, v - 3), v - 1)
        out.append((par[v], v, ri(10 ** 6, 10 ** 9)))
    while len(out) < m:
        v = ri(1, n - 1)
        u = v
        for _ in range(ri(1, 4)):
            u = par[u]
        if rnd() < 0.8:
            out.append((v, u, ri(1, 10 ** 6)))          # backward, light
        else:
            a, b = ri(0, n - 1), ri(0, n - 1)
            if a != b:
                out.append((a, b, ri(1, MAXW)))
    return out


def with_cloud(n, lanes, k, m, lo, hi):
    """append k points reached from point 0 only through m light lanes (a random tree plus extras)"""
    out = list(lanes)
    for v in range(1, k + 1):
        u = 0 if v == 1 else n + ri(0, v - 2)
        out.append((u, n + v - 1, ri(lo, hi)))
    while len(out) < len(lanes) + m:
        a, b = n + ri(0, k - 1), n + ri(0, k - 1)
        if a != b:
            out.append((a, b, ri(lo, hi)))
    return n + k, out


def ladder(n):
    """a chain 0 -> 1 -> ... of slowly growing light lanes plus a direct long lane 0 -> v for every v:
    the direct lane is shorter than the chain but its length is above the chain's longest lane"""
    out = []
    pre = 0
    for v in range(1, n):
        c = 5000 + v
        out.append((v - 1, v, c))
        pre += c
        if v >= 2:
            out.append((0, v, ri(c + 1, min(pre - 1, MAXW))))
    return out


# samples
tests.append("6 8 1\n1 2 5\n2 3 1\n1 4 3\n4 3 4\n3 2 2\n5 1 2\n4 6 2\n3 6 1\n")
tests.append("6 8 1\n1 2 6\n2 4 4\n1 3 7\n3 4 3\n3 5 2\n4 5 1\n1 6 2\n6 3 6\n")
tests.append("4 3 3\n1 3 2\n2 3 7\n4 1 1\n")
tests.append("6 8 2\n5 1 636939143\n1 4 908538600\n6 4 923442626\n2 1 761916048\n1 4 732340048\n"
             "5 1 873572427\n4 3 887373855\n2 5 554882787\n")

# hidden: small (brute checks these)
add(1, 0, [])
add(2, 0, [(1, 0, 5)])
add(8, 3, rand_lanes(8, 14, 1, 5))
add(10, 0, rand_lanes(10, 20, 1, 3))
n, ls = diamonds(8, 3, 4, 30, 6, 1, 40)
add(n, 0, ls)
add(200, 0, tree_plus(200, 400, 1, MAXW))
n, ls = layers(6, 40, 30, 3)
add(n, 0, ls)
add(300, 0, [(i, i + 1, MAXW) for i in range(299)], relabel=False)
add(300, 0, traps(300, 700))
add(150, 0, ladder(150))

# hidden: big
N, M = MAXN, MAXM
add(N, 0, tree_plus(N, M, 1, MAXW))
add(N, 0, tree_plus(N, M, 1, MAXW, local=20))
add(N, ri(0, N - 1), rand_lanes(N, M, 1, MAXW))
add(N, 0, tree_plus(N, M, 1, 200000))
n, ls = diamonds(10000, 4, 2, 2 * 10 ** 5, M - 9999 * 8, 1, MAXW, grow=True)
add(n, 0, ls)
n, ls = diamonds(12500, 3, 2, MAXW // 2, M - 12499 * 6, 1, MAXW)
add(n, 0, ls)
n, ls = diamonds(16667, 2, 2, 10 ** 6, M - 16666 * 4, 10 ** 5, 10 ** 7)
add(n, 0, ls)
n, ls = layers(5, 9999, 0, 2)
add(n, 0, ls)
n, ls = layers(10, 4999, 0, 1)
add(n, 0, ls)
n, ls = layers(4, 12000, M - 4 * 12000 * 2, 4)
add(n, 0, ls)
add(N, 0, traps(N, M))
n, ls = with_cloud(N // 2, traps(N // 2, M // 2), N // 2, M // 2, 1, 1000)
add(n, 0, ls)
add(N, 0, ladder(N))
add(N, 0, [(i, i + 1, MAXW - (N - 1 - i)) for i in range(N - 1)] + [(0, i, MAXW) for i in range(2, N)])
add(N, 0, [(0, v, ri(1, MAXW)) for v in range(1, N)] + rand_lanes(N, M - (N - 1), 1, MAXW))
n, ls = diamonds(8334, 5, 2, MAXW, M - 8333 * 10, 1, MAXW)
add(n, 0, ls)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
