# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import bisect, gc, itertools, os, random

gc.disable()     # only acyclic data: the cyclic garbage collector just slows gen.py down

MAXN, MAXQ, MAXV = 20000, 20000, 10 ** 7
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a, qs):
    assert 1 <= len(a) <= MAXN and 1 <= len(qs) <= MAXQ
    assert 1 <= min(a) and max(a) <= MAXV and 1 <= min(qs) and max(qs) <= MAXV
    tests.append(f"{len(a)}\n{' '.join(map(str, a))}\n{len(qs)}\n" + "\n".join(map(str, qs)) + "\n")


# primality table up to MAXV
sieve = bytearray([1]) * (MAXV + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(MAXV ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = bytes(len(range(i * i, MAXV + 1, i)))
SMALL = [p for p in range(2, 3200) if sieve[p]]


PRIMES = list(itertools.compress(range(MAXV + 1), sieve))


def primes_in(lo, hi):
    """a function returning a random prime in [lo, hi]"""
    sub = PRIMES[bisect.bisect_left(PRIMES, lo):bisect.bisect_right(PRIMES, hi)]
    m = len(sub)
    return lambda: sub[int(rnd() * m)]


BIGP, MIDP, HIP = primes_in(10 ** 6, MAXV), primes_in(1000, 3162), primes_in(3000, 3162)
LOWP, ANYP, TOPP = primes_in(2, 200000), primes_in(2, MAXV), primes_in(9 * 10 ** 6, MAXV)
# queries that never divide (an unused prime) or are hard to factor (a prime > 9e6) take their primes from small
# fixed pools: a per-query scan that remembers the answer of every prime power it has seen then stays fast, so no
# correct method sits near the time limit (trial division costs the same per query either way)
_pool_rng = random.Random(150099).random         # own seed: built before the per-test seeds are set
_any_sub, _top_sub = PRIMES, PRIMES[bisect.bisect_left(PRIMES, 9 * 10 ** 6):]
_any_pool = sorted({_any_sub[int(_pool_rng() * len(_any_sub))] for _ in range(600)})
_top_pool = sorted({_top_sub[int(_pool_rng() * len(_top_sub))] for _ in range(400)})
ANYQ = lambda: _any_pool[int(rnd() * len(_any_pool))]
TOPQ = lambda: _top_pool[int(rnd() * len(_top_pool))]


class Built:
    """an array built from known factorisations; remembers, for every prime power p^e,
    the first index whose value is divisible by it"""

    def __init__(self):
        self.a = []
        self.first = {}      # p << 5 | e (e <= 23 < 32, so sorting these keys sorts by (p, e)) -> first index (1-based)
        self.maxe = {}       # p -> largest exponent so far


# each val_* returns a value v <= MAXV and its factorisation as pairs (p, e)
def val_bigprime():
    p = BIGP()
    return p, ((p, 1),)


def val_top():
    p = TOPP()
    return p, ((p, 1),)


def val_semi():
    p, q = MIDP(), MIDP()
    return (p, ((p, 1),)) if p == q else (p * q, ((p, 1), (q, 1)))


def val_semihi():
    p, q = HIP(), HIP()
    return (p, ((p, 1),)) if p == q else (p * q, ((p, 1), (q, 1)))


def val_power():
    p = SMALL[int(rnd() * 40)]
    e = 1
    while p ** (e + 1) <= MAXV and rnd() < 0.8:
        e += 1
    return p ** e, ((p, e),)


def val_smooth():
    fac, v = {}, 1
    for _ in range(ri(1, 8)):
        p = SMALL[int(rnd() * 25)]
        if v * p > MAXV:
            break
        v *= p
        fac[p] = fac.get(p, 0) + 1
    return v, fac.items()


def val_mixed():
    p = LOWP()
    fac, v = {p: 1}, p
    while True:
        q = SMALL[int(rnd() * 60)]
        if v * q > MAXV or rnd() < 0.3:
            break
        v *= q
        fac[q] = fac.get(q, 0) + 1
    return v, fac.items()


TINY = SMALL[:8]      # 2 .. 19 (23 is left out: it never appears where these are used)


def val_tiny():
    """a product of powers of primes <= 19 (several of them)"""
    fac, v = {}, 1
    for p in TINY:
        if rnd() < 0.6:
            e = 1 + int(rnd() * 3)
            if v * p ** e <= MAXV:
                v *= p ** e
                fac[p] = e
    return v, fac.items()


KINDS = {"top": val_top, "big": val_bigprime, "semi": val_semi, "semihi": val_semihi, "pow": val_power,
         "smooth": val_smooth, "mixed": val_mixed, "tiny": val_tiny}


def build_array(n, weights, raw=0.0, tail=0):
    """tail > 0: the last `tail` values are "tiny" ones, so primes <= 19 first appear at the very end"""
    b = Built()
    pick = [KINDS[k] for k in sorted(weights) for _ in range(weights[k])]
    m, first, maxe = len(pick), b.first, b.maxe
    append, get = b.a.append, maxe.get
    for k in range(1, n + 1):            # (written for speed: gen.py must be quick)
        if rnd() < raw:                  # a value whose factorisation is not tracked
            append(1 + int(rnd() * MAXV))
            continue
        v, fac = val_tiny() if k > n - tail else pick[int(rnd() * m)]()
        for p, e in fac:
            old = get(p, 0)
            if e > old:
                if e == 1:
                    first[p << 5 | 1] = k
                else:
                    for j in range(old + 1, e + 1):
                        first[p << 5 | j] = k
                maxe[p] = e
        assert v <= MAXV
        append(v)
    return b


def queries(b, q, late, none, n, hard):
    """late: a product of 1-3 prime powers that first appear in the second half;
    none: a power one higher than ever reached (maybe times a reached power), or an unused large prime;
    hard: a prime > 9e6 not in the array, or a product of two primes near sqrt(MAXV)"""
    first, maxe = b.first, b.maxe
    keys = sorted(first)
    late_list = sorted(pe for pe, k in first.items() if k > n // 2)
    ps = sorted(p for p, e in maxe.items() if p ** (e + 1) <= MAXV)
    nk, nl, nps = len(keys), len(late_list), len(ps)
    t1, t2, t3 = late + none, late + none + hard, late + none + hard + 0.05
    qs = []
    append = qs.append
    for _ in range(q):
        r = rnd()
        if r < late:
            if not late_list:
                append(1 + int(rnd() * MAXV))
                continue
            x = 1
            for _ in range(1 + int(rnd() * 3)):
                pe = late_list[int(rnd() * nl)]
                p, e = pe >> 5, pe & 31
                if x * p ** e <= MAXV:
                    x *= p ** e
            append(x)
        elif r < t1:
            if ps and rnd() < 0.6:
                p = ps[int(rnd() * nps)]
                x = p ** (maxe[p] + 1)
                if rnd() < 0.5:
                    for _ in range(5):
                        pe = keys[int(rnd() * nk)]
                        p2, e = pe >> 5, pe & 31
                        if p2 != p and x * p2 ** e <= MAXV:
                            x *= p2 ** e
                            break
                append(x)
                continue
            while True:
                p = ANYQ()
                if p not in maxe:
                    append(p if rnd() < 0.5 or p * 2 > MAXV else p * ri(1, MAXV // p))
                    break
        elif r < t2:
            if rnd() < 0.5:
                while True:
                    p = TOPQ()
                    if p not in maxe:
                        append(p)
                        break
            else:
                append(HIP() * HIP())
        elif r < t3:
            append(1)
        else:
            append(1 + int(rnd() * MAXV) if rnd() < 0.5 else ri(1, 1000))
    return qs


def tiny_queries(b, q):
    """products of powers of as many primes <= 19 as fit (up to 8 prime powers), each power reached by
    the tail; half of them also times 23, which never appears (their largest prime, so -1)"""
    maxe, qs = b.maxe, []
    for _ in range(q):
        x, ps = 1, []
        for p in TINY:
            e = maxe.get(p, 0)
            if e == 0 or rnd() < 0.1:
                continue
            e = 1 if rnd() < 0.6 else 1 + int(rnd() * e)
            if x * p ** e > MAXV:
                e = 1
            if x * p ** e <= MAXV:
                x *= p ** e
                ps.append(p ** e)
        if rnd() < 0.5:
            while x * 23 > MAXV:
                x //= ps.pop()
            x *= 23
        qs.append(x)
    return qs


def case(n, q, weights, late=0.4, none=0.45, raw=0.0, hard=0.0):
    b = build_array(n, weights, raw)
    add(b.a, queries(b, q, late, none, n, hard))


random.seed(150101)
# samples
add([4, 6, 9, 10, 7], [12, 36, 8, 1, 35, 18])
add([10, 15, 7], [6, 7, 4])
add([1], [1, 2])
add([12, 18, 5, 49, 15], [180, 7, 49, 60])
add([7, 1, 14, 3], [2, 21, 1, 9])
# hidden: small (brute checks these)
ALL = {"big": 1, "semi": 1, "pow": 2, "smooth": 3, "mixed": 2}
for seed, n, q in [(1, 10, 30), (2, 60, 200), (3, 300, 1000), (4, 3000, 3000)]:
    random.seed(150200 + seed)
    case(n, q, ALL, raw=0.2)
random.seed(150301)
add([1] * 50, [1, 2, 3, 9999991, 1, 10000000])
random.seed(150302)
add([2 ** 23] * 3 + [3 ** 14, 5 ** 10, 7 ** 8], [2 ** 23, 2 ** 22 * 2, 3 ** 14, 3 ** 13, 5 ** 10, 7 ** 8, 7 ** 8 * 1, 6, 10 ** 7])
random.seed(150303)
case(2500, 4000, {"pow": 4, "smooth": 2}, late=0.6, none=0.35)
# hidden: big, each with its own seed
BIG = [
    (150401, dict(weights=ALL, raw=0.3)),
    (150402, dict(weights={"big": 1}, late=0.5, none=0.45)),
    (150404, dict(weights={"pow": 2, "smooth": 1}, late=0.55, none=0.4)),
    (150405, dict(weights={"smooth": 1}, late=0.5, none=0.45)),
    (150406, dict(weights={"mixed": 1}, late=0.45, none=0.45)),
    (150409, dict(weights=ALL, late=0.2, none=0.75)),
    (150413, dict(weights=ALL, raw=1.0, late=0.0, none=0.6)),
    (150414, dict(weights={"big": 3, "pow": 1, "semi": 1}, late=0.45, none=0.5)),
    # values and queries whose factorisation needs the most trial divisions
    (150418, dict(weights={"semihi": 1}, late=0.2, none=0.1, hard=0.7)),
    (150419, dict(weights={"semihi": 1, "big": 1}, late=0.2, none=0.2, hard=0.6)),
    (150420, dict(weights={"top": 1}, late=0.1, none=0.1, hard=0.8)),
    (150421, dict(weights={"top": 1, "semihi": 1}, late=0.3, none=0.2, hard=0.5)),
]
for seed, kw in BIG:
    random.seed(seed)
    case(MAXN, MAXQ, **kw)
# primes <= 19 only in the last values, queries made of many of their powers: every prime power of x
# first divides some a_k near the end, or never (23)
for seed, w in [(150431, {"big": 1}), (150432, {"top": 1, "semihi": 1}), (150433, {"big": 2, "semihi": 1})]:
    random.seed(seed)
    b = build_array(MAXN, w, tail=40)
    add(b.a, tiny_queries(b, MAXQ))
# the whole array equal to one big prime, all queries asking for that prime or more
random.seed(150417)
p = 9999991
add([p] * MAXN, [p if rnd() < 0.3 else 2 for _ in range(MAXQ)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
