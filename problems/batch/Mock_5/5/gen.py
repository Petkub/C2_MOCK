# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(50005)
MAXN, MAXH = 300_000, 10**6
tests = []


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


def add(h):
    n = len(h)
    assert 1 <= n <= MAXN
    assert all(1 <= x <= MAXH for x in h)
    tests.append(f"{n}\n" + " ".join(map(str, h)) + "\n")


def rnd(n, v):
    return [ri(1, v) for _ in range(n)]


def perm(n):
    p = list(range(1, n + 1))
    random.shuffle(p)
    return p


def teeth(n, small, base=None):
    """peaks rising by one at even positions, small heights in [1, small] at odd positions:
    every peak sees the whole row on its left and one small height on its right"""
    if base is None:
        base = small
    return [base + i // 2 + 1 if i % 2 else ri(1, small) for i in range(n)]


def mountain_teeth(n, small):
    half = n // 2
    left = teeth(half, small)
    right = teeth(n - half, small)[::-1]
    return left + right


def valley_teeth(n, small):
    half = n // 2
    return teeth(half, small)[::-1] + teeth(n - half, small)


def ruler(n, noise):
    """height grows with the number of trailing zero bits of the position: a balanced shape where
    both sides of every maximum are equally long"""
    return [((i & -i).bit_length()) * noise + ri(1, noise - 1) for i in range(1, n + 1)]


def perm_mountain(n):
    """a permutation rising to n then falling; each smaller number goes to a random side"""
    up, down = [], []
    for x in range(1, n):
        (up if random.random() < 0.5 else down).append(x)
    return up + [n] + down[::-1]


def blocks(n, k, v):
    """runs of k small heights separated by single taller ones"""
    h = []
    while len(h) < n:
        h += [ri(1, v) for _ in range(k)]
        h.append(ri(v, 2 * v))
    return h[:n]


def spine(n, small, base):
    """n heights: peaks base + 1, base + 2, ... at odd positions, small heights in [1, small] between"""
    return [base + i // 2 + 1 if i % 2 else ri(1, small) for i in range(n)]


def in_mountain(content, total):
    """the content followed by a mountain of teeth taller than all of it (total length `total`)"""
    k = total - len(content)
    top, small = max(content), min(max(content), 1000)
    return content + spine(k // 2, small, top) + spine(k - k // 2, small, top)[::-1]


def in_valley(content, total):
    """falling teeth, the content, rising teeth: both sides of every tooth reach across the content"""
    k = total - len(content)
    top, small = max(content), min(max(content), 1000)
    return spine(k // 2, small, top)[::-1] + content + spine(k - k // 2, small, top)


# samples
add([1, 3, 2, 5, 3, 2])
add([1, 2, 1, 2, 1])
add([7])
add([3, 1, 2, 4, 1, 3, 6])
add([2, 5, 3, 3, 8, 2, 6, 4, 2, 9])
# hidden: small (checked by trying every segment)
add([1, 2])
add([4, 4, 4, 4, 4])
add(rnd(60, 6))
add(rnd(400, 3))
add(perm(3000))
add(in_mountain(rnd(1500, 20), 4000))
add(in_valley(rnd(2000, 4), 5000))
add(in_valley(perm_mountain(1000), 3000))
add(ruler(4096, 20))
# hidden: maximum size. Teeth around the data (and mountain/valley shapes) make walking the longer side,
# always the left or always the right side, or finding each maximum by a scan quadratic; balanced and random
# shapes make pairing the two sides directly quadratic; repeated small heights give answers above 2^31.
N, H = MAXN, MAXN // 2
add(perm(N // 2))
add(ruler(N, 1000))
add(ruler(N, 30))
add(in_mountain(rnd(H, 10), N))
add(in_valley(rnd(H, 1000), N))
add(in_mountain(rnd(H, 3), N))
add(in_valley(ruler(H, 30), N))
add(in_mountain(perm(H), N))
add(in_valley([1] * (H // 2) + [2] + [1] * (H // 2), N))
add(in_mountain([random.choice((1, 1, 1, 2)) for _ in range(H)], N))
add(in_valley(blocks(H, 300, 500), N))
add(in_mountain([7] * H, N))
# heights near 450 000 pair up to the height 900 000
add(in_valley([900_000 if random.random() < 0.1 else 450_000 + ri(-50, 50) for _ in range(H)], N))
add(in_mountain(rnd(H, MAXH - N), N))
add(teeth(N, N // 2))
add(teeth(N, 1000)[::-1])
add(mountain_teeth(N, N // 4))
add(valley_teeth(N, 10))
add(perm_mountain(N))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
