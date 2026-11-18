# Writes tests/NN.in for this problem. Samples first (01..04), then hidden tests.
# Integers only (big tests are rebuilt on students' machines and checked by SHA-256).
import heapq, os, random

random.seed(510517)
rnd = random.random
MAXN, MAXA, MAXX = 200000, 10 ** 9, 10 ** 15
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def best(a, k):
    """best score with level k (same rule as sol.cpp): deepest card L, leave the k - 1 most negative above it"""
    h, left, pre, ans = [], 0, 0, 0
    for x in a:
        pre += x
        if pre - left > ans:
            ans = pre - left
        if x < 0 and k > 1:
            heapq.heappush(h, -x)
            left += x
            if len(h) > k - 1:
                left += heapq.heappop(h)
    return ans


def add(a, x):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= x <= MAXX
    assert all(-MAXA <= v <= MAXA for v in a)
    tests.append(f"{n} {x}\n" + " ".join(map(str, a)) + "\n")


def add_k(a, k0):
    """X chosen so that the answer is k0 (or the start of the flat part of best() that ends at k0)"""
    add(a, best(a, k0))


def add_all(a, extra=0):
    """X = the sum of all positive cards (+ extra)"""
    add(a, max(1, sum(v for v in a if v > 0) + extra))


def uniform(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def dig(n, small, big, gap):
    """long runs of small negative cards with a big positive card after each run"""
    a = []
    while len(a) < n:
        run = ri(gap // 2, gap)
        a.extend(-ri(1, small) for _ in range(run))
        a.append(ri(big // 2, big))
    return a[:n]


def walls(n, gap):
    """very bad cards (must be left behind) mixed with mild cards and some big ones"""
    a = []
    for i in range(n):
        r = rnd()
        if r < 0.3:
            a.append(-ri(MAXA - 1000, MAXA))
        elif r < 0.7:
            a.append(ri(-1000, 1000))
        elif i % gap == 0:
            a.append(ri(MAXA // 2, MAXA))
        else:
            a.append(-ri(1, 10 ** 6))
    return a


# samples
add([-4, -4, 5, 7, -3, -4, 4], 12)
add([3, -2, 4, -7, 2], 10)
add([-17, 17, 5, -22, 22, -21, 5, -15, 20, 8], 70)
add([2, 3, -1, -10, 8, 1], 5)

# hidden: small (brute checks these)
add([MAXA], MAXA)
add([-5], 1)
add([0] * 9, 1)
add([-1] * 11 + [MAXA], MAXA)                          # answer N
add([-1] * 11 + [MAXA], MAXA - 1)
add(uniform(12, -MAXA, MAXA), MAXA)
a = dig(12, 5, 20, 3)
add_k(a, 3)
a = uniform(300, -50, 30)
add_k(a, 40)
a = dig(2000, 1000, MAXA, 40)
add_k(a, 300)
a = walls(2000, 7)
add_k(a, 450)

# hidden: big (every answer is large or -1)
N = MAXN
a = uniform(N, -MAXA, MAXA)
add_k(a, 60000)
a = uniform(N, -MAXA, MAXA // 3)
add_k(a, 23456)
a = uniform(N, -MAXA, MAXA // 2)
add_all(a)
add_all(a, 1)                                           # -1
a = dig(N, 1000, MAXA, 50)
add_k(a, 30000)
a = dig(N, 10 ** 6, MAXA, 20)
add_k(a, 9000)
a = dig(N, MAXA // 1000, MAXA, 200)
add_k(a, 120000)
a = walls(N, 5)
add_k(a, 40000)
a = walls(N, 11)
add_k(a, 15000)
a = [-1] * (N - 1) + [MAXA]                             # answer N
add(a, MAXA)
a = [-MAXA if i % 2 == 0 else MAXA - 1 for i in range(N)]
add(a, MAXA // 2 * (N // 4))
a = [-(i + 1) * 5000 if i % 3 else MAXA - i for i in range(N)]   # left-behind cards change at every step
add_k(a, 50000)
a = [-(N - i) * 5000 if i % 3 else ri(1, MAXA) for i in range(N)]
add_k(a, 50000)
a = uniform(N, -MAXA, MAXA)
add(a, MAXX)                                            # -1
a = dig(N, 100, MAXA, 6)
add_k(a, 3000)
a = uniform(N, -1000, 1000)
add_k(a, 80000)
a = dig(N, MAXA, MAXA, 30)
add_k(a, 70000)
a = [ri(-MAXA, -1) for _ in range(N)]                   # no positive card: -1
add(a, 1)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
