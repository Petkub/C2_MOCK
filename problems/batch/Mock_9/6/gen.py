# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(960602)
rnd = random.random
MAXN, MAXA, MAXB = 100000, 10 ** 9, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(jobs, shuffle=True):
    n = len(jobs)
    assert 1 <= n <= MAXN
    for a, b in jobs:
        assert 0 <= a <= MAXA and -MAXB <= b <= MAXB
    jobs = list(jobs)
    if shuffle:
        random.shuffle(jobs)
    tests.append(f"{n}\n" + "".join(f"{a} {b}\n" for a, b in jobs))


def uniform(n, amax, bmax, pgain=0.5, bmin=None):
    """needs in [0, amax], changes of size up to bmax; a gain with probability pgain"""
    lo = 0 if bmin is None else bmin
    out = []
    for _ in range(n):
        b = ri(lo, bmax)
        if rnd() >= pgain:
            b = -max(b, 1)
        out.append((ri(0, amax), b))
    return out


def chain(n, pgain, step, slack, start):
    """a schedule that works from `start`: every job's need is at most `slack` below the reputation it is
    done with (in the generated order), changes up to `step`; the input is shuffled"""
    out, r = [], start
    ng = int(n * pgain)
    for i in range(n):
        if i < ng:
            b = ri(0, step)
        else:
            b = -ri(1, min(step, r)) if r > 0 else 0
        a = max(0, r - ri(0, slack))
        out.append((min(a, MAXA), b))
        r += b
    return out


def mixed_losses(n, big):
    """losses whose need and size are unrelated: a + b differs from a and from b in order"""
    out = []
    for _ in range(n):
        b = -ri(1, big)
        out.append((ri(0, MAXA), b))
    return out


# samples
add([(3, 2), (0, 1), (6, -4), (4, -3)], False)
add([(2, -3), (0, 2), (5, -1)], False)
add([(10, 5), (0, 3), (8, -7), (12, -2), (1, 4)], False)
add([(0, 0), (7, -7)], False)
add([(4, 1), (9, -2), (2, -2), (0, 6), (6, -3), (3, 2)], False)
# hidden: small (brute checks these)
add([(0, 5)])
add([(1000000000, -1000000000)])
add([(0, -1000000000), (0, 1000000000)])
add(uniform(8, 20, 15))
add(uniform(12, 50, 40, 0.3))
add(uniform(15, 1000, 1000, 0.5))
add(chain(16, 0.4, 30, 10, 25))
add(uniform(18, 10 ** 9, 10 ** 9, 0.5))
add(mixed_losses(17, 10 ** 9))
# hidden: big (N = 100000)
N = MAXN
add(uniform(N, MAXA, MAXB))
add(uniform(N, MAXA, 10 ** 4))
add(uniform(N, 1000, MAXB))
add(uniform(N, MAXA, MAXB, 0.1))
add(uniform(N, MAXA, MAXB, 0.9))
add(mixed_losses(N, MAXB))
add(mixed_losses(N, 10 ** 5))
add(uniform(N // 2, MAXA, MAXB, 1.0) + mixed_losses(N // 2, MAXB))
add(chain(N, 0.3, 10 ** 4, 10 ** 4, 10 ** 8))
add(chain(N, 0.5, 10 ** 6, 10 ** 5, 10 ** 9))
add(chain(N, 0.1, 10 ** 3, 10 ** 3, 10 ** 7))
add(chain(N, 0.6, 10 ** 9, 10 ** 9, 10 ** 9))
add([(MAXA, MAXB)] * N)                                  # all gains at the largest values
add([(MAXA, -MAXB)] * N)                                 # all losses at the largest values
add([(ri(0, MAXA), MAXB) for _ in range(N - 1)] + [(MAXA, -MAXB)])
add([(ri(0, 10), -ri(1, MAXB)) for _ in range(N)])       # needs tiny: only "never below 0" matters
add([(ri(0, MAXA), 0) for _ in range(N)])                # no change at all
add(uniform(N, MAXA, MAXB, 0.5, MAXB // 2))
add(uniform(N, MAXA, 10 ** 6, 0.2))
add(chain(N, 0.0, 10 ** 4, 10 ** 9, 10 ** 9))
# losses whose need is about the size of the loss (a = -b + d, d small): a + b, a and b give three different orders
# (kills "losses by a", "smallest loss first" and a "best available now" check that forgets a job can stop being
# available after the reputation drops)
add([(ri(0, MAXA), ri(0, MAXB)) if rnd() < 0.3 else (lambda b: (-b + ri(0, 10 ** 6), b))(-ri(1, MAXB - 10 ** 6))
     for _ in range(N)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
