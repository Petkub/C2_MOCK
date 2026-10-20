# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import math, os, random

random.seed(1103)
MAXN, MAXM, K = 500000, 200000, 100000
rnd = random.random
tests = []


def add(a, b):
    n, m = len(a), len(b)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    assert 1 <= min(a) and max(a) <= K and 1 <= min(b) and max(b) <= K
    cnt = [0] * (K + 1)
    for x in b:
        cnt[x] += 1
    assert max(cnt) <= 2
    tests.append(f"{n} {m}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n")


_base = []


_perm = {}


def relabel(k=K):
    """a random-looking one-to-one map of the values 1..k onto themselves (index 0 unused): one shuffled
    order per k (shuffling is slow), read with a random step coprime to k from a random start"""
    if k not in _perm:
        p = list(range(1, k + 1))
        random.shuffle(p)
        _perm[k] = p
    p = _perm[k]
    while True:
        step = 1 + int(rnd() * k)
        if math.gcd(step, k) == 1:
            break
    c = int(rnd() * k)
    return [0] + [p[(c + step * x) % k] for x in range(1, k + 1)]


def double_perm(m, k=K):
    """m values, each of 1..k at most twice, in random order (one shuffled base list reused, relabelled)"""
    assert m <= 2 * k
    if not _base:
        _base.extend(list(range(1, K + 1)) * 2)
        random.shuffle(_base)
    mp = relabel(k)
    off = int(rnd() * 2 * K)
    out = [mp[x] for x in _base[off:] + _base[:off] if x <= k]
    return out[:m]


def rand_a(n, vals):
    """n values drawn from the list vals"""
    L = len(vals)
    return [vals[int(rnd() * L)] for _ in range(n)]


def edited(b, n, keep=0.8, k=K):
    """walk along b keeping each value with probability keep and inserting random values, until n values"""
    out = []
    while len(out) < n:
        for x in b:
            if rnd() < keep:
                out.append(x)
            if rnd() < 1 - keep:
                out.append(1 + int(rnd() * k))
        if len(out) < n and rnd() < 0.5:
            b = b[::-1]
    return out[:n]


def near_pairs(m, k, spread):
    """the songs 1..k in random order, the second copy of each song comes at most `spread` songs later"""
    mp = relabel(k)
    buckets = [[] for _ in range(k + spread + 2)]
    out = []
    for i in range(1, k + 1):
        out.append(mp[i])
        buckets[i + int(rnd() * (spread + 1))].append(mp[i])
        out.extend(buckets[i])
    for j in range(k + 1, len(buckets)):
        out.extend(buckets[j])
    return out[:m]


def front(b, n, part):
    """n songs drawn from the songs of the first `part` places of b"""
    return rand_a(n, list(dict.fromkeys(b[:part])))


def order_small_front(ks, frac):
    """a random order of the songs 1..K in which the songs 1..ks all come within the first frac * K places"""
    mp = relabel()
    rest = [x for x in mp[1:] if x > ks]
    h = int(frac * K) - ks
    head = list(range(1, ks + 1)) + rest[:h]
    random.shuffle(head)
    return head + rest[h:]


def pairs_of(order, spread):
    """each song of `order` twice: the second copy comes at most `spread` songs later"""
    k = len(order)
    buckets = [[] for _ in range(k + spread + 2)]
    out = []
    for i, x in enumerate(order):
        out.append(x)
        buckets[i + int(rnd() * (spread + 1))].append(x)
        out.extend(buckets[i])
    for j in range(k, len(buckets)):
        out.extend(buckets[j])
    return out


def pad(core, n, ks=99):
    """core with random songs 1..ks put in at random places, n songs in all (each core song keeps its order)"""
    p = 1 - len(core) / n
    out = []
    for x in core:
        while rnd() < p:
            out.append(1 + int(rnd() * ks))
        out.append(x)
    out = out[:n]
    out += [1 + int(rnd() * ks) for _ in range(n - len(out))]
    return out


def each_times(seq, lo, hi):
    """every song of seq repeated lo..hi times in a row"""
    out = []
    for x in seq:
        out += [x] * (lo + int(rnd() * (hi - lo + 1)))
    return out


# samples
add([1, 2, 3, 2, 1], [2, 1, 3, 1])
add([5, 6, 7], [1, 2, 3, 3])
add([4, 4, 4, 4], [4, 1, 1, 4])
add([7, 3, 7, 3, 7, 3], [3, 7, 3, 7])
add([2, 9, 2, 8, 9, 8, 2], [9, 8, 2, 8, 2, 9])
# hidden: small (brute checks these)
add([1], [2])
add([3], [3, 3])
b = near_pairs(200, 100, 0)
add(list(dict.fromkeys(b)), b)
b = near_pairs(1000, 500, 3)
add(edited(list(dict.fromkeys(b)), 3000, 0.9, 500), b)
b = double_perm(3000, 1500)
add(edited(b, 3000, 0.7, 1500), b)
add(rand_a(3000, list(range(1, 3001))), [x for x in range(1, 1501) for _ in range(2)])
b = double_perm(2000, 1000)
add(b[::-1] + rand_a(1000, list(range(1, 1001))), b)
# hidden: big (M = 200000, N = 500000 or less so that a test stays below about 3 MB): a core of up to 10^5
# songs over all song numbers, mixed with many songs 1..99 (short numbers), most of them near the start of B
N, M, C = MAXN, MAXM, 100000
ALLV = list(range(1, K + 1))
dedup = lambda b: list(dict.fromkeys(b))
b = pairs_of(order_small_front(99, 0.25), 1)
add(pad(edited(dedup(b), C, 0.9), N), b)                          # the core follows the songs of B once each
b = pairs_of(order_small_front(99, 0.5), 0)
add(pad(each_times(dedup(b), 1, 3)[:C], N), b)
b = pairs_of(order_small_front(99, 0.25), 20)
add(pad(edited(b, C, 0.8), N), b)
b = pairs_of(order_small_front(99, 0.3), 3)
add(pad(dedup(b)[::-1][:C], N), b)
b = pairs_of(order_small_front(99, 0.25), K)                     # second copies anywhere later
add(pad(edited(dedup(b), C, 0.95), N), b)
o = order_small_front(99, 0.2)
b = o + o                                                          # B is one order played twice
add(pad(edited(o, C, 0.9), N), b)
b = pairs_of(order_small_front(99, 0.1), 5)
add(pad(rand_a(C, ALLV), N), b)
b = pairs_of(order_small_front(99, 0.25), 2)
add(pad(front(b, C, M // 4), N), b)
b = pairs_of(order_small_front(99, 0.25), 1)
add(pad(edited(dedup(b)[: K // 2], C // 2, 0.9) + edited(dedup(b)[K // 2:], C // 2, 0.9), N), b)
b = pairs_of(order_small_front(99, 0.4), 50)
add(pad(edited(dedup(b), C, 0.6), N), b)
b = pairs_of(order_small_front(99, 0.25), 10)
add(pad(each_times(dedup(b)[:C // 2], 3, 3), 450000), b)          # songs three times in a row
b = pairs_of(order_small_front(99, 0.3), 0)
add(pad(dedup(b)[:C], N), b)                                    # each song once, B has it twice in a row
mp = relabel()
add(rand_a(300000, ALLV), [mp[x] for x in range(1, K + 1)])       # every song once in B

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
