# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random, re

random.seed(920202)
MAXN, MAXLEN = 100000, 3000000
NM = r"[A-Z]{1,3}[1-9][0-9]{0,4}"
TM = r"(?:" + NM + r"|0|[1-9][0-9]{0,9})"
NAME = re.compile(NM + "$")
LINE = re.compile(NM + "=-?" + TM + "(?:[+-]" + TM + ")*$")
SPLIT = re.compile(r"[=+\n-]")
tests = []


def add(lines):
    """lines: the cells as strings NAME=EXPR. Small tests are checked fully here; big ones are built only by
    Sheet, whose names are distinct (checked in Sheet) with the right format (checked in names()), whose
    references are names of its own cells and whose constants come from const() (checked there)"""
    n = len(lines)
    assert 1 <= n <= MAXN
    body = "".join(s + "\n" for s in lines)
    if n <= 5000:
        assert all(map(LINE.match, lines))
        defined = set(s[:s.index("=")] for s in lines)
        toks = set(SPLIT.split(body))
        assert len(defined) == n and set(t for t in toks if t[:1].isalpha()) == defined
        assert all(int(t) <= 10 ** 9 for t in toks if t[:1].isdigit())
    text = f"{n}\n" + body
    assert len(text) <= MAXLEN, len(text)
    tests.append(text)


def ri(lo, hi):
    """uniform integer in [lo, hi] (faster than randint, still deterministic)"""
    return lo + int(random.random() * (hi - lo + 1))


LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


_pool = {}


def name_of(x, num):
    """x in [0, 26 + 26^2 + 26^3): the x-th string of 1-3 capital letters, then the number"""
    k = 1
    while x >= 26 ** k:
        x -= 26 ** k
        k += 1
    s = ""
    for _ in range(k):
        s += LET[x % 26]
        x //= 26
    return s + str(num)


def names(n, short=False):
    """n distinct random names (short: numbers below 1000): a window of one random pool per kind (fast)"""
    if short not in _pool:
        seen, out = set(), []
        top = 999 if short else 99999
        while len(out) < MAXN + 5000:
            k = ri(1, 3)
            s = name_of(sum(26 ** j for j in range(1, k)) + ri(0, 26 ** k - 1), ri(1, top))
            if s not in seen:
                seen.add(s)
                out.append(s)
        assert all(map(NAME.match, out))
        _pool[short] = out
    s = ri(0, 5000)
    return _pool[short][s:s + n]


def const():
    r = random.random()
    if r < 0.15:
        x = ri(0, 9)
    elif r < 0.3:
        x = ri(10 ** 9 - 1000, 10 ** 9)
    else:
        x = ri(0, 10 ** 9)
    assert 0 <= x <= 10 ** 9
    return str(x)


def sgn(p_minus=0.4):
    return -1 if random.random() < p_minus else 1


class Sheet:
    """cells 0..n-1 with names; terms[i] = the terms of cell i as strings with their sign (`+X1`, `-5`)"""

    def __init__(self, n, short=False):
        self.n = n
        self.nm = names(n, short)
        assert len(set(self.nm)) == n
        self.terms = [[] for _ in range(n)]

    def ref(self, i, j, sg=1):
        self.terms[i].append(("-" if sg < 0 else "+") + self.nm[j])

    def num(self, i, sg=1):
        self.terms[i].append(("-" if sg < 0 else "+") + const())

    def lines(self, order):
        out = []
        for i in order:
            if not self.terms[i]:
                self.num(i)
            e = "".join(self.terms[i])
            out.append(self.nm[i] + "=" + (e[1:] if e[0] == "+" else e))
        return out


def chain_step(sh, i, j):
    """cell i is built from cell j (the previous cell of a chain), often using it twice"""
    r = random.random()
    if r < 0.45:
        sh.ref(i, j), sh.ref(i, j, sgn(0.3))
    elif r < 0.6:
        sh.ref(i, j), sh.ref(i, j), sh.ref(i, j, -1)
    elif r < 0.8:
        sh.ref(i, j, sgn()), sh.num(i, sgn())
    else:
        sh.ref(i, j, sgn())
    if random.random() < 0.2:
        sh.num(i, sgn())


def dag(sh, lo, hi, kmin, kmax, pick=None):
    """cells lo..hi-1 refer to kmin..kmax random earlier cells (pick(i) chooses one), maybe a constant too"""
    for i in range(lo, hi):
        for _ in range(ri(kmin, kmax)):
            j = pick(i) if pick else ri(0, i - 1)
            sh.ref(i, j, sgn())
        if random.random() < 0.3:
            sh.num(i, sgn())


_perm = []


def order_of(n, kind):
    if kind == "rev":
        return list(range(n - 1, -1, -1))
    if kind == "fwd":
        return list(range(n))
    if n < MAXN:
        o = list(range(n))
        random.shuffle(o)
        return o
    if not _perm:                   # every big test uses the same random line order (fast)
        _perm.extend(range(MAXN))
        random.shuffle(_perm)
    return _perm


def mixed(n, L, kind, cycles=0, selfs=0, kmax=3, short=False):
    """a chain of L cells (cell k uses cell k-1), then a random DAG over everything before it, then `cycles`
    back references (a cell refers to a later cell) and `selfs` self references, all in the upper half of the
    chain (everything built on them later breaks too)"""
    sh = Sheet(n, short)
    sh.num(0)
    for k in range(1, L):
        chain_step(sh, k, k - 1)
    dag(sh, L, n, 1, kmax)
    for _ in range(cycles):
        i = ri(L // 2, min(L, n - 2))
        sh.ref(i, ri(i + 1, min(n - 1, i + 1 + ri(0, n // 50 + 1))), sgn())
    for _ in range(selfs):
        i = ri(L // 2, L - 1)
        sh.ref(i, i, sgn())
    return sh.lines(order_of(n, kind))


# samples
add(["A1=B2+B2-3", "C7=A1+X1", "B2=10", "X1=Y2", "Y2=-X1+1"])
add(["AB1=AB1", "Y1=900000000", "Z2=Y1+Y1", "CAT3=Z2-Z2+Z2", "D1=0"])
add(["A1=A2+A2", "A2=A3+A3-1", "A3=A4+A4", "A4=-1000000000"])
add(["X99999=-5"])
add(["K1=K2+M3-7", "K2=5+P10", "M3=M3-M3+2", "P10=-4", "T6=-P10-P10+K2"])
# hidden: small (brute checks these)
add(["A1=0"])
add(["Z1=-0"])
add(["ZZZ99999=ZZZ99999+ZZZ99999"])
add(["A1=B1", "B1=C1", "C1=A1", "D1=C1-C1", "E1=7-3+0"])
add(mixed(30, 10, "rand", cycles=2, selfs=1, short=True))
add(mixed(200, 60, "rev", cycles=0))
add(mixed(500, 300, "rand", cycles=3, selfs=0))
add(mixed(2000, 1200, "rev", cycles=1))
add(mixed(4000, 3000, "rand", cycles=0))
add(mixed(4000, 2000, "fwd", cycles=3, selfs=2))
# hidden: big (N = 100000)
N = MAXN
add(mixed(N, N, "rev"))                                           # one long chain, lines in reverse order
add(mixed(N, N, "rand"))                                          # the same in random order
add(mixed(N, 60000, "rev", kmax=2, selfs=1))
add(mixed(N, 50000, "rand", kmax=2, cycles=2))
add(mixed(N, 40000, "rand", cycles=3))                            # a few cycles, everything after them breaks
add(mixed(N, 40000, "rev", cycles=1, selfs=1))
add(mixed(N, 70000, "rand", selfs=1))
add(mixed(N, 30000, "rand", cycles=30, kmax=2, short=True))
sh = Sheet(N)                                                     # one cycle through every cell
for i in range(N):
    sh.ref(i, (i + 1) % N, sgn())
add(sh.lines(order_of(N, "rand")))
sh = Sheet(N)                                                     # two interleaved long chains,
sh.num(0)                                                         # one starts at a self reference
sh.ref(1, 1, -1), sh.num(1)
for i in range(2, N):
    chain_step(sh, i, i - 2)
add(sh.lines(order_of(N, "rev")))
sh = Sheet(N)                                                     # a cycle in the middle of a long chain
sh.num(0)
for i in range(1, N):
    chain_step(sh, i, i - 1)
mid = N // 2
sh.ref(mid, mid + 1000, -1)
add(sh.lines(order_of(N, "rand")))
sh = Sheet(N)                                                     # every cell uses the last one many times,
sh.num(N - 1)                                                     # half of them also use a cell on a cycle
sh.ref(N - 2, N - 3), sh.ref(N - 3, N - 2, -1)
for i in range(N - 3):
    for _ in range(ri(1, 3)):
        sh.ref(i, N - 1, sgn(0.5))
    if i % 2:
        sh.ref(i, N - 2 - i % 4 // 2, sgn(0.5))
add(sh.lines(order_of(N, "rand")))
sh = Sheet(N, short=True)                                         # two long chains, one huge sum of all cells
sh.num(0)
for i in range(1, N - 1):
    chain_step(sh, i, i - 1 if i != N // 2 else 0)
for i in range(N - 1):
    sh.ref(N - 1, i, sgn(0.5))
add(sh.lines(order_of(N, "rev")))
sh = Sheet(N)                                                     # chain where each cell also uses the cell two back
sh.num(0)
sh.ref(1, 0)
for i in range(2, N):
    sh.ref(i, i - 1, sgn()), sh.ref(i, i - 2, sgn())
add(sh.lines(order_of(N, "rand")))
sh = Sheet(N)                                                     # many small cycles and self references
dag(sh, 1, N, 1, 2)
sh.num(0)
for _ in range(2000):
    i = ri(0, N - 1)
    sh.ref(i, i if random.random() < 0.5 else ri(i, min(N - 1, i + 5)), sgn())
add(sh.lines(order_of(N, "rand")))
add(mixed(N, 80000, "rand", cycles=1, kmax=2))

for t in tests:
    assert t.endswith("\n") and " " not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
