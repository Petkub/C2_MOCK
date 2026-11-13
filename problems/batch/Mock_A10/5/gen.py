# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random
from itertools import accumulate

random.seed(1204023)
rnd = random.random
MAXNK, MAXV = 200_000, 10 ** 9
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(rnd() * (hi - lo + 1))


def add(s, Q):
    """s = starting power of each kind, Q = list of quests, each one row: requirement A then reward B (2K numbers)"""
    n, k = len(Q), len(s)
    assert 1 <= n and 1 <= k and n * k <= MAXNK
    assert 0 <= min(s) and max(s) <= MAXV
    assert set(map(len, Q)) == {2 * k}
    assert 0 <= min(map(min, Q)) and max(map(max, Q)) <= MAXV
    if k <= 20:
        body = "\n".join(map(" ".join(["%d"] * (2 * k)).__mod__, map(tuple, Q)))
    else:
        body = "\n".join([" ".join(map(str, r)) for r in Q])
    tests.append(f"{n} {k}\n" + " ".join(map(str, s)) + "\n" + body + "\n")


def addq(s, Q):
    """the same with quests written as pairs (A, B)"""
    add(s, [A + B for A, B in Q])


def place(Q, order):
    """order: 'fwd' = as built, 'rev' = reversed, 'rand' = shuffled"""
    if order == "rev":
        Q.reverse()
    elif order == "rand":
        random.shuffle(Q)
    return Q


def blockers(P, cnt, G, k, exact=False):
    """quests that can never be done: one kind needs more than the final power P (exactly P + 1 when exact)"""
    Q = []
    free = [j for j in range(k) if P[j] < MAXV]           # kinds where more than the final power is allowed
    for _ in range(cnt):
        A = [int(rnd() * (x + 1)) for x in P]
        j = free[int(rnd() * len(free))]
        A[j] = P[j] + 1 if exact else min(MAXV, P[j] + ri(1, 3 * G))
        Q.append(A + [int(rnd() * (G + 1)) for _ in range(k)])
    return Q


def chain(s, m, gate, noise, G, order, nblock=0, slack=False, extra=0.0):
    """m quests that can only be done one at a time in one fixed order: quest t needs the reward of quest t - 1 in
    its gate kind (gate: 'first', 'last', 'rand'). The other kinds need: noise = 'zero' -> 0, 'tight' -> the
    current power, 'rand' -> random up to the current power. slack: the gate need is anywhere above the power
    before quest t - 1 (not only exactly the power). extra: chance of a random reward in a non-gate kind."""
    k = len(s)
    if k == 1:
        b = [1 + int(rnd() * G) for _ in range(m)]
        P = list(accumulate([s[0]] + b))            # P[t] = power after t quests
        if slack:
            a = [P[0]] + [P[t - 1] + 1 + int(rnd() * (P[t] - P[t - 1])) for t in range(1, m)]
        else:
            a = P[:m]
        Q = [[x, y] for x, y in zip(a, b)]
        Q += blockers(P[m:], nblock, G, 1, exact=True)
        return place(Q, order)
    P = list(s)
    g = [k - 1 if gate == "last" else 0 if gate == "first" else ri(0, k - 1) for _ in range(m + 1)]
    Q = []
    prev = None
    for t in range(m):
        A = [0] * k if noise == "zero" else list(P) if noise == "tight" else [int(rnd() * (x + 1)) for x in P]
        gj = g[t]
        if slack and prev is not None:
            A[gj] = prev + 1 + int(rnd() * (P[gj] - prev))
        else:
            A[gj] = P[gj]
        B = [0] * k
        if extra:
            for j in range(k):
                if rnd() < extra:
                    B[j] = int(rnd() * (G + 1))
        nj = g[t + 1]
        B[nj] = 1 + int(rnd() * G)
        prev = P[nj]                     # the power in the next gate kind before this quest
        P = [x + y for x, y in zip(P, B)]
        Q.append(A + B)
    Q += blockers(P, nblock, G, k, exact=True)
    return place(Q, order)


def near(s, m, G, tight, nblock, order="rand", zero=0.0):
    """m quests planned in a random order, quest t needs a bit less than the power after the quests before it
    (tight = largest fraction taken away); then nblock quests that can never be done. Answer = m."""
    k = len(s)
    P = list(s)
    Q = []
    for _ in range(m):
        A = [x - int(x * rnd() * tight) for x in P]
        B = [0 if rnd() < zero else int(rnd() * (G + 1)) for _ in range(k)]
        P = [x + y for x, y in zip(P, B)]
        Q.append(A + B)
    Q += blockers(P, nblock, G, k)
    return place(Q, order)


def rand_inst(n, k, R, G, s=None):
    s = s or [0] * k
    return s, [[ri(0, R) for _ in range(k)] + [ri(0, G) for _ in range(k)] for _ in range(n)]


# samples
addq([3, 0], [([0, 2], [1, 1]), ([3, 0], [0, 2]), ([5, 4], [2, 2]), ([4, 3], [0, 5])])
addq([0], [([4], [3]), ([0], [1]), ([1], [2]), ([7], [4]), ([3], [1])])
addq([2, 0, 5], [([2, 1, 0], [4, 4, 4]), ([0, 0, 6], [1, 0, 0]), ([3, 0, 5], [0, 2, 0])])
addq([1, 1, 0], [([2, 0, 0], [0, 3, 1]), ([0, 4, 0], [2, 0, 0]), ([1, 1, 1], [5, 5, 5]),
                ([3, 3, 1], [0, 0, 2]), ([1, 0, 0], [1, 0, 0]), ([4, 4, 9], [1, 1, 1])])
addq([2, 6], [([6, 2], [0, 1]), ([2, 7], [3, 0]), ([5, 7], [1, 4]), ([2, 6], [0, 1]),
             ([9, 12], [2, 2]), ([8, 11], [1, 0]), ([6, 9], [0, 3])])

# hidden: small (brute checks these)
addq([5], [([5], [0])])                                                   # exactly enough
addq([0, 0, 0], [([0, 0, 1], [7, 7, 0])])                                 # nothing can be done
add(*rand_inst(12, 3, 9, 1, [5, 5, 5]))
s = [ri(0, 5) for _ in range(4)]
add(s, near(s, 11, 4, 0.5, 4))
add([0, 0], chain([0, 0], 250, "rand", "rand", 3, "rand", nblock=50, slack=True, extra=0.3))
s = [ri(0, 50) for _ in range(5)]
add(s, near(s, 1500, 30, 0.3, 500))
s = [ri(0, 20) for _ in range(2000)]
add(s, chain(s, 8, "rand", "tight", 5, "rev", nblock=2))               # few quests, many kinds

# hidden: big (N * K = 200 000)
add([0], chain([0], MAXNK, "last", "zero", 5, "rev"))                   # one at a time, listed backwards
add([0], chain([0], 160_000, "last", "zero", 3, "rand", nblock=40_000))
s = [MAXV, 0]
add(s, chain(s, 100_000, "last", "rand", 3, "rand", slack=True))       # kind 1 decides, kind 0 is noise
add([0, 0], chain([0, 0], 100_000, "rand", "rand", 3, "rev", extra=0.2))
s = [MAXV] * 3 + [0]
add(s, chain(s, 50_000, "last", "rand", 4, "rev"))                     # the last kind decides
s = [ri(0, 1000) for _ in range(4)]
add(s, chain(s, 45_000, "rand", "rand", 6, "rand", nblock=5_000, slack=True, extra=0.3))
s = [ri(0, 100) for _ in range(10)]
add(s, chain(s, 20_000, "rand", "rand", 5, "rev"))
s = [ri(0, 1000), ri(0, 1000)]
add(s, near(s, 70_000, 20, 0.05, 30_000))
s = [ri(0, 100) for _ in range(5)]
add(s, near(s, 30_000, 10, 0.15, 10_000, zero=0.5))
add([0], near([0], MAXNK, 8, 1.0, 0))                                  # everything can be done
s = [ri(0, 10 ** 6), ri(0, 10 ** 6)]
add(s, blockers(s, 100_000, 10 ** 6, 2, exact=True))                   # nothing can be done
s = [ri(0, 30) for _ in range(5)]
addq(s, [([ri(0, x) for x in s], [ri(0, 9) for _ in range(5)]) for _ in range(40_000)])  # all doable at once
k = 100_000
addq([0] * k, [([0] * k, [0] * (k - 1) + [1]), ([0] * (k - 1) + [1], [0] * k)])  # two quests, many kinds
s = [ri(0, 9) for _ in range(10_000)]
add(s, chain(s, 20, "rand", "rand", 9, "rand"))
s = [ri(0, 9) for _ in range(MAXNK)]
A = list(s)
A[-1] += 1
addq(s, [(A, [ri(0, 9) for _ in range(MAXNK)])])                       # one quest, one short in the last kind
s = [0, 0, 0]
add(s, chain(s, 50_000, "rand", "rand", 2, "rand", nblock=16_666, extra=0.5))
P = [0]
Q = []
for _ in range(50_000):                                                 # large rewards (power above 2^31)
    a = ri(0, MAXV) if rnd() < 0.8 else ri(0, 10)
    Q.append([a, ri(MAXV // 2, MAXV)])
add(P, Q)
add([0, 0, 0], chain([0, 0, 0], 66_666, "rand", "tight", 3, "rand"))
s = [MAXV, 0]
add(s, chain(s, 100_000, "last", "rand", 2, "rev"))                    # kind 1 decides, kind 0 is noise
s = [0, MAXV]
add(s, chain(s, 90_000, "first", "rand", 4, "rand", nblock=10_000, slack=True))  # kind 0 decides, kind 1 is noise

k = MAXNK                                                                 # one quest, one short in a middle kind
s = [ri(0, 9) for _ in range(k)]
A = list(s)
A[ri(k // 3, 2 * k // 3)] += 1
addq(s, [(A, [ri(0, 9) for _ in range(k)])])
k = 100_000                                                               # two quests, each one short in a middle kind
s = [ri(0, 9) for _ in range(k)]
Q = []
for _ in range(2):
    A = [int(rnd() * (x + 1)) for x in s]
    A[ri(9 * k // 20, 11 * k // 20)] += 10
    Q.append((A, [ri(0, 9) for _ in range(k)]))
addq(s, Q)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
