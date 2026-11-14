# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A monster's "first trap" is the first trap at or to the right of it; d = its distance to that trap.
import os, random

random.seed(82025)
rnd = random.random
MAXN, MAXM, MAXV = 100000, 100000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(mons, xs):
    n, m = len(mons), len(xs)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    assert all(1 <= a <= MAXV and 1 <= h <= MAXV for a, h in mons)
    assert all(1 <= x <= MAXV for x in xs) and len(set(xs)) == m
    tests.append(f"{n} {m}\n" + "".join(f"{a} {h}\n" for a, h in mons) + " ".join(map(str, xs)) + "\n")


def shuffle(v):
    for i in range(len(v) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        v[i], v[j] = v[j], v[i]
    return v


def traps(m, lo, hi):
    """m distinct positions in [lo, hi], in random order"""
    assert hi - lo + 1 >= m
    seen, out = set(), []
    while len(out) < m:
        x = ri(lo, hi)
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def first_trap(xs):
    s = sorted(xs)

    def f(a):
        lo, hi = 0, len(s)
        while lo < hi:
            mid = (lo + hi) // 2
            if s[mid] < a:
                lo = mid + 1
            else:
                hi = mid
        return s[lo] if lo < len(s) else None
    return f


def rand_mons(n, lo, hi, hlo, hhi):
    return [(ri(lo, hi), ri(hlo, hhi)) for _ in range(n)]


def tie_mons(n, xs, lo, hi, p_tie):
    """health = d for a share p_tie of the monsters, health < d (or a fireball-only monster) for the others,
    so that many traps have no monster closer than its health but one with d == h"""
    f = first_trap(xs)
    out = []
    for _ in range(n):
        a = ri(lo, hi)
        t = f(a)
        if t is None or t == a:
            out.append((a, ri(1, 1000)))
        elif rnd() < p_tie:
            out.append((a, t - a))
        else:
            out.append((a, ri(1, t - a)))
    return out


def on_traps(n, xs, share, hlo, hhi, lo, hi):
    """a share of the monsters stand exactly on a trap"""
    out = []
    for _ in range(n):
        a = xs[int(rnd() * len(xs))] if rnd() < share else ri(lo, hi)
        out.append((a, ri(hlo, hhi)))
    return out


N, M = MAXN, MAXM
# samples
add([(3, 2), (5, 6), (6, 3), (9, 4)], [7, 10])
add([(1, 4), (6, 7), (12, 5)], [4, 9])
add([(15, 9), (28, 4), (6, 9), (16, 3)], [20, 27, 17])
add([(5, 2), (12, 3), (29, 8), (11, 9)], [14, 19, 21])
add([(11, 9), (17, 7), (14, 1), (11, 1)], [6, 21, 19])
# hidden: small and medium (brute checks these)
add([(5, 7)], [5])                                                     # on the trap
add([(9, 4)], [3])                                                     # right of the only trap
xs = traps(40, 1, 400)
add(tie_mons(300, xs, 1, 420, 0.3), xs)                                # d == h
xs = traps(60, 1, 600)
add(on_traps(300, xs, 0.5, 1, 30, 1, 650), xs)                         # monsters on traps
xs = traps(50, 1, 5000)
add(rand_mons(400, 1, 5200, 1, 150), xs)                               # many traps with nobody worth it
xs = traps(250, 1, 10 ** 9)
add(rand_mons(2000, 1, MAXV, 1, MAXV), xs)
xs = traps(300, 1, 10 ** 6)
add(rand_mons(2000, 1, 10 ** 6, 1, 6000), xs)
xs = traps(200, 1, 10 ** 5)
add(rand_mons(2000, 10 ** 5 + 1, MAXV, MAXV - 1000, MAXV), xs)         # all right of every trap, big sum
xs = traps(300, 10 ** 8, 2 * 10 ** 8)
add(rand_mons(1500, 1, 10 ** 8, MAXV // 2, MAXV), xs)                  # all left of every trap, big distances
# hidden: max size (some with most monsters right of most traps, some with most monsters left of them)
xs = traps(M, 1, MAXV)
add(rand_mons(N, 1, MAXV, 1, MAXV), xs)                                # uniform
xs = traps(M, 1, MAXV)
add(rand_mons(N, 1, MAXV, 1, 20000), xs)                               # health ~ the gaps: mixed
xs = traps(M, 1, MAXV)
add(rand_mons(N, 1, MAXV, 1, 3000), xs)                                # mostly arrows
xs = traps(M, 1, MAXV)
add(tie_mons(N, xs, 1, MAXV, 0.25), xs)                                # d == h
xs = traps(M, 1, 3 * 10 ** 6)
add(tie_mons(N, xs, 2 * 10 ** 6, 3 * 10 ** 6, 0.5), xs)                # d == h, dense, right third
xs = traps(M, 1, MAXV)
add(on_traps(N, xs, 0.5, 1, 10 ** 6, 1, MAXV), xs)                     # on traps
xs = traps(M, 1, 10 ** 6)
add(on_traps(N, xs, 0.7, 1, 50, 1, 10 ** 6), xs)                       # on traps, dense, small health
xs = traps(M, 1, 10 ** 6)
add(rand_mons(N, 10 ** 6 + 1, MAXV, MAXV - 10 ** 6, MAXV), xs)         # all right of every trap
xs = traps(M, 9 * 10 ** 8, MAXV)
add(rand_mons(N, 1, 9 * 10 ** 8, MAXV // 2, MAXV), xs)                 # all left of every trap
xs = traps(M, 1, 2 * 10 ** 8)
add(rand_mons(N, 1, MAXV, 1, 10 ** 6), xs)                             # traps on the left
xs = traps(M, 1, 4 * 10 ** 5)
add(rand_mons(N, 1, 2 * 10 ** 6, 1, 5), xs)                            # dense, tiny health, traps on the left
xs = traps(M, 1, 2 * 10 ** 6)
add(tie_mons(N, xs, 1, 4 * 10 ** 5, 0.3), xs)                          # d == h, monsters left of most traps
xs = traps(M, 1, MAXV)
pos = [ri(1, MAXV // 10) for _ in range(450)] + [ri(1, MAXV) for _ in range(50)]
add([(pos[int(rnd() * 500)], ri(1, 10 ** 6)) for _ in range(N)], xs)      # few positions, many monsters each
xs = traps(M, 1, MAXV)
add(shuffle(rand_mons(N * 9 // 10, 1, 10 ** 8, 1, 10 ** 6) + rand_mons(N // 10, 1, MAXV, 1, MAXV)), xs)
xs = traps(M, 8 * 10 ** 8, MAXV)
add(shuffle(rand_mons(N // 2, 1, 8 * 10 ** 8, 1, 200) + rand_mons(N // 2, 8 * 10 ** 8, 10 ** 9, 1, 200000)), xs)
xs = traps(M, 1, MAXV)
add(on_traps(N, xs, 0.3, 1, 30000, 9 * 10 ** 8, MAXV), xs)            # on traps, the others far right

os.makedirs("tests", exist_ok=True)
for k, t in enumerate(tests, 1):
    with open(f"tests/{k:02d}.in", "w") as f:
        f.write(t)
