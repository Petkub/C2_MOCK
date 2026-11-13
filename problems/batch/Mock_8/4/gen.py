# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A person is (t, v); the arrival t + L / v is the fraction (t v + L) / v. Every test is checked for distinct starts
# and distinct exact arrivals.
# "Chains" are groups of people where everyone meets everyone (starts increasing, arrivals decreasing, speeds
# increasing). "Near pairs" are two speeds v < w whose fractional parts of L / v and L / w differ by less than
# 1.1e-7; placed with starts s and s + (L div v) - (L div w), the two arrivals differ by that tiny amount. Only pairs
# whose two arrivals round to the same double (t + L / v and (t v + L) / v) are kept: for starts near 9e8 this
# depends only on v and w, since integers do not move the arrival on the double grid of [2^29, 2^30).
import gc, os, random
from collections import Counter
from itertools import repeat
from operator import add as add_, mul, truediv

gc.disable()                      # many small tuples: the cycle collector only costs time here
random.seed(80412)
rnd = random.random
MAXN, MAXL, MAXT, MAXV = 200000, 10 ** 9, 10 ** 9, 10 ** 4
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def arr(t, v, L):
    # the arrival as the nearest double (int / int is correctly rounded): equal arrivals give equal doubles
    return (t * v + L) / v


def arrivals(L, T, V):
    return list(map(truediv, map(add_, map(mul, T, V), repeat(L)), V))


def add(L, T, V):
    """a test from the starts T and speeds V (lists of the same length)"""
    n = len(T)
    assert 1 <= n <= MAXN and len(V) == n and 1 <= L <= MAXL
    assert 0 <= min(T) and max(T) <= MAXT and 1 <= min(V) and max(V) <= MAXV
    assert len(set(T)) == n
    fl = arrivals(L, T, V)
    if len(set(fl)) < n:                  # equal doubles: compare those arrivals exactly
        twice = {x for x, c in Counter(fl).items() if c > 1}
        groups = {}
        for i in [i for i, x in enumerate(fl) if x in twice]:
            groups.setdefault(fl[i], []).append((T[i], V[i]))
        for g in groups.values():
            for a in range(len(g)):
                for b in range(a + 1, len(g)):
                    (t1, v1), (t2, v2) = g[a], g[b]
                    assert (t1 * v1 + L) * v2 != (t2 * v2 + L) * v1
    both = [0] * (2 * n)
    both[0::2], both[1::2] = T, V
    tests.append("%d %d\n" % (n, L) + ("%d %d\n" * n) % tuple(both))


def add_pairs(L, ppl):
    add(L, [t for t, v in ppl], [v for t, v in ppl])


def shuffled(T, V):
    key = [rnd() for _ in T]
    idx = sorted(range(len(T)), key=key.__getitem__)
    return [T[i] for i in idx], [V[i] for i in idx]


def mix(T, V, extra):
    """T, V (already in random order) with the people (t, v) of extra put at random places"""
    pos = sorted(int(rnd() * (len(T) + 1)) for _ in extra)
    et, ev = shuffled([t for t, v in extra], [v for t, v in extra])
    ot, ov, prev = [], [], 0
    for p, t, v in zip(pos, et, ev):
        ot.extend(T[prev:p])
        ov.extend(V[prev:p])
        ot.append(t)
        ov.append(v)
        prev = p
    ot.extend(T[prev:])
    ov.extend(V[prev:])
    return ot, ov


def rand_people(n, L, tlo, thi, vlo, vhi, used_t=None, used_a=None):
    """n random people in random order (lists T, V) with distinct starts and distinct arrival doubles;
    if given, starts not in used_t and arrival doubles not in used_a (both updated)"""
    T, V = [], []
    tsp, vsp = thi - tlo + 1, vhi - vlo + 1
    while len(T) < n:
        m = (n - len(T)) * 11 // 10 + 16
        d = dict(zip([tlo + int(rnd() * tsp) for _ in range(m)], [vlo + int(rnd() * vsp) for _ in range(m)]))
        if used_t:
            d = {t: v for t, v in d.items() if t not in used_t}
        ct, cv = list(d), list(d.values())
        da = dict(zip(arrivals(L, ct, cv), range(len(ct))))
        if used_a:
            da = {a: i for a, i in da.items() if a not in used_a}
        idx = list(da.values())[:n - len(T)]
        if len(idx) < len(ct):
            ct, cv = [ct[i] for i in idx], [cv[i] for i in idx]
        T += ct
        V += cv
        if len(T) < n or used_a is not None:
            if used_t is None:
                used_t, used_a = set(), set()
            used_t.update(ct)
            used_a.update(arrivals(L, ct, cv))
    return T, V


def near_pairs(L, vlo=1000, dmax=1.1e-7):
    """disjoint near pairs (v, w, meet) chosen greedily by w; meet: the earlier starter arrives later"""
    order = sorted(range(vlo, MAXV + 1), key=lambda v: (L % v) / v)
    found = []
    for i in range(len(order) - 1):
        for j in range(i + 1, min(i + 4, len(order))):
            a, b = order[i], order[j]
            num = (L % a) * b - (L % b) * a
            if num != 0 and abs(num) < dmax * a * b:
                v, w = min(a, b), max(a, b)
                s = 900000000            # every start in [2^29, 2^30 - 10^6] gives the same rounding
                if collapse(s, v, s + L // v - L // w, w, L):
                    found.append((v, w, (L % v) * w - (L % w) * v > 0))
    found.sort(key=lambda p: p[1])
    out, end = [], -1
    for p in found:
        if p[0] > end + 40:
            out.append(p)
            end = p[1]
    return out


def collapse(s1, v1, s2, v2, L):
    return s1 + L / v1 == s2 + L / v2 and (s1 * v1 + L) / v1 == (s2 * v2 + L) / v2


def chain(L, speeds, s0, pairs=None, tight=0.0):
    """people forming a chain: speeds increasing; pairs = {v: w} near pairs (w follows v in speeds).
    tight: probability of taking the latest possible start (arrival just below the previous one).
    Returns (people, size of the largest group inside the chain)."""
    pairs = pairs or {}
    out = []
    an, ad = None, 1          # smallest arrival so far, as a fraction an / ad
    s_last = s0 - 1
    skip_next = False
    lost = 0
    for idx, u in enumerate(speeds):
        if skip_next:
            skip_next = False
            continue
        lo = s_last + 1
        if an is None:
            hi = lo + (1000 if u in pairs else 0)
        else:
            hi = (an * u - L * ad - 1) // (ad * u)   # largest s with s + L / u < an / ad
        if hi < lo:
            continue
        w = pairs.get(u)
        if w is not None:
            assert speeds[idx + 1] == w
            d = L // u - L // w
            ok = False
            for _ in range(400):
                s = ri(lo, hi)
                s2 = s + d
                if not collapse(s, u, s2, w, L):
                    continue
                if an is not None and (s2 * w + L) * ad >= an * w:
                    continue
                ok = True
                break
            assert ok, (u, w)
            out.append((s, u))
            out.append((s2, w))
            a1, a2 = (s * u + L, u), (s2 * w + L, w)
            if a2[0] * a1[1] > a1[0] * a2[1]:   # the later starter arrives later: no meeting
                lost += 1
                an, ad = a1
            else:
                an, ad = a2
            s_last = s2
            skip_next = True
            continue
        s = hi if rnd() < tight else ri(lo, hi)
        out.append((s, u))
        an, ad = s * u + L, u
        s_last = s
    return out, len(out) - lost


def chain_speeds(lo, hi, p, pairs):
    """increasing speeds in [lo, hi], each kept with probability p, the near pairs consecutive,
    nothing in (v - 40, w) of a pair except v and w"""
    banned = set()
    for v, w in pairs.items():
        banned.update(range(v - 40, w + 1))
    sp = [u for u in range(lo, hi + 1) if u not in banned and rnd() < p]
    sp += [x for v, w in pairs.items() for x in (v, w)]
    return sorted(sp)


def near_test(L, kinds, n, p, base=None):
    """one long chain near t = 9e8 containing near pairs of the given kinds (True = meeting pair),
    plus random people (t <= 3 10^7) who all finish before the chain starts.
    base: random people (T, V) to reuse, moved by a random time and rotated (add() rechecks the arrivals)"""
    np_ = [q for q in near_pairs(L) if q[2] in kinds]
    pairs = {v: w for v, w, m in np_}
    sp = chain_speeds(1000, MAXV, p, pairs)
    s0 = ri(900000000, 990000000)
    ppl, best = chain(L, sp, s0, pairs, tight=0.3)
    assert max(t for t, v in ppl) <= MAXT
    if base is None:
        T, V = rand_people(n - len(ppl), L, 0, 2 * 10 ** 7, 2, MAXV)
    else:
        m, off, r = n - len(ppl), ri(0, 10 ** 7), ri(0, len(base[0]) - 1)
        T, V = base[0][r:] + base[0][:r], base[1][r:] + base[1][:r]
        T, V = [t + off for t in T[:m]], V[:m]
        assert len(T) == m
    assert 3 * 10 ** 7 + L // 2 < s0           # the others finish before the chain starts
    return mix(T, V, ppl), best, len(np_)


# samples
add_pairs(600, [(50, 1), (0, 2), (40, 4), (10, 3), (100, 6)])
add_pairs(100, [(0, 5), (30, 1), (10, 2)])
add_pairs(46, [(3, 2), (2, 6), (15, 2), (27, 7), (20, 3), (28, 1)])
add_pairs(1000, [(158, 1), (288, 9), (9, 8), (69, 5), (207, 2), (232, 4), (97, 15)])
add_pairs(60, [(17, 4), (39, 9), (36, 4), (37, 1), (12, 1), (40, 1), (15, 5), (38, 5)])

# hidden: small and medium (brute checks these)
add_pairs(MAXL, [(MAXT, MAXV)])
LM = 528921005                                   # its near pairs are all meeting pairs
pm = near_pairs(LM)
assert len(pm) >= 5 and all(m for v, w, m in pm)
v, w, _ = pm[0]
add_pairs(LM, chain(LM, [v, w], ri(900000000, 950000000), {v: w})[0][::-1])     # 2 people who just meet
LN = 530907473                                   # its near pairs never meet
pn = near_pairs(LN)
assert len(pn) >= 5 and not any(m for v, w, m in pn)
v, w, _ = pn[-1]
add_pairs(LN, chain(LN, [v, w], ri(900000000, 950000000), {v: w})[0])           # 2 who just miss each other
for n, L, tm, vm in ((15, 40, 60, 8), (2000, 500, 10 ** 6, 50)):
    add(L, *rand_people(n, L, 0, tm, 1, vm))
ppl, best, k = near_test(906199897, (True, False), 3000, 0.02)
assert k >= 5
add(906199897, *ppl)
add(MAXL, *rand_people(5000, MAXL, 0, 10 ** 5, 5000, MAXV))

# hidden: big (N = 200000)
N = MAXN
add(MAXL, *rand_people(N, MAXL, 0, MAXT, 1, MAXV))
L = ri(1, 1000)
add(L, *rand_people(N, L, 0, MAXT, 1, MAXV))
L = ri(9 * 10 ** 8, MAXL)
add(L, *rand_people(N, L, 0, 10 ** 6, 5000, MAXV))
L = ri(9 * 10 ** 8, MAXL)
add(L, *rand_people(N, L, 0, MAXT, 1, 100))

# every speed 1..10^4 in one chain (answer 10^4) plus random people
L = MAXL
ppl, best = chain(L, list(range(1, MAXV + 1)), ri(0, 1000), tight=0.5)
assert best == MAXV
used_t = {t for t, v in ppl}
used_a = {arr(t, v, L) for t, v in ppl}
add(L, *mix(*rand_people(N - len(ppl), L, 0, MAXT, 1, MAXV, used_t, used_a), ppl))

# nobody meets: speeds never increase in start order (answer 1)
L = ri(10 ** 8, MAXL)
ts = sorted(set(ri(0, MAXT) for _ in range(N + 1000)))[:N]
vs = sorted((ri(1, MAXV) for _ in range(N)), reverse=True)
add(L, *shuffled(ts, vs))

# many short chains with tight gaps in separate time windows, plus random people
L = ri(5 * 10 ** 8, MAXL)
used_t, used_a, ppl = set(), set(), []
s0 = 0
while len(ppl) < N // 2:
    lo = ri(500, 3000)
    sp = sorted(u for u in range(lo, MAXV + 1) if rnd() < 0.15)
    part, _ = chain(L, sp, s0, tight=0.8)
    part = [q for q in part if q[0] not in used_t and arr(q[0], q[1], L) not in used_a][:N - len(ppl)]
    ppl += part
    used_t.update(t for t, v in part)
    used_a.update(arr(t, v, L) for t, v in part)
    s0 = ri(s0 + 1, s0 + L // lo)
    assert s0 <= MAXT - L // 500
T, V = rand_people(N - len(ppl), L, 0, MAXT, 1, MAXV, used_t, used_a)
add(L, *shuffled([t for t, v in ppl] + T, [v for t, v in ppl] + V))

# one long chain with near pairs (arrivals that differ by less than 1.1e-7) plus random people before it
base = rand_people(N - 1000, 685663189, 0, 2 * 10 ** 7, 2, MAXV)
for L, kinds in ((528921005, (True,)), (530907473, (False,)), (664333013, (True, False)),
                 (802944641, (True, False)), (837840583, (True, False)), (685663189, (True, False))):
    ppl, best, k = near_test(L, kinds, N, 0.6, base)
    assert k >= 5
    add(L, *ppl)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
