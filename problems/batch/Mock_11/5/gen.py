# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1105)
MAXN, MAXQ, MAXH = 100000, 100000, 10 ** 9
tests = []
rnd = random.random


def add(h, ops):
    n, q = len(h), len(ops)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(1 <= x <= MAXH for x in h)
    assert any(t == 2 for t, a, b in ops)
    for t, a, b in ops:
        assert (t == 1 and 1 <= a <= n and 1 <= b <= MAXH) or (t == 2 and 1 <= a <= b <= n)
    tests.append(f"{n} {q}\n" + " ".join(map(str, h)) + "\n" + "".join(f"{t} {a} {b}\n" for t, a, b in ops))


def clamp(x):
    return min(MAXH, max(1, x))


# heights: value(i) for building i (1-based), n buildings
def trend(step, noise, base=1):
    return lambda i: clamp(base + i * step + int(rnd() * (noise + 1)))


def uniform(top):
    return lambda i: 1 + int(rnd() * top)


def make(n, value):
    return [value(i) for i in range(1, n + 1)]


def ranges(n, style):
    """one query range [l, r]"""
    if style == "long":
        w = max(1, n // 50)
        l = 1 + int(rnd() * w)
        r = n - int(rnd() * w)
        return (l, r) if l <= r else (r, l)
    if style == "half":
        l = 1 + int(rnd() * (n // 2))
        r = l + n // 2 - 1 - int(rnd() * (n // 20))
        return l, max(l, min(n, r))
    l, r = 1 + int(rnd() * n), 1 + int(rnd() * n)
    return (l, r) if l <= r else (r, l)


def operations(n, q, upd, value, styles=("long",), order="random"):
    """q operations, a share `upd` of them updates (building chosen at random, new height value(i));
    order: "random" (mixed), "alternate" (update, query, update, ...), "updates first" """
    nu = int(q * upd)
    kinds = [1] * nu + [2] * (q - nu)
    if order == "random":
        random.shuffle(kinds)
    elif order == "alternate":
        kinds = [1, 2] * (nu) + [2] * (q - 2 * nu)
        kinds = kinds[:q]
    ops = []
    for t in kinds:
        if t == 1:
            i = 1 + int(rnd() * n)
            ops.append((1, i, value(i)))
        else:
            l, r = ranges(n, random.choice(styles))
            ops.append((2, l, r))
    if ops[-1][0] == 1:
        ops.append((2, 1, n)) if len(ops) < MAXQ else ops.__setitem__(-1, (2, 1, n))
    return ops


# samples
add([3, 1, 4, 1, 5, 9, 2, 6], [(2, 1, 8), (2, 2, 5), (1, 4, 7), (2, 2, 8), (2, 7, 8)])
add([2, 2, 3, 3, 1], [(2, 1, 5), (1, 5, 4), (2, 1, 5), (2, 4, 4)])
add([7], [(2, 1, 1), (1, 1, 1000000000), (2, 1, 1)])
add([9, 8, 7, 6, 5, 4], [(2, 1, 6), (1, 6, 10), (1, 1, 1), (2, 1, 6)])
add([5, 6, 5, 7, 7, 8, 3, 9, 9, 1], [(2, 1, 10), (2, 3, 8), (1, 9, 10), (2, 2, 9), (2, 5, 10)])

# hidden: small (the brute checks these)
add(make(1, uniform(5)), [(2, 1, 1), (1, 1, 3), (2, 1, 1)])
add(make(300, uniform(6)), operations(300, 300, 0.5, uniform(6), ("any",)))
add(make(1000, trend(3, 5)), operations(1000, 500, 0.5, trend(3, 5), ("any", "long")))
add(make(1500, uniform(MAXH)), operations(1500, 2000, 0.4, uniform(MAXH), ("any", "half")))
add(make(800, lambda i: 1 + i // 4), operations(800, 800, 0.5, lambda i: 1 + i // 4 + int(rnd() * 2), ("any",)))
add(make(1200, lambda i: 2000 - i + int(rnd() * 3)), operations(1200, 1000, 0.5, uniform(2500), ("any", "long")))

# hidden: big
N, Q = MAXN, MAXQ
add(make(N, uniform(MAXH)), operations(N, Q, 0.5, uniform(MAXH), ("long",)))
add(make(N, trend(10, 30)), operations(N, Q, 0.5, trend(10, 30), ("long",)))
add(make(N, lambda i: i), operations(N, Q, 0.5, lambda i: i + int(rnd() * 2), ("long", "half")))
add(make(N, lambda i: 1 + i // 3), operations(N, Q, 0.5, lambda i: 1 + i // 3, ("long", "any")))
add(make(N, lambda i: N + 1 - i), operations(N, Q, 0.5, lambda i: N + 1 - i + int(rnd() * 3), ("long",)))
add(make(N, uniform(5)), operations(N, Q, 0.5, uniform(5), ("long",)))
add(make(N, trend(10, 5)), operations(N, Q, 0.5, lambda i: 10 * i if rnd() < 0.9 else 10 * N + int(rnd() * 100), ("long",)))
add(make(N, trend(7, 20)), operations(N, Q, 0.1, trend(7, 20), ("long", "half")))
add(make(N, trend(5, 12)), operations(N, Q, 0.5, trend(5, 12), ("long",), "updates first"))
add(make(N, lambda i: abs(N // 2 - i) * 4 + 1 + int(rnd() * 6)),
    operations(N, Q, 0.5, lambda i: abs(N // 2 - i) * 4 + 1 + int(rnd() * 6), ("long", "half")))
add(make(N, lambda i: (i % 1000) * 50 + i // 1000 + 1), operations(N, Q, 0.5, trend(1, 50000), ("long",)))
add(make(N, trend(4, 400)), operations(N, Q, 0.5, trend(4, 400), ("long",)))
add(make(N, lambda i: i), operations(N, Q, 0.5, lambda i: i, ("long",), "alternate"))
add(make(N, trend(10, 30)), operations(N, Q, 0.5, trend(10, 30), ("any",)))
add(make(N, lambda i: 1000), operations(N, Q, 0.5, lambda i: 1000 - int(rnd() * 2), ("long",)))
add(make(N, lambda i: i * 10000), operations(N, Q, 0.5, lambda i: clamp(i * 10000 + int(rnd() * 20000) - 10000), ("long",)))
add(make(N, lambda i: 7), operations(N, Q, 0.5, lambda i: 7 + i // 100, ("long", "half")))
add(make(N, lambda i: 2 * i + 3 * (i % 2)), operations(N, Q, 0.5, lambda i: 2 * i + 3 * (i % 2) - int(rnd() * 4), ("long",)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
