# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1401)
MAXN, MAXC, MAXLINE, MAXTOTAL = 200000, 20, 1000, 2000000
tests = []
rnd = random.random


def ri(a, b):
    """random integer in [a, b] (only random.random(), so every Python version gives the same tests)"""
    return a + int(rnd() * (b - a + 1))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def add(C, K, V, lines):
    assert 1 <= len(lines) <= MAXN and 2 <= C <= MAXC and 1 <= K <= C and 1 <= V <= C and K != V
    assert max(len(ln) for ln in lines) <= MAXLINE
    body = "".join(ln + "\n" for ln in lines)
    assert len(body) - len(lines) <= MAXTOTAL
    assert set(body) <= PRINTABLE
    tests.append(f"{len(lines)} {C} {K} {V}\n" + body)


PLAIN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-_'/()&:;!?+*=<>#@$%[]{}|~^`\\"
ANY = PLAIN + ',,""'
PRINTABLE = set(chr(c) for c in range(32, 127)) | {"\n"}
# long random strings; a random text is a slice of one of them (much faster than letter by letter)
SOURCE = {a: "".join(pick(a) for _ in range(200000)) for a in (PLAIN, ANY)}


def text(alphabet, lo, hi):
    n = ri(lo, hi)
    src = SOURCE[alphabet]
    i = ri(0, len(src) - n)
    return src[i:i + n]


def quote(s):
    return '"' + s.replace('"', '""') + '"'


def enc(s, pq=0.3):
    """a field holding the value s: quoted when it must be, otherwise quoted with probability pq"""
    if ',' in s or '"' in s or (s and rnd() < pq):
        return quote(s)
    return s


AMOUNT_LO = [0, 0] + [10 ** (d - 1) for d in range(2, 10)]
AMOUNT_SPAN = [0] + [10 ** d - AMOUNT_LO[d] for d in range(1, 10)]


def amount(big):
    """same draws as ri(...) calls, written inline because gen.py calls it about 1.5 million times"""
    d = 1 + int(rnd() * 9) if not big else 8 + int(rnd() * 2)
    s = str(AMOUNT_LO[d] + int(rnd() * AMOUNT_SPAN[d]))
    if rnd() < 0.08 and len(s) <= 7:
        s = "0" * (1 + int(rnd() * 2)) + s
    if rnd() < 0.35:
        s = "-" + s
    return s


BAD_AMOUNTS = ["+5", "1 2", " 5", "5 ", "1234567890", "-", "", "--5", "5-", "1e3", "0x1", "12a", "- 3",
               "0000000000", "-1234567890", "\t"[:0] + "3.5", "1,000", '2"']


def make_keys(n, maxlen):
    """n distinct non-empty keys with commas, quotes, spaces, shared prefixes and case differences
    (the hot draws are written inline: same random sequence as text() / pick() / ri(), but faster)"""
    keys = set()
    base = []
    plain, anys = SOURCE[PLAIN], SOURCE[ANY]
    lim = len(plain) + 1                                # both sources have the same length
    draw = rnd
    while len(base) < n:
        r = draw()
        if r < 0.55 or not base:                        # text(PLAIN or ANY, 1, maxlen)
            m = 1 + int(draw() * maxlen)
            i = int(draw() * (lim - m))
            k = (plain if r < 0.35 or not base else anys)[i:i + m]
        elif r < 0.75:                                  # a variant of an earlier key
            b = base[int(rnd() * len(base))]
            v = int(rnd() * 8)
            if v == 0:
                k = b + text(ANY, 1, 2)
            elif v == 1:
                k = b[:-1] if len(b) > 1 else b + "a"
            elif v == 2:
                k = b.swapcase()
            elif v == 3:
                k = " " + b
            elif v == 4:
                k = b + " "
            elif v == 5:
                k = b.replace(" ", ",")
            else:
                k = '"' + b if v == 6 else b + '"'
        else:
            k = pick(["Ann", "Bob", "ann", "A", "a", " ", "  ", ",", '"', '""', "Ann, B", "Ann,B", "Ann ,B",
                      "x" * ri(1, 5), '"q"', "B" * ri(1, 3)]) + (str(ri(0, 99)) if rnd() < 0.5 else "")
        k = k[:maxlen]
        if k and k not in keys:
            keys.add(k)
            base.append(k)
    return base


POOL = {}


def other(maxlen):
    """a random field value of length <= maxlen, taken from a pool of pre-made texts (keeps gen.py fast)"""
    if maxlen not in POOL:
        POOL[maxlen] = [text(PLAIN if i % 2 else ANY, 0, maxlen) for i in range(3000)]
    return pick(POOL[maxlen])


def broken(C, K, V, key, maxlen, row):
    """a record that breaks exactly one chosen rule (fields are well formed otherwise);
    row = (values, encoded values) of the other fields, pre-made"""
    vals, f = row[0][:], row[1][:]
    vals[K - 1] = key
    f[K - 1] = enc(key)
    vals[V - 1] = amount(False)
    f[V - 1] = enc(vals[V - 1])
    kind = ri(0, 11)
    j = ri(0, C - 1)
    if kind == 0:            # quote inside a plain field
        s = text(PLAIN, 0, 4)
        f[j] = s + '"' + text(PLAIN, 0, 4)
    elif kind == 1:          # a plain field that starts with a space and then holds a quoted text
        f[j] = " " + quote(vals[j])
    elif kind == 2:          # unclosed quoted field at the end
        f[-1] = '"' + vals[-1].replace('"', '""') + pick(["", '""', ",x", '"",'])
    elif kind == 3:          # something after the closing quote
        f[j] = quote(vals[j]) + pick([" ", "x", '"x"', "a b", " ,"[:1]])
    elif kind == 4:          # one field too many
        f.insert(ri(0, C), enc(other(maxlen)))
    elif kind == 5:          # one field too few (C >= 2)
        f.pop(ri(0, C - 1))
    elif kind == 6:          # a trailing comma (an extra empty field)
        f.append("")
    elif kind == 7:          # empty key
        f[K - 1] = pick(["", '""'])
    elif kind == 8:          # bad amount
        f[V - 1] = enc(pick(BAD_AMOUNTS), 0.5)
    elif kind == 9:          # empty line or a single field
        return pick(["", enc(key), quote(",".join(vals))])
    elif kind == 10:         # the whole record put inside quotes: one field
        return quote(",".join(f))
    else:                    # quoted key whose comma a naive split would cut
        f[K - 1] = quote(key + "," + text(PLAIN, 0, 3))
        f.pop(ri(0, C - 1) if C > 2 else 0)
    return ",".join(f)


def records(n, C, K, V, nkeys, pbad, big=False, maxlen=8, keylen=10, total=1900000):
    keys = make_keys(nkeys, keylen)
    # well-formed records are built from pre-made pieces (a few random draws per line keep gen.py fast):
    # rows of encoded other fields, a pool of encoded amounts, and each key both as it must be written and quoted
    other(maxlen)
    vals = POOL[maxlen]
    rows = []
    for _ in range(3000):
        row = [pick(vals) for _ in range(C)]
        rows.append((row, [enc(v) for v in row]))
    amounts = [enc(amount(big)) for _ in range(5000)]
    quoted = [quote(k) for k in keys]
    written = [q if (',' in k or '"' in k) else k for k, q in zip(keys, quoted)]
    out, used, nxt = [], 0, 0
    walk = nkeys >= 10000                       # mostly walk through all keys, so most of them really occur
    draw = rnd
    for _ in range(n):
        if walk and draw() < 0.8:
            j = nxt % nkeys
            nxt += 1
        else:
            j = int(draw() * nkeys)
        if draw() < pbad:
            ln = broken(C, K, V, keys[j], maxlen, rows[int(draw() * 3000)])[:MAXLINE]
        else:
            f = rows[int(draw() * 3000)][1][:]
            f[K - 1] = quoted[j] if draw() < 0.3 else written[j]
            f[V - 1] = amounts[int(draw() * 5000)]
            ln = ",".join(f)[:MAXLINE]
        if used + len(ln) > total:
            break
        used += len(ln)
        out.append(ln)
    return out


# samples
add(3, 1, 3, ['"Ann, B",x,10', 'Bob,y,"-5"', '"Ann, B",z,7', 'Bob,"q"x,1', '"He said ""hi""",,3'])
add(2, 2, 1, ['5,apple', '12', '1234567890,pear', '7,ap"ple'])
add(3, 2, 1, ['-007,  x ,a', '', '3,"  x ",', ',y,z', '"4",x,'])
add(3, 3, 1, ['250,x,"Lee, K."', '"-40",y,Ploy', '90,,"Lee, K."', '0,x,ploy'])
add(2, 1, 2, ['"abc,5', ' "a",5', '"a""b",5', '"",5', 'x,"5"'])
# hidden: small (brute checks these)
add(2, 2, 1, ['0,a'])
add(2, 1, 2, [''])
for C, K, V, n, nk, pb in [(2, 1, 2, 30, 4, 0.5), (3, 3, 1, 60, 8, 0.4), (5, 2, 4, 200, 20, 0.3),
                           (4, 1, 4, 500, 60, 0.6)]:
    add(C, K, V, records(n, C, K, V, nk, pb, maxlen=5, keylen=6))
add(3, 1, 2, records(3000, 3, 1, 2, 5, 0.1, big=True))
# hidden: big
BIG = [
    (14100, lambda: (2, 1, 2, records(MAXN, 2, 1, 2, 60000, 0.25, big=True, maxlen=6, keylen=8))),
    (14101, lambda: (2, 2, 1, records(MAXN, 2, 2, 1, 90000, 0.1, big=True, maxlen=6, keylen=7))),
    (14102, lambda: (3, 1, 3, records(MAXN, 3, 1, 3, 50000, 0.3, big=True, maxlen=3, keylen=6))),
    (14103, lambda: (4, 3, 1, records(MAXN, 4, 3, 1, 70000, 0.2, big=True, maxlen=2, keylen=6))),
    (14104, lambda: (5, 2, 5, records(MAXN, 5, 2, 5, 50000, 0.4, big=True, maxlen=2, keylen=5))),
    (14105, lambda: (8, 7, 4, records(MAXN, 8, 7, 4, 100000, 0.2, big=True, maxlen=1, keylen=8))),
    (14106, lambda: (3, 2, 3, records(MAXN, 3, 2, 3, 3, 0.05, big=True, maxlen=2, keylen=4))),
    (14107, lambda: (2, 1, 2, records(MAXN, 2, 1, 2, 120000, 0.02, big=True, maxlen=3, keylen=9))),
    (14108, lambda: (6, 6, 1, records(MAXN, 6, 6, 1, 100000, 0.35, big=True, maxlen=3, keylen=8))),
    (14109, lambda: (3, 1, 2, records(MAXN, 3, 1, 2, 100000, 0.1, big=True, maxlen=8, keylen=24))),
    (14110, lambda: (2, 1, 2, records(MAXN, 2, 1, 2, 1000, 0.15, maxlen=4, keylen=2, total=MAXTOTAL))),
    (14111, lambda: (10, 1, 10, records(MAXN, 10, 1, 10, 100000, 0.2, big=True, maxlen=1, keylen=12))),
    (14112, lambda: (2, 2, 1, records(MAXN, 2, 2, 1, 80000, 0.5, big=True, maxlen=5, keylen=8))),
    (14113, lambda: (3, 3, 2, records(5000, 3, 3, 2, 3000, 0.3, big=True, maxlen=400, keylen=400))),
    (14114, lambda: (4, 1, 2, records(MAXN, 4, 1, 2, 60000, 0.25, big=True, maxlen=3, keylen=7))),
    (14115, lambda: (2, 1, 2, records(MAXN, 2, 1, 2, 100000, 0.2, maxlen=5, keylen=20))),
    (14116, lambda: (7, 4, 3, records(MAXN, 7, 4, 3, 60000, 0.2, big=True, maxlen=2, keylen=6))),
]
for seed, make in BIG:
    random.seed(seed)
    add(*make())

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
