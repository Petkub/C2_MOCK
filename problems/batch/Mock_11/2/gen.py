# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(910101)
MAXN, MAXA, MAXC = 100000, 10 ** 9, 10 ** 4
tests = []


def add(a, c):
    n = len(a)
    assert 1 <= n <= MAXN and len(c) == n
    assert all(-MAXA <= x <= MAXA for x in a) and all(1 <= x <= MAXC for x in c)
    tests.append(f"{n}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, c)) + "\n")


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def clamp(x):
    return max(-MAXA, min(MAXA, x))


def cs(n, lo, hi):
    return [ri(lo, hi) for _ in range(n)]


def skew(n):
    """flexibilities of very different sizes: many large, a few tiny"""
    return [ri(1, 3) if random.random() < 0.05 else ri(100, MAXC) for _ in range(n)]


def noisy_line(n, start, step, noise):
    """a_i = start + i * step + noise (a rising or falling line)"""
    return [clamp(start + i * step + ri(-noise, noise)) for i in range(n)]


# samples
add([6, 2, 9, 4, 3], [1, 3, 2, 1, 2])
add([0, 0, 0, 0], [3, 1, 1, 3])
add([-5, 1, 2, 8], [4, 1, 1, 7])
add([1000000000], [1])
add([-7, 12, -30, 5, 5, 41, 0], [2, 5, 1, 1, 3, 10, 4])
# hidden: small (brute checks these)
add([3, 3], [1, 1])
add([-1000000000, 1000000000], [1, 1])
add([1000000000, -1000000000], [1, 1])
add([ri(-10, 10) for _ in range(8)], cs(8, 1, 3))
add([ri(-100, 100) for _ in range(50)], cs(50, 1, 10))
add([ri(-MAXA, MAXA) for _ in range(300)], cs(300, 1, MAXC))
add(noisy_line(1500, 5000, -3, 40), cs(1500, 1, 20))
add([7] * 2000, skew(2000))
add(noisy_line(2000, -MAXA, 900000, 3000000), cs(2000, 1, 50))
add([ri(-MAXA, MAXA) for _ in range(3000)], skew(3000))
# hidden: big (N = 100000)
N = MAXN
add([ri(-MAXA, MAXA) for _ in range(N)], cs(N, 1, MAXC))
add([ri(-MAXA, MAXA) for _ in range(N)], cs(N, 1, 20))
add([ri(-MAXA, MAXA) for _ in range(N)], skew(N))
add(noisy_line(N, MAXA - 10 ** 6, -19000, 10 ** 6), cs(N, 1, MAXC))       # falling line
add(noisy_line(N, MAXA - 10 ** 6, -19000, 10 ** 6), skew(N))
add(noisy_line(N, -MAXA, 19000, 3 * 10 ** 8), cs(N, 1, 100))              # rising line with big noise
add(noisy_line(N, -MAXA, 20000, 10 ** 7), cs(N, 1, MAXC))
add(noisy_line(N, 0, 0, 10 ** 6), cs(N, 1, 1000))                          # a crowd around 0
a = [ri(-MAXA, MAXA) for _ in range(N)]
a[0], a[-1] = MAXA, -MAXA
c = cs(N, 5000, MAXC)
c[0] = c[-1] = 1
add(a, c)                                                                   # the answer exceeds 10^9
a = sorted(ri(-MAXA, MAXA) for _ in range(N))
for _ in range(30):                                                         # a sorted street with a few jumps
    i = ri(0, N - 1)
    a[i] = clamp(a[i] + ri(-10 ** 8, 10 ** 8))
add(a, cs(N, 1, MAXC))
a = sorted(ri(-MAXA, MAXA) for _ in range(N))
i = ri(N // 3, 2 * N // 3)
a[i], a[i + 1] = a[i + 1] + 5 * 10 ** 7, a[i] - 5 * 10 ** 7                  # one big local swap
add([clamp(x) for x in a], skew(N))
add([ri(-MAXA, MAXA) for _ in range(N)], [1] * N)                           # all flexibilities 1
add([ri(-MAXA, MAXA) for _ in range(N)], [MAXC] * N)                        # all flexibilities 10^4
add([5] * N, cs(N, 1, 3))                                                   # everybody at the same place
a = []
for blk in range(100):                                                      # rising blocks, each falling inside
    base = -MAXA + blk * 2 * 10 ** 7
    a += [base + 10 ** 7 - 5000 * j + ri(-2000, 2000) for j in range(N // 100)]
add(a, cs(N, 1, 50))
a = [MAXA - 20000 * i for i in range(N)]                                    # strictly falling, very flexible middle
add(a, [1 if i in (0, N - 1) or i % 997 == 0 else ri(5000, MAXC) for i in range(N)])
add(list(range(-N // 2, N - N // 2)), cs(N, 1, MAXC))                        # already in order: 0

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
