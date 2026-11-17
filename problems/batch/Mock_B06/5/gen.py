# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The beads l..r reduce to the path between two nodes of the trie of prefix rows (the row left after
# beads 1..l-1 and after beads 1..r), read upwards from the first node and then downwards.
# The big tests make the trie deep (depth above 2^17), branchy, with long upward parts, and use long ranges,
# so a stack per query is too slow; k is spread over both parts of the path and past its end (answer -1).
import os, random

random.seed(20261117)
rnd = random.random
MAXN, MAXQ, MAXC = 200000, 80000, 10 ** 9
N, Q = MAXN, MAXQ
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def depths(c):
    """dep[i] = number of beads left after beads 1..i (a stack)"""
    st, dep = [], [0]
    for x in c:
        if st and st[-1] == x:
            st.pop()
        else:
            st.append(x)
        dep.append(len(st))
    return dep


def add(c, qs):
    n, q = len(c), len(qs)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert all(1 <= x <= MAXC for x in c)
    assert all(1 <= l <= r <= n and 1 <= k <= r - l + 1 for l, r, k in qs)
    lines = ["%d %d" % (n, q), " ".join(map(str, c))]
    lines += ["%d %d %d" % t for t in qs]
    tests.append("\n".join(lines) + "\n")


def pick_k(dep, l, r):
    """k over the reduced row (its length is at most dep[l-1] + dep[r]) and a bit past it"""
    ln = r - l + 1
    t = rnd()
    if t < 0.1:
        k = ri(1, ln)
    elif t < 0.2:
        k = 1
    else:
        k = ri(1, min(ln, dep[l - 1] + dep[r] + 2))
    return k


def queries(c, q, mode="long"):
    n = len(c)
    dep = depths(c)
    qs = []
    for _ in range(q):
        if mode == "long":                       # long ranges (a stack per query is too slow)
            l, r = ri(1, n // 4), ri(3 * n // 4, n)
        elif mode == "pref":                     # l = 1
            l, r = 1, ri(n // 2, n)
        elif mode == "mix":
            if rnd() < 0.7:
                l, r = ri(1, n // 3), ri(2 * n // 3, n)
            else:
                l = ri(1, n)
                r = ri(l, n)
        else:                                    # anywhere (small tests)
            l = ri(1, n)
            r = ri(l, n)
        qs.append((l, r, pick_k(dep, l, r)))
    return qs


def rand_colours(n, m, base=1):
    return [base + int(rnd() * m) for _ in range(n)]


def walk(n, m, phases, base=1):
    """a walk on the trie: each phase (length share, push probability); a push adds a colour from m colours
    (not the top one), a pop repeats the top colour"""
    c, st = [], []
    tot = sum(p[0] for p in phases)
    for share, pp in phases:
        for _ in range(int(n * share / tot)):
            if st and rnd() >= pp:
                c.append(st.pop())
            else:
                x = base + int(rnd() * m)
                while st and x == st[-1]:
                    x = base + int(rnd() * m)
                st.append(x)
                c.append(x)
    while len(c) < n:
        c.append(base + int(rnd() * m))
    return c[:n]


def mountains(n, m, h, base=1):
    """repeated climbs of about h beads then falls of random depth: long branches off a deep trunk"""
    c, st = [], []
    while len(c) < n:
        for _ in range(ri(h // 2, h)):
            x = base + int(rnd() * m)
            while st and x == st[-1]:
                x = base + int(rnd() * m)
            st.append(x)
            c.append(x)
        for _ in range(ri(0, h // 2 + h // 4)):
            if st:
                c.append(st.pop())
    return c[:n]


# samples
add([4, 2, 2, 4, 4, 1, 5, 5], [(1, 4, 1), (2, 7, 2), (4, 8, 1), (3, 8, 3)])
add([1, 2, 3, 3, 2, 1, 1, 2], [(1, 6, 1), (1, 8, 2), (3, 5, 1), (2, 8, 1)])
add([7, 7, 7], [(1, 3, 1), (1, 2, 1), (2, 3, 2)])
add([3, 1, 4, 1, 5, 9, 2, 6], [(2, 4, 3), (1, 8, 8), (5, 8, 2)])
add([10, 20, 20, 30, 30, 10, 40, 10, 10, 40], [(1, 10, 1), (2, 9, 2), (7, 10, 2), (1, 7, 1), (4, 7, 2)])
# hidden: small and medium (brute checks these)
add([1000000000], [(1, 1, 1)])
c = rand_colours(12, 2)
add(c, queries(c, 30, "any"))
c = walk(40, 3, [(1, 0.6), (1, 0.4)])
add(c, queries(c, 60, "any"))
c = mountains(300, 4, 40)
add(c, queries(c, 300, "any"))
c = walk(2000, 3, [(1, 0.7), (1, 0.35), (1, 0.6)])
add(c, queries(c, 2000, "mix"))
c = rand_colours(3000, 2)
add(c, queries(c, 3000, "any"))
c = mountains(3000, 10 ** 9, 200)
add(c, queries(c, 3000, "mix"))
# hidden: big (n = 200 000, q = 80 000)
c = mountains(N, 3, 3000)
add(c, queries(c, Q))
c = walk(N, 3, [(7, 0.97), (1, 0.1), (2, 0.9)])                   # deeper than 2^17
add(c, queries(c, Q))
c = mountains(N, 10 ** 5, 1000)
add(c, queries(c, Q, "mix"))
c = walk(N, 3, [(6, 0.95), (1, 0.3), (2, 0.8)])                    # deeper than 2^17, then branches
add(c, queries(c, Q))
c = walk(N, 1000, [(9, 0.95), (1, 0.05)])                          # a trunk deeper than 2^17
add(c, queries(c, Q))
c = walk(N, 2, [(1, 0.75), (1, 0.25), (1, 0.75), (1, 0.25)])
add(c, queries(c, Q))
c = walk(N, 5, [(1, 0.6), (1, 0.4)] * 5)
add(c, queries(c, Q, "mix"))
c = rand_colours(N, 2)
add(c, queries(c, Q, "mix"))
c = rand_colours(N, 4)
add(c, queries(c, Q))
c = rand_colours(N, 10 ** 5)                                        # nothing cancels: one long path
add(c, queries(c, Q))
c = [7] * N                                                        # one colour
add(c, queries(c, Q))
h = rand_colours(N // 2, 3)
c = h + h[::-1]                                                    # the whole row vanishes
add(c, queries(c, Q))
c = mountains(N, 3, 5000)
add(c, queries(c, Q, "pref"))
c = walk(N, 1000, [(8, 0.99), (2, 0.3)], MAXC - 999)               # colours near 10^9, deep
add(c, queries(c, Q)[:45000])                                      # fewer queries: keeps the input near 3 MB
c = mountains(N, 2, 100)
add(c, queries(c, Q, "mix"))
c = walk(N, 3, [(4, 0.95), (1, 0.45), (3, 0.9)])
add(c, queries(c, Q))
h = rand_colours(N // 4, 50)
c = h + rand_colours(N // 4, 50) + h[::-1] + rand_colours(N // 4, 50)
add(c, queries(c, Q))
c = mountains(N, 6, 60000)
add(c, queries(c, Q))
c = walk(N, 4, [(8, 0.93), (2, 0.5)])
add(c, queries(c, Q, "mix"))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
assert len(tests) <= 35
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
