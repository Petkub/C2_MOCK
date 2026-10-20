# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1104)
MAXN, MAXM = 4000, 10000
tests = []


def add(n, st):
    assert 1 <= n <= MAXN and 1 <= len(st) <= MAXM
    for l, r, op, c in st:
        assert 1 <= l <= r <= n and op in (">=", "<=", "=") and 0 <= c <= r - l + 1
    tests.append(f"{n} {len(st)}\n" + "".join(f"{l} {r} {op} {c}\n" for l, r, op, c in st))


def pattern(n, kind):
    """a hidden on/off pattern x[1..n] (x[0] unused); every statement made from it is true for it"""
    if kind == "blocks":
        x, cur = [0], random.randint(0, 1)
        while len(x) <= n:
            x += [cur] * random.randint(1, 40)
            cur ^= 1
        return x[:n + 1]
    p = {"sparse": 0.1, "half": 0.5, "dense": 0.9}[kind]
    return [0] + [1 if random.random() < p else 0 for _ in range(n)]


def prefix(x):
    s = [0]
    for v in x[1:]:
        s.append(s[-1] + v)
    return s


def interval(n, lens):
    k = random.choice(lens)
    if k == "short":
        ln = random.randint(1, min(n, 12))
    elif k == "mid":
        ln = random.randint(1, min(n, 300))
    else:
        ln = random.randint(1, n)
    l = random.randint(1, n - ln + 1)
    return l, l + ln - 1


def true_statements(n, s, m, ops=(">=", "<=", "="), lens=("short", "mid", "long"), slack=(0, 0, 0, 1, 2), loose=0.0):
    """m statements that hold for the pattern with prefix counts s: tight most of the time, or off by up to
    loose * length (then "=" statements are rare)"""
    out = []
    for _ in range(m):
        l, r = interval(n, lens)
        cnt, ln = s[r] - s[l - 1], r - l + 1
        op = random.choice(ops)
        d = random.choice(slack) + random.randint(0, int(loose * ln))
        if op == "=" and loose > 0 and random.random() < 0.8:
            op = random.choice((">=", "<="))
        if op == ">=":
            c = max(0, cnt - d)
        elif op == "<=":
            c = min(ln, cnt + d)
        else:
            c = cnt
        out.append((l, r, op, c))
    return out


def contradiction(n, s, a, b, pieces, kind):
    """statements on [a, b] that cannot hold together: pieces that are true for the pattern (with single-lamp gaps
    between them when kind == "gaps"), and one statement on the whole of [a, b] that disagrees with them by one lamp"""
    cuts = sorted(random.sample(range(a, b), pieces - 1)) if pieces > 1 else []
    bounds, prev = [], a - 1
    for c in cuts + [b]:
        bounds.append((prev + 1, c))
        prev = c
    out, lo, hi = [], 0, 0          # lo..hi: what the pieces (and the gap lamps) allow on [a, b]
    gaps = kind == "gaps"
    for idx, (l, r) in enumerate(bounds):
        if gaps and idx % 2 == 1 and r - l + 1 == 1:
            lo, hi = lo, hi + 1     # a lone gap lamp: anything
            continue
        cnt = s[r] - s[l - 1]
        out.append((l, r, "=", cnt))
        lo, hi = lo + cnt, hi + cnt
    ln = b - a + 1
    if hi + 1 <= ln and (lo == 0 or (not gaps and random.random() < 0.5)):
        out.append((a, b, ">=", hi + 1))
    else:
        out.append((a, b, "<=", lo - 1))
    return out


def soft_contradiction(n, s, a, b, pieces, skip=0.0):
    """like contradiction(), but the pieces are only ">=" (the true counts), a share `skip` of them left out,
    and the whole is "<=" one less than the pieces force"""
    cuts = sorted(random.sample(range(a, b), pieces - 1))
    out, prev, tot = [], a - 1, 0
    for c in cuts + [b]:
        cnt = s[c] - s[prev]
        if not out or random.random() >= skip:
            out.append((prev + 1, c, ">=", cnt))
            tot += cnt
        prev = c
    assert tot >= 1
    out.append((a, b, "<=", tot - 1))
    return out


def feasible(n, m, kind, **kw):
    s = prefix(pattern(n, kind))
    return true_statements(n, s, m, **kw)


def infeasible(n, m, kind, pieces, how, span=None, skip=0.0, tight=False, **kw):
    """tight: the statement on the whole of [a, b] gets the true count instead, so the test is feasible
    but only just (every piece is forced to its exact count when nothing is skipped)"""
    x = pattern(n, kind)
    s = prefix(x)
    if span is None:
        a, b = 1, n
    else:
        a = random.randint(1, n - span + 1)
        b = a + span - 1
    while True:
        if how == "soft":
            if s[b] - s[a - 1] == 0:
                a, b = 1, n
            bad = soft_contradiction(n, s, a, b, pieces, skip)
        else:
            bad = contradiction(n, s, a, b, pieces, how)
        if tight:
            bad[-1] = (a, b, bad[-1][2], s[b] - s[a - 1])
        if all(0 <= c <= r - l + 1 for l, r, op, c in bad):
            break
    st = true_statements(n, s, m - len(bad), **kw) + bad
    random.shuffle(st)
    return st


def windows(n, s, w, op, step=1):
    """the true statement of type op on every window [i, i + w - 1] (i = 1, 1 + step, ...)"""
    out = []
    for i in range(1, n - w + 2, step):
        cnt = s[i + w - 1] - s[i - 1]
        out.append((i, i + w - 1, op, cnt))
    return out


# samples
add(6, [(1, 3, ">=", 2), (3, 6, "<=", 1), (2, 5, "=", 2)])
add(5, [(1, 5, "=", 4), (1, 2, "<=", 1), (4, 5, "<=", 1)])
add(7, [(1, 4, ">=", 2), (3, 7, "<=", 2), (2, 6, "=", 3), (5, 7, ">=", 1)])
add(8, [(3, 5, ">=", 0), (1, 8, "<=", 8)])
add(9, [(1, 3, "=", 2), (3, 5, "<=", 0), (5, 9, ">=", 4), (2, 8, "<=", 4)])

# hidden: small (the brute tries every pattern)
add(1, [(1, 1, ">=", 1)])
add(1, [(1, 1, "<=", 0), (1, 1, ">=", 0)])
add(16, feasible(16, 30, "half"))
add(18, feasible(18, 40, "blocks", slack=(0,)))
add(17, infeasible(17, 12, "half", 5, "gaps", loose=0.5))
add(20, feasible(20, 25, "sparse", lens=("short",)))
add(15, infeasible(15, 20, "dense", 4, "soft", skip=0.4))
add(19, feasible(19, 50, "dense", ops=(">=", "<="), slack=(0, 1)))

# hidden: medium
add(600, feasible(600, 1500, "half"))
add(700, infeasible(700, 2000, "blocks", 40, "plain"))
add(650, feasible(650, 2000, "blocks", ops=(">=", "<="), slack=(0,)))

# hidden: big
N, M = MAXN, MAXM
add(N, feasible(N, M, "half", loose=0.3))
add(N, feasible(N, M, "blocks", slack=(0,)))
add(N, feasible(N, M, "sparse", ops=(">=", "<="), lens=("mid", "long"), loose=0.4))
add(N, feasible(N, M, "dense", lens=("short", "mid"), loose=0.2))
add(N, feasible(N, M, "half", lens=("short",), loose=0.5))
s = prefix(pattern(N, "half"))
st = windows(N, s, 3, ">=")[::-1]
add(N, st + true_statements(N, s, M - len(st), ops=("<=",), loose=0.2))      # every window of 3, right to left
s = prefix(pattern(N, "blocks"))
st = windows(N, s, 2, "<=") + windows(N, s, 5, ">=", 2)
random.shuffle(st)
add(N, st[:M])
s = prefix(pattern(N, "sparse"))
st = windows(N, s, 7, "=", 3)
add(N, st + true_statements(N, s, M - len(st), lens=("long",), loose=0.1))
s = prefix(pattern(N, "blocks"))
st = true_statements(N, s, 3000, ops=("=",), lens=("mid",))
add(N, st + true_statements(N, s, M - len(st), lens=("short", "long"), loose=0.4))
s = prefix(pattern(N, "half"))
st = windows(N, s, 4, "<=", 2)[::-1] + windows(N, s, 9, ">=", 3)
add(N, st + true_statements(N, s, M - len(st), lens=("mid",), loose=0.25))
add(N, feasible(N, M, "dense", ops=(">=", "<="), lens=("long",), loose=0.3))
add(N, infeasible(N, M, "half", 1600, "plain", loose=0.2))
add(N, infeasible(N, M, "blocks", 1200, "gaps", loose=0.6))
add(N, infeasible(N, M, "half", 2500, "soft", skip=0.3, tight=True, loose=0.6))      # feasible, only just
add(N, infeasible(N, M, "sparse", 50, "gaps", span=400, tight=True, loose=0.1))
add(N, infeasible(N, M, "dense", 2, "soft", ops=(">=", "<="), slack=(0, 1)))
add(N, infeasible(N, M, "blocks", 3500, "soft", skip=0.0, tight=True, lens=("short",), slack=(0,)))

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
