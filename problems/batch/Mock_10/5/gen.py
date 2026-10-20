# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1005)
MAXN, MAXV, MAXC = 200000, 10**9, 10**9
tests = []


def add(C, a):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= C <= MAXC
    assert min(a) >= 1 and max(a) <= MAXV
    tests.append(f"{n} {C}\n" + " ".join(map(str, a)) + "\n")


def steps(k, d):
    """k random steps 1..d"""
    r = random.randrange
    return [1 + r(d) for _ in range(k)]


def zigzag(n, lo, hi, d, noise=0):
    """converging zigzag: hi, lo, hi', lo', ... with the high side going down and the low side going up
    (steps 1..d); with noise > 0 some values repeat the previous one of their side"""
    m = (n + 1) // 2
    assert lo + 2 * m * d < hi
    up = steps(m, d)
    dn = steps(m, d)
    a = []
    h, l = hi, lo
    r = random.random
    for k in range(m):
        if not (noise and r() < noise):
            h -= dn[k]
        if not (noise and r() < noise):
            l += up[k]
        a.append(h)
        a.append(l)
    return a[:n]


def mono(n, start, d, sign):
    """increasing (sign = 1) or decreasing (sign = -1) with steps 0..d"""
    r = random.randrange
    a = [start]
    for _ in range(n - 1):
        a.append(a[-1] + sign * r(d + 1))
    return a


def lo_rising(n, d, spread):
    """every second value climbs slowly (the minimum keeps rising), the others are random above it"""
    r = random.randrange
    a = []
    base = 1
    for k in range(n):
        if k % 2 == 0:
            base += r(d + 1)
            a.append(base)
        else:
            a.append(base + 1 + r(spread))
    return a


def waves(n, period, amp, base):
    """long monotone runs up and down (a triangle wave) with a small random wobble"""
    r = random.randrange
    a = []
    for k in range(n):
        t = k % (2 * period)
        v = t if t < period else 2 * period - t
        a.append(base + v * amp // period + r(3))
    return a


def band(n, lo, hi, kind):
    """n values inside [lo, hi]: converging zigzag ('zig'), increasing ('inc'), decreasing ('dec') or random"""
    r = random.randrange
    w = hi - lo
    if kind == "zig":
        d = max(1, w // (n + 1))
        return zigzag(n, lo - 1, hi + 1, d, 0 if d > 1 else 0.5) if lo - 1 + (n + 1) * d < hi + 1 else \
            [hi if k % 2 == 0 else lo for k in range(n)]
    if kind in ("inc", "dec"):
        d = max(1, w // n)
        v = [lo + min(w, k * d + r(d)) for k in range(n)]
        return v if kind == "inc" else v[::-1]
    return [lo + r(w + 1) for _ in range(n)]


def bands(n, B, V, levels, kinds, wmin, wmax):
    """the row is cut into B pieces of random lengths; piece s holds values in a band [L_s, L_s + w_s]
    (w_s in wmin..wmax); levels: 'desc' (bands go down), 'walk' (random walk) or 'rand'"""
    r = random.randrange
    cuts = sorted(random.sample(range(1, n), B - 1))
    lens = [b - a for a, b in zip([0] + cuts, cuts + [n])]
    top = V - wmax
    if levels == "desc":
        L = sorted((1 + r(top) for _ in range(B)), reverse=True)
    elif levels == "walk":
        step = top // (2 * int(B ** 0.5) + 1)
        x = r(top) + 1
        L = []
        for _ in range(B):
            x += r(2 * step + 1) - step
            x = min(max(x, 1), top)
            L.append(x)
    else:
        L = [1 + r(top) for _ in range(B)]
    out = []
    for m, l in zip(lens, L):
        w = random.randint(wmin, wmax)
        out += band(m, l, l + w, random.choice(kinds))
    return out


def blocks(parts):
    out = []
    for p in parts:
        out += p
    return out


# ---------- samples ----------
add(5, [3, 9, 4, 8, 20, 21])
add(100, [5, 1, 8, 2])
add(1, [7])
add(4, [10, 1, 9, 2, 8, 3, 7, 4])
add(6, [12, 15, 13, 30, 2, 4, 3, 28, 26, 27])

# ---------- small (brute.cpp checks these) ----------
add(MAXC, [MAXV, 1])
add(1, [random.randint(1, MAXV) for _ in range(10)])
add(6, [random.randint(1, 20) for _ in range(40)])
add(50, zigzag(60, 1, 1000, 7))
add(300, [random.randint(1, 1000) for _ in range(500)])
add(10**6, zigzag(3000, 1, 10**8, 9000, 0.2))
add(3 * 10**6, bands(20000, 40, MAXV, "desc", ["zig"], 10**5, 10**6))
add(2000, bands(25000, 200, 10**6, "walk", ["zig", "inc", "dec", "rand"], 100, 5000))
add(40000, bands(20000, 60, 10**7, "rand", ["zig", "dec"], 10**4, 10**5))
add(MAXC, [MAXV] * 20000)

# ---------- big ----------
N = MAXN
add(MAXC, zigzag(N, 1, MAXV, 4900))
add(9 * 10**8, zigzag(N, 1, MAXV, 4900, 0.3))
add(MAXC, mono(N, 1, 9000, 1))
add(600, mono(N, 10**8, 900, -1))
add(10**6, bands(N, 100, MAXV, "desc", ["zig"], 10**5, 10**6))
add(10**7, bands(N, 100, MAXV, "desc", ["zig"], 10**5, 10**6))
add(5 * 10**6, bands(N, 300, MAXV, "desc", ["zig", "inc", "dec"], 10**4, 10**6))
add(2 * 10**5, bands(N, 30, 10**8, "desc", ["zig"], 10**5, 10**6))
add(3 * 10**5, bands(N, 100, 10**8, "walk", ["zig"], 10**4, 10**5))
add(2000, bands(N, 300, 10**7, "walk", ["zig", "inc", "dec", "rand"], 10**3, 10**4))
add(5 * 10**6, bands(N, 100, MAXV, "rand", ["zig", "inc", "dec"], 10**5, 10**6))
add(2 * 10**4, bands(N, 500, 10**8, "desc", ["zig", "dec"], 10**4, 10**5))
add(30000, bands(N, 50, 10**7, "desc", ["zig", "rand"], 10**4, 10**5))
add(3 * 10**5, bands(N, 200, 10**8, "desc", ["zig", "zig", "inc"], 10**3, 10**5))
add(200, bands(N, 300, 10**6, "desc", ["zig", "dec", "inc"], 100, 2000))
add(2 * 10**6, bands(N, 20, MAXV, "desc", ["zig"], 10**6, 10**7))
add(10**7, [random.randint(1, MAXV) for _ in range(N)])
add(1, [random.randint(1, MAXV) for _ in range(N)])
add(1000, [random.randint(1, 10**4) for _ in range(N)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
