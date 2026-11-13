# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A graph is three lists (A, B, C): road i joins A[i] and B[i] with score C[i]. Big graphs are built on internal
# ids 0..V-1 with the start at id 0, then relabelled at random (id 0 becomes point 1); the roads are shuffled (mix)
# or the list starts at a random place, and every other road is written in the other direction.
import os, random

random.seed(72014)
rnd = random.random
MAXV, MAXE, MAXC = 50000, 100000, 100000
V, E = MAXV, MAXE
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def rl(n, a, b):
    """n random integers in [a, b]"""
    w = b - a + 1
    return [a + int(rnd() * w) for _ in range(n)]


def shuffled(a):
    keys = [rnd() for _ in a]
    return [a[i] for i in sorted(range(len(a)), key=keys.__getitem__)]


PERM_V = shuffled(list(range(1, MAXV)))    # one random order of destinations, reused by every big test
LAB = [1] + shuffled(list(range(2, MAXV + 1)))   # one random relabelling, reused by every big test
PERM_E = shuffled(list(range(MAXE)))       # one random order of roads


def write(v, A, B, C, qs):
    lines = ["%d %d %d" % (v, len(A), len(qs))]
    lines += map("%d %d %d".__mod__, zip(A, B, C))
    lines += map(str, qs)
    tests.append("\n".join(lines) + "\n")


def check(v, A, B, C, qs):
    assert 2 <= v <= MAXV and v - 1 <= len(A) <= MAXE and len(A) == len(B) == len(C)
    assert min(A) >= 1 and min(B) >= 1 and max(A) <= v and max(B) <= v
    assert min(C) >= 0 and max(C) <= MAXC
    assert all(map(int.__ne__, A, B))
    assert 1 <= len(qs) <= v - 1 and min(qs) >= 2 and max(qs) <= v


def add_raw(v, roads, qs):
    """small tests written by hand, labels 1..V"""
    A, B, C = map(list, zip(*roads))
    check(v, A, B, C, qs)
    p = list(range(v + 1))
    for a, b in zip(A, B):
        while p[a] != a:
            a = p[a]
        while p[b] != b:
            b = p[b]
        p[a] = b
    assert len({x for x in range(1, v + 1) if p[x] == x}) == 1   # connected
    write(v, A, B, C, qs)


def add(v, g, qs=None, mix=False):
    """g = (A, B, C) on internal ids, start = 0; qs = internal ids (default: every other point once, shuffled)"""
    A, B, C = g
    # every id x >= 1 has a road to a smaller id, so every point is linked to the start
    assert set(map(max, A, B)) >= set(range(1, v))
    lab = LAB if v == MAXV else [1] + shuffled(list(range(2, v + 1)))
    if mix:                                # roads in a random order
        assert len(A) == MAXE
        A, B, C = (list(map(x.__getitem__, PERM_E)) for x in (A, B, C))
    else:                                  # start the list of roads at a random place
        s = ri(0, len(A) - 1)
        A, B, C = A[s:] + A[:s], B[s:] + B[:s], C[s:] + C[:s]
    A = list(map(lab.__getitem__, A))
    B = list(map(lab.__getitem__, B))
    A[::2], B[::2] = B[::2], A[::2]
    if qs is None:
        qs = [x for x in PERM_V if x < v]
    qs = list(map(lab.__getitem__, qs))
    check(v, A, B, C, qs)
    write(v, A, B, C, qs)


def join(*gs):
    return tuple(sum((list(g[k]) for g in gs), []) for k in range(3))


def tree(v, reach, cl, ch):
    """the parent of id i is one of the `reach` ids before it; scores in [cl, ch]"""
    return ([i - 1 - int(rnd() * (i if i < reach else reach)) for i in range(1, v)], list(range(1, v)),
            rl(v - 1, cl, ch))


def extra(v, k, cl, ch, base=0):
    """k random roads among ids base..base+v-1, scores in [cl, ch]"""
    A = [int(rnd() * v) for _ in range(k)]
    B = [int(rnd() * v) for _ in range(k)]
    for i in range(k):
        if A[i] == B[i]:
            B[i] = (A[i] + 1 + int(rnd() * (v - 1))) % v
    if base:
        A = [a + base for a in A]
        B = [b + base for b in B]
    return A, B, rl(k, cl, ch)


def graph(v, e, reach, cl, ch):
    return join(tree(v, reach, cl, ch), extra(v, e - v + 1, cl, ch))


# samples
add_raw(4, [(1, 2, 7), (1, 3, 4), (2, 3, 9), (2, 4, 3), (3, 4, 8)], [4, 3])
add_raw(4, [(1, 2, 5), (2, 3, 2), (1, 4, 3), (4, 3, 6), (2, 4, 1)], [3, 2])
add_raw(4, [(1, 2, 4), (2, 3, 10), (3, 1, 6), (3, 4, 0)], [4, 2])
add_raw(3, [(2, 1, 40), (3, 2, 70), (1, 3, 50), (2, 3, 45)], [2, 3])
add_raw(5, [(1, 2, 1), (1, 3, 8), (3, 4, 6), (2, 4, 9), (4, 5, 5)], [5, 2])

# hidden: small (brute checks these)
add_raw(2, [(2, 1, 0)], [2])
add_raw(2, [(1, 2, 31), (2, 1, 87), (1, 2, 87), (2, 1, 5)], [2])                 # parallel roads
n = 100
add(n, (list(range(n)), [(i + 1) % n for i in range(n)], rl(n, 0, 1000)), rl(50, 1, n - 1))   # one cycle
add(500, graph(500, 4000, 500, 0, 20), rl(100, 1, 499))
add(2000, graph(2000, 8000, 30, 0, MAXC))
add(3000, tree(3000, 3000, 0, MAXC))                                              # a tree
add(1000, graph(1000, 5000, 1000, 0, 0))                                          # every score 0
add(1500, graph(1500, 1500, 5, 0, MAXC))                                          # long and thin

# hidden: big
add(V, graph(V, E, V, 0, MAXC), mix=True)
add(V, graph(V, E, 50, 0, MAXC))
add(V, graph(V, E, V, 0, 10))                                                     # many equal scores
# a long path of good roads (the answer drops slowly along it) plus many poor shortcuts
path = (list(range(V - 1)), list(range(1, V)), [MAXC - i // 3 for i in range(1, V)])
add(V, join(path, extra(V, E - V + 1, 0, 30000)))
# a path of good roads with the start in the middle (ids fall towards the start)
order = list(range(V - 1, 0, -2)) + list(range(0, V, 2))
path = (order[:-1], order[1:], rl(V - 1, 50000, MAXC))
add(V, join(path, extra(V, E - V + 1, 0, 49999)))
# grid 200 x 250, random scores; then scores that grow away from the start in a corner
R, C = 200, 250
GA = [r * C + c for r in range(R) for c in range(C - 1)] + list(range(V - C))
GB = [r * C + c + 1 for r in range(R) for c in range(C - 1)] + list(range(C, V))
add(V, (GA, GB, rl(len(GA), 0, MAXC)))
add(V, (GA, GB, [min(MAXC, (a // C + a % C) * 200 + int(rnd() * 3001)) for a in GA]))
# a star of poor roads from the start + good roads among the others
add(V, join(([0] * (V - 1), list(range(1, V)), rl(V - 1, 0, 1000)), extra(V, E - V + 1, 1001, MAXC)))
# two random halves joined by a few poor roads
h = V // 2
t1, t2 = tree(h, h, 0, MAXC), tree(V - h, V - h, 0, MAXC)
t2 = ([a + h for a in t2[0]], [b + h for b in t2[1]], t2[2])
cross = ([ri(0, h - 1) for _ in range(5)], [h] + rl(4, h, V - 1), rl(5, 0, 20000))
rest = E - (V - 2) - 5
add(V, join(t1, t2, cross, extra(h, rest // 2, 0, MAXC), extra(V - h, rest - rest // 2, 0, MAXC, h)))
# many parallel roads: every tree road three times
t = tree(V, 200, 0, MAXC)
add(V, join(t, (t[0], t[1], rl(V - 1, 0, MAXC)), (t[0][:E - 2 * (V - 1)], t[1][:E - 2 * (V - 1)], rl(E - 2 * (V - 1), 0, MAXC))))
# repeated destinations
add(V, graph(V, E, 1000, 0, MAXC), rl(V - 1, 1, V - 1))
# a caterpillar: a spine of good roads, leaves hanging on it, poor shortcuts
sp = V // 5
spine = (list(range(sp - 1)), list(range(1, sp)), rl(sp - 1, 60000, MAXC))
leaves = (rl(V - sp, 0, sp - 1), list(range(sp, V)), rl(V - sp, 0, MAXC))
add(V, join(spine, leaves, extra(V, E - V + 1, 0, 59999)))
# improvements reach one gate later and later: a chain of excellent roads from the start, each chain point
# has a road to the gate whose score grows along the chain; behind the gate is a long line of excellent roads
K = V // 2
chain = (list(range(K)), list(range(1, K + 1)), [MAXC] * K)                  # ids 0..K
gate = (list(range(1, K + 1)), [K + 1] * K, list(range(1, K + 1)))          # chain point i -> gate K+1, score i
line = (list(range(K + 1, V - 1)), list(range(K + 2, V)), [MAXC] * (V - K - 2))
g = join(chain, gate, line)
add(V, join(g, extra(V, E - len(g[0]), 0, 0)), mix=True)
# the same with a random tree of good roads behind the gate
gate = (list(range(1, K + 1)), [K + 1] * K, [2 * i for i in range(1, K + 1)])
behind = tree(V - K - 1, V, MAXC - 100, MAXC)
behind = ([a + K + 1 for a in behind[0]], [b + K + 1 for b in behind[1]], behind[2])
g = join(chain, gate, behind)
add(V, join(g, extra(V, E - len(g[0]), 0, 1)), mix=True)
# a shorter chain to the gate and a random graph of good roads behind it
K = V // 3
chain = (list(range(K)), list(range(1, K + 1)), [MAXC] * K)
gate = (list(range(1, K + 1)), [K + 1] * K, [3 * i + ri(0, 2) for i in range(1, K + 1)])
behind = tree(V - K - 1, V, 90000, MAXC)
behind = ([a + K + 1 for a in behind[0]], [b + K + 1 for b in behind[1]], behind[2])
g = join(chain, gate, behind)
add(V, join(g, extra(V - K - 1, E - len(g[0]), 90000, MAXC, K + 1)), mix=True)
# a deep random tree of good roads plus poor shortcuts
add(V, join(tree(V, 3, 50000, MAXC), extra(V, E - V + 1, 0, 49999)))

assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
