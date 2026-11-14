# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random, re

random.seed(1203001)
MAXLINE, MAXK = 10 ** 6, 10 ** 9
tests = []


def enc(runs, ones="omit"):
    """runs: list of (letter, count); a count of 1 is omitted, written, or either at random"""
    out = []
    for c, k in runs:
        assert 1 <= k <= MAXK and "a" <= c <= "z"
        if k == 1 and (ones == "omit" or (ones == "mix" and random.random() < 0.5)):
            out.append(c)
        else:
            out.append(c + str(k))
    return "".join(out)


def add(a, b):
    for s in (a, b):
        assert 1 <= len(s) <= MAXLINE and re.fullmatch(r"[a-z][a-z0-9]*", s)
        for num in re.findall(r"[0-9]+", s):
            assert num[0] != "0" and 1 <= int(num) <= MAXK
    tests.append(a + "\n" + b + "\n")


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(random.random() * (b - a + 1))


def rruns(n, kmax, alpha="ab", kmin=1):
    m = len(alpha)
    return [(alpha[int(random.random() * m)], ri(kmin, kmax)) for _ in range(n)]


def resplit(runs, parts=3):
    """the same string written with differently split runs (same letter runs may be adjacent)"""
    out = []
    for c, k in runs:
        while k > 1 and random.random() < 0.5 and parts > 0:
            x = ri(1, k - 1)
            out.append((c, x))
            k -= x
        out.append((c, k))
    return out


def merge(runs):
    out = []
    for c, k in runs:
        if out and out[-1][0] == c and out[-1][1] + k <= MAXK:
            out[-1] = (c, out[-1][1] + k)
        else:
            out.append((c, k))
    return out


def mutate(runs, cnt, alpha):
    """change cnt random runs at one position each (split the run and put other letters in)"""
    hit = set(random.randrange(len(runs)) for _ in range(cnt))
    out = []
    for i, (c, k) in enumerate(runs):
        if i not in hit:
            out.append((c, k))
            continue
        d = random.choice([x for x in alpha if x != c] or ["z"])
        x = random.randint(0, k - 1)
        if x:
            out.append((c, x))
        out.append((d, random.randint(1, 3)))
        if k - x - 1 > 0:
            out.append((c, k - x - 1))
    return out


def fit(runs, limit=MAXLINE):
    """keep the longest prefix of runs whose encoding fits in limit characters"""
    total, out = 0, []
    for c, k in runs:
        w = 1 + len(str(k))          # the count of 1 may be written
        if total + w > limit:
            break
        total += w
        out.append((c, k))
    return out


# samples
add("a3b2c", "a2b3c1")
add("x2y", "x2y4")
add("p2q3r", "p3r2s")
add("m10n5", "m7m3o5")
add("z", "y1000000000")

# hidden: small (brute checks these)
for n, kmax, alpha in [(3, 3, "ab"), (10, 5, "ab"), (50, 20, "abc"), (200, 50, "ab"), (1000, 30, "abcd")]:
    A = rruns(n, kmax, alpha)
    B = rruns(n + random.randint(-n // 3, n // 3), kmax, alpha)
    add(enc(A, "mix"), enc(B, "mix"))
A = rruns(500, 100, "ab")
add(enc(A), enc(resplit(A)))                                   # equal strings, different runs
add(enc(A), enc(resplit(A) + [("a", 1)]))                      # one longer
add(enc(mutate(A, 1, "ab")), enc(resplit(A)))                  # one changed spot
add("q", "q")
add("ab2", "a1b1b1")                                         # equal, written differently
add("q1", "r")

# hidden: big (each line up to 10^6 characters; lengths up to ~10^14)


def big(seed, make):
    random.seed(seed)
    a, b = make()
    add(a, b)


def same(kmax, alpha, n=110000, kmin=1):
    A = fit(rruns(n, kmax, alpha, kmin), 600000)
    return enc(A, "mix"), enc(fit(resplit(A), MAXLINE), "mix")


def near(kmax, alpha, cnt, extra=None, n=100000, kmin=1):
    A = fit(rruns(n, kmax, alpha, kmin), 550000)
    B = resplit(mutate(A, cnt, alpha))
    if extra:
        B += extra
    return enc(A), enc(fit(B, MAXLINE), "mix")


def rand(kmax, alpha, kmin=1):
    A = fit(rruns(120000, kmax, alpha, kmin))
    B = fit(rruns(120000, kmax, alpha, kmin))
    return enc(A), enc(B)


big(1204001, lambda: same(MAXK, "ab", kmin=MAXK // 2))                    # equal, about 5 * 10^13 long
big(1204002, lambda: near(MAXK, "abc", 1, kmin=10 ** 8))
big(1204003, lambda: near(MAXK, "ab", 50))
big(1204004, lambda: rand(MAXK, "ab"))
big(1204005, lambda: rand(MAXK, "ab", MAXK - 1000))
big(1204006, lambda: rand(10, "abc"))
big(1204007, lambda: near(MAXK, "xy", 0, [("x", MAXK)] * 3))            # equal prefix, the second is longer
big(1204008, lambda: (enc([("a", MAXK)] * 90000 + [("b", 1)]), enc([("a", MAXK)] * 90000 + [("c", 1)])))
big(1204009, lambda: (enc([("a", MAXK)] * 45000), enc([("a", MAXK // 2)] * 90000)))       # equal
big(1204010, lambda: (enc([("a", MAXK)] * 45000), enc([("a", MAXK // 2)] * 89999 + [("a", MAXK // 2 - 1)])))
big(1204011, lambda: (enc([("a", 1)] * MAXLINE), enc([("a", 1)] * (MAXLINE - 1) + [("b", 1)])))
big(1204012, lambda: (enc(rruns(MAXLINE, 1, "ab")), enc(rruns(MAXLINE, 1, "ab"))))
big(1204013, lambda: (enc([("a", MAXK)] * 90000), "b" + str(MAXK)))
big(1204014, lambda: near(10 ** 5, "abcdefghijklmnopqrstuvwxyz", 300))
big(1204015, lambda: near(MAXK, "ab", 100000))
big(1204016, lambda: (enc([("z", MAXK)] * 90000), enc([("z", MAXK - 1)] * 90000)))
big(1204017, lambda: same(10 ** 6, "abc"))
big(1204018, lambda: near(MAXK, "ab", 3, [("b", 7)], kmin=MAXK - 10))
big(1204019, lambda: rand(MAXK, "a"))

for t in tests:
    assert t.endswith("\n") and " " not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
