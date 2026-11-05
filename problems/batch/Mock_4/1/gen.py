# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(2011)
MAXN, MAXM, MAXLEN, MAXTOTAL = 100000, 100000, 20, 1000000
LET = "abcdefghijklmnopqrstuvwxyz"
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only rnd(), so every Python version gives the same tests)"""
    return a + int(rnd() * (b - a + 1))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = ri(0, i)
        a[i], a[j] = a[j], a[i]


TABLE = {}


def table(alpha):
    """all words of length c over the first alpha letters, c as large as keeps the table under 5 * 10^5"""
    if alpha not in TABLE:
        c = 1
        while alpha ** (c + 1) <= 500000:
            c += 1
        t = [""]
        for _ in range(c):
            t = [w + ch for w in t for ch in LET[:alpha]]
        TABLE[alpha] = (c, t)
    return TABLE[alpha]


def word(L, alpha=26):
    """random word of length L over the first alpha letters (one rnd() gives two pieces of the table)"""
    c, t = table(alpha)
    n = len(t)
    if L <= 2 * c:
        x = int(rnd() * n * n)
        return (t[x // n] + t[x % n])[:L]
    need = (L + c - 1) // c
    parts = []
    while need >= 2:
        x = int(rnd() * n * n)
        parts.append(t[x // n])
        parts.append(t[x % n])
        need -= 2
    if need:
        parts.append(t[int(rnd() * n)])
    return "".join(parts)[:L]


def add(dic, text):
    n, m = len(dic), len(text)
    assert 1 <= n <= MAXN and 1 <= m <= MAXM
    assert len(set(dic)) == n
    allw = dic + text
    assert min(map(len, allw)) >= 1 and max(map(len, allw)) <= MAXLEN
    assert sum(map(len, allw)) <= MAXTOTAL
    assert set("".join(allw)) <= set(LET)
    tests.append(f"{n} {m}\n" + " ".join(dic) + "\n" + " ".join(text) + "\n")


DICTS = {}


def make_dict(n, lens, alpha=26, extra=()):
    """n distinct words, lengths drawn from lens; words of extra come first (big lists are reused, as copies)"""
    key = (n, tuple(lens), alpha, tuple(extra))
    if n >= 50000 and key in DICTS:
        return DICTS[key][:]
    seen = set(extra)
    dic = list(extra)
    tries = 0
    nl = len(lens)
    while len(dic) < n:
        w = word(lens[int(rnd() * nl)], alpha)
        tries += 1
        assert tries < 50 * n + 1000
        if w not in seen:
            seen.add(w)
            dic.append(w)
    if n >= 50000:
        DICTS[key] = dic[:]
    return dic


def slip(w):
    """swap one pair of different neighbouring letters (w itself if there is none)"""
    L = len(w)
    if L < 2:
        return w
    for _ in range(4):
        j = int(rnd() * (L - 1))
        if w[j] != w[j + 1]:
            return w[:j] + w[j + 1] + w[j] + w[j + 2:]
    js = [j for j in range(L - 1) if w[j] != w[j + 1]]
    if not js:
        return w
    j = pick(js)
    return w[:j] + w[j + 1] + w[j] + w[j + 2:]


def far(w):
    """swap two different letters that are not neighbours (w itself if impossible)"""
    L = len(w)
    for _ in range(10):
        if L < 3:
            break
        i = ri(0, L - 3)
        j = ri(i + 2, L - 1)
        if w[i] != w[j]:
            c = list(w)
            c[i], c[j] = c[j], c[i]
            return "".join(c)
    return w


def text_of(dic, budget, mix, lens=None, alpha=26, maxm=MAXM):
    """text words until about budget letters: mix = list of (integer weight, kind)"""
    kinds = [kind for p, kind in mix for _ in range(p)]
    nk, nd = len(kinds), len(dic)
    text, used = [], 0
    while len(text) < maxm:
        kind = kinds[int(rnd() * nk)]
        if kind == "rand":
            w = word(pick(lens), alpha)
        else:
            w = dic[int(rnd() * nd)]
            if kind == "slip":
                w = slip(w)
            elif kind == "far":
                w = far(w)
            elif kind == "two":
                w = slip(slip(w))
        used += len(w)
        if used > budget:
            break
        text.append(w)
    return text


def dict_chars(dic):
    return sum(len(w) for w in dic)


# samples
add("the cat sat on a mat".split(), "teh cat sta no a dog mta".split())
add("ant tan at".split(), "nat tna ta at tan ant".split())
add("dear dare friend i read your card".split(), "daer freind i raed yuor card tow times".split())
add("we go to the zoo on sunday".split(), "ew og ot hte zoo on sunady ta".split())
add("table black stable cable".split(), "talbe balck stalbe cbale tabel lbock table".split())

# hidden: small hand-made (a tie inside one family of anagrams; words whose swap is also in the list)
add("dare dear read".split(), "daer raed ared dera".split())
add("i a no on is si to".split(), "on i so no ti a si ot".split())

# hidden: small (brute checks these)
add(["a"], ["a"])
add(["ab"], ["ba", "ab", "a", "b", "aab"])
abc = [x + y + z for x in "abc" for y in "abc" for z in "abc"]
words3 = ["a", "b", "c"] + [x + y for x in "abc" for y in "abc"] + abc
for seed in (1, 2, 3):
    random.seed(seed)
    d = [w for w in words3 if rnd() < 0.4] or ["a"]
    add(d, words3[:])
random.seed(7)
for n, lens, alpha, m in [(100, [4, 5, 6], 2, 600), (500, [5, 6], 3, 1500),
                          (1500, list(range(1, 9)), 4, 2000), (2000, [6, 7, 8], 26, 3000),
                          (800, [8, 9, 10, 11], 2, 2500)]:
    d = make_dict(n, lens, alpha)
    shuffle(d)
    t = text_of(d, 10 ** 6, [(2, "exact"), (4, "slip"), (1, "far"), (1, "two"), (2, "rand")], lens, alpha, m)
    add(d, t)

# hidden: big
MIX = [(3, "exact"), (4, "slip"), (1, "far"), (1, "two"), (1, "rand")]


def big_random(n, lens, alpha, mix=MIX, maxm=MAXM):
    d = make_dict(n, lens, alpha)
    shuffle(d)
    t = text_of(d, MAXTOTAL - dict_chars(d), mix, lens, alpha, maxm)
    return d, t


def pairs_dict(n, L):
    """n / 2 words together with one slip of each (both in the list)"""
    d, seen = [], set()
    while len(d) < n - 1:
        w = word(L)
        v = slip(w)
        if w != v and w not in seen and v not in seen:
            seen.update((w, v))
            d += [w, v]
    shuffle(d)
    return d


def same_letter_text():
    d = make_dict(50000, [10], 26, extra=["a" * k for k in range(1, 21, 2)] + ["ab" * 5, "ba" * 5])
    shuffle(d)
    t = []
    used = dict_chars(d)
    while True:
        k = ri(1, 20)
        w = pick(["a" * k, "b" * k, "a" * (k - 1) + "b", "b" + "a" * (k - 1), ("ab" * 10)[:k], ("ba" * 10)[:k]])
        if used + len(w) > MAXTOTAL or len(t) == MAXM:
            break
        t.append(w)
        used += len(w)
    return d, t


def repeated_word():
    d = make_dict(MAXN, [4, 5], 26)
    w = slip(d[0])
    t = [w] * min(MAXM, (MAXTOTAL - dict_chars(d)) // len(w))
    return d, t


def order_trap():
    d = pairs_dict(50000, 9)
    t = text_of(d, MAXTOTAL - dict_chars(d), [(5, "exact"), (4, "slip"), (1, "rand")], [9], 26)
    return d, t


def order_trap_short():
    d = pairs_dict(MAXN, 6)
    t = text_of(d, MAXTOTAL - dict_chars(d), [(4, "exact"), (5, "slip"), (1, "rand")], [6], 26)
    return d, t


BIG = [
    (5001, lambda: big_random(50000, list(range(6, 13)), 26)),
    (5002, lambda: big_random(20000, [14, 15], 2)),
    (5003, lambda: big_random(40000, [15, 16, 17], 2)),
    (5004, lambda: big_random(30000, [10], 3)),
    (5005, lambda: big_random(25000, [20], 26, [(1, "exact"), (2, "slip"), (2, "far"), (3, "rand")])),
    (5006, lambda: big_random(50000, [10], 26, [(1, "far"), (1, "rand"), (1, "two")])),
    (5007, lambda: big_random(MAXN, [1, 2, 3, 3, 4, 4, 4, 4], 26, [(1, "exact"), (1, "slip"), (1, "rand")])),
    (5008, lambda: big_random(50000, [8, 9], 4)),
    (5009, lambda: big_random(50000, list(range(1, 21)), 26)),
    (5011, same_letter_text),
    (5012, repeated_word),
    (5013, order_trap),
    (5014, lambda: big_random(MAXN, [4, 5], 26, [(1, "slip")])),
    (5015, lambda: big_random(30000, [18, 19, 20], 2, [(1, "slip"), (1, "rand")])),
    (5017, lambda: big_random(50000, [9, 10, 11], 5, [(2, "slip"), (1, "two"), (1, "rand")])),
    (5018, lambda: big_random(MAXN, [4, 5], 26, [(1, "rand"), (1, "far")])),
    (5019, lambda: big_random(MAXN, [3, 4, 5, 6], 26, [(1, "exact"), (2, "slip"), (1, "rand")])),
    (5020, lambda: order_trap_short()),
]
for seed, make in BIG:
    random.seed(seed)
    d, t = make()
    add(d, t)

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
