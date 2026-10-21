# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(7404)
MAXN, MAXK, MAXC = 50000, 700, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(k, c):
    n = len(c)
    assert 1 <= n <= MAXN and 1 <= k <= min(n, MAXK)
    assert all(x == -1 or 1 <= x <= MAXC for x in c)
    tests.append(f"{n} {k}\n" + " ".join(map(str, c)) + "\n")


def costs(n, lo=1, hi=MAXC, broken=0.0):
    return [-1 if rnd() < broken else ri(lo, hi) for _ in range(n)]


def wrap_trap(n, k, cheap=1, dear=MAXC, base=(10 ** 6, 10 ** 7)):
    """posts near the cut 1|N are dear, except one cheap post at K and one at N-K+1: a line DP that only asks
    for a guard among posts 1..K and among posts N-K+1..N takes both, leaving a gap of 2K-1 around the ring"""
    c = costs(n, *base)
    for i in range(k):
        c[i] = dear - ri(0, 1000)
        c[n - 1 - i] = dear - ri(0, 1000)
    c[k - 1] = cheap
    c[n - k] = cheap
    return c


def periodic(n, k, period, cheap=(1, 10), dear=(10 ** 8, MAXC), shift=0):
    return [ri(*cheap) if (i + shift) % period == 0 else ri(*dear) for i in range(n)]


def break_run(c, start, length):
    """posts start..start+length-1 (0-based, around the ring) become broken"""
    n = len(c)
    for t in range(length):
        c[(start + t) % n] = -1
    return c


# samples
add(3, [4, 1, 5, 3, 2, 6, 2, 5])
add(2, [3, -1, -1, 4, 2, 5])
add(1, [7])
add(4, [6, -1, 3, 8])
add(3, [2, 9, 4, -1, 1, 7, 7, 3, -1, 5])

def decoys(c, k, spots, cost=1):
    """the cheapest posts of all sit between the posts of a cheap every-K pattern (or elsewhere)"""
    for p in spots:
        c[p] = cost
    return c


def trap(n, k, r, rr, cheap=(10, 99), dec=(1, 9), dear=(10 ** 6, MAXC), broken=0.0, base=None):
    """K divides n; the cheap posts r, r + K, ... (0-based) are the only cheapest cover; decoys rr, rr + 2K, ...
    (rr != r, never K apart, not even across the join) are the cheapest posts of all and one of them lies in
    1..K, but a cover using a decoy needs an extra guard: forcing the cheapest post (globally or in 1..K) fails"""
    assert n % k == 0 and r != rr and 0 <= min(r, rr) and max(r, rr) < k
    c = base if base is not None else costs(n, *dear, broken)
    for i in range(r, n, k):
        c[i] = ri(*cheap)
    for i in range(rr, rr + n - 2 * k + 1, 2 * k):
        c[i] = ri(*dec)
    return c


# hidden: small (the brute checks these)
add(2, [-1, 5])
add(3, break_run(costs(12, 1, 20), 10, 3))               # three broken posts across the join of N and 1
add(5, wrap_trap(40, 5, base=(100, 200), dear=1000))
add(4, decoys(periodic(60, 4, 4, cheap=(5, 6), dear=(50, 90)), 4, (2, 30)))
add(15, trap(300, 15, 9, 2, dear=(1000, MAXC)))
add(300, costs(300, 1, MAXC, 0.3))
add(5, decoys(periodic(500, 5, 5, cheap=(20, 30), dear=(40, 100)), 5, (2, 97, 242)))
add(25, trap(1000, 25, 3, 20, broken=0.3))
add(20, trap(400, 20, 0, 13, cheap=(5, 9), dec=(1, 4), dear=(100, 1000)))
add(9, break_run(costs(700, 1, 1000, 0.1), 300, 9))      # a run of K broken posts in the middle: -1

# hidden: big
N, K = MAXN, MAXK
NK = N - N % K                                            # the largest ring that K divides
add(K, costs(N))
add(K - 1, costs(N, 1, MAXC, 0.05))
add(K, decoys(periodic(NK, K, K, cheap=(100, 300), dear=(301, 1000), shift=17), K, (200, 30 * K + 250, 31 * K + 260)))
add(K, wrap_trap(N, K))
add(625, trap(N, 625, 624, 0))
add(K, decoys(periodic(NK, K, K, cheap=(2, 10), shift=K // 2), K, (0, 40 * K, 42 * K)))  # cheap posts exactly K apart
add(K, decoys(periodic(NK, K, K, cheap=(2, 9), shift=100), K, (25, 50 * K + 25)))
add(1, [MAXC] * N)
add(K, [MAXC] * N)
add(K, trap(NK, K, 0, K - 1, cheap=(10 ** 8, 10 ** 8 + 99), dec=(10 ** 8 - 99, 10 ** 8 - 1), dear=(MAXC, MAXC)))
add(K, trap(NK, K, 123, 45, base=[MAXC - i * 9000 for i in range(NK)]))          # decreasing, with a trap
add(625, trap(N, 625, 77, 200, cheap=(5000, 9000), dec=(1, 4999)))
add(K, trap(NK, K, 7, 150, broken=0.4))
add(K, break_run(costs(N), N - 250, K))                   # K broken posts across the join of N and 1: -1
add(200, trap(N, 200, 77, 5, broken=1.0))                 # only the cheap posts and the decoys work
# every K-th post works (the gap across the join is shorter), plus cheaper decoys that never replace one of them
c = [-1 if i % K != 5 else ri(10, 99) for i in range(N)]
add(K, decoys(c, K, range(K - 200, N - 2 * K + 1, 2 * K)))
add(10, trap(N, 10, 4, 6, cheap=(10 ** 5, 10 ** 6), dec=(1, 10 ** 5 - 1), dear=(10 ** 7, MAXC)))
add(K, [ri(1, 10) if i < K or i >= N - K else ri(10 ** 6, 10 ** 9) for i in range(N)])
add(K, trap(NK, K, K - 7, K // 2, cheap=(5, 10), dec=(1, 4), broken=0.1))
add(500, decoys(periodic(N, 500, 500, cheap=(100, 200), dear=(10 ** 5, MAXC)), 500, (123, 25000 + 200, 37777)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
