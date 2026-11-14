# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1304)
MAXN, MAXQ = 100_000, 100_000
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(p, qs):
    """p = [p_2, ..., p_N]"""
    n = len(p) + 1
    assert 2 <= n <= MAXN and 1 <= len(qs) <= MAXQ
    for i, x in enumerate(p, 2):
        assert 1 <= x < i
    for u, v in qs:
        assert 1 <= u <= n and 1 <= v <= n
    lines = [str(n), " ".join(map(str, p)), str(len(qs))] + [f"{u} {v}" for u, v in qs]
    tests.append("\n".join(lines) + "\n")


# trees (p_2 .. p_N)
def path(n):
    return [i - 1 for i in range(2, n + 1)]


def near(n, k):
    """p_i among the k previous towns: deep, a little branched"""
    return [max(1, i - ri(1, k)) for i in range(2, n + 1)]


def uniform(n):
    return [ri(1, i - 1) for i in range(2, n + 1)]


def chains(n, k):
    """k long chains hanging from town 1 (town i continues chain i mod k)"""
    return [1 if i <= k + 1 else i - k for i in range(2, n + 1)]


def caterpillar(n, spine):
    return [i - 1 if i <= spine else ri(1, spine) for i in range(2, n + 1)]


def broom(n, handle):
    return [i - 1 if i <= handle else handle for i in range(2, n + 1)]


def heap(n):
    return [i // 2 for i in range(2, n + 1)]


def relabel(p):
    """random numbering that still gives every town a parent with a smaller number (a random topological order)"""
    n = len(p) + 1
    children = [[] for _ in range(n + 1)]
    for i, x in enumerate(p, 2):
        children[x].append(i)
    new = [0] * (n + 1)
    avail = [1]
    k = 0
    while avail:
        j = ri(0, len(avail) - 1) if rnd() < 0.5 else len(avail) - 1
        avail[j], avail[-1] = avail[-1], avail[j]
        v = avail.pop()
        k += 1
        new[v] = k
        avail.extend(children[v])
    q = [0] * (n + 1)
    for i, x in enumerate(p, 2):
        q[new[i]] = new[x]
    return q[2:]


# queries
def rand_q(n, q):
    return [(ri(1, n), ri(1, n)) for _ in range(q)]


def far_q(n, q, w):
    """one end among the first w towns, the other among the last w (long routes in deep trees)"""
    out = []
    for _ in range(q):
        a, b = ri(1, w), ri(n - w + 1, n)
        out.append((a, b) if rnd() < 0.5 else (b, a))
    return out


def deep_q(n, q, w):
    """both ends among the last w towns"""
    return [(ri(n - w + 1, n), ri(n - w + 1, n)) for _ in range(q)]


def mix(*parts):
    out = [x for part in parts for x in part]
    random.shuffle(out)
    return out


def spare(p, qs, k=3):
    """pick k leaves and never end a route there (their roads stay unrepaired to the end)"""
    n = len(p) + 1
    has_child = [False] * (n + 1)
    for x in p:
        has_child[x] = True
    leaves = [v for v in range(2, n + 1) if not has_child[v]]
    keep = set(random.sample(leaves, min(k, len(leaves))))
    par = lambda v: p[v - 2] if v in keep else v
    return p, [(par(u), par(v)) for u, v in qs]


# samples
add([1, 1, 2, 2, 3, 6], [(4, 5), (6, 4), (1, 5)])
add([1, 1, 1, 1], [(2, 3), (4, 2), (1, 4)])
add([1], [(1, 2)])
add([1, 2, 1, 3, 3, 4, 6], [(5, 8), (7, 2), (6, 1), (8, 6)])
add([1, 1, 2, 3, 3, 2, 7, 5], [(9, 4), (6, 6), (8, 1), (2, 3), (9, 4)])

# hidden: small (brute checks these)
add([1], [(2, 2), (1, 1)])
add(path(30), [(30, 1), (1, 30), (5, 9)])
add(path(40), mix(rand_q(40, 25), [(i, i) for i in range(1, 6)]))
add(uniform(60), rand_q(60, 40))
add(near(80, 3), rand_q(80, 30))
add(relabel(chains(70, 3)), rand_q(70, 50))
add(relabel(caterpillar(100, 40)), rand_q(100, 20))
add(relabel(near(300, 4)), rand_q(300, 300))
add(broom(500, 250), mix(far_q(500, 100, 20), rand_q(500, 50)))
add(relabel(uniform(2000)), rand_q(2000, 2000))

# hidden: big
N, Q = MAXN, MAXQ
BIG = [
    (13041, lambda: (path(N), far_q(N, Q, 1000))),
    (13042, lambda: (path(N), [(1, N)] * (Q // 2) + [(N, 1)] * (Q // 2))),
    (13043, lambda: (path(N), mix(rand_q(N, Q // 2), deep_q(N, Q // 2, 5000)))),
    (13044, lambda: (path(N), [(ri(1, 100), N - ri(0, 99)) if i % 1000 == 0 else (ri(N // 2, N), ri(N // 2, N))
                                for i in range(Q)])),
    (13045, lambda: (near(N, 3), far_q(N, Q, 3000))),
    (13046, lambda: (near(N, 10), mix(rand_q(N, Q // 2), deep_q(N, Q // 2, 20000)))),
    (13047, lambda: (relabel(near(N, 2)), rand_q(N, Q))),
    (13048, lambda: (chains(N, 2), far_q(N, Q, 2000))),
    (13049, lambda: (chains(N, 5), deep_q(N, Q, 1000))),
    (13050, lambda: (relabel(chains(N, 3)), rand_q(N, Q))),
    (13051, lambda: (caterpillar(N, N // 2), deep_q(N, Q, N // 2))),
    (13052, lambda: (relabel(caterpillar(N, 75_000)), rand_q(N, Q))),
    (13053, lambda: (broom(N, 75_000), mix(far_q(N, Q // 2, 1000), deep_q(N, Q // 2, 25_000)))),
    (13054, lambda: (broom(N, 50_000), mix(far_q(N, Q // 2, 1000), [(ri(1, 1000), ri(1, 1000)) for _ in range(Q // 2)]))),
    (13055, lambda: (uniform(N), rand_q(N, Q))),
    (13056, lambda: (heap(N), rand_q(N, Q))),
    (13057, lambda: (path(N), [(i, i) for i in range(1, Q)] + [(N, N - 1)])),       # a single road repaired
    (13058, lambda: (near(N, 2), [(N - ri(0, 100), N - ri(0, 100)) for _ in range(Q)])),   # few roads repaired
    (13059, lambda: (path(N), [(ri(1, 10), N - ri(0, 9)) for _ in range(Q)])),
]
for seed, make in BIG:
    random.seed(seed)
    p, qs = make()
    if seed not in (13057, 13058):
        p, qs = spare(p, qs)
    add(p, qs)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
