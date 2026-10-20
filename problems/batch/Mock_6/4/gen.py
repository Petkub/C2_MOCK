# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random, sys
from array import array
assert array("I").itemsize == 4
from itertools import combinations

random.seed(630320)
MAXN, MAXM = 300000, 20
tests = []


def add(m, a):
    n = len(a)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    assert min(a) >= 0 and max(a) < (1 << m)
    tests.append(f"{n} {m}\n" + " ".join(map(str, a)) + "\n")


_low = {}


def low_masks(m, kmax):
    """every mask of m bits with at most kmax bits set (these make submask enumeration slow)"""
    if (m, kmax) in _low:
        return _low[(m, kmax)]
    out = []
    for k in range(kmax + 1):
        for c in combinations(range(m), k):
            x = 0
            for b in c:
                x |= 1 << b
            out.append(x)
    _low[(m, kmax)] = out
    return out


def rnd(m, kind):
    """one random mask: 'u' each bit 1/2, 's' 1/4, 'ss' 1/8, 'd' 3/4, 'dd' 7/8"""
    g = random.getrandbits
    if kind == "u":
        return g(m)
    if kind == "s":
        return g(m) & g(m)
    if kind == "ss":
        return g(m) & g(m) & g(m)
    if kind == "d":
        return g(m) | g(m)
    return g(m) | g(m) | g(m)


def words(c):
    """the next c 32-bit outputs of the generator: getrandbits(m) for m <= 32 is the next output >> (32 - m),
    and getrandbits(32 * c) puts c outputs in a row, the first one in the lowest bits"""
    w = array("I", random.getrandbits(32 * c).to_bytes(4 * c, "little"))
    if sys.byteorder == "big":
        w.byteswap()
    return w


def below(n, count):
    """count numbers, the same as count calls of random.randrange(n) (= the index random.choice uses), made faster:
    each call draws getrandbits(n.bit_length()) until the value is below n, so count - len(out) more draws never
    overshoot"""
    sh, out = 32 - n.bit_length(), []
    while len(out) < count:
        out += [r for r in [w >> sh for w in words(count - len(out))] if r < n]
    return out


def distinct(m, n, kinds, base=()):
    """n masks: the masks of `base` first, then distinct random masks of the given kinds (in turn);
    when the skewed kinds run out of new masks, uniform ones fill the rest"""
    a = list(dict.fromkeys(base))
    each = (n - len(a)) // len(kinds) + 1
    cand = []
    sh = 32 - m
    for kind in kinds:
        # w = words(c * each): the same numbers as c * each calls g(m) in a row, made in one call (faster)
        if kind == "u":
            cand += [x >> sh for x in words(each)]
        elif kind == "s":
            w = words(2 * each)
            cand += [(x & y) >> sh for x, y in zip(w[0::2], w[1::2])]
        elif kind == "ss":
            w = words(3 * each)
            cand += [(x & y & z) >> sh for x, y, z in zip(w[0::3], w[1::3], w[2::3])]
        elif kind == "d":
            w = words(2 * each)
            cand += [(x | y) >> sh for x, y in zip(w[0::2], w[1::2])]
        else:
            w = words(3 * each)
            cand += [(x | y | z) >> sh for x, y, z in zip(w[0::3], w[1::3], w[2::3])]
    seen = dict.fromkeys(a + cand)          # the distinct masks in order
    if len(seen) >= n:
        return list(seen)[:n]
    need = n - len(seen)
    while need:             # draw g(m) until n masks; each draw adds at most one, so `need` draws never overshoot
        new = [x for x in dict.fromkeys([w >> sh for w in words(need)]) if x not in seen]
        seen.update(dict.fromkeys(new))
        need -= len(new)
    return list(seen)


_perm = []


def mix(a):
    """a in a random order; every big test has MAXN members, so one shuffled order is reused (fast)"""
    assert len(a) == MAXN
    if not _perm:
        _perm.extend(range(MAXN))
        random.shuffle(_perm)
    return array("I", map(a.__getitem__, _perm))      # compact: later passes over it are fast


def big(kinds, kmax, dup=0):
    """a big test: every mask with <= kmax bits, distinct random masks, `dup` repeated masks of <= 1 bit"""
    a = distinct(MAXM, MAXN - dup, kinds, low_masks(MAXM, kmax))
    one = [0] + [1 << b for b in range(MAXM)]
    a += [one[i] for i in below(len(one), dup)]
    return mix(a)


# samples
add(4, [13, 7, 3, 8])
add(2, [3, 3, 0])
add(3, [1, 1, 2, 4, 7, 6])
add(1, [1])
add(5, [5, 18, 31, 0, 12, 9, 20, 3])
# hidden: small (brute checks these)
add(20, [0])
add(20, [(1 << 20) - 1, (1 << 20) - 1])
add(1, [random.randint(0, 1) for _ in range(10)])
add(3, [random.randint(0, 7) for _ in range(60)])
add(20, [rnd(20, "s") for _ in range(2000)])
add(20, [random.choice(low_masks(20, 2)) for _ in range(3000)])
add(10, [random.getrandbits(10) for _ in range(5000)])
add(20, [rnd(20, random.choice(["u", "s", "ss", "d"])) for _ in range(4000)])
add(20, distinct(20, 4000, ["d", "dd"], low_masks(20, 1)))
add(15, [rnd(15, "ss") if i % 3 else 1 << random.randrange(15) for i in range(5000)])
# hidden: big (N = 300000, m = 20)
add(MAXM, big(["u"], 4))
add(MAXM, big(["u", "s"], 4, 500))
add(MAXM, big(["s"], 5))
add(MAXM, big(["ss", "s", "u"], 5, 2000))
add(MAXM, big(["d"], 4, 100))
add(MAXM, big(["dd", "u"], 3))
add(MAXM, big(["u", "d", "s"], 4, 20000))
add(MAXM, big(["s", "ss"], 3, 50000))
add(MAXM, big(["ss"], 4))
add(MAXM, big(["d", "u", "s", "ss", "dd"], 5))
add(MAXM, big(["u", "s"], 4, 3))
add(MAXM, big(["s", "d"], 5, 10))
add(MAXM, [0] * MAXN)                                              # nobody has a skill
half = MAXN // 2
a = [1 << i for i in below(MAXM, half)] + distinct(MAXM, MAXN - half, ["u", "s"], low_masks(MAXM, 4))
add(MAXM, mix(a))                                                       # many members with one skill
two = low_masks(MAXM, 2)
a = [two[i] for i in below(len(two), half)] + distinct(MAXM, MAXN - half, ["s", "d"], low_masks(MAXM, 3))
add(MAXM, mix(a))
add(MAXM, [(1 << MAXM) - 1] * (MAXN // 2) + low_masks(MAXM, 1) * (MAXN // 42) + [0] * (MAXN - MAXN // 2 - 21 * (MAXN // 42)))
add(17, [random.getrandbits(17) & random.getrandbits(17) for _ in range(MAXN)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
