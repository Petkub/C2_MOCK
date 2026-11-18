# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(31021)
rnd = random.random
MAXN, MAXV, MAXD = 200000, 10 ** 18, 10 ** 12
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(S, d, t, shuffle=False):
    t = list(t)
    if shuffle:
        random.shuffle(t)
    n = len(t)
    assert 1 <= n <= MAXN
    assert 0 <= S <= MAXV and 1 <= d <= MAXD
    assert all(0 <= x <= MAXV for x in t)
    tests.append(f"{n} {S} {d}\n{' '.join(map(str, t))}\n")


def from_levels(S, d, levels, off=None):
    """child with level c arrives at S + c * d + offset (0 <= offset < d), so it can use c rounds of a pump"""
    out = []
    for c in levels:
        o = off() if off else ri(0, d - 1)
        out.append(S + c * d + o)
    return out


# samples
add(10, 5, [18, 15, 21, 20, 27])
add(4, 10, [20, 13, 30])
add(7, 2, [9, 18, 14, 30, 25])
add(8, 6, [27, 15, 16, 29, 21, 21, 29, 26])
add(999999999999, 10 ** 12, [1999999999999, 3000000000000, 2999999999999])

# hidden: small (brute matches children to pump rounds on these)
add(5, 3, [8])                                          # exactly S + d
add(5, 3, [7])                                          # one minute short
add(0, 1, [1, 1, 1, 1, 1, 1, 1, 1])                     # everyone at the first round
add(20, 4, [3, 30, 40, 50, 60])                         # a child before the staff arrives
add(0, 7, from_levels(0, 7, [1, 2, 2, 3, 3, 3, 4, 5], lambda: 6), True)   # offsets d - 1
add(3, 5, from_levels(3, 5, [1, 1, 2, 2, 2, 3, 3, 3], lambda: 0), True)   # arrivals exactly on a round
add(10 ** 18 - 9 * 10 ** 12, 10 ** 12, from_levels(10 ** 18 - 9 * 10 ** 12, 10 ** 12, [1, 1, 2, 3, 3, 4, 7, 8]), True)
add(6, 9, from_levels(6, 9, [2, 2, 2, 2, 2, 2, 2, 2]), True)
add(1, 4, from_levels(1, 4, [1, 1, 1, 2, 5, 6, 7, 8]), True)
add(100, 1000, [99 + 1000] + from_levels(100, 1000, [1, 2, 3, 4, 5, 6]), True)


# hidden: big (every answer is large or -1)
def big_s():
    return ri(0, 10 ** 9)


N = MAXN
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [1] * N), True)                                   # everyone in round 1: M = N
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [1] * (N // 4) + [2] * (N - N // 4)), True)        # M = N / 2
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [ri(1, 4) for _ in range(N)]), True)
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [ri(1, 3) for _ in range(N)], lambda: d - 1), True)  # offsets d - 1
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [ri(1, 3) for _ in range(N)], lambda: 0), True)      # exactly on a round
S, d = big_s(), ri(10 ** 6, 10 ** 9)
A = 61234
add(S, d, from_levels(S, d, [(k + A - 1) // A for k in range(1, N + 1)]), True)  # staircase, M = A
S, d = big_s(), ri(10 ** 6, 10 ** 9)
A = 45000
lv = [(k + A - 1) // A for k in range(1, N + 1)]
lv[2 * A] = 2                                     # one child a round earlier: M = A + 1
add(S, d, from_levels(S, d, lv, lambda: ri(d - 3, d - 1)), True)
S, d = big_s(), ri(10 ** 6, 10 ** 9)
lv = [1] * 1000 + [2] * 99000 + [ri(3, 1000) for _ in range(N - 100000)]     # tight in the middle
add(S, d, from_levels(S, d, lv), True)
S, d = big_s(), ri(10 ** 6, 10 ** 9)
lv = [ri(1, 2) for _ in range(N - 1)] + [0]                                    # one child at S + d - 1
add(S, d, from_levels(S, d, lv[:-1]) + [S + d - 1], True)
S, d = ri(10 ** 8, 10 ** 9), ri(10 ** 6, 10 ** 7)
add(S, d, from_levels(S, d, [ri(1, 3) for _ in range(N - 1)]) + [ri(0, S - 1)], True)   # before the staff
S, d = big_s(), 1
add(S, d, from_levels(S, d, [ri(1, 6) for _ in range(N)]), True)               # d = 1
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, sorted(from_levels(S, d, [ri(1, 5) for _ in range(N)])))             # sorted
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, sorted(from_levels(S, d, [ri(1, 5) for _ in range(N)]), reverse=True))   # reverse sorted
S, d = big_s(), ri(10 ** 6, 10 ** 9)
add(S, d, from_levels(S, d, [1] * 40000 + [ri(1, 40) for _ in range(N - 40000)]), True)
S, d = big_s(), ri(2, 9)
add(S, d, from_levels(S, d, [ri(1, 2) for _ in range(N)]), True)               # small d
N2 = 150000                                                                    # values near 10^18
S, d = MAXV - 4 * MAXD, MAXD
add(S, d, from_levels(S, d, [ri(1, 3) for _ in range(N2)], lambda: ri(MAXD - 1000, MAXD - 1)), True)
S, d = MAXV - 2 * MAXD - 1, MAXD
add(S, d, [S + MAXD + ri(0, MAXD - 1) for _ in range(N2 - 1)] + [MAXV], True)  # M = N - 1

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
