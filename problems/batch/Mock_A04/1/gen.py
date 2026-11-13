# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# '.' = free stall, '#' = rented stall; stall N is next to stall 1.
import math, os, random

random.seed(20261113)
rnd = random.random
MAXN, MAXQ = 200000, 200000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(s, ks):
    n, q = len(s), len(ks)
    assert 1 <= n <= MAXN and 1 <= q <= MAXQ
    assert set(s) <= {".", "#"}
    assert all(1 <= k <= n for k in ks)
    tests.append(f"{n} {q}\n{s}\n" + " ".join(map(str, ks)) + "\n")


def dens(n, p):
    """each stall rented with probability p"""
    return "".join("#" if rnd() < p else "." for _ in range(n))


def blocks(lengths):
    """free runs of the given lengths, each followed by one rented stall"""
    return "#".join("." * x for x in lengths) + "#"


def rotate(s, r):
    return s[r:] + s[:r]


def small_ks(q, hi):
    return [ri(1, hi) for _ in range(q)]


def mixed_ks(q, n, lo, hi):
    """mostly k in [lo, hi], a few anywhere in [1, n]"""
    return [ri(lo, hi) if rnd() < 0.9 else ri(1, n) for _ in range(q)]


N, Q = MAXN, MAXQ
# samples
add("..#...#...", [1, 2, 3, 4])
add("#.##..", [3, 1, 2])
add(".#..#....#..", [2, 1, 4, 3, 5])
add("...##.#.....#..", [5, 2, 1, 7])
add("#...#..#.#....#.#...", [1, 3, 2, 4, 6, 5])
# hidden: small (brute checks these)
add(".", [1])
add("#", [1, 1])
add(".....", [1, 2, 3, 4, 5])
add("#######", [1, 4, 7])
add(".....#..", list(range(1, 9)))
add("." * 50, [ri(1, 50) for _ in range(40)] + [50, 49, 1, 50])
add(dens(30, 0.3), [ri(1, 30) for _ in range(30)])
add("." * 13 + dens(10, 0.6) + "." * 9, list(range(1, 33)))       # long run across stall N and stall 1
add(dens(300, 0.15), [ri(1, 60) for _ in range(300)])
add(rotate(blocks([4, 4, 1, 7, 7, 2, 4]), 3), list(range(1, 36)))
# hidden: big (N = Q = 200000)
add("." * N, [N if rnd() < 0.2 else ri(1, N) for _ in range(Q)])                 # all free
add("." * N, [N - ri(0, 2) if rnd() < 0.5 else ri(1, 5) for _ in range(Q)])      # all free, k near N
add("#" * N, small_ks(Q, N))                                                       # all rented
p = ri(N // 4, 3 * N // 4)
add("." * p + "#" + "." * (N - p - 1), small_ks(Q, 3))                            # one rented stall
add("#" + "." * (N - 1), mixed_ks(Q, N, 1, 10))                                    # one rented, stall 1
add("." * (N - 1) + "#", [N - 1 if rnd() < 0.3 else ri(1, N - 1) for _ in range(Q)])  # one rented, stall N
add(".#" * (N // 2), small_ks(Q, 2))                                               # 100000 runs of 1
add(rotate("..#" * (N // 3) + ".." , 1), small_ks(Q, 3))                          # about 66666 runs of 2
lens, tot, x = [], 0, 1
while tot + x + 1 <= N:                                                            # many different lengths
    lens.append(x)
    tot += x + 1
    x += 1
random.shuffle(lens)
s = blocks(lens)
add(s + "#" * (N - len(s)), small_ks(Q // 4, 3))
lens = [ri(1, 3) for _ in range(30000)]
s = blocks(lens)
big = N - len(s)
add(rotate(s + "." * big, len(s) + big // 2), small_ks(Q, 2))                      # one long run across the cut
add(dens(N, 0.5), small_ks(Q, 4))
add(dens(N, 0.5), mixed_ks(Q, N, 1, 25))
add(dens(N, 0.08), mixed_ks(Q, N, 1, 150))
add(dens(N, 0.0015), mixed_ks(Q, N, 1, 1200))
add(dens(N, 0.92), small_ks(Q, 3))
a, b = 70000, 60000
s = "." * a + dens(N - a - b - 2, 0.4).join("##") + "." * b                       # the longest run crosses the cut
add(s, [ri(100000, a + b) if rnd() < 0.7 else ri(1, 20) for _ in range(Q)])
lens, tot = [], 0
while tot < N - 7000:
    lens.append(min(int(-8 * math.log(1 - rnd())) + 1, 5000))       # mostly short, some long
    tot += lens[-1] + 1
s = blocks(lens)
add(rotate(s + dens(N - len(s), 0.3), ri(0, N - 1)), mixed_ks(Q, N, 1, 80))
s = "." * 99999 + "#" + "." * 99999 + "#"
add(rotate(s, 50000), [99999 if rnd() < 0.3 else ri(1, 99999) for _ in range(Q)])      # two equal runs
lens, tot = [], 0
while tot < N - 4000:                                                              # short runs and a few long ones
    lens.append(ri(1, 3) if rnd() < 0.998 else ri(500, 3000))
    tot += lens[-1] + 1
s = blocks(lens)
add(rotate(s + "#" * (N - len(s)), ri(0, N - 1)), small_ks(Q, 2))
add(dens(N, 0.3), [ri(1, N) for _ in range(Q)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
