# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A frog facing E at p and a frog facing W at q meet iff p <= q, q - p is even and q - p <= 2K;
# two frogs facing the same way meet iff they start on the same pad. The big tests make these cases common:
# many pairs at distance exactly 2K, many pairs at odd distances, many shared start pads with both directions,
# answers above 2^31 and pads p with p + 2K above 2^31.
import os, random

random.seed(1226)
rnd = random.random
MAXN, MAXK, MAXX = 200000, 10 ** 9, 10 ** 9
N = MAXN
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(k, xs, ds, mix=False):
    """xs: start pads, ds: string of 'E' / 'W'; mix: shuffle the frogs (for lists built in blocks)"""
    n = len(xs)
    assert 1 <= n <= MAXN and len(ds) == n and 1 <= k <= MAXK
    assert 1 <= min(xs) and max(xs) <= MAXX and set(ds) <= set("EW")
    if mix:
        order = sorted(range(n), key=lambda i: rnd())
        xs = [xs[i] for i in order]
        ds = "".join(ds[i] for i in order)
    tests.append(f"{n} {k}\n" + " ".join(map(str, xs)) + "\n" + ds + "\n")


def pads(n, lo, hi, par=None):
    """n random pads in [lo, hi]; with par: all with pad % 2 == par"""
    w = hi - lo + 1
    xs = [lo + int(rnd() * w) for _ in range(n)]
    if par is not None:
        xs = [x if x % 2 == par else (x + 1 if x < hi else x - 1) for x in xs]
    return xs


def dirs(n, pe=0.5):
    return "".join(["E" if rnd() < pe else "W" for _ in range(n)])


def rand_test(k, n, lo, hi, pe=0.5):
    add(k, pads(n, lo, hi), dirs(n, pe))


def blocks(k, parts):
    """parts: list of (xs, direction letter); the frogs are shuffled"""
    xs, ds = [], []
    for p, c in parts:
        xs += p
        ds.append(c * len(p))
    add(k, xs, "".join(ds), True)


def lattice(k, n, step, base, jitter):
    """pads base + j * step, a fifth of them moved by an offset from jitter"""
    m = min((MAXX - base) // step, n // 40)
    xs = [base + int(rnd() * m) * step for _ in range(n)]
    xs = [x + jitter[int(rnd() * len(jitter))] if rnd() < 0.2 else x for x in xs]
    add(k, xs, dirs(n))


# samples
add(3, [1, 5, 8, 4], "EWWE")
add(10, [3, 3, 7, 9, 12], "EEWEW")
add(2, [10, 4, 6, 8, 6, 1], "WEWEWE")
add(4, [5, 3, 9, 2, 15, 6, 11, 4], "EWEEWWWE")
add(1000000000, [800, 15, 2026, 17, 999999999, 444], "EWWEWE")
# hidden: small and medium (brute checks these)
add(7, [5], "E")
add(1, [5, 5], "EW")
rand_test(ri(1, 8), 12, 1, 30)
rand_test(ri(3, 9), 40, 1, 50, 0.8)
rand_test(100, 2000, 1, 3000)                                         # many pairs at distance 2K
rand_test(30, 2500, 1, 200)                                           # many shared start pads
blocks(1000, [(pads(1000, 1, 4000, 0), "E"), (pads(1000, 1, 4000, 1), "W"), (pads(30, 1, 4000), "E"),
              (pads(30, 1, 4000), "W")])
rand_test(500, 1500, 1, 1000000)
# hidden: big (N = 200000)
add(ri(1, MAXK), [7] * N, dirs(N))                                    # all on one pad
add(ri(1, MAXK), [123456] * N, "W" * N)                               # all on one pad, same way
add(MAXK, pads(N, 1, MAXX, 0), dirs(N))                               # K covers every distance
blocks(MAXK, [(pads(N // 2, 1, 5 * 10 ** 8, 0), "E"), (pads(N // 2, 5 * 10 ** 8, MAXX, 0), "W")])
blocks(3 * 10 ** 8 // 2, [(pads(N // 2, 1, 3 * 10 ** 8, 1), "E"), (pads(N // 2, 3 * 10 ** 8, 6 * 10 ** 8, 1), "W")])
rand_test(ri(10 ** 7, 2 * 10 ** 7), N, 1, MAXX)
rand_test(1000, N, 1, 100000)                                         # dense, distance 2K common
rand_test(20, N, 1, 1000)                                             # very dense
lattice(12345, N, 2 * 12345, ri(1, 1000), (1, 12345))                 # many pairs at exactly 2K
lattice(9999, N, 9999, ri(1, 1000), (2 * 9999 + 1,))                  # pads K apart (odd)
rand_test(ri(1, MAXK), N, 1, 60000, 1.0)                              # all face E
rand_test(ri(1, 1000), N, 1, 150000, 0.0)                             # all face W
rand_test(1, 50000, 1, 50000)
blocks(MAXK, [(pads(N // 2, 1, MAXX, 0), "E"), (pads(N // 2, 1, MAXX, 1), "W")])   # only odd distances
blocks(MAXK, [(pads(N - 200, 1, MAXX), "E"), (pads(200, 1, MAXX), "W")])
ws = pads(N // 2, 1, 50000)
blocks(1000, [([2 * x for x in ws], "W"), ([2 * x + 2 * int(rnd() * 50000) for x in ws], "E")])  # E frogs near W frogs, mostly on their right
blocks(ri(5 * 10 ** 8, MAXK), [(pads(N // 2 - 1000, 1, 4 * 10 ** 8, 0), "W"),
                               (pads(N // 2 - 1000, 4 * 10 ** 8, MAXX, 0), "E"), (pads(2000, 1, MAXX), "E")])
add(ri(9 * 10 ** 8, MAXK), pads(N, 7 * 10 ** 8, MAXX, 1), dirs(N))   # pads near 10^9
rand_test(ri(1000, 3000), N, 1, 1000000)
add(ri(95 * 10 ** 7, MAXK), pads(N, 3 * 10 ** 8, MAXX), dirs(N))     # every p + 2K above 2^31, both parities

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
