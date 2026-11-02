# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A member is written as its input line "k s_1 ... s_k"; big tests draw these lines from precomputed tables (fast).
import os, random, bisect
from itertools import combinations, permutations

random.seed(640421)
MAXN, MAXS = 50000, 10 ** 9
tests = []
rnd = random.random


def line(s):
    assert 1 <= len(s) <= 4 and len(set(s)) == len(s) and 1 <= min(s) and max(s) <= MAXS
    return f"{len(s)} " + " ".join(map(str, s))


def add(members):
    """members: lists of skills or ready lines"""
    n = len(members)
    assert 1 <= n <= MAXN
    lines = [str(n)] + [m if isinstance(m, str) else line(m) for m in members]
    tests.append("\n".join(lines) + "\n")


def ids(k, lo=1, hi=MAXS):
    """k distinct random skill ids in [lo, hi]"""
    return random.sample(range(lo, hi + 1), k)


_tab = {}


def table(pool, ks):
    """the lines of every ordered choice of k distinct skills of pool, for every k in ks (repeats give weights:
    each size is equally likely per repeat, whatever its number of choices)"""
    key = (tuple(pool), tuple(ks))
    if key not in _tab:
        per = {k: [line(p) for p in permutations(pool, k)] for k in set(ks)}
        _tab[key] = [per[k] for k in ks]
    return _tab[key]


def pooled(n, pool, ks):
    """n members, each takes k = a random entry of ks skills of pool"""
    t = table(pool, ks)
    out = []
    for _ in range(n):
        lst = t[int(rnd() * len(t))]
        out.append(lst[int(rnd() * len(lst))])
    return out


def mixed(s):
    """s shuffled in place (a small list) and returned"""
    for i in range(len(s) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        s[i], s[j] = s[j], s[i]
    return s


def clusters(n, groups, gsize, ks, popular=(), pp=0.0, lo=1, hi=MAXS):
    """members in groups; each group has its own pool of gsize skills; a member takes k (from ks) positions of
    the pool, and (with probability pp each) the popular skills too (a member keeps at most 4 skills)"""
    pools = [ids(gsize, lo, hi) for _ in range(groups)]
    pos = [list(permutations(range(gsize), k)) for k in ks]
    out = []
    for _ in range(n):
        g = pools[int(rnd() * groups)]
        lst = pos[int(rnd() * len(pos))]
        s = [g[i] for i in lst[int(rnd() * len(lst))]]
        for x in popular:
            if rnd() < pp and x not in s:
                if len(s) == 4:
                    s[int(rnd() * 4)] = x
                else:
                    s.append(x)
        out.append(mixed(s))
    return out


def zipf(n, nskills, ks, lo=1, hi=MAXS):
    """skill r (r = 1..nskills) is drawn with weight 1 / r"""
    sk = ids(nskills, lo, hi)
    cum, t = [], 0.0
    for r in range(1, nskills + 1):
        t += 1.0 / r
        cum.append(t)
    out = []
    for _ in range(n):
        k = ks[int(rnd() * len(ks))]
        s = []
        while len(s) < k:
            x = sk[min(nskills - 1, bisect.bisect_left(cum, rnd() * t))]
            if x not in s:
                s.append(x)
        out.append(s)
    return out


def all_subsets(pool, copies):
    """every subset of pool with 1..4 skills, `copies` times each, shuffled"""
    out = []
    for k in range(1, 5):
        for c in combinations(pool, k):
            out += [list(c) for _ in range(copies)]
    random.shuffle(out)
    return [mixed(s) for s in out]


def popular_too(members, xs, pp):
    """every member (a list of skills) also gets each skill of xs with probability pp (a member with 4 skills
    gives up a random other one): a few skills that almost everybody has"""
    for s in members:
        for x in xs:
            if rnd() < pp and x not in s:
                if len(s) == 4:
                    s[int(rnd() * 4)] = x
                else:
                    s.append(x)
        mixed(s)
    return members


def shuffled(a):
    a = list(a)
    random.shuffle(a)
    return a


# samples
add([[3, 7, 100], [20, 3, 7], [5, 3], [100, 20, 8, 9]])
add([[5, 1000000000], [1000000000, 5], [5]])
add([[42, 7, 1, 9]])
add([[1, 2, 3, 4], [4, 3, 2, 1], [2, 3, 4], [1, 5], [6, 2, 4, 8], [9]])
add([[10, 20], [20, 30], [30, 10], [10, 20, 30], [40, 10, 20, 50], [50, 40], [60]])
# hidden: small (brute checks these)
add([[MAXS, 1, 500000000, 2]])
add([[1, 2, 3, 4], [4, 1, 3, 2]])
add(pooled(10, [1, 2, 3, 4, 5], [1, 2, 3, 4]))
add(pooled(200, ids(6, 1, 100), [1, 2, 3, 4, 4]))
add(clusters(3000, 40, 6, [2, 3, 4, 4], [77], 0.5, 1, 10 ** 4))
add(clusters(4000, 300, 5, [3, 4], ids(2), 0.3))
add(pooled(5000, ids(8), [1, 2, 3, 4]))
add(zipf(4000, 60, [2, 3, 4, 4], 1, 1000))
add(all_subsets(ids(6, 1, 50), 5))
add(shuffled(clusters(2500, 30, 7, [4], [], 0, 1, 999) + pooled(2500, ids(300, 1, 999), [1, 2])))
# hidden: big (N = 50000); most have a popular skill or a popular pair of skills (walking the members of
# every skill, or of every pair of skills, then touches about N^2 entries)
add([line(mixed([123456789, 987654321, 1, 1000000000]))] * MAXN)                # everybody the same
add(pooled(MAXN, ids(6, 1, 99), [4]))                                             # every pair shares >= 2
add(popular_too([ids(2, 1, 10 ** 5) for _ in range(MAXN)], [100, 200], 0.5))
add(popular_too([ids(3, 1, 20000) for _ in range(MAXN)], [5, 6], 0.6))
add(popular_too(clusters(MAXN, 1000, 6, [2, 3, 4, 4], [5000], 1.0, 1, 99999), [5001, 5002], 0.93))
add(popular_too(clusters(MAXN, 100, 7, [4], [31337], 0.98, 1, 99999), [31338], 0.7))
add(clusters(MAXN, 2500, 5, [3, 4], ids(2, 1, 9999), 0.85, 1, 99999))
add([[1] + ids(3, 2, 10 ** 5) for _ in range(MAXN)])                              # skill 1 is everybody's
add(clusters(MAXN, 20, 8, [2, 3, 4], [777, 888, 999], 0.92, 1, 9999))
add(zipf(MAXN, 1000, [2, 3, 4, 4], 1, 99999))
add(zipf(MAXN, 20000, [3, 4], 1, 99999))
add(all_subsets(ids(7, 1, 999), MAXN // 98)[:MAXN] + pooled(MAXN - 98 * (MAXN // 98), ids(7, 1, 999), [4]))
base = popular_too([ids(2) for _ in range(MAXN * 7 // 10)], [999999937], 0.98)
base = [line(s) for s in popular_too(base, [999999929, 999999893], 0.93)]
add(shuffled(base + [base[int(rnd() * len(base))] for _ in range(MAXN - len(base))]))   # big ids, copies
add(shuffled(pooled(MAXN // 2, ids(100, 1, 9999), [1]) + pooled(MAXN // 2, ids(6, 1, 9999), [3, 4])))
add(popular_too(shuffled(clusters(MAXN // 2, 50, 6, [4], [], 0, 10 ** 8, MAXS)
                         + zipf(MAXN // 2, 300, [2, 3, 4])), ids(3, 10 ** 8, MAXS), 0.93))
add(popular_too([ids(1, 1, 10 ** 6) for _ in range(MAXN)], [7777], 0.98))         # mostly {7777, x}
# almost every member's skill set is different, but a popular skill remains (grouping equal sets does not help)
add(popular_too([ids(3, 1, 10 ** 5) for _ in range(MAXN)], [4242], 0.95))
add(popular_too([ids(2, 1, 3000) for _ in range(MAXN)], [11, 12], 0.9))
add(popular_too([ids(2) for _ in range(MAXN)], [7], 0.97))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
