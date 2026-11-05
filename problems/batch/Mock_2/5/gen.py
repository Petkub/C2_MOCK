# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1103)
MAXN, MAXQ, MAXH = 100000, 100000, 10 ** 9
tests = []
rnd = random.random


def add(h, qs):
    n, q = len(h), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(1 <= x <= MAXH for x in h)
    assert all(1 <= l <= r <= n and 0 <= e <= MAXH for l, r, e in qs)
    tests.append(f"{n} {q}\n" + " ".join(map(str, h)) + "\n" + "".join(f"{l} {r} {e}\n" for l, r, e in qs))


def clamp(x):
    return min(MAXH, max(1, x))


# heights: value(i) for building i (1-based)
def trend(step, noise, base=1):
    return lambda i: clamp(base + i * step + int(rnd() * (noise + 1)))


def uniform(top):
    return lambda i: 1 + int(rnd() * top)


def make(n, value):
    return [value(i) for i in range(1, n + 1)]


def photos(h, q, rstyles=("long",), estyles=("zero", "low")):
    """q photos; each picks a range style and an eye-level style at random"""
    n = len(h)
    w = max(1, n // 50)
    half, cut = n // 2, n // 20 + 1
    nr, ne = len(rstyles), len(estyles)
    out = []
    for _ in range(q):
        rs = rstyles[int(rnd() * nr)]
        if rs == "long":          # almost the whole street
            l, r = 1 + int(rnd() * w), n - int(rnd() * w)
            if l > r:
                l, r = r, l
        elif rs == "half":
            l = 1 + int(rnd() * half)
            r = max(l, min(n, l + half - 1 - int(rnd() * cut)))
        elif rs == "short":
            l = 1 + int(rnd() * n)
            r = min(n, l + int(rnd() * 20))
        else:
            l, r = 1 + int(rnd() * n), 1 + int(rnd() * n)
            if l > r:
                l, r = r, l
        es = estyles[int(rnd() * ne)]
        if es == "zero":
            e = 0
        elif es == "low":         # below building l: the eye level changes nothing
            e = int(rnd() * h[l - 1])
        elif es == "tie":         # exactly the height of a building of the range (or one below)
            e = max(0, h[l - 1 + int(rnd() * (r - l + 1))] - int(rnd() * 2))
        elif es == "early":       # the height of a building in the first tenth of the range
            e = h[l - 1 + int(rnd() * ((r - l) // 10 + 1))]
        elif es == "high":
            e = MAXH - int(rnd() * 3)
        else:
            e = int(rnd() * (MAXH + 1))
        out.append((l, r, e))
    return out


# samples
add([3, 1, 4, 1, 5, 9, 2, 6], [(1, 8, 0), (1, 8, 4), (2, 5, 3), (7, 8, 5), (4, 6, 9)])
add([2, 2, 3, 3, 1], [(1, 5, 0), (1, 5, 2), (5, 5, 0), (5, 5, 1), (2, 4, 3)])
add([7], [(1, 1, 6), (1, 1, 7), (1, 1, 1000000000)])
add([9, 8, 7, 6, 5, 4], [(1, 6, 0), (2, 6, 8), (3, 6, 6), (6, 6, 3)])
add([5, 6, 5, 7, 7, 8, 3, 9, 9, 1], [(1, 10, 0), (3, 8, 5), (2, 9, 7), (5, 10, 8), (1, 10, 9)])

ALL = ("zero", "low", "tie", "early", "any", "high")
# hidden: small (the brute checks these)
add([1], [(1, 1, 0), (1, 1, 1)])
h = make(300, uniform(6)); add(h, photos(h, 300, ("any", "short"), ALL))
h = make(1000, trend(3, 5)); add(h, photos(h, 1000, ("any", "long"), ALL))
h = make(1500, uniform(MAXH)); add(h, photos(h, 2000, ("any", "half"), ALL))
h = make(800, lambda i: 1 + i // 4); add(h, photos(h, 1500, ("any", "long"), ALL))
h = make(1200, lambda i: 2000 - i + int(rnd() * 3)); add(h, photos(h, 1500, ("any", "long"), ALL))
h = make(2000, lambda i: abs(1000 - i) * 3 + int(rnd() * 4) + 1); add(h, photos(h, 2000, ("any", "half"), ALL))
h = make(1000, lambda i: 5); add(h, photos(h, 1000, ("any",), ("zero", "tie", "low")))

# hidden: big
N, Q = MAXN, MAXQ
h = make(N, lambda i: i); add(h, photos(h, Q, ("long",), ("zero", "low", "early")))
h = make(N, lambda i: i * 10000); add(h, photos(h, Q, ("long",), ("zero", "low", "early", "tie")))
h = make(N, trend(10, 9)); add(h, photos(h, Q, ("long", "half"), ("zero", "low", "early")))
h = make(N, trend(10, 30)); add(h, photos(h, Q, ("long",), ("zero", "low", "tie")))
h = make(N, lambda i: 1 + i // 3); add(h, photos(h, Q, ("long",), ("zero", "low", "tie", "early")))
h = make(N, lambda i: 2 * i + 3 * (i % 2)); add(h, photos(h, Q, ("long",), ("zero", "low", "tie")))
h = make(N, lambda i: (i // 1000) * 30000 + (i % 1000) * 50 + 1); add(h, photos(h, Q, ("long",), ("zero", "early", "any")))
h = make(N, lambda i: i * 9000 + (i % 7) * 4000 + 1); add(h, photos(h, Q, ("long", "any"), ALL))
h = make(N, lambda i: N + 1 - i); add(h, photos(h, Q, ("long",), ALL))
h = make(N, uniform(MAXH)); add(h, photos(h, Q, ("long",), ALL))
h = make(N, uniform(5)); add(h, photos(h, Q, ("long", "any"), ("zero", "tie", "low")))
h = make(N, lambda i: abs(N // 2 - i) * 4 + 1 + int(rnd() * 4)); add(h, photos(h, Q, ("long", "half"), ALL))
h, cur = [], 1
for i in range(N):
    cur = max(1, cur + int(rnd() * 9) - 3)
    h.append(cur)
add(h, photos(h, Q, ("long", "half"), ("zero", "low", "tie", "early")))
h = make(N, lambda i: MAXH); add(h, photos(h, Q, ("long", "any"), ("zero", "tie", "high")))
h = make(N, lambda i: clamp(MAXH - (N - i) * 10000 + int(rnd() * 3))); add(h, photos(h, Q, ("long",), ("zero", "tie", "any")))
h = make(N, lambda i: i if i <= N // 2 else N + 1 - i + N // 2); add(h, photos(h, Q, ("long",), ("zero", "low", "early")))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
