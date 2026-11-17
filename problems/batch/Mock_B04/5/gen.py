# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
# Every bulb of a group is a[v] = s[v] * t + c[v] (s = +-1) for the value t of one bulb; an odd cycle pins t
# (2t = k needs k even), so the big tests mix: one huge free group (the best t moves after every change), huge
# pinned groups, many small groups, infeasible wires (only a parity clash, only a sum clash on an even cycle),
# and chains whose c[v] grows far beyond 2^31.
import os, random

random.seed(7121)
rnd = random.random
MAXN = MAXM = MAXQ = 30000
V = 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(rng, wires, qs, mix=True):
    """rng: list of (l, r); wires: list of (x, y, z) 1-based; qs: list of (p, l, r); mix: shuffle the wires"""
    n, m, q = len(rng), len(wires), len(qs)
    assert 1 <= n <= MAXN and 0 <= m <= MAXM and 1 <= q <= MAXQ
    for l, r in rng:
        assert -V <= l <= r <= V
    for x, y, z in wires:
        assert 1 <= x <= n and 1 <= y <= n and -V <= z <= V
    for p, l, r in qs:
        assert 1 <= p <= n and -V <= l <= r <= V
    wires = list(wires)
    if mix:
        wires.sort(key=lambda w: rnd())
        wires = [(y, x, z) if rnd() < 0.5 else (x, y, z) for x, y, z in wires]
    lines = [f"{n} {m} {q}"] + [f"{l} {r}" for l, r in rng] + [f"{x} {y} {z}" for x, y, z in wires]
    lines += [f"{p} {l} {r}" for p, l, r in qs]
    tests.append("\n".join(lines) + "\n")


def clamp(v):
    return max(-V, min(V, v))


def rg_around(a, w):
    """a range of width about w holding a (clamped to [-V, V])"""
    lo, hi = clamp(a - ri(0, w)), clamp(a + ri(0, w))
    return (lo, hi) if lo <= hi else (a, a) if -V <= a <= V else rand_rg(w)


LIM = V          # rand_rg draws inside [-LIM, LIM]; the small tests lower it so brute.cpp can check them


def rand_rg(w, lim=None):
    lim = LIM if lim is None else lim
    l = ri(-lim, lim)
    return (l, min(lim, l + ri(0, w)))


def tree_edges(n, shape):
    """parent list of a tree on 0..n-1 (root 0); the nodes are relabelled randomly later"""
    if shape == "path":
        return [(i - 1, i) for i in range(1, n)]
    if shape == "star":
        return [(0, i) for i in range(1, n)]
    if shape == "cater":
        sp = max(2, n // 10)
        return [(i - 1, i) for i in range(1, sp)] + [(ri(0, sp - 1), i) for i in range(sp, n)]
    if shape == "deep":
        return [(max(0, i - ri(1, 3)), i) for i in range(1, n)]
    return [(ri(max(0, i - 50), i - 1) if rnd() < 0.5 else ri(0, i - 1), i) for i in range(1, n)]


def group(n, shape, amp, extra, pin, base=0):
    """one connected group on nodes base..base+n-1 with hidden values a (|a| <= amp so every z fits):
    tree wires, `extra` more wires inside even cycles, and with pin an odd cycle (all consistent with a)"""
    a = [ri(-amp, amp) for _ in range(n)]
    col = [0] * n
    es = []
    for p, v in tree_edges(n, shape):
        col[v] = col[p] ^ 1
        es.append((p, v))
    side = [[v for v in range(n) if col[v] == k] for k in range(2)]
    for _ in range(extra):
        if side[0] and side[1]:
            es.append((side[0][ri(0, len(side[0]) - 1)], side[1][ri(0, len(side[1]) - 1)]))
    if pin:
        x = ri(0, n - 1)
        same = side[col[x]]
        es.append((x, same[ri(0, len(same) - 1)]))
    return a, col, [(base + x + 1, base + y + 1, a[x] + a[y]) for x, y in es]


def relabel(rng, wires, qs, keep_first=False):
    n = len(rng)
    perm = list(range(n))
    random.shuffle(perm)
    if keep_first:
        i = perm.index(0)
        perm[0], perm[i] = perm[i], perm[0]
    nr = [None] * n
    for i in range(n):
        nr[perm[i]] = rng[i]
    w2 = [(perm[x - 1] + 1, perm[y - 1] + 1, z) for x, y, z in wires]
    q2 = [(perm[p - 1] + 1, l, r) for p, l, r in qs]
    return nr, w2, q2


def ranges_for(a, col, hit, w, shift):
    """bulb v lights at the hidden values with chance hit; else its range sits where t is moved by about
    +-shift, so the best t is a real choice"""
    out = []
    for v in range(len(a)):
        if rnd() < hit:
            out.append(rg_around(a[v], w))
        else:
            d = ri(-shift, shift)
            out.append(rg_around(clamp(a[v] + (d if col[v] == 0 else -d)), w))
    return out


def queries_for(a, col, q, w, shift, nodes=None, hit=0.4, base=0):
    qs = []
    n = len(a)
    for _ in range(q):
        v = nodes[ri(0, len(nodes) - 1)] if nodes else ri(0, n - 1)
        u = rnd()
        if u < hit:
            l, r = rg_around(a[v], w)
        elif u < 0.9:
            d = ri(-shift, shift)
            l, r = rg_around(clamp(a[v] + (d if col[v] == 0 else -d)), w)
        else:
            l, r = rand_rg(w)
        qs.append((base + v + 1, l, r))
    return qs


def big_group(n, m, q, shape, amp, pin, hit, w, shift, qhit=0.4):
    a, col, ws = group(n, shape, amp, m - (n - 1) - (1 if pin else 0), pin)
    rng = ranges_for(a, col, hit, w, shift)
    qs = queries_for(a, col, q, w, shift, hit=qhit)
    return relabel(rng, ws, qs)


def many_groups(n, q, sizes, amp, pin_p, hit, w, shift, extra_p=0.3, bad=None):
    """groups of random sizes from `sizes`; bad: None, 'parity' (one odd 2t = k) or 'sum' (one even cycle off by 1)"""
    rng, ws, A, C = [], [], [], []
    base = 0
    while base < n:
        k = min(n - base, ri(*sizes))
        room = MAXM - 2 - len(ws) - (n - base)          # keep space for the tree wires still to come
        a, col, gw = group(k, "rand", amp, max(0, min(room, int(k * extra_p * rnd()))), rnd() < pin_p, base)
        rng += ranges_for(a, col, hit, w, shift)
        ws += gw
        A += a
        C += col
        base += k
    qs = queries_for(A, C, q, w, shift)
    spoil(ws, A, C, bad)
    return relabel(rng, ws, qs)


def merge(*parts):
    """put several instances side by side (labels of a later part come after the earlier ones), mix the queries"""
    rng, ws, qs = [], [], []
    for r, w, q in parts:
        b = len(rng)
        rng += r
        ws += [(x + b, y + b, z) for x, y, z in w]
        qs += [(p + b, l, r2) for p, l, r2 in q]
    qs.sort(key=lambda _: rnd())
    return rng, ws, qs


def spoil(ws, a, col, bad):
    """make the wires infeasible in one way only (a, col: hidden values and 2-colouring, 0-based)"""
    if bad is None:
        return
    n = len(a)
    for _ in range(1000):
        x, y = ri(0, n - 1), ri(0, n - 1)
        if bad == "parity" and abs(a[x] + a[y] + 1) <= V:
            # a 3rd wire between x and y would make 2t odd only if x, y are in one group with the same colour:
            # use a self-loop on x instead, which always pins with an odd total
            ws.append((x + 1, x + 1, 2 * a[x] + 1) if abs(2 * a[x] + 1) <= V else (x + 1, x + 1, 1))
            return
        if bad == "sum":
            # a wire parallel to an existing tree wire, off by one: an even cycle (length 2) whose sums clash
            for i in range(len(ws)):
                u, v, z = ws[ri(0, len(ws) - 1)]
                if u != v and abs(z + 1) <= V:
                    ws.append((u, v, z + 1))
                    return
    raise AssertionError("spoil failed")


def overflow_chain(n, q, mid, pin):
    """bulb 1 starts a path of `mid` bulbs whose hidden values shrink by 4.9 * 10^8 per step (alternating sign)
    down to 0, then a big tree with small hidden values hangs from the end of the path. Measured from bulb 1
    (label 1 is kept), c[v] of the tree is about mid * 4.9 * 10^8, far beyond 2^31. With pin, an odd cycle in
    the tree fixes t."""
    D = 49 * 10 ** 7
    if pin:
        n -= 3                           # room for the 3 extra wires
    a = [(-1) ** k * (mid - 1 - k) * D for k in range(mid)]
    col = [k % 2 for k in range(mid)]
    ws = [(k, k + 1, a[k - 1] + a[k]) for k in range(1, mid)]
    for v in range(mid, n):
        p = mid - 1 if rnd() < 0.05 or v == mid else ri(max(mid - 1, v - 30), v - 1)
        a.append(ri(-10 ** 8, 10 ** 8))
        col.append(col[p] ^ 1)
        ws.append((p + 1, v + 1, a[p] + a[v]))
    if pin:
        for _ in range(3):
            x = ri(mid, n - 1)
            same = [v for v in range(x - 40, x) if v >= mid and col[v] == col[x]]
            if same:
                y = same[ri(0, len(same) - 1)]
                ws.append((x + 1, y + 1, a[x] + a[y]))
    for x, y, z in ws:
        assert abs(z) <= V
    rng, qs = [], []
    for v in range(n):
        rng.append(rg_around(a[v], 10 ** 6) if abs(a[v]) <= V and rnd() < 0.6 else rand_rg(ri(0, 2 * V)))
    for _ in range(q):
        v = ri(0, n - 1)
        qs.append((v + 1,) + (rg_around(a[v], 10 ** 6) if abs(a[v]) <= V and rnd() < 0.5 else rand_rg(ri(0, 2 * V))))
    return relabel(rng, ws, qs, keep_first=True)


# samples
add([(1, 3), (2, 5), (0, 0), (-2, 4)], [(1, 2, 5), (2, 3, 4), (4, 4, 6)], [(3, 5, 6), (4, 4, 9), (4, 2, 3)], False)
add([(0, 2), (0, 1), (5, 6), (-4, -3)], [(1, 2, 3), (2, 3, 5), (3, 4, 2), (4, 1, 0)], [(1, 3, 3), (3, 0, 1)], False)
add([(0, 9), (0, 9), (5, 5)], [(1, 2, 4), (2, 1, 5)], [(3, 1, 1), (1, 2, 2)], False)
add([(-1000000000, 1000000000), (-1000000000, 0), (0, 0), (500000000, 500000000)],
    [(1, 2, 500000000), (2, 3, -500000000), (3, 4, 500000000)],
    [(1, 500000000, 500000000), (2, -5, 5), (3, -500000000, -500000000)], False)
# hidden: small (brute checks these)
add([(5, 5)], [], [(1, 6, 6)])
add([(0, 0)], [(1, 1, 1)], [(1, -3, 3)])
add([(2, 2), (2, 2)], [(1, 2, 4), (1, 1, 4), (2, 2, 4)], [(1, 1, 3), (2, 3, 3)])
LIM = 12
for sd in range(3):
    add(*many_groups(8, 8, (1, 5), 6, 0.5, 0.5, 4, 5))
add(*many_groups(9, 6, (3, 9), 5, 0.0, 0.4, 3, 6, 0.6, "parity"))
add(*many_groups(40, 40, (5, 15), 8, 0.5, 0.5, 6, 8, 0.4))
LIM = V
add(*many_groups(12000, 12000, (3000, 12000), 10 ** 8, 0.0, 0.5, 10 ** 6, 10 ** 7, 0.3, "parity"))
add(*many_groups(12000, 12000, (1, 3000), 10 ** 8, 0.5, 0.5, 10 ** 6, 10 ** 7, 0.3, "parity"))
add(*many_groups(12000, 12000, (2000, 12000), 10 ** 8, 0.0, 0.5, 10 ** 6, 10 ** 7, 0.5, "sum"))
# hidden: big (N = Q = 30000)
N, Q = MAXN, MAXQ
add(*big_group(N, N - 1, Q, "path", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6))
add(*big_group(N, N - 1, Q, "path", 4 * 10 ** 8, False, 0.3, 10 ** 8, 4 * 10 ** 7, 0.2))
add(*big_group(N, MAXM, Q, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6))
add(*big_group(N, MAXM, Q, "star", 10 ** 7, False, 0.4, 10 ** 4, 10 ** 5))
add(*big_group(N, N - 1, Q, "cater", 10 ** 7, False, 0.6, 10 ** 4, 10 ** 5, 0.3))
add(*big_group(N, N - 1, Q, "deep", 10 ** 3, False, 0.2, 30, 300, 0.2))   # many ties of t
# a huge pinned group next to a huge free group (the queries hit both)
add(*merge(big_group(15000, 15000, 15000, "rand", 10 ** 7, True, 0.5, 10 ** 5, 10 ** 6),
           big_group(15000, 14999, 15000, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))
add(*merge(big_group(15000, 15000, 15000, "path", 10 ** 7, True, 0.6, 10 ** 5, 10 ** 6),
           big_group(15000, 14999, 15000, "cater", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))
add(*merge(many_groups(12000, 12000, (1, 8), 10 ** 7, 0.5, 0.5, 10 ** 5, 10 ** 6, 0.0),
           big_group(18000, 17999, 18000, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))
add(*many_groups(N, Q, (100, 3000), 10 ** 7, 0.6, 0.4, 10 ** 5, 10 ** 6))
add(*overflow_chain(N, Q, 60, False))
add(*overflow_chain(N, Q, 200, False))
add(*merge(overflow_chain(18000, 15000, 120, True),
           big_group(12000, 11999, 15000, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))
add(*overflow_chain(N, Q, 9, False))
add(*overflow_chain(N, Q, 1000, False))
add(*merge(overflow_chain(18000, 15000, 30, True),
           big_group(12000, 11999, 15000, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))
add(*merge(overflow_chain(18000, 15000, 600, True),
           big_group(12000, 11999, 15000, "rand", 10 ** 7, False, 0.5, 10 ** 5, 10 ** 6)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
