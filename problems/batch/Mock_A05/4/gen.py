# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(70504)
rnd = random.random
MAXN, MAXM, MAXSUM = 200000, 100000, 400000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


STR = [str(i) for i in range(MAXM + 1)]


def add(m, piers):
    n = len(piers)
    assert 2 <= n <= MAXN
    assert 1 <= m <= MAXM
    flat = [c for p in piers for c in p]
    assert len(flat) <= MAXSUM
    assert not flat or (1 <= min(flat) and max(flat) <= m)
    assert all(len(set(p)) == len(p) for p in piers if len(p) > 1)    # distinct companies at a pier
    lines = ["%d %d" % (n, m)]
    for p in piers:
        lines.append(" ".join([STR[len(p)]] + [STR[c] for c in p]))
    tests.append("\n".join(lines) + "\n")


def pick(m, k):
    """k distinct companies out of 1..m, random order"""
    if k == 1:
        return [1 + int(rnd() * m)]
    if k >= 50 and k * 3 >= m:
        p = list(range(1, m + 1))
        random.shuffle(p)
        return p[:k]
    out = []
    while len(out) < k:
        c = 1 + int(rnd() * m)
        if c not in out:
            out.append(c)
    return out


def rand_piers(n, m, kmin, kmax, empty=0.0):
    """random piers; the number of companies is cut so that the total stays <= MAXSUM"""
    piers, left = [], MAXSUM
    for i in range(n):
        k = 0 if rnd() < empty else min(ri(kmin, kmax), left - (n - 1 - i) * kmin)
        piers.append(pick(m, k))
        left -= k
    return piers


# samples
add(2, [[1, 2], [1, 2], [2], [2, 1]])
add(3, [[1, 2], [2, 3], [3, 1], [2], [1, 2]])
add(5, [[1, 2], [2, 3], [3, 1], [4, 5], [5]])
add(4, [[3, 1, 4], [2, 4], [1, 3], [4, 2, 3], [1], [3, 4], [2, 1, 4]])
add(5, [[2, 5], [5, 1], [1, 2, 3], [4, 3], [5, 3], [2, 4], [1, 4, 5], [3, 5], [4, 1]])

# hidden: small (brute tries every journey on these)
add(1, [[1], [1]])
add(3, [[1, 2, 3], [3, 2, 1]])
add(2, [[1], [2]])
add(1, [[1]] * 9)                                     # one company: only the direct ride
add(2, [[1, 2]] * 10)
add(4, [[], [1, 2, 3, 4], [1, 2], [3, 4], [1, 2, 3, 4], [4], [1, 2, 3]])   # nobody can leave pier 1
add(3, [[1, 2, 3], [1], [2], [3], [1, 2], [3, 1], [2, 3], []])            # nobody reaches pier N
add(4, rand_piers(10, 4, 1, 4))
add(3, rand_piers(10, 3, 0, 3, 0.1))

# hidden: big (N = 200 000)
N = MAXN
add(2, [[1, 2] if i % 2 else [2, 1] for i in range(N)])                  # two companies everywhere
add(3, rand_piers(N, 3, 1, 3))
add(30, rand_piers(N, 30, 1, 3))
add(MAXM, rand_piers(N, MAXM, 1, 3))                                     # many companies (no N x M table)
add(MAXM, [[1, ri(2, MAXM)] for _ in range(N)])                          # company 1 serves every pier
add(1, [[1]] * N)                                                        # answer 1
add(5, [[1] if rnd() < 0.5 else pick(5, ri(1, 5)) for _ in range(N)])  # company 1 very common
p = rand_piers(N, 10, 1, 2); p[0] = []
add(10, p)                                                               # pier 1 has no boat: 0
p = rand_piers(N, 1000, 1, 2); p[-1] = [1000]
p = [[c for c in q if c != 1000] for q in p[:-1]] + [p[-1]]
p[0] = p[0] or [1]
add(1000, p)                                                             # only pier N has company 1000: 0
add(20, rand_piers(N, 20, 1, 3, 0.2))                                    # piers without boats
add(5, [[i % 5 + 1, (i + 1) % 5 + 1] for i in range(N)])                 # neighbouring companies
big = []
left = MAXSUM - N
for i in range(N):                                                       # some piers with many companies
    k = 1
    if left > 0 and rnd() < 0.002:
        k = min(left + 1, ri(200, 2000))
        left -= k - 1
    big.append(pick(2000, k))
add(2000, big)
p = rand_piers(N, 3, 1, 1)
p[N // 2] = list(range(1, MAXM + 1))
p[N // 2 + 1] = pick(MAXM, 99999)
add(MAXM, p)                                                             # two piers with (almost) every company
add(4, rand_piers(N, 4, 1, 4))
add(8, rand_piers(N, 8, 1, 3))
add(1000, rand_piers(N, 1000, 1, 3))
add(MAXM, [[1, ri(2, MAXM)] if rnd() < 0.9 else [ri(2, MAXM)] for _ in range(N)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
