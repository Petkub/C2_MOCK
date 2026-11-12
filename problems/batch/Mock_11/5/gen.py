# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(611505)
rnd = random.random
MAXN, MAXQ, MAXA = 100000, 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a, ops):
    n, q = len(a), len(ops)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(1 <= x <= MAXA for x in a)
    assert any(o[0] == 2 for o in ops)
    for t, x, y in ops:
        if t == 1:
            assert 1 <= x <= n and 1 <= y <= MAXA
        else:
            assert t == 2 and 1 <= x <= y <= n
    tests.append(f"{n} {q}\n" + " ".join(map(str, a)) + "\n"
                 + "".join(f"{t} {x} {y}\n" for t, x, y in ops))


def rand_vals(n, hi):
    return [ri(1, hi) for _ in range(n)]


def trend(n, hi, slope, noise):
    """a walk that drifts by `slope` per day with noise in [-noise, noise], clipped to 1..hi"""
    a, v = [], ri(hi // 3, 2 * hi // 3)
    for _ in range(n):
        v += slope + ri(-noise, noise)
        v = min(hi, max(1, v))
        a.append(v)
    return a


def ops_gen(n, q, upd, hi, rng="any", val=None):
    """q operations; a fraction `upd` are updates (value from val() or 1..hi);
    rng: 'any' random l <= r, 'long' both ends near the borders, 'short' length <= 50, 'mix'"""
    ops = []
    for _ in range(q):
        if rnd() < upd:
            ops.append((1, ri(1, n), val() if val else ri(1, hi)))
            continue
        kind = rng if rng != "mix" else ("any", "long", "short", "long")[int(rnd() * 4)]
        if kind == "long":
            l, r = ri(1, max(1, n // 10)), ri(n - n // 10, n)
        elif kind == "short":
            l = ri(1, n)
            r = min(n, l + ri(0, 50))
        else:
            l, r = ri(1, n), ri(1, n)
            if l > r:
                l, r = r, l
        ops.append((2, l, r))
    return ops


# samples
add([8, 3, 6, 9, 2, 7], [(2, 1, 6), (2, 4, 6), (1, 5, 10), (2, 4, 6), (2, 2, 3)])
add([9, 7, 4, 4, 1], [(2, 1, 5), (1, 3, 12), (2, 2, 4), (2, 3, 3)])
add([6, 2, 8, 5, 1, 9, 4], [(2, 1, 7), (1, 6, 3), (2, 1, 7), (2, 4, 7)])
add([4, 10, 1, 6, 3, 8, 2, 5], [(2, 1, 8), (1, 6, 1), (2, 3, 7), (2, 2, 5)])
add([100, 250, 175, 300, 120, 90, 310], [(2, 2, 6), (1, 4, 200), (2, 1, 7)])
# hidden: small (brute checks these)
add([5], [(2, 1, 1), (1, 1, 8), (2, 1, 1)])
add([1, 1000000000], [(2, 1, 2), (1, 1, 1000000000), (2, 1, 2), (1, 2, 1), (2, 1, 2)])
add([7, 7, 7, 7], [(2, 1, 4), (1, 2, 3), (2, 1, 4), (2, 2, 4), (2, 1, 2)])
add(rand_vals(10, 20), ops_gen(10, 50, 0.3, 20))
add(trend(300, 1000, -3, 20), ops_gen(300, 2000, 0.3, 1000, "mix"))
add(rand_vals(2000, MAXA), ops_gen(2000, 5000, 0.5, MAXA))
add(trend(3000, 10 ** 6, -5, 300), ops_gen(3000, 8000, 0.2, 10 ** 6, "mix"))
# hidden: big (N = Q = 100000)
N, Q = MAXN, MAXQ
add(rand_vals(N, MAXA), ops_gen(N, Q, 0.5, MAXA))
add(rand_vals(N, MAXA), ops_gen(N, Q, 0.2, MAXA, "long"))
add(trend(N, 10 ** 6, -1, 40), ops_gen(N, Q, 0.3, 10 ** 6, "long"))       # falling prices: max - min is wrong
add(trend(N, 10 ** 6, 1, 40), ops_gen(N, Q, 0.3, 10 ** 6, "mix"))         # rising prices
add(sorted(rand_vals(N, MAXA), reverse=True), ops_gen(N, Q, 0.05, MAXA, "long"))
add(sorted(rand_vals(N, MAXA)), ops_gen(N, Q, 0.1, MAXA, "mix"))
add(list(range(N, 0, -1)), ops_gen(N, Q, 0.02, N, "long", lambda: ri(1, N)))  # mostly answer 0
a = trend(N, 10 ** 6, -2, 25)
for i in range(0, N, 997):
    a[i] = 10 ** 6                                                          # spikes on a falling walk
add(a, ops_gen(N, Q, 0.3, 10 ** 6, "mix"))
add([ri(1, 10) if i % 2 else ri(MAXA - 10, MAXA) for i in range(N)], ops_gen(N, Q, 0.3, MAXA, "long"))
add(trend(N, 10 ** 6, 0, 1000), ops_gen(N, Q, 0.5, 10 ** 6, "long"))
add(rand_vals(N, 10 ** 6), ops_gen(N, Q, 0.0, 10 ** 6, "long"))           # questions only
add(rand_vals(N, 10 ** 6), ops_gen(N, Q, 0.9, 10 ** 6, "mix"))            # mostly updates
add([ri(1, 1000) for _ in range(N)], ops_gen(N, Q, 0.3, 1000, "long"))
add([ri(1, 9) for _ in range(N)], ops_gen(N, Q, 0.4, 9, "any"))
add(trend(N, MAXA, -10000, 30000), ops_gen(N, Q, 0.3, MAXA, "long"))
add([MAXA] * N, ops_gen(N, Q, 0.3, MAXA, "long", lambda: ri(1, 2) * (MAXA // 2)))
# a falling walk where updates only lower prices (the answers keep shrinking)
add(trend(N, 10 ** 6, -3, 30), ops_gen(N, Q, 0.4, 10 ** 6, "long", lambda: ri(1, 1000)))
add([ri(1, 10 ** 6) for _ in range(N)], ops_gen(N, Q, 0.3, 10 ** 6, "short"))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
