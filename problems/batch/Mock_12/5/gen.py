# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import gc, os, random
gc.disable()          # many small lists: the cyclic GC only costs time here
from itertools import chain
from collections import deque

random.seed(1205190)
rnd = random.random
MAXN, MAXQ, MAXSUMK = 100000, 50000, 100000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, edges, queries, connected=False, edge_text=None):
    """edges: (u, v) with towns 1..n; queries: lists of towns; connected: already checked by Tree;
    edge_text: the edge lines already formatted (a Tree used for several tests)"""
    assert 2 <= n <= MAXN and len(edges) == n - 1
    assert 1 <= len(queries) <= MAXQ and sum(len(x) for x in queries) <= MAXSUMK
    if not connected:
        assert all(1 <= u <= n and 1 <= v <= n and u != v for u, v in edges)
        # n - 1 edges + connected = the roads form a tree
        adj = [[] for _ in range(n + 1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        seen = [False] * (n + 1)
        seen[1] = True
        order = [1]
        for u in order:
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    order.append(v)
        assert len(order) == n
    assert all(len(x) >= 1 and len(set(x)) == len(x) for x in queries)
    flat = [t for x in queries for t in x]
    assert 1 <= min(flat) and max(flat) <= n
    lines = [f"{n} {len(queries)}\n"]
    lines.append(edge_text or "%d %d\n" * len(edges) % tuple(chain.from_iterable(edges)))
    lines += [f"{len(x)} " + " ".join(map(str, x)) + "\n" for x in queries]
    tests.append("".join(lines))


class Tree:
    """a tree on internal vertices 0..n-1 (root 0) given by its edges; towns are a random relabelling, root -> 1"""

    def __init__(self, n, edges, root=0):
        """edges: (child, parent) pairs with parent < child when root = 0; any edges when root != 0"""
        self.n = n
        par = [0] * n
        dep = [0] * n
        if root == 0:
            for c, p in edges:
                assert p < c
                par[c] = p
            for c in range(1, n):
                dep[c] = dep[par[c]] + 1
        else:
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            par[root] = -1
            seen = [False] * n
            seen[root] = True
            order = [root]
            for u in order:
                for v in adj[u]:
                    if not seen[v]:
                        seen[v] = True
                        par[v] = u
                        dep[v] = dep[u] + 1
                        order.append(v)
            par[root] = root
        ch = [[] for _ in range(n)]
        for c in range(root):
            ch[par[c]].append(c)
        for c in range(root + 1, n):
            ch[par[c]].append(c)
        # n - 1 edges and every vertex reaches the root: the edges form a tree
        assert len(edges) == n - 1 and sum(len(x) for x in ch) == n - 1 and max(dep) < n
        self.par, self.dep, self.ch, self.root = par, dep, ch, root
        key = [rnd() for _ in range(n - 1)]
        lab = [x + 2 for x in sorted(range(n - 1), key=key.__getitem__)]      # a random permutation of 2..n
        lab.insert(root, 1)
        self.lab = lab
        es = [(lab[u], lab[v]) if rnd() < 0.5 else (lab[v], lab[u]) for u, v in edges]
        key = [rnd() for _ in range(n - 1)]
        self.edges = [es[i] for i in sorted(range(n - 1), key=key.__getitem__)]   # random order
        self.deep_list = sorted(range(n), key=dep.__getitem__, reverse=True)
        self.order = self.edge_text = None

    def fill(self, wants):
        """wants: list of (endpoint e, k); returns for each a list of at most k towns, each on the route
        root -> e or a child of a route town; a DFS preorder keeps the current route in `route`"""
        at = {}
        for i, (e, k) in enumerate(wants):
            at.setdefault(e, []).append(i)
        res = [None] * len(wants)
        if self.order is None:          # once per tree (a tree may be used for several tests)
            order, st = [], [self.root]
            while st:
                u = st.pop()
                order.append(u)
                st.extend(self.ch[u])
            tin = [0] * self.n
            for i, u in enumerate(order):
                tin[u] = i
            size = [1] * self.n
            par = self.par
            for u in order[:0:-1]:      # order[0] is the root
                size[par[u]] += size[u]
            self.order, self.tin, self.size = order, tin, size
        order = self.order
        route = [0] * self.n
        dep, ch = self.dep, self.ch
        for u in order:
            route[dep[u]] = u
            if u not in at:
                continue
            m = dep[u] + 1
            for i in at[u]:
                k = wants[i][1]
                got = {}
                for _ in range(3 * k + 5):
                    if len(got) == k:
                        break
                    a = route[int(rnd() * m)]
                    c = ch[a]
                    if c and rnd() < 0.5:
                        got[c[int(rnd() * len(c))]] = 0
                    else:
                        got[a] = 0
                res[i] = list(got)       # random order (insertion order of the dict)
        return res

    def random_query(self, k):
        s = set()
        while len(s) < k:
            s.add(int(rnd() * self.n))
        return sorted(s)

    def anc(self, a, b):
        """a is b or an ancestor of b"""
        return self.tin[a] <= self.tin[b] < self.tin[a] + self.size[a]

    def mix(self, q, sumk, kmax, p_far=0.3, p_broken=0.4):
        """yes-queries (towns served by one random route), far queries (a deep route plus a town near the root);
        p_broken of them get one extra town whose parent is off that route (the answer becomes -1)"""
        plan = []
        left = sumk
        for i in range(q):
            room = left - (q - i - 1)
            k = max(1, min(room, ri(1, kmax), self.n - 1))
            brk = rnd() < p_broken and k >= 2
            far = rnd() < p_far and k - brk >= 2
            kk = k - brk - far
            if far:
                e = self.deep_list[int(rnd() * min(self.n, 50))]
            else:
                e = self.deep_list[int(rnd() * rnd() * self.n)]
            plan.append((e, kk, far, brk))
            left -= k
        got = self.fill([(e, kk) for e, kk, _, _ in plan])
        out = []
        par, dep = self.par, self.dep
        for (e, kk, far, brk), x in zip(plan, got):
            x = list(x)
            if far:
                r = self.root if rnd() < 0.3 or not self.ch[self.root] else \
                    self.ch[self.root][int(rnd() * len(self.ch[self.root]))]
                if r not in x:
                    x.insert(int(rnd() * (len(x) + 1)), r)
            if brk:
                deep = max((par[v] for v in x), key=dep.__getitem__)
                for _ in range(6):
                    y = int(rnd() * self.n)
                    py = par[y]
                    if y not in x and not self.anc(py, deep) and not self.anc(deep, py):
                        x.insert(int(rnd() * (len(x) + 1)), y)
                        break
            out.append(x)
        return out

    def emit(self, queries):
        lab = self.lab
        if self.edge_text is None:
            self.edge_text = "%d %d\n" * len(self.edges) % tuple(chain.from_iterable(self.edges))
        add(self.n, self.edges, [[lab[v] for v in x] for x in queries], connected=True, edge_text=self.edge_text)


def path_edges(n):
    return [(i, i - 1) for i in range(1, n)]


def rec_edges(n, back):
    """parent of i is one of the `back` previous vertices (back = n: a random recursive tree)"""
    return [(i, i - 1 - int(rnd() * min(back, i))) for i in range(1, n)]


def caterpillar(n, spine):
    e = path_edges(spine)
    for i in range(spine, n):
        e.append((i, int(rnd() * spine)))
    return e


def broom(n, handle):
    e = path_edges(handle)
    for i in range(handle, n):
        e.append((i, handle - 1))
    return e


def two_arms(n):
    """root 0 with two long paths"""
    e = [(1, 0), (2, 0)]
    for i in range(3, n):
        e.append((i, i - 2))
    return e


def binary(n):
    return [(i, (i - 1) // 2) for i in range(1, n)]


def star(n):
    return [(i, 0) for i in range(1, n)]


def raw(n, edges, queries):
    add(n, edges, queries)


# samples
raw(7, [(1, 2), (1, 3), (2, 4), (2, 5), (4, 6), (3, 7)], [[5, 6, 3], [6, 7]])
raw(5, [(2, 1), (3, 2), (4, 3), (5, 2)], [[4, 5], [5]])
raw(5, [(3, 1), (1, 5), (5, 2), (4, 3)], [[2, 4], [4, 1]])
raw(5, [(5, 1), (4, 5), (2, 4), (3, 1)], [[2, 3], [1]])
raw(5, [(1, 4), (4, 2), (2, 5), (4, 3)], [[5, 3], [3, 2, 1]])
# hidden: small (brute checks these)
raw(2, [(2, 1)], [[1], [2], [1, 2]])
for n, shape in ((12, "rec"), (30, "deep"), (40, "cat"), (25, "binary"), (60, "arms")):
    e = {"rec": rec_edges(n, n), "deep": rec_edges(n, 3), "cat": caterpillar(n, 12),
         "binary": binary(n), "arms": two_arms(n)}[shape]
    t = Tree(n, e, root=int(rnd() * n) if shape == "rec" else 0)
    t.emit(t.mix(60, 300, 6, p_broken=0.35))
t = Tree(8, star(8))
t.emit([t.random_query(ri(1, 8)) for _ in range(20)])
# hidden: big
N = MAXN


def big(edges, q, sumk, kmax, root=0, **kw):
    """edges: a list of edges, or a Tree (used for several tests)"""
    t = edges if isinstance(edges, Tree) else Tree(N, edges, root)
    t.emit(t.mix(q, sumk, kmax, **kw))


PATH, DEEP = Tree(N, path_edges(N)), Tree(N, rec_edges(N, 2))           # each used in several tests
big(PATH, MAXQ, 70000, 2)                                              # one long road, root at the end
big(path_edges(N), 30000, 45000, 2, root=N // 3)                        # root inside the road
big(DEEP, 30000, 45000, 3)                                              # deep, random branches
big(rec_edges(N, 3), 25000, 40000, 3, p_far=0.6)
big(caterpillar(N, N // 2), 30000, 45000, 3, p_far=0.6)
big(caterpillar(N, 9 * N // 10), 30000, 40000, 2, p_far=0.7, p_broken=0.2)
big(broom(N, N // 2), 40000, 55000, 2, p_far=0.7)
big(two_arms(N), MAXQ, 70000, 2, p_far=0.5)
big(rec_edges(N, N), 25000, 40000, 3)                                  # random recursive tree (shallow)
big(rec_edges(N, 5), 600, 60000, 400)                               # few queries with many towns
big(PATH, 6, 60000, 20000, p_far=0.0, p_broken=0.5)        # huge queries on a long road
big(DEEP, MAXQ, MAXQ, 1, p_far=0.0, p_broken=0.0)           # one town per query
big(caterpillar(N, 2 * N // 3), 30000, 45000, 2, root=N // 8)
big(rec_edges(N, 4), 40000, 60000, 2, p_far=0.7, p_broken=0.7)
DEEP.emit([DEEP.random_query(ri(1, 2)) for _ in range(30000)])                # random towns: mostly -1

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
