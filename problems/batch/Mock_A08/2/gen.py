# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Job i needs skill p_i and adds g_i when done; at most K jobs may be passed on; print the smallest start.
# Hidden tests: tiny edge cases, small random (brute tries every set of passed jobs), medium (brute dp),
# then max tests: large gains (the running skill passes 2^31), small gains with large answers,
# hard jobs late in the day (every check below the answer runs to the end), K = N (answer 0),
# answer equal to max p, all gains 0, increasing / decreasing needs.
import os, random

random.seed(7202)
rnd = random.random
MAXN, MAXV = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(k, p, g):
    n = len(p)
    assert 1 <= n <= MAXN and len(g) == n and 0 <= k <= n
    assert all(0 <= x <= MAXV for x in p) and all(0 <= x <= MAXV for x in g)
    tests.append(f"{n} {k}\n" + " ".join(map(str, p)) + "\n" + " ".join(map(str, g)) + "\n")


def rand_case(n, k, plo, phi, glo, ghi):
    return k, [ri(plo, phi) for _ in range(n)], [ri(glo, ghi) for _ in range(n)]


def late_hard(n, k, m, glo, ghi, plo):
    """easy jobs with small gains, then m hard jobs (p near 10^9) at the end; K < m"""
    p = [ri(0, 100) for _ in range(n - m)] + [ri(plo, MAXV) for _ in range(m)]
    g = [ri(glo, ghi) for _ in range(n)]
    return k, p, g


def ramp(n, k, step, jitter, gain):
    """needs grow along the day by about step per job, each job adds about gain"""
    p = [min(MAXV, max(0, i * step + ri(-jitter, jitter))) for i in range(n)]
    g = [ri(max(0, gain - jitter), gain + jitter) for _ in range(n)]
    return k, p, g


def easy_start(p, g, m):
    """the first m jobs are easy and give nothing"""
    for i in range(m):
        p[i], g[i] = ri(0, 1000), 0
    return p, g


# samples
add(1, [3, 6, 2, 9, 7], [2, 1, 4, 0, 3])
add(0, [0, 4, 3, 10], [3, 2, 5, 1])
add(2, [8, 1, 5, 12, 6, 20], [3, 2, 2, 4, 6, 1])
add(3, [10, 2, 30, 4, 25, 7, 40], [5, 6, 1, 8, 2, 9, 3])
add(1, [5, 9, 14, 3, 20, 11, 26, 30], [4, 5, 2, 6, 3, 7, 4, 1])

# hidden: tiny and small (brute tries every set of passed jobs)
add(0, [7], [0])
add(1, [6], [2])
add(3, [0, 0, 5, 0, 9, 2, 0, 14, 3, 20, 1, 8], [4, 0, 3, 1, 0, 6, 2, 0, 5, 1, 0, 2])
add(2, [0, 50, 60, 70, 80, 200, 90, 100, 300, 110, 120, 130, 140, 150, 400], [40] * 15)
add(0, [ri(0, 1000) for _ in range(18)], [ri(0, 60) for _ in range(18)])
add(5, [ri(0, 10 ** 6) for _ in range(18)], [ri(0, 10 ** 5) for _ in range(18)])
# medium (brute dp)
add(*rand_case(2000, 40, 0, 10 ** 4, 0, 20))
add(*ramp(1500, 300, 10, 3, 7))
add(*late_hard(2500, 20, 30, 0, 3, 9 * 10 ** 8))

# max tests
N = MAXN
# skill passes 2^31 within a few jobs once the first 1000 easy jobs are done
k, p, g = rand_case(N, 0, 0, MAXV, 0, MAXV)
for i in range(1000):
    p[i], g[i] = ri(0, 1000), ri(0, 1)
add(k, p, g)
k, p, g = rand_case(N, 7, 0, MAXV, 0, MAXV)
add(k, *easy_start(p, g, 3000))
k, p, g = rand_case(N, 100, 0, MAXV, 10 ** 8, MAXV)
add(k, *easy_start(p, g, 50000))
add(*rand_case(N, 12, 0, MAXV, 0, 20))                      # small gains: the answer is large
add(*rand_case(N, 5000, 0, MAXV, 0, 3000))
add(*late_hard(N, 0, 3, 0, 2, 9 * 10 ** 8))
add(*late_hard(N, 9, 25, 0, 5, 5 * 10 ** 8))
add(*late_hard(N, 999, 1500, 0, 3, 8 * 10 ** 8))
add(*ramp(N, 100, 5000, 2000, 4990))                        # needs grow a little faster than the gains
add(*ramp(N, 10000, 5000, 4000, 4000))
add(*ramp(N, 3, 5000, 100, 4950))
add(N, [ri(0, MAXV) for _ in range(N)], [ri(0, MAXV) for _ in range(N)])        # K = N: answer 0
add(N - 1, [ri(1, MAXV) for _ in range(N)], [ri(0, 10) for _ in range(N)])      # K = N - 1
# answer = max p: the hardest job comes after many jobs with no gain
add(0, [ri(0, 1000) for _ in range(N // 2)] + [MAXV] + [ri(0, MAXV) for _ in range(N - N // 2 - 1)],
    [0] * (N // 2) + [ri(0, MAXV) for _ in range(N - N // 2)])
add(777, [ri(0, MAXV) for _ in range(N)], [0] * N)          # no gains at all
# a few huge gains early, then the needs rise to 10^9 (an int skill wraps below zero)
k, p, g = rand_case(N, 50, 0, 10 ** 6, 0, 1000)
for i in range(0, 4):
    p[i], g[i] = ri(0, 10), MAXV
for i in range(N // 2, N):
    p[i] = ri(10 ** 9 - 10 ** 6, MAXV)
add(k, p, g)
# first job free with a big gain: answer 0 although K < N
k, p, g = rand_case(N, 30, 0, MAXV, 0, 5000)
p[0], g[0] = 0, MAXV
add(k, p, g)
# needs sorted increasing / decreasing
k, p, g = rand_case(N, 200, 0, MAXV, 0, 4000)
add(k, sorted(p), g)
k, p, g = rand_case(N, 200, 0, MAXV, 0, 10 ** 5)
add(k, sorted(p, reverse=True), g)
# mostly easy jobs, but every 1000th job is hard; gains medium
k = 10
p = [ri(9 * 10 ** 8, MAXV) if i % 1000 == 999 else ri(0, 10 ** 5) for i in range(N)]
g = [ri(0, 10 ** 5) for _ in range(N)]
add(k, p, g)

assert 25 <= len(tests) <= 35
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
