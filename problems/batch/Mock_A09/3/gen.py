# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Integer randomness only (randint), so every machine rebuilds the same files.
import os, random

R = random.Random(9031)
ri = R.randint
MAXN, MAXV = 100000, 10 ** 6
tests = []


def add(T, c, E):
    n = len(T)
    assert 1 <= n <= MAXN and len(c) == n and len(E) == n
    assert all(0 <= x <= MAXV for x in T + c + E)
    tests.append("%d\n%s\n%s\n%s\n" % (n, " ".join(map(str, T)), " ".join(map(str, c)), " ".join(map(str, E))))


def chance(p):
    return ri(1, 100) <= p


def homework(c, p, lo, hi, cap=MAXV):
    """E_i on about p% of the days: lo..hi percent of the hours still free (so a plan always exists)"""
    E, slack = [], 0
    for x in c:
        slack += x
        e = 0
        if chance(p) and slack > 0:
            e = min(cap, slack * ri(lo, hi) // 100)
        E.append(e)
        slack -= e
    return E


def fail_at(c, E, d):
    """make day d impossible: the homework due on day d is one hour more than all the hours still free"""
    slack = sum(c[:d + 1]) - sum(E[:d + 1]) + E[d]
    assert slack + 1 <= MAXV
    E = E[:]
    E[d] = slack + 1
    return E


# samples
add([3, 8, 5, 1, 6], [4, 2, 3, 2, 2], [0, 3, 0, 3, 1])
add([6, 3, 8, 1, 4], [2, 1, 0, 5, 3], [0, 1, 3, 0, 2])
add([4, 0, 7], [2, 5, 3], [0, 0, 0])
add([4, 0, 3, 2, 9, 7, 9], [5, 1, 1, 5, 1, 5, 5], [4, 0, 2, 2, 0, 0, 3])
add([3, 6, 2], [1, 2, 2], [0, 3, 2])

# hidden: small (brute checks these)
add([7], [0], [0])
add([7], [3], [3])
add([0], [5], [6])
add([5, 4, 3, 2, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2], [1, 0, 1, 0, 1, 0, 1, 6])   # early homework is costly
for n, cv, tv, p in ((12, 6, 9, 50), (40, 25, 1000, 40), (60, 30, MAXV, 60)):
    c = [ri(0, cv) for _ in range(n)]
    add([ri(0, tv) for _ in range(n)], c, homework(c, p, 20, 100))
c = [ri(0, 20) for _ in range(50)]
add(sorted([ri(0, 50) for _ in range(50)], reverse=True), c, homework(c, 40, 30, 100))
c = [ri(1, 20) for _ in range(50)]
add([ri(0, 9) for _ in range(50)], c, fail_at(c, homework(c, 50, 10, 90), 31))
c = [ri(0, 5) for _ in range(2000)]
add([ri(0, MAXV) for _ in range(2000)], c, homework(c, 30, 30, 100))


# hidden: max size
def big(tshape, cshape, p, lo, hi, fail=None):
    n = MAXN
    if tshape == "rand":
        T = [ri(0, MAXV) for _ in range(n)]
    elif tshape == "down":                      # early days pay more: deadlines force costly hours
        T = sorted((ri(0, MAXV) for _ in range(n)), reverse=True)
    elif tshape == "up":
        T = sorted(ri(0, MAXV) for _ in range(n))
    elif tshape == "max":
        T = [MAXV] * n
    elif tshape == "few":                       # many equal pays
        T = [ri(1, 5) * 200000 for _ in range(n)]
    elif tshape == "zigzag":                    # cheap and dear days alternate
        T = [ri(0, 1000) if i % 2 else ri(MAXV - 1000, MAXV) for i in range(n)]
    elif tshape == "waves":                     # pay falls inside each block of 1000 days
        T = [MAXV - (i % 1000) * 1000 + ri(0, 999) - 999 for i in range(n)]
    if cshape == "rand":
        c = [ri(0, MAXV) for _ in range(n)]
    elif cshape == "max":
        c = [MAXV] * n
    elif cshape == "high":
        c = [ri(MAXV - 1000, MAXV) for _ in range(n)]
    elif cshape == "gaps":                      # most days have no free time
        c = [ri(0, MAXV) if chance(20) else 0 for _ in range(n)]
    E = homework(c, p, lo, hi)
    if fail is not None:
        E = fail_at(c, E, fail)
    assert sum(E) >= 5 * 10 ** 8                # an hour-by-hour method has no chance
    add(T, c, E)


big("rand", "rand", 30, 10, 100)
big("rand", "rand", 80, 30, 100)
big("down", "rand", 40, 20, 100)
big("down", "high", 60, 50, 100)
big("down", "max", 100, 90, 100)
big("up", "rand", 40, 20, 100)
big("max", "max", 50, 30, 100)
big("max", "max", 100, 100, 100)                # every hour is homework: the answer is 0
big("few", "rand", 50, 20, 100)
big("zigzag", "high", 70, 40, 100)
big("zigzag", "gaps", 12, 50, 100)
big("waves", "rand", 50, 30, 100)
big("waves", "max", 90, 70, 100)
big("rand", "high", 5, 100, 100)                # few homeworks, each taking everything still free
big("down", "rand", 100, 85, 100, fail=MAXN - 1) # the last homework cannot be finished
big("zigzag", "rand", 100, 85, 100, fail=MAXN - 7)
big("rand", "max", 50, 30, 100)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
