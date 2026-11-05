# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(810451)
MAXN, MAXT = 100000, 10 ** 9
tests = []


def add(k, t):
    n = len(t)
    assert 1 <= n <= MAXN and 1 <= k <= n
    assert all(1 <= x <= MAXT for x in t)
    tests.append(f"{n} {k}\n" + " ".join(map(str, t)) + "\n")


def relabel(t, big):
    """replace type numbers by distinct random labels (up to 10^9 when big)"""
    used = sorted(set(t))
    hi = MAXT if big else max(len(used) * 3, 10)
    lab = random.sample(range(1, hi + 1), len(used))
    m = dict(zip(used, lab))
    return [m[x] for x in t]


def uniform(n, m):
    return [random.randint(1, m) for _ in range(n)]


def rare(n, common, rares, gaps, tail, late=False):
    """`common` frequent types everywhere, rare types (labels common+1 .. common+rares) at spaced positions:
    the gaps between consecutive rare items are drawn from `gaps` (a (lo, hi) range), the last rare item is
    `tail` positions before the end; late: the longest gaps come last"""
    t = [random.randint(1, common) for _ in range(n)]
    g = [random.randint(*gaps) for _ in range(n // gaps[0] + 1)]
    if late:
        g.sort(reverse=True)
    pos, j = n - 1 - tail, 0
    while pos >= 0:
        t[pos] = common + random.randint(1, rares)
        pos -= g[j]
        j += 1
    return t


def tailfix(t, k, x):
    """the last x items get only k - 1 of the types that occur in t"""
    keep = random.sample(sorted(set(t)), k - 1)
    return t[:len(t) - x] + [random.choice(keep) for _ in range(x)]


def runs(n, m, mean):
    """runs of one type with random lengths 1 .. 2 * mean"""
    t = []
    while len(t) < n:
        t += [random.randint(1, m)] * random.randint(1, 2 * mean)
    return t[:n]


def cyc(n, m, noise):
    """a fixed order of m types repeated, with a few positions changed"""
    p = list(range(1, m + 1))
    random.shuffle(p)
    t = [p[i % m] for i in range(n)]
    for _ in range(noise):
        t[random.randrange(n)] = random.randint(1, m)
    return t


# samples
add(3, [5, 2, 5, 5, 7, 2, 2, 7])
add(4, [3, 1, 3, 1, 2])
add(1, [4, 4, 4, 4, 4, 4])
add(4, [1, 3, 1, 7, 3, 4, 6, 3, 7, 1])
add(3, [9, 4, 4, 9, 1, 4, 1, 1, 9, 9, 4, 4])
# hidden: small (brute checks these)
add(1, [7])
add(3, [1, 2, 3, 1, 2, 3, 4, 4, 4, 4])                      # the tail decides (answer 6)
add(2, [8, 8])
add(6, [6, 1, 5, 2, 4, 3])
add(30, relabel(uniform(30, 29), True))                      # K = N, a repeated type: -1
add(7, relabel(rare(500, 6, 2, (20, 60), 120), False))     # long tail without rare types
add(25, relabel(tailfix(runs(3000, 40, 6), 25, 900), False))
add(40, relabel(cyc(4000, 45, 300), False))
add(300, relabel(tailfix(uniform(20000, 330), 300, 2500), False))
# hidden: big (N = 100000)
N = MAXN
add(5, relabel(rare(N, 4, 1, (5000, 15000), 47500), False))       # the tail decides
add(5, relabel(rare(N, 4, 1, (12500, 25000), 1000, True), True))  # the last inner gap decides
add(9, relabel(rare(N, 7, 3, (1, 35000), 40000), False))
add(30, relabel(rare(N, 28, 5, (4000, 15000), 12500, True), True))
add(1500, relabel(tailfix(uniform(N, 1500), 1500, 35000), False))
t = [2101] + uniform(N - 2, 2100) + [2101]
add(len(set(t)), relabel(t, True))                                 # a type only at both ends: answer N - 1
add(1250, relabel(tailfix(uniform(N, 1250), 1250, 50000), False))
add(50, relabel(tailfix(uniform(N, 50), 50, 55000), True))
add(100, relabel(tailfix(runs(N, 120, 150), 100, 45000), False))
t = runs(N, 40, 75)
t[N - N // 100:] = cyc(N // 100, 40, 0)                            # every type occurs near the end
t[N // 400] = t[N - N // 100 - 5] = 41
add(len(set(t)), relabel(t, True))                                 # a type only twice, far apart
add(4000, relabel(tailfix(uniform(N, 10000), 4000, 45000), True))
add(10000, relabel(cyc(N, 10000, 0), False))                      # answer = K
add(4750, relabel(tailfix(cyc(N, 5000, 1500), 4750, 20000), True))
add(15000, relabel(cyc(N, 15001, 1), False))
t = tailfix(rare(N, 12, 4, (2500, 10000), 0, True), 14, 55000)
add(14, relabel(t, False))
t = relabel(uniform(N, 2500), False)
add(len(set(t)) + 1, t)                                            # -1
add(1, relabel(uniform(N, 2), True))                               # K = 1
t = [1] + [random.randint(2, 50) for _ in range(N - 1)]
add(len(set(t)), relabel(t, True))                                 # type 1 only first: answer N
t = rare(N, 10, 1, (500, 20000), 0, True)
t[-1] = 11
add(11, relabel(t, False))                                         # a rare item at the very end
add(2, relabel(tailfix(runs(N, 2, 10000), 2, 60000), False))
add(N, list(range(1, N + 1)))                                      # K = N, all different

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
