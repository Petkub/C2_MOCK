# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Each student is a subset of {M, P, C} (bit 1 = M, 2 = P, 4 = C), written as its letters in a random order or `-`.
# Many tests have at least 3 students with no subject (the - C(none, 3) term of the count); big tests have
# N = 200000 (answers up to ~1.3 * 10^15).
import os, random

random.seed(6022027)
rnd = random.random
MAXN = 200000
LET = "MPC"
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def word(mask):
    s = [LET[b] for b in range(3) if mask >> b & 1]
    for i in range(len(s) - 1, 0, -1):          # random letter order
        j = ri(0, i)
        s[i], s[j] = s[j], s[i]
    return "".join(s) if s else "-"


def add_words(ws):
    n = len(ws)
    assert 1 <= n <= MAXN
    for w in ws:
        assert w == "-" or (1 <= len(w) <= 3 and len(set(w)) == len(w) and set(w) <= set(LET))
    tests.append(f"{n}\n" + " ".join(ws) + "\n")


def add_masks(masks):
    add_words([word(m) for m in masks])


def weighted(n, w):
    """n masks, mask m with weight w[m]"""
    tot = sum(w)
    acc, out = [], 0
    for x in w:
        out += x
        acc.append(out / tot)
    res = []
    for _ in range(n):
        r = rnd()
        m = 0
        while m < 7 and r >= acc[m]:
            m += 1
        res.append(m)
    return res


# samples
add_words(["M", "P", "C", "MP", "M"])
add_words(["MC", "P", "PC", "C"])
add_words(["MPC", "-", "M", "P", "C", "MC"])
add_words(["PM", "C", "-", "CP", "M", "M", "P"])
add_words(["M", "MP", "P", "PC", "C", "CM", "-", "M"])
# hidden: small (brute checks these)
add_words(["MPC"])
add_words(["MPC", "MPC"])
add_words(["MPC", "-", "-"])
add_words(["M", "P", "-", "C", "-", "-", "-"])
add_masks([ri(0, 7) for _ in range(60)])
add_masks(weighted(300, [5, 3, 3, 1, 3, 1, 1, 0]))      # nobody good at everything, many with nothing
add_masks(weighted(400, [0, 4, 4, 1, 4, 1, 1, 0]))      # nobody with nothing
add_masks(weighted(500, [10, 1, 1, 1, 1, 1, 1, 1]))
add_masks(weighted(450, [1, 3, 3, 3, 0, 0, 0, 0]))      # nobody good at C: 0
add_masks(weighted(500, [2, 0, 0, 3, 0, 3, 3, 0]))      # pairs of subjects only
# hidden: big (N = 200000)
N = MAXN
add_masks([7] * N)                                       # every team
add_masks([0] * N)                                       # no team
add_masks([0] * (N - 3) + [1, 2, 4])                     # exactly one team
add_masks([ri(0, 7) for _ in range(N)])
add_masks([ri(0, 7) for _ in range(N)])
add_masks(weighted(N, [6, 3, 3, 1, 3, 1, 1, 0]))
add_masks(weighted(N, [1, 1, 1, 1, 1, 1, 1, 1000]))      # almost everyone good at everything
add_masks(weighted(N, [1000, 1, 1, 1, 1, 1, 1, 1]))      # almost everyone good at nothing
add_masks(weighted(N, [3, 1, 1, 0, 1, 0, 0, 0]))         # single subjects and nothing
add_masks(weighted(N, [0, 1, 1, 0, 1, 0, 0, 0]))
add_masks(weighted(N, [1, 0, 0, 5, 0, 5, 5, 0]))
add_masks(weighted(N, [4, 2, 2, 2, 2, 2, 2, 0]))
add_masks(weighted(N, [5, 1, 9, 1, 2, 1, 1, 0]))
add_masks(weighted(N, [1, 3, 3, 3, 0, 0, 0, 0]))         # nobody good at C: 0
add_masks(weighted(N, [2, 7, 0, 0, 1, 0, 0, 0]))         # few good at C
add_masks([0] * (N // 2) + [7] * (N // 2))
add_masks([ri(1, 7) for _ in range(N)])
add_masks(weighted(N, [9, 0, 0, 0, 0, 0, 0, 1]))
add_masks(weighted(N, [20, 1, 1, 0, 1, 0, 0, 0]))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
