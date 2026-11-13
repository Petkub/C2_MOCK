# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1201001)
MAXN, MAXM, MAXQ, MAXP = 20, 20, 50000, 10 ** 9
MAXLR = 10 ** 11
tests = []


def add(M, dishes, bad, qs):
    N = len(dishes)
    assert 1 <= N <= MAXN and 1 <= M <= MAXM and 1 <= len(qs) <= MAXQ
    lines = [f"{N} {M} {len(qs)}"]
    for p, al in dishes:
        assert 1 <= p <= MAXP and len(set(al)) == len(al) and all(1 <= a <= M for a in al)
        lines.append(" ".join(map(str, [p, len(al)] + list(al))))
    assert len(set(bad)) == len(bad) and all(1 <= b <= M for b in bad)
    lines.append(" ".join(map(str, [len(bad)] + list(bad))))
    for L, R in qs:
        assert 0 <= L <= R <= MAXLR
        lines.append(f"{L} {R}")
    tests.append("\n".join(lines) + "\n")


def rdish(M, pmin, pmax, kmax):
    k = random.randint(0, min(kmax, M))
    return (random.randint(pmin, pmax), sorted(random.sample(range(1, M + 1), k)))


def rq(tot, mode):
    """a question whose range sits around the menu prices (answers neither always 0 nor everything)"""
    if mode == "mid":
        a, b = sorted(random.randint(0, tot) for _ in range(2))
    elif mode == "low":
        a = random.randint(0, 3)
        b = random.randint(a, max(a, tot // 3))
    elif mode == "high":
        a, b = random.randint(tot // 2, tot + 5), MAXLR
    elif mode == "wide":
        a, b = random.randint(0, 3), MAXLR
    elif mode == "point":
        a = b = random.randint(0, tot)
    else:                                   # narrow
        c = random.randint(0, tot)
        w = max(1, tot // 2000)
        a, b = max(0, c - w), c + w
    return (a, min(b, MAXLR))


def case(M, dishes, bad, q, modes):
    tot = sum(p for p, _ in dishes)
    add(M, dishes, bad, [rq(tot, random.choice(modes)) for _ in range(q)])


ALL = ["mid", "mid", "low", "high", "wide", "narrow", "point"]
# samples
add(3, [(50, [1]), (30, []), (40, [2, 3])], [1], [(60, 100), (20, 50)])
add(1, [(10, [1]), (10, [1])], [], [(10, 20), (11, 19)])
add(2, [(7, [1, 2]), (5, []), (9, [2])], [1], [(6, 13), (0, 100)])
add(2, [(100, [])], [1, 2], [(100, 100), (1, 99), (101, 200)])
add(3, [(4, [2, 3]), (8, [])], [1], [(12, 12), (0, 8)])

# hidden: small (brute checks these)
for N, M, Q, pmax, kmax, t in [(1, 1, 5, 10, 1, 1), (4, 3, 30, 20, 2, 1), (8, 6, 50, 100, 2, 2),
                               (10, 10, 40, 10 ** 9, 3, 3), (12, 20, 30, 50, 3, 5), (13, 5, 20, 10 ** 6, 1, 1)]:
    dishes = [rdish(M, 1, pmax, kmax) for _ in range(N)]
    case(M, dishes, random.sample(range(1, M + 1), t), Q, ALL)
dishes = [(random.randint(1, 30), [1, 2, 3]) for _ in range(9)]           # every dish has every allergen
case(3, dishes, [2], 20, ALL)
dishes = [(random.randint(1, 30), []) for _ in range(11)]                 # no dish has an allergen
case(20, dishes, list(range(1, 21)), 30, ALL)


# hidden: big (N = 20, Q = 50 000; the customer can eat almost every dish)
def big(seed, M, pmin, pmax, kmax, t, modes=ALL, equal=False, q=MAXQ):
    random.seed(seed)
    dishes = [rdish(M, pmin, pmax, kmax) for _ in range(MAXN)]
    if equal:
        dishes = [(dishes[0][0], al) for _, al in dishes]
    bad = random.sample(range(1, M + 1), t)
    case(M, dishes, bad, q, modes)


big(1202001, 20, 1, MAXP, 0, 20)                                    # no dish has an allergen
big(1202002, 20, MAXP - 1000, MAXP, 0, 5, ["wide", "high"])          # the largest prices, nearly all menus
big(1202003, 20, 1, 1000, 1, 1)
big(1202004, 20, 1, MAXP, 2, 2, ["mid", "narrow"])
big(1202005, 20, 1, 100, 1, 1, ["mid", "point"])
big(1202006, 20, 1, MAXP, 1, 0)
big(1202007, 20, 1, MAXP, 0, 0, ["wide", "point"])
big(1202008, 1, 1, MAXP, 0, 1)
big(1202009, 20, 1, 20, 2, 1, ["narrow", "mid", "point"])
big(1202010, 20, 1, MAXP, 0, 0, ["narrow", "point", "mid"], equal=True)
big(1202011, 20, MAXP, MAXP, 0, 3, ALL, equal=True)
big(1202012, 20, 1, 10 ** 6, 1, 1)
big(1202013, 20, 1, MAXP, 0, 20, ["low", "high"])
big(1202014, 20, 1, 1000, 1, 2, ["mid"])
big(1202015, 20, 5 * 10 ** 8, MAXP, 0, 2, ["high", "mid", "wide"])
big(1202016, 20, 1, 3, 1, 1)
big(1202017, 20, 1, MAXP, 1, 1, ["mid", "wide", "point"])
big(1202018, 20, 1, 50, 0, 0, ["mid"])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
