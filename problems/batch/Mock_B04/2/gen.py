# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1505)
MAXN, MAXC, V = 200000, 10 ** 9, 1000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (faster than randint, still deterministic)"""
    return a + int(rnd() * (b - a + 1))


def clamp(x):
    return max(1, min(V, x))


def add(C, a):
    assert 1 <= len(a) <= MAXN and 0 <= C <= MAXC
    assert all(1 <= x <= V for x in a)
    tests.append(f"{len(a)} {C}\n" + " ".join(map(str, a)) + "\n")


def walk(n, lo, hi, step):
    """a melody moving by at most `step` per note inside [lo, hi]"""
    x, out = ri(lo, hi), []
    for _ in range(n):
        x = max(lo, min(hi, x + ri(-step, step)))
        out.append(x)
    return out


def mix(n, parts, stay):
    """interleave melodies: parts = list of (lo, hi, step, weight); the next note comes from the same
    melody with probability `stay`, otherwise from a random melody chosen by weight"""
    cur = [ri(lo, hi) for lo, hi, _, _ in parts]
    tot = sum(w for _, _, _, w in parts)
    k, out = 0, []
    for _ in range(n):
        if rnd() >= stay:
            r = rnd() * tot
            k = 0
            while r >= parts[k][3]:
                r -= parts[k][3]
                k += 1
        lo, hi, step, _ = parts[k]
        cur[k] = max(lo, min(hi, cur[k] + ri(-step, step)))
        out.append(cur[k])
    return out


def rare(n, base, every, lo, hi):
    """a smooth melody with a note from far away about once in `every` notes"""
    return [ri(lo, hi) if rnd() * every < 1 else x for x in base]


def with_gaps(a, k, length):
    """k times: a far pitch X, a long quiet passage in a narrow band, then X again"""
    a = list(a)
    for _ in range(k):
        p = ri(0, len(a) - length - 2)
        lo = ri(1, 60) if rnd() < 0.5 else ri(900, V - 40)
        far = V if lo < 500 else 1
        a[p:p + length + 2] = [far] + walk(length, lo, lo + 40, 3) + [far]
    return a


# samples
add(3, [5, 1, 6, 2, 5, 1])
add(10, [4, 7, 5, 6])
add(0, [8])
add(4, [2, 9, 2, 3, 9, 8, 3, 9])
add(25, [40, 42, 100, 41, 43, 99, 40, 101, 44, 100])

# hidden: small (brute tries all ways up to N = 20, then a slower DP)
add(MAXC, [1, V])
add(0, [V, 1, V, 1, V])
for n, C, vmax in [(12, 2, 10), (16, 0, 20), (18, 5, 30), (20, 40, V), (20, 1, 4)]:
    add(C, [ri(1, vmax) for _ in range(n)])
add(30, mix(2000, [(1, 200, 20, 1), (800, V, 20, 1)], 0.6))
add(15, rare(3000, walk(3000, 300, 700, 15), 40, 1, V))
add(MAXC, [ri(1, V) for _ in range(5000)])

# hidden: big (each with its own seed)
N = MAXN
BIG = [
    (150501, lambda: (ri(25, 50), with_gaps([ri(1, V) for _ in range(N)], 3, 3000))),
    (150502, lambda: (0, [ri(1, V) for _ in range(N)])),
    (150503, lambda: (MAXC, [ri(1, V) for _ in range(N)])),
    (150504, lambda: (250, with_gaps([ri(1, 400) if i % 2 else ri(600, V) for i in range(N)], 2, 5000))),
    (150505, lambda: (150, with_gaps(mix(N, [(1, 450, 120, 1), (550, V, 120, 1)], 0.5), 3, 5000))),
    (150506, lambda: (120, with_gaps(mix(N, [(1, 200, 10, 1), (400, 600, 10, 1), (800, V, 10, 1)], 0.7), 3, 5000))),
    (150507, lambda: (60, rare(N, walk(N, 1, V, 8), 300, 1, V))),
    (150508, lambda: (150, rare(N, walk(N, 200, 800, 40), 2000, 1, V))),
    (150509, lambda: (7, [V // 2] * N)),
    (150510, lambda: (MAXC, [1 if i % 2 else V for i in range(N)])),
    (150511, lambda: (ri(300, 450), with_gaps([(1, V // 2, V)[ri(0, 2)] for _ in range(N)], 4, 2000))),
    (150512, lambda: (35, with_gaps([1 + (i * 37) % V for i in range(N)], 2, 4000))),
    (150513, lambda: (90, with_gaps(mix(N, [(1, V, 25, 5), (1, V, 25, 1)], 0.9), 3, 5000))),
    (150514, lambda: (60, mix(N, [(1, 300, 50, 20), (700, V, 50, 1)], 0.95))),
    (150515, lambda: (180, with_gaps(mix(N, [(1, 300, 30, 1), (700, V, 30, 1), (350, 650, 30, 1)], 0.3), 3, 3000))),
    (150516, lambda: (ri(6, 20), with_gaps(walk(N, 1, V, 60), 3, 5000))),
    (150517, lambda: (100, with_gaps([ri(1, 200) if (i // 1000) % 2 else ri(800, V) for i in range(N)], 3, 5000))),
]
for seed, make in BIG:
    random.seed(seed)
    add(*make())

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
