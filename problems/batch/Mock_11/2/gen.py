# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import itertools, math, operator, os, random

random.seed(1102)
MAXN, T, MAXW = 100000, 1000000, 1000000
rnd = random.random
tests = []


PERM = {}


def add(jobs, shuffle=True):
    """jobs = list of (r, d, w); shuffle: in a random order (one shuffled order per size, reused: fast)"""
    n = len(jobs)
    assert 1 <= n <= MAXN
    R, D, W = zip(*jobs)
    assert min(R) >= 0 and max(D) <= T and all(map(operator.lt, R, D))
    assert 1 <= min(W) and max(W) <= MAXW
    if shuffle:
        if n not in PERM:
            p = list(range(n))
            random.shuffle(p)
            PERM[n] = p
        jobs = [jobs[i] for i in PERM[n]]
    tests.append(f"{n}\n" + "%d %d %d\n" * n % tuple(itertools.chain.from_iterable(jobs)))


def logu(lo, hi):
    """log-uniform real in [lo, hi]"""
    return math.exp(math.log(lo) + rnd() * (math.log(hi) - math.log(lo)))


def clusters(n, k, lo=10, hi=T, rate=(0.01, 100.0), lens=None):
    """n jobs in k clusters; a cluster has a start, a width, a work rate; a job of length L in it has work about
    L * rate (so a single job is never much denser than its cluster, but overlapping jobs add up)"""
    cl = []
    for _ in range(k):
        width = int(logu(lo, hi))
        start = int(rnd() * (T - width + 1))
        cl.append((start, width, logu(*rate), math.log(width if lens is None else min(width, lens))))
    jobs = []
    exp = math.exp
    for _ in range(n):
        start, width, rt, lg = cl[int(rnd() * k)]
        L = int(exp(rnd() * lg)) or 1
        r = start + int(rnd() * (width - L + 1))
        w = int(L * rt * (0.3 + 0.7 * rnd()))
        jobs.append((r, r + L, 1 if w < 1 else MAXW if w > MAXW else w))
    return jobs


def nested_blocks(n, k, exact=True, wmax=MAXW, gap=True):
    """k blocks side by side; inside a block the jobs are nested (r goes up, d goes down, ties allowed).
    The answer is known: the densest window is [r_j, d_j] of some job j with the jobs nested in it
    (a window across blocks is never denser than its densest part).
    exact: the outer job of the densest block gets extra work so that block is exactly full at the answer.
    Returns (jobs, answer)."""
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    # a block of m nested jobs needs length >= 2 m - 1 in the worst case; give it more
    lens = [2 * m + int(rnd() * 3 * m) + 1 for m in sizes]
    room = T - sum(lens)
    assert room >= 0
    cuts = sorted(int(rnd() * (room + 1)) for _ in range(k)) if gap else [0] * k
    jobs, best, x, prev = [], [], 0, 0
    for b in range(k):
        x += cuts[b] - prev
        prev = cuts[b]
        L, m = lens[b], sizes[b]
        lo, hi = x, x + L
        blk = []
        rt = logu(1, wmax / 2)
        for j in range(m):
            if j:
                slack = hi - lo - 2 * (m - j - 1) - 1         # leave room for the jobs still to come
                step = int(rnd() * min(3, slack + 1))
                lo += step
                hi -= int(rnd() * min(3, slack - step + 1))
            w = int(rt * (0.2 + 0.8 * rnd()))
            blk.append([lo, hi, 1 if w < 1 else wmax if w > wmax else w])
        x += L
        # densest window of this block: max over j of ceil(work of jobs j..m-1 / (d_j - r_j))
        suf, bb = 0, (0, 0)
        for j in range(m - 1, -1, -1):
            suf += blk[j][2]
            ln = blk[j][1] - blk[j][0]
            c = -(-suf // ln)
            if c > bb[0]:
                bb = (c, j)
        best.append(bb)
        jobs.append(blk)
    top = max(range(k), key=lambda b: best[b][0])
    ans = max(bb[0] for bb in best)
    if exact:
        # make the outer job of the densest block fill [r_0, d_0] exactly at speed ans
        blk = jobs[top]
        extra = ans * (blk[0][1] - blk[0][0]) - sum(j[2] for j in blk)
        if blk[0][2] + extra <= wmax:
            blk[0][2] += extra
    return [tuple(j) for blk in jobs for j in blk], ans


def long_short(n, k, nlong, lo=1000, hi=100000, slen=30):
    """k regions; in each, nlong long heavy jobs over most of the region and a stream of short jobs whose
    total density is about that of the long jobs (a long job must be interrupted for the short ones)"""
    jobs = []
    per = n // k
    for b in range(k):
        m = per if b < k - 1 else n - per * (k - 1)
        ns = m - nlong
        L = int(logu(lo, hi))
        x = int(rnd() * (T - L + 1))
        a = MAXW / L * (0.3 + 0.7 * rnd())
        for _ in range(nlong):
            r = x + int(rnd() * L / 4)
            d = x + L - int(rnd() * L / 4)
            jobs.append((r, d, max(1, min(MAXW, int(a * (d - r))))))
        avg = (slen + 1) / 2
        dens = nlong * a * (0.5 + rnd())           # wanted total density of the short jobs
        bs = dens * L / max(1, ns) / avg          # work per time unit of one short job
        for _ in range(ns):
            l = 1 + int(rnd() * slen)
            r = x + int(rnd() * (L - l + 1))
            jobs.append((r, r + l, max(1, min(MAXW, int(bs * l * (0.5 + rnd()))))))
    return jobs


def stairs(n, k):
    """k runs of overlapping jobs of one length L: job j of a run covers [x + j g, x + j g + L] with g < L and
    heavy work, so the densest window spans many jobs of a run and is not the window of any single job"""
    jobs = []
    for b in range(k):
        m = n // k + (1 if b < n % k else 0)
        g = 1 + int(rnd() * 3)
        L = g + 1 + int(rnd() * 10)
        x = int(rnd() * (T - (m - 1) * g - L + 1))
        for j in range(m):
            r = x + j * g
            jobs.append((r, r + L, MAXW - int(rnd() * MAXW * 0.3)))
    return jobs


# samples
add([(0, 4, 4), (1, 2, 3)], False)
add([(0, 10, 10), (2, 3, 5), (5, 7, 4), (8, 10, 6)], False)
add([(3, 5, 1000000)], False)
add([(3, 5, 3), (3, 4, 2), (4, 5, 2), (1, 7, 2), (5, 8, 3)], False)
add([(0, 1, 7), (0, 1, 7), (1, 3, 5), (2, 3, 9), (0, 3, 1)], False)
# hidden: small (brute checks these)
add([(0, 1000000, 1)])
add([(999999, 1000000, 1000000)] * 7)
add(long_short(30, 2, 1, 10, 60, 5))
add(clusters(200, 4, 10, 2000))
add(nested_blocks(300, 3)[0])
add(long_short(400, 4, 2, 50, 500, 10))
add(nested_blocks(1000, 10, False)[0])
add(clusters(2000, 6, 20, 100000, (0.1, 20)))
add(long_short(3000, 10, 3, 200, 5000))
add(nested_blocks(3000, 4, True, 50)[0] + long_short(500, 2, 2, 100, 1000))
add([(5, 6, MAXW - i) for i in range(3000)] + clusters(500, 2, 10, 1000))
# hidden: big (N = 100000)
N = MAXN
add(clusters(N, 5))
add(clusters(N, 20))
add(clusters(N, 50, 10, 10000, (0.1, 10)))
add(clusters(N, 200, 10, T, (0.001, 1000)))
add(long_short(N, 5, 2))
add(long_short(N, 50, 1, 100, 10000))
add(long_short(N, 1, 3, 100000, T))
add(long_short(N, 20, 3, 1000, 50000))
add(nested_blocks(N, 1)[0])
add(nested_blocks(N - 20000, 7)[0] + stairs(20000, 4))
add(nested_blocks(N - 5000, 40)[0] + stairs(5000, 50))
add(nested_blocks(N - 30000, 500)[0] + stairs(30000, 300))
add(nested_blocks(N, 30, True, 300)[0])
add(nested_blocks(N, 2, True, MAXW, False)[0])
add(nested_blocks(N // 2, 5)[0] + long_short(N // 2, 10, 2))
t = 1 + int(rnd() * (T - 3))            # a huge answer: almost all the work in three time units
add([(t, t + 1 + int(rnd() * 2), MAXW - int(rnd() * 1000)) for _ in range(N - 1000)] + clusters(1000, 3))
t = 1 + int(rnd() * (T - 3))            # about 4 * 10^9 in one time unit, the rest elsewhere
add([(t, t + 1, MAXW - int(rnd() * 100)) for _ in range(4000)] + long_short(N - 4000, 20, 2))
add([(0, 1 + int(logu(1, T - 1)), int(logu(1, MAXW))) for _ in range(N)])        # every job released at 0

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
