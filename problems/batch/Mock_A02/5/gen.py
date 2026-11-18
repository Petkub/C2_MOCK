# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
import os, random

random.seed(23705)
rnd = random.random
MAXN, MAXM, MAXK, MAXH = 100000, 100000, 100, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = ri(0, i)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def add(k, h, edges, relabel=True):
    """h: heights of junctions 0..n-1, edges: pairs of 0-based junctions"""
    n, m = len(h), len(edges)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM and 1 <= k <= MAXK
    assert all(0 <= x <= MAXH for x in h)
    perm = shuffled(range(n)) if relabel else list(range(n))
    hh = [0] * n
    for i in range(n):
        hh[perm[i]] = h[i]
    seen = set()
    lines = []
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n and u != v
        key = (min(u, v), max(u, v))
        assert key not in seen
        seen.add(key)
        a, b = perm[u] + 1, perm[v] + 1
        if rnd() < 0.5:
            a, b = b, a
        lines.append(f"{a} {b}\n")
    if relabel:
        lines = shuffled(lines)
    tests.append(f"{n} {m} {k}\n" + " ".join(map(str, hh)) + "\n" + "".join(lines))


def tree_plus(n, m, wide=False):
    """a random spanning tree on 0..n-1 plus random extra edges, m edges in all"""
    es, seen = [], set()
    for v in range(1, n):
        u = ri(0, v - 1) if wide else ri(max(0, v - 5), v - 1)
        es.append((u, v))
        seen.add((u, v))
    while len(es) < m:
        u, v = ri(0, n - 1), ri(0, n - 1)
        if u == v:
            continue
        key = (min(u, v), max(u, v))
        if key in seen:
            continue
        seen.add(key)
        es.append(key)
    return es


def path(n):
    return [(i, i + 1) for i in range(n - 1)]


def rand_h(n, hi):
    return [ri(0, hi) for _ in range(n)]


def walls(n, hi, wall_every):
    """valleys separated by high walls; the floors get lower to the right"""
    h = []
    for i in range(n):
        if i % wall_every == wall_every - 1:
            h.append(ri(hi - hi // 10, hi))
        else:
            floor = (hi // 2) * (n - i) // n
            h.append(min(hi, floor + ri(0, hi // 3)))
    return h


def zigzag(n, hi, bump):
    """slowly going down with small bumps up: climbing a bump often pays"""
    h = []
    for i in range(n):
        base = hi - bump - (hi - 2 * bump) * i // n
        h.append(base + ri(0, bump))
    return h


def grid(r, c, hi):
    """a hilly r x c terrain: smooth waves plus noise; edges between side neighbours (keep m <= MAXM)"""
    # integer triangle waves (no floating point: big tests are rebuilt on students' machines and hash-checked)
    P = 1000
    waves = [(ri(1, 300), ri(1, 300), ri(0, 2 * P - 1)) for _ in range(4)]

    def tri(x):                     # period 2P, values 0..P
        x %= 2 * P
        return x if x <= P else 2 * P - x
    h, es = [], []
    for i in range(r):
        for j in range(c):
            s = sum(tri(a * i + b * j + p) for a, b, p in waves)   # 0..4P
            v = s * (hi * 9 // 10) // (4 * P) + ri(0, hi // 10)
            h.append(max(0, min(hi, v)))
            if j + 1 < c:
                es.append((i * c + j, i * c + j + 1))
            if i + 1 < r:
                es.append((i * c + j, (i + 1) * c + j))
    return h, es


# samples
tests.append("4 3 2\n5 7 0 3\n1 2\n2 3\n1 4\n")
tests.append("6 3 1\n4 9 2 2 6 5\n1 2\n2 3\n4 5\n")
tests.append("7 7 3\n2 11 4 14 10 16 18\n2 4\n1 3\n5 7\n1 7\n2 6\n3 4\n2 5\n")
tests.append("7 7 5\n2 9 17 10 8 0 11\n2 7\n2 3\n1 5\n5 6\n5 7\n2 4\n3 7\n")

# hidden: small (brute checks these)
add(7, [ri(0, MAXH)], [])
add(MAXK, [5, 5], [(0, 1)])
add(3, rand_h(6, 20), [])
add(4, [500, 100, MAXH, 0, 300, 1000, 0, 7, 7], path(9), relabel=False)
add(2, rand_h(30, MAXH), tree_plus(30, 60, True))
add(MAXK, walls(40, MAXH, 5), tree_plus(40, 45))
add(3, rand_h(12, 30), [(u, v) for u in range(12) for v in range(u + 1, 12)])
add(1, rand_h(35, MAXH), tree_plus(15, 20, True) + [(u + 15, v + 15) for u, v in tree_plus(20, 22)])
add(2, zigzag(40, 1000, 60), path(40))

# hidden: big
N, M = MAXN, MAXM
add(2, rand_h(N, MAXH), tree_plus(N, M, True))
add(MAXK, rand_h(N, MAXH), tree_plus(N, M, True))
add(1, rand_h(N, MAXH), tree_plus(N, M))
add(3, rand_h(N, 50), tree_plus(N, M, True))
add(57, [123456789] * N, tree_plus(N, M, True))
add(2, zigzag(N, MAXH, 3000000), path(N))
add(5, walls(N, MAXH, 7), tree_plus(N, M))
add(MAXK, walls(N, MAXH, 4), path(N))
h, es = grid(250, 200, MAXH)
add(3, h, es)
h, es = grid(250, 200, 10 ** 6)
add(2, h, es)
add(2, [MAXH] + rand_h(N - 1, MAXH), [(0, v) for v in range(1, N)])
add(4, [0] + rand_h(N - 1, MAXH), [(0, v) for v in range(1, N)])
add(2, [MAXH - 10000 - i * 7000 + ri(0, 9000) for i in range(N)], path(N), relabel=False)
add(10, rand_h(20000, MAXH), tree_plus(20000, M, True))
q = N // 4
add(6, rand_h(N, MAXH), [(u + c * q, v + c * q) for c in range(4) for u, v in tree_plus(q, M // 4)])
add(MAXK, zigzag(N, MAXH, 20000000), tree_plus(N, M))
add(3, [ri(0, 10 ** 8) if i % 2 else ri(9 * 10 ** 8, MAXH) for i in range(N)], tree_plus(N, M, True))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
