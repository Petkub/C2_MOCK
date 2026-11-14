# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1404001)
MAXN, MAXW = 150000, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def add(people):
    n = len(people)
    assert 1 <= n <= MAXN
    for w, c in people:
        assert 1 <= w <= MAXW and 1 <= c <= n
    tests.append(f"{n}\n" + "".join(f"{w} {c}\n" for w, c in people))


def shuffled(people):
    people = list(people)
    random.shuffle(people)
    return people


def cheap_small(n, wmax, noise=0):
    """the cheaper the applicant, the smaller the team he accepts"""
    ws = sorted(ri(1, wmax) for _ in range(n))
    cs = sorted(ri(1, n) for _ in range(n))
    out = []
    for w, c in zip(ws, cs):
        if noise and ri(1, noise) == 1:
            c = ri(1, n)
        out.append((w, c))
    return shuffled(out)


def cheap_big(n, wmax):
    """the cheaper the applicant, the larger the team he accepts"""
    ws = sorted(ri(1, wmax) for _ in range(n))
    cs = sorted((ri(1, n) for _ in range(n)), reverse=True)
    return shuffled(zip(ws, cs))


def few_limits(n, k, wmax):
    """only k different limits, many applicants share each"""
    lim = [ri(1, n) for _ in range(k)]
    return [(ri(1, wmax), lim[int(rnd() * k)]) for _ in range(n)]


def upper_half(n, wmax):
    """every applicant accepts at least half of n, so most sizes have an answer"""
    return [(ri(1, wmax), ri(n // 2, n)) for _ in range(n)]


def steps(n, wmax):
    """limit c is taken by about c applicants... a staircase where c applicants accept exactly c"""
    out = []
    c = n
    while len(out) < n:
        take = min(n - len(out), max(1, c // 3))
        out += [(ri(1, wmax), c) for _ in range(take)]
        c = max(1, c - take)
    return shuffled(out)


# samples
add([(5, 2), (3, 4), (8, 5), (1, 1), (4, 3)])
add([(6, 4), (2, 3), (7, 4), (1, 2)])
add([(3, 2), (3, 2), (3, 2)])
add([(10, 6), (4, 2), (9, 5), (2, 3), (7, 6), (5, 1)])
add([(1, 7), (8, 3), (6, 4), (2, 2), (9, 7), (3, 5), (4, 6)])
# hidden: small (brute checks these)
add([(MAXW, 1)])
add([(ri(1, 9), ri(1, 8)) for _ in range(8)])
add(cheap_small(1000, 1000))
add(cheap_big(1000, MAXW))
add(few_limits(2000, 3, 50))
add(upper_half(2000, MAXW))
add(steps(2000, 10 ** 6))
add([(MAXW, 3000)] * 3000)
# hidden: big (each with its own seed)
N = MAXN
BIG = [
    (1407000, lambda: [(MAXW, N)] * N),
    (1407001, lambda: [(ri(1, MAXW), ri(1, N)) for _ in range(N)]),
    (1407002, lambda: cheap_small(N, MAXW)),
    (1407003, lambda: cheap_small(N, 1000, 50)),
    (1407004, lambda: cheap_big(N, MAXW)),
    (1407005, lambda: few_limits(N, 5, 10 ** 6)),
    (1407006, lambda: few_limits(N, 100, 1000)),
    (1407007, lambda: upper_half(N, 10 ** 6)),
    (1407008, lambda: steps(N, 10 ** 6)),
    (1407009, lambda: [(ri(MAXW - 1000, MAXW), ri(N - 1000, N)) for _ in range(N)]),
    (1407010, lambda: shuffled([(i + 1, i + 1) for i in range(N)])),
    (1407011, lambda: shuffled([(MAXW - i, i + 1) for i in range(N)])),
    (1407012, lambda: [(ri(1, 10 ** 6), N if ri(0, 1) else ri(1, 10)) for _ in range(N)]),
    (1407013, lambda: [(ri(1, 10), ri(1, N)) for _ in range(N)]),
    (1407014, lambda: cheap_small(N, 10 ** 6, 1000)),
    (1407015, lambda: [(ri(1, 10 ** 6), N - int(N * rnd() ** 3)) for _ in range(N)]),
    (1407016, lambda: [(ri(1, 10 ** 5), N // 2) for _ in range(N)]),
]
for seed, make in BIG:
    random.seed(seed)
    add(make())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
