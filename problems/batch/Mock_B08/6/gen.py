# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# After each new member the answer is the least number of digits to append so that no code is a prefix of another.
# Rerunning the one-shot greedy for every prefix is O(N * total length): every big test has N and the total length
# near the limits. Fitting each new member into the codes chosen so far is wrong: the big tests put short codes
# first and longer codes under them later, so the earlier choices have to be redone.
import os, random

random.seed(20240317)
rnd = random.random
MAXN, MAXL = 200000, 400000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(codes):
    n = len(codes)
    assert 1 <= n <= MAXN
    total = 0
    for c in codes:
        assert len(c) >= 1 and set(c) <= set("01")
        total += len(c)
    assert total <= MAXL
    tests.append("%d\n%s\n" % (n, "\n".join(codes)))


def bits(k):
    return "".join("1" if rnd() < 0.5 else "0" for _ in range(k))


def shuffled(a):
    a = list(a)
    for i in range(len(a) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        a[i], a[j] = a[j], a[i]
    return a


def fill(codes, n, total, maker):
    """append codes from maker() until n codes or the total length would pass `total`"""
    used = sum(len(c) for c in codes)
    while len(codes) < n:
        c = maker()
        if used + len(c) > total - (n - len(codes) - 1):
            c = bits(1)
        codes.append(c)
        used += len(c)
    return codes


def rand_short(n, lo, hi, total=MAXL):
    return fill([], n, total, lambda: bits(ri(lo, hi)))


def from_pool(n, pool, total=MAXL, tail=0):
    """codes drawn from a few base codes, each maybe followed by up to `tail` random digits"""
    return fill([], n, total, lambda: pool[int(rnd() * len(pool))] + bits(ri(0, tail)))


def short_then_long(n, base, total=MAXL):
    """first the short codes (often equal), then longer codes below them: earlier choices must change"""
    half = n // 2
    first = [base[int(rnd() * len(base))] for _ in range(half)]
    rest = []
    used = sum(map(len, first))
    while len(first) + len(rest) < n:
        c = base[int(rnd() * len(base))] + bits(ri(1, 3))
        if used + len(c) > total - (n - len(first) - len(rest) - 1):
            c = bits(1)
        rest.append(c)
        used += len(c)
    return first + rest


# samples
add(["1", "1", "1"])
add(["10", "1", "0", "11"])
add(["0", "01", "0011", "010", "01"])
add(["1", "0", "1", "1", "10", "0"])
add(["0", "0", "100", "000", "000", "11", "111"])
# hidden: small (brute checks these)
add(["0"])
add(["0", "1", "0", "1", "00", "11"])
for k in range(4):
    add(rand_short(ri(5, 12), 1, 4))
add(from_pool(30, ["1", "10", "0110", "011"], tail=2))
add(short_then_long(40, ["0", "1", "01"]))
add(rand_short(50, 1, 7))
# hidden: big (N and the total length near the limits)
add(["1"] * MAXN)                                                  # one code repeated
add(["0" if rnd() < 0.5 else "1" for _ in range(MAXN)])
add(rand_short(MAXN, 1, 3))                                        # heavy duplicates
add(rand_short(MAXN, 1, 4))
add(short_then_long(MAXN, ["0", "1", "10", "01", "110"]))
add(short_then_long(MAXN, ["1"]))
add(short_then_long(MAXN, [bits(1) for _ in range(2)] + [bits(2) for _ in range(3)]))
add(sorted(rand_short(MAXN, 1, 3), key=len))                        # shortest first
add(sorted(rand_short(MAXN, 1, 3), key=len, reverse=True))          # longest first
add(from_pool(MAXN, ["0", "00", "000", "0000", "1", "11"], tail=0))
full = [format(i, "017b") for i in range(1 << 17)][: MAXL // 17]    # a full binary trie, depth 17
full = shuffled(full)
add(fill(full[:12000], MAXN, MAXL, lambda: bits(1)))
add(fill(shuffled(full)[:12000], 150000, MAXL, lambda: full[int(rnd() * len(full))][: ri(1, 16)]))
chain = ["1" * k for k in range(1, 601)]                           # every code a prefix of the next
add(chain[:600] + fill([], MAXN - 600, MAXL - 180300, lambda: "1" * ri(1, 3) if rnd() < 0.7 else bits(ri(1, 3))))
add(fill(shuffled(chain[:600]), MAXN, MAXL, lambda: "1" * ri(1, 2)))
add(fill([bits(60000)] + ["1"] * 1000, MAXN, MAXL, lambda: bits(ri(1, 2))))
deep = bits(100000)
add(fill([], MAXN, MAXL, lambda: deep[: ri(1, 4)] if rnd() < 0.9 else deep[: ri(1, 3000)]))
add(fill([], MAXN, MAXL, lambda: deep[: ri(1, 3)] + bits(ri(0, 1))))
# few duplicates, long codes: fitting each newcomer in is fast here, so it fails by wrong answers
add([bits(ri(12, 22)) for _ in range(23000)])


def pairs(prefix_first, total=MAXL - 10000):
    codes, used = [], 0
    while used < total:
        b = bits(ri(14, 20))
        p = b[: ri(8, len(b))]
        part = [p, b] if prefix_first else ([b, p] if rnd() < 0.5 else [b])
        codes += part
        used += sum(map(len, part))
    return codes


add(pairs(False))                                                  # a code, sometimes later its prefix
add(pairs(True))                                                   # a prefix, then the longer code


def clusters(total=MAXL - 10000):
    codes, used = [], 0
    while used < total:
        b = bits(ri(10, 16))
        part = [b] * ri(1, 3) + [b + bits(ri(1, 2)) for _ in range(ri(0, 3))]
        codes += part
        used += sum(map(len, part))
    return codes


add(clusters())

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
