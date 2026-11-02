# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(850505)
MAXN, MAXR, MAXK, MAXV, MAXLEN = 50000, 50000, 250000, 10 ** 9, 3000000
tests = []


def add(price, recipes):
    """price[1..n] (price[0] unused); recipes: list of (target, fee, [ingredients])"""
    n, r = len(price) - 1, len(recipes)
    assert 1 <= n <= MAXN and 1 <= r <= MAXR
    assert all(1 <= p <= MAXV for p in price[1:])
    assert sum(len(x[2]) for x in recipes) <= MAXK
    lines = [f"{n} {r}", " ".join(map(str, price[1:]))]
    for t, f, ing in recipes:
        assert 1 <= t <= n and 0 <= f <= MAXV and len(ing) >= 1
        assert len(set(ing)) == len(ing) and all(1 <= x <= n for x in ing)
        lines.append(f"{t} {f} {len(ing)} " + " ".join(map(str, ing)))
    text = "\n".join(lines) + "\n"
    assert len(text) <= MAXLEN, len(text)
    tests.append(text)


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def pick(pool, k):
    """k distinct elements of pool (k small: retry on repeats)"""
    out = set()
    res = []
    while len(res) < k:
        x = pool[ri(0, len(pool) - 1)]
        if x not in out:
            out.add(x)
            res.append(x)
    return res


class Shop:
    def __init__(self, n):
        self.n = n
        self.price = [0] + [MAXV] * n
        self.rec = []
        self.ids = list(range(1, n + 1))
        random.shuffle(self.ids)
        self.next = 0

    def take(self, k):
        """k fresh item numbers (random)"""
        s = self.ids[self.next:self.next + k]
        assert len(s) == k
        self.next += k
        return s

    def chain(self, L, order, base):
        """items u_1..u_L, u_(j+1) is made from u_j for 1 coin, price of u_j = base + 2j: crafting along the
        chain always wins, the cost of u_j is base + j + 1. Item numbers fall along the chain. Returns the items
        in chain order."""
        u = sorted(self.take(L), reverse=True)
        for j in range(L):
            self.price[u[j]] = base + 2 * (j + 1)
        rs = [(u[j + 1], 1, [u[j]]) for j in range(L - 1)]
        if order == "rev":
            rs.reverse()
        else:
            random.shuffle(rs)
        self.rec += rs
        return u

    def mesh(self, items, R, kmin, kmax, pool, fee_hi, self_p=0.03, budget=MAXK):
        """R recipes for targets among items (several per item), ingredients from pool (+ maybe the target);
        stops early when the ingredient lists would exceed `budget` entries"""
        for _ in range(R):
            t = items[ri(0, len(items) - 1)]
            k = ri(kmin, kmax)
            if k > budget:
                break
            budget -= k
            ing = pick(pool, k)
            if t not in ing and random.random() < self_p:
                ing[ri(0, len(ing) - 1)] = t
            self.rec.append((t, ri(0, fee_hi), ing))


def shuffled(xs):
    xs = xs[:]
    random.shuffle(xs)
    return xs


def big_all(L, nbig, kbig, order, R_mesh, kmesh, fee_hi):
    """a long chain, `nbig` recipes that use the first kbig chain items (cheapest first), a random cyclic mesh"""
    sh = Shop(MAXN)
    base = ri(10 ** 7, 10 ** 8)
    u = sh.chain(L, order, base)
    rest = sh.take(MAXN - L)
    leaves, craft = rest[:len(rest) // 3], rest[len(rest) // 3:]
    for x in leaves:
        sh.price[x] = ri(1, 10 ** 6)
    for x in craft:
        sh.price[x] = ri(10 ** 8, MAXV)
    for _ in range(nbig):
        t = craft[ri(0, len(craft) - 1)]
        sh.price[t] = MAXV
        sh.rec.append((t, ri(0, 10 ** 6), u[:kbig]))
    budget = MAXK - (L - 1) - nbig * kbig
    R = min(MAXR - len(sh.rec), R_mesh)
    sh.mesh(craft, R, 1, kmesh, craft + leaves + u[-200:], fee_hi, budget=budget)
    recs = sh.rec
    if order == "rand":
        recs = shuffled(recs)
    return sh.price, recs


def mesh_only(n, R, kmin, kmax, leaf_frac, leaf_hi, craft_lo, fee_hi, self_p=0.03):
    sh = Shop(n)
    ids = sh.take(n)
    nl = max(1, int(n * leaf_frac))
    leaves, craft = ids[:nl], ids[nl:]
    for x in leaves:
        sh.price[x] = ri(1, leaf_hi)
    for x in craft:
        sh.price[x] = ri(craft_lo, MAXV)
    sh.mesh(craft, R, kmin, kmax, ids, fee_hi, self_p)
    return sh.price, sh.rec


# samples
add([0, 5, 3, 20, 15], [(3, 2, [1, 2]), (4, 1, [3]), (3, 10, [4])])
add([0, 100, 4, 7], [(1, 0, [2, 3]), (2, 1, [1]), (3, 5, [3, 2])])
add([0, 1000000000, 1000000000, 1000000000, 1], [(1, 0, [2, 3, 4]), (2, 0, [4]), (3, 999999999, [4])])
add([0, 8], [(1, 0, [1])])
add([0, 50, 6, 6, 40, 30, 2],
    [(1, 5, [4, 5]), (4, 1, [2, 3, 6]), (5, 3, [4]), (2, 0, [6, 3]), (1, 20, [2, 3, 6]), (6, 4, [1])])
# hidden: small (brute checks these)
add([0, 7], [(1, 3, [1])])
add([0, 10, 1], [(1, 0, [2]), (2, 0, [1])])
add([0] + [1000000000] * 6, [(1, 1000000000, [2, 3, 4, 5, 6]), (2, 0, [3]), (6, 0, [1])])
add(*mesh_only(10, 15, 1, 3, 0.3, 50, 30, 10))
add(*mesh_only(60, 120, 1, 4, 0.2, 1000, 500, 100, 0.1))
add(*mesh_only(300, 900, 1, 5, 0.1, 10 ** 6, 10 ** 8, 10 ** 4))
add(*mesh_only(3000, 6000, 1, 3, 0.05, 10 ** 9, 10 ** 9, 0, 0.05))       # prices near 10^9, free recipes
sh = Shop(3000)                                                   # a chain, a big recipe, a mesh
u = sh.chain(1500, "rand", 1000)
rest = sh.take(1500)
for x in rest:
    sh.price[x] = ri(10 ** 6, MAXV)
sh.mesh(rest, 3000, 1, 4, rest + u, 1000)
sh.rec.append((rest[0], 0, u[:1500]))
add(sh.price, shuffled(sh.rec))
# hidden: big
N = MAXN
add(*big_all(46000, 4, 46000, "rev", 3000, 6, 10 ** 6))
add(*big_all(46000, 4, 46000, "rand", 3000, 6, 10 ** 6))
add(*big_all(45000, 4, 45000, "rev", 4000, 6, 10 ** 4))
add(*big_all(45000, 4, 45000, "rand", 4000, 6, 10 ** 9))
add(*big_all(40000, 5, 40000, "rev", 7000, 3, 10 ** 6))
add(*big_all(40000, 5, 40000, "rand", 7000, 3, 100))
add(*big_all(48000, 4, 48000, "rand", 2000, 6, 1000))
add(*big_all(35000, 6, 35000, "rand", 10000, 4, 10 ** 6))
add(*big_all(30000, 7, 30000, "rev", 15000, 3, 10 ** 6))
add(*big_all(44000, 4, 44000, "rand", 5000, 4, 0))
add(*big_all(47000, 4, 47000, "rev", 2500, 6, 10 ** 7))
add(*big_all(49000, 4, 49000, "rev", 0, 1, 0))                     # only the chain and the big recipes
add(*big_all(49000, 4, 49000, "rand", 0, 1, 0))
add(*mesh_only(N, MAXR, 2, 6, 0.3, MAXV, 9 * 10 ** 8, 10 ** 9))     # sums above 2^31
add(*mesh_only(N, MAXR, 1, 3, 0.1, MAXV, 1, 0, 0.2))              # free recipes, many use their own target
sh = Shop(N)                                                      # a chain plus big recipes in random order
u = sh.chain(40000, "rev", 10 ** 6)
rest = sh.take(N - 40000)
for x in rest:
    sh.price[x] = MAXV
for t in rest[:4]:
    sh.rec.append((t, 0, shuffled(u)))
sh.mesh(rest, 9000, 1, 4, rest + u[-100:], 10 ** 6, budget=MAXK - 5 * 40000)
add(sh.price, shuffled(sh.rec))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
