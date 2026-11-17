# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1004170)
MAXN, MAXQ, MAXC = 10 ** 6, 100000, 10 ** 9
rnd = random.random
tests = []


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(n, P, ops):
    q = len(ops)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ and 1 <= P <= MAXC
    has2 = False
    for o in ops:
        if o[0] == 1:
            assert len(o) == 3 and 1 <= o[1] <= n and 1 <= o[2] <= MAXC
        else:
            assert o[0] == 2 and len(o) == 4 and 1 <= o[1] <= n and 1 <= o[2] <= o[3] <= n
            has2 = True
    assert has2
    lines = [f"{n} {q} {P}"] + [" ".join(map(str, o)) for o in ops]
    tests.append("\n".join(lines) + "\n")


def clamp(x):
    return max(1, min(MAXC, x))


def gen_ops(n, q, P, upd, rng="long", pmode="any", price="below", spread=None, first=0, where="any"):
    """q operations; the first `first` of them are updates, after that a fraction `upd` (never the last one).
    price of an update: below (P - [0, spread]), around (P +- spread), rand (1..MAXC), slope (P - spread +
    2 i: cheaper to the left), vee (cheapest around a random point);
    where: positions of updates: any, or cluster (a few dense blocks);
    rng: long (l in the first tenth, r in the last tenth), any, short, point, whole;
    pmode: any, inside (l <= p <= r), outside (p < l or p > r when possible), end (p = l or r)"""
    spread = spread if spread is not None else 3 * n
    centre = ri(1, n)
    blocks = [(ri(1, n), ri(100, 3000)) for _ in range(8)]
    ops = []
    for k in range(q):
        if (k < first or rnd() < upd) and k < q - 1:
            if where == "cluster":
                st, ln = blocks[int(rnd() * len(blocks))]
                i = min(n, st + ri(0, ln))
            else:
                i = ri(1, n)
            if price == "below":
                x = P - ri(0, spread)
            elif price == "around":
                x = P + ri(-spread, spread)
            elif price == "rand":
                x = ri(1, MAXC)
            elif price == "slope":
                x = P - spread + 2 * i + ri(0, 3)
            else:
                x = P - spread + 3 * abs(i - centre) + ri(0, 5)
            ops.append((1, i, clamp(x)))
            continue
        if rng == "long":
            l, r = ri(1, max(1, n // 10)), ri(n - n // 10, n)
        elif rng == "short":
            l = ri(1, n)
            r = min(n, l + ri(0, 30))
        elif rng == "point":
            l = r = ri(1, n)
        elif rng == "whole":
            l, r = 1, n
        else:
            l, r = ri(1, n), ri(1, n)
            if l > r:
                l, r = r, l
        if pmode == "inside":
            p = ri(l, r)
        elif pmode == "outside" and (l > 1 or r < n):
            if l > 1 and (r == n or rnd() < 0.5):
                p = ri(1, l - 1)
            else:
                p = ri(r + 1, n)
        elif pmode == "end":
            p = l if rnd() < 0.5 else r
        else:
            p = ri(1, n)
        ops.append((2, p, l, r))
    return ops


# ---------------- samples ----------------
add(6, 9, [(1, 2, 3), (1, 6, 2), (2, 3, 1, 6), (2, 5, 4, 6), (1, 6, 9), (2, 1, 5, 6)])
add(5, 5, [(2, 2, 4, 5), (1, 3, 1), (2, 5, 1, 4), (2, 3, 3, 3)])
add(7, 10, [(1, 2, 1), (1, 7, 1), (2, 4, 1, 7), (2, 4, 3, 5), (2, 1, 1, 6)])
add(8, 7, [(1, 4, 1), (2, 5, 2, 8), (1, 4, 10), (2, 5, 2, 8), (2, 1, 6, 8)])
add(10, 15, [(1, 3, 6), (1, 8, 4), (2, 1, 1, 10), (2, 10, 1, 10), (2, 6, 5, 9)])

# ---------------- hidden: small (brute checks these) ----------------
add(1, 1, [(2, 1, 1, 1)])
add(2, 5, [(1, 2, 1), (2, 1, 1, 2), (1, 2, 7), (2, 1, 1, 2), (2, 2, 1, 1)])
add(50, 100, gen_ops(50, 60, 100, 0.4, "any", spread=60))
add(300, 1000, gen_ops(300, 400, 1000, 0.4, "any", price="around", spread=400))
add(2000, 10 ** 6, gen_ops(2000, 2000, 10 ** 6, 0.3, "any", "outside", price="vee", spread=3000))
add(2000, 5000, gen_ops(2000, 2000, 5000, 0.3, "short", price="rand"))
add(5000, 10 ** 9, gen_ops(5000, 5000, 10 ** 9, 0.5, "any", "inside", spread=200))
add(3000, 10 ** 5, gen_ops(3000, 3000, 10 ** 5, 0.3, "any", "end", price="slope", spread=6000))

# ---------------- hidden: N = 10^6, Q = 10^5 ----------------
N, Q, B = MAXN, MAXQ, MAXC
add(N, B, gen_ops(N, Q, B, 0.3, "long"))
add(N, B, gen_ops(N, Q, B, 0.5, "long", "inside", spread=N))
add(N, B - 5 * N, gen_ops(N, Q, B - 5 * N, 0.4, "long", price="around", spread=5 * N))
add(N, 7 * 10 ** 8, gen_ops(N, Q, 7 * 10 ** 8, 0.3, "long", price="rand"))
add(N, B, gen_ops(N, Q, B, 0.5, "any", price="below", spread=10 * N))
add(N, B, gen_ops(N, Q, B, 0.3, "long", price="slope", spread=2 * N))
add(N, B, gen_ops(N, Q, B, 0.3, "long", "outside", price="vee", spread=3 * N))
add(N, B, gen_ops(N, Q, B, 0.5, "long", "end", where="cluster", spread=4 * N))
add(N, 1, gen_ops(N, Q, 1, 0.2, "long", price="around", spread=10 ** 5))          # the cheapest start price
add(N, B, gen_ops(N, Q, B, 0.6, "long", spread=50, first=30000))                  # many shops change first
add(N, B, gen_ops(N, Q, B, 0.3, "any", "outside", spread=N))
add(N, B, gen_ops(N, Q, B, 0.3, "short", price="rand"))
add(N, B, gen_ops(N, Q, B, 0.2, "whole", spread=2 * N))
add(N, B, gen_ops(N, Q, B, 0.0, "long"))                                         # no change: P plus a distance

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
