# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(7011)
rnd = random.random
MAXN, MAXR = 200000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(L, R, s):
    n = len(s)
    assert 1 <= n <= MAXN
    assert 1 <= L <= R <= MAXR
    assert all("0" <= c <= "9" for c in s)
    tests.append(f"{n} {L} {R}\n{s}\n")


def digits(n, zero=0.1, first_nonzero=True):
    """random digits; a digit is 0 with probability `zero`"""
    out = []
    for i in range(n):
        if rnd() < zero and not (i == 0 and first_nonzero):
            out.append("0")
        else:
            out.append(str(ri(1, 9)))
    return "".join(out)


def price(L, R, tail):
    """a price in [L, R]; with probability `tail` its last few digits are set to 0"""
    while True:
        v = ri(L, R)
        if rnd() < tail:
            k = ri(1, len(str(v)) - 1) if v >= 10 else 0
            v = v // 10 ** k * 10 ** k
        if L <= v <= R:
            return v


def prices(n, L, R, tail=0.0, pick=None):
    """a concatenation of prices in [L, R] with about n digits (so at least one split exists)"""
    parts, length = [], 0
    while length < n - 12:
        v = pick() if pick else price(L, R, tail)
        parts.append(str(v))
        length += len(parts[-1])
    return "".join(parts)


# samples
add(10, 300, "284155")
add(1, 50, "7005")
add(5, 99, "1036512168")
add(1000, 500000, "3997528820018263")
add(20, 400, "146304175")

# hidden: small (brute tries every split on these)
add(1, 9, "5")
add(1, 9, "0")
add(1, 1000, "0123")                                   # starts with 0
add(10, 10, "1010101010")
add(100, 999, "1000")                                  # the 0 left over: no split
add(1, 1000000000, "10000000001000000000")             # only 10-digit prices work for the zeros
add(100000000, 1000000000, "1000000000100000000")      # 9-digit + 10-digit, nothing shorter
add(1, 1000000000, digits(18, 0.15))                    # 10-digit pieces exceed int
add(10, 999, prices(18, 10, 999, 0.6))
add(1, 120, prices(16, 1, 120, 0.7))
add(3, 90, prices(18, 3, 90, 0.5))
add(500, 2000, prices(18, 500, 2000, 0.6))

# hidden: big
add(1, MAXR, digits(MAXN, 0.1))                        # random digits, every price allowed
add(1, MAXR, digits(MAXN, 0.02))
add(10, 999, prices(MAXN, 10, 999, 0.5))
add(10, 999, digits(MAXN, 0.0))                         # no zeros at all
add(100, 99999, prices(MAXN, 100, 99999, 0.6))
add(1000, 5000000, prices(MAXN, 1000, 5000000, 0.7))
add(100000000, 999999999, prices(MAXN, 100000000, 999999999, 0.3))   # totals near 2 * 10^13
add(100000000, MAXR, prices(MAXN, 100000000, MAXR, 0.0,
                            lambda: MAXR if rnd() < 0.4 else ri(100000000, 999999999)))
add(1, MAXR, prices(MAXN, 1, MAXR, 0.0, lambda: MAXR if rnd() < 0.3 else 10 ** ri(0, 8) * ri(1, 9)))
add(50000000, MAXR, digits(MAXN, 0.05))
add(5, 70, prices(MAXN, 5, 70, 0.6))
add(2, 30, digits(MAXN, 0.0))
add(1, 100, prices(MAXN, 1, 100, 0.8))
add(40, 400, prices(MAXN, 40, 400, 0.4))
add(1, MAXR, "1" + "0" * (MAXN - 1))                    # one long price is too big
add(10, 999, prices(MAXN - 20, 10, 999, 0.5) + "0" * 3)  # the end cannot be split
add(123456, 7654321, prices(MAXN, 123456, 7654321, 0.5))
add(1, MAXR, "9" * MAXN)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
