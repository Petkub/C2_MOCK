# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(611101)
rnd = random.random
MAXD, MAXP, MAXS = 100000, 6, 1000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


ALL = ["M", "SB", "DB"] + [c + str(k) for c in "SDT" for k in range(1, 21)]
NEIGH = {20: (1, 5), 19: (7, 3), 18: (4, 1), 17: (3, 2), 16: (8, 7), 15: (10, 2), 14: (9, 11), 13: (6, 4),
         12: (5, 9), 11: (14, 8), 10: (6, 15), 9: (12, 14), 8: (11, 16), 7: (16, 19), 6: (13, 10), 5: (20, 12),
         4: (18, 13), 3: (19, 17), 2: (17, 15), 1: (18, 20)}


def value(t):
    if t == "M":
        return 0, False
    if t == "SB":
        return 25, False
    if t == "DB":
        return 50, True
    k = int(t[1:])
    return k * " SDT".index(t[0]), t[0] == "D"


def aim(c, skill):
    """the dart a player with points c throws (skill 0..1)"""
    r = rnd()
    if c == 50 and r < 0.5:
        return "DB" if rnd() < skill * 0.5 else ("SB" if rnd() < 0.7 else "S" + str(ri(1, 20)))
    if c <= 40 and c % 2 == 0:
        k = c // 2
        if r < skill * 0.6:
            return "D" + str(k)
        if r < 0.75:
            return "S" + str(k)
        if r < 0.85:
            return "D" + str(NEIGH[k][ri(0, 1)])
        if r < 0.95:
            return "M"
        return "S" + str(NEIGH[k][ri(0, 1)])
    if c <= 60:
        # leave an even number: aim at a single
        k = c - 32 if 1 <= c - 32 <= 20 else (c - 40 if 1 <= c - 40 <= 20 else (1 if c % 2 else 2))
        k = max(1, min(20, k))
        if r < 0.7:
            return "S" + str(k)
        if r < 0.8:
            return "T" + str(k)
        if r < 0.9:
            return "D" + str(k)
        return "S" + str(NEIGH[k][ri(0, 1)])
    target = 20 if rnd() < 0.7 else 19
    if r < skill * 0.45:
        return "T" + str(target)
    if r < 0.8:
        return "S" + str(target)
    if r < 0.9:
        return ("S", "T")[ri(0, 1)] + str(NEIGH[target][ri(0, 1)])
    if r < 0.93:
        return "D" + str(target)
    if r < 0.96:
        return "M"
    return ("SB", "DB")[ri(0, 1)]


def game(p, s, d, skill, noise, win_after=None, bull=False):
    """simulate a game of p players and at most d darts; nobody wins before dart `win_after`
    (None: wins are never allowed; bull: only a finish on DB is allowed); returns the dart list (it ends at the winning dart if any)"""
    pts = [s] * p
    darts = []
    who = 0
    c50 = bull and win_after is not None
    while len(darts) < d:
        start = cur = pts[who]
        for _ in range(3):
            if len(darts) >= d:
                break
            t = ALL[int(rnd() * len(ALL))] if rnd() < noise else aim(cur, skill[who])
            v, dbl = value(t)
            x = cur - v
            if c50 and len(darts) + 1 < win_after and 2 <= x < 52:
                t, v, dbl, x = "M", 0, False, cur                  # keep every player above 50 until the end
            if c50 and len(darts) + 1 >= win_after:              # going for 50, then the bull
                e = cur - 50
                t = ("DB" if e == 0 else "S" + str(e) if e <= 20 else "T" + str(e // 3) if e % 3 == 0 and e <= 60
                     else "D" + str(e // 2) if e % 2 == 0 and e <= 40 else "S20")
                v, dbl = value(t)
                x = cur - v
            if x == 0 and dbl and (win_after is None or len(darts) + 1 < win_after or (bull and t != "DB")):
                # no win yet: the dart misses the board or lands on the single area
                t = "M" if rnd() < 0.6 else ("S" + t[1:] if t != "DB" else "SB")
                v, dbl = value(t)
                x = cur - v
            darts.append(t)
            if x == 0 and dbl:
                return darts
            if x < 2:
                cur = start
                break
            cur = x
        pts[who] = cur
        who = (who + 1) % p
    return darts


def add(p, s, darts):
    assert 1 <= p <= MAXP and 2 <= s <= MAXS and 1 <= len(darts) <= MAXD
    assert all(t in ALL for t in darts)
    # the log ends at the first winning dart
    pts, who, i, n = [s] * p, 0, 0, len(darts)
    while i < n:
        start = cur = pts[who]
        for _ in range(3):
            if i >= n:
                break
            v, dbl = value(darts[i])
            i += 1
            x = cur - v
            if x == 0 and dbl:
                assert i == n, "darts after the win"
                cur = 0
                break
            if x < 2:
                cur = start
                break
            cur = x
        pts[who] = cur
        who = (who + 1) % p
    tests.append(f"{p} {s} {n}\n" + " ".join(darts) + "\n")


# samples
add(2, 101, "T20 S20 S1 T19 T20 S10 D5".split())
add(3, 80, "T20 S19 T20 D10".split())
add(3, 301, "T20 T20 T20 T19 S19".split())
add(1, 170, "T20 T20 DB".split())
add(2, 90, "T20 S6 D3 T20 D15".split())
# hidden: small hand-made (each bust kind, a bull finish, the log ending inside a turn)
add(1, 501, "T20 T20 T20 T20 T20 T20 T20 T19 D12".split())          # a nine-dart finish
add(1, 40, "S20 S10 S10 D10 D10".split())                             # 0 with a single: bust
add(2, 41, "S20 S20 T20 S1 D20".split())                              # 1 left, below 0
add(1, 110, "T20 DB".split())                                          # the bull finishes
add(2, 75, "SB SB SB M D20 S5 DB".split())                            # SB to 0: bust; ends inside a turn
add(3, 60, "T20 S20 S20 D10".split())                                 # T20 to 0: bust after one dart
add(2, 2, "S1 S2 M D1".split())                                       # 2 points: only D1 finishes
add(3, 3, "S2 S1 T1 S1 M M D1 S1 S1 S1 D1".split())
# hidden: random small games (brute checks these)
for p, s, d, sk, nz, wa, bl in ((2, 501, 60, 0.7, 0.05, 1, False), (3, 301, 400, 0.5, 0.1, 300, True), (4, 501, 3000, 0.4, 0.15, None, False)):
    add(p, s, game(p, s, d, [sk] * p, nz, wa, bl))
# hidden: big (D = 100000, or a game that ends at a win after more than 90000 darts)
D = MAXD
for p, s, sk, nz, wa in ((2, 501, 0.5, 0.1, None), (2, 501, 0.8, 0.03, None), (3, 501, 0.6, 0.2, 99000),
                         (4, 301, 0.3, 0.05, None), (6, 501, 0.7, 0.1, 95000), (1, 501, 0.5, 0.05, None),
                         (5, 1000, 0.9, 0.0, 99990), (2, 501, 0.2, 0.4, None), (3, 701, 0.95, 0.02, None),
                         (4, 501, 0.6, 0.6, 92000), (6, 999, 0.4, 0.15, None), (1, 2, 0.8, 0.2, 98000),
                         (2, 101, 0.6, 0.0, None), (3, 41, 0.7, 0.08, 97000),
                         (2, 501, 0.4, 1.0, None)):
    add(p, s, game(p, s, D, [sk + (rnd() - 0.5) * 0.1 for _ in range(p)], nz, wa))
# hidden: big games that end with a finish on the bull
for p, s, sk, nz, wa in ((6, 501, 0.6, 0.1, 99000), (4, 301, 0.8, 0.05, 98000), (5, 701, 0.5, 0.2, 99500)):
    add(p, s, game(p, s, D, [sk] * p, nz, wa, True))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
