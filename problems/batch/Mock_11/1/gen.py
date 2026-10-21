# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1101)
MAXN, MAXM, MAXP, MAXW = 50000, 100000, 10, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(n, p, lights, us, vs, ws):
    m = len(us)
    assert 2 <= n <= MAXN and 1 <= m <= MAXM and 1 <= p <= MAXP and len(lights) == n
    assert len(vs) == m and len(ws) == m
    assert all(len(s) == p and set(s) <= {"0", "1"} for s in lights)
    assert 1 <= min(us) and max(us) <= n and 1 <= min(vs) and max(vs) <= n
    assert all(map(int.__ne__, us, vs)) and 1 <= min(ws) and max(ws) <= MAXW
    lines = [f"{n} {m} {p}", " ".join(lights)] + list(map("{} {} {}".format, us, vs, ws))
    tests.append("\n".join(lines) + "\n")


def add_list(n, p, lights, roads):
    """roads as (u, v, w) triples (samples)"""
    add(n, p, lights, *map(list, zip(*roads)))


POOL = {}


def rand_light(p, dens):
    """a light as a bit mask (bit r = green at remainder r), drawn from a pool of 2048 random masks"""
    if (p, dens) not in POOL:
        POOL[(p, dens)] = [sum(1 << r for r in range(p) if rnd() < dens) for _ in range(2048)]
    pool = POOL[(p, dens)]
    return pool[int(rnd() * 2048)]


def light_str(p):
    """text of every mask: character r is bit r"""
    return ["".join("1" if x >> r & 1 else "0" for r in range(p)) for x in range(1 << p)]


class Graph:
    """towns 0..n-1 while building, lights as bit masks; emit() relabels them
    (start -> 1, goal -> N, the rest shuffled)"""

    def __init__(self, p):
        self.p = p
        self.lt = []
        self.e = []

    def node(self, light=None, dens=0.5):
        self.lt.append(light if light is not None else rand_light(self.p, dens))
        return len(self.lt) - 1

    def green(self, v, r):
        self.lt[v] |= 1 << (r % self.p)

    def edge(self, u, v, w):           # (add() checks every road)
        self.e.append((u, v, w))

    def room(self):
        return MAXM - len(self.e)

    def emit(self, start, goal):
        n = len(self.lt)
        rest = [v for v in range(n) if v != start and v != goal]
        for i in range(len(rest) - 1, 0, -1):
            j = int(rnd() * (i + 1))
            rest[i], rest[j] = rest[j], rest[i]
        lab = [0] * n
        lab[start] = 1
        lab[goal] = n
        for i, v in enumerate(rest):
            lab[v] = i + 2
        text = light_str(self.p)
        lights = [""] * n
        for v, x in zip(lab, self.lt):
            lights[v - 1] = text[x]
        # roads in the order of a random key (the build order would show the structure)
        key = [rnd() for _ in self.e]
        order = sorted(range(len(self.e)), key=key.__getitem__)
        eu, ev, ew = zip(*self.e)
        add(n, self.p, lights, [lab[eu[i]] for i in order], [lab[ev[i]] for i in order], [ew[i] for i in order])


def weight_with(res, p, lo, hi):
    """a random weight in [lo, hi] that is = res (mod p)"""
    lo2 = lo + (res - lo) % p
    assert lo2 <= hi
    return lo2 + p * int(rnd() * ((hi - lo2) // p + 1))


def chain(p, hubs, k, dens, wlo=1, whi=MAXW, flood=0, noise=0, mid_dens=1.0, back=0):
    """hubs in a row; between two hubs k routes hub -> mid -> next hub. One route (planted) keeps a
    remainder that works all the way; the other k - 1 routes are shorter and arrive with other
    remainders (flood: that many extra short routes all arriving with the same wrong remainder).
    noise: random roads between towns of nearby gadgets; back: roads from a hub back to an earlier hub"""
    g = Graph(p)
    h = [g.node(dens=dens) for _ in range(hubs)]
    g.green(h[0], 0)
    r = 0                       # planted minute mod p at the current hub
    near = [[h[i]] for i in range(hubs)]       # towns of gadget i (its first hub and its mid towns)
    for i in range(hubs - 1):
        a, b = h[i], h[i + 1]
        r2 = int(rnd() * p)
        g.green(b, r2)
        span = whi - wlo
        W = weight_with(r2 - r, p, wlo + span // 2, whi)            # planted total
        routes = [(W, True)]
        for _ in range(k - 1):
            routes.append((ri(max(2, wlo), max(2, W - 1)), False))     # shorter decoys
        if flood and p > 1:
            bad = (r2 + ri(1, p - 1)) % p
            for _ in range(flood):
                routes.append((weight_with(bad - r, p, max(2, wlo), max(2 + p, W - 1)), False))
        for tot, planted in routes:
            tot = max(tot, 2)
            w1 = ri(1, tot - 1)
            md = g.node(dens=mid_dens)
            g.green(md, r + w1)
            if planted:
                g.green(a, r)
            g.edge(a, md, w1)
            g.edge(md, b, tot - w1)
            near[i].append(md)
        r = (r + W) % p
    for _ in range(back):
        if g.room() < 1:
            break
        i = ri(1, hubs - 1)
        j = ri(max(0, i - 20), i - 1)
        g.edge(h[i], h[j], ri(1, max(1, whi // 50)))
    for _ in range(noise):
        if g.room() < 1:
            break
        i = int(rnd() * hubs)
        j = min(hubs - 1, max(0, i + ri(-2, 2)))
        u = near[i][int(rnd() * len(near[i]))]
        v = near[j][int(rnd() * len(near[j]))]
        if u != v and v != h[0] and u != h[-1]:
            g.edge(u, v, ri(wlo, whi))
    g.emit(h[0], h[-1])


def planted_random(p, n, m, dens, plen, wlo=1, whi=MAXW, goal_in=3, flood=0, start_red=False):
    """random roads and lights, plus one planted walk from 1 to N whose remainders work;
    the goal can be entered only from a few towns. flood: on every planted step that many shorter
    parallel roads, all arriving with the same wrong remainder"""
    g = Graph(p)
    for _ in range(n):
        g.node(dens=dens)
    start, goal = 0, n - 1
    walk = [start] + [ri(1, n - 2) for _ in range(plen - 1)] + [goal]
    t = 0
    for a, b in zip(walk, walk[1:]):
        if a == b:
            continue
        g.green(a, t)
        w = ri(max(wlo, p + 2), whi)
        g.edge(a, b, w)
        if flood and p > 1:
            bad = (t + w + ri(1, p - 1)) % p
            for _ in range(flood):
                g.edge(a, b, weight_with(bad - t, p, 1, w - 1))
        t += w
    if start_red:
        g.lt[start] &= ~1
    into = [ri(1, n - 2) for _ in range(goal_in)]
    while len(g.e) < m:
        u, v = int(rnd() * n), int(rnd() * n)
        if v == goal and u not in into:
            continue
        if u != v and u != goal:
            g.edge(u, v, ri(wlo, whi))
    g.emit(start, goal)


def loops(p, units, dens=0.3, whi=MAXW):
    """each unit: hub a (green at the planted remainder), a small cycle a -> x -> y -> a that shifts the
    remainder, a direct road a -> b that only works after going round the cycle a certain number of times"""
    g = Graph(p)
    a = g.node(dens=dens)
    start = a
    r = 0
    g.green(a, 0)
    for _ in range(units):
        x = g.node((1 << p) - 1)
        y = g.node((1 << p) - 1)
        c = weight_with(ri(1, p - 1), p, 3, whi // 4)               # cycle length, not = 0 mod p
        c1 = ri(1, c - 2)
        c2 = ri(1, c - c1 - 1)
        g.edge(a, x, c1)
        g.edge(x, y, c2)
        g.edge(y, a, c - c1 - c2)
        turns = ri(1, p - 1)
        r_dep = (r + turns * c) % p
        for j in range(turns + 1):                                  # a is green on the way round
            g.green(a, r + j * c)
        b = g.node(dens=dens)
        w = ri(1, whi)
        g.edge(a, b, w)
        r = (r_dep + w) % p
        g.green(b, r)
        a = b
    g.emit(start, a)


def dead_end(p, n, m, dens, whi=MAXW, gate_in=0):
    """random roads where waiting would always help; the goal is entered from one town only (the gate),
    which is green at a single remainder; gate_in extra roads lead into the gate"""
    g = Graph(p)
    for _ in range(n):
        g.node(dens=dens)
    gate = 1
    g.lt[gate] = 1 << int(rnd() * p)
    g.green(0, 0)
    g.edge(gate, n - 1, ri(1, whi))
    for _ in range(gate_in):
        g.edge(ri(2, n - 2), gate, ri(1, whi))
    for _ in range(20):         # a few ways out of the start
        g.edge(0, ri(2, n - 2), ri(1, whi))
    while len(g.e) < m:
        u, v = int(rnd() * n), int(rnd() * n)
        if u != v and u != n - 1 and v != n - 1:
            g.edge(u, v, ri(1, whi))
    g.emit(0, n - 1)


# samples
add_list(4, 3, ["100", "001", "001", "000"], [(1, 2, 1), (1, 3, 2), (3, 2, 3), (2, 4, 2), (1, 4, 10)])
add_list(4, 2, ["11", "10", "01", "00"], [(1, 2, 1), (1, 3, 1), (3, 1, 2), (2, 4, 5)])
add_list(2, 4, ["0111", "0000"], [(1, 2, 3)])
add_list(4, 4, ["1000", "0001", "0001", "0000"],
    [(1, 2, 10 ** 9), (1, 2, 999999999), (2, 3, 10 ** 9), (3, 4, 10 ** 9), (1, 3, 1)])
add_list(3, 3, ["100", "010", "000"], [(1, 2, 2), (2, 3, 1), (2, 1, 1)])
# hidden: small (brute checks these)
add_list(2, 1, ["1", "0"], [(1, 2, MAXW)])
chain(5, 6, 3, 0.4, whi=30)
chain(7, 40, 3, 0.3, whi=1000, flood=8, back=10)
loops(10, 30, whi=10 ** 4)
planted_random(6, 300, 900, 0.35, 15, whi=100, flood=7)
dead_end(8, 200, 600, 0.6, gate_in=10)
chain(10, 300, 3, 0.25, flood=12, noise=200)
# hidden: big
chain(10, 12000, 3, 0.3, noise=4000)
chain(10, 9000, 4, 0.2, noise=10000, back=5000)
chain(10, 3500, 2, 0.3, flood=11, noise=5000)
chain(10, 16000, 2, 0.15, back=30000)
chain(7, 10000, 3, 0.4, flood=1, noise=8000, back=8000)
chain(10, 12000, 3, 0.3, wlo=MAXW // 2, noise=3000)
chain(3, 15000, 2, 0.5, noise=15000)
chain(2, 16000, 2, 0.5, noise=20000)
loops(10, 16000)
loops(6, 16000, dens=0.6)
planted_random(10, MAXN, MAXM, 0.3, 2000, flood=11)
planted_random(10, MAXN, MAXM, 0.5, 400, wlo=10 ** 8, flood=12)
planted_random(8, MAXN, MAXM, 0.2, 5000, whi=1000, flood=9)
planted_random(9, MAXN, MAXM, 0.4, 3000, whi=10 ** 6, flood=4, start_red=True)
planted_random(1, 20000, 40000, 0.7, 200)
planted_random(10, MAXN, MAXM, 1.0, 300)
dead_end(10, MAXN, MAXM, 0.75, gate_in=40)
dead_end(5, MAXN, MAXM, 0.8, whi=10 ** 6, gate_in=20)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
