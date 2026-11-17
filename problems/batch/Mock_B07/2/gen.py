# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
# The route must pass a checkpoint before it ends at city 1, so the big tests put the checkpoints away from
# the cheap ways into city 1, make the start city a checkpoint in many queries, make the cheapest route
# without coupons differ from the best route with coupons, and use long chains of 10^9 tolls (answers above 2^31).
# Every big test has Q = 50 000 queries from many different start cities.
import os, random

random.seed(2207)
rnd = random.random
MAXN, MAXM, MAXQ, MAXC, MAXP = 5000, 10000, 50000, 10 ** 9, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def toll(lo, hi):
    """a random multiple of 10 in [lo, hi]"""
    return 10 * ri(max(1, lo // 10), hi // 10)


def add(n, roads, chk, qs):
    m, k, q = len(roads), len(chk), len(qs)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM and 1 <= k <= n and 1 <= q <= MAXQ
    assert len(set(chk)) == k and all(1 <= t <= n for t in chk)
    for u, v, c in roads:
        assert 1 <= u <= n and 1 <= v <= n and u != v and 10 <= c <= MAXC and c % 10 == 0
    for s, *p in qs:
        assert 1 <= s <= n and len(p) == 5 and all(x == -1 or 0 <= x <= MAXP for x in p)
    lines = [f"{n} {m} {k}", " ".join(map(str, chk))]
    lines += [f"{u} {v} {c}" for u, v, c in roads]
    lines.append(str(q))
    lines += [" ".join(map(str, x)) for x in qs]
    t = "\n".join(lines) + "\n"
    assert len(t) <= 3 * 10 ** 6
    tests.append(t)


def relabel(n, roads, chk, keep1=True):
    """shuffle the city numbers 2..n (city 1 stays the capital)"""
    perm = list(range(2, n + 1))
    random.shuffle(perm)
    mp = {1: 1}
    for i, x in enumerate(perm):
        mp[i + 2] = x
    roads = [(mp[u], mp[v], c) for u, v, c in roads]
    random.shuffle(roads)
    return roads, sorted(mp[t] for t in chk), mp


def price(kind):
    """one coupon price: kind 'mix' / 'cheap' / 'dear' / 'none' / 'zero'"""
    if kind == "none":
        return -1
    if kind == "zero":
        return 0 if rnd() < 0.8 else -1
    if rnd() < 0.25:
        return -1
    if kind == "cheap":
        return ri(0, 1000)
    if kind == "dear":
        return ri(10 ** 8, MAXP)
    r = rnd()
    if r < 0.4:
        return ri(0, 10 ** 4)
    if r < 0.8:
        return ri(10 ** 4, 10 ** 7)
    return ri(10 ** 7, MAXP)


def queries(n, q, kind="mix", starts=None, scale=1):
    qs = []
    for _ in range(q):
        s = starts[int(rnd() * len(starts))] if starts else ri(1, n)
        p = [price(kind) for _ in range(5)]
        if scale != 1:
            p = [x if x <= 0 else min(MAXP, x * scale) for x in p]
        qs.append([s] + p)
    return qs


def rand_graph(n, m, lo, hi):
    roads = []
    for _ in range(m):
        u = ri(1, n)
        v = ri(1, n - 1)
        if v >= u:
            v += 1
        roads.append((u, v, toll(lo, hi)))
    return roads


def two_ways(n, m, k, lo=10, hi=MAXC, q=MAXQ, kind="mix"):
    """a random graph where the cities near city 1 have cheap roads into it, and the k checkpoints are
    far from city 1: the cheapest raw route never passes a checkpoint"""
    roads = rand_graph(n, m - n // 2, lo, hi)
    for v in range(2, n // 2 + 2):
        roads.append((v, 1, toll(lo, lo * 20)))
    chk = random.sample(range(n // 2 + 2, n + 1), k)
    roads, chk, _ = relabel(n, roads, chk)
    add(n, roads, chk, queries(n, q, kind))


def chain(n, extra, k_far, hi_toll, q=MAXQ, kind="mix", back=True, cap_chk=False):
    """cities 1..n on a line, roads i -> i - 1 into the capital and (back) i -> i + 1 away from it;
    the checkpoints are the far end, so most routes walk out and come back. extra random roads on top."""
    roads = []
    for i in range(2, n + 1):
        roads.append((i, i - 1, toll(hi_toll // 2, hi_toll)))
    if back:
        for i in range(1, n):
            roads.append((i, i + 1, toll(hi_toll // 2, hi_toll)))
    for _ in range(extra):
        u = ri(1, n)
        v = min(n, u + ri(1, 50))
        if u != v:
            roads.append((u, v, toll(hi_toll // 2, hi_toll)))
    chk = list(range(n - k_far + 1, n + 1))
    if cap_chk:
        chk.append(1)
    roads, chk, mp = relabel(n, roads, chk)
    add(n, roads, chk, queries(n, q, kind))


def greedy_trap(n, q=MAXQ, kind="cheap"):
    """from every start two families of routes to a checkpoint and on to city 1: many medium roads (cheapest
    without coupons) or few huge roads (cheapest once coupons cut them in half)"""
    roads = []
    hub_a = list(range(2, 2 + n // 4))           # many-road side
    hub_b = list(range(2 + n // 4, 2 + n // 2))  # few-road side
    rest = list(range(2 + n // 2, n + 1))
    chk = random.sample(rest, max(1, len(rest) // 50))
    for v in rest:
        a = random.choice(hub_a)
        b = random.choice(hub_b)
        roads.append((v, a, 3000))
        roads.append((v, b, 10000))
    for i, a in enumerate(hub_a):
        nxt = hub_a[i + 1] if i + 1 < len(hub_a) else 1
        roads.append((a, nxt, toll(10, 100)))
        roads.append((a, random.choice(chk), toll(2000, 3000)))
    for b in hub_b:
        roads.append((b, random.choice(chk), 6000))
    for t in chk:
        roads.append((t, random.choice(hub_a), toll(2000, 3000)))
        roads.append((t, 1, 10000))
    roads, chk, _ = relabel(n, roads, chk)
    add(n, roads, chk, queries(n, q, kind))


# samples
add(4, [(2, 1, 100), (2, 3, 200), (3, 1, 300), (4, 3, 50)], [3],
    [[2, 10, 20, -1, -1, -1]])
add(3, [(1, 3, 20), (3, 1, 40), (2, 1, 500)], [3],
    [[1, -1, -1, -1, -1, -1], [2, 0, 0, 0, 0, 0]])
add(3, [(2, 1, 1000), (3, 2, 400)], [1, 3],
    [[1, 0, 0, 0, 0, 0], [3, -1, -1, -1, -1, 500]])
add(4, [(3, 2, 1000), (2, 1, 1000)], [2],
    [[4, 7, 7, 7, 7, 7], [2, 60, 60, 60, 60, -1]])
# hidden: small (brute checks these)
for n, m, k in [(5, 8, 1), (6, 12, 2), (8, 16, 3), (8, 10, 1), (10, 25, 4), (12, 30, 1), (12, 20, 12)]:
    roads = rand_graph(n, m, 10, ri(100, 1000))
    chk = random.sample(range(1, n + 1), k)
    add(n, roads, chk, queries(n, 40, random.choice(["mix", "cheap", "zero"])))
add(15, rand_graph(15, 40, 10, 10 ** 9), random.sample(range(2, 16), 2), queries(15, 30, "dear"))
# hidden: big (N = 5 000, M <= 10 000, Q = 50 000)
N, M = MAXN, MAXM
two_ways(N, M, 5)
two_ways(N, M, 50, kind="cheap")
two_ways(N, M, 1, 10, 10 ** 5, kind="zero")
two_ways(N, M, 200, 10 ** 6, MAXC, kind="dear")
chain(N, 0, 1, MAXC)                                     # out to the far end and back: answers near 2 * 10^13
chain(N, 0, 3, MAXC, kind="cheap")
chain(N, 0, 1, 10 ** 6, kind="zero", cap_chk=True)
chain(N, 0, 10, 10000, kind="none")
greedy_trap(N)
greedy_trap(N, kind="zero")
add(N, rand_graph(N, M, 10, MAXC), random.sample(range(1, N + 1), N // 2), queries(N, MAXQ))   # half are checkpoints
add(N, rand_graph(N, M, 10, 1000), random.sample(range(2, N + 1), N // 10), queries(N, MAXQ, "cheap"))
add(N, rand_graph(N, M, 10 ** 5, 2 * 10 ** 5), [ri(2, N)], queries(N, MAXQ, "mix"))
sparse = rand_graph(N, N + N // 2, 10, MAXC)                                                   # many -1 answers
add(N, sparse, random.sample(range(2, N + 1), 3), queries(N, MAXQ, "mix"))
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
print(len(tests))
