# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A stack = an order of ranks 0..n-1 (top first, 0 = smallest number) + n distinct numbers.
import os, random
from collections import deque
from itertools import permutations

random.seed(1205002)
rnd = random.random
MAXT, MAXN, MAXV = 15000, 8, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(stacks):
    assert 1 <= len(stacks) <= MAXT
    lines = [str(len(stacks))]
    for s in stacks:
        assert 1 <= len(s) <= MAXN and len(set(s)) == len(s)
        assert 1 <= min(s) and max(s) <= MAXV
        lines.append(f"{len(s)} " + " ".join(map(str, s)))
    tests.append("\n".join(lines) + "\n")


# fewest flips of every order of 8 ranks (only used to pick hard stacks for the big tests)
start = tuple(range(MAXN))
dist = {start: 0}
q = deque([start])
while q:
    u = q.popleft()
    for k in range(2, MAXN + 1):
        v = u[k - 1::-1] + u[k:]
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)
by_dist = [[] for _ in range(10)]
for p, d in dist.items():
    by_dist[d].append(p)
for lst in by_dist:
    lst.sort()


def pick(lst):
    return lst[int(rnd() * len(lst))]


# ---- orders of ranks ----
def shuffled(a):
    a = list(a)
    key = [rnd() for _ in a]
    return [a[i] for i in sorted(range(len(a)), key=key.__getitem__)]


def far8(lo):
    """an order of 8 ranks that needs at least lo flips (lo = 7 or 8); 9 flips only now and then"""
    x = rnd()
    if x < 0.06:
        return pick(by_dist[9])
    return pick(by_dist[8] if lo == 8 or x < 0.55 else by_dist[7])


def near(n, k):
    """k random flips from the sorted stack"""
    a = list(range(n))
    for _ in range(k):
        j = ri(2, n) if n >= 2 else 1
        a[:j] = a[:j][::-1]
    return a


# ---- numbers (sorted, distinct) ----
def v_uniform(n):
    s = set()
    while len(s) < n:
        s.add(ri(1, MAXV))
    return sorted(s)


def v_small(n):
    s = set()
    while len(s) < n:
        s.add(ri(1, 2 * n + 4))
    return sorted(s)


def v_mixed(n):
    """numbers of very different sizes: 1 digit up to 10 digits"""
    s = set()
    while len(s) < n:
        e = ri(0, 9)
        s.add(min(MAXV, ri(10 ** e, 10 ** (e + 1) - 1)))
    return sorted(s)


def v_top(n):
    """numbers close to 10^9"""
    s = set()
    while len(s) < n:
        s.add(MAXV - ri(0, 40))
    return sorted(s)


def v_perm(n):
    return list(range(1, n + 1))


VALS = [v_uniform, v_small, v_mixed, v_top, v_perm]


def make(order, vals):
    return [vals[r] for r in order]


def hard_or_random(n, lo, p):
    """with 8 boxes: a hard order with probability p, otherwise a random order"""
    return list(far8(lo)) if n == 8 and rnd() < p else shuffled(range(n))


def rand_n():
    """mostly 8 boxes, sometimes fewer"""
    return 8 if rnd() < 0.7 else ri(1, 7)


# samples
add([[30, 10, 20, 40], [7, 5, 2], [15, 60, 45, 30, 90]])
add([[12, 5, 8, 3, 20, 15], [2, 4, 6, 8, 10]])
add([[3, 9, 6, 1, 8, 2, 7, 5], [44, 11, 33, 22, 66, 55], [8, 7, 6, 5, 4, 3, 2, 1], [25, 5, 35, 15]])
add([[9], [8, 6], [6, 8], [40, 10, 30, 20, 60, 50], [17, 4, 12, 9, 2, 20, 6]])
add([[70, 999999999, 5, 300], [1000000000, 1, 2], [8, 600000, 40, 2, 9000]])

# hidden: small (brute checks these)
st = []
for n in range(1, 6):
    st += [make(list(p), v_mixed(n)) for p in permutations(range(n))]
add(shuffled(st))   # every order of 1..5 boxes
add(shuffled(make(list(p), v_uniform(6)) for p in permutations(range(6))))   # every order of 6 boxes
add([make(shuffled(range(8)), v_uniform(8)) for _ in range(60)])
add([make(shuffled(range(n)), VALS[ri(0, 4)](n)) for n in (rand_n() for _ in range(120))])
add([make(list(pick(by_dist[9])), v_uniform(8))])                       # one stack, 9 flips
add([make(list(pick(by_dist[9])), v_top(8)) for _ in range(40)])
add([make(near(n, ri(0, 3)), v_small(n)) for n in (ri(1, 8) for _ in range(150))])
add([make(list(pick(by_dist[d])), v_mixed(8)) for d in range(10) for _ in range(6)])

# hidden: big (T = 15000)
T = MAXT
add([make(shuffled(range(8)), v_uniform(8)) for _ in range(T)])
add([make(shuffled(range(8)), v_uniform(8)) for _ in range(T)])
add([make(shuffled(range(8)), v_mixed(8)) for _ in range(T)])
add([make(shuffled(range(8)), v_top(8)) for _ in range(T)])
add([make(shuffled(range(n)), v_uniform(n)) for n in (rand_n() for _ in range(T))])
add([make(shuffled(range(n)), VALS[ri(0, 4)](n)) for n in (rand_n() for _ in range(T))])
add([make(shuffled(range(n)), v_mixed(n)) for n in (ri(1, 8) for _ in range(T))])
add([make(list(far8(7)), v_uniform(8)) for _ in range(T)])
add([make(list(far8(7)), v_mixed(8)) for _ in range(T)])
add([make(list(far8(8)), v_uniform(8)) for _ in range(T)])
add([make(list(far8(8)), v_small(8)) for _ in range(T)])
add([make(hard_or_random(n, 8, 0.9), v_uniform(n)) for n in (rand_n() for _ in range(T))])
add([make(list(pick(by_dist[9]) if rnd() < 0.25 else far8(8)), VALS[ri(0, 4)](8)) for _ in range(T)])
add([make(list(p), v_mixed(8)) for p in shuffled(by_dist[7] + by_dist[8])[:T]])   # distinct orders
add([make(hard_or_random(n, 7, 0.9), v_perm(n)) for n in (rand_n() for _ in range(T))])
add([make(near(8, ri(6, 12)), v_uniform(8)) for _ in range(T)])
add([make(list(far8(8)), v_top(8)) for _ in range(T)])
add([make(shuffled(range(8)) if rnd() < 0.5 else list(far8(8)), v_mixed(8)) for _ in range(T)])
add([make(hard_or_random(n, 7, 0.8), VALS[ri(0, 4)](n)) for n in (rand_n() for _ in range(T))])
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
