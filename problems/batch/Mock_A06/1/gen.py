# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A command is 1 (east), -1 (west) or 0 (north, starts a new row).
import os, random

random.seed(60111)
rnd = random.random
MAXN = 200000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(cmds):
    n = len(cmds)
    assert 1 <= n <= MAXN
    assert all(x in (-1, 0, 1) for x in cmds)
    tests.append(f"{n}\n{' '.join(map(str, cmds))}\n")


def rand_row(m, pw):
    """m east/west moves, each west with probability pw"""
    return [-1 if rnd() < pw else 1 for _ in range(m)]


def tie_row(k, cheap):
    """k west and k east moves; keeping every `cheap` move costs fewer deletions than keeping the other side:
    the other side starts and ends the row, so all `cheap` moves lie inside its span"""
    other = -cheap
    x = ri(1, max(1, k // 10))
    y = ri(1, max(1, k // 10))
    mid = [other] * (k - x - y) + [cheap] * k
    random.shuffle(mid)
    return [other] * x + mid + [other] * y


def block_row(m, major, pieces, tail):
    """`major` moves in runs separated by short opposite runs, then `tail` opposite moves at the end"""
    row, left = [], m
    for _ in range(pieces):
        if left <= 0:
            break
        t = min(left, ri(1, 2 * m // pieces + 1))
        row += [major] * t + [-major] * ri(0, 3)
        left -= t
    return row + [-major] * tail


def short_rows(total, maker):
    """rows made by maker() joined by 0, about `total` commands"""
    out = []
    while len(out) < total:
        out += maker() + [0]
    return out[:total]


def short_tie():
    k = ri(1, 6)
    return tie_row(k, random.choice([1, 1, -1])) if k > 1 else [1, -1]


def short_any():
    m = ri(0, 12)
    return rand_row(m, random.choice([0.2, 0.5, 0.8]))


# samples
add([1, -1, 1, 1, 0, -1])
add([0, 1, 1, -1, -1, 0])
add([-1, 1, -1, 1, -1, 0, -1, 1, -1, 1, 1, 1, 0, 0])
add([0])
add([1, 1, -1, 1, 0, 1, -1, 1, 1, -1, -1, -1, -1])

# hidden: small (brute tries every set of kept commands)
add([1])
add([-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1])
add([-1, 1, 1, -1, 1, -1])                             # tie: keeping the east moves is cheaper
add([1, -1, -1, 1, 0, 1, 1, -1, -1, 0, -1, 1, 1, -1])  # tie rows with both choices
add([0, 0, 1, -1, 1, -1, 1, -1, 1, -1, 0, 0])
add([1, 1, 1, -1, -1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1])
add([-1, 1, 1, 1, -1, -1, 1, -1, -1, -1, 1, 1, -1, 0, 1, -1, -1, 1])

# hidden: medium, many short rows
add(short_rows(60000, short_tie))
add(short_rows(70000, short_any))
add([0] * 60000)

# hidden: big; every big test has one row of at least 120 000 moves
L = 130000
add(rand_row(MAXN, 0.5))                                                 # one row, nearly a tie
add(rand_row(MAXN, 0.7))
add(rand_row(MAXN - 1, 0.3) + [0])
add(tie_row(MAXN // 2, 1))                                               # tie, keep east
add(tie_row(MAXN // 2 - 30000, -1) + [0] + short_rows(59999, short_tie))
add(short_rows(MAXN - L - 1, short_tie) + [0] + tie_row(L // 2, 1))
r = block_row(L, 1, 400, 2000)                                           # east wins, west moves at the end
add(r + [0] + short_rows(MAXN - len(r) - 1, short_any))
r = block_row(L - 10000, -1, 3000, 1000)
add(short_rows(MAXN - len(r) - 1, short_any) + [0] + r)
add([-1] * MAXN)                                                         # nothing to delete
add([1] * (MAXN // 2) + [-1] * (MAXN // 2))                              # tie, both cost 0
add([(1 if i % 2 == 0 else -1) for i in range(MAXN)])                    # zigzag
add([(1 if i % 3 else -1) for i in range(MAXN)])
add(rand_row(L, 0.5) + [0] + short_rows(MAXN - L - 1, short_tie))
add([0] * 30000 + rand_row(MAXN - 60000, 0.45) + [0] * 30000)
add(tie_row(68000, 1) + [-1] * 2 + tie_row(31000, -1))                   # one row, west wins by 2
add(rand_row(L, 0.55) + [0] + [ri(-1, 1) for _ in range(MAXN - L - 1)])

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
