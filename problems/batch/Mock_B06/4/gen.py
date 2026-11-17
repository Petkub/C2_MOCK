# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Big tests: deep chains (type 1 keeps a copy of itself at one end of its string, so the queries near that end
# walk through every night and scan every string), random growth that passes 2^63 within a few nights
# (lengths must be capped), positions up to 10^18 with fine-grained types (doubles lose the exact position),
# renaming chains, many different query types.
import os, random

random.seed(7243)
rnd = random.random
MAXN, MAXSUM, MAXT, MAXQ, MAXP = 200000, 200000, 100000, 500, 10 ** 18
CAP = 4 * 10 ** 18
tests = []


def ri(a, b):
    return random.randint(a, b)


def pick(seq):
    return seq[int(rnd() * len(seq))]


def final_len(ops, t0=1):
    """length of the final row (capped at CAP), started from one cell of type t0"""
    L = {}
    for c, s in reversed(ops):
        L[c] = min(CAP, sum(L.get(y, 1) for y in s))
    return L.get(t0, 1)


def final_lens(ops, types):
    L = {}
    for c, s in reversed(ops):
        L[c] = min(CAP, sum(L.get(y, 1) for y in s))
    return [L.get(t, 1) for t in types]


def add(ops, qs):
    n, q = len(ops), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert sum(len(s) for c, s in ops) <= MAXSUM
    for c, s in ops:
        assert 1 <= c <= MAXT and len(s) >= 1 and all(1 <= y <= MAXT for y in s)
    R = min(final_len(ops), MAXP)
    for l, r, x in qs:
        assert 1 <= l <= r <= R and 1 <= x <= MAXT, (l, r, R, x)
    lines = [f"{n} {q}"]
    lines += [f"{c} {len(s)} " + " ".join(map(str, s)) for c, s in ops]
    lines += [f"{l} {r} {x}" for l, r, x in qs]
    tests.append("\n".join(lines) + "\n")


def queries(ops, q, xs, style="mix", R=None):
    """q queries with types from xs; styles: mix (random, near ends, single cells, whole range), end (r near the end)"""
    if R is None:
        R = min(final_len(ops), MAXP)
    qs = []
    for j in range(q):
        x = pick(xs)
        k = j % 6 if style == "mix" else 5
        if k == 0:                                   # random range
            a, b = ri(1, R), ri(1, R)
            l, r = min(a, b), max(a, b)
        elif k == 1:                                 # whole row (or first 10^18 cells)
            l, r = ri(1, min(R, 3)), R
        elif k == 2:                                 # one cell
            l = r = ri(1, R)
        elif k == 3:                                 # a short range somewhere
            l = ri(1, R)
            r = min(R, l + ri(0, 1000))
        elif k == 4:                                 # starts at 1
            l, r = 1, ri(1, R)
        else:                                        # both ends in the last part of the row
            w = max(1, R // ri(50, 5000))
            a, b = ri(max(1, R - w), R), ri(max(1, R - w), R)
            l, r = max(1, min(a, b)), max(a, b)
        qs.append((l, r, x))
    return qs


def growth_ops(n, total, types, keep=0.9, kmax=4, extra=None):
    """random nights; the replaced type is usually one that is in the row (tracked in plist / pos)"""
    ops, used = [], 0
    plist, pos = [1], {1: 0}

    def put(y):
        if y not in pos:
            pos[y] = len(plist)
            plist.append(y)

    def drop(y):
        i = pos.pop(y)
        last = plist.pop()
        if last != y:
            plist[i] = last
            pos[last] = i

    while len(ops) < n and used < total:
        c = pick(plist) if rnd() < keep else pick(types)
        room = total - used - (n - len(ops) - 1)
        k = max(1, min(ri(1, kmax), room))
        s = [pick(types) for _ in range(k)]
        if extra is not None:
            s = extra(c, s)
        ops.append((c, s))
        used += len(s)
        if c in pos:
            drop(c)
            for y in s:
                put(y)
    return ops


def filler(types, limit, base):
    """nights over `types` (base excluded) until every type's expansion is long but at most limit"""
    ops = []
    while True:
        c = pick(types)
        s = [pick(types) for _ in range(ri(2, 3))]
        L = max(final_lens(ops + [(c, s)], types))
        if L > limit:
            if len(ops) >= 5:
                return ops
            continue
        ops.append((c, s))
        if len(ops) >= 600:
            return ops


HUGE = 99999


def deep_chain(m, k, front, types, q, xs=None, fill_types=None):
    """night 1: 1 -> 1 HUGE (HUGE grows past 2^64, after position 10^18); then m nights 1 -> [k types] + [1]
    (or [1] + [k types]); then nights that make the other types long. Deep queries stay before HUGE."""
    if m is None:
        m = (MAXSUM - 2400) // (k + 1)
    ops = []
    for _ in range(m):
        s = [pick(types) for _ in range(k)]
        ops.append((1, [1] + s if front else s + [1]))
    lim = MAXP // (m * k + 1)
    ops += filler(fill_types or types, lim, 1)
    R = min(final_len(ops), MAXP)
    ops = [(1, [1, HUGE])] + ops + [(HUGE, [HUGE, HUGE])] * 70
    xs = xs or ([1] + types)
    qs = queries(ops, q, xs, "end" if not front else "mix", R)
    if front:   # deep queries are the ones near the start
        qs = [(ri(1, 50), ri(1, max(1, R // 10 ** 6)), pick(xs)) for _ in range(q // 2)] + qs[:q - q // 2]
    return ops, qs


# ---------------- samples ----------------
tests.append("3 3\n1 2 1 2\n2 2 3 1\n1 2 2 3\n1 5 3\n2 4 2\n1 1 1\n")
tests.append("4 3\n3 2 1 1\n1 3 3 2 3\n3 1 4\n2 2 4 1\n2 4 4\n2 3 1\n1 4 2\n")
tests.append("6 4\n1 4 1 2 1 2\n2 3 3 1 3\n1 4 2 1 1 3\n3 2 2 3\n1 3 1 1 1\n2 2 1 4\n"
             "1 56 1\n1 56 4\n7 40 3\n30 30 2\n")
tests.append("8 3\n1 9 2 2 2 2 2 2 2 2 3\n2 9 3 3 3 3 3 3 3 3 4\n3 9 4 4 4 4 4 4 4 4 1\n"
             "4 9 1 1 1 1 1 1 1 1 2\n1 9 5 5 5 5 2 2 2 2 3\n2 3 3 5 5\n3 3 4 4 1\n5 2 5 1\n"
             "1 170967 5\n1000 100000 1\n170967 170967 4\n")
tests.append("1 3\n5 3 1 1 1\n1 1 7\n1 1 1\n1 1 5\n")

# ---------------- hidden: small (brute checks these) ----------------
for n, T, kmax in ((6, 3, 3), (12, 4, 3), (20, 5, 2), (40, 6, 2)):
    while True:
        ops = growth_ops(n, 10 ** 9, list(range(1, T + 1)), 0.8, kmax)
        if 5 <= final_len(ops) <= 5000:
            break
    add(ops, queries(ops, 30, list(range(1, T + 1))))
ops = [(1, [1, 2])] * 300 + [(2, [3, 2])] * 5 + [(3, [2, 4])]                    # long row of slow growth
add(ops, queries(ops, 60, [1, 2, 3, 4]))
ops = growth_ops(3000, 6000, list(range(1, 9)), 0.85, 3)                         # huge row, brute keeps a prefix
qs = [(l, r, x) for l, r, x in queries(ops, 100, list(range(1, 9))) if r <= 200000]
qs += [(ri(1, 1000), ri(150000, 200000), ri(1, 8)) for _ in range(20)]
add(ops, qs)

# ---------------- hidden: big ----------------
Z = list(range(2, 14))
o, q = deep_chain(None, 1, False, Z, MAXQ)                                # deepest chain, 1 at the end
add(o, q)
o, q = deep_chain(None, 10, False, Z, MAXQ)
add(o, q)
o, q = deep_chain(None, 1000, False, Z, MAXQ)                                     # long strings on the path
add(o, q)
o, q = deep_chain(None, 2, True, Z, MAXQ)                                       # 1 at the front
add(o, q)
W = list(range(2, 600))
o, q = deep_chain(None, 5, False, W, MAXQ, W[:MAXQ], list(range(2, 16)))        # 500 different query types
add(o, q)

for T, keep, kmax in ((3, 0.9, 3), (8, 0.9, 4), (30, 0.95, 3), (1000, 0.97, 4), (MAXT, 0.97, 3)):
    ops = growth_ops(MAXSUM * 2 // (kmax + 1) - 10, MAXSUM, list(range(1, T + 1)), keep, kmax)
    xs = sorted(set(y for c, s in ops[-2000:] for y in s))[:400] or [1]
    add(ops, queries(ops, MAXQ, xs + [1, ri(1, T)]))

# growth to above 2^63 early, then fine-grained nights (exact positions matter)
ops = [(1, [1, 1, 1, 1])] * 33 + [(1, [2, 3, 1, 2])] + growth_ops(MAXSUM // 2 - 100, MAXSUM - 136, list(range(1, 25)), 0.95, 3)
add(ops, queries(ops, MAXQ, list(range(1, 25))))
ops = [(1, [2, 3])] + [(2, [2, 3]), (3, [3, 2])] * 40 + growth_ops(MAXN // 2, MAXSUM - 162, list(range(2, 12)), 0.9, 3)
add(ops, queries(ops, MAXQ, list(range(1, 12))))

# renaming chains: 1 -> 2 -> 3 -> ... with growth in between
ops = []
t = 1
for i in range(MAXN - 2000):
    if i % 1000 == 999:
        ops.append((t, [t + 1, t + 1, t + 1]))
    else:
        ops.append((t, [t + 1]))
    t = t % (MAXT - 1) + 1 if t + 1 < MAXT else 1
add(ops, queries(ops, MAXQ, list(range(1, MAXT, 997)) + [t, t - 1]))

# the row is all one type for a long time (huge answers), then split
ops = [(1, [1, 1])] * 62 + [(1, [2, 1, 2])] + growth_ops(50000, MAXSUM - 127, [1, 2, 3, 4, 5], 0.6, 2)
add(ops, queries(ops, MAXQ, [1, 2, 3, 4, 5]))

# two-level chains: several deep chains inside each other
ops = []
for _ in range(50000):
    ops.append((1, [2, 1]))
for _ in range(49000):
    ops.append((2, [3, 2] if rnd() < 0.5 else [2, 3]))
ops += filler(list(range(3, 10)), MAXP // 10 ** 10, 1)
add(ops, queries(ops, MAXQ, list(range(1, 10))))
o, q = deep_chain(None, 2, False, [2, 3], MAXQ)
add(o, q)
o, q = deep_chain(None, 1, True, Z, MAXQ)
add(o, q)
ops = []                                                                         # renames only, few types
t = 1
while len(ops) < MAXN - 100:
    if len(ops) % 3000 == 2999:
        ops.append((t, [t, t]))
    else:
        u = pick([y for y in (1, 2, 3) if y != t])
        ops.append((t, [u]))
        t = u
add(ops, queries(ops, MAXQ, [1, 2, 3]))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
