# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1101)
MAXN, MAXQ = 100000, 50000
rnd = random.random
tests = []
LABELS = {}


def add(n, par, qs, is_tree=False):
    """par[i] for i = 2..n (par[0], par[1] unused); qs = list of (a, b, c, d);
    is_tree: par comes from a Tree, which checked it already, and qs is flat (a1, b1, c1, d1, a2, ...)"""
    q = len(qs) // 4 if is_tree else len(qs)
    assert 2 <= n <= MAXN and 1 <= q <= MAXQ
    if not is_tree:
        # n - 1 roads and every town is reached from town 1 going down to children: a tree
        p = par[2:n + 1]
        assert 1 <= min(p) and max(p) <= n and all(par[i] != i for i in range(2, n + 1))
        kids = [[] for _ in range(n + 1)]
        for i in range(2, n + 1):
            kids[par[i]].append(i)
        seen = [1]
        for u in seen:
            seen.extend(kids[u])
        assert len(seen) == n
    flat = qs if is_tree else [x for t in qs for x in t]
    assert len(flat) % 4 == 0
    assert 1 <= min(flat) and max(flat) <= n
    lines = [f"{n} {q}", " ".join(map(str, par[2:n + 1]))]
    tests.append("\n".join(lines) + "\n" + "%d %d %d %d\n" * q % tuple(flat))


class Tree:
    """a tree given in build order: p[i] < i for i >= 1 (vertex 0 is the root);
    labels: build vertex i is town lab[i], the root is town 1, the others are shuffled"""

    def __init__(self, p):
        n = len(p)
        self.n = n
        if n not in LABELS:         # one shuffled labelling per size (shuffling is slow)
            lab = list(range(2, n + 1))
            random.shuffle(lab)
            LABELS[n] = [1] + lab
        self.lab = LABELS[n]
        # p[i] < i and the labels are a permutation with the root as town 1: a tree whose towns all reach town 1
        assert p[0] == 0 and all(0 <= p[i] < i for i in range(1, n))
        assert self.lab[0] == 1 and len(set(self.lab)) == n and min(self.lab) == 1 and max(self.lab) == n
        par = [0] * (n + 1)
        for i in range(1, n):
            par[self.lab[i]] = self.lab[p[i]]
        self.par = par
        self.p = p
        ch = [[] for _ in range(n)]
        for i in range(1, n):
            ch[p[i]].append(i)
        self.ch = ch
        size = [1] * n
        for i in range(n - 1, 0, -1):
            size[p[i]] += size[i]
        self.size = size
        # preorder: subtree of v = order[tin[v] .. tin[v] + size[v] - 1]
        tin = [0] * n
        order = []
        st = [0]
        while st:
            u = st.pop()
            tin[u] = len(order)
            order.append(u)
            st.extend(ch[u])
        self.tin, self.order = tin, order

    def any(self):
        return int(rnd() * self.n)

    def arms(self, v):
        """the parts of the tree around v: each child subtree, and the rest above v (as -1)"""
        a = list(self.ch[v])
        if v != 0:
            a.append(-1)
        return a

    def pt(self, v, arm):
        """a random vertex of the arm `arm` of v"""
        if arm == -1:
            r = int(rnd() * (self.n - self.size[v]))
            return self.order[r if r < self.tin[v] else r + self.size[v]]
        return self.order[self.tin[arm] + int(rnd() * self.size[arm])]

    def query(self, kind):
        """one query of the given kind, in build vertices"""
        n = self.n
        if kind == "rand":
            return (self.any(), self.any(), self.any(), self.any())
        if kind == "same":
            a, b = self.any(), self.any()
            r = rnd()
            if r < 0.4:
                return (a, b, a, b)
            if r < 0.8:
                return (a, b, b, a)
            return (a, a, a, a) if r < 0.9 else (a, a, b, b)
        for _ in range(100):
            v = self.any()
            ar = self.arms(v)
            if len(ar) >= 2 or (kind == "nest" and self.ch[v]):
                break
        else:
            return self.query("rand")       # tiny tree without a suitable vertex
        k = len(ar)
        if k > 1:       # move up to four random distinct arms to the front (a partial shuffle)
            for i in range(min(k - 1, 4)):
                j = i + int(rnd() * (k - i))
                ar[i], ar[j] = ar[j], ar[i]
        P = self.pt
        if kind == "one":         # two paths meeting only at v
            a, b = P(v, ar[0]), (P(v, ar[2]) if len(ar) >= 3 and rnd() < 0.6 else v)
            c, d = P(v, ar[1]), (P(v, ar[3]) if len(ar) >= 4 and rnd() < 0.6 else v)
        elif kind == "nest":      # a path inside one child subtree of v, the other through v
            c0 = next(x for x in ar if x != -1)
            rest = [x for x in ar if x != c0]
            a, b = P(v, c0), P(v, c0)
            c = P(v, rest[0]) if rest else v
            d = P(v, rest[1]) if len(rest) >= 2 and rnd() < 0.7 else v
        elif kind == "sib":       # paths inside two different arms of v
            a, b = P(v, ar[0]), P(v, ar[0])
            c, d = P(v, ar[1]), P(v, ar[1])
        else:                     # "over": both paths through v using some common arms
            x, y = ar[0], ar[1]
            a, b = P(v, x), P(v, y)
            if len(ar) >= 3 and rnd() < 0.4:
                y = ar[2]
            c, d = P(v, x), P(v, y)
        return (a, b, c, d)

    def queries(self, q, mix):
        """q queries as a flat list a1 b1 c1 d1 a2 ...; mix = list of (kind, weight), each kind gets its share
        of the q queries; endpoints of each path and the two paths in random order"""
        tot = sum(w for _, w in mix)
        cnt = [q * w // tot for _, w in mix]
        cnt[0] += q - sum(cnt)
        n, lab = self.n, self.lab
        out = []
        for (kind, _), c in zip(mix, cnt):
            if kind == "rand":          # made in bulk (fast)
                out += [lab[int(rnd() * n)] for _ in range(4 * c)]
                continue
            for _ in range(c):
                a, b, c2, d = self.query(kind)
                if rnd() < 0.5:
                    a, b = b, a
                if rnd() < 0.5:
                    c2, d = d, c2
                if rnd() < 0.5:
                    a, b, c2, d = c2, d, a, b
                out += (lab[a], lab[b], lab[c2], lab[d])
        return out


def emit(t, q, mix):
    add(t.n, t.par, t.queries(q, mix), True)


ALL = [("rand", 3), ("one", 3), ("nest", 3), ("sib", 2), ("over", 3), ("same", 1)]
BIG = [("rand", 20), ("one", 1), ("nest", 1), ("sib", 1), ("over", 1), ("same", 1)]


# build orders (p[i] < i)
def path(n):
    return [0] + list(range(n - 1))


def near_path(n, k):
    """parent is one of the k previous vertices: deep, with many short side branches"""
    return [0] + [max(0, i - 1 - int(rnd() * k)) for i in range(1, n)]


def chains(n, legs):
    """the root with `legs` long chains"""
    p = [0] * n
    for i in range(1, n):
        p[i] = 0 if i <= legs else i - legs
    return p


def caterpillar(n, spine):
    return [0] + [i - 1 if i < spine else int(rnd() * spine) for i in range(1, n)]


def broom(n, handle):
    return [0] + [i - 1 if i < handle else handle - 1 for i in range(1, n)]


def long_branches(n, prob):
    """keep extending the last vertex; with probability prob start a new chain at a random earlier vertex"""
    return [0] + [int(rnd() * i) if rnd() < prob else i - 1 for i in range(1, n)]


def binary(n):
    return [0] + [(i - 1) // 2 for i in range(1, n)]


def recursive(n):
    return [0] + [int(rnd() * i) for i in range(1, n)]


def deep_halves(n, k):
    """two near-path halves hanging from the root"""
    h = n // 2
    p = [0] * n
    for i in range(1, n):
        if i == 1 or i == h:
            p[i] = 0
        elif i < h:
            p[i] = max(1, i - 1 - int(rnd() * k))
        else:
            p[i] = max(h, i - 1 - int(rnd() * k))
    return p


# samples
add(7, [0, 0, 1, 1, 2, 2, 3, 3], [(4, 6, 5, 7), (4, 5, 6, 7), (6, 7, 4, 1), (4, 7, 7, 4)])
add(5, [0, 0, 1, 2, 3, 4], [(1, 3, 3, 5), (2, 2, 4, 1), (5, 1, 4, 2)])
add(9, [0, 0, 1, 1, 2, 2, 4, 4, 3, 3], [(8, 9, 3, 6), (5, 6, 7, 8), (7, 6, 9, 8)])
add(2, [0, 0, 1], [(1, 2, 2, 1), (1, 1, 2, 2), (2, 2, 1, 2)])
add(8, [0, 0, 5, 1, 3, 1, 4, 6, 4], [(2, 7, 8, 6), (5, 6, 1, 4), (7, 6, 8, 5)])
# hidden: small and medium (brute checks these)
for n in (2, 3, 5):
    t = Tree(recursive(n))
    emit(t, 200, ALL)
emit(Tree(near_path(300, 3)), 2000, ALL)
emit(Tree(recursive(1000)), 2000, ALL)
emit(Tree(binary(1500)), 2000, ALL)
emit(Tree(path(2000)), 2000, ALL)
emit(Tree(caterpillar(3000, 1000)), 3000, ALL)
emit(Tree(long_branches(5000, 0.01)), 5000, ALL)
emit(Tree(chains(5000, 3)), 5000, [("one", 1), ("nest", 1), ("same", 1)])
# hidden: big (N = 100000, Q = 50000); most are deep trees, where the paths are long
N, Q = MAXN, MAXQ
t = Tree(path(N))
emit(t, Q, BIG)
emit(t, Q, [("rand", 24), ("nest", 3), ("one", 3), ("same", 1)])
t = Tree(near_path(N, 3))
emit(t, Q, BIG)
emit(t, Q, [("rand", 16), ("nest", 2), ("one", 2), ("sib", 1)])
emit(Tree(near_path(N, 8)), Q, BIG)
t = Tree(chains(N, 2))
emit(t, Q, BIG)
emit(t, Q, [("rand", 20), ("one", 2), ("nest", 2), ("over", 2)])
emit(Tree(chains(N, 5)), Q, [("rand", 20), ("one", 2), ("nest", 2), ("over", 2)])
t = Tree(caterpillar(N, N // 2))
emit(t, Q, BIG)
emit(t, Q, [("rand", 6), ("nest", 1), ("one", 1), ("sib", 1)])
emit(Tree(broom(N, N // 2)), Q, BIG)
t = Tree(deep_halves(N, 4))
emit(t, Q, BIG)
emit(t, Q, [("rand", 16), ("over", 2), ("one", 2), ("nest", 1)])
emit(Tree(long_branches(N, 0.0005)), Q, BIG)
emit(Tree(binary(N)), Q, BIG)
emit(Tree(recursive(N)), Q, BIG)
emit(Tree(near_path(N, 2)), Q, [("rand", 5), ("same", 1)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
