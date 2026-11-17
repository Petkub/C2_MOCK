# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Every test is built from a hidden colouring (1 red, 0 blue), so the reports never contradict each other.
# Shapes: random pairs, long chains, many reports inside one group (no new information),
# small groups with a known student that join a bigger group without one, known students given early or late,
# and a skewed hidden colouring (mostly red) where the known students decide the answer.
import os, random

random.seed(20190)
rnd = random.random
MAXN, MAXQ = 200000, 150000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, evs):
    q = len(evs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    lines = ["%d %d" % (n, q)]
    for e in evs:
        assert e[0] in (1, 2, 3, 4)
        if e[0] <= 2:
            assert len(e) == 3 and 1 <= e[1] <= n and 1 <= e[2] <= n and e[1] != e[2]
        else:
            assert len(e) == 2 and 1 <= e[1] <= n
        lines.append(" ".join(map(str, e)))
    tests.append("\n".join(lines) + "\n")


def check(n, evs):
    """assert some colouring fits every report (simple DSU with parity)"""
    up, par = list(range(n + 1)), [0] * (n + 1)

    sz = [1] * (n + 1)

    def find(v):
        path = []
        while up[v] != v:
            path.append(v)
            v = up[v]
        for u in reversed(path):        # compress, nearest to the root first
            if up[u] != v:
                par[u] ^= par[up[u]]
                up[u] = v
        return v, (par[path[0]] if path else 0)
    for e in evs:
        a, b, d = (e[1], 0, e[0] - 1) if e[0] <= 2 else (e[1], 0, e[0] - 3)
        if e[0] <= 2:
            b = e[2]
        ra, pa = find(a)
        rb, pb = find(b)
        if ra == rb:
            assert pa ^ pb == d
        else:
            if sz[ra] < sz[rb]:
                ra, rb = rb, ra
            up[rb] = ra
            par[rb] = pa ^ pb ^ d
            sz[ra] += sz[rb]
    return True


def colouring(n, pred=0.5):
    return [0] + [1 if rnd() < pred else 0 for _ in range(n)]


def pair_ev(col, a, b):
    return (1 if col[a] == col[b] else 2, a, b)


def know_ev(col, a):
    return (3 if col[a] == 1 else 4, a)


def rand_events(n, q, col, pknow=0.05, local=0):
    evs = []
    while len(evs) < q:
        a = ri(1, n)
        if rnd() < pknow:
            evs.append(know_ev(col, a))
            continue
        if local:
            b = a + ri(-local, local)
            if b < 1 or b > n or b == a:
                continue
        else:
            b = ri(1, n)
            if b == a:
                continue
        evs.append(pair_ev(col, a, b))
    return evs


def build(n, evs):
    if n <= 2000:                        # big tests come from a colouring as well; checking them is slow in Python
        check(n, evs)
    add(n, evs)


def chain(n, q, col, pknow=0.0):
    """joins along a random order of the students, so groups grow into long paths"""
    perm = list(range(1, n + 1))
    random.shuffle(perm)
    links = [(perm[i], perm[i + 1]) for i in range(n - 1)]
    random.shuffle(links)
    evs = []
    for a, b in links:
        if len(evs) >= q:
            break
        if rnd() < pknow:
            evs.append(know_ev(col, a))
        evs.append(pair_ev(col, a, b) if rnd() < 0.5 else pair_ev(col, b, a))
    while len(evs) < q:
        a, b = ri(1, n), ri(1, n)
        if a != b:
            evs.append(pair_ev(col, a, b))
    return evs[:q]


def small_known_into_big(n, q, col, gsize):
    """first many small groups, each with one known student, then one big group without a known student,
    then the small groups join the big one (the big one is larger, so it stays the root in a union by size)"""
    ids = list(range(1, n + 1))
    random.shuffle(ids)
    half = n // 2
    big, rest = ids[:half], ids[half:]
    evs = []
    ng = min(len(rest) // gsize, (q - len(big) + 1) // (gsize + 1))
    groups = [rest[i * gsize:(i + 1) * gsize] for i in range(ng)]
    for g in groups:
        for i in range(1, len(g)):
            evs.append(pair_ev(col, g[i - 1], g[i]))
        evs.append(know_ev(col, g[ri(0, len(g) - 1)]))
    for i in range(1, len(big)):
        evs.append(pair_ev(col, big[ri(0, i - 1)], big[i]))
    for g in groups:
        evs.append(pair_ev(col, big[ri(0, len(big) - 1)], g[ri(0, len(g) - 1)]))
    while len(evs) < q:
        a, b = ri(1, n), ri(1, n)
        if a != b:
            evs.append(pair_ev(col, a, b))
    assert len(evs) <= q
    return evs


def redundant(n, q, col, groups):
    """a few groups built first, then mostly reports inside a group (no new information), merges late"""
    ids = list(range(1, n + 1))
    random.shuffle(ids)
    parts = [ids[i::groups] for i in range(groups)]
    evs = []
    for g in parts:
        for i in range(1, len(g)):
            evs.append(pair_ev(col, g[ri(0, i - 1)], g[i]))
    extra = q - len(evs) - (groups - 1)
    for _ in range(extra):
        g = parts[ri(0, groups - 1)]
        if rnd() < 0.1:
            evs.append(know_ev(col, g[ri(0, len(g) - 1)]))
            continue
        a, b = g[ri(0, len(g) - 1)], g[ri(0, len(g) - 1)]
        if a == b:
            b = g[0] if a != g[0] else g[1]
        evs.append(pair_ev(col, a, b))
    for i in range(1, groups):
        pos = ri(len(evs) // 2, len(evs))
        evs.insert(pos, pair_ev(col, parts[0][ri(0, len(parts[0]) - 1)], parts[i][0]))
    return evs[:q]


# samples
add(5, [(2, 1, 2), (1, 2, 3), (2, 4, 5), (3, 2), (1, 1, 4)])
add(6, [(1, 1, 2), (1, 2, 3), (2, 3, 4), (3, 1), (2, 5, 6), (1, 4, 5)])
add(4, [(3, 2), (3, 2), (1, 2, 1), (4, 3), (2, 3, 4), (1, 4, 1)])
add(7, [(2, 1, 2), (2, 2, 3), (2, 3, 4), (2, 5, 6), (1, 6, 7), (2, 4, 5), (1, 1, 3), (4, 7)])
add(8, [(1, 1, 2), (2, 3, 4), (2, 5, 6), (1, 7, 8), (2, 2, 3), (1, 6, 7), (4, 8), (1, 5, 4)])
# hidden: small (the brute checks these)
add(1, [(3, 1), (3, 1)])
for n, q, pk in [(8, 12, 0.2), (10, 15, 0.3), (12, 20, 0.1), (15, 25, 0.0)]:
    c = colouring(n, ri(2, 8) / 10)
    build(n, rand_events(n, q, c, pk))
c = colouring(300, 0.7)
build(300, small_known_into_big(300, 500, c, 3))
c = colouring(2000)
build(2000, rand_events(2000, 3000, c, 0.05))
c = colouring(1500)
build(1500, redundant(1500, 3000, c, 4))
# hidden: big (N = 200000, Q = 150000 unless said)
N, Q = MAXN, MAXQ
c = colouring(N)
build(N, rand_events(N, Q, c, 0.02))
c = colouring(N, 0.9)
build(N, rand_events(N, Q, c, 0.01))                          # mostly red: known students matter
c = colouring(N)
build(N, rand_events(N, Q, c, 0.0))                           # nobody known
c = colouring(N, 0.3)
build(N, rand_events(N, Q, c, 0.3))                           # many known students
c = colouring(N)
build(N, chain(N, Q, c))                                      # one long path at the end
c = colouring(N, 0.8)
build(N, chain(N, Q, c, 0.001))
c = colouring(N, 0.85)
build(N, small_known_into_big(N, Q, c, 2))
c = colouring(N, 0.2)
build(N, small_known_into_big(N, Q, c, 5))
c = colouring(N)
build(N, small_known_into_big(N, Q, c, 50))
c = colouring(N, 0.6)
build(N, redundant(N, Q, c, 2))
c = colouring(N)
build(N, redundant(N, Q, c, 30))
c = colouring(N, 0.75)
build(N, rand_events(N, Q, c, 0.02, local=3))                 # many small groups for a long time
c = colouring(N)
build(N, rand_events(N, Q, c, 0.05, local=50))
c = colouring(N, 1.0)
build(N, rand_events(N, Q, c, 0.0005))                        # everybody red
c = colouring(1000, 0.65)
build(1000, rand_events(1000, Q, c, 0.01))                    # few students, many reports
c = colouring(N, 0.55)
build(N, [know_ev(c, i) for i in random.sample(range(1, N + 1), N // 2)] +
      chain(N, Q - N // 2, c))                                # known students first, joins later
c = colouring(N, 0.45)
evs = chain(N, Q - N // 4, c)
build(N, evs + [know_ev(c, i) for i in random.sample(range(1, N + 1), N // 4)])  # joins first, known students last

c = colouring(N)
evs = [pair_ev(c, i + 1, i) for i in range(1, 100000)]       # a path where the newest student is always first
while len(evs) < Q:
    b = ri(2, N)
    evs.append(pair_ev(c, 1, b) if rnd() < 0.9 else know_ev(c, 1))
build(N, evs)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for f in os.listdir("tests"):
    if f.endswith(".in") or f.endswith(".out"):
        os.remove(os.path.join("tests", f))
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
