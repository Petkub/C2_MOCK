# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The big tests use N = MAXN with small numbers (inputs <= ~3 MB); large distances come from a few wide gaps
# along the river that only long roads cross.
import os, random

random.seed(1104)
MAXN, MAXM, MAXW, MAXX, MAXC = 130000, 130000, 10 ** 9, 10 ** 9, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def put(n, c, x, lines):
    assert 2 <= n <= MAXN and len(lines) <= MAXM and len(x) == n and 0 <= c <= MAXC
    assert 0 <= min(x) and max(x) <= MAXX
    tests.append(f"{n} {len(lines)} {c}\n" + " ".join(map(str, x)) + "\n" + "".join(lines))


def check_edges(lo, hi, edges):
    """towns lo..hi"""
    if edges:
        us, vs, ws = zip(*edges)
        assert lo <= min(us) and max(us) <= hi and lo <= min(vs) and max(vs) <= hi
        assert 1 <= min(ws) and max(ws) <= MAXW and all(map(int.__ne__, us, vs))


def add(n, c, x, edges):
    check_edges(1, n, edges)
    put(n, c, x, [f"{u} {v} {w}\n" for u, v, w in edges])


def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        a[i], a[j] = a[j], a[i]


def emit(n, c, x, edges, start, goal):
    """towns 0..n-1 while building; start -> 1, goal -> N, the rest shuffled; roads shuffled"""
    rest = [v for v in range(n) if v != start and v != goal]
    shuffle(rest)
    lab = [0] * n
    lab[start] = 1
    lab[goal] = n
    for i, v in enumerate(rest):
        lab[v] = i + 2
    xs = [0] * n
    for v in range(n):
        xs[lab[v] - 1] = x[v]
    check_edges(0, n - 1, edges)     # before relabelling (lab is a permutation of 1..n)
    out = [f"{lab[u]} {lab[v]} {w}\n" if rnd() < 0.5 else f"{lab[v]} {lab[u]} {w}\n" for u, v, w in edges]
    shuffle(out)            # the build order would show the structure
    put(n, c, xs, out)


def river(n, extra, X, s_num, s_den, noise, c, ends="far", back=6, local=25, ties=0, gaps=0, G=2 * 10 ** 8):
    """towns along a river (sorted by x); roads join nearby towns and are slower than the ferry per km
    (length about s_num / s_den times the distance along the river, plus noise); `gaps` wide empty stretches
    of G km near the downstream end (only long roads cross them)"""
    if ties:
        step = X // max(1, ties)
        x = sorted(int(rnd() * (ties + 1)) * step for _ in range(n))
    else:
        x = sorted(int(rnd() * (X + 1)) for _ in range(n))
    if gaps:
        cuts = sorted(ri(n - n // 6, n - 1) for _ in range(gaps))
        k = 0
        for i in range(n):
            while k < gaps and cuts[k] <= i:
                k += 1
            x[i] += k * G

    edges, noise1 = [], noise + 1
    for i in range(1, n):
        j = i - 1 - int(rnd() * back)
        if j < 0:
            j = 0
        w = (x[i] - x[j]) * s_num // s_den + int(rnd() * noise1)
        edges.append((i, j, w if 0 < w <= MAXW else (1 if w <= 0 else MAXW)))
    while len(edges) < n - 1 + extra:
        i = int(rnd() * n)
        j = min(n - 1, max(0, i + int(rnd() * (2 * local + 1)) - local))
        if i != j:
            w = abs(x[i] - x[j]) * s_num // s_den + int(rnd() * noise1)
            edges.append((i, j, w if 0 < w <= MAXW else (1 if w <= 0 else MAXW)))
    if ends == "far":
        s, t = ri(0, n // 50), n - 1 - ri(0, n // 50)
    elif ends == "mid":
        s, t = ri(n // 4, n // 2), ri(n // 2 + 1, 3 * n // 4)
    else:
        s, t = ri(0, n - 1), ri(0, n - 1)
        while t == s:
            t = ri(0, n - 1)
    if rnd() < 0.5:
        s, t = t, s
    emit(n, c, x, edges, s, t)


def random_graph(n, extra, W, X, c, wlo=1):
    """random recursive tree plus random extra roads, random x"""
    span = W - wlo + 1
    edges = [(v, int(rnd() * v), wlo + int(rnd() * span)) for v in range(1, n)]
    while len(edges) < n - 1 + extra:
        u, v = int(rnd() * n), int(rnd() * n)
        if u != v:
            edges.append((u, v, ri(wlo, W)))
    x = [ri(0, X) for _ in range(n)]
    emit(n, c, x, edges, 0, n - 1)


def path(n, step, extra, c, plus=0):
    """a single road line along the river, road length = distance along the river (+ plus); distinct x"""
    x = [0] * n
    for i in range(1, n):
        x[i] = x[i - 1] + ri(1, step)
    edges = [(i, i + 1, max(1, x[i + 1] - x[i] + ri(0, plus))) for i in range(n - 1)]
    for _ in range(extra):      # long detours that never help
        i = ri(0, n - 2)
        j = min(n - 1, i + ri(1, 5))
        edges.append((i, j, MAXW))
    emit(n, c, x, edges, 0, n - 1)


def split(n1, n2, n3, m, X, c, W=MAXW):
    """1 and N in different parts (n3 towns in further parts); every part is a random tree plus extra roads"""
    n = n1 + n2 + n3
    parts = [(0, n1), (n1, n1 + n2)]
    p = n1 + n2
    while p < n:
        q = min(n, p + ri(1, 200))
        parts.append((p, q))
        p = q
    edges = []
    for lo, hi in parts:
        for v in range(lo + 1, hi):
            edges.append((v, ri(lo, v - 1), ri(1, W)))
    while len(edges) < m:
        lo, hi = parts[0] if rnd() < 0.5 else parts[1]
        u, v = ri(lo, hi - 1), ri(lo, hi - 1)
        if u != v:
            edges.append((u, v, ri(1, W)))
    x = [ri(0, X) for _ in range(n)]
    emit(n, c, x, edges, 0, n1)


def grid(rows, cols, X, s, noise, c, extra, down=0.5):
    """towns on a grid, x = column; roads between neighbours"""
    n = rows * cols
    step = X // cols
    x = [(i % cols) * step + ri(0, step // 3) for i in range(n)]
    edges = []
    for r in range(rows):
        for q in range(cols):
            v = r * cols + q
            if q + 1 < cols:
                edges.append((v, v + 1, max(1, s * abs(x[v + 1] - x[v]) + ri(0, noise))))
            if r + 1 < rows and rnd() < down:
                edges.append((v, v + cols, ri(1, noise + 1)))
    for _ in range(extra):
        u, v = int(rnd() * n), int(rnd() * n)
        if u != v:
            edges.append((u, v, ri(MAXW // 2, MAXW)))
    edges = edges[:MAXM]
    emit(n, c, x, edges, ri(0, rows - 1) * cols, ri(0, rows - 1) * cols + cols - 1)


# samples
add(5, 1, [0, 3, 4, 8, 9], [(1, 2, 4), (2, 3, 2), (3, 5, 9), (1, 4, 20), (4, 5, 1)])
add(4, 5, [7, 1, 2, 3], [(1, 2, 1), (3, 4, 1)])
add(3, 0, [0, 5, 10], [(1, 2, 5), (2, 3, 5)])
add(2, 3, [4, 4], [(1, 2, 4)])
add(6, 2, [1, 6, 2, 5, 3, 8], [(1, 3, 3), (3, 5, 4), (5, 2, 6), (2, 6, 5), (1, 4, 9), (4, 6, 7), (3, 4, 2)])
# hidden: small (brute checks these)
add(2, 0, [0, 0], [])
add(3, 7, [3, 1, 9], [(2, 3, 1)])
river(40, 31, 1000, 3, 1, 30, 300, ends="any")
river(80, 41, 10 ** 6, 2, 1, 100, 10 ** 5, ties=4)
random_graph(100, 61, 50, 80, 7)
path(120, 80, 30, 0, plus=1)
split(30, 40, 20, 110, 1000, 5)
grid(10, 14, 10 ** 5, 2, 300, 2000, 20)
river(120, 30, 10 ** 4, 3, 1, 5, 2000, gaps=3, G=3 * 10 ** 8)
# hidden: big
N = MAXN
river(N, 1, 10 ** 5, 3, 1, 1, 30000, gaps=2)
river(N - 3000, 3001, 10 ** 5, 3, 1, 1, 5000, ends="mid")
river(N, 1, 10 ** 5, 2, 1, 3, 0, ends="far", back=2)
river(N - 3000, 3001, 10 ** 5, 5, 4, 1, 3000, ties=20, gaps=1)
river(N, 1, 10 ** 5, 6, 5, 0, 4000, back=1, local=3)
river(N - 3000, 3001, 10 ** 5, 7, 2, 3, 2 * 10 ** 8, ties=1000, gaps=3)
river(N, 1, 10 ** 5, 2, 1, 2, 3, ties=6)
random_graph(N - 500, 501, 9, 10 ** 5, 3)
random_graph(N, 0, 10, 10, 0, wlo=10)
path(N, 15, 0, 0)
path(N, 15, 0, 1, plus=1)
split(N // 3, N // 2, N - N // 3 - N // 2, N, 10 ** 5, 0, W=99)
grid(200, 300, MAXX // 2, 3, 10 ** 5, MAXX // 20, 5000, down=0.3)
river(N, 1, 10 ** 5, 3, 1, 2, 2000, ties=300, gaps=2)        # many towns share an x
random_graph(N - 1000, 1001, 1000, 50, 3)                  # x in 0..50: big groups of equal x

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
