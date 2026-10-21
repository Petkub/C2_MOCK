# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1105)
MAXN, MAXM, MAXD = 100000, 100000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        a[i], a[j] = a[j], a[i]


def add(d, edges):
    n, m = len(d), len(edges)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM
    assert 1 <= min(d) and max(d) <= MAXD
    if edges:
        us, vs = zip(*edges)
        assert 1 <= min(us) and max(us) <= n and 1 <= min(vs) and max(vs) <= n
        assert all(map(int.__ne__, us, vs))
    lines = [f"{n} {m}", " ".join(map(str, d))] + [f"{u} {v}" for u, v in edges]
    tests.append("\n".join(lines) + "\n")


def emit(d, edges):
    """steps 0..n-1 are in a topological order while building (every edge goes from a smaller to a larger
    number); relabel them at random and shuffle the rules"""
    n = len(d)
    assert all(u < v for u, v in edges)
    lab = list(range(1, n + 1))
    shuffle(lab)
    dd = [0] * n
    for v in range(n):
        dd[lab[v] - 1] = d[v]
    out = [(lab[u], lab[v]) for u, v in edges]
    shuffle(out)
    add(dd, out)


def backbone(L, nby, maxk, jumps, dlo=MAXD // 2, direct=0.2, side=0):
    """a chain of L heavy steps is the unique longest chain; bypasses leave the chain at step i and come back
    at step j through k new steps (k = 0: a direct rule) whose total is a little less than the skipped part;
    side = light steps hanging off the chain; jumps = extra rules from a chain or side step to a later chain
    step (they skip at least one chain step, so they are shorter too). Stops adding when N or M is full."""
    d = [ri(dlo, MAXD) for _ in range(L)]
    pre = [0]
    for x in d:
        pre.append(pre[-1] + x)
    n_used, m_used = L, L - 1
    keyed = [(float(i), 0, i) for i in range(L)]
    bstep, byp = [], []
    for _ in range(nby):
        i = ri(0, L - 3)
        j = min(L - 1, i + 2 + int(rnd() ** 3 * ri(1, max(1, L // 3))))
        skipped = pre[j] - pre[i + 1]
        k = 0 if rnd() < direct else ri(1, maxk)
        total = skipped - ri(1, max(1, min(skipped - k, MAXD // 10)))
        if k > total:
            k = 0
        if n_used + k > MAXN or m_used + k + 1 > MAXM - side:
            break
        n_used += k
        m_used += k + 1
        ids = []
        rest = total - k
        for t in range(k):          # split the bypass total at random (each part 1..MAXD)
            take = rest if t == k - 1 else int(rest * rnd() * 2 / k)
            take = min(take, rest, MAXD - 1)
            rest -= take
            ids.append(len(bstep))
            bstep.append(1 + take)
            keyed.append((i + (j - i) * (t + 1) / (k + 1) + rnd() * 1e-6, 1, len(bstep) - 1))
        byp.append((i, j, ids))
    sides = []
    for _ in range(min(side, MAXN - n_used, MAXM - m_used)):
        i = ri(0, L - 1)
        sides.append((i, ri(1, max(1, dlo // 4))))
        keyed.append((i + 0.5 + rnd() * 0.4, 2, len(sides) - 1))
    m_used += len(sides)
    keyed.sort()
    num = {}
    for idx, (_, kind, x) in enumerate(keyed):
        num[(kind, x)] = idx
    n = len(keyed)
    dur = [0] * n
    for i in range(L):
        dur[num[(0, i)]] = d[i]
    for x in range(len(bstep)):
        dur[num[(1, x)]] = bstep[x]
    for x, (i, w) in enumerate(sides):
        dur[num[(2, x)]] = w
    edges = [(num[(0, i)], num[(0, i + 1)]) for i in range(L - 1)]
    for i, j, ids in byp:
        path = [num[(0, i)]] + [num[(1, x)] for x in ids] + [num[(0, j)]]
        edges += list(zip(path, path[1:]))
    for x, (i, w) in enumerate(sides):
        edges.append((num[(0, i)], num[(2, x)]))
    for _ in range(min(jumps, MAXM - len(edges))):
        if sides and rnd() < 0.5:
            x = int(rnd() * len(sides))
            i = sides[x][0]
            if i + 1 >= L:
                continue
            u = num[(2, x)]
            t = min(L - 1, i + 1 + int(rnd() ** 2 * 30))
        else:
            i = ri(0, L - 3)
            u = num[(0, i)]
            t = min(L - 1, i + 2 + int(rnd() ** 2 * 30))
        edges.append((u, num[(0, t)]))
    emit(dur, edges)


def random_dag(n, m, span, dk="rand"):
    """random forward edges between nearby positions (long chains)"""
    if dk == "rand":
        d = [ri(1, MAXD) for _ in range(n)]
    elif dk == "eq":
        d = [MAXD] * n
    else:
        d = [ri(1, 3) for _ in range(n)]
    edges = []
    while len(edges) < m:
        u = ri(0, n - 2)
        v = min(n - 1, u + 1 + int(rnd() ** 2 * span))
        edges.append((u, v))
    emit(d, edges)


def layered(n, width, m, dk="rand"):
    layers = [list(range(s, min(n, s + width))) for s in range(0, n, width)]
    d = [ri(1, MAXD) if dk == "rand" else ri(MAXD - 10, MAXD) for _ in range(n)]
    edges = []
    for a, b in zip(layers, layers[1:]):
        for v in b:                          # everyone has a predecessor in the previous layer
            edges.append((a[int(rnd() * len(a))], v))
    while len(edges) < m:
        t = ri(0, len(layers) - 2)
        jump = 1 if rnd() < 0.8 else ri(1, min(20, len(layers) - 1 - t))
        a, b = layers[t], layers[t + jump]
        edges.append((a[int(rnd() * len(a))], b[int(rnd() * len(b))]))
    emit(d, edges)


def braid(n, k, m, dk="rand"):
    """k parallel chains (step i is on chain i mod k) with forward rules between nearby levels"""
    d = [ri(1, MAXD) if dk == "rand" else ri(MAXD - 1000, MAXD) for _ in range(n)]
    edges = [(i, i + k) for i in range(n - k)]
    while len(edges) < m:
        u = ri(0, n - k - 1)
        v = min(n - 1, (u // k + ri(1, 3)) * k + ri(0, k - 1))
        if v > u:
            edges.append((u, v))
    emit(d, edges)


def chain(n, dk="max"):
    d = [MAXD] * n if dk == "max" else [ri(1, MAXD) for _ in range(n)]
    emit(d, [(i, i + 1) for i in range(n - 1)])


# samples
add([3, 2, 4, 1, 5], [(1, 2), (2, 4), (1, 3), (3, 4), (4, 5)])
add([5, 1, 3, 4], [(1, 2), (3, 4)])
add([7], [])
add([2, 2, 2, 2], [(1, 2), (2, 3), (3, 4), (1, 4)])
add([4, 1, 6, 2, 3, 5], [(1, 2), (2, 3), (1, 4), (4, 5), (5, 3), (2, 6), (4, 6)])
# hidden: small (brute checks these)
add([MAXD], [])
add([MAXD, MAXD], [(2, 1)])
backbone(12, 6, 3, 10)
backbone(300, 60, 6, 300, side=100)
random_dag(800, 1600, 30)
layered(900, 3, 1500)
random_dag(1200, 1200, 5, "small")
backbone(600, 200, 3, 400, dlo=1, direct=0.5)
chain(1000, "rand")
# hidden: big
backbone(50000, 4000, 8, MAXM)
backbone(60000, 12000, 3, MAXM, direct=0.6)
backbone(40000, 1500, 20, MAXM, side=20000)
backbone(70000, 20000, 1, MAXM, direct=0.3)
backbone(30000, 800, 60, MAXM, dlo=MAXD - 1000)
backbone(80000, 8000, 1, MAXM, direct=0.9, side=5000)
chain(MAXN)
chain(MAXN, "rand")
layered(MAXN, 2, MAXM)
layered(MAXN, 5, MAXM, "near")
random_dag(MAXN, MAXM, 40)
random_dag(MAXN, MAXM, 3, "eq")
random_dag(MAXN, MAXM, 200, "small")
braid(MAXN, 3, MAXM)
braid(MAXN, 8, MAXM, "near")
backbone(90000, 10000, 0, MAXM, direct=1.0)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
