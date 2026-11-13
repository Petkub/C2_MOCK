# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Most big tests are built around a "front": k varieties with increasing a and decreasing b (none beats another).
# The other varieties are placed relative to one front variety t:
#   below  - strictly inside the step of t (only t beats it)
#   deep   - anywhere under t
#   tie_a  - same a as t, smaller b but larger than the next front b
#   tie_b  - same b as t, a between the previous front a and a_t
#   twin   - identical to t (then t and its twin are both not worth planting)
import os, random

random.seed(620232)
rnd = random.random
MAXN, MAXV = 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(pts):
    n = len(pts)
    assert 1 <= n <= MAXN
    assert all(1 <= a <= MAXV and 1 <= b <= MAXV for a, b in pts)
    tests.append(f"{n}\n" + "".join(f"{a} {b}\n" for a, b in pts))


def shuffle(pts):
    random.shuffle(pts)
    return pts


def increasing(k, top):
    """k strictly increasing values in [1, top] with gaps >= 2"""
    g = max(2, int(1.6 * top / (k + 1)))
    out, x = [], 0
    for _ in range(k):
        x += ri(2, g)
        out.append(x)
    assert out[-1] <= top, (k, top)
    return out


def front(k, top=MAXV):
    a = increasing(k, top)
    b = increasing(k, top)[::-1]
    return a, b


def stair(n, k, mix, top=MAXV, keep=1.0):
    """front of k varieties (a fraction `keep` of them kept as given) plus n - len(front) others of the kinds in mix"""
    a, b = front(k, top)
    kinds = [x for x, w in mix for _ in range(w)]
    pts = [(a[t], b[t]) for t in range(k) if rnd() < keep]
    while len(pts) < n:
        t = int(rnd() * k)
        lo_a = a[t - 1] if t > 0 else 0
        lo_b = b[t + 1] if t + 1 < k else 0
        kind = kinds[int(rnd() * len(kinds))]
        if kind == "below":
            pts.append((ri(lo_a + 1, a[t]), ri(lo_b + 1, b[t] - 1)))
        elif kind == "deep":
            pts.append((ri(1, a[t]), ri(1, b[t])))
        elif kind == "tie_a":
            pts.append((a[t], ri(lo_b + 1, b[t] - 1)))
        elif kind == "tie_b":
            pts.append((ri(lo_a + 1, a[t] - 1), b[t]))
        else:
            pts.append((a[t], b[t]))
    return shuffle(pts)


def rand_pts(n, va, vb=None):
    vb = vb or va
    return [(ri(1, va), ri(1, vb)) for _ in range(n)]


N = MAXN
# samples
add([(3, 7), (5, 4), (2, 8), (6, 1), (1, 6), (4, 3)])
add([(4, 6), (7, 6), (2, 9), (1, 2)])
add([(8, 2), (3, 5), (6, 6), (2, 9), (7, 4), (5, 6), (1, 3)])
add([(10, 10), (4, 12), (9, 3), (7, 11), (9, 8), (2, 2), (9, 3), (6, 12)])
add([(15, 40), (19, 25), (15, 40), (30, 10), (18, 41), (20, 30)])
# hidden: small (brute checks these)
add([(7, 7)])
add([(5, 9), (5, 9)])                                                   # nothing worth planting
add([(3, 3), (3, 3), (1, 8), (8, 1), (2, 2)])
add(rand_pts(12, 4))                                                    # many ties and twins
add(rand_pts(300, 12))
add(rand_pts(2000, 60))
add(stair(3000, 400, [("twin", 2), ("tie_a", 2), ("tie_b", 2), ("below", 2)], top=10 ** 6))
add(stair(5000, 1500, [("twin", 1), ("tie_a", 3), ("below", 1)], keep=0.9))
# hidden: big (N = 100 000)
add(rand_pts(N, MAXV))                                                  # random, a small front
add(rand_pts(N, 1000))                                                  # small values: many ties and twins
add(rand_pts(N, 300, MAXV))                                             # many equal a
add(shuffle([(ri(1, MAXV), ri(1, MAXV)) for _ in range(N - 1)] + [(MAXV, MAXV)]))   # one beats all
a, b = front(N)
add(shuffle(list(zip(a, b))))                                           # every variety worth planting
pts = list(zip(a, b))[: N // 2]
add(shuffle(pts + pts))                                                 # every variety has a twin
add([(MAXV, MAXV)] * N)                                                 # all identical
add([(MAXV, ri(1, MAXV)) for _ in range(N)])                            # all the same a
add([(ri(1, MAXV), 777) for _ in range(N)])                             # all the same b
add(stair(N, 95000, [("tie_a", 1)]))                                    # a large front, ties in a
add(stair(N, 97000, [("tie_b", 1)]))                                    # a large front, ties in b
add(stair(N, 10000, [("twin", 1), ("below", 3)]))                       # twins on the front
add(stair(N, 8000, [("twin", 1), ("tie_a", 1), ("tie_b", 1), ("below", 1), ("deep", 1)]))
add(stair(N, 12000, [("below", 3), ("deep", 1)]))
add(stair(N, 98000, [("tie_a", 2), ("twin", 1)], keep=0.99))
add(stair(N, 8000, [("tie_a", 1), ("tie_b", 1), ("twin", 1), ("below", 2)], top=10 ** 5))
add(stair(N, 97000, [("below", 1), ("tie_a", 1)]))
add(stair(N, 200, [("deep", 1), ("tie_a", 1), ("twin", 1)]))
add(stair(N, 99000, [("twin", 1)], keep=0.99))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
