# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The answer sums C(c, 2) over the good stretches l..r, c = carriages inside whose colour is unique there.
# Big tests: N = 100000 with long gaps between equal colours (an O(N^2) sweep that stops at the previous
# equal colour still runs ~N^2 / 8 steps), colours repeated 2, 3, 4 or more times (a colour that comes back a
# third time must not be removed twice), answers near C(N, 4) > 2^62 (all colours different).
import os, random

random.seed(20210301)
MAXN = 100000
N = MAXN
tests = []


def add(b):
    n = len(b)
    assert 1 <= n <= MAXN and all(1 <= x <= n for x in b)
    tests.append(f"{n}\n" + " ".join(map(str, b)) + "\n")


def rand(n, k):
    return [random.randint(1, k) for _ in range(n)]


def perm(n):
    p = list(range(1, n + 1))
    random.shuffle(p)
    return p


def repeat(n, c):
    """a random order of n // c colours, written c times (n divisible by c)"""
    q = perm(n // c)
    return q * c


# samples
add([1, 2, 3, 1, 4, 2, 5])
add([2, 5, 1, 3, 6, 4])
add([2, 2, 2, 2, 2])
add([4, 1, 2, 4, 3, 2, 5, 1, 4])
add([12, 10, 5, 6, 4, 3, 1, 2, 9, 12, 3, 3])
# hidden: small and medium (brute checks these)
add([1])
add([1, 2, 3, 4])
add([1, 2, 1, 3])
add(rand(12, 4))
add(rand(50, 10))
add(rand(300, 30))
add(rand(3000, 200))
add(perm(3000))
add(rand(20000, 3))                                     # few colours, almost every stretch is bad
add(repeat(30000, 30))                                  # each colour 30 times
# hidden: big (N = 100000)
add(perm(N))                                            # every stretch good, answer C(N, 4)
add(list(range(1, N + 1)))
add(rand(N, N))
add(rand(N, N // 2))
add(rand(N, N // 4))
add(rand(N, N // 6))
add(repeat(N, 2))
add(repeat(N, 3))
add(repeat(N, 4))
q = perm(N // 2)
add(q + q[::-1])                                        # mirrored: gaps of every length
add([(i % (N // 4)) + 1 for i in range(N)])             # 1 2 .. N/4 four times
b = perm(N)
for i in range(N):                                      # a tenth of the carriages in 3 hot colours
    if random.random() < 0.1:
        b[i] = random.randint(1, 3)
add(b)
b = rand(N, N // 3)
b[-1] = b[0]                                            # first and last carriage share a colour
add(b)
add(perm(N // 2) + rand(N // 2, N // 6))                # a long clean half, then a repeating half
add(rand(N // 2, N // 6) + perm(N // 2))
add(perm(N)[: N // 2] + perm(N)[: N // 2])              # two distinct halves drawn from all N colours
add([x for pair in zip(perm(N // 2), perm(N // 2)) for x in pair])  # each colour twice, random gaps

assert 25 <= len(tests) <= 35
for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
