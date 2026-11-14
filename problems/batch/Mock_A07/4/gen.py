import random, os
random.seed(7404)
rnd = random.random
ri = lambda a, b: a + int(rnd() * (b - a + 1))
os.makedirs("tests", exist_ok=True)
NMAX, MMAX, V = 200000, 50000, 10**9
cases = []
# samples
cases.append((1, [1, 3, 4, 7, 10], [2, 8, 12]))
cases.append((3, [2, 5, 6, 7], [4, 8]))
cases.append((0, [5, 5, 12, 6], [5, 9, 14]))
cases.append((3, [3, 12, 13, 15, 16, 20, 25], [4, 20, 30]))
cases.append((1, [7, 3, 9, 11, 2, 6, 13], [4, 13]))


def boats(m, top, lo=0):
    s = set()
    while len(s) < m:
        s.add(ri(lo, top))
    return sorted(s)


def small(n, m, top, d):
    b = boats(m, top)
    return (d, [ri(0, b[-1]) for _ in range(n)], b)


# small tests for brute.cpp
for top, d in ((10, 1), (20, 2), (30, 0), (50, 4), (60, 10), (100, 20)):
    cases.append(small(ri(1, 12), ri(1, 5), top, d))
cases.append((3, [0, 0, 1, 2, 3], [9]))                  # only the first gap, arrivals at time 0
cases.append((50, [10, 20, 30], [40, 60, 99]))           # band too wide everywhere: no extra boat


def uniform(n, m, top, d):
    b = boats(m, top)
    return (d, [ri(0, b[-1]) for _ in range(n)], b)


def bursts(n, m, top, d, w):
    # passengers come in bursts right after each boat, inside the forbidden band
    b = boats(m, top)
    a = []
    for _ in range(n):
        j = ri(0, m - 1)
        lo = b[j - 1] + 1 if j > 0 else max(0, b[0] - w)
        a.append(min(b[j], ri(lo, lo + w)))
    return (d, a, b)


def first_gap(n, m, d):
    # long wait before the first boat, short gaps after it
    b = [V - 3 * m + 3 * i for i in range(m)]
    a = [ri(0, b[0]) if rnd() < 0.7 else ri(b[0], b[-1]) for _ in range(n)]
    return (d, a, b)


def ties(n, m, top, d):
    # few distinct arrival times, many equal to a boat time or to a band edge
    b = boats(m, top)
    pts = []
    for j in range(m):
        p = b[j - 1] if j > 0 else 0
        pts += [b[j], p + d, b[j] - d, (p + b[j]) // 2]
    pts = [x for x in pts if 0 <= x <= b[-1]]
    return (d, [pts[int(rnd() * len(pts))] for _ in range(n)], b)


def big_first(n, m, d):
    # a long first gap with a wide band, later gaps too short for the extra boat
    b0 = ri(4 * 10**8, 6 * 10**8)
    b = [b0]
    while len(b) < m:
        b.append(b[-1] + d + ri(0, d // 2))
    a = [ri(0, d - 1) if rnd() < 0.6 else ri(b[0] + 1, b[-1]) for _ in range(n)]
    return (d, a, b)


def mixed(n, m, top, d):
    # gaps of similar length: passengers spread out in odd gaps, about three times fewer and early in even gaps
    step = top // m
    b = [i * step - ri(0, step // 10) for i in range(1, m + 1)]
    a = []
    for _ in range(n):
        j = ri(0, m - 1)
        while j % 2 == 0 and rnd() < 0.67:
            j = ri(0, m - 1)
        p = b[j - 1] + 1 if j > 0 else 0
        if j % 2:
            a.append(ri(p, b[j]))
        else:
            a.append(p + int(rnd() * step * 0.05))
    return (d, a, b)


# largest sizes
cases.append(uniform(NMAX, MMAX, 10**8, 0))
cases.append(uniform(NMAX, MMAX, 10**8, 900))
cases.append(uniform(NMAX, 3, V, 10**8))
cases.append(uniform(NMAX, 1, V, 0))                     # one gap holds everyone
cases.append(uniform(NMAX, 2, V, 4 * 10**8))
cases.append(bursts(NMAX, MMAX, V, 15000, 12000))
cases.append(bursts(NMAX, 5, V, 10**8, 9 * 10**7))
cases.append(bursts(NMAX, 1000, 10**7, 4000, 3500))
cases.append(first_gap(NMAX, MMAX, 1))
cases.append(first_gap(NMAX, 4, 2))
cases.append(ties(NMAX, MMAX, 10**6, 3))
cases.append(ties(NMAX, 100, V, 10**6))
cases.append((10**8 + 1, [ri(0, 10**8) for _ in range(NMAX)], [10**8]))   # band covers everything: no extra boat
cases.append((0, [0] * NMAX, [V]))                            # everyone at time 0, one boat at 10^9
cases.append(uniform(NMAX, MMAX, 10**6, 7))
cases.append(bursts(NMAX, 20000, V, 30000, 25000))
cases.append(bursts(NMAX, 300, V, 10**6, 8 * 10**5))
cases.append(big_first(NMAX, 10000, 2 * 10**4))
cases.append(big_first(NMAX, 5, 5 * 10**7))
cases.append(mixed(NMAX, 8, V, 0))
cases.append(mixed(NMAX, 2000, 10**8, 1000))
# medium
cases.append(ties(2000, 30, 1000, 4))

for i, (d, a, b) in enumerate(cases, 1):
    n, m = len(a), len(b)
    assert 1 <= n <= NMAX and 1 <= m <= MMAX and 0 <= d <= V
    assert all(0 <= b[k] < b[k + 1] for k in range(m - 1)) and 0 <= b[0] and b[-1] <= V
    assert all(0 <= x <= b[-1] for x in a)
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(f"{n} {m} {d}\n{' '.join(map(str, a))}\n{' '.join(map(str, b))}\n")
print(len(cases), "tests,", sum(1 for d, a, b in cases if len(a) == NMAX), "with N = 200000")
