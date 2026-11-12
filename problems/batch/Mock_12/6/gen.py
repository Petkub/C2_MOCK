# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(61126)
rnd = random.random
MAXN, MAXQ = 1_000_000, 200_000
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(rnd() * (hi - lo + 1))


def add(n, ops):
    q = len(ops)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    for t, a, b in ops:
        assert t in (1, 2, 3)
        if t == 3:
            assert 1 <= a <= n and 1 <= b <= n
        else:
            assert 1 <= a <= b <= n
    assert any(t != 1 for t, _, _ in ops)
    tests.append(f"{n} {q}\n" + "".join(f"{t} {a} {b}\n" for t, a, b in ops))


def rnd_range(n, kind):
    if kind == "long":                         # almost the whole row
        w = max(1, n // 1000)
        return ri(1, w), ri(n - w + 1, n)
    if kind == "short":                        # 1 to 3 coins
        l = ri(1, n)
        return l, min(n, l + ri(0, 2))
    if kind == "mid":                          # about a tenth of the row
        l = ri(1, n)
        return l, min(n, l + ri(n // 20, n // 7))
    l, r = ri(1, n), ri(1, n)
    return min(l, r), max(l, r)


def rnd_ops(n, q, mix, kind="any", far=True, kbig=False):
    """mix = weights of the three commands; far: walks start near coin 1 (they pass many coins);
    kbig: k around a third to a half of the row (often more than there are heads: answer -1)"""
    ops = []
    c1, c2 = mix[0] / sum(mix), (mix[0] + mix[1]) / sum(mix)
    for _ in range(q):
        x = rnd()
        t = 1 if x < c1 else 2 if x < c2 else 3
        if t == 3:
            p = ri(1, max(1, n // 1000)) if far else ri(1, n)
            k = ri(n // 3, n // 2 + 1) if kbig else ri(1, max(1, n // 8))
            ops.append((3, p, min(n, max(1, k))))
        else:
            l, r = rnd_range(n, kind)
            ops.append((t, l, r))
    if all(t == 1 for t, _, _ in ops):
        ops[-1] = (2, 1, n)
    return ops


# samples
add(8, [(1, 2, 6), (2, 1, 8), (1, 4, 8), (3, 3, 2), (3, 1, 5), (3, 8, 1)])
add(5, [(1, 1, 5), (1, 2, 3), (3, 4, 1), (3, 2, 1), (3, 2, 3), (2, 2, 3)])
add(1, [(3, 1, 1), (1, 1, 1), (3, 1, 1), (2, 1, 1)])
add(10, [(1, 1, 10), (1, 5, 5), (1, 1, 3), (3, 1, 6), (2, 1, 10)])
add(12, [(1, 3, 9), (1, 6, 12), (2, 4, 8), (3, 2, 4), (3, 6, 3)])
# hidden: small (checked by direct simulation)
add(1, [(1, 1, 1), (2, 1, 1), (3, 1, 1), (1, 1, 1), (3, 1, 1), (2, 1, 1)])
add(2, [(1, 2, 2), (3, 1, 1), (3, 1, 2), (1, 1, 2), (3, 1, 1), (3, 2, 1), (2, 1, 2), (1, 1, 1), (2, 1, 2)])
for n, q, kind in ((10, 60, "any"), (100, 500, "any"), (1000, 3000, "short"), (3000, 6000, "any"),
                   (20_000, 20_000, "long")):
    add(n, rnd_ops(n, q, (2, 1, 2), kind, far=False, kbig=(kind == "long")))
n = 20_000                                     # a fragmented row, then walks to the very end
add(n, rnd_ops(n, 10_000, (1, 0, 0), "short") + rnd_ops(n, 10_000, (1, 1, 2), "long", kbig=True))

# hidden: maximum size (N = 10^6, Q between 120 000 and 200 000 so that all inputs stay under 40 MB).
# Long commands and walks from near coin 1 make one pass over the coins per command too slow (even over packed
# bits); a fragmented row (many short flips first) defeats keeping the heads as a set of runs or of change points.
N = MAXN
add(N, rnd_ops(N, 140_000, (1, 1, 1), kbig=True))
add(N, rnd_ops(N, MAXQ, (1, 1, 2), "long"))
add(N, rnd_ops(N, 160_000, (1, 1, 2), "long", kbig=True))
add(N, rnd_ops(N, 130_000, (2, 1, 2), "any", kbig=True))
add(N, rnd_ops(N, 50_000, (1, 0, 0), "short") + rnd_ops(N, 110_000, (1, 1, 2), "long", kbig=True))
add(N, rnd_ops(N, 60_000, (1, 0, 0), "short") + rnd_ops(N, 100_000, (1, 2, 2), "long"))
add(N, rnd_ops(N, 130_000, (1, 1, 1), "short", far=False))
add(N, rnd_ops(N, 130_000, (2, 1, 2), "mid", far=False, kbig=True))
# single-coin flips spread over the row, then walks from coin 1 and counts of almost the whole row
ops = [(1, i, i) for i in random.sample(range(1, N + 1), 90_000)]
ops += [(3, 1, ri(80_000, 100_000)) if k % 2 else (2, ri(1, 1000), ri(N - 1000, N)) for k in range(60_000)]
add(N, ops)
# the whole row turned over again and again; walks whose answer is the last coin, or one too many (-1)
ops = []
for k in range(MAXQ):
    c = k % 4
    if c == 0:
        ops.append((1, 1, N))
    elif c == 1:
        p = ri(1, 1000)
        ops.append((3, p, N - p + 1))
    elif c == 2:
        p = ri(1, 1000)
        ops.append((3, p, N - p + 2 if p > 1 else ri(N // 2, N)))
    else:
        ops.append((2, ri(1, 1000), N))
add(N, ops)
# nested flips [i, N + 1 - i]: the heads form two growing and shrinking bands
ops = []
for k in range(140_000):
    if k % 2 == 0:
        i = ri(1, N // 2)
        ops.append((1, i, N + 1 - i))
    elif rnd() < 0.5:
        ops.append((2, ri(1, 1000), ri(N - 1000, N)))
    else:
        ops.append((3, ri(1, 1000), ri(N // 4, N // 2)))
add(N, ops)
# walks starting near the right end, counts of single coins, flips of suffixes and prefixes
ops = []
for k in range(140_000):
    c = k % 5
    if c == 0:
        ops.append((1, ri(1, N), N))
    elif c == 1:
        ops.append((1, 1, ri(1, N)))
    elif c == 2:
        ops.append((3, ri(N - 1000, N), ri(1, 3)))
    elif c == 3:
        i = ri(1, N)
        ops.append((2, i, i))
    else:
        ops.append((3, ri(1, 100), ri(N // 3, N // 2)))
add(N, ops)
add(N, rnd_ops(N, 160_000, (3, 1, 2), "long", kbig=True))
add(N, rnd_ops(N, 70_000, (1, 0, 0), "short") + rnd_ops(N, 80_000, (2, 1, 3), "long", kbig=True))
add(N, rnd_ops(N, MAXQ, (1, 3, 0), "long"))
add(N, rnd_ops(N, 140_000, (1, 1, 1), "any", far=False))
# long flips with walks of a few heads from anywhere (answers close to p)
ops = []
for k in range(160_000):
    if k % 2 == 0:
        ops.append((1,) + rnd_range(N, "long"))
    else:
        ops.append((3, ri(1, N), ri(1, 5)))
add(N, ops)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
