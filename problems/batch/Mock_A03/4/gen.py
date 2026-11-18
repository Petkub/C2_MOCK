# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Graphs are built with a hidden 2-colouring (each new vertex hangs under an earlier one with the other colour,
# extra edges join opposite colours); an "odd" edge joins two vertices of the same colour.
# Shifts are the hidden colouring, flipped per component at random, with some noise.
import gc, os, random
from math import gcd
from operator import add as add_str, itemgetter

gc.disable()  # many small tuples: the collector would only slow this down

random.seed(7054)
rnd = random.random
MAXN, MAXM = 100000, 100000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def shuffle(a):
    keys = [rnd() for _ in a]
    order = sorted(range(len(a)), key=keys.__getitem__)
    a[:] = [a[i] for i in order]


def add(n, s, edges):
    """edges: list of "u v" strings"""
    m = len(edges)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM and len(s) == n and set(s) <= {"A", "B"}
    tests.append(f"{n} {m}\n{s}\n" + "\n".join(edges) + "\n")


def add_pairs(n, s, pairs):
    for u, v in pairs:
        assert 1 <= u <= n and 1 <= v <= n and u != v
    add(n, s, [f"{u} {v}" for u, v in pairs])


class G:
    """vertices 0..n-1 (internal), relabelled when written"""

    def __init__(self, n):
        self.n = n
        self.col = [0] * n
        self.edges = []
        self.tail = []          # written after the (shuffled) edges
        self.comps = []

    def comp(self, vs, extra, kind="random"):
        """make vs one connected bipartite component with len(vs)-1 tree edges plus extra edges"""
        col, n = self.col, len(vs)
        if kind == "path":
            par = vs[:-1]
        else:
            par = [vs[int(rnd() * k)] for k in range(1, n)]
        col[vs[0]] = 0
        for p, v in zip(par, vs[1:]):
            col[v] = 1 - col[p]
        self.edges += zip(par, vs[1:])
        s0 = [v for v in vs if col[v] == 0]
        s1 = [v for v in vs if col[v] == 1]
        if s1:
            a, b = len(s0), len(s1)
            self.edges += [(s0[int(rnd() * a)], s1[int(rnd() * b)]) for _ in range(extra)]
        self.comps.append(vs)

    def odd(self, vs):
        """an edge inside vs between two vertices of the same colour"""
        side = [v for v in vs if self.col[v] == 0]
        if len(side) < 2:
            side = [v for v in vs if self.col[v] == 1]
        assert len(side) >= 2
        while True:
            a, b = side[int(rnd() * len(side))], side[int(rnd() * len(side))]
            if a != b:
                self.edges.append((a, b))
                return

    def labels(self, noise):
        """the hidden colouring, flipped per component at random, then each shift flipped with probability noise"""
        ori = [rnd() < 0.5 for _ in range(self.n)]     # a vertex outside every component gets a random shift
        for vs in self.comps:
            o = rnd() < 0.5
            for v in vs:
                ori[v] = o
        return [c ^ o ^ (rnd() < noise) for c, o in zip(self.col, ori)]

    def write(self, lab, perm=True, order=True, ids=None):
        n = self.n
        if ids is None:
            ids = list(range(1, n + 1))
            if perm:
                shuffle(ids)
        e = self.edges
        m = len(e)
        if order and m > 1:
            # a golden-ratio stride visits every edge once and spreads neighbouring ones apart
            step, start = int(m * 0.6180339887), int(rnd() * m)
            while gcd(step, m) != 1:
                step += 1
            e = [e[(start + k * step) % m] for k in range(m)]
        e = e + self.tail
        eu, ev = list(map(itemgetter(0), e)), list(map(itemgetter(1), e))
        eu[::3], ev[::3] = ev[::3], eu[::3]
        assert all(map(int.__ne__, eu, ev)) and min(eu) >= 0 and min(ev) >= 0 and max(eu) < n and max(ev) < n
        sid = list(map(str, ids))
        sp = [x + " " for x in sid]
        out = list(map(add_str, map(sp.__getitem__, eu), map(sid.__getitem__, ev)))
        s = [""] * n
        for v, x in zip(ids, lab):
            s[v - 1] = "AB"[x]
        add(n, "".join(s), out)


def split(n, k, lo=1):
    """k sizes >= lo summing to n"""
    cuts = sorted(ri(0, n - k * lo) for _ in range(k - 1))
    sizes, prev = [], 0
    for c in cuts + [n - k * lo]:
        sizes.append(c - prev + lo)
        prev = c
    return sizes


def build(n, sizes, m, kind="random"):
    """components of the given sizes (others isolated), about m edges in total"""
    g = G(n)
    vs = list(range(n))
    shuffle(vs)                  # so the vertex numbers need no shuffle when written
    tree = sum(s - 1 for s in sizes)
    spare = max(0, m - tree)
    pos, big = 0, [s for s in sizes if s >= 2]
    tot = sum(big)
    for s in sizes:
        part = vs[pos:pos + s]
        pos += s
        if s >= 2:
            g.comp(part, spare * s // tot, kind)
        else:
            g.comps.append(part)     # a lone vertex: what comp() does for it, without the call
    return g


def random_case(n, m, ncomp, noise, odd=0, kind="random", lo=2):
    g = build(n, split(n, ncomp, lo), m - odd, kind)
    cs = [c for c in g.comps if len(c) >= 3]
    for _ in range(odd):
        g.odd(cs[int(rnd() * len(cs))])
    g.write(g.labels(noise), perm=False)


def odd_late(g, frac):
    """an odd edge in the group (>= 3 workers) whose least number is at position frac among those groups"""
    cs = sorted((c for c in g.comps if len(c) >= 3), key=min)
    c = cs[min(len(cs) - 1, int(frac * len(cs)))]
    assert 0 not in c
    g.odd(c)


# samples
add_pairs(7, "ABAAABB", [(1, 2), (2, 3), (3, 4), (5, 6), (6, 7)])
add_pairs(4, "ABAB", [(1, 2), (2, 3), (3, 1), (3, 4)])
add_pairs(6, "BBABAB", [(1, 4), (4, 2), (2, 5), (5, 1), (3, 6)])
add_pairs(6, "AAAAAA", [(2, 4), (4, 6), (1, 3)])
add_pairs(7, "AABBABA", [(1, 7), (7, 4), (4, 6), (2, 5), (5, 3), (6, 1)])
# hidden: small (brute tries every assignment) and medium
add_pairs(2, "AA", [(1, 2)])
add_pairs(2, "AB", [(2, 1), (1, 2), (1, 2)])
random_case(15, 18, 3, 0.2)
random_case(18, 20, 4, 0.1, odd=1)
random_case(20, 16, 6, 0.5, lo=1)
random_case(2000, 3000, 50, 0.1)
g = G(3000)                                    # long odd cycle away from vertex 1
g.comp(list(range(999)), 600)
g.comp(list(range(999, 3000)), 0, "path")
g.edges.append((999, 2999))
g.write(g.labels(0.2), perm=False)
random_case(5000, 5000, 300, 0.3, lo=1)
# hidden: big (N = 100000 or M = 100000)
N, H = MAXN, MAXN // 2
g = G(N)                                       # 95000 alone, 1000 small groups, one dense group of 2000
vs = list(range(N))
shuffle(vs)
pos = 0
for s in split(3000, 1000, 2):
    g.comp(vs[pos:pos + s], 0)
    pos += s
g.comp(vs[pos:pos + 2000], MAXM - len(g.edges) - 1999)
g.write(g.labels(0.5), perm=False)
random_case(N, MAXM, 25000, 0.0)               # 25000 groups, nobody moves
g = G(N)                                       # path 1-2-...-N, edges listed from the far end
g.comp(list(range(N)), 0, "path")
g.edges.reverse()
g.write(g.labels(0.4), perm=False, order=False)
g = G(N)                                       # even cycle of N vertices
g.comp(list(range(N)), 0, "path")
g.edges.append((0, N - 1))
g.write(g.labels(0.3))
g = G(N)                                       # complete bipartite 150 x 300, 2500 pairs, the rest isolated
vs = list(range(N))
shuffle(vs)
a, b = vs[:150], vs[150:450]
g.edges += [(u, v) for u in a for v in b]
for v in b:
    g.col[v] = 1
g.comps.append(a + b)
for i in range(450, 5450, 2):
    g.comp([vs[i], vs[i + 1]], 0)
g.write(g.labels(0.45))
C = 33333                                      # grid 2 x 33333 with holes, numbered by column, far edges first
g = G(2 * C)
alive = [rnd() < 0.99 for _ in range(2 * C)]
for c in range(C):
    for r in range(2):
        i = 2 * c + r
        if not alive[i]:
            continue
        g.col[i] = (r + c) & 1
        if r == 0 and alive[i + 1]:
            g.edges.append((i, i + 1))
        if c + 1 < C and alive[i + 2]:
            g.edges.append((i, i + 2))
g.comps.append([i for i in range(2 * C) if alive[i]])
g.edges.reverse()
g.write(g.labels(0.2), perm=False, order=False)
g = build(N, split(N, 5000, 1), N - 5000)      # forest of 5000 groups, 2000 pairs twice
g.edges = g.edges + g.edges[:2000]
g.write(g.labels(0.25), perm=False)
g = build(N, split(N, 20000, 2), MAXM)         # 20000 groups, all in shift A
g.write([0] * N, perm=False)
g = build(N, split(N, 50, 1000), N - 50, "path")   # 50 long paths
g.write(g.labels(0.35), perm=False)
g = build(60000, [6] * 10000, MAXM)            # 10000 groups of 6 with many repeated edges
g.write(g.labels(0.3), perm=False)
g = build(N, [2] * 3 + [1] * (N - 6), 3)      # almost everyone alone
g.write(g.labels(0.5), perm=False)
g = build(N, [2] * 2000 + [3] * 1000 + [1] * (N - 7000), 4000)   # pairs and triples, the rest alone
g.write(g.labels(0.3), perm=False)
# hidden: big, impossible
g = build(N, split(N, 25000, 2), MAXM - 1)     # 25000 groups, the odd edge in the last one reached
odd_late(g, 1.0)
g.write(g.labels(0.1), perm=False)
g = build(N, [3] + split(N - 3, 5000, 2), MAXM - 1)   # one triangle, the highest numbers
tri = g.comps[0]
g.odd(tri)
ids = list(range(1, N - 2))
shuffle(ids)
idmap = [0] * N
trs = set(tri)
rest = [v for v in range(N) if v not in trs]
for k, v in enumerate(rest):
    idmap[v] = ids[k]
for k, v in enumerate(tri):
    idmap[v] = N - 2 + k
g.write(g.labels(0.1), ids=idmap)
g = G(N)                                       # odd cycle of N - 1 vertices, one more vertex hangs on it
g.comp(list(range(N)), 0, "path")
g.edges.append((1, N - 1))
g.write(g.labels(0.3))
g = build(N, split(N, 20000, 2), MAXM - 1)     # the odd edge is the last line, in a group reached late
odd_late(g, 0.7)
g.tail.append(g.edges.pop())
g.write(g.labels(0.2), perm=False)
L = 30001                                      # odd cycle of 30001 with the highest numbers, 15000 groups before it
g = G(N)
low, high = list(range(N - L)), list(range(N - L, N))
shuffle(low)
shuffle(high)
pos = 0
sizes = split(N - L, 15000, 2)
spare = MAXM - L - (N - L - 15000)
for s in sizes:
    g.comp(low[pos:pos + s], spare * s // (N - L))
    pos += s
g.comp(high, 0, "path")
g.edges.append((high[0], high[-1]))
g.write(g.labels(0.2), perm=False)
L = 49999                                      # worker 1 in a dense group, 30001 alone, then an odd cycle of 49999
g = G(N)
dense = list(range(20000))
shuffle(dense)
g.comp(dense, MAXM - 19999 - L)
cyc = list(range(N - L, N))
shuffle(cyc)
g.comp(cyc, 0, "path")
g.edges.append((cyc[0], cyc[-1]))
g.write(g.labels(0.3), perm=False)
g = build(N, split(N, 40, 1000), N - 41, "path")   # 40 long paths, an odd edge in the last one reached
odd_late(g, 1.0)
g.write(g.labels(0.25), perm=False)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
