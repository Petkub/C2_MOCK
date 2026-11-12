# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1006070)
rnd = random.random
MAXN, MAXC, MAXH = 20000, 1000, 1000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(c, a, b, h):
    n = len(h)
    assert 1 <= n <= MAXN and 1 <= c <= MAXC
    assert all(1 <= x <= MAXH for x in h + [a, b])
    tests.append(f"{n} {c}\n{a} {b}\n" + " ".join(map(str, h)) + "\n")


def uniform(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def spikes(n, low, p):
    """low ground with rare tall segments"""
    return [ri(990, 1000) if rnd() < p else ri(1, low) for _ in range(n)]


def walk(n, step, lo=1, hi=MAXH):
    """a random walk of heights"""
    h, x = [], ri(lo, hi)
    for _ in range(n):
        x = min(hi, max(lo, x + ri(-step, step)))
        h.append(x)
    return h


def valleys(n, width, depth):
    """tall plateau with valleys of about `width` segments, `depth` deep"""
    h = []
    while len(h) < n:
        h += [ri(980, 1000)] * ri(1, 6)
        w = ri(1, width)
        h += [max(1, 1000 - depth + ri(-depth // 4, depth // 4)) for _ in range(w)]
    return h[:n]


def saw(n, period, lo, hi):
    return [lo + (hi - lo) * (i % period) // max(1, period - 1) for i in range(n)]


# samples
add(3, 5, 5, [2, 5, 1, 4])
add(10, 1, 1, [1, 1, 4, 1])
add(2, 3, 2, [3, 1, 2])
add(1, 6, 2, [1, 4, 2, 7, 3])
add(8, 2, 9, [3, 1, 6, 2, 2, 5])
# hidden: small (brute checks these)
add(1, 1, 1, [1])
add(1000, 1, 1, [7])
add(6, 1, 1, [2, 9, 9, 2, 1])
add(4, 2, 2, [5, 1, 1, 5, 1, 6])
add(3, 7, 4, uniform(7, 1, 9))
add(7, 1, 1, [4, 1, 1, 1, 1, 4])
add(30, 9, 8, [6, 5, 7])
# hidden: medium (checked by the O(N M^2) DP)
add(7, 40, 900, walk(300, 50))
add(1000, 1000, 999, [950 if rnd() < 0.995 else 949 for _ in range(1000)])          # both plazas above every section
add(15, 1, 1, spikes(800, 100, 0.02))
add(1000, 1000, 1000, [999 if rnd() < 0.9 else ri(990, 998) for _ in range(800)])   # the ends are the tallest
add(1000, 1000, 1000, [500] * 1800)                                                 # (raising everything pays)
# hidden: big (N = 20000)
N = MAXN
add(1, 500, 500, uniform(N, 1, 1000))
add(13, 1, 1000, uniform(N, 1, 1000))
add(250, 1000, 1, uniform(N, 1, 1000))
add(1000, ri(1, 1000), ri(1, 1000), uniform(N, 1, 1000))
add(2, 1, 1, spikes(N, 50, 0.002))
add(30, 3, 2, spikes(N, 200, 0.01))
add(700, 5, 5, spikes(N, 400, 0.05))
add(1, 1, 1, valleys(N, 40, 300))
add(60, 1000, 1000, valleys(N, 8, 700))
add(400, 990, 1, valleys(N, 3, 999))
add(5, ri(1, 1000), ri(1, 1000), walk(N, 30))
add(120, 1, 1, walk(N, 150))
add(600, 1000, 3, walk(N, 5, 700, 960))
add(1000, 1000, 1000, [1] * N)
add(1, 1, 1, saw(N, 50, 1, 1000))
add(45, 500, 600, saw(N, 7, 100, 1000))
add(9, 1, 1, [1000 if i % 2 else 1 for i in range(N)])
add(1000, 1, 1, [ri(1, 1000) for _ in range(N)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
