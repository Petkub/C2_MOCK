# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1004)
MAXN = 200000
tests = []


def add_par(p):
    """p = [p_2, ..., p_N] with 1 <= p_i < i"""
    n = len(p) + 1
    assert 2 <= n <= MAXN
    assert min(p) >= 1 and all(map(int.__lt__, p, range(2, n + 1)))
    tests.append(f"{n}\n" + " ".join(map(str, p)) + "\n")


def add_tree(par, root=None):
    """par[v] (v = 1..n-1) is the neighbour of v towards vertex 0 (par[v] < v) in a tree on 0..n-1.
    The tree is relabelled: a random vertex becomes person 1 (the path from it to 0 is reversed), then
    people get numbers in a random order in which everyone comes after the neighbour towards person 1"""
    n = len(par)
    assert n >= 2           # (par[v] < v is checked on the result by add_par)
    par = list(par)
    if root is None:
        root = random.randrange(n)
    on_path = [False] * n
    route = [root]                       # root, ..., 0
    while route[-1] != 0:
        route.append(par[route[-1]])
    for x in route:
        on_path[x] = True
    for i in range(len(route) - 1, 0, -1):
        par[route[i]] = route[i - 1]
    par[root] = root
    order = route + [v for v in range(n) if not on_path[v]]     # every vertex after its new parent
    # key = sum of random positive steps along the path from the root: larger than the parent's key
    key = [random.random() + 1e-9 for _ in range(n)]
    key[root] = 0.0
    for v in order[1:]:
        key[v] += key[par[v]]           # a wrong par[v] >= v here would break the order (caught by add_par)
    inv = sorted(range(n), key=key.__getitem__)
    lab = [0] * n
    list(map(lab.__setitem__, inv, range(1, n + 1)))
    assert inv[0] == root
    add_par([lab[par[v]] for v in inv[1:]])


# ---------- shapes: parent arrays with par[v] < v, vertex 0 first ----------
def path(n):
    return [0] + list(range(n - 1))


def star(n):
    return [0] * n


def rand_tree(n, win=None):
    r = random.randrange
    if win is None:
        return [0] + [r(v) for v in range(1, n)]
    return [0] + [v - 1 - r(min(v, win)) for v in range(1, n)]


def caterpillar(n, spine, legs=1):
    """a spine 0..spine-1; every other vertex hangs on a random spine vertex, or (legs > 1) on a short leg"""
    p = path(spine)
    r = random.randrange
    while len(p) < n:
        v = len(p)
        if legs > 1 and v > spine and r(legs) != 0:
            p.append(v - 1)
        else:
            p.append(r(spine))
    return p[:n]


def spider(n, maxleg):
    """vertex 0 with legs (paths) of random length 1..maxleg"""
    p = [0]
    while len(p) < n:
        L = random.randint(1, maxleg)
        prev = 0
        for _ in range(L):
            if len(p) == n:
                break
            p.append(prev)
            prev = len(p) - 1
    return p


def binomial(k):
    """binomial tree of order k (2^k vertices): v hangs on v with its lowest set bit cleared"""
    return [0] + [v & (v - 1) for v in range(1, 1 << k)]


def kary(n, k):
    return [0] + [(v - 1) // k for v in range(1, n)]


def pref_attach(n):
    """preferential attachment: a new vertex picks an endpoint of a random earlier edge"""
    p = [0, 0]
    ends = [0, 1]
    r = random.randrange
    for v in range(2, n):
        u = ends[r(len(ends))]
        p.append(u)
        ends.append(u)
        ends.append(v)
    return p[:n]


def star_of_stars(n, k):
    """k hubs below the root with the leaves dealt out in turn (equal sizes, so whom the root calls first matters)"""
    p = [0] * (k + 1)
    while len(p) < n:
        p.append(1 + len(p) % k)
    return p


def with_hub(base, h, total):
    """attach a hub to a random vertex of `base`, with h neighbours below it and `extra` more vertices
    hanging inside the hub's part (random small subtrees of different depths), `total` vertices in all"""
    extra = total - len(base) - 1 - h
    assert extra >= 0
    p = list(base)
    hub = len(p)
    p.append(random.randrange(hub))
    first = len(p)
    p += [hub] * h
    r = random.randrange
    for _ in range(extra):
        v = len(p)
        p.append(first + r(v - first))
    return p


def mixed(n, fan=(2, 6), shapes=("path", "bushy", "mix", "mix")):
    """n vertices: a random mixture of long thin parts (paths, few branches) and bushy parts
    (binomial-like: children of sizes about n/2, n/4, ...) under common parents, so a big part often
    needs less time than a smaller thin one"""
    P = [-1]
    r = random.random
    todo = [(0, n - 1, "mix")]           # (vertex, vertices still to hang below it, shape)
    while todo:
        root, m, kind = todo.pop()
        if m <= 0:
            continue
        if kind == "path" or m <= 2:
            prev = root
            for _ in range(m):
                P.append(prev)
                v = len(P) - 1
                if r() < 0.1 and v > 0:  # a short branch now and then
                    prev = P[v] if r() < 0.5 else v
                else:
                    prev = v
        elif kind == "bushy":
            while m > 0:
                s = max(1, int(m * (0.35 + 0.3 * r())))
                P.append(root)
                todo.append((len(P) - 1, s - 1, "bushy" if r() < 0.9 else "path"))
                m -= s
        else:
            k = random.randint(*fan)
            cuts = sorted(random.randrange(m + 1) for _ in range(k - 1))
            parts = [b - a for a, b in zip([0] + cuts, cuts + [m])]
            for s in parts:
                if s > 0:
                    P.append(root)
                    todo.append((len(P) - 1, s - 1, random.choice(shapes)))
    assert len(P) == n
    return [0] + P[1:]


# ---------- samples ----------
add_par([1, 1, 1, 2, 1, 5, 5, 8])        # figure
add_par([1, 1, 1, 1])                    # star
add_par([1, 2, 3])                       # path
add_par([1, 1, 3, 2, 4, 6, 2, 4])
add_par([1, 2, 1, 3, 4, 3, 5, 2, 4])

# ---------- small (brute.cpp searches every call schedule) ----------
add_par([1])
add_par([1, 2, 2, 1, 1, 5, 2, 7, 5, 6, 10, 10, 2])
add_par([1, 1, 3, 2, 5, 6, 6, 6, 8, 8, 11, 11])
add_par([1, 1, 2, 3, 1, 6, 2, 3, 1, 7, 5, 11])
add_par([1, 2, 1, 3, 5, 5, 5, 7, 7, 8, 9, 11])
add_par([1, 1, 3, 3, 5, 5, 7, 7, 8, 9, 11, 12, 12])
# ---------- medium ----------
add_tree(mixed(300, (2, 4), ("path", "bushy")))
add_tree(with_hub(mixed(1000), 600, 2000))
add_tree(mixed(5000, (2, 30)))

# ---------- big: one person with very many friends ----------
N = MAXN
add_tree(star(N))
add_tree(with_hub(rand_tree(40000), 155000, N))
add_tree(with_hub(path(40000), 158000, N))
add_tree(with_hub(binomial(15), 160000, N))
add_tree(star_of_stars(N, 4))
add_tree(star_of_stars(N, 2))
add_tree(with_hub(mixed(30000, (2, 3)), 165000, N))
add_tree(with_hub(mixed(20000, (2, 40)), 170000, N))
# ---------- big: no such person ----------
add_tree(path(N))
add_tree(rand_tree(N))
add_tree(binomial(17) + [random.randrange(1 << 17) for _ in range(N - (1 << 17))])
add_tree(mixed(N))
add_tree(mixed(N, (2, 3), ("path", "bushy")))
add_tree(mixed(N, (3, 200)))
add_tree(mixed(N, (2, 8), ("path", "bushy", "mix")))
add_tree(mixed(N, (2, 50)))
add_tree(star_of_stars(N, 3))                          # a few big hubs compete: call order matters
add_tree(star_of_stars(N, 9))
add_tree(mixed(N, (10, 100), ("bushy", "mix")))
add_tree(mixed(N, (2, 5), ("bushy",)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
