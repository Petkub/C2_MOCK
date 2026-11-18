# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Integer-only randomness (getrandbits), so every machine builds the same files.
import os, random

random.seed(116611)
MAXN, MAXQ, MAXX = 10 ** 9, 100000, 10 ** 9
tests = []


def ri(a, b):
    """uniform integer in [a, b] from getrandbits only"""
    k = b - a + 1
    bits = k.bit_length()
    while True:
        r = random.getrandbits(bits)
        if r < k:
            return a + r


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = ri(0, i)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def add(n, cmds):
    q = len(cmds)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    for l, r, x in cmds:
        assert 1 <= l <= r <= n and 1 <= x <= MAXX
    tests.append(f"{n} {q}\n" + "".join(f"{l} {r} {x}\n" for l, r, x in cmds))


def order(cmds, how):
    """reorder the commands (their numbers): keep, reverse, shuffle, local (small shifts), halves (interleave)"""
    if how == "keep":
        return list(cmds)
    if how == "reverse":
        return list(reversed(cmds))
    if how == "shuffle":
        return shuffled(cmds)
    if how == "local":
        c = list(cmds)
        for i in range(len(c) - 1):
            if ri(0, 2) == 0:
                j = min(len(c) - 1, i + ri(1, 3))
                c[i], c[j] = c[j], c[i]
        return c
    if how == "halves":
        h = len(cmds) // 2
        a, b = cmds[:h], cmds[h:]
        out = []
        for i in range(max(len(a), len(b))):
            if i < len(b):
                out.append(b[i])
            if i < len(a):
                out.append(a[i])
        return out
    raise ValueError(how)


def disjoint(q, n, x, gap):
    """q separate commands, the same X, gaps of `gap` lamps (0 = touching)"""
    w = (n - gap * (q - 1)) // q
    assert w >= 1
    out, p = [], 1
    for _ in range(q):
        out.append((p, p + w - 1, x))
        p += w + gap
    return out


def chain(q, n, d, xs):
    """command j covers pieces j .. j+d-1 of width s, so every inner piece lies under d neighbouring commands;
    X repeats with period d (xs), so every inner piece gets the same total"""
    s = n // (q + d)
    assert s >= 1
    return [(j * s + 1, (j + d) * s, xs[j % d]) for j in range(q)]


def heavy(cmds, k, x, n):
    """insert k commands over the whole street with X = x at random places in the middle half"""
    c = list(cmds)
    for _ in range(k):
        c.insert(ri(len(c) // 4, 3 * len(c) // 4), (1, n, x))
    return c


def leveled(q, n, k, base, xr, span, how):
    """k single-lamp peaks raised to the same total T by one top-up command each (placed by `how`);
    the other commands: `base` over the whole street (X up to 10^9) and random ones with X <= xr"""
    peaks = set()
    while len(peaks) < k:
        peaks.add(ri(1, n))
    peaks = sorted(peaks)
    other = [(1, n, ri(MAXX // 2, MAXX)) for _ in range(base)]
    for _ in range(q - k - base):
        l = ri(1, n)
        other.append((l, min(n, l + ri(0, span)), ri(1, xr)))
    # totals at the peaks, and the largest total anywhere, of the other commands
    import bisect
    diff = [0] * (k + 1)
    ev = []
    for l, r, x in other:
        diff[bisect.bisect_left(peaks, l)] += x
        diff[bisect.bisect_right(peaks, r)] -= x
        ev.append((l, x))
        ev.append((r + 1, -x))
    ev.sort()
    cur = top = 0
    for i, (p, x) in enumerate(ev):
        cur += x
        if i + 1 == len(ev) or ev[i + 1][0] != p:
            top = max(top, cur)
    tot, cur = [], 0
    for i in range(k):
        cur += diff[i]
        tot.append(cur)
    T = top + ri(1, 5)
    ups = [(p, p, T - t) for p, t in zip(peaks, tot)]
    other = shuffled(other)
    if how == "shuffle":
        return shuffled(other + ups)
    if how == "middle":       # the top-ups in the middle, in street order
        h = len(other) // 2
        return other[:h] + ups + other[h:]
    if how == "spread":       # the top-ups spread evenly, in street order
        out, j = [], 0
        for i, u in enumerate(ups):
            while j < len(other) and j * k < i * len(other):
                out.append(other[j])
                j += 1
            out.append(u)
        return out + other[j:]
    raise ValueError(how)


# samples
add(6, [(3, 3, 1), (4, 4, 1), (2, 5, 5), (6, 6, 1)])
add(6, [(1, 4, 2), (3, 6, 3), (2, 3, 1)])
add(8, [(4, 5, 1), (6, 6, 3), (7, 7, 3), (6, 8, 4)])
add(MAXN, [(1, MAXN, 600000000), (1, 500000000, 700000000), (400000000, MAXN, 700000000),
           (999999999, MAXN, 1)])
add(10, [(2, 3, 2), (9, 9, 3), (10, 10, 3), (7, 8, 3), (7, 7, 5), (9, 10, 5)])

# hidden: small (brute tries every block on these)
add(1, [(1, 1, 1)])
add(1, [(1, 1, MAXX)] * 3)
add(12, order(disjoint(4, 12, 3, 0), "shuffle"))                          # touching, all tied
add(20, order(chain(9, 20, 2, [2, 3]), "shuffle"))
add(30, leveled(12, 30, 4, 1, 3, 6, "shuffle"))
add(50, heavy(order(chain(30, 50, 3, [1, 5, 2]), "shuffle"), 2, MAXX, 50))
add(1000, leveled(250, 1000, 60, 3, 20, 80, "shuffle"))
add(MAXN, order(chain(300, MAXN, 2, [MAXX, MAXX]), "shuffle"))          # 2 * 10^9 exceeds int
add(600, order(disjoint(250, 600, 4, 1), "local"))

# hidden: big (q = 10^5)
Q = MAXQ
add(MAXN, disjoint(Q, MAXN, 7, 3))                                        # every block counts: Q(Q+1)/2
add(1000000, order(disjoint(Q, 1000000, MAXX, 0), "reverse"))            # touching, 10^9 each
add(MAXN, order(chain(Q, MAXN, 2, [3, 4]), "shuffle"))
add(MAXN, order(chain(Q, MAXN, 2, [1, 1]), "local"))
add(MAXN, order(chain(Q, MAXN, 3, [5, 1, 9]), "shuffle"))
add(MAXN, order(chain(Q, MAXN, 3, [2, 2, 2]), "halves"))
add(MAXN, order(chain(Q, MAXN, 5, [1, 2, 3, 4, 5]), "local"))
add(MAXN, heavy(order(chain(Q - 100, MAXN, 2, [6, 1]), "shuffle"), 100, MAXX, MAXN))       # M near 10^11
add(MAXN, heavy(order(disjoint(Q - 1000, MAXN, 1, 1), "local"), 1000, MAXX, MAXN))        # M near 10^12
add(MAXN, leveled(Q, MAXN, 60000, 0, 1000, 30000, "shuffle"))
add(MAXN, leveled(Q, MAXN, 60000, 50, 100, 10 ** 6, "middle"))
add(MAXN, leveled(Q, MAXN, 70000, 5, 1000, 3000, "spread"))
add(300000, leveled(Q, 300000, 65000, 0, 50, 20, "shuffle"))             # many peaks side by side
add(MAXN, order(chain(Q, MAXN, 4, [MAXX, 1, MAXX, 1]), "shuffle"))
add(MAXN, order(disjoint(Q, MAXN, 2, 0), "halves"))
add(MAXN, order(chain(Q, MAXN, 2, [1, 2]), "keep"))
add(MAXN, leveled(Q, MAXN, 60000, 20, 5, 100, "spread"))
add(200000, order(disjoint(Q, 200000, 9, 0), "shuffle"))                # every lamp has exactly one command

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
    assert len(t) <= 3 * 10 ** 6
assert 25 <= len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
